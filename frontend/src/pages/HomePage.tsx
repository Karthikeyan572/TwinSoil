import React from 'react';
import { Upload, Sparkles, Shield, Cpu, BookOpen, ArrowRight, CheckCircle2 } from 'lucide-react';

interface HomePageProps {
  onStartUpload: () => void;
  onTryDemo: () => void;
  isDemoLoading: boolean;
}

export const HomePage: React.FC<HomePageProps> = ({
  onStartUpload,
  onTryDemo,
  isDemoLoading,
}) => {
  return (
    <div className="space-y-16 py-8">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-emerald-900 via-stone-900 to-stone-900 text-white p-8 sm:p-14 shadow-2xl border border-emerald-800/40">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none"></div>
        <div className="max-w-3xl relative z-10 space-y-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-xs font-semibold tracking-wide uppercase">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Agentic Agricultural Intelligence</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight">
            Understand Your Soil. <br />
            <span className="text-emerald-400">Backed by Evidence.</span>
          </h1>

          <p className="text-stone-300 text-base sm:text-lg leading-relaxed max-w-2xl">
            Upload any soil-test report (PDF or image). SoilTwin AI extracts every scientifically relevant measurement,
            validates numbers deterministically, cites university extension literature, and runs a trained ML model for crop suitability.
          </p>

          <div className="flex flex-wrap gap-4 pt-4">
            <button
              onClick={onStartUpload}
              className="inline-flex items-center space-x-2 px-6 py-3.5 rounded-xl font-bold bg-emerald-500 hover:bg-emerald-400 text-stone-950 transition shadow-lg shadow-emerald-500/25 cursor-pointer"
            >
              <Upload className="w-5 h-5" />
              <span>Analyze Soil Report</span>
            </button>

            <button
              onClick={onTryDemo}
              disabled={isDemoLoading}
              className="inline-flex items-center space-x-2 px-6 py-3.5 rounded-xl font-bold bg-white/10 hover:bg-white/20 text-white border border-white/15 transition cursor-pointer disabled:opacity-50"
            >
              <Sparkles className="w-5 h-5 text-emerald-300" />
              <span>{isDemoLoading ? 'Loading Demo...' : 'Try Demo (Duffy Rear)'}</span>
            </button>
          </div>

          <div className="flex items-center space-x-6 text-xs text-stone-400 pt-6 border-t border-white/10">
            <div className="flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Zero Hallucination Guarantee</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Audited Extension Citations</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Real Scikit-Learn ML Classifier</span>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - 3 Layer Mental Model */}
      <section className="space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-stone-900">
            The Three-Layer Agricultural Architecture
          </h2>
          <p className="text-sm text-stone-600">
            Built as a genuine scientific intelligence system — not a PDF uploader wrapped around a chatbot.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white border border-stone-200 rounded-3xl p-6 shadow-xs hover:border-emerald-300 transition">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 flex items-center justify-center text-emerald-700 mb-4">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-stone-900 mb-2">1. Agentic AI</h3>
            <p className="text-xs text-stone-600 leading-relaxed">
              Supervisor, Parser, Retrieval, Interpreter, Critic, and Crop agents orchestrated via LangGraph with bounded retries (Max Retries = 2) and deterministic numerical validation.
            </p>
          </div>

          <div className="bg-white border border-stone-200 rounded-3xl p-6 shadow-xs hover:border-emerald-300 transition">
            <div className="w-12 h-12 rounded-2xl bg-sky-100 flex items-center justify-center text-sky-700 mb-4">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-stone-900 mb-2">2. Grounded RAG</h3>
            <p className="text-xs text-stone-600 leading-relaxed">
              Provides the knowledge foundation using all-MiniLM-L6-v2 embeddings and vector search across Penn State, Cornell, USDA NRCS, and Purdue Extension publications with exact page citations.
            </p>
          </div>

          <div className="bg-white border border-stone-200 rounded-3xl p-6 shadow-xs hover:border-emerald-300 transition">
            <div className="w-12 h-12 rounded-2xl bg-amber-100 flex items-center justify-center text-amber-700 mb-4">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-lg text-stone-900 mb-2">3. LLM Optimization & ML</h3>
            <p className="text-xs text-stone-600 leading-relaxed">
              Adaptive retrieval, context compression, model routing, caching, and an audited scikit-learn classifier for crop suitability that refuses to guess missing weather variables.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
