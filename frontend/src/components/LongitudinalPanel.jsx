import { useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Heart, Loader2, TrendingDown } from "lucide-react";
import {
  computeLongitudinal, fetchLongitudinalSlice,
} from "../lib/api.js";
import MetricCard from "./MetricCard.jsx";

const PANELS = [
  { key: "pre",       label: "Pre-treatment" },
  { key: "post",      label: "Post-treatment" },
  { key: "recovered", label: "Recovered tissue" },
];

export default function LongitudinalPanel({ caseId, nSlices, suggestedSlice }) {
  const [eff, setEff] = useState(0.30);
  const [data, setData] = useState(null);
  const [busy, setBusy] = useState(false);
  const [z, setZ] = useState(suggestedSlice ?? Math.floor((nSlices ?? 1) / 2));
  const [imgs, setImgs] = useState({});

  useEffect(() => {
    if (suggestedSlice != null) setZ(suggestedSlice);
  }, [caseId, suggestedSlice]);

  useEffect(() => {
    if (!caseId) return;
    setBusy(true);
    computeLongitudinal(caseId, eff)
      .then((d) => setData(d))
      .finally(() => setBusy(false));
  }, [caseId, eff]);

  useEffect(() => {
    if (!caseId || !data) return;
    let cancelled = false;
    Promise.all(
      PANELS.map((p) =>
        fetchLongitudinalSlice(caseId, z, p.key).then((url) => [p.key, url])
      )
    ).then((entries) => {
      if (cancelled) return;
      setImgs(Object.fromEntries(entries));
    });
    return () => { cancelled = true; };
  }, [caseId, z, data]);

  const interpretationTone = useMemo(() => {
    if (!data) return "bg-slate-50 border-slate-200 text-slate-700";
    const pct = data.volume_change_pct;
    if (pct <= -50) return "bg-emerald-50 border-emerald-200 text-emerald-800";
    if (pct <= -20) return "bg-teal-50 border-teal-200 text-teal-800";
    if (pct <  20) return "bg-amber-50 border-amber-200 text-amber-800";
    return "bg-rose-50 border-rose-200 text-rose-700";
  }, [data]);

  return (
    <div className="card !p-6 lg:!p-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
        <div>
          <span className="section-eyebrow">Step 4</span>
          <h2 className="h3 mt-1">Longitudinal analysis (synthetic demo)</h2>
          <p className="text-sm text-clinical-muted mt-1 max-w-2xl">
            Drag the slider to simulate post-treatment recovery. The post-mask is
            synthesised by morphological erosion of the predicted lesion - all
            architecture for real follow-up scans is in place.
          </p>
        </div>
        <div className="pill pill-amber"><Heart className="w-3.5 h-3.5" />Synthetic demo</div>
      </div>

      <div className="rounded-2xl bg-clinical-bg border border-clinical-border p-4 lg:p-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-widest text-clinical-muted">
            Treatment effectiveness
          </span>
          <span className="font-mono text-sm font-bold text-clinical-ink">{(eff * 100).toFixed(0)}%</span>
        </div>
        <input
          type="range" min="0" max="0.9" step="0.05" value={eff}
          onChange={(e) => setEff(parseFloat(e.target.value))}
          className="w-full accent-brand-600"
          disabled={busy}
        />
        <div className="flex justify-between text-[11px] text-clinical-muted mt-1 font-medium">
          <span>None (0%)</span>
          <span>Partial</span>
          <span>Strong (90%)</span>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          icon={TrendingDown}
          label="Volume change"
          value={data ? data.volume_change_pct : "--"}
          suffix={data ? "%" : ""}
        />
        <MetricCard
          label="Pre / Post"
          value={data ? `${data.pre_volume_ml} -> ${data.post_volume_ml}` : "--"}
          suffix="mL"
        />
        <MetricCard label="Dice similarity" value={data ? data.dice_similarity : "--"} />
        <MetricCard label="COM displacement" value={data ? data.com_displacement_mm : "--"} suffix="mm" />
      </div>

      {data && (
        <div className={`mt-5 rounded-xl border px-4 py-3 text-sm leading-relaxed ${interpretationTone}`}>
          <span className="font-semibold">Interpretation: </span>
          {data.interpretation}
        </div>
      )}

      <div className="mt-6">
        <div className="flex items-center justify-between mb-3">
          <span className="section-eyebrow">Pre / Post / Recovered viewer</span>
          <div className="hidden sm:flex items-center gap-2">
            <button onClick={() => setZ((v) => Math.max(0, v - 1))} className="btn-ghost !p-2">
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="font-mono text-xs text-clinical-muted">slice {z + 1} / {nSlices}</span>
            <button onClick={() => setZ((v) => Math.min((nSlices ?? 1) - 1, v + 1))} className="btn-ghost !p-2">
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {PANELS.map((p) => (
            <div key={p.key} className="rounded-2xl bg-slate-900 overflow-hidden relative aspect-square">
              {imgs[p.key] ? (
                <img src={imgs[p.key]} alt={p.label} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-500 text-xs">
                  <Loader2 className="w-5 h-5 animate-spin" />
                </div>
              )}
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/70 to-transparent px-3 py-2">
                <span className="text-[11px] uppercase tracking-widest text-white/90 font-semibold">
                  {p.label}
                </span>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center gap-4">
          <span className="text-xs text-clinical-muted font-mono whitespace-nowrap">slice {z + 1}/{nSlices}</span>
          <input
            type="range" min={0} max={(nSlices ?? 1) - 1} step={1}
            value={z}
            onChange={(e) => setZ(parseInt(e.target.value, 10))}
            className="flex-1 accent-brand-600"
          />
        </div>
      </div>
    </div>
  );
}
