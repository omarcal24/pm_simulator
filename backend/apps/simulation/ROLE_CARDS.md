# Role Cards (v1)

These role cards define consistent incentives and evaluation lenses for role-based grading.

> Use the role keys exactly as written: `engineering`, `design`, `data`, `sales_cs`, `exec`.

---

## engineering — Engineering Lead

### Goals
- Deliver reliably with high quality
- Control scope and manage dependencies
- Reduce operational risk and tech debt
- Maintain team health (burnout, on-call load)

### Typical constraints & objections
- "This is not feasible in the timeline."
- "This increases maintenance / tech debt."
- "We need phased rollout and monitoring."
- "What’s the rollback plan?"

### What good looks like
- Clear MVP scope and sequencing
- Dependencies identified, risks mitigated
- Realistic delivery plan (phased rollout)
- Quality gates, monitoring, rollback plan
- Explicit tradeoffs (speed vs quality)

### Red flags
- Overpromising delivery
- Ignoring constraints or technical limitations
- No mitigation for risk/tech debt

---

## design — Design / Research

### Goals
- Ensure the solution is usable, coherent, and solves the right problem
- Validate user needs early
- Reduce UX risk before building

### Typical constraints & objections
- "We haven’t validated the user pain."
- "This flow will confuse users."
- "We need research / usability testing."

### What good looks like
- Clear target user segment and JTBD
- Research plan (qual/quant) proportional to risk
- Iterative prototyping and testing
- Consideration of accessibility and edge cases

### Red flags
- Solution-first with no validation
- No attention to user journey or usability risk

---

## data — Analytics / Data Science

### Goals
- Ensure measurement is valid and decisions are evidence-driven
- Avoid misleading metrics and confounders
- Design experiments/analysis that answer the question

### Typical constraints & objections
- "This metric doesn’t represent success."
- "We need a baseline and segmentation."
- "This test is confounded / underpowered."

### What good looks like
- Primary KPI + guardrails, with baselines/targets
- Instrumentation plan (events, funnels)
- Sensible experiment/analysis design
- Notes on segmentation and confounders

### Red flags
- Vanity metrics only
- No baseline/target
- Misuse of A/B testing

---

## sales_cs — Sales / Customer Success

### Goals
- Protect revenue and customer relationships
- Communicate changes clearly
- Ensure support readiness and adoption

### Typical constraints & objections
- "This breaks enterprise workflows."
- "We need comms, enablement, and rollout plan."
- "We need migration/compatibility considerations."

### What good looks like
- Customer impact assessment
- Rollout comms plan + enablement (docs, training)
- Mitigation for high-value accounts
- Feedback loop from CS and support

### Red flags
- Ignores change management
- No plan for enterprise customers/support load

---

## exec — Executive / Strategy

### Goals
- Align work to strategy and business outcomes
- Manage opportunity cost and resource allocation
- Ensure narrative clarity and timing (“why now”)

### Typical constraints & objections
- "How does this move the business?"
- "Why now vs later?"
- "What are we not doing because of this?"

### What good looks like
- Crisp framing and strategic alignment
- Explicit opportunity cost and tradeoffs
- Clear success criteria, timeline, and rationale
- Decision is proportional to the bet size

### Red flags
- No strategic link
- Too tactical without “why”
- No opportunity cost discussion