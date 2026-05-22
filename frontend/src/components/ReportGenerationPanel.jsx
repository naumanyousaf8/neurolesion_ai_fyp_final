import { useCallback, useEffect, useState } from "react";
import {
  AlertOctagon,
  Bot,
  CheckCircle2,
  Download,
  FileText,
  Loader2,
  Sparkles,
} from "lucide-react";
import { downloadReportPdf, formatApiError, generateLLMReport } from "../lib/api.js";
import LLMReportSections, { llmReportToPlainText } from "./LLMReportSections.jsx";

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function downloadText(filename, text) {
  downloadBlob(
    new Blob([text ?? ""], { type: "text/plain;charset=utf-8" }),
    filename,
  );
}

function safeFilename(caseLabel, suffix, ext = "txt") {
  const base = (caseLabel || "case").replace(/[^a-zA-Z0-9_.-]/g, "_");
  return `${base}_${suffix}.${ext}`;
}

export default function ReportGenerationPanel({
  caseId,
  caseLabel,
  templateSource,
}) {
  const [templateReport, setTemplateReport] = useState(null);
  const [llmReport, setLlmReport] = useState(null);

  const [loadingTemplate, setLoadingTemplate] = useState(false);
  const [loadingLlm, setLoadingLlm] = useState(false);
  const [loadingPdfTemplate, setLoadingPdfTemplate] = useState(false);
  const [loadingPdfAi, setLoadingPdfAi] = useState(false);

  const [errorTemplate, setErrorTemplate] = useState(null);
  const [errorLlm, setErrorLlm] = useState(null);
  const [errorPdfTemplate, setErrorPdfTemplate] = useState(null);
  const [errorPdfAi, setErrorPdfAi] = useState(null);

  const [successTemplate, setSuccessTemplate] = useState(false);
  const [successLlm, setSuccessLlm] = useState(false);

  const busy =
    loadingTemplate || loadingLlm || loadingPdfTemplate || loadingPdfAi;
  const canGenerate = Boolean(caseId) && Boolean(templateSource);

  useEffect(() => {
    setTemplateReport(null);
    setLlmReport(null);
    setErrorTemplate(null);
    setErrorLlm(null);
    setErrorPdfTemplate(null);
    setErrorPdfAi(null);
    setSuccessTemplate(false);
    setSuccessLlm(false);
  }, [caseId]);

  const handlePdfDownload = useCallback(async (reportType) => {
    if (!caseId) return;
    const setLoading =
      reportType === "template" ? setLoadingPdfTemplate : setLoadingPdfAi;
    const setError =
      reportType === "template" ? setErrorPdfTemplate : setErrorPdfAi;
    setLoading(true);
    setError(null);
    try {
      const blob = await downloadReportPdf(caseId, reportType);
      downloadBlob(blob, safeFilename(caseLabel, `${reportType}_report`, "pdf"));
    } catch (e) {
      console.error(e);
      setError(formatApiError(e, "PDF download failed."));
    } finally {
      setLoading(false);
    }
  }, [caseId, caseLabel]);

  const handleTemplate = useCallback(async () => {
    if (!templateSource) {
      setErrorTemplate("No segmentation metadata available. Run analysis first.");
      return;
    }
    setLoadingTemplate(true);
    setErrorTemplate(null);
    setSuccessTemplate(false);
    try {
      await new Promise((r) => setTimeout(r, 120));
      setTemplateReport(templateSource);
      setSuccessTemplate(true);
    } catch (e) {
      setErrorTemplate(formatApiError(e, "Template report could not be prepared."));
    } finally {
      setLoadingTemplate(false);
    }
  }, [templateSource]);

  const handleLlm = useCallback(async () => {
    if (!caseId) {
      setErrorLlm("Missing case identifier. Run segmentation before generating an AI report.");
      return;
    }
    setLoadingLlm(true);
    setErrorLlm(null);
    setSuccessLlm(false);
    setLlmReport(null);
    try {
      const data = await generateLLMReport(caseId);
      setLlmReport(data);
      setSuccessLlm(true);
    } catch (e) {
      console.error(e);
      setErrorLlm(formatApiError(e, "AI report generation failed."));
    } finally {
      setLoadingLlm(false);
    }
  }, [caseId]);

  return (
    <div className="card !p-6 lg:!p-8 print:shadow-none" id="report-generation">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between mb-6">
        <div>
          <span className="section-eyebrow">Step 3</span>
          <h2 className="h3 mt-1">Report generation</h2>
          <p className="text-sm text-clinical-muted mt-1 max-w-xl">
            Generate deterministic template and local AI (Ollama) radiology reports
            separately from the segmentation metrics above.
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-clinical-border bg-clinical-bg p-4 sm:p-5 mb-6 transition-colors">
        <p className="text-xs font-semibold uppercase tracking-widest text-clinical-muted mb-3">
          Actions
        </p>
        <div className="flex flex-col sm:flex-row flex-wrap gap-3">
          <button
            type="button"
            className="btn-secondary disabled:opacity-50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:hover:translate-y-0"
            onClick={handleTemplate}
            disabled={busy || !canGenerate}
            aria-busy={loadingTemplate}
          >
            {loadingTemplate ? (
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
            ) : (
              <FileText className="w-4 h-4" aria-hidden />
            )}
            Generate Template Report
          </button>

          <button
            type="button"
            className="btn-primary disabled:opacity-50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:hover:translate-y-0"
            onClick={handleLlm}
            disabled={busy || !caseId}
            aria-busy={loadingLlm}
          >
            {loadingLlm ? (
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
            ) : (
              <Sparkles className="w-4 h-4" aria-hidden />
            )}
            Generate AI Report
          </button>

          <button
            type="button"
            className="btn-secondary disabled:opacity-50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:hover:translate-y-0"
            onClick={() => handlePdfDownload("template")}
            disabled={busy || !caseId}
            aria-busy={loadingPdfTemplate}
          >
            {loadingPdfTemplate ? (
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
            ) : (
              <Download className="w-4 h-4" aria-hidden />
            )}
            Download Template PDF
          </button>

          <button
            type="button"
            className="btn-secondary disabled:opacity-50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:hover:translate-y-0"
            onClick={() => handlePdfDownload("ai")}
            disabled={busy || !caseId}
            aria-busy={loadingPdfAi}
          >
            {loadingPdfAi ? (
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden />
            ) : (
              <Download className="w-4 h-4" aria-hidden />
            )}
            Download AI Report PDF
          </button>
        </div>

        {!canGenerate && caseId && (
          <p className="mt-3 text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2">
            Template metrics are not available for this case. Re-run segmentation.
          </p>
        )}

        {loadingLlm && (
          <p className="mt-3 text-sm text-clinical-muted flex items-center gap-2 animate-fade-in">
            <Loader2 className="w-4 h-4 animate-spin text-brand-600" />
            Generating AI radiology report via local Ollama (gemma:2b)…
          </p>
        )}
        {(loadingPdfTemplate || loadingPdfAi) && (
          <p className="mt-3 text-sm text-clinical-muted flex items-center gap-2 animate-fade-in">
            <Loader2 className="w-4 h-4 animate-spin text-brand-600" />
            {loadingPdfAi
              ? "Building AI report PDF (includes Ollama generation)…"
              : "Building template report PDF…"}
          </p>
        )}

        {successTemplate && !loadingTemplate && (
          <p className="mt-3 text-sm text-brand-700 flex items-center gap-2 animate-fade-in">
            <CheckCircle2 className="w-4 h-4" /> Template report ready.
          </p>
        )}
        {successLlm && !loadingLlm && (
          <p className="mt-3 text-sm text-brand-700 flex items-center gap-2 animate-fade-in">
            <CheckCircle2 className="w-4 h-4" /> AI radiology report ready.
          </p>
        )}
      </div>

      {errorTemplate && (
        <div
          className="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 flex items-start gap-2 animate-fade-in"
          role="alert"
        >
          <AlertOctagon className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{errorTemplate}</span>
        </div>
      )}
      {errorLlm && (
        <div
          className="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 flex items-start gap-2 animate-fade-in"
          role="alert"
        >
          <AlertOctagon className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{errorLlm}</span>
        </div>
      )}
      {errorPdfTemplate && (
        <div
          className="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 flex items-start gap-2 animate-fade-in"
          role="alert"
        >
          <AlertOctagon className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{errorPdfTemplate}</span>
        </div>
      )}
      {errorPdfAi && (
        <div
          className="mb-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 flex items-start gap-2 animate-fade-in"
          role="alert"
        >
          <AlertOctagon className="w-4 h-4 shrink-0 mt-0.5" />
          <span>{errorPdfAi}</span>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-2 lg:items-start">
        <section
          className="report-display-card"
          aria-labelledby="template-report-heading"
        >
          <div className="flex items-center justify-between gap-3 mb-4">
            <div>
              <h3 id="template-report-heading" className="text-base font-bold text-clinical-ink">
                Template report
              </h3>
              <p className="text-xs text-clinical-muted mt-0.5">
                Deterministic narrative from segmentation metrics
              </p>
            </div>
            {templateReport && (
              <button
                type="button"
                className="btn-ghost shrink-0 print:hidden"
                onClick={() =>
                  downloadText(safeFilename(caseLabel, "template_report"), templateReport)
                }
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">Download .txt</span>
              </button>
            )}
          </div>

          <div className="report-scroll printable-report">
            {templateReport ? (
              <pre className="report-panel m-0">{templateReport}</pre>
            ) : (
              <p className="report-placeholder">
                Click &quot;Generate Template Report&quot; to view the structured template output.
              </p>
            )}
          </div>
        </section>

        <section
          className="report-display-card"
          aria-labelledby="llm-report-heading"
        >
          <div className="flex items-center justify-between gap-3 mb-4">
            <div className="flex items-start gap-2">
              <Bot className="w-5 h-5 text-brand-600 shrink-0 mt-0.5" aria-hidden />
              <div>
                <h3 id="llm-report-heading" className="text-base font-bold text-clinical-ink">
                  AI radiology report
                </h3>
                <p className="text-xs text-clinical-muted mt-0.5">
                  Local Ollama · Findings, Impression, Recommendations
                </p>
              </div>
            </div>
            {llmReport && (
              <button
                type="button"
                className="btn-ghost shrink-0 print:hidden"
                onClick={() =>
                  downloadText(
                    safeFilename(caseLabel, "ai_report"),
                    llmReportToPlainText(llmReport, llmReport.disclaimer),
                  )
                }
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">Download .txt</span>
              </button>
            )}
          </div>

          <div className="report-scroll printable-report">
            {llmReport ? (
              <LLMReportSections
                report={llmReport}
                disclaimer={llmReport.disclaimer}
              />
            ) : (
              <p className="report-placeholder">
                Click &quot;Generate AI Report&quot; after segmentation completes.
                Requires Ollama running with gemma:2b.
              </p>
            )}
          </div>
        </section>
      </div>

      <div className="mt-4 text-xs text-clinical-muted flex items-center gap-2">
        <FileText className="w-3.5 h-3.5 shrink-0" />
        Both reports are for research demonstration only. AI and template outputs require
        radiologist confirmation before any clinical use.
      </div>
    </div>
  );
}
