import { useCallback, useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { FileUp, FolderOpen, Sparkles, UploadCloud, X } from "lucide-react";
import { listSamples } from "../lib/api.js";

export default function UploadZone({ onSubmit, busy }) {
  const [file, setFile] = useState(null);
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState("");
  const [threshold, setThreshold] = useState(0.5);

  useEffect(() => {
    listSamples().then(setSamples).catch(() => setSamples([]));
  }, []);

  const onDrop = useCallback((accepted) => {
    if (accepted && accepted.length) {
      setFile(accepted[0]);
      setSelectedSample("");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/octet-stream": [".nii", ".nii.gz", ".gz"] },
    multiple: false,
    disabled: busy,
  });

  const submit = () => {
    if (file)        onSubmit({ kind: "upload", file, threshold });
    else if (selectedSample) onSubmit({ kind: "sample", sampleName: selectedSample, threshold });
  };

  const ready = !!(file || selectedSample);

  return (
    <div className="card !p-6 lg:!p-8">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <span className="section-eyebrow">Step 1</span>
          <h2 className="h3 mt-1">Choose an MRI volume</h2>
          <p className="text-sm text-clinical-muted mt-1">
            Drop a NIfTI file from your machine, or pick one of the built-in
            ISLES 2022 samples.
          </p>
        </div>
        <FolderOpen className="w-6 h-6 text-brand-600 hidden md:block" />
      </div>

      <div {...getRootProps()} className={`relative rounded-2xl border-2 border-dashed transition cursor-pointer p-8 lg:p-12 text-center
        ${isDragActive ? "border-brand-500 bg-brand-50" : "border-clinical-border hover:border-brand-400 hover:bg-brand-50/40"}
        ${busy ? "opacity-60 pointer-events-none" : ""}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-2">
          <div className="w-14 h-14 rounded-2xl bg-brand-50 text-brand-700 flex items-center justify-center mb-2">
            <UploadCloud className="w-6 h-6" />
          </div>
          {file ? (
            <>
              <div className="font-semibold text-clinical-ink flex items-center gap-2">
                <FileUp className="w-4 h-4 text-brand-600" />
                {file.name}
              </div>
              <div className="text-xs text-clinical-muted">
                {(file.size / (1024 * 1024)).toFixed(2)} MB &middot; ready to analyse
              </div>
              <button
                type="button"
                className="mt-2 text-xs text-rose-600 hover:underline inline-flex items-center gap-1"
                onClick={(e) => { e.stopPropagation(); setFile(null); }}
              >
                <X className="w-3 h-3" /> remove
              </button>
            </>
          ) : (
            <>
              <div className="font-semibold text-clinical-ink">
                {isDragActive ? "Drop the NIfTI file here..." : "Drag & drop a .nii / .nii.gz file"}
              </div>
              <div className="text-xs text-clinical-muted">
                or <span className="text-brand-700 font-semibold underline">click to browse</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="my-6 flex items-center gap-3 text-xs uppercase tracking-widest text-clinical-muted font-semibold">
        <div className="h-px bg-clinical-border flex-1" />
        OR pick a sample
        <div className="h-px bg-clinical-border flex-1" />
      </div>

      <div className="grid sm:grid-cols-[1fr_auto] gap-3">
        <select
          value={selectedSample}
          onChange={(e) => { setSelectedSample(e.target.value); setFile(null); }}
          disabled={busy}
          className="rounded-xl border border-clinical-border bg-white px-4 py-3 text-sm
            focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
        >
          <option value="">Select a built-in ISLES 2022 sample...</option>
          {samples.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <div className="text-[11px] text-clinical-muted self-center">
          {samples.length} samples available
        </div>
      </div>

      <div className="mt-6 grid sm:grid-cols-2 gap-4 items-center">
        <div>
          <div className="text-xs font-semibold uppercase tracking-widest text-clinical-muted">
            Decision threshold
          </div>
          <div className="flex items-center gap-3 mt-2">
            <input
              type="range" min="0.1" max="0.9" step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              disabled={busy}
              className="flex-1 accent-brand-600"
            />
            <span className="font-mono text-sm font-bold text-clinical-ink w-12 text-right">
              {threshold.toFixed(2)}
            </span>
          </div>
        </div>
        <button
          type="button"
          className="btn-primary justify-center !py-3.5 disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={submit}
          disabled={!ready || busy}
        >
          <Sparkles className="w-4 h-4" />
          {busy ? "Running model..." : "Run AI analysis"}
        </button>
      </div>
    </div>
  );
}
