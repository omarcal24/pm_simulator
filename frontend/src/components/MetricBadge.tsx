interface MetricBadgeProps {
  label: string
  value: number | string
  delta?: number
}

export function MetricBadge({ label, value, delta }: MetricBadgeProps) {
  return (
    <div className="rounded-lg bg-slate-100 px-3 py-2">
      <div className="text-xs font-medium text-slate-500 uppercase tracking-wide truncate">
        {label}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-lg font-semibold text-slate-900">
          {typeof value === 'number' ? value.toFixed(2) : value}
        </span>
        {delta !== undefined && (
          <span
            className={`text-sm ${
              delta > 0 ? 'text-emerald-600' : delta < 0 ? 'text-rose-600' : 'text-slate-500'
            }`}
          >
            {delta > 0 ? '+' : ''}{delta} pts
          </span>
        )}
      </div>
    </div>
  )
}
