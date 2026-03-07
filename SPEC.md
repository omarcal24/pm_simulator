# PM Simulator — Product Spec (MVP)

## Problem
Aspiring PMs struggle to get realistic experience and build credible portfolios. Traditional case studies are static and don’t show decision-making under constraints, stakeholder conflict, or iteration.

## Solution
A simulation-based practice environment (“PM flight simulator”) where users complete scenario runs, make decisions across multiple turns, and automatically generate a portfolio-ready case study based on their decisions, events, and metrics.

## Target users
- **Primary:** Aspiring / early-career PMs
- **Secondary:** Career switchers preparing for PM interviews
- **Tertiary:** Bootcamps / educators (institutional use later)

## Core user flows

### Flow A — Run a scenario
1. Browse scenarios
2. View scenario details (context, objectives, KPIs, difficulty)
3. Start run
4. For each turn:
   - read prompt + constraints + KPIs
   - submit decision + rationale + risks/assumptions
   - review events + KPI changes + feedback
5. Finish run → receive debrief

### Flow B — Generate case study
1. Create case study from a completed run
2. Auto-filled draft appears (template sections)
3. User edits/refines narrative
4. Export (Markdown first; PDF later)

## MVP scope (must-have)
- Scenarios list + detail
- Start run
- Turn-based decision submission
- Engine produces events + metric snapshots + next prompt
- Run history timeline
- Create case study draft from run history
- Case study editor (basic)
- Authentication (basic)

## Non-goals (MVP)
- Perfect multi-agent realism
- Real-time multiplayer runs
- “Anything goes” freeform prompts without structure
- AI-generated full portfolio text with minimal user contribution (portfolio trust risk)

## Data model (high-level)
- Scenario → Run → Decision → Event + MetricSnapshot
- Run → CaseStudy → CaseStudySection(s)

## Success criteria
- Users can complete a run end-to-end
- Case study output is coherent and references run history
- Run is replayable/auditable (seed + stored inputs/outputs per step)
- Time-to-first-case-study < 30 minutes for a short scenario

## Future extensions
- Scenario marketplace / authoring tools
- Rubric scoring + skill progression
- Export to PDF / Docx
- Bootcamp/institution mode (cohorts, grading)