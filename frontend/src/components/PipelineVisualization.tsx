import React from 'react';
import { CheckCircle2, Loader2, Sparkles, ShieldCheck, Database, FileSearch } from 'lucide-react';
import { PipelineStep } from '../types';

interface PipelineVisualizationProps {
  steps?: PipelineStep[];
  isProcessing?: boolean;
}

export const PipelineVisualization: React.FC<PipelineVisualizationProps> = ({
  steps = [],
  isProcessing = false,
}) => {
  const defaultSteps: PipelineStep[] = [
    { step: 'Report Received', detail: 'Uploaded lab document validated & registered', status: 'COMPLETED' },
    { step: 'Document Parsed', detail: 'PyMuPDF digital text & table structure extracted', status: 'COMPLETED' },
    { step: 'Parameters Extracted', detail: 'Canonical soil parameters identified & deterministically verified', status: 'COMPLETED' },
    { step: 'Evidence Retrieved', detail: 'Parameter-aware vector search across extension publications', status: 'COMPLETED' },
    { step: 'Interpretation & Critic', detail: 'Claim-to-evidence validation & numerical range checks passed', status: 'COMPLETED' },
  ];

  const activeSteps = steps && steps.length > 0 ? steps : defaultSteps;

  const getStepIcon = (index: number) => {
    switch (index) {
      case 0: return <CheckCircle2 className="w-5 h-5 text-emerald-600" />;
      case 1: return <FileSearch className="w-5 h-5 text-emerald-600" />;
      case 2: return <Database className="w-5 h-5 text-emerald-600" />;
      case 3: return <Sparkles className="w-5 h-5 text-emerald-600" />;
      case 4: return <ShieldCheck className="w-5 h-5 text-emerald-600" />;
      default: return <CheckCircle2 className="w-5 h-5 text-emerald-600" />;
    }
  };

  return (
    <div className="bg-white border border-stone-200 rounded-2xl p-6 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-stone-700">
            Agentic AI Pipeline Execution
          </h3>
        </div>
        <span className="text-xs text-stone-500 font-medium">Supervisor Workflow · Max Retries: 2</span>
      </div>

      <div className="space-y-3">
        {activeSteps.map((s, idx) => (
          <div
            key={idx}
            className="flex items-start space-x-3 p-3 rounded-xl bg-stone-50/80 border border-stone-100 transition-all hover:bg-stone-50"
          >
            <div className="mt-0.5 shrink-0">
              {s.status === 'RUNNING' || (isProcessing && idx === activeSteps.length - 1) ? (
                <Loader2 className="w-5 h-5 text-emerald-600 animate-spin" />
              ) : (
                getStepIcon(idx)
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <span className="text-sm font-semibold text-stone-900">{s.step}</span>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-emerald-100 text-emerald-800">
                  {s.status}
                </span>
              </div>
              <p className="text-xs text-stone-600 mt-0.5">{s.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
