"""
Simulation engine step logic — pure Python, deterministic.
Input: current state, decision payload, scenario config, seed.
Output: events, metric snapshot, updated state, next prompt.

Scoring model
─────────────
Each decision is evaluated on two dimensions:

1. Rationale quality (0.0–1.0)
   Rewards length and PM-specific vocabulary (data, tradeoffs, hypotheses…).
   A thoughtful rationale amplifies the magnitude of KPI changes; a vague one
   dampens it and introduces a slight negative drift.

2. Decision direction (speed / quality / alignment / focus)
   Keywords in the rationale and choice_id are matched to four axes. Each KPI
   has a sensitivity profile that maps those axes to positive or negative
   impact — reflecting real PM tradeoffs (e.g. shipping fast improves
   time_to_market but hurts quality_score and retention).
"""
import random
from dataclasses import dataclass, field


@dataclass
class EngineInput:
    state: dict
    decision: dict
    config: dict
    step_number: int
    seed: int


@dataclass
class EngineEvent:
    type: str
    severity: str
    actor: str
    message: str
    payload: dict = field(default_factory=dict)


@dataclass
class EngineOutput:
    events: list[EngineEvent]
    metrics: dict[str, float]
    next_state: dict
    next_prompt: str
    is_complete: bool


# ── KPI sensitivity profiles ─────────────────────────────────────────────────
# Each axis value: positive = KPI improves, negative = KPI hurts. Scale [-2, 2]
# Unknown KPIs fall back to _DEFAULT_PROFILE.
_KPI_PROFILES: dict[str, dict[str, float]] = {
    "activation_rate":  {"speed": 1.2,  "quality": 0.2,  "alignment": 0.9,  "focus": 0.6},
    "retention_30d":    {"speed": -0.6, "quality": 1.6,  "alignment": 0.8,  "focus": 0.4},
    # Schedule health: speed helps delivery, quality work and scope cuts also help;
    # misalignment or over-engineering hurts.
    "schedule_health":  {"speed": 1.5,  "quality": -0.5, "alignment": 0.4,  "focus": 1.2},
    # Quality index: quality/investigative work improves it; rushing hurts it.
    "quality_index":    {"speed": -1.3, "quality": 1.8,  "alignment": 0.2,  "focus": 0.5},
    "nps":              {"speed": -0.4, "quality": 1.3,  "alignment": 1.0,  "focus": 0.3},
    "revenue":          {"speed": 0.7,  "quality": 0.6,  "alignment": 1.0,  "focus": 0.7},
    # Legacy names kept for existing runs
    "time_to_market":   {"speed": 1.5,  "quality": -0.7, "alignment": 0.3,  "focus": 1.0},
    "quality_score":    {"speed": -1.3, "quality": 1.8,  "alignment": 0.2,  "focus": 0.5},
}
_DEFAULT_PROFILE = {"speed": 0.3, "quality": 0.5, "alignment": 0.4, "focus": 0.4}

# ── Decision-axis keyword sets ────────────────────────────────────────────────
_SPEED_WORDS = frozenset({
    "ship", "mvp", "fast", "quick", "partial", "now", "deadline",
    "launch", "release", "iterate", "sprint", "asap", "rapid",
})
_QUALITY_WORDS = frozenset({
    "investigate", "research", "experiment", "validate", "fix", "test",
    "quality", "thorough", "deep", "root", "cause", "data", "evidence",
    "hypothesis", "measure", "metric", "analyse", "analyze", "audit",
})
_ALIGNMENT_WORDS = frozenset({
    "stakeholder", "align", "communicate", "agree", "consensus",
    "sales", "engineering", "support", "design", "collaborate",
    "leadership", "present", "buy-in", "cross-functional",
})
_FOCUS_WORDS = frozenset({
    "scope", "simplify", "focus", "reduce", "cut", "prioritize", "prioritise",
    "narrow", "constraint", "tradeoff", "trade-off", "core", "essential",
})


def _rationale_quality(rationale: str) -> float:
    """
    Score 0.0–1.0 based on rationale quality.
    60 % weight on length (saturates at ~30 words), 40 % on PM vocabulary.
    """
    if not rationale:
        return 0.0
    words = rationale.lower().split()
    pm_terms = frozenset({
        "data", "hypothesis", "tradeoff", "trade-off", "risk", "metric",
        "validate", "experiment", "customer", "feedback", "outcome",
        "assumption", "iterate", "prioritize", "stakeholder", "scope",
    })
    length_score = min(1.0, len(words) / 30)
    term_score = min(1.0, sum(1 for w in words if w in pm_terms) / 2)
    return round(0.6 * length_score + 0.4 * term_score, 2)


def _decision_axes(choice_id: str, rationale: str) -> dict[str, int]:
    """
    Count keyword matches per axis. Capped at 2 per axis to prevent gaming
    by stuffing the rationale with keywords.
    """
    words = set((str(choice_id) + " " + rationale).lower().split())
    return {
        "speed":     min(2, len(words & _SPEED_WORDS)),
        "quality":   min(2, len(words & _QUALITY_WORDS)),
        "alignment": min(2, len(words & _ALIGNMENT_WORDS)),
        "focus":     min(2, len(words & _FOCUS_WORDS)),
    }


def step_engine(input_data: EngineInput, quality_override: float | None = None) -> EngineOutput:
    """Apply a decision and produce events, metrics, and next state.

    quality_override: if provided (0.0–1.0), replaces the keyword-based
    rationale quality score. Used to recalculate metrics after LLM grading.
    """
    rng = random.Random(input_data.seed + input_data.step_number * 1000)

    state = dict(input_data.state)
    config = input_data.config
    decision = input_data.decision

    kpis = config.get("kpis", ["activation_rate", "retention_30d"])
    initial_metrics = config.get("initial_metrics", {k: 50.0 for k in kpis})
    prev_metrics = state.get("metrics", initial_metrics) or {k: 50.0 for k in kpis}

    choice_id = decision.get("choice_id", decision.get("decision_type", ""))
    rationale = decision.get("rationale", "")

    quality = quality_override if quality_override is not None else _rationale_quality(rationale)
    axes = _decision_axes(choice_id, rationale)

    events: list[EngineEvent] = []
    new_metrics: dict[str, float] = {}

    for kpi in kpis:
        base = prev_metrics.get(kpi, 50.0)
        profile = _KPI_PROFILES.get(kpi, _DEFAULT_PROFILE)

        # Directional impact: sum of (matched_words × kpi_sensitivity)
        directional_delta = sum(axes[ax] * profile.get(ax, 0.0) for ax in axes)

        # Quality amplifies impact: 0.0 → ×0.5 (weak); 1.0 → ×1.5 (strong)
        quality_multiplier = 0.5 + quality

        # Base drift: positive nudge for thoughtful responses, slight negative otherwise
        base_drift = (
            rng.uniform(-0.5, 2.0) if quality >= 0.3 else rng.uniform(-2.5, 0.5)
        )

        noise = rng.uniform(-0.8, 0.8)

        delta = directional_delta * quality_multiplier * 1.5 + base_drift + noise
        new_metrics[kpi] = round(max(0.0, min(100.0, base + delta)), 2)

    # ── Events ────────────────────────────────────────────────────────────────
    if rationale:
        events.append(EngineEvent(
            type="decision_recorded",
            severity="info",
            actor="system",
            message="Your decision and rationale have been recorded.",
            payload={"choice_id": choice_id, "rationale_quality": quality},
        ))

    if quality >= 0.7:
        events.append(EngineEvent(
            type="strong_rationale",
            severity="info",
            actor="system",
            message="Strong rationale: structured thinking and data references noted.",
            payload={},
        ))
    elif rationale and quality < 0.2:
        events.append(EngineEvent(
            type="weak_rationale",
            severity="warning",
            actor="system",
            message=(
                "Rationale is brief. Consider referencing data, tradeoffs, "
                "or stakeholder impact to strengthen your decision."
            ),
            payload={},
        ))

    if rng.random() < 0.4:
        stakeholders = config.get("stakeholders", ["Engineering", "Sales"])
        actor = rng.choice(stakeholders)
        events.append(EngineEvent(
            type="stakeholder_reaction",
            severity="info",
            actor=actor,
            message=f"{actor} has acknowledged the decision. Awaiting outcomes.",
            payload={},
        ))

    # ── Next state ────────────────────────────────────────────────────────────
    max_steps = config.get("max_steps", 5)
    next_step = input_data.step_number + 1
    is_complete = next_step >= max_steps

    state["metrics"] = new_metrics
    state["step_number"] = next_step
    state["last_decision"] = decision.get("decision_type", "unknown")

    if is_complete:
        next_prompt = (
            "**Run complete.** You've reached the end of the scenario. "
            "Review your metrics and create a case study to capture your learnings."
        )
    else:
        prompts = config.get("prompts", {})
        next_prompt = prompts.get(
            str(next_step),
            f"**Step {next_step}**: Consider the updated metrics and make your next decision.",
        )

    return EngineOutput(
        events=events,
        metrics=new_metrics,
        next_state=state,
        next_prompt=next_prompt,
        is_complete=is_complete,
    )
