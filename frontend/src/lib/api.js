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
