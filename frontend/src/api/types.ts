export interface Scenario {
  id: string
  name: string
  version: number
  difficulty: string
  context: string
  config: Record<string, unknown>
  learning_objectives: { id: string; name: string; description?: string }[]
  kpis: string[]
}

export interface Run {
  id: string
  scenario: string
  scenario_name: string
  scenario_context?: string
  scenario_difficulty?: string
  scenario_learning_objectives?: { id: string; name: string; description?: string }[]
  status: string
  step_number: number
  state: Record<string, unknown>
  seed: number
  started_at: string
  completed_at: string | null
  current_prompt?: string
  kpis: string[]
  decisions: Decision[]
  events: RunEvent[]
  metric_snapshots: MetricSnapshot[]
}

export interface Decision {
  id: string
  step_number: number
  decision_type: string
  rationale: string
  created_at: string
  grade_status: 'succeeded' | 'pending' | null
}

export interface RunEvent {
  id: string
  step_number: number
  type: string
  severity: string
  actor: string
  message: string
}

export interface MetricSnapshot {
  id: string
  step_number: number
  metrics: Record<string, number>
  created_at: string
}

export interface DimensionScore {
  key: string
  score: number
  reason: string
}

export interface RoleScore {
  role: string
  score: number
  reason: string
}

export interface GradeGates {
  has_clear_recommendation: boolean
  mentions_constraints: boolean
  mentions_success_metrics: boolean
  mentions_risks_and_mitigation: boolean
  compares_alternatives: boolean
}

export interface GradeResult {
  rubric_version: string
  overall_score: number
  universal_score: number
  dimension_scores: DimensionScore[]
  role_scores: RoleScore[]
  gates: GradeGates
  strengths: string[]
  improvements: string[]
  red_flags: string[]
  confidence: number
}

export interface DecisionGrade {
  id: string
  decision: string
  run: string
  rubric_version: string
  model_name: string
  temperature: number
  status: 'pending' | 'succeeded' | 'failed'
  result_json: GradeResult | null
  error: string | null
  latency_ms: number | null
  created_at: string
  updated_at: string
}

// ── Case Study Template ───────────────────────────────────────────────────────

export interface TemplateSection {
  key: string
  title: string
  description: string
  guiding_questions: string[]
  placeholder: string
  required: boolean
}

export interface ScoringDimension {
  key: string
  label: string
  description: string
  good_signals: string[]
}

export interface RoleOverride {
  label: string
  focus_note: string
  section_hints: Record<string, string>
  what_we_look_for: string[]
}

export interface WhatSystemExpects {
  summary: string
  expectations: string[]
  always_expected: string[]
  valued_but_not_required: string[]
}

export interface CaseStudyTemplate {
  version: string
  sections: TemplateSection[]
  what_system_expects: WhatSystemExpects
  scoring_dimensions: ScoringDimension[]
  scale: Record<string, string>
  scoring_notes: string[]
  role_overrides: Record<string, RoleOverride>
  example_good_outline: { title: string; note: string; content: string }
  active_role_override?: RoleOverride
}

export interface CaseStudy {
  id: string
  run: string
  scenario: string
  title: string
  status: string
  sections: CaseStudySection[]
  created_at: string
  updated_at: string
}

export interface CaseStudySection {
  id: string
  key: string
  content: string
  is_auto_generated: boolean
}
