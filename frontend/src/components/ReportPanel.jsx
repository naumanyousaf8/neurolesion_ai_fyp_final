import { Download, FileText } from "lucide-react";

export default function ReportPanel({ report, caseLabel }) {
  const downloadReport = () => {
    const blob = new Blob([report ?? ""], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(caseLabel || "case").replace(/[^a-zA-Z0-9_.-]/g, "_")}_neurolesion_report.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card !p-6 lg:!p-8">
      <div className="flex items-center justify-between mb-5">
        <div>
          <span className="section-eyebrow">Step 3</span>
          <h2 className="h3 mt-1">AI-generated radiology report</h2>
          <p className="text-sm text-clinical-muted mt-1">
            Structured, deterministic narrative produced from the
            quantitative segmentation metrics above.
          </p>
        </div>
        <button className="btn-secondary" onClick={downloadReport}>
          <Download className="w-4 h-4" /> Download .txt
        </button>
      </div>
      <div className="report-panel">{report || "Report will appear here once analysis completes."}</div>
      <div className="mt-3 text-xs text-clinical-muted flex items-center gap-2">
        <FileText className="w-3.5 h-3.5" />
        Template-based natural language generation. AI findings must be confirmed by a radiologist.
      </div>
    </div>
  );
}
