import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts';
import { AlertCircle, CheckCircle2, FileText, Info } from 'lucide-react';
import { ReportAnalysis, SoilParameter } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { ParameterCard } from '../components/ParameterCard';
import { ParameterModal } from '../components/ParameterModal';
import { PipelineVisualization } from '../components/PipelineVisualization';

interface SoilDashboardPageProps {
  analysis: ReportAnalysis;
}

export const SoilDashboardPage: React.FC<SoilDashboardPageProps> = ({ analysis }) => {
  const [selectedParam, setSelectedParam] = useState<SoilParameter | null>(null);

  const { summary, parameters = [], pipeline_steps = [] } = analysis;

  // Prepare chart data for parameters with numeric values and ranges
  const chartData = parameters
    .filter((p) => p.value !== null && p.value !== undefined && p.reference_min !== null)
    .slice(0, 8) // Display primary parameters for clean visualization
    .map((p) => ({
      name: p.name,
      'Your Value': p.value,
      'Lab Min': p.reference_min || 0,
      'Lab Max': p.reference_max || p.reference_min || 0,
    }));

  return (
    <div className="space-y-8 py-6">
      {/* Overview Banner */}
      <div className="bg-white border border-stone-200 rounded-3xl p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-stone-100">
          <div>
            <div className="flex items-center space-x-3">
              <h2 className="text-2xl font-black text-stone-900 tracking-tight">Soil Health Overview</h2>
              <StatusBadge status={summary.overall_observation} />
            </div>
            <p className="text-xs text-stone-500 mt-1">
              Report ID: <code className="bg-stone-100 px-2 py-0.5 rounded text-stone-700 font-mono">{analysis.report_id}</code>
            </p>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold uppercase tracking-wider text-stone-400">Total Analyzed</span>
            <div className="text-xl font-extrabold text-stone-900">{parameters.length} Parameters</div>
          </div>
        </div>

        {/* Key Findings */}
        <div className="mt-6 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-stone-500 flex items-center space-x-1.5">
            <Info className="w-4 h-4 text-emerald-600" />
            <span>Key Diagnostic Findings</span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            {summary.key_findings.map((finding, idx) => (
              <div
                key={idx}
                className="flex items-start space-x-2.5 p-3 rounded-xl bg-stone-50 border border-stone-200/70 text-xs text-stone-700 leading-relaxed"
              >
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 shrink-0"></div>
                <span>{finding}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chart: Parameters vs Lab Reference Range */}
      {chartData.length > 0 && (
        <div className="bg-white border border-stone-200 rounded-3xl p-6 sm:p-8 shadow-xs">
          <div className="mb-6">
            <h3 className="text-base font-bold text-stone-900">Measured Values vs. Optimal Lab Ranges</h3>
            <p className="text-xs text-stone-500">
              Comparative visualization of extracted report measurements against baseline laboratory agronomic thresholds.
            </p>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: '#475569', fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#475569', fontSize: 11 }} tickLine={false} axisLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1c1917',
                    borderRadius: '12px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="Your Value" fill="#059669" radius={[6, 6, 0, 0]} barSize={24} />
                <Bar dataKey="Lab Min" fill="#cbd5e1" radius={[6, 6, 0, 0]} barSize={16} />
                <Bar dataKey="Lab Max" fill="#94a3b8" radius={[6, 6, 0, 0]} barSize={16} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Grid of Parameter Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-stone-900">Analyzed Soil Parameters</h3>
            <p className="text-xs text-stone-500">
              Click any parameter card to inspect evidence citations, why it matters, and scientific recommendations.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {parameters.map((param, idx) => (
            <ParameterCard key={idx} parameter={param} onSelect={(p) => setSelectedParam(p)} />
          ))}
        </div>
      </div>

      {/* Pipeline Checklist Observability */}
      {pipeline_steps && pipeline_steps.length > 0 && (
        <div className="mt-8">
          <PipelineVisualization steps={pipeline_steps} />
        </div>
      )}

      {/* Parameter Detail Modal */}
      <ParameterModal parameter={selectedParam} onClose={() => setSelectedParam(null)} />
    </div>
  );
};
