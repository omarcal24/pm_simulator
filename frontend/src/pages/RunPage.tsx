import { useEffect, useRef, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getRun, submitDecision } from '@/api/runs'
import { createFromRun } from '@/api/caseStudies'
import { gradeDecision } from '@/api/grades'
import { getCaseStudyTemplate } from '@/api/template'
import type { Run, DecisionGrade, CaseStudyTemplate } from '@/api/types'
import { Button } from '@/components/Button'
import { Card } from '@/components/Card'
import { MetricBadge } from '@/components/MetricBadge'
import { CaseStudyGuide } from '@/components/CaseStudyGuide'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

const DIMENSION_LABELS: Record<string, string> = {
  problem_framing: 'Problem Framing',
  tradeoffs: 'Tradeoffs',
  evidence_assumptions: 'Evidence & Assumptions',
  execution_realism: 'Execution Realism',
  metrics_success: 'Metrics & Success',
}

function ScoreBar({ score }: { score: number }) {
  const pct = (score / 5) * 100
  const color = score >= 4 ? 'bg-emerald-500' : score >= 3 ? 'bg-primary-500' : score >= 2 ? 'bg-amber-400' : 'bg-rose-400'
  return (
    <div className="flex items-center gap-2">
      <div className="h-2 flex-1 rounded-full bg-slate-200">
        <div className={`h-2 rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="w-6 text-right text-xs font-semibold text-slate-700">{score}</span>
    </div>
  )
}

function GradePanel({ grade }: { grade: DecisionGrade }) {
  if (grade.status === 'failed') {
    return (
      <p className="mt-2 text-sm text-rose-600">
        Grading failed: {grade.error ?? 'Unknown error'}
      </p>
    )
  }
  if (grade.status === 'pending' || !grade.result_json) {
    return <p className="mt-2 text-sm text-slate-500">Grading in progress…</p>
  }
  const r = grade.result_json
  return (
    <div className="mt-3 border-t border-slate-200 pt-3 space-y-4">
      {/* Overall score */}
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold text-slate-900">{r.overall_score.toFixed(1)}</span>
        <span className="text-sm text-slate-500">/ 5.0 overall</span>
        <span className="ml-auto text-xs text-slate-400">confidence {Math.round(r.confidence * 100)}%</span>
      </div>

      {/* Dimension scores */}
      {r.dimension_scores.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Dimension Scores</p>
          <div className="space-y-2">
            {r.dimension_scores.map((dim) => (
              <div key={dim.key}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-slate-600">{DIMENSION_LABELS[dim.key] ?? dim.key}</span>
                  <span className="text-slate-400">{dim.score}/5</span>
                </div>
                <ScoreBar score={dim.score} />
                <p className="mt-1 text-xs text-slate-500">{dim.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strengths */}
      {r.strengths.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wide mb-1">Strengths</p>
          <ul className="space-y-1">
            {r.strengths.map((s, i) => (
              <li key={i} className="text-xs text-slate-700 flex gap-1.5"><span className="text-emerald-600 font-bold shrink-0">✓</span>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Improvements */}
      {r.improvements.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1">Improvements</p>
          <ul className="space-y-1">
            {r.improvements.map((s, i) => (
              <li key={i} className="text-xs text-slate-700 flex gap-1.5"><span className="text-amber-600 shrink-0">→</span>{s}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Red flags */}
      {r.red_flags.length > 0 && (
        <div>
          <p className="text-xs font-semibold text-rose-700 uppercase tracking-wide mb-1">Red Flags</p>
          <ul className="space-y-1">
            {r.red_flags.map((s, i) => (
              <li key={i} className="text-xs text-rose-600 flex gap-1.5"><span className="font-bold shrink-0">!</span>{s}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default function RunPage() {
  const { id } = useParams<{ id: string }>()
  const [run, setRun] = useState<Run | null>(null)
  const [template, setTemplate] = useState<CaseStudyTemplate | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [rationale, setRationale] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [grades, setGrades] = useState<Record<string, DecisionGrade | 'loading'>>({})
  const [expandedDecision, setExpandedDecision] = useState<string | null>(null)
  const rationaleRef = useRef<HTMLTextAreaElement>(null)

  async function fetchRun() {
    if (!id) return
    try {
      const r = await getRun(id)
      setRun(r)
      setError('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load run')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRun()
    getCaseStudyTemplate().then(setTemplate).catch(() => {})
  }, [id])

  function handleInsertTemplate(scaffold: string) {
    setRationale(scaffold)
    rationaleRef.current?.focus()
    rationaleRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!id || !run || run.status !== 'active') return
    setSubmitting(true)
    setError('')
    try {
      await submitDecision(id, {
        decision_type: 'general',
        rationale: rationale || 'Proceeding with current approach.',
      })
      setRationale('')
      await fetchRun()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleGrade(decisionId: string) {
    setGrades((prev) => ({ ...prev, [decisionId]: 'loading' }))
    setExpandedDecision(decisionId)
    try {
      const grade = await gradeDecision(decisionId)
      setGrades((prev) => ({ ...prev, [decisionId]: grade }))
      // Refresh run data so updated metrics and grade_status are reflected
      await fetchRun()
    } catch (err) {
      setGrades((prev) => {
        const next = { ...prev }
        delete next[decisionId]
        return next
      })
    }
  }

  async function handleCreateCaseStudy() {
    if (!id || !run) return
    try {
      const cs = await createFromRun(id)
      window.location.href = `/case-studies/${cs.id}`
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create case study')
    }
  }

  if (loading) return <div className="flex min-h-screen items-center justify-center">Loading...</div>
  if (error && !run) return <div className="p-8 text-rose-600">Error: {error}</div>
  if (!run) return null

  const hasDecisions = (run.decisions?.length ?? 0) > 0
  const snapshots = run.metric_snapshots ?? []
  // snapshot[0] is always the baseline seeded at run creation.
  // Only show live metrics after the user has made at least one decision.
  const baselineMetrics = snapshots.length > 0 ? snapshots[0].metrics : {}
  const latestMetrics = hasDecisions && snapshots.length > 0
    ? snapshots[snapshots.length - 1].metrics
    : {}
  const prevMetrics = hasDecisions && snapshots.length > 1
    ? snapshots[snapshots.length - 2].metrics
    : {}
  // Only show the chart once there are at least 2 snapshots (baseline + 1 decision)
  const chartData = hasDecisions
    ? snapshots.map((m) => ({ step: m.step_number, ...m.metrics }))
    : []

  const decisions = run.decisions ?? []
  const lastDecision = decisions.length > 0 ? decisions[decisions.length - 1] : null
  const lastDecisionGraded = !lastDecision || lastDecision.grade_status === 'succeeded'
  const allDecisionsGraded = decisions.length > 0 && decisions.every((d) => d.grade_status === 'succeeded')
  // True when a decision has been submitted but not yet graded — KPIs are pending
  const pendingGrade = !!lastDecision && lastDecision.grade_status !== 'succeeded'

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
      <main className="mx-auto max-w-5xl px-4 py-8">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="font-display text-2xl font-bold text-slate-900">
            {run.scenario_name} — Run
          </h1>
          <span className="rounded-full bg-slate-200 px-2.5 py-0.5 text-sm font-medium text-slate-700">
            {run.status} · Step {run.step_number}
          </span>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <h2 className="font-display text-lg font-semibold text-slate-900">
                Current Prompt
              </h2>
              <p className="mt-2 whitespace-pre-wrap text-slate-700">
                {typeof run.current_prompt === 'string'
                  ? run.current_prompt
                  : typeof run.state?.prompt === 'string'
                    ? run.state.prompt
                    : 'Make your next decision.'}
              </p>
            </Card>

            {run.status === 'active' && !lastDecisionGraded ? (
              <Card>
                <div className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-100 text-amber-600 font-bold text-sm">!</div>
                  <div>
                    <h2 className="font-display text-lg font-semibold text-slate-900">Grade required</h2>
                    <p className="mt-1 text-sm text-slate-600">
                      Grade your previous decision to see how it impacted the KPIs, then continue to the next step.
                    </p>
                  </div>
                </div>
              </Card>
            ) : run.status === 'active' ? (
              <Card>
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Submit Decision
                </h2>
                <form onSubmit={handleSubmit} className="mt-4 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700">
                      Rationale
                    </label>
                    <textarea
                      ref={rationaleRef}
                      value={rationale}
                      onChange={(e) => setRationale(e.target.value)}
                      rows={8}
                      className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 font-mono text-sm"
                      placeholder="Explain your decision and reasoning..."
                    />
                    {template && !rationale && (
                      <button
                        type="button"
                        onClick={() => handleInsertTemplate(
                          template.sections
                            .map((s) => `## ${s.title}\n${s.placeholder}`)
                            .join('\n\n')
                        )}
                        className="mt-1 text-xs text-primary-600 hover:text-primary-800 underline"
                      >
                        Insert template scaffold
                      </button>
                    )}
                  </div>
                  <Button type="submit" disabled={submitting}>
                    {submitting ? 'Submitting...' : 'Submit'}
                  </Button>
                </form>
              </Card>
            ) : run.status === 'completed' ? (
              <Card>
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Run Complete
                </h2>
                {allDecisionsGraded ? (
                  <>
                    <p className="mt-2 text-slate-600">
                      All decisions graded. Create a case study to capture your learnings and
                      export it for your portfolio.
                    </p>
                    <Button className="mt-4" onClick={handleCreateCaseStudy}>
                      Create Case Study
                    </Button>
                  </>
                ) : (
                  <>
                    <p className="mt-2 text-slate-600">
                      Grade all your decisions to unlock the case study.
                    </p>
                    <p className="mt-1 text-sm text-amber-600">
                      {decisions.filter((d) => d.grade_status !== 'succeeded').length} decision(s) still need grading.
                    </p>
                  </>
                )}
              </Card>
            ) : null}

            {run.events?.length > 0 && (
              <Card>
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Timeline
                </h2>
                <ul className="mt-4 space-y-2">
                  {run.events.map((ev) => (
                    <li
                      key={ev.id}
                      className="flex gap-3 rounded-lg bg-slate-50 p-3 text-sm"
                    >
                      <span className="shrink-0 font-medium text-slate-500">
                        Step {ev.step_number}
                      </span>
                      <span className="text-slate-700">{ev.message}</span>
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {run.decisions?.length > 0 && (
              <Card>
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Decisions
                </h2>
                <ul className="mt-4 space-y-3">
                  {run.decisions.map((d) => {
                    const grade = grades[d.id]
                    const isExpanded = expandedDecision === d.id
                    return (
                      <li key={d.id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                        <div className="flex items-start justify-between gap-3">
                          <div className="min-w-0">
                            <span className="text-xs font-medium text-slate-500">
                              Step {d.step_number} · {d.decision_type}
                            </span>
                            <p className="mt-0.5 text-sm text-slate-700 line-clamp-2">
                              {d.rationale}
                            </p>
                          </div>
                          <div className="shrink-0 flex gap-2 items-center">
                            {grade && grade !== 'loading' && grade.result_json && (
                              <span className="text-sm font-semibold text-slate-700">
                                {grade.result_json.overall_score.toFixed(1)}/5
                              </span>
                            )}
                            <Button
                              size="sm"
                              variant={grade && grade !== 'loading' ? 'outline' : 'primary'}
                              disabled={grade === 'loading'}
                              onClick={() =>
                                isExpanded && grade
                                  ? setExpandedDecision(null)
                                  : grade && grade !== 'loading'
                                  ? setExpandedDecision(isExpanded ? null : d.id)
                                  : handleGrade(d.id)
                              }
                            >
                              {grade === 'loading'
                                ? 'Grading…'
                                : grade
                                ? isExpanded ? 'Hide' : 'Show grade'
                                : 'Grade'}
                            </Button>
                          </div>
                        </div>
                        {isExpanded && grade && grade !== 'loading' && (
                          <GradePanel grade={grade} />
                        )}
                      </li>
                    )
                  })}
                </ul>
              </Card>
            )}
          </div>

          <div className="space-y-6">
            {template && (
              <CaseStudyGuide
                template={template}
                onInsertTemplate={run.status === 'active' ? handleInsertTemplate : undefined}
                defaultOpen={false}
              />
            )}

            {run.scenario_context && (
              <Card>
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Scenario
                </h2>
                {run.scenario_difficulty && (
                  <span className="mt-1 inline-block rounded-full bg-slate-200 px-2.5 py-0.5 text-xs font-medium text-slate-700">
                    {run.scenario_difficulty}
                  </span>
                )}
                {run.scenario_learning_objectives && run.scenario_learning_objectives.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {run.scenario_learning_objectives.map((lo) => (
                      <span
                        key={lo.id}
                        className="rounded bg-primary-50 px-2 py-0.5 text-xs text-primary-700"
                      >
                        {lo.name}
                      </span>
                    ))}
                  </div>
                )}
                <p className="mt-3 text-sm text-slate-600 whitespace-pre-wrap">
                  {run.scenario_context}
                </p>
              </Card>
            )}

            <Card>
              <div className="flex items-center justify-between">
                <h2 className="font-display text-lg font-semibold text-slate-900">KPIs</h2>
                <span className="text-xs text-slate-400">0–100 index</span>
              </div>
              {!hasDecisions ? (
                <div className="mt-3">
                  <p className="text-xs text-slate-500 mb-2">Baseline (before any decision)</p>
                  <div className="grid grid-cols-2 gap-3">
                    {run.kpis?.map((kpi) => (
                      <MetricBadge
                        key={kpi}
                        label={kpi.replace(/_/g, ' ')}
                        value={baselineMetrics[kpi] ?? '—'}
                      />
                    ))}
                  </div>
                  <p className="mt-3 text-xs text-slate-400 italic">
                    Submit your first decision to see how metrics change.
                  </p>
                </div>
              ) : pendingGrade ? (
                <div className="mt-3">
                  <div className="grid grid-cols-2 gap-3">
                    {run.kpis?.map((kpi) => (
                      <div key={kpi} className="rounded-lg bg-slate-100 px-3 py-2">
                        <div className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">
                          {kpi.replace(/_/g, ' ')}
                        </div>
                        <div className="h-6 w-16 rounded bg-slate-200 animate-pulse" />
                      </div>
                    ))}
                  </div>
                  <p className="mt-3 text-xs text-slate-500 italic">
                    Grade your decision to see KPI impact.
                  </p>
                </div>
              ) : (
                <div className="mt-4 grid grid-cols-2 gap-3">
                  {run.kpis?.map((kpi) => {
                    const val = latestMetrics[kpi]
                    const prev = prevMetrics[kpi]
                    const delta = prev != null && val != null ? Math.round((val - prev) * 100) / 100 : undefined
                    return (
                      <MetricBadge
                        key={kpi}
                        label={kpi.replace(/_/g, ' ')}
                        value={val ?? '—'}
                        delta={delta}
                      />
                    )
                  })}
                </div>
              )}
            </Card>

            {chartData.length > 0 && !pendingGrade && (
              <Card>
                <h2 className="font-display text-lg font-semibold text-slate-900">
                  Metrics Over Time
                </h2>
                <div className="mt-4 h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="step" stroke="#64748b" fontSize={12} />
                      <YAxis stroke="#64748b" fontSize={12} />
                      <Tooltip />
                      {run.kpis?.map((kpi, i) => (
                        <Line
                          key={kpi}
                          type="monotone"
                          dataKey={kpi}
                          stroke={['#0ea5e9', '#10b981', '#f59e0b'][i % 3]}
                          strokeWidth={2}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </Card>
            )}
          </div>
        </div>

        {error && (
          <p className="mt-4 text-sm text-rose-600">{error}</p>
        )}
      </main>
    </div>
  )
}
