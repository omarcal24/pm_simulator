import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getCaseStudy, updateSections, exportCaseStudy, exportLearningReport } from '@/api/caseStudies'
import type { CaseStudy } from '@/api/types'
import { Button } from '@/components/Button'
import { Card } from '@/components/Card'

export default function CaseStudyPage() {
  const { id } = useParams<{ id: string }>()
  const [caseStudy, setCaseStudy] = useState<CaseStudy | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [exported, setExported] = useState<string | null>(null)
  const [exportingReport, setExportingReport] = useState(false)

  useEffect(() => {
    if (!id) return
    getCaseStudy(id)
      .then(setCaseStudy)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  async function handleSave() {
    if (!id || !caseStudy) return
    setSaving(true)
    try {
      await updateSections(
        id,
        caseStudy.sections.map((s) => ({ key: s.key, content: s.content }))
      )
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  async function handleExport() {
    if (!id) return
    try {
      const { markdown, title } = await exportCaseStudy(id)
      const blob = new Blob([markdown], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${title.replace(/\s+/g, '-')}.md`
      a.click()
      URL.revokeObjectURL(url)
      setExported(title)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export')
    }
  }

  async function handleDownloadLearningReport() {
    if (!id) return
    setExportingReport(true)
    try {
      const { markdown, title } = await exportLearningReport(id)
      const blob = new Blob([markdown], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `learning-report-${title.replace(/\s+/g, '-')}.md`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export learning report')
    } finally {
      setExportingReport(false)
    }
  }

  function updateSection(key: string, content: string) {
    if (!caseStudy) return
    setCaseStudy({
      ...caseStudy,
      sections: caseStudy.sections.map((s) =>
        s.key === key ? { ...s, content } : s
      ),
    })
  }

  if (loading) return <div className="flex min-h-screen items-center justify-center">Loading...</div>
  if (error && !caseStudy) return <div className="p-8 text-rose-600">Error: {error}</div>
  if (!caseStudy) return null

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link to="/" className="font-display text-xl font-semibold text-slate-900">
            Product Management Simulator
          </Link>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </Button>
            <Button onClick={handleExport}>Export Case Study</Button>
            <Button variant="secondary" onClick={handleDownloadLearningReport} disabled={exportingReport}>
              {exportingReport ? 'Exporting...' : 'Download Learning Report'}
            </Button>
            <Link to="/scenarios">
              <Button variant="ghost">← Scenarios</Button>
            </Link>
          </div>
        </div>
      </nav>
      <main className="mx-auto max-w-3xl px-4 py-8">
        {exported && (
          <div className="mb-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700">
            Exported: {exported}
          </div>
        )}
        <h1 className="font-display text-2xl font-bold text-slate-900">
          {caseStudy.title}
        </h1>
        <p className="mt-1 text-sm text-slate-600">
          Edit your case study below. Auto-generated sections are marked.
        </p>
        <div className="mt-8 space-y-6">
          {caseStudy.sections.map((section) => (
            <Card key={section.id}>
              <div className="flex items-center justify-between">
                <h2 className="font-display text-lg font-semibold text-slate-900 capitalize">
                  {section.key.replace(/_/g, ' ')}
                </h2>
                {section.is_auto_generated && (
                  <span className="text-xs text-slate-500">Auto-generated</span>
                )}
              </div>
              <textarea
                value={section.content}
                onChange={(e) => updateSection(section.key, e.target.value)}
                rows={Math.min(12, section.content.split('\n').length + 2)}
                className="mt-3 w-full rounded-lg border border-slate-300 px-3 py-2 font-mono text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </Card>
          ))}
        </div>
        {error && <p className="mt-4 text-sm text-rose-600">{error}</p>}
      </main>
    </div>
  )
}
