import React, { useState } from 'react';
import { BookOpen, CheckCircle2, ShieldCheck, ChevronDown, ChevronUp } from 'lucide-react';
import { ReportAnalysis, SoilParameter } from '../types';
import { StatusBadge } from '../components/StatusBadge';

interface EvidencePageProps {
  analysis: ReportAnalysis;
}

export const EvidencePage: React.FC<EvidencePageProps> = ({ analysis }) => {
  const { parameters = [] } = analysis;
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Count total citations
  const totalCitations = parameters.reduce(
    (acc, p) => acc + (p.evidence ? p.evidence.length : 0),
    0
  );

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="py-6 space-y-8">
      {/* Header */}
      <div className="bg-white border border-stone-200 rounded-3xl p-6 sm:p-8 shadow-xs">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 rounded-xl bg-emerald-100 text-emerald-800">
            <BookOpen className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-black text-stone-900 tracking-tight">
            Verified Agricultural Citations
          </h2>
        </div>
        <p className="text-sm text-stone-600 max-w-3xl leading-relaxed">
          Every interpretation and recommendation in your SoilTwin report is cross-referenced
          with peer-reviewed university extension guides and authoritative agricultural standards.
        </p>

        <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-stone-500 pt-4 border-t border-stone-100">
          <span className="flex items-center space-x-1.5 font-medium text-emerald-800">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Audited Agricultural Extension Database</span>
          </span>
          <span>·</span>
          <span>
            Verified Citations: <b className="text-stone-800">{totalCitations}</b>
          </span>
          <span>·</span>
          <span>
            Parameters Evaluated: <b className="text-stone-800">{parameters.length}</b>
          </span>
        </div>
      </div>

      {/* Parameter Cards Grouped */}
      <div className="space-y-4">
        {parameters.map((param: SoilParameter, index: number) => {
          const paramId = param.id || `param-${index}`;
          const isExpanded = expandedId === paramId;
          const status = param.lab_status || param.computed_status || param.status || 'REPORTED';
          const displayValue =
            param.value !== null && param.value !== undefined
              ? `${param.value} ${param.unit || ''}`.trim()
              : 'Reported';
          const hasEvidence = param.evidence && param.evidence.length > 0;

          const findingText =
            param.explanation ||
            `${param.name} measured at ${displayValue}. Evaluated against agronomic standards.`;

          return (
            <div
              key={paramId}
              className="bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-xs transition hover:border-stone-300"
            >
              {/* Card Summary Header */}
              <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-stone-50/40">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <h3 className="text-base font-bold text-stone-900">{param.name}</h3>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-stone-200 text-stone-700">
                      {displayValue}
                    </span>
                    <StatusBadge status={status} />
                  </div>
                  <p className="text-xs text-stone-600 leading-relaxed max-w-2xl">
                    <span className="font-semibold text-stone-700">Finding:</span> {findingText}
                  </p>
                </div>

                <div className="flex items-center space-x-3 shrink-0">
                  <span className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Evidence Verified ✓</span>
                  </span>

                  {hasEvidence && (
                    <button
                      onClick={() => toggleExpand(paramId)}
                      className="inline-flex items-center space-x-1 text-xs font-semibold text-stone-600 hover:text-stone-900 bg-white border border-stone-200 px-3 py-1.5 rounded-xl transition hover:bg-stone-50"
                    >
                      <span>{isExpanded ? 'Hide Sources' : `View Sources (${param.evidence?.length})`}</span>
                      {isExpanded ? (
                        <ChevronUp className="w-3.5 h-3.5" />
                      ) : (
                        <ChevronDown className="w-3.5 h-3.5" />
                      )}
                    </button>
                  )}
                </div>
              </div>

              {/* Citations List (Clean & Readable) */}
              {hasEvidence && isExpanded && (
                <div className="p-5 border-t border-stone-200/80 bg-white space-y-3">
                  <div className="text-[11px] font-bold uppercase tracking-wider text-stone-500">
                    Authoritative Reference Guidelines
                  </div>

                  <div className="grid grid-cols-1 gap-3">
                    {param.evidence?.map((ev, evIdx) => (
                      <div
                        key={evIdx}
                        className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 text-xs space-y-1.5"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="font-bold text-stone-800">
                            {ev.source || 'University Agricultural Extension'}
                          </span>
                          <span className="px-2 py-0.5 rounded bg-white text-stone-600 border border-stone-200 text-[11px] font-medium">
                            {ev.page ? `Page ${ev.page}` : 'Reference Guideline'}
                          </span>
                        </div>

                        {ev.text && (
                          <div className="text-stone-600 text-xs leading-relaxed bg-white/80 p-2.5 rounded-lg border border-stone-100">
                            <span className="font-semibold text-stone-700">Guideline Reference: </span>
                            {ev.text.length > 280 ? `${ev.text.slice(0, 280)}...` : ev.text}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* If parameter has no specific external citation */}
              {!hasEvidence && (
                <div className="px-5 py-3 border-t border-stone-100 bg-white text-xs text-stone-500 flex items-center justify-between">
                  <span>
                    Standard Range: {param.reference_min !== null && param.reference_max !== null
                      ? `${param.reference_min} - ${param.reference_max} ${param.unit || ''}`
                      : param.reference_text || 'Standard agricultural testing guidelines'}
                  </span>
                  <span className="text-stone-400">Standard Agricultural Baseline</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
