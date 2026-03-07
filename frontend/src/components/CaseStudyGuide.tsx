import { useState } from 'react'
import type { CaseStudyTemplate, RoleOverride } from '@/api/types'

interface Props {
  template: CaseStudyTemplate
  roleOverride?: RoleOverride
  onInsertTemplate?: (scaffold: string) => void
  defaultOpen?: boolean
}

function buildScaffold(template: CaseStudyTemplate, roleOverride?: RoleOverride): string {
  return template.sections
    .map((section) => {
      const hint = roleOverride?.section_hints?.[section.key]
      const lines = [`## ${section.title}`]
      if (hint) {
        lines.push(`[${hint}]`)
      } else {
        lines.push(`[${section.placeholder}]`)
      }
      return lines.join('\n')
    })
    .join('\n\n')
}

export function CaseStudyGuide({ template, roleOverride, onInsertTemplate, defaultOpen = false }: Props) {
  const [open, setOpen] = useState(defaultOpen)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)

  const activeOverride = roleOverride ?? template.active_role_override

  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-5 py-4 text-left"
      >
        <div className="flex items-center gap-2">
          <span className="text-base font-semibold text-slate-900 font-display">Case study template</span>
          {activeOverride && (
            <span className="rounded-full bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-700">
              {activeOverride.label}
            </span>
          )}
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
            {template.sections.length} sections
          </span>
        </div>
        <span className="text-slate-400 text-lg">{open ? '−' : '+'}</span>
      </button>

      {open && (
        <div className="border-t border-slate-100 px-5 pb-5">
          {/* Role-specific focus note */}
          {activeOverride && (
            <div className="mt-4 rounded-lg bg-violet-50 border border-violet-100 p-3">
              <p className="text-xs font-semibold text-violet-800 mb-1">{activeOverride.label} guidance</p>
              <p className="text-xs text-violet-700">{activeOverride.focus_note}</p>
              {activeOverride.what_we_look_for.length > 0 && (
                <ul className="mt-2 space-y-0.5">
                  {activeOverride.what_we_look_for.map((item, i) => (
                    <li key={i} className="text-xs text-violet-700 flex gap-1.5">
                      <span className="shrink-0 font-bold">→</span>
                      {item}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* What's always expected */}
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="rounded-lg bg-emerald-50 border border-emerald-100 p-3">
              <p className="text-xs font-semibold text-emerald-800 mb-1">Always expected</p>
              <ul className="space-y-0.5">
                {template.what_system_expects.always_expected.map((item, i) => (
                  <li key={i} className="text-xs text-emerald-700 flex gap-1.5">
                    <span className="shrink-0">✓</span>{item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-lg bg-slate-50 border border-slate-100 p-3">
              <p className="text-xs font-semibold text-slate-600 mb-1">Optional</p>
              <ul className="space-y-0.5">
                {template.what_system_expects.valued_but_not_required.map((item, i) => (
                  <li key={i} className="text-xs text-slate-500 flex gap-1.5">
                    <span className="shrink-0">·</span>{item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Section list */}
          <div className="mt-4 space-y-1.5">
            {template.sections.map((section) => {
              const isExpanded = expandedSection === section.key
              const hint = activeOverride?.section_hints?.[section.key]
              return (
                <div
                  key={section.key}
                  className="rounded-lg border border-slate-200"
                >
                  <button
                    onClick={() => setExpandedSection(isExpanded ? null : section.key)}
                    className="flex w-full items-center justify-between px-3 py-2.5 text-left"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-slate-800">{section.title}</span>
                      {section.required && (
                        <span className="rounded bg-primary-100 px-1.5 py-0.5 text-xs font-medium text-primary-700">
                          required
                        </span>
                      )}
                      {hint && (
                        <span className="rounded bg-violet-100 px-1.5 py-0.5 text-xs font-medium text-violet-600">
                          role hint
                        </span>
                      )}
                    </div>
                    <span className="text-slate-400 text-sm">{isExpanded ? '−' : '+'}</span>
                  </button>

                  {isExpanded && (
                    <div className="border-t border-slate-100 px-3 pb-3">
                      {hint && (
                        <div className="mt-2 rounded bg-violet-50 px-2.5 py-2 text-xs text-violet-700 border border-violet-100">
                          <span className="font-semibold">Role guidance: </span>{hint}
                        </div>
                      )}
                      <p className="mt-2 text-xs text-slate-600">{section.description}</p>
                      <ul className="mt-2 space-y-1">
                        {section.guiding_questions.map((q, i) => (
                          <li key={i} className="text-xs text-slate-500 flex gap-1.5">
                            <span className="shrink-0 font-semibold text-slate-400">Q{i + 1}</span>
                            {q}
                          </li>
                        ))}
                      </ul>
                      <p className="mt-2 text-xs text-slate-400 italic">{section.placeholder}</p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>

          {/* Insert template button */}
          {onInsertTemplate && (
            <button
              onClick={() => onInsertTemplate(buildScaffold(template, activeOverride))}
              className="mt-4 w-full rounded-lg border border-dashed border-slate-300 px-4 py-2.5 text-sm text-slate-600 hover:border-primary-400 hover:text-primary-700 hover:bg-primary-50 transition-colors"
            >
              Insert template scaffold into editor →
            </button>
          )}
        </div>
      )}
    </div>
  )
}
