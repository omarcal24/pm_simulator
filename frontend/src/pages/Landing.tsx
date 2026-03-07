import { Link } from 'react-router-dom'
import { useAuth } from '@/features/simulation/hooks/useAuth'
import { Button } from '@/components/Button'

export default function Landing() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen">
      <nav className="border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <span className="font-display text-xl font-semibold text-slate-900">
            Product Management Simulator
          </span>
          <div className="flex gap-3">
            {user ? (
              <Link to="/scenarios">
                <Button>Browse Scenarios</Button>
              </Link>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost">Log in</Button>
                </Link>
                <Link to="/scenarios">
                  <Button>Browse Scenarios</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
      <main className="mx-auto max-w-4xl px-4 py-20 text-center">
        <h1 className="font-display text-5xl font-bold tracking-tight text-slate-900">
          Practice Product Management Like a Pro
        </h1>
        <p className="mt-6 text-xl text-slate-600">
          Run realistic scenarios, make decisions under pressure, and generate
          portfolio-ready case studies for interviews.
        </p>
        <div className="mt-10 flex justify-center gap-4">
          <Link to="/scenarios">
            <Button size="lg">Browse Scenarios</Button>
          </Link>
          {!user && (
            <Link to="/login">
              <Button size="lg" variant="outline">
                Sign in
              </Button>
            </Link>
          )}
        </div>
        <div className="mt-20 grid gap-8 md:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-left shadow-sm">
            <h3 className="font-display text-lg font-semibold text-slate-900">
              Turn-based decisions
            </h3>
            <p className="mt-2 text-slate-600">
              Submit decisions with rationale, assumptions, and risks. See how
              the simulated world responds.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-left shadow-sm">
            <h3 className="font-display text-lg font-semibold text-slate-900">
              KPI feedback
            </h3>
            <p className="mt-2 text-slate-600">
              Track activation, retention, and more. Every decision affects your
              metrics.
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-left shadow-sm">
            <h3 className="font-display text-lg font-semibold text-slate-900">
              Portfolio case studies
            </h3>
            <p className="mt-2 text-slate-600">
              Auto-generate a case study draft from your run. Edit and export to
              Markdown.
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
