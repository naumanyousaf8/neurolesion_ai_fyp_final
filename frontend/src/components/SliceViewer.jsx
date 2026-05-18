import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { fetchSlice } from "../lib/api.js";

const PANELS = [
  { key: "original", label: "Original DWI" },
  { key: "mask",     label: "Predicted mask" },
  { key: "overlay",  label: "Overlay" },
];

export default function SliceViewer({ caseId, nSlices, suggestedSlice }) {
  const [z, setZ] = useState(suggestedSlice ?? Math.floor((nSlices ?? 1) / 2));
  const [images, setImages] = useState({ original: null, mask: null, overlay: null });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (suggestedSlice != null) setZ(suggestedSlice);
  }, [caseId, suggestedSlice]);

  useEffect(() => {
    if (!caseId) return;
    let cancelled = false;
    setLoading(true);
    Promise.all(
      PANELS.map((p) =>
        fetchSlice(caseId, z, p.key).then((url) => [p.key, url])
      )
    ).then((entries) => {
      if (cancelled) return;
      const next = Object.fromEntries(entries);
      setImages(next);
      setLoading(false);
    }).catch(() => setLoading(false));
    return () => { cancelled = true; };
  }, [caseId, z]);

  const dec = () => setZ((v) => Math.max(0, v - 1));
  const inc = () => setZ((v) => Math.min((nSlices ?? 1) - 1, v + 1));

  return (
    <div className="card !p-6 lg:!p-7">
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="section-eyebrow">Image previewer</span>
          <h3 className="h3 mt-1">Slice-by-slice review</h3>
        </div>
        <div className="hidden sm:flex items-center gap-2">
          <button onClick={dec} disabled={loading || z <= 0} className="btn-ghost !p-2">
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="font-mono text-xs text-clinical-muted">
            slice {z + 1} / {nSlices}
          </span>
          <button onClick={inc} disabled={loading || z >= (nSlices ?? 1) - 1} className="btn-ghost !p-2">
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {PANELS.map((p) => (
          <div key={p.key} className="rounded-2xl bg-slate-900 overflow-hidden relative aspect-square shadow-card">
            {images[p.key] ? (
              <img src={images[p.key]} alt={p.label} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-500 text-xs">
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "..."}
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

      <div className="mt-5 flex items-center gap-4">
        <span className="text-xs text-clinical-muted font-mono whitespace-nowrap">slice {z + 1}/{nSlices}</span>
        <input
          type="range" min={0} max={(nSlices ?? 1) - 1} step={1}
          value={z}
          onChange={(e) => setZ(parseInt(e.target.value, 10))}
          className="flex-1 accent-brand-600"
        />
      </div>
    </div>
  );
}
