import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
  timeout: 60000,
});

export async function listSamples() {
  const { data } = await api.get("/samples");
  return data.samples ?? [];
}

export async function predictBySample(sampleName, threshold = 0.5) {
  const form = new FormData();
  form.append("sample_name", sampleName);
  form.append("threshold", String(threshold));
  const { data } = await api.post("/predict", form);
  return data;
}

export async function predictByUpload(file, threshold = 0.5) {
  const form = new FormData();
  form.append("file", file);
  form.append("threshold", String(threshold));
  const { data } = await api.post("/predict", form);
  return data;
}

export function getSliceUrl(caseId, z, panel = "overlay") {
  const params = new URLSearchParams({ case_id: caseId, z: String(z), panel });
  return `/api/slice?${params.toString()}`;
}

export async function fetchSlice(caseId, z, panel = "overlay") {
  const { data } = await api.get("/slice", { params: { case_id: caseId, z, panel } });
  return data.data_url;
}

export async function computeLongitudinal(caseId, effectiveness) {
  const { data } = await api.post("/longitudinal", {
    case_id: caseId,
    effectiveness,
  });
  return data;
}

export async function fetchLongitudinalSlice(caseId, z, panel = "recovered") {
  const { data } = await api.get("/longitudinal/slice", {
    params: { case_id: caseId, z, panel },
  });
  return data.data_url;
}

/** Human-readable message from FastAPI / axios errors. */
export function formatApiError(error, fallback = "Request failed.") {
  if (!error?.response) {
    if (error?.code === "ECONNABORTED") {
      return "Request timed out. For AI reports, ensure Ollama is running locally.";
    }
    return error?.message || fallback;
  }

  const { status, data } = error.response;
  const detail = data?.detail;

  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d?.msg ?? JSON.stringify(d)).join("; ");
  }

  if (status === 504) {
    return "AI report generation timed out. Retry or check Ollama performance.";
  }
  if (status === 503) {
    return "Cannot reach Ollama. Start the local server and ensure gemma:2b is available.";
  }
  if (status === 404) {
    return "Case not found. Run segmentation on this volume first.";
  }
  if (status === 502) {
    return "AI report could not be structured. Please retry generation.";
  }
  if (status === 400) {
    return "Missing metadata for report generation. Re-run analysis first.";
  }

  return fallback;
}

/** Generate structured LLM radiology report (Findings / Impression / Recommendations). */
export async function generateLLMReport(caseId) {
  const { data } = await api.post(
    "/generate-llm-report",
    { case_id: caseId },
    { timeout: 130000 },
  );
  return data;
}

/** Download hospital-style PDF (template or ai). Returns a Blob. */
export async function downloadReportPdf(caseId, reportType) {
  const timeout = reportType === "ai" ? 150000 : 90000;
  const { data } = await api.get("/download-report-pdf", {
    params: { case_id: caseId, report_type: reportType },
    responseType: "blob",
    timeout,
  });
  return data;
}
