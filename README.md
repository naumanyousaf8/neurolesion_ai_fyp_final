# NeuroLesion AI &mdash; Stroke Lesion Analysis on DWI MRI

> **Final Year Project &middot; BS Computer Science &middot; GCU Lahore**
> AI-powered stroke lesion segmentation, longitudinal analysis, and structured radiology reporting on diffusion-weighted MRI.

NeuroLesion AI is an end-to-end stroke imaging prototype that runs **fully locally on a CPU**. It segments ischaemic lesions from 3D DWI MRI volumes using a 2D U-Net, computes per-lesion morphometrics, simulates pre/post-treatment longitudinal change, and produces clinical-style radiology reports (deterministic template, optional **Ollama** LLM sections, and downloadable PDFs) &mdash; all served behind a polished React + Tailwind front-end.

---

## Project layout

```text
project_main/
|
|-- analysis/                       Clinical post-processing layer (numpy/scipy only)
|   |-- __init__.py                 Public re-exports
|   |-- lesion.py                   Connected components, per-lesion morphometrics
|   |-- longitudinal.py             Pre vs. post comparison + synthetic post-mask
|   |-- report.py                   Template-based radiology-style narrative
|
|-- ml/                             Machine-learning pipeline (PyTorch)
|   |-- __init__.py
|   |-- model.py                    TinyUNet (compact 2D U-Net, ~250 K params)
|   |-- losses.py                   Dice loss, BCE+Dice combined loss, Dice metric
|   |-- metrics.py                  Pixel accuracy and IoU helpers
|   |-- dataset.py                  PyTorch Dataset + on-the-fly augmentation
|   |-- preprocess.py               Raw NIfTI -> 64x64 .npz slices + 80/10/10 split
|   |-- train.py                    Training loop (AdamW + Cosine LR + best-checkpoint)
|   |-- predict.py                  Inference: load checkpoint, run on a 3D volume
|   |-- evaluate.py                 Held-out test Dice / Precision / Recall
|   |-- plot_metrics.py             Training curves + test metric bar charts (PNG)
|
|-- backend/                        FastAPI inference server
|   |-- __init__.py
|   |-- main.py                     create_app() factory + uvicorn entry point
|   |-- config.py                   Paths and runtime constants
|   |-- schemas.py                  Pydantic request/response models
|   |-- dependencies.py             Model singleton + per-process prediction cache
|   |-- services/                   Pure-Python domain logic (no FastAPI imports)
|   |   |-- __init__.py
|   |   |-- nifti_io.py             Decode NIfTI bytes / paths -> numpy
|   |   |-- rendering.py            2D slice -> base64 PNG (4 panels)
|   |   |-- inference.py            run_inference_pipeline + serialise_findings
|   |   |-- llm_report_service.py   Ollama (gemma:2b) structured radiology sections
|   |   |-- pdf_report_service.py   Hospital-style PDF export (template or AI)
|   |-- routes/                     One APIRouter per resource
|       |-- __init__.py             Aggregates all routers under /api
|       |-- health.py               GET  /api/health
|       |-- samples.py              GET  /api/samples
|       |-- predict.py              POST /api/predict
|       |-- slice_views.py          GET  /api/slice
|       |-- longitudinal.py         POST /api/longitudinal + GET /api/longitudinal/slice
|       |-- llm_report.py           POST /api/generate-llm-report
|       |-- pdf_report.py           GET  /api/download-report-pdf
|
|-- frontend/                       React + Vite + Tailwind web app (the UI)
|   |-- index.html
|   |-- package.json
|   |-- vite.config.js              Dev proxy to FastAPI backend on :8000
|   |-- tailwind.config.js          Brand colour palette + design tokens
|   |-- postcss.config.js           Tailwind PostCSS pipeline
|   |-- eslint.config.js
|   |-- public/
|   |   |-- brain.svg, icons.svg    Static assets
|   |-- src/
|       |-- main.jsx, App.jsx       Routing + entry point
|       |-- index.css               Tailwind layers + custom CSS components
|       |-- pages/
|       |   |-- Home.jsx            Marketing landing page (hero, features, ...)
|       |   |-- Analyzer.jsx        Upload, results, reports, longitudinal view
|       |   |-- About.jsx           Project background + methodology + limitations
|       |-- components/
|       |   |-- Navbar.jsx, Footer.jsx
|       |   |-- UploadZone.jsx, SliceViewer.jsx, ResultsPanel.jsx
|       |   |-- ReportPanel.jsx, ReportGenerationPanel.jsx, LLMReportSections.jsx
|       |   |-- LongitudinalPanel.jsx, MetricCard.jsx, SeverityBadge.jsx
|       |-- lib/api.js              Axios client for the FastAPI backend
|
|-- scripts/                        Thin CLI wrappers around ml.* and utilities
|   |-- __init__.py
|   |-- run_preprocessing.py        -> ml.preprocess.main()
|   |-- run_training.py             -> ml.train.main()
|   |-- run_evaluation.py           -> ml.evaluate.main()
|   |-- run_plot_metrics.py         -> ml.plot_metrics.main()
|   |-- ollama_test.py              Quick Ollama connectivity smoke test
|
|-- docs/                           FYP documentation (optional; not tracked in git)
|
|-- my_dataset/                     Raw ISLES 2022 DWI volumes + binary masks (input)
|   |-- images/                     Per-case DWI NIfTI volumes
|   |-- masks/                      Matching lesion label maps
|
|-- data_processed/                 Preprocessed 64x64 .npz slices (generated)
|   |-- train/, val/, test/         Patient-disjoint 80 / 10 / 10 split
|
|-- checkpoints/                    Trained weights: best.pt, last.pt, history.json
|-- sample_outputs/                 Evaluation artefacts
|   |-- test_metrics.json           Held-out test scores
|   |-- plots/                      training_curves.png, test_metrics_bar.png, ...
|
|-- run.py                          One-shot launcher (boots backend + frontend)
|-- requirements.txt                Python dependencies
|-- README.md                       (you are here)
```

---

## Quick start (1 command)

```powershell
# Install Python deps once
pip install -r requirements.txt

# Boot the full stack (backend + frontend) and open the browser
python run.py
```

`run.py` will:
1. Install `frontend/node_modules` on first run.
2. Start the FastAPI backend on `http://localhost:8000`.
3. Start the Vite React dev server on `http://localhost:5173`.
4. Open the home page in your default browser.

> **Requires:** Python 3.10+, Node.js 18+, and a trained checkpoint at `checkpoints/best.pt`.
>
> **Optional (AI reports & PDF):** [Ollama](https://ollama.com) with `gemma:2b` pulled (`ollama pull gemma:2b`) for `/api/generate-llm-report` and AI PDF export.

---

## Manual run (two terminals)

### Terminal 1 &mdash; backend

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

### Terminal 2 &mdash; frontend

```powershell
cd frontend
npm install     # first time only
npm run dev
```

Open <http://localhost:5173>.

---

## ML pipeline (re-train / re-evaluate)

```powershell
python -m scripts.run_preprocessing     # NIfTI -> .npz slices, train/val/test split
python -m scripts.run_training          # Train TinyUNet on CPU
python -m scripts.run_evaluation        # Held-out test metrics -> sample_outputs/test_metrics.json
python -m scripts.run_plot_metrics      # PNG plots from history.json + test_metrics.json
```

Outputs land in `checkpoints/`, `sample_outputs/`, and `sample_outputs/plots/`.

---

## Backend API surface

| Method | Path                           | Purpose                                                    |
| ------ | ------------------------------ | ---------------------------------------------------------- |
| `GET`  | `/api/health`                  | Liveness + checkpoint presence                             |
| `GET`  | `/api/samples`                 | List built-in ISLES 2022 sample cases                      |
| `POST` | `/api/predict`                 | Run segmentation on uploaded `.nii` or sample              |
| `GET`  | `/api/slice`                   | Render a 2D slice (original / mask / overlay)              |
| `POST` | `/api/longitudinal`            | Compute synthetic pre/post longitudinal metrics            |
| `GET`  | `/api/longitudinal/slice`      | Render pre / post / recovered slice                        |
| `POST` | `/api/generate-llm-report`     | Ollama structured report (Findings / Impression / Recs)    |
| `GET`  | `/api/download-report-pdf`     | Download PDF (`report_type=template` or `ai`)              |

Interactive docs live at <http://localhost:8000/docs> when the backend is running.

---

## Performance snapshot

| Metric                              | Value     |
| ----------------------------------- | --------- |
| Best validation Dice                | **0.8184**|
| Held-out test slice-mean Dice       | 0.7668    |
| Held-out test voxel Dice            | 0.4684    |
| Held-out test voxel precision       | 0.8367    |
| Held-out test voxel recall          | 0.3252    |
| Trainable parameters                | ~250 K    |
| Training time (CPU, 6 epochs)       | 19.7 min  |
| Inference time per volume (CPU)     | ~0.30 s   |

All metrics are computed on a **patient-disjoint** 80 / 10 / 10 split.

---

## Limitations & honest scope

- Trained on CPU only &mdash; the architecture and 64x64 resolution were chosen for tractability, not for state-of-the-art accuracy.
- Single modality (DWI). Multi-modal fusion (DWI + ADC + FLAIR) is left as future work.
- Default report is a deterministic template; the optional AI path uses a small local model (`gemma:2b` via Ollama), not a fine-tuned clinical LLM.
- Longitudinal analysis is demonstrated using a **synthetic** post-treatment mask (morphological erosion). Real follow-up scans will replace it in production.
- **Academic prototype only &mdash; NOT a regulated medical device.**

---

## Troubleshooting

- **Files keep disappearing on Windows** &rarr; whitelist this folder in Windows Defender (`Settings -> Virus & threat protection -> Manage settings -> Add an exclusion`).
- **`Trained checkpoint not found`** &rarr; run `python -m scripts.run_training` first, or restore `checkpoints/best.pt` from your backup.
- **Port already in use** &rarr; another instance is running. Stop it, or change ports in `run.py` / `vite.config.js`.
- **AI report / PDF errors (503 / 504)** &rarr; start Ollama, run `ollama pull gemma:2b`, and verify with `python scripts/ollama_test.py`.

---

&copy; FYP prototype, 2026. Not for clinical use.
