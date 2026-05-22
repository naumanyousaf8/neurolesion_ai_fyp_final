import { useState } from "react";
import { AlertOctagon, ArrowDown, Loader2 } from "lucide-react";
import UploadZone from "../components/UploadZone.jsx";
import ResultsPanel from "../components/ResultsPanel.jsx";
import SliceViewer from "../components/SliceViewer.jsx";
import ReportGenerationPanel from "../components/ReportGenerationPanel.jsx";
import LongitudinalPanel from "../components/LongitudinalPanel.jsx";
import { predictByUpload, predictBySample } from "../lib/api.js";

export default function Analyzer() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleSubmit = async ({ kind, file, sampleName, threshold }) => {
    setBusy(true); setError(null); setResult(null);
    try {
      const data = kind === "upload"
        ? await predictByUpload(file, threshold)
        : await predictBySample(sampleName, threshold);
      setResult(data);
      setTimeout(() => {
        const el = document.getElementById("results");
        el?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 60);
    } catch (e) {
      console.error(e);
      const msg = e?.response?.data?.detail || e.message || "Inference failed.";
      setError(typeof msg === "string" ? msg : "Inference failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <section className="bg-hero-gradient">
        <div className="absolute inset-0 bg-grid-faint opacity-50 pointer-events-none" />
        <div className="container-wide relative pt-14 pb-10">
          <span className="pill pill-brand">Analyzer</span>
          <h1 className="h2 mt-3 max-w-3xl">
            <span className="gradient-text">Upload, segment, report</span> - all in one workflow.
          </h1>
          <p className="lead mt-3 max-w-2xl">
            Drop a DWI MRI volume or pick a built-in sample, then walk through
            the four-step pipeline below. Everything runs on your local CPU.
          </p>
        </div>
      </section>

      <section className="container-wide py-10">
        <UploadZone onSubmit={handleSubmit} busy={busy} />
        {busy && (
          <div className="mt-6 flex items-center gap-3 text-clinical-muted">
            <Loader2 className="w-5 h-5 animate-spin text-brand-600" />
            <span className="font-medium">Running U-Net inference and analysis...</span>
          </div>
        )}
        {error && (
          <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 flex items-center gap-2">
            <AlertOctagon className="w-4 h-4" /> {error}
          </div>
        )}
      </section>

      {result && (
        <section id="results" className="container-wide pb-20 space-y-6 animate-fade-up">
          <div className="flex items-center justify-between">
            <div>
              <span className="section-eyebrow">Case</span>
              <h2 className="h3 mt-1 font-mono">{result.case_label}</h2>
            </div>
            <a href="#results" className="text-xs text-clinical-muted inline-flex items-center gap-1.5">
              <ArrowDown className="w-3.5 h-3.5" />Scroll for full breakdown
            </a>
          </div>

          <ResultsPanel result={result} />

          <SliceViewer
            caseId={result.case_id}
            nSlices={result.n_slices}
            suggestedSlice={result.suggested_slice}
          />

          <ReportGenerationPanel
            caseId={result.case_id}
            caseLabel={result.case_label}
            templateSource={result.report}
          />

          <LongitudinalPanel
            caseId={result.case_id}
            nSlices={result.n_slices}
            suggestedSlice={result.suggested_slice}
          />
        </section>
      )}
    </>
  );
}
