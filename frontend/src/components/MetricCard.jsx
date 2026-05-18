export default function MetricCard({ icon: Icon, label, value, suffix = "", hint }) {
  return (
    <div className="card !p-5 card-hover">
      <div className="flex items-center justify-between">
        <div className="text-xs font-semibold uppercase tracking-widest text-clinical-muted">
          {label}
        </div>
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-700 flex items-center justify-center">
            <Icon className="w-4 h-4" strokeWidth={2.2} />
          </div>
        )}
      </div>
      <div className="mt-3 flex items-baseline gap-1">
        <div className="text-2xl md:text-3xl font-extrabold tracking-tight text-clinical-ink">
          {value}
        </div>
        {suffix && <div className="text-sm font-semibold text-clinical-muted">{suffix}</div>}
      </div>
      {hint && <div className="mt-1 text-xs text-clinical-muted">{hint}</div>}
    </div>
  );
}
