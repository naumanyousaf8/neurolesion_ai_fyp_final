import { Link } from "react-router-dom";
import {
  ArrowRight, Brain, Database, FileCog, FlaskConical, GitBranch,
  GraduationCap, Layers, ShieldAlert,
} from "lucide-react";

const TECH = [
  { icon: Brain,       title: "Architecture",     desc: "TinyUNet (2D U-Net, ~250k parameters), trained from scratch." },
  { icon: Database,    title: "Dataset",          desc: "ISLES 2022 - 250 DWI MRI volumes with binary stroke masks." },
  { icon: Layers,      title: "Preprocessing",    desc: "Z-score normalisation, axial slicing, bilinear resize to 64x64." },
  { icon: FlaskConical,title: "Augmentation",     desc: "On-the-fly: flips, rotations, intensity scaling, additive noise." },
  { icon: FileCog,     title: "Reporting",        desc: "Template-based NLG driven by quantitative segmentation metrics." },
  { icon: GitBranch,   title: "Validation",       desc: "Patient-disjoint train / val / test split (80 / 10 / 10)." },
];

const RESULTS = [
  ["Best validation Dice",         "0.8184"],
  ["Held-out test slice-mean Dice","0.7668"],
  ["Held-out test voxel Dice",     "0.4684"],
  ["Held-out test voxel precision","0.8367"],
  ["Held-out test voxel recall",   "0.3252"],
  ["Training time (CPU)",          "19.7 min"],
  ["Inference time per volume",    "~0.30 s"],
  ["Trainable parameters",         "~250 K"],
];

export default function About() {
  return (
    <>
      <section className="bg-hero-gradient">
        <div className="absolute inset-0 bg-grid-faint opacity-50 pointer-events-none" />
        <div className="container-wide relative pt-20 pb-16">
          <span className="pill pill-brand"><GraduationCap className="w-3.5 h-3.5" />Final Year Project</span>
          <h1 className="h1 mt-4 max-w-3xl">
            Building <span className="gradient-text">explainable</span> stroke-imaging AI
            on a single laptop.
          </h1>
          <p className="lead mt-5 max-w-2xl">
            NeuroLesion AI is a Bachelor of Computer Science Final Year
            Project from the Department of Computer Science, Government
            College University, Lahore. It demonstrates that meaningful
            stroke-imaging AI can be built end to end on commodity hardware
            with transparent methodology.
          </p>
        </div>
      </section>

      <section className="py-20 border-y border-clinical-border bg-white">
        <div className="container-wide grid lg:grid-cols-3 gap-10">
          <div>
            <span className="section-eyebrow">Motivation</span>
            <h2 className="h3 mt-3">Why stroke?</h2>
          </div>
          <div className="lg:col-span-2 space-y-4 text-clinical-muted leading-relaxed">
            <p>
              Stroke is the second-leading cause of death globally and the
              third-leading cause of long-term disability. Every minute of
              delay in identifying the ischaemic core worsens functional
              outcome.
            </p>
            <p>
              Manual delineation of stroke lesions on MRI is time-consuming,
              subjective, and bottlenecked by radiologist availability -
              especially in low-resource settings. NeuroLesion AI shows that
              a lightweight, locally-runnable model can complement the
              radiology workflow.
            </p>
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="container-wide">
          <div className="max-w-2xl">
            <span className="section-eyebrow">Methodology</span>
            <h2 className="h2 mt-3">Honest engineering, transparent metrics.</h2>
            <p className="lead mt-4">
              The pipeline is deliberately small and reproducible, with every
              choice documented and every metric computed on a held-out test
              set the model never saw during training.
            </p>
          </div>
          <div className="mt-12 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {TECH.map((t) => (
              <div key={t.title} className="card card-hover">
                <div className="w-11 h-11 rounded-xl bg-brand-50 text-brand-700 flex items-center justify-center mb-4">
                  <t.icon className="w-5 h-5" strokeWidth={2.2} />
                </div>
                <div className="h3 text-lg">{t.title}</div>
                <p className="mt-2 text-sm text-clinical-muted leading-relaxed">{t.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-white border-y border-clinical-border">
        <div className="container-wide grid lg:grid-cols-2 gap-12">
          <div>
            <span className="section-eyebrow">Results</span>
            <h2 className="h2 mt-3">Performance snapshot</h2>
            <p className="lead mt-4">
              Trained for 6 epochs on a single laptop CPU. All metrics are
              computed on patients the model never saw during training or
              validation. The high-precision / lower-recall pattern reflects
              the conservative model trained at 64x64 resolution; future GPU
              training at higher resolution is expected to lift recall.
            </p>
          </div>
          <div className="card !p-0 overflow-hidden">
            <table className="w-full text-sm">
              <tbody>
                {RESULTS.map(([k, v], i) => (
                  <tr
                    key={k}
                    className={i % 2 === 0 ? "bg-clinical-bg" : "bg-white"}
                  >
                    <td className="px-5 py-3 text-clinical-muted">{k}</td>
                    <td className="px-5 py-3 font-mono font-bold text-clinical-ink text-right">{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="container-wide grid lg:grid-cols-2 gap-12 items-start">
          <div>
            <span className="section-eyebrow">Limitations</span>
            <h2 className="h2 mt-3">Honest scope</h2>
          </div>
          <ul className="space-y-3 text-clinical-ink">
            {[
              "Trained on CPU only - architecture and resolution were chosen for tractability, not for state-of-the-art accuracy.",
              "Single modality (DWI). Multi-modal fusion (DWI + ADC + FLAIR) is left as future work.",
              "Diagnostic report uses a deterministic template generator. A fine-tuned medical LLM is the planned next iteration.",
              "Longitudinal pre/post analysis is demonstrated using a synthetic post-treatment mask - real follow-up scans will replace it in production.",
              "Academic prototype only. NOT a regulated medical device.",
            ].map((s) => (
              <li key={s} className="flex items-start gap-3 card !py-4">
                <ShieldAlert className="w-5 h-5 text-amber-600 mt-0.5 shrink-0" />
                <span className="text-sm leading-relaxed">{s}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="py-20 bg-clinical-ink text-white">
        <div className="container-narrow text-center">
          <h2 className="text-3xl md:text-4xl font-bold">Run it yourself.</h2>
          <p className="text-slate-300 mt-3">
            The analyser is fully local - no data leaves your laptop.
          </p>
          <div className="mt-8 flex justify-center gap-3 flex-wrap">
            <Link to="/analyze" className="btn-primary text-base !py-3.5 !px-6">
              Launch Analyzer <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
