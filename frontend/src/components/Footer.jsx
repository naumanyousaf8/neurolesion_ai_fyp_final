import { Brain, GraduationCap, ShieldAlert } from "lucide-react";

export default function Footer() {
  return (
    <footer className="border-t border-clinical-border bg-white">
      <div className="container-wide py-12 grid md:grid-cols-3 gap-10">
        <div>
          <div className="flex items-center gap-2.5 mb-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center">
              <Brain className="w-4 h-4 text-white" strokeWidth={2.4} />
            </div>
            <span className="font-bold text-clinical-ink">NeuroLesion AI</span>
          </div>
          <p className="text-sm text-clinical-muted leading-relaxed max-w-sm">
            AI-powered stroke lesion segmentation, longitudinal analysis, and
            structured radiology reporting on diffusion-weighted MRI.
          </p>
        </div>

        <div>
          <div className="text-sm font-bold text-clinical-ink mb-3 flex items-center gap-2">
            <GraduationCap className="w-4 h-4 text-brand-600" />
            Academic project
          </div>
          <p className="text-sm text-clinical-muted leading-relaxed">
            Final Year Project, BS Computer Science.<br/>
            Supervisor: Dr. Zia Ur Rehman.<br/>
            Department of Computer Science,<br/>
            Government College University, Lahore.
          </p>
        </div>

        <div>
          <div className="text-sm font-bold text-clinical-ink mb-3 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-amber-600" />
            Disclaimer
          </div>
          <p className="text-sm text-clinical-muted leading-relaxed">
            Research / educational prototype only. <b>Not</b> a clinical
            diagnostic device. All AI findings must be confirmed by a
            qualified radiologist before any clinical use.
          </p>
        </div>
      </div>

      <div className="border-t border-clinical-border">
        <div className="container-wide py-5 text-xs text-clinical-muted flex flex-wrap justify-between items-center gap-2">
          <span>&copy; {new Date().getFullYear()} NeuroLesion AI - FYP prototype.</span>
          <span>
            Built with PyTorch &middot; FastAPI &middot; React &middot; Tailwind CSS
          </span>
        </div>
      </div>
    </footer>
  );
}
