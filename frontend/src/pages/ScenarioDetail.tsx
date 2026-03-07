import { useEffect, useState } from 'react'
import { useParams, useNavigate, useLocation, Link } from 'react-router-dom'
import { useAuth } from '@/features/simulation/hooks/useAuth'
import { getScenario } from '@/api/scenarios'
import { createRun } from '@/api/runs'
import { getCaseStudyTemplate } from '@/api/template'
import type { Scenario, CaseStudyTemplate } from '@/api/types'
import { Button } from '@/components/Button'
import { Card } from '@/components/Card'
import { CaseStudyGuide } from '@/components/CaseStudyGuide'
import { ScoringExplainer } from '@/components/ScoringExplainer'

export default function ScenarioDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const { user } = useAuth()
  const [scenario, setScenario] = useState<Scenario | null>(null)
  const [template, setTemplate] = useState<CaseStudyTemplate | null>(null)
  const [loading, setLoading] = useState(true)
  const [starting, setStarting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    Promise.all([
      getScenario(id),
      getCaseStudyTemplate(),
    ])
      .then(([s, t]) => { setScenario(s); setTemplate(t) })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    if (scenario && user && (location.state as { autoStart?: boolean })?.autoStart) {
      handleStart()
    }
  }, [scenario, user])

  async function handleStart() {
    if (!id || !user) return
    setStarting(true)
    setError('')
    try {
      const run = await createRun(id)
      navigate(`/runs/${run.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start run')
    } finally {
      setStarting(false)
    }
  }

  if (loading) return <div className="flex min-h-screen items-center justify-center">Loading...</div>
  if (error || !scenario) return <div className="p-8 text-rose-600">Error: {error || 'Not found'}</div>

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link to="/" className="font-display text-xl font-semibold text-slate-900">
            Product Management Simulator
          </Link>
          <Link to="/scenarios">
            <Button variant="ghost">← Scenarios</Button>
          </Link>
        </div>
      </nav>

      <main className="mx-auto max-w-3xl px-4 py-12">
        {/* Header */}
        <div className="mb-6 flex items-center gap-3">
          <span className="rounded-full bg-slate-200 px-2.5 py-0.5 text-sm font-medium text-slate-700">
            {scenario.difficulty}
          </span>
          {scenario.kpis?.length > 0 && (
            <span className="text-sm text-slate-600">
              KPIs: {scenario.kpis.join(', ')}
            </span>
          )}
        </div>
        <h1 className="font-display text-3xl font-bold text-slate-900">
          {scenario.name}
        </h1>
        {scenario.learning_objectives?.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {scenario.learning_objectives.map((lo) => (
              <span
                key={lo.id}
                className="rounded bg-primary-50 px-2.5 py-1 text-sm text-primary-700"
              >
                {lo.name}
              </span>
            ))}
          </div>
        )}

        {/* Scenario context */}
        <Card className="mt-8">
          <div
            className="prose prose-slate max-w-none prose-headings:font-display prose-headings:font-semibold"
            dangerouslySetInnerHTML={{
              __html: scenario.context
                .replace(/\n/g, '<br/>')
                .replace(/^## (.+)$/gm, '<h2>$1</h2>')
                .replace(/^### (.+)$/gm, '<h3>$1</h3>')
                .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>'),
            }}
          />
        </Card>

        {/* Pre-run guidance */}
        {template && (
          <div className="mt-6 space-y-3">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide px-1">
              Before you start
            </p>
            <ScoringExplainer template={template} />
            <CaseStudyGuide template={template} />
          </div>
        )}

        {/* Start button */}
        <div className="mt-8">
          {user ? (
            <Button size="lg" onClick={handleStart} disabled={starting}>
              {starting ? 'Starting...' : 'Start Run'}
            </Button>
          ) : (
            <Link to="/login">
              <Button size="lg">Sign in to Start</Button>
            </Link>
          )}
          {error && (
            <p className="mt-2 text-sm text-rose-600">{error}</p>
          )}
        </div>
      </main>
    </div>
  )
}
