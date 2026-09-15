import React from 'react';

interface StatusBadgeProps {
  status?: string | null;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  if (!status) return null;

  const normalized = status.toUpperCase();

  let colorClasses = 'bg-stone-100 text-stone-700 border-stone-200';

  if (
    normalized.includes('OPTIMAL') ||
    normalized.includes('WITHIN_RANGE') ||
    normalized.includes('SAFE') ||
    normalized.includes('GENERALLY WITHIN')
  ) {
    colorClasses = 'bg-emerald-50 text-emerald-800 border-emerald-300 ring-1 ring-emerald-500/20';
  } else if (
    normalized.includes('SLIGHTLY LOW') ||
    normalized.includes('LOW') ||
    normalized.includes('BELOW') ||
    normalized.includes('NEEDS ATTENTION')
  ) {
    colorClasses = 'bg-amber-50 text-amber-800 border-amber-300 ring-1 ring-amber-500/20';
  } else if (
    normalized.includes('DEFICIENT') ||
    normalized.includes('CRITICAL') ||
    normalized.includes('ELEVATED') ||
    normalized.includes('HIGH') ||
    normalized.includes('ABOVE')
  ) {
    colorClasses = 'bg-rose-50 text-rose-800 border-rose-300 ring-1 ring-rose-500/20';
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase tracking-wider border shadow-xs ${colorClasses} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-75"></span>
      {status.replace(/_/g, ' ')}
    </span>
  );
};
