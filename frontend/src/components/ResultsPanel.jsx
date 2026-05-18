import { Activity, AlertCircle, Box, Brain, Droplet, Layers, Microscope } from "lucide-react";
import MetricCard from "./MetricCard.jsx";
import SeverityBadge from "./SeverityBadge.jsx";

export default function ResultsPanel({ result }) {
  if (!result) return null;
  return (
    <div className="card !p-6 lg:!p-8">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-6">
        <div>
          <span className="section-eyebrow">Step 2</span>
          <h2 className="h3 mt-1">Quantitative findings</h2>
          <p className="text-sm text-clinical-muted mt-1">
            Per-volume statistics computed from the predicted 3D mask.
          </p>
        </div>
        <SeverityBadge volume_ml={result.total_volume_ml} />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={Droplet}   label="Total lesion volume"   value={result.total_volume_ml}   suffix="mL" />
        <MetricCard icon={Activity}  label="Lesions detected"      value={result.n_lesions} />
        <MetricCard icon={Microscope}label="Largest lesion volume" value={result.largest_volume_ml} suffix="mL" />
        <MetricCard icon={Layers}    label="Volume shape"          value={result.shape.join(" x ")}
                                     hint={`spacing ${result.spacing.join(" x ")} mm`} />
      </div>

      {result.findings && result.findings.length > 0 && (
        <div className="mt-7">
          <h3 className="text-sm font-bold uppercase tracking-widest text-clinical-muted mb-3 flex items-center gap-2">
            <Brain className="w-4 h-4 text-brand-600" />
            Per-lesion breakdown
          </h3>
          <div className="overflow-x-auto rounded-xl border border-clinical-border">
            <table className="min-w-full text-sm">
              <thead className="bg-clinical-bg text-clinical-muted text-[11px] uppercase tracking-widest">
                <tr>
                  <th className="text-left px-4 py-3 font-semibold">#</th>
                  <th className="text-left px-4 py-3 font-semibold">Volume</th>
                  <th className="text-left px-4 py-3 font-semibold">Side</th>
                  <th className="text-left px-4 py-3 font-semibold">Region (axial)</th>
                  <th className="text-left px-4 py-3 font-semibold">Voxels</th>
                  <th className="text-left px-4 py-3 font-semibold">Bounding box</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-clinical-border">
                {result.findings.map((f) => (
                  <tr key={f.index} className="hover:bg-brand-50/40 transition">
                    <td className="px-4 py-3 font-mono">{f.index}</td>
                    <td className="px-4 py-3 font-semibold text-clinical-ink">{f.volume_ml} mL</td>
                    <td className="px-4 py-3 capitalize">{f.side}</td>
                    <td className="px-4 py-3 capitalize">{f.region}</td>
                    <td className="px-4 py-3 font-mono">{f.voxel_count}</td>
                    <td className="px-4 py-3 font-mono">{f.bounding_box.join(" x ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {result.n_lesions === 0 && (
        <div className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          No discrete lesion foci detected at the current threshold.
        </div>
      )}
    </div>
  );
}
