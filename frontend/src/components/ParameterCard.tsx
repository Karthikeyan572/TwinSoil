import React from 'react';
import { ChevronRight, BookOpen } from 'lucide-react';
import { SoilParameter } from '../types';
import { StatusBadge } from './StatusBadge';

interface ParameterCardProps {
  parameter: SoilParameter;
  onSelect: (param: SoilParameter) => void;
}

export const ParameterCard: React.FC<ParameterCardProps> = ({ parameter, onSelect }) => {
  const displayValue = parameter.value !== null && parameter.value !== undefined
    ? `${parameter.value} ${parameter.unit || ''}`.trim()
    : 'Not Reported';

  const rangeText = parameter.reference_text || (
    parameter.reference_min !== null && parameter.reference_max !== null
      ? `${parameter.reference_min} - ${parameter.reference_max}`
      : 'Not stated'
  );

  return (
    <div
      onClick={() => onSelect(parameter)}
      className="group relative bg-white border border-stone-200 rounded-2xl p-5 hover:border-emerald-300 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
    >
      <div>
        <div className="flex items-start justify-between mb-3">
          <div>
            <h4 className="font-bold text-lg text-stone-900 group-hover:text-emerald-700 transition">
              {parameter.name}
            </h4>
            <span className="text-xs text-stone-500">
              Lab Range: {rangeText}
            </span>
          </div>
          <StatusBadge status={parameter.lab_status || parameter.computed_status || parameter.status} />
        </div>

        <div className="my-4">
          <div className="text-2xl font-extrabold text-stone-900 tracking-tight">
            {displayValue}
          </div>
          {(parameter.computed_status || parameter.status) && (
            <div className="text-xs text-stone-500 mt-1">
              Verified: <span className="font-medium text-stone-700">{(parameter.computed_status || parameter.status || '').replace(/_/g, ' ')}</span>
            </div>
          )}
        </div>

        {parameter.explanation && (
          <p className="text-xs text-stone-600 line-clamp-3 mt-2 leading-relaxed min-h-[3rem]">
            {parameter.explanation}
          </p>
        )}
      </div>

      <div className="pt-4 mt-4 border-t border-stone-100 flex items-center justify-between">
        <div className="flex items-center space-x-1.5 text-xs font-semibold text-emerald-700">
          <BookOpen className="w-3.5 h-3.5" />
          <span>{parameter.evidence?.length || 0} Citation(s)</span>
        </div>
        <button className="flex items-center space-x-1 text-xs font-semibold text-stone-600 group-hover:text-emerald-700 transition">
          <span>Understand</span>
          <ChevronRight className="w-4 h-4 transform group-hover:translate-x-0.5 transition" />
        </button>
      </div>
    </div>
  );
};
