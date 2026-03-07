# Rubric (v1)

This rubric defines how we score candidate decisions in the PM Simulator.

## Goals
- Score **decision quality** (judgment), not writing flair.
- Produce **actionable feedback** the user can apply next turn.
- Be **auditable**: results are reproducible given the same input, rubric version, and model.

## Scoring scale (0–5)

**0 — Missing / Not addressed**
- Does not answer the question, or irrelevant.

**1 — Weak**
- Mentions the area but vague; no reasoning; major gaps.

**2 — Basic**
- Some structure, but incomplete tradeoffs, assumptions, or feasibility.

**3 — Solid**
- Clear recommendation with reasoning; addresses constraints; reasonable plan.

**4 — Strong**
- Good prioritization and risk mitigation; anticipates stakeholder concerns; metrics are appropriate.

**5 — Excellent**
- Demonstrates expert-level judgment: crisp framing, explicit tradeoffs, strong evidence plan, pragmatic execution, and measurable success definition.

> Note: Scores should be anchored to **scenario context + turn prompt**. A "5" is rare.

---

## Universal dimensions (apply to every decision)

### D1 — Problem framing & clarity
What we look for:
- Restates the problem in their own words
- Defines scope and constraints
- Clarifies user/business impact

Anchor examples:
- **1:** Repeats prompt with no reframing.
- **3:** Defines problem + constraints + who is impacted.
- **5:** Adds sharp insight (root cause hypothesis, segmentation, key unknowns).

### D2 — Decision quality & tradeoffs
What we look for:
- Clear recommendation
- Alternatives considered
- Explicit tradeoffs (cost/impact/time/risk)

Anchors:
- **1:** “We should do X” without tradeoffs.
- **3:** Picks X and explains why vs Y.
- **5:** Explicit opportunity cost + sequencing + fallback plan.

### D3 — Evidence & assumptions
What we look for:
- Assumptions stated
- What data would validate/invalidates them
- Discovery plan if uncertainty is high

Anchors:
- **1:** No assumptions; “users want this” vibes.
- **3:** Lists assumptions + data sources.
- **5:** Prioritized unknowns + fastest tests + decision thresholds.

### D4 — Execution realism (engineering/ops reality)
What we look for:
- Feasible scope and sequencing
- Dependencies, risks, mitigation
- Rollout / QA / monitoring

Anchors:
- **1:** Ignores constraints.
- **3:** Reasonable plan + risks.
- **5:** Crisp phased rollout + guardrails + mitigations.

### D5 — Metrics & success criteria
What we look for:
- Defines success metrics + guardrails
- Links actions to KPIs
- Mentions instrumentation if relevant

Anchors:
- **1:** “Improve engagement” with no metric.
- **3:** Defines a primary KPI and at least one guardrail.
- **5:** Metric tree, baselines, targets, and measurement plan.

---

## Role-based scoring (only if role appears in scenario)

Each scenario can define role weights and which dimensions are role-specific. The grader should evaluate alignment to each role’s incentives and concerns.

### Engineering Lead
Look for:
- Feasibility, scope control, dependencies, risk reduction
Common misses:
- Overpromising, ignoring delivery constraints

### Design / Research
Look for:
- User journey quality, research plan, usability risk
Common misses:
- No validation plan; solution-first thinking

### Data / Analytics
Look for:
- Metric validity, experiment design, confounders
Common misses:
- Vanity metrics; no baseline/segmentation

### Sales / Customer Success
Look for:
- Customer impact, rollout comms, support readiness
Common misses:
- No change management; ignores enterprise constraints

### Executive / Strategy
Look for:
- Narrative clarity, strategic alignment, opportunity cost
Common misses:
- No “why now”; no link to strategy

---

## Gates (binary checks)

These don’t directly set the score but influence it and appear in feedback.

- G1: Clear recommendation present (yes/no)
- G2: Mentions constraints (yes/no)
- G3: Mentions success metrics (yes/no)
- G4: Mentions risks + mitigation (yes/no)
- G5: Compares alternatives (yes/no)

If G1 is **no**, overall score should not exceed **2**.

---

## Computing scores

Suggested default:
- Universal dimensions weight equally:
  - overall = average(D1..D5)
- If role-based scoring is enabled, combine:
  - overall = 70% universal + 30% role-weighted average

Role weights should be defined per scenario (example):
- Engineering 0.4
- Exec 0.3
- Sales/CS 0.2
- Design 0.1

---

## Output requirements (what the grader must produce)
- Dimension scores (0–5) with one-sentence justification each
- Role scores (0–5) if roles present
- 3–5 strengths (bullets)
- 3–5 improvements (bullets, actionable)
- Gates results
- Red flags (hallucinations, contradictions, ignoring constraints)
- Confidence (0.0–1.0)

---

## Versioning
- Update this file with a new top-level version when changing scoring meaningfully.
- Persist `rubric_version` with each grade result.