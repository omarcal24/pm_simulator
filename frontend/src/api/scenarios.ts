import { api } from './client'
import type { Scenario } from './types'

export async function listScenarios(): Promise<Scenario[]> {
  return api.get<Scenario[]>('/scenarios/')
}

export async function getScenario(id: string): Promise<Scenario> {
  return api.get<Scenario>(`/scenarios/${id}/`)
}
