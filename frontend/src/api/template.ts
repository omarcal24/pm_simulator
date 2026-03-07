import { api } from './client'
import type { CaseStudyTemplate } from './types'

export async function getCaseStudyTemplate(role?: string): Promise<CaseStudyTemplate> {
  const params = role ? `?role=${encodeURIComponent(role)}` : ''
  return api.get<CaseStudyTemplate>(`/template/${params}`)
}
