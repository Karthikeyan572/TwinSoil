import React, { useState, useEffect } from 'react';
import {
  FileText,
  Download,
  Printer,
  ArrowLeft,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Sprout
} from 'lucide-react';
import { FinalAnalysis, ReportAnalysis } from '../types';
import { api } from '../services/api';
import { StatusBadge } from './StatusBadge';

interface FinalReportModalProps {
  analysis: ReportAnalysis;
  onClose: () => void;
}

export const FinalReportModal: React.FC<FinalReportModalProps> = ({ analysis, onClose }) => {
  const [data, setData] = useState<FinalAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [pdfDownloading, setPdfDownloading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const load = async () => {
      try {
        setLoading(true);
        const res = await api.getFinalAnalysis(analysis.report_id, analysis);
        if (isMounted) setData(res);
      } catch (err) {
        console.error('Failed to load final report analysis', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };
    load();
    return () => {
      isMounted = false;
    };
  }, [analysis.report_id]);

  const handleDownload = async () => {
    setPdfDownloading(true);
    try {
      await api.downloadReportPdf(analysis.report_id);
    } finally {
      setPdfDownloading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading || !data) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/60 backdrop-blur-xs">
        <div className="bg-white p-8 rounded-3xl shadow-xl flex items-center space-x-3 text-stone-800">
          <Loader2 className="w-5 h-5 animate-spin text-emerald-600" />
          <span className="font-semibold text-sm">Compiling verified final soil health assessment...</span>
        </div>
      </div>
    );
  }

  const { report_metadata, executive_summary, parameters, crop_suitability, provenance_audit } = data;

  const isCritical =
    executive_summary.overall_health_status.toUpperCase().includes('ATTENTION') ||
    executive_summary.overall_health_status.toUpperCase().includes('CRITICAL');

  return (
    <div className="fixed inset-0 z-50 bg-stone-900/70 backdrop-blur-xs overflow-y-auto p-2 sm:p-6 flex justify-center">
      <div className="bg-white max-w-4xl w-full rounded-3xl shadow-2xl border border-stone-200 overflow-hidden my-auto print:m-0 print:border-none print:shadow-none print:max-w-none print:w-full">
        {/* Top Control Bar (Hidden when printing) */}
        <div className="sticky top-0 z-20 bg-stone-900 text-white px-6 py-3.5 flex flex-wrap items-center justify-between gap-3 print:hidden">
          <button
            onClick={onClose}
            className="inline-flex items-center space-x-2 text-xs font-semibold text-stone-300 hover:text-white transition cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Dashboard</span>
          </button>

          <div className="flex items-center space-x-2.5">
            <button
              onClick={handlePrint}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-stone-800 hover:bg-stone-700 text-stone-200 transition cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print</span>
            </button>

            <button
              onClick={handleDownload}
              disabled={pdfDownloading}
              className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white transition shadow-xs disabled:opacity-50 cursor-pointer"
            >
              {pdfDownloading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Generating PDF...</span>
                </>
              ) : (
                <>
                  <Download className="w-3.5 h-3.5" />
                  <span>Download PDF</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Document Body */}
        <div className="p-6 sm:p-10 space-y-8 bg-white text-stone-900 print:p-0 print:space-y-6">
          {/* Document Header */}
          <div className="border-b border-stone-200 pb-6 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-emerald-800 font-extrabold text-sm tracking-wider uppercase">
                <Sprout className="w-5 h-5 text-emerald-600" />
                <span>SoilTwin AI Decision Support</span>
              </div>
              <span className="text-xs font-medium text-stone-400">
                Official Advisory Document
              </span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-black text-stone-900 tracking-tight">
              Comprehensive Soil Health Assessment &amp; Agronomic Advisory
            </h1>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs text-stone-600 pt-2">
              <div>
                <span className="text-stone-400 block uppercase text-[10px] font-bold">Sample / Report ID</span>
                <span className="font-mono font-semibold text-stone-800">{report_metadata.report_id.slice(0, 16)}</span>
              </div>
              <div>
                <span className="text-stone-400 block uppercase text-[10px] font-bold">Report Name</span>
                <span className="font-semibold text-stone-800">{report_metadata.report_name}</span>
              </div>
              <div>
                <span className="text-stone-400 block uppercase text-[10px] font-bold">Analysis Date</span>
                <span className="font-semibold text-stone-800">{report_metadata.date}</span>
              </div>
              <div>
                <span className="text-stone-400 block uppercase text-[10px] font-bold">Testing Standard</span>
                <span className="font-semibold text-stone-800">{report_metadata.lab_name}</span>
              </div>
            </div>
          </div>

          {/* Section 1: Executive Summary */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-base font-bold text-stone-900 uppercase tracking-wider">
                1. Executive Summary &amp; Overall Health
              </h2>
              <span
                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
                  isCritical
                    ? 'bg-rose-100 text-rose-800 border border-rose-200'
                    : 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                }`}
              >
                {isCritical ? (
                  <AlertTriangle className="w-3.5 h-3.5 mr-1 text-rose-600" />
                ) : (
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                )}
                {executive_summary.overall_health_status}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Primary Concerns */}
              <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-stone-500">
                  Key Findings &amp; Limiting Factors
                </span>
                <ul className="space-y-1.5 text-xs text-stone-700">
                  {executive_summary.key_findings.map((f, idx) => (
                    <li key={idx} className="flex items-start space-x-1.5">
                      <span className="text-emerald-700 font-bold">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Priority Actions */}
              <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200/80 space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-900">
                  Priority Agronomic Actions
                </span>
                <ul className="space-y-1.5 text-xs text-emerald-950 font-medium">
                  {executive_summary.priority_actions.map((act, idx) => (
                    <li key={idx} className="flex items-start space-x-1.5">
                      <span className="text-emerald-600 font-bold">✓</span>
                      <span>{act}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Section 2: Soil Chemistry & Nutrient Evaluation */}
          <div className="space-y-3">
            <h2 className="text-base font-bold text-stone-900 uppercase tracking-wider">
              2. Measured Soil Parameters &amp; Lab Standards
            </h2>

            <div className="border border-stone-200 rounded-2xl overflow-hidden shadow-xs">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-stone-900 text-white font-bold">
                    <th className="py-2.5 px-3">Parameter</th>
                    <th className="py-2.5 px-3">Measured</th>
                    <th className="py-2.5 px-3">Reference Range</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3">Agronomic Evaluation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-200 text-stone-700">
                  {parameters.map((p, idx) => (
                    <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-stone-50/50'}>
                      <td className="py-2.5 px-3 font-bold text-stone-900">{p.name}</td>
                      <td className="py-2.5 px-3 font-semibold">
                        {p.value !== null && p.value !== undefined ? `${p.value} ${p.unit || ''}` : 'Reported'}
                      </td>
                      <td className="py-2.5 px-3 text-stone-500">{p.reference_text}</td>
                      <td className="py-2.5 px-3">
                        <StatusBadge status={p.status} />
                      </td>
                      <td className="py-2.5 px-3 text-stone-600 leading-relaxed max-w-xs">
                        {p.interpretation}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 3: Corrective Management Plan */}
          <div className="space-y-3">
            <h2 className="text-base font-bold text-stone-900 uppercase tracking-wider">
              3. Corrective Management &amp; Application Plan
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {parameters
                .filter((p) => p.action_item)
                .map((p, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-stone-50 border border-stone-200 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-stone-900">{p.name} Corrective Practice</span>
                      <StatusBadge status={p.status} />
                    </div>
                    <p className="text-stone-700 leading-relaxed">{p.action_item}</p>
                  </div>
                ))}
            </div>
          </div>

          {/* Section 4: Crop Suitability Guidance */}
          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200 space-y-2">
            <h2 className="text-xs font-bold text-stone-500 uppercase tracking-wider">
              4. Regional Crop Suitability Evaluation
            </h2>
            <p className="text-xs text-stone-700 leading-relaxed">
              {crop_suitability.explanation ||
                'To evaluate crop suitability, sync ambient weather data (temperature, humidity, rainfall) in the Crop Recommendation tab.'}
            </p>
          </div>

          {/* Section 5: Authoritative Evidence & Provenance */}
          <div className="space-y-3 border-t border-stone-200 pt-6">
            <div className="flex items-center space-x-2 text-stone-900">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <h2 className="text-xs font-bold uppercase tracking-wider">
                5. Extension Evidence &amp; Provenance Audit
              </h2>
            </div>
            <p className="text-xs text-stone-500 leading-relaxed">
              All findings and threshold benchmarks in this report are grounded in peer-reviewed university extension guides
              and soil testing manuals:
            </p>

            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-stone-700">
              {provenance_audit.guidelines_referenced.map((ref, idx) => (
                <li key={idx} className="flex items-center space-x-1.5 p-2 rounded-lg bg-stone-50 border border-stone-200">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                  <span className="truncate">{ref}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Document Footer */}
          <div className="border-t border-stone-200 pt-4 text-[11px] text-stone-400 space-y-1">
            <p>
              <b>Standard Agronomic Advisory Disclaimer:</b> This report is an evidence-grounded decision support tool prepared
              by SoilTwin AI. Soil amendment rates reflect university extension standards. Field outcomes depend on seasonal
              moisture, cultivar genetics, and local application practices.
            </p>
            <p className="text-[10px] text-stone-400">
              Generated by SoilTwin AI on {report_metadata.date} · Report ID: {report_metadata.report_id}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
