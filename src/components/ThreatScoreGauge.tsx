import React from 'react';

interface ThreatScoreGaugeProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  label?: string;
}

const ThreatScoreGauge: React.FC<ThreatScoreGaugeProps> = ({ score, size = 'md', label }) => {
  const sizeClasses = {
    sm: 'w-16 h-16',
    md: 'w-24 h-24',
    lg: 'w-32 h-32'
  };

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-neon-red';
    if (score >= 60) return 'text-neon-orange';
    if (score >= 40) return 'text-yellow-500';
    return 'text-neon-green';
  };

  const getStrokeColor = (score: number) => {
    if (score >= 80) return '#ef4444';
    if (score >= 60) return '#f97316';
    if (score >= 40) return '#eab308';
    return '#10b981';
  };

  const circumference = 2 * Math.PI * 45;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center space-y-2">
      <div className={`relative ${sizeClasses[size]}`}>
        <svg className="transform -rotate-90 w-full h-full" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="currentColor"
            strokeWidth="8"
            fill="none"
            className="text-slate-200 dark:text-slate-700"
          />
          {/* Progress circle */}
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke={getStrokeColor(score)}
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-1000 ease-out"
            style={{
              filter: `drop-shadow(0 0 6px ${getStrokeColor(score)}40)`
            }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={`font-bold ${getScoreColor(score)} ${textSizes[size]}`}>
              {Math.round(score)}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 -mt-1">
              Risk
            </div>
          </div>
        </div>
      </div>
      {label && (
        <div className="text-xs text-slate-600 dark:text-slate-400 text-center font-medium">
          {label}
        </div>
      )}
    </div>
  );
};

export default ThreatScoreGauge;