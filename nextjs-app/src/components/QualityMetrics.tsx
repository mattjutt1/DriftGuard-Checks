"use client";

import { OptimizationMetrics } from "../hooks/useOptimization";

// UI Component Types
interface ProgressBarProps {
  label: string;
  value: number;
  maxValue?: number;
  className?: string;
  showValue?: boolean;
}

interface QualityMetricsProps {
  metrics: OptimizationMetrics;
  overallScore?: number;
}

// Progress Bar Component
function ProgressBar({ label, value, maxValue = 10, className = "", showValue = true }: ProgressBarProps) {
  const percentage = Math.min((value / maxValue) * 100, 100);
  
  const getColorClass = (percentage: number) => {
    if (percentage >= 80) return "bg-emerald-500";
    if (percentage >= 60) return "bg-blue-500";
    if (percentage >= 40) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className={`space-y-1 ${className}`}>
      <div className="flex justify-between items-center text-sm">
        <span className="font-medium text-gray-700">{label}</span>
        {showValue && (
          <span className="text-gray-600">{value.toFixed(1)}/{maxValue}</span>
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          className={`h-2.5 rounded-full transition-all duration-500 ease-out ${getColorClass(percentage)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// Quality Metrics Dashboard Component
export function QualityMetrics({ metrics, overallScore }: QualityMetricsProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Quality Metrics</h3>
        {overallScore && (
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-600">Overall Score:</span>
            <span className="text-xl font-bold text-blue-600">{overallScore.toFixed(1)}</span>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ProgressBar label="Clarity" value={metrics.clarity} />
        <ProgressBar label="Specificity" value={metrics.specificity} />
        <ProgressBar label="Engagement" value={metrics.engagement} />
        {metrics.structure && (
          <ProgressBar label="Structure" value={metrics.structure} />
        )}
        {metrics.completeness && (
          <ProgressBar label="Completeness" value={metrics.completeness} />
        )}
        {metrics.error_prevention && (
          <ProgressBar label="Error Prevention" value={metrics.error_prevention} />
        )}
      </div>
    </div>
  );
}