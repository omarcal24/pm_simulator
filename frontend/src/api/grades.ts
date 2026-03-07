import { api } from './client'
import type { DecisionGrade } from './types'

export async function getDecisionGrade(decisionId: string): Promise<DecisionGrade> {
  return api.get<DecisionGrade>(`/decisions/${decisionId}/grade/`)
}

export async function gradeDecision(decisionId: string): Promise<DecisionGrade> {
  return api.post<DecisionGrade>(`/decisions/${decisionId}/grade/`, {})
}
