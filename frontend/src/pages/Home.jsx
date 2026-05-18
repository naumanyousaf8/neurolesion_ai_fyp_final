import { Link } from "react-router-dom";
import {
  ActivitySquare, ArrowRight, Brain, CheckCircle2, ClipboardList,
  Cpu, FileText, Gauge, ImageIcon, LineChart, Microscope,
  ShieldCheck, Sparkles, Stethoscope, Target, Timer, Workflow,
  Zap,
} from "lucide-react";

const FEATURES = [
  {
    icon: Brain,
    title: "U-Net stroke segmentation",
    desc: "Trained 2D U-Net (TinyUNet) extracts ischaemic lesions from DWI MRI volumes with patient-disjoint validation.",
  },
  {
    icon: ImageIcon,
    title: "Interactive slice viewer",
    desc: "Scroll through every axial slice and instantly see the predicted lesion overlay against the original scan.",
  },
  {
    icon: LineChart,
    title: "Longitudinal analysis",
    desc: "Compare pre-treatment and post-treatment lesion masks: volume change, Dice, and centre-of-mass displacement.",
  },
  {
    icon: ClipboardList,
    title: "Structured AI report",
    desc: "Auto-generated radiology-style narrative with FINDINGS, IMPRESSION, longitudinal section, and disclaimer.",
  },
  {
    icon: Gauge,
    title: "Real-time on CPU",
    desc: "Full-volume inference in 0.3 s on a regular laptop. No GPU required, no cloud upload, no setup pain.",
  },
  {
    icon: ShieldCheck,
    title: "Honest, auditable",
    desc: "Patient-disjoint train / val / test split. Held-out metrics published. Template NLG explicitly labelled.",
  },
];

const HOW = [
  {
    n: "01",
    icon: Workflow,
    title: "Upload",
    desc: "Drop a DWI MRI volume in NIfTI (.nii / .nii.gz) format - or pick one of the 25 built-in sample cases.",
  },
  {
    n: "02",
    icon: Cpu,
    title: "Segment",
    desc: "The pretrained 2D U-Net runs slice-by-slice on CPU and reconstructs a 3D binary lesion mask in under a second.",
  },
  {
    n: "03",
    icon: Microscope,
    title: "Analyse",
    desc: "Connected-component analysis computes per-lesion volume, hemisphere, anatomical region, and bounding box.",
  },
  {
    n: "04",
    icon: FileText,
    title: "Report",
    desc: "A clinical-style narrative is generated and downloadable. Findings, impression, longitudinal trend, disclaimer.",
  },
];

const STATS = [
  { label: "Training cases", value: "250" },
  { label: "Best validation Dice", value: "0.818" },
  { label: "Test slice-mean Dice", value: "0.767" },
  { label: "Inference time", value: "0.3s" },
];

export default function Home() {
  return (
    <>
      <Hero />
      <TrustStrip />
      <Features />
      <ShowcaseStrip />
      <HowItWorks />
      <Stats />
      <CTA />
    </>
  );
}

function Hero() {
  return (
    <section className="relative bg-hero-gradient overflow-hidden">
      <div className="absolute inset-0 bg-grid-faint opacity-50 pointer-events-none" />
      <div className="container-wide relative pt-20 lg:pt-28 pb-20 lg:pb-32 grid lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-6 animate-fade-up">
          <span className="pill pill-brand">
            <Sparkles className="w-3.5 h-3.5" />
            FYP prototype &middot; ISLES 2022 trained
          </span>
          <h1 className="h1 mt-5">
            AI-assisted{" "}
            <span className="gradient-text">stroke lesion analysis</span>{" "}
            for diffusion-weighted MRI.
          </h1>
          <p className="lead mt-6 max-w-xl">
            NeuroLesion AI segments ischaemic stroke lesions, tracks
            pre vs. post-treatment change, and writes a structured radiology
            report - in seconds, on a laptop, with full reproducibility.
          </p>
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Link to="/analyze" className="btn-primary text-base !py-3.5 !px-6">
              <Stethoscope className="w-4 h-4" />
              Launch Analyzer
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a href="#how" className="btn-secondary text-base !py-3.5 !px-6">
              See how it works
            </a>
          </div>
          <div className="mt-8 flex flex-wrap gap-x-8 gap-y-3 text-sm">
            <span className="flex items-center gap-2 text-clinical-muted">
              <CheckCircle2 className="w-4 h-4 text-brand-600" />
              No cloud upload
            </span>
            <span className="flex items-center gap-2 text-clinical-muted">
              <CheckCircle2 className="w-4 h-4 text-brand-600" />
              No GPU required
            </span>
            <span className="flex items-center gap-2 text-clinical-muted">
              <CheckCircle2 className="w-4 h-4 text-brand-600" />
              Patient-disjoint validation
            </span>
          </div>
        </div>

        <div className="lg:col-span-6 animate-fade-up [animation-delay:120ms]">
          <HeroVisual />
        </div>
      </div>
    </section>
  );
}

function HeroVisual() {
  return (
    <div className="relative">
      <div className="absolute -inset-6 bg-gradient-to-tr from-brand-200/40 to-brand-500/20 blur-3xl rounded-[40px]" />
      <div className="relative bg-white rounded-3xl border border-clinical-border shadow-cardLg p-5 lg:p-6">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-400/70"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400/70"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400/70"></span>
          </div>
          <span className="font-mono text-clinical-muted">case_010.nii &middot; DWI &middot; 112x112x72</span>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-3">
          {[0, 1, 2].map((i) => (
            <BrainSlicePreview key={i} variant={i} />
          ))}
        </div>

        <div className="mt-4 grid grid-cols-3 gap-3">
          <MiniMetric icon={ActivitySquare} label="Lesion volume" value="2.98 mL" />
          <MiniMetric icon={Target} label="Foci" value="4" />
          <MiniMetric icon={Timer} label="Inference" value="0.32 s" />
        </div>

        <div className="mt-4 px-3 py-2 rounded-xl bg-brand-50 border border-brand-100 text-[12px] text-brand-800 font-medium">
          <span className="inline-flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" />
            Findings consistent with small/minor acute infarct, left hemisphere.
          </span>
        </div>
      </div>
    </div>
  );
}

function MiniMetric({ icon: Icon, label, value }) {
  return (
    <div className="rounded-xl bg-clinical-bg border border-clinical-border p-3">
      <div className="flex items-center gap-1.5 text-clinical-muted text-[11px] uppercase tracking-wider font-semibold">
        <Icon className="w-3.5 h-3.5" />
        {label}
      </div>
      <div className="mt-1 text-base font-bold text-clinical-ink leading-tight">{value}</div>
    </div>
  );
}

function BrainSlicePreview({ variant = 0 }) {
  const titles = ["Original", "Mask", "Overlay"];
  return (
    <div className="rounded-xl bg-slate-900 aspect-square overflow-hidden relative">
      <svg viewBox="0 0 100 100" className="w-full h-full">
        <defs>
          <radialGradient id={`brain-${variant}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#cbd5e1" />
            <stop offset="60%" stopColor="#475569" />
            <stop offset="100%" stopColor="#0f172a" />
          </radialGradient>
        </defs>
        <rect width="100" height="100" fill="#0f172a" />
        <ellipse cx="50" cy="52" rx="34" ry="28" fill={`url(#brain-${variant})`} />
        <path d="M 50 30 Q 32 35, 32 55 Q 35 72, 50 74 Q 65 72, 68 55 Q 68 35, 50 30 Z" fill="none" stroke="#1e293b" strokeWidth="1" opacity="0.6" />
        <path d="M 50 32 L 50 72" stroke="#1e293b" strokeWidth="0.8" opacity="0.7" />

        {variant === 1 && (
          <g>
            <circle cx="38" cy="50" r="4.2" fill="#ef4444" opacity="0.95" />
            <circle cx="42" cy="56" r="2.8" fill="#ef4444" opacity="0.9" />
            <circle cx="36" cy="58" r="2.2" fill="#ef4444" opacity="0.85" />
          </g>
        )}
        {variant === 2 && (
          <g>
            <circle cx="38" cy="50" r="4.2" fill="#ef4444" opacity="0.55" />
            <circle cx="42" cy="56" r="2.8" fill="#ef4444" opacity="0.55" />
            <circle cx="36" cy="58" r="2.2" fill="#ef4444" opacity="0.55" />
          </g>
        )}
      </svg>
      <div className="absolute bottom-1.5 left-2 text-[10px] text-white/80 font-mono">
        {titles[variant]}
      </div>
    </div>
  );
}

function TrustStrip() {
  return (
    <section className="border-y border-clinical-border bg-white">
      <div className="container-wide py-6 grid grid-cols-2 sm:grid-cols-4 gap-6 text-center">
        <TrustItem label="Dataset" value="ISLES 2022" />
        <TrustItem label="Modality" value="DWI MRI" />
        <TrustItem label="Architecture" value="2D U-Net" />
        <TrustItem label="Runtime" value="CPU only" />
      </div>
    </section>
  );
}
function TrustItem({ label, value }) {
  return (
    <div>
      <div className="text-xs font-semibold uppercase tracking-widest text-clinical-muted">{label}</div>
      <div className="mt-1 text-base font-bold text-clinical-ink">{value}</div>
    </div>
  );
}

function Features() {
  return (
    <section id="features" className="py-20 lg:py-28">
      <div className="container-wide">
        <div className="max-w-2xl">
          <span className="section-eyebrow">Features</span>
          <h2 className="h2 mt-3">
            Everything a clinician needs <br className="hidden md:block" />
            for AI-assisted stroke screening.
          </h2>
          <p className="lead mt-4">
            From the raw MRI volume to a downloadable diagnostic report,
            every step is exposed, measurable, and reproducible.
          </p>
        </div>

        <div className="mt-12 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map((f, i) => (
            <div
              key={f.title}
              className="card card-hover"
              style={{ animationDelay: `${i * 60}ms` }}
            >
              <div className="w-11 h-11 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center mb-4">
                <f.icon className="w-5 h-5" strokeWidth={2.2} />
              </div>
              <div className="h3 text-lg">{f.title}</div>
              <p className="mt-2 text-sm text-clinical-muted leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ShowcaseStrip() {
  return (
    <section className="py-16 bg-white border-y border-clinical-border">
      <div className="container-wide grid lg:grid-cols-2 gap-12 items-center">
        <div className="animate-fade-up">
          <span className="section-eyebrow">Visualisation</span>
          <h2 className="h2 mt-3">
            Side-by-side image previewer for every axial slice.
          </h2>
          <p className="lead mt-4">
            Scroll through the brain volume slice by slice. The original DWI,
            the predicted mask, and an overlaid view sit side-by-side so you
            can verify model behaviour at a glance.
          </p>
          <ul className="mt-6 space-y-3 text-sm text-clinical-ink">
            {[
              "Crisp 2D slice rendering with red lesion overlay",
              "Auto-jumps to the slice with the largest lesion area",
              "Manual slider for full control over slice navigation",
              "Pre vs. post longitudinal viewer with green recovery overlay",
            ].map((s) => (
              <li key={s} className="flex items-start gap-2.5">
                <CheckCircle2 className="w-4 h-4 text-brand-600 mt-0.5 shrink-0" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="animate-fade-up [animation-delay:80ms]">
          <div className="relative">
            <div className="absolute -inset-6 bg-gradient-to-tr from-brand-200/40 to-brand-500/10 blur-3xl rounded-[40px]" />
            <div className="relative grid grid-cols-3 gap-3 bg-white rounded-2xl border border-clinical-border shadow-cardLg p-4">
              <BrainSlicePreview variant={0} />
              <BrainSlicePreview variant={1} />
              <BrainSlicePreview variant={2} />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function HowItWorks() {
  return (
    <section id="how" className="py-20 lg:py-28">
      <div className="container-wide">
        <div className="max-w-2xl">
          <span className="section-eyebrow">Pipeline</span>
          <h2 className="h2 mt-3">From DWI volume to diagnostic report in four steps.</h2>
          <p className="lead mt-4">
            Every step is exposed in the UI, every metric is computed
            transparently, and every output is downloadable.
          </p>
        </div>

        <div className="mt-12 grid md:grid-cols-2 lg:grid-cols-4 gap-5">
          {HOW.map((s, i) => (
            <div
              key={s.n}
              className="card card-hover"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className="flex items-center justify-between">
                <div className="w-11 h-11 rounded-xl bg-brand-600 text-white flex items-center justify-center">
                  <s.icon className="w-5 h-5" strokeWidth={2.2} />
                </div>
                <span className="text-xs font-mono text-clinical-muted">{s.n}</span>
              </div>
              <div className="h3 text-lg mt-4">{s.title}</div>
              <p className="mt-2 text-sm text-clinical-muted leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Stats() {
  return (
    <section className="py-16 bg-clinical-ink text-white relative overflow-hidden">
      <div className="absolute inset-0 bg-grid-faint opacity-15" />
      <div className="container-wide relative">
        <div className="max-w-2xl">
          <span className="text-xs font-semibold uppercase tracking-widest text-brand-300">Validated</span>
          <h2 className="text-3xl md:text-4xl font-bold mt-3">
            Performance figures, transparent and reproducible.
          </h2>
          <p className="text-slate-300 mt-3 leading-relaxed">
            All numbers below come from the public ISLES 2022 dataset under a
            patient-disjoint 80 / 10 / 10 split. No tricks, no leakage.
          </p>
        </div>
        <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-5">
          {STATS.map((s) => (
            <div key={s.label} className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur">
              <div className="text-3xl md:text-4xl font-extrabold tracking-tight gradient-text">
                {s.value}
              </div>
              <div className="mt-1 text-xs font-medium uppercase tracking-widest text-slate-400">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CTA() {
  return (
    <section className="py-24">
      <div className="container-narrow text-center">
        <h2 className="h2">Ready to see it on your own MRI?</h2>
        <p className="lead mt-4 max-w-xl mx-auto">
          Upload a DWI volume or pick a built-in sample - the analyser runs
          locally on your laptop and never sends data to the cloud.
        </p>
        <div className="mt-8 flex justify-center gap-3 flex-wrap">
          <Link to="/analyze" className="btn-primary text-base !py-3.5 !px-6">
            Open the Analyzer
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link to="/about" className="btn-secondary text-base !py-3.5 !px-6">
            About this project
          </Link>
        </div>
      </div>
    </section>
  );
}
