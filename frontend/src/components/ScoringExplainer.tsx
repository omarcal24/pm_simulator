import { useState } from 'react'
import type { CaseStudyTemplate } from '@/api/types'

interface Props {
  template: CaseStudyTemplate
  defaultOpen?: boolean
}

export function ScoringExplainer({ template, defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen)

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-5 py-4 text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-base font-semibold text-slate-900 font-display">How you'll be evaluated</span>
          <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
            {template.scoring_dimensions.length} dimensions
          </span>
        </div>
        <span className="text-slate-400 text-lg">{open ? '−' : '+'}</span>
      </button>

      {open && (
        <div className="border-t border-slate-100 px-5 pb-5">
          {/* What we look for */}
          <div className="mt-4">
            <p className="text-sm text-slate-600">{template.what_system_expects.summary}</p>
          </div>

          {/* Scoring dimensions */}
          <div className="mt-5 space-y-3">
            {template.scoring_dimensions.map((dim) => (
              <div key={dim.key} className="rounded-lg bg-slate-50 p-3">
                <p className="text-sm font-semibold text-slate-800">{dim.label}</p>
                <p className="mt-0.5 text-xs text-slate-500">{dim.description}</p>
                {dim.good_signals.length > 0 && (
                  <ul className="mt-1.5 space-y-0.5">
                    {dim.good_signals.map((s, i) => (
                      <li key={i} className="text-xs text-slate-600 flex gap-1.5">
                        <span className="text-emerald-500 shrink-0">✓</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>

          {/* Score scale */}
          <div className="mt-5">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Score scale (0–5)</p>
            <div className="space-y-1">
              {Object.entries(template.scale)
                .sort(([a], [b]) => Number(b) - Number(a))
                .map(([score, label]) => (
                  <div key={score} className="flex gap-3 text-xs">
                    <span className="w-4 font-bold text-slate-700 shrink-0">{score}</span>
                    <span className="text-slate-500">{label}</span>
                  </div>
                ))}
            </div>
          </div>

          {/* Scoring notes */}
          <div className="mt-4 rounded-lg bg-amber-50 border border-amber-100 p-3">
            <p className="text-xs font-semibold text-amber-800 mb-1">Good to know</p>
            <ul className="space-y-1">
              {template.scoring_notes.map((note, i) => (
                <li key={i} className="text-xs text-amber-700 flex gap-1.5">
                  <span className="shrink-0">·</span>
                  {note}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
