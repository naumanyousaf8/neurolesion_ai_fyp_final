import { Link, NavLink } from "react-router-dom";
import { Brain, Menu, X } from "lucide-react";
import { useState } from "react";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const linkClass = ({ isActive }) =>
    `text-sm font-medium transition ${
      isActive
        ? "text-brand-700"
        : "text-clinical-muted hover:text-clinical-ink"
    }`;

  return (
    <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-clinical-border">
      <div className="container-wide flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-glow group-hover:shadow-cardLg transition">
            <Brain className="w-5 h-5 text-white" strokeWidth={2.4} />
          </div>
          <div className="leading-tight">
            <div className="font-bold text-[15px] text-clinical-ink">
              NeuroLesion <span className="text-brand-600">AI</span>
            </div>
            <div className="text-[10.5px] text-clinical-muted tracking-wider uppercase font-semibold">
              Clinical&nbsp;Imaging&nbsp;Suite
            </div>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-7">
          <NavLink to="/" end className={linkClass}>Home</NavLink>
          <a href="/#features" className="text-sm font-medium text-clinical-muted hover:text-clinical-ink transition">Features</a>
          <a href="/#how" className="text-sm font-medium text-clinical-muted hover:text-clinical-ink transition">How it works</a>
          <NavLink to="/about" className={linkClass}>About</NavLink>
          <Link to="/analyze" className="btn-primary !py-2 !px-4">
            Open Analyzer
          </Link>
        </nav>

        <button
          className="md:hidden p-2 rounded-lg text-clinical-ink"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {open && (
        <div className="md:hidden border-t border-clinical-border bg-white">
          <div className="container-wide py-4 flex flex-col gap-3">
            <NavLink to="/" end className={linkClass} onClick={() => setOpen(false)}>Home</NavLink>
            <a href="/#features" className="text-sm font-medium text-clinical-muted" onClick={() => setOpen(false)}>Features</a>
            <a href="/#how" className="text-sm font-medium text-clinical-muted" onClick={() => setOpen(false)}>How it works</a>
            <NavLink to="/about" className={linkClass} onClick={() => setOpen(false)}>About</NavLink>
            <Link to="/analyze" className="btn-primary !py-2 !px-4 self-start" onClick={() => setOpen(false)}>
              Open Analyzer
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
