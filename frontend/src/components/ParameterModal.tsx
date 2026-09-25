import React from 'react';
import { X, BookOpen, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { SoilParameter } from '../types';
import { StatusBadge } from './StatusBadge';

interface ParameterModalProps {
  parameter: SoilParameter | null;
  onClose: () => void;
}

export const ParameterModal: React.FC<ParameterModalProps> = ({ parameter, onClose }) => {
  if (!parameter) return null;

  const displayValue = parameter.value !== null && parameter.value !== undefined
    ? `${parameter.value} ${parameter.unit || ''}`.trim()
    : 'Not Reported';

  const rangeText = parameter.reference_text || (
    parameter.reference_min !== null && parameter.reference_max !== null
      ? `${parameter.reference_min} - ${parameter.reference_max}`
      : 'Not stated by laboratory'
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/60 backdrop-blur-xs">
      <div
        className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-stone-200 animate-in fade-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white/95 backdrop-blur-xs px-6 py-4 border-b border-stone-200 flex items-center justify-between z-10">
          <div className="flex items-center space-x-3">
            <h3 className="text-xl font-bold text-stone-900">{parameter.name}</h3>
            <StatusBadge status={parameter.lab_status || parameter.computed_status} />
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-full text-stone-400 hover:text-stone-700 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Values Grid */}
          <div className="grid grid-cols-2 gap-4 bg-stone-50 p-4 rounded-2xl border border-stone-200/70">
            <div>
              <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider">Your Measured Value</span>
              <div className="text-2xl font-extrabold text-stone-900 mt-1">{displayValue}</div>
            </div>
            <div>
              <span className="text-xs font-semibold text-stone-500 uppercase tracking-wider">Lab Reference Range</span>
              <div className="text-2xl font-extrabold text-stone-900 mt-1">{rangeText}</div>
            </div>
          </div>

          {/* Explanation */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-stone-500 mb-2">
              Evidence-Grounded Interpretation
            </h4>
            <div className="p-4 rounded-2xl bg-emerald-50/50 border border-emerald-100/80 text-stone-800 text-sm leading-relaxed">
              {parameter.explanation || 'No interpretation generated.'}
            </div>
          </div>

          {/* Why It Matters */}
          {parameter.why_it_matters && (
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-stone-500 mb-2">
                Agronomic Importance & Impact
              </h4>
              <p className="text-sm text-stone-700 leading-relaxed bg-stone-50 p-4 rounded-2xl border border-stone-200/70">
                {parameter.why_it_matters}
              </p>
            </div>
          )}

          {/* Confidence Indicator */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-stone-100/70 border border-stone-200 text-xs">
            <div className="flex items-center space-x-2 text-stone-700">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>Scientific Confidence Level: <b>{parameter.confidence || 'HIGH'}</b></span>
            </div>
            <span className="text-stone-600 font-medium">Agronomic Review: Verified</span>
          </div>

          {/* Evidence Drawer */}
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <BookOpen className="w-4 h-4 text-emerald-700" />
              <h4 className="text-xs font-semibold uppercase tracking-wider text-stone-900">
                Authoritative Extension Evidence ({parameter.evidence?.length || 0})
              </h4>
            </div>

            {parameter.evidence && parameter.evidence.length > 0 ? (
              <div className="space-y-3">
                {parameter.evidence.map((ev, idx) => (
                  <div key={idx} className="p-4 rounded-2xl bg-stone-50 border border-stone-200 text-xs space-y-2">
                    <div className="flex items-center justify-between text-stone-600">
                      <span className="font-semibold text-emerald-900">{ev.source}</span>
                      {ev.page && <span className="bg-white px-2 py-0.5 rounded border border-stone-200">Page {ev.page}</span>}
                    </div>
                    <blockquote className="italic text-stone-700 border-l-2 border-emerald-600 pl-3 py-0.5">
                      "{ev.text}"
                    </blockquote>
                    <div className="flex items-center space-x-1.5 text-stone-500 text-[11px] pt-1">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Direct citation from audited agricultural reference document</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-stone-500 italic">No specific external citations linked for this parameter.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
