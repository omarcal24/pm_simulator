import { api } from './client'
import type { Run } from './types'

export async function createRun(scenarioId: string): Promise<Run> {
  return api.post<Run>('/runs/', { scenario_id: scenarioId })
}

export async function getRun(id: string): Promise<Run> {
  return api.get<Run>(`/runs/${id}/`)
}

export async function submitDecision(
  runId: string,
  decision: {
    decision_type: string
    choice_id?: string
    rationale: string
    assumptions?: string[]
    risks?: string[]
    artifacts?: Record<string, unknown>
  }
) {
  return api.post<{
    run_id: string
    step_number: number
    events: { type: string; severity: string; actor: string; message: string }[]
    metrics: Record<string, number>
    next_prompt: string
    is_complete: boolean
  }>(`/runs/${runId}/decisions/`, decision)
}
