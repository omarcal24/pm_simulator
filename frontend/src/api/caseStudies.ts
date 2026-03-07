import { api } from './client'
import type { CaseStudy } from './types'

export async function createFromRun(runId: string): Promise<CaseStudy & { sections: { key: string; content: string }[] }> {
  return api.post(`/case-studies/from-run/${runId}/`, {})
}

export async function getCaseStudy(id: string): Promise<CaseStudy> {
  return api.get<CaseStudy>(`/case-studies/${id}/`)
}

export async function updateCaseStudy(id: string, data: Partial<CaseStudy>): Promise<CaseStudy> {
  return api.patch<CaseStudy>(`/case-studies/${id}/`, data)
}

export async function updateSections(id: string, sections: { key: string; content: string }[]): Promise<CaseStudy> {
  return api.patch<CaseStudy>(`/case-studies/${id}/sections/`, { sections })
}

export async function exportCaseStudy(id: string): Promise<{ markdown: string; title: string }> {
  return api.get<{ markdown: string; title: string }>(`/case-studies/${id}/export/`)
}

export async function exportLearningReport(id: string): Promise<{ markdown: string; title: string }> {
  return api.get<{ markdown: string; title: string }>(`/case-studies/${id}/learning-report/`)
}
