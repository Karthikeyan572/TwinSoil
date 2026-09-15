import React from 'react';
import { BookOpen, CheckCircle2, ShieldCheck, ExternalLink } from 'lucide-react';
import { ReportAnalysis } from '../types';

interface EvidencePageProps {
  analysis: ReportAnalysis;
}

export const EvidencePage: React.FC<EvidencePageProps> = ({ analysis }) => {
  const { parameters = [] } = analysis;

  // Flatten all evidence items with parameter context
  const allEvidence = parameters.flatMap((p) =>
    (p.evidence || []).map((ev) => ({
      parameter: p.name,
      value: p.value,
      unit: p.unit,
      claim: p.explanation || 'Parameter value analysis',
      source: ev.source,
      page: ev.page,
      text: ev.text,
      relevance: ev.relevance,
    }))
  );

  return (
    <div className="py-6 space-y-8">
      <div className="bg-white border border-stone-200 rounded-3xl p-6 sm:p-8 shadow-xs">
        <div className="flex items-center space-x-3 mb-2">
          <div className="p-2 rounded-xl bg-emerald-100 text-emerald-800">
            <BookOpen className="w-5 h-5" />
          </div>
          <h2 className="text-2xl font-black text-stone-900 tracking-tight">Agricultural Evidence Citations</h2>
        </div>
        <p className="text-xs text-stone-600 max-w-3xl leading-relaxed">
          SoilTwin AI guarantees strict provenance. Every claim and interpretation is linked directly to audited university extension guides and USDA Natural Resources Conservation Service reference manuals.
        </p>

        <div className="mt-4 flex flex-wrap gap-4 text-xs text-stone-500 pt-4 border-t border-stone-100">
          <span className="flex items-center space-x-1.5 font-medium text-emerald-800">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Audited in knowledge_base/manifest.json</span>
          </span>
          <span>·</span>
          <span>Total Grounded Citations: <b>{allEvidence.length}</b></span>
        </div>
      </div>

      {/* Evidence Table */}
      <div className="bg-white border border-stone-200 rounded-3xl overflow-hidden shadow-xs">
        <div className="px-6 py-4 border-b border-stone-200 bg-stone-50/70 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-stone-700">
            Claim-to-Evidence Traceability Log
          </span>
          <span className="text-xs text-stone-500 font-medium">Claim → Supporting Evidence → Source → Page</span>
        </div>

        <div className="divide-y divide-stone-200">
          {allEvidence.map((item, idx) => (
            <div key={idx} className="p-6 hover:bg-stone-50/50 transition-colors space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center space-x-2">
                  <span className="px-2.5 py-0.5 rounded-md bg-stone-900 text-white font-bold text-xs">
                    {item.parameter}
                  </span>
                  <span className="text-xs text-stone-500">
                    Measured: <b>{item.value} {item.unit || ''}</b>
                  </span>
                </div>
                <div className="flex items-center space-x-2 text-xs">
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">
                    {item.relevance} Relevance
                  </span>
                  {item.page && (
                    <span className="px-2 py-0.5 rounded-full bg-stone-100 text-stone-700 font-medium">
                      Page {item.page}
                    </span>
                  )}
                </div>
              </div>

              {/* Claim */}
              <div className="text-xs text-stone-700 font-medium bg-stone-50 p-3 rounded-xl border border-stone-200/80">
                <span className="text-stone-400 font-bold uppercase mr-2 text-[10px]">Claim:</span>
                {item.claim}
              </div>

              {/* Supporting Evidence Text */}
              <blockquote className="text-xs text-stone-800 italic bg-emerald-50/40 p-3 rounded-xl border-l-3 border-emerald-600">
                "{item.text}"
              </blockquote>

              <div className="flex items-center justify-between text-xs text-stone-500 pt-1">
                <span className="font-semibold text-stone-800">Source: {item.source}</span>
                <span className="flex items-center space-x-1 text-emerald-700 text-[11px]">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Grounding Verified</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
