import { AlertCircle } from "lucide-react";

const SECTIONS = [
  { key: "findings", label: "Findings" },
  { key: "impression", label: "Impression" },
  { key: "recommendations", label: "Recommendations" },
];

export default function LLMReportSections({ report, disclaimer }) {
  if (!report) return null;

  return (
    <div className="space-y-4 animate-fade-in">
      {SECTIONS.map(({ key, label }) => (
        <article
          key={key}
          className="report-section-block"
          aria-labelledby={`llm-${key}-heading`}
        >
          <h3 id={`llm-${key}-heading`} className="report-section-title">
            {label}
          </h3>
          <p className="report-section-body">
            {report[key]?.trim() || "Not provided."}
          </p>
        </article>
      ))}

      {disclaimer && (
        <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-900">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" aria-hidden />
          <p>{disclaimer}</p>
        </div>
      )}
    </div>
  );
}

export function llmReportToPlainText(report, disclaimer) {
  if (!report) return "";
  const blocks = SECTIONS.map(
    ({ key, label }) => `${label.toUpperCase()}:\n${report[key] ?? ""}`,
  );
  const body = blocks.join("\n\n");
  return disclaimer ? `${body}\n\n---\n${disclaimer}` : body;
}
