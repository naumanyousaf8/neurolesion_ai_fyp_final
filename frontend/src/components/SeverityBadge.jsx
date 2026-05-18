import { AlertCircle, AlertTriangle, CheckCircle2, Activity } from "lucide-react";

export function severityFromVolume(vol_ml) {
  if (vol_ml <= 0)  return { key: "none",     label: "No lesion",   tone: "emerald" };
  if (vol_ml < 1)   return { key: "minor",    label: "Small / minor",     tone: "emerald" };
  if (vol_ml < 5)   return { key: "moderate", label: "Moderate",          tone: "amber" };
  if (vol_ml < 20)  return { key: "large",    label: "Large",             tone: "orange" };
  return                  { key: "extensive",label: "Extensive",         tone: "rose" };
}

const TONE = {
  emerald: "bg-emerald-50 text-emerald-700 border-emerald-200",
  amber:   "bg-amber-50 text-amber-800 border-amber-200",
  orange:  "bg-orange-50 text-orange-800 border-orange-200",
  rose:    "bg-rose-50 text-rose-700 border-rose-200",
};

export default function SeverityBadge({ volume_ml = 0 }) {
  const sev = severityFromVolume(volume_ml);
  const Icon = sev.key === "none" || sev.key === "minor" ? CheckCircle2
             : sev.key === "moderate" ? Activity
             : sev.key === "large"    ? AlertTriangle
             : AlertCircle;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold border ${TONE[sev.tone]}`}>
      <Icon className="w-3.5 h-3.5" />
      {sev.label} infarct
    </span>
  );
}
