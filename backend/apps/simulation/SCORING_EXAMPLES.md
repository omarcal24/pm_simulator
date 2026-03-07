# SCORING_EXAMPLES (v1)

This file calibrates grading so scores are consistent across scenarios and over time.

**How to use**
- These examples are “golden” test cases.
- Run them through the grader whenever you change:
  - `RUBRIC.md`
  - `GRADER_PROMPT.md`
  - `ROLE_CARDS.md`
  - model selection or temperature
- The grader output should be close to the **expected ranges** below.
- If scores drift, update rubric/prompts or create a new rubric version.

---

## Example 1 — Prioritization under deadline pressure (B2B SaaS)

### Scenario (summary)
You are a PM for a B2B SaaS product. Activation dropped from **28% → 20%** over 6 weeks. Sales says onboarding is “too long” and wants feature work paused to fix it. Engineering says the onboarding code is fragile and warns against rushing changes.

**Constraints**
- 2 engineers + 1 designer available
- 4 weeks until a major enterprise renewal decision
- Cannot break existing enterprise workflows
- Must show measurable impact within 4 weeks

**KPIs**
- Primary: Activation rate
- Guardrails: Support tickets, churn, time-to-first-value

**Roles in play**
- `engineering`, `sales_cs`, `exec`, `design`

**Turn prompt**
> You can do only one of these in the next 2 weeks:
> A) Redesign onboarding flow (UI + steps)  
> B) Add in-product guided checklist with minimal backend changes  
> C) Pause onboarding and ship requested enterprise feature for renewal  
>  
> What do you choose and why? Provide scope, risks, and success metrics.

---

### Candidate Answer A (Weak) — Expected overall: **1.0–2.0**
**Response**
- “I choose A because onboarding is the problem. We should simplify it and make it shorter. This will improve activation quickly.”

**Why this is weak**
- No scope or sequencing
- No constraints addressed
- No risks or mitigations
- No metrics plan beyond “improve activation”
- Ignores engineering warning

**Expected gates**
- recommendation: ✅
- constraints: ❌
- metrics: ❌
- risks+mitigation: ❌
- alternatives compared: ❌

**Expected dimension score ranges**
- problem_framing: 1–2
- tradeoffs: 0–1
- evidence_assumptions: 0–1
- execution_realism: 0–1
- metrics_success: 0–1

**Expected role score ranges**
- engineering: 0–1
- sales_cs: 1–2
- exec: 1–2
- design: 1–2

---

### Candidate Answer B (Solid) — Expected overall: **3.0–3.7**
**Response**
- “I choose B (guided checklist) as the fastest reversible change in 2 weeks.  
  Scope: add a checklist with 3–5 critical setup tasks, progress indicator, and contextual tips; no major backend refactor.  
  Assumption: users drop because they don’t know the next step; checklist reduces confusion.  
  Risks: enterprise users may ignore it; mitigations: show only to new accounts, add dismissal, measure completion.  
  Metrics: activation (primary), time-to-first-value, checklist completion; guardrails: support tickets and churn.  
  Next: if checklist moves activation +2–3 points in 2 weeks, iterate with design on A; otherwise do targeted onboarding step removal based on funnel drop-offs.”

**Expected gates**
- recommendation: ✅
- constraints: ✅
- metrics: ✅
- risks+mitigation: ✅
- alternatives compared: ✅ (implicit via rationale + sequencing)

**Expected dimension score ranges**
- problem_framing: 3–4
- tradeoffs: 3–4
- evidence_assumptions: 2–4
- execution_realism: 3–4
- metrics_success: 3–4

**Expected role score ranges**
- engineering: 3–4
- sales_cs: 3–4
- exec: 3–4
- design: 3–4

---

### Candidate Answer C (Excellent) — Expected overall: **4.3–5.0**
**Response**
- “I choose B now, and explicitly *do not* choose A yet because of engineering risk and the 2-week constraint.  
  First 48h: confirm drop-off points in onboarding funnel (segmented by enterprise vs SMB) and review top 20 support tickets.  
  Deliver in 2 weeks: guided checklist + progressive disclosure of advanced steps.  
  Scope control: only UI + tracking + copy; no backend refactor.  
  Rollout: 10% new users → 50% → 100% with rollback flag.  
  Success: activation +3pp within 2 weeks for SMB, no increase in support tickets; guardrail churn stable.  
  Stakeholders: sales/CS get a comms plan for enterprise accounts; exec gets narrative + why-now and tradeoffs vs renewal feature.  
  If improvement <1pp, pivot to removing one high-friction step (based on data) and schedule a refactor ticket for fragile onboarding code.”

**Expected gates**
- all ✅

**Expected dimension score ranges**
- problem_framing: 4–5
- tradeoffs: 4–5
- evidence_assumptions: 4–5
- execution_realism: 4–5
- metrics_success: 4–5

**Expected role score ranges**
- engineering: 4–5
- sales_cs: 4–5
- exec: 4–5
- design: 4–5

---

## Example 2 — Incident + stakeholder pressure (Consumer app)

### Scenario (summary)
A consumer app shipped a new feed ranking model. Engagement rose +6%, but complaints increased and app store rating dropped from 4.6 → 4.2.

**Constraints**
- PR risk; press is noticing
- You can’t fully rollback due to infrastructure changes, but can “feature-flag” logic
- Engineering bandwidth is limited (1 week for fixes)

**KPIs**
- Primary: retention (7-day), report rate
- Guardrails: app store rating, CS load

**Roles in play**
- `engineering`, `exec`, `data`, `sales_cs` (support)

**Turn prompt**
> What do you do in the next 72 hours?

---

### Candidate Answer A (Weak) — Expected overall: **1.0–2.0**
- “We should roll back immediately and apologize to users.”

Expected issues:
- ignores constraint (“can’t fully rollback”)
- no concrete mitigation steps
- no measurement plan

Expected gates:
- recommendation ✅
- constraints ❌
- metrics ❌
- risks+mitigation ❌
- alternatives ❌

---

### Candidate Answer B (Solid) — Expected overall: **3.0–3.8**
- “Hotfix: tighten the feature flag to reduce exposure, adjust ranking weights to reduce sensational content, and add a ‘show less of this’ feedback control.  
  Data: compare report rate by segment, check if a cohort is disproportionately affected.  
  Comms: CS macros + in-app message for affected users.  
  Metrics: report rate + rating + retention; guardrail CS ticket volume.  
  In 72h: stabilize and prepare a longer-term plan.”

---

### Candidate Answer C (Excellent) — Expected overall: **4.2–5.0**
- “72h plan:  
  1) Limit exposure using feature flags for the most impacted segments; rollback only the ranking component we can safely toggle.  
  2) Instrument: report rate per 1k sessions, negative feedback actions, and rating trend; compare to pre-launch baseline and run a counterfactual with holdout if possible.  
  3) Mitigate: cap repetition/virality, add user controls, publish a clear update in-app; provide CS a playbook.  
  4) Exec alignment: clear narrative—engagement gain not worth trust loss; set thresholds for further rollback (e.g., rating <4.1 or report rate >X).  
  5) Engineering: small, reversible changes first; commit to a follow-up model iteration with safety constraints.”

---

## Example 3 — AI feature with compliance constraints (Enterprise)

### Scenario (summary)
You want to ship an AI assistant that summarizes customer documents. Some customers require **data locality** and opt-out of model training.

**Constraints**
- EU data residency for a subset of customers
- No retention of customer content beyond processing
- Must provide an admin control for enabling/disabling

**KPIs**
- Primary: weekly active usage of assistant
- Guardrails: compliance incidents, latency, cost per summary

**Roles in play**
- `engineering`, `exec`, `sales_cs`, `data`

**Turn prompt**
> What is your MVP scope and rollout plan?

### Candidate Answer A (Weak) — Expected overall: **1.0–2.0**
- “Ship summaries for all docs to all customers. We’ll fix compliance later.”

### Candidate Answer B (Solid) — Expected overall: **3.2–3.9**
- “MVP: summaries for a limited doc type, opt-in only, admin toggle, retention disabled, EU routing for EU customers if feasible; phased rollout + monitoring; metrics include WAU and latency + cost.”

### Candidate Answer C (Excellent) — Expected overall: **4.3–5.0**
- “MVP: opt-in pilot for non-regulated customers, strict data handling (no training, no retention), admin controls, per-tenant region routing, and a fallback ‘no AI available’ state for EU tenants until residency is verified; staged rollout with cost/latency budgets; sales enablement and legal signoff gates.”

---

## Notes for maintainers

### Expected stability
- Overall scores may vary slightly run-to-run.
- **Dimension ordering and presence** must remain consistent with `GRADING_SCHEMA.json`.
- Gates should be stable.

### When to bump rubric version
- If you change any dimension meaning, scoring scale anchors, or how overall is computed.

### Suggested regression tests
- Run each example 5 times:
  - Expected overall variance <= ~0.4
  - Gate outcomes stable
  - No missing fields in JSON