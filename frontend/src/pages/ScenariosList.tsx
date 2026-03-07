import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { listScenarios } from '@/api/scenarios'
import type { Scenario } from '@/api/types'
import { Button } from '@/components/Button'
import { Card } from '@/components/Card'

export default function ScenariosList() {
  const navigate = useNavigate()
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    listScenarios()
      .then(setScenarios)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="flex min-h-screen items-center justify-center">Loading...</div>
  if (error) return <div className="p-8 text-rose-600">Error: {error}</div>

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link to="/" className="font-display text-xl font-semibold text-slate-900">
            Product Management Simulator
          </Link>
          <Link to="/">
            <Button variant="ghost">← Home</Button>
          </Link>
        </div>
      </nav>
      <main className="mx-auto max-w-4xl px-4 py-12">
        <h1 className="font-display text-3xl font-bold text-slate-900">
          Scenarios
        </h1>
        <p className="mt-2 text-slate-600">
          Choose a scenario to run. You'll make decisions across multiple turns
          and receive feedback on your KPIs.
        </p>
        <div className="mt-8 space-y-4">
          {scenarios.length === 0 ? (
            <Card>
              <p className="text-slate-600">
                No scenarios yet. Seed the database with:{' '}
                <code className="rounded bg-slate-100 px-1.5 py-0.5">
                  python manage.py seed_scenarios
                </code>
              </p>
            </Card>
          ) : (
            scenarios.map((s) => (
              <Card key={s.id} className="hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="font-display text-lg font-semibold text-slate-900">
                      {s.name}
                    </h2>
                    <span className="mt-1 inline-block rounded-full bg-slate-200 px-2.5 py-0.5 text-xs font-medium text-slate-700">
                      {s.difficulty}
                    </span>
                    <p className="mt-2 text-sm text-slate-600 line-clamp-2">
                      {s.context.replace(/^#+.*$/gm, '').trim().slice(0, 150)}...
                    </p>
                    {s.learning_objectives?.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {s.learning_objectives.map((lo) => (
                          <span
                            key={lo.id}
                            className="rounded bg-primary-50 px-2 py-0.5 text-xs text-primary-700"
                          >
                            {lo.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex shrink-0 gap-2">
                    <Link to={`/scenarios/${s.id}`}>
                      <Button variant="outline" size="sm">View</Button>
                    </Link>
                    <Button
                      size="sm"
                      onClick={() => navigate(`/scenarios/${s.id}`, { state: { autoStart: true } })}
                    >
                      Start
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </main>
    </div>
  )
}
