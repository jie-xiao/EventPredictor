import { ChevronDown, ChevronUp } from 'lucide-react';

interface ProbabilityBarProps {
  probabilities?: Array<{
    label: string;
    value: number;
    description?: string;
  }>;
  confidenceInterval?: number;
  showDetails?: boolean;
  onToggleDetails?: () => void;
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const getTrendColor = (label: string): string => {
  const l = label.toUpperCase();
  if (l.includes('UP') || l.includes('上涨')) return COLORS.status.success;
  if (l.includes('DOWN') || l.includes('下跌')) return COLORS.status.danger;
  if (l.includes('UNCERTAIN') || l.includes('不确定')) return COLORS.text.muted;
  return COLORS.status.warning;
};

const defaultProbabilities = [
  { label: 'UP', value: 0.85, description: 'Positive trend expected' },
  { label: 'SIDEWAYS', value: 0.08, description: 'No significant change' },
  { label: 'DOWN', value: 0.05, description: 'Negative trend possible' },
  { label: 'UNCERTAIN', value: 0.01, description: 'Insufficient data' },
  { label: 'OTHER', value: 0.01, description: 'Unforeseen factors' }
];

export default function ProbabilityBar({
  probabilities = defaultProbabilities,
  confidenceInterval = 95,
  showDetails = false,
  onToggleDetails
}: ProbabilityBarProps) {
  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-[14px] font-semibold" style={{ color: COLORS.text.primary }}>
          PROBABILITY DISTRIBUTION
        </h3>
        <button
          onClick={onToggleDetails}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all duration-200 hover:bg-[#00E5FF]10"
          style={{ color: COLORS.text.secondary }}
        >
          <span className="text-xs">{showDetails ? 'Collapse' : 'Expand'} Details</span>
          {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Probability Bars */}
      <div className="space-y-3">
        {probabilities.map((item, idx) => {
          const color = getTrendColor(item.label);
          const percentage = Math.round(item.value * 100);
          const barWidth = Math.max(percentage, 2); // Minimum 2% width for visibility

          return (
            <div key={idx} className="group">
              <div className="flex items-center justify-between mb-1.5">
                {/* Label */}
                <span
                  className="text-xs font-semibold uppercase tracking-wider"
                  style={{ color: color }}
                >
                  {item.label}
                </span>

                {/* Percentage */}
                <span className="text-xs font-mono" style={{ color: COLORS.text.muted }}>
                  {percentage}%
                </span>
              </div>

              {/* Bar Container */}
              <div
                className="h-3 rounded-full overflow-hidden relative group-hover:h-4 transition-all duration-200"
                style={{ backgroundColor: `${COLORS.border}50` }}
              >
                {/* Progress Bar */}
                <div
                  className="h-full rounded-full transition-all duration-500 relative"
                  style={{
                    width: `${barWidth}%`,
                    background: `linear-gradient(90deg, ${color} 0%, ${color}cc 100%)`,
                    boxShadow: percentage > 10 ? `0 0 15px ${color}40` : 'none'
                  }}
                >
                  {/* Shimmer Effect */}
                  {percentage > 10 && (
                    <div
                      className="absolute inset-0 opacity-30"
                      style={{
                        background: 'linear-gradient(90deg, transparent 0%, white 50%, transparent 100%)',
                        backgroundSize: '200% 100%',
                        animation: 'shimmer 2s infinite'
                      }}
                    />
                  )}
                </div>
              </div>

              {/* Description (shown on hover or expanded) */}
              {(showDetails || percentage > 20) && item.description && (
                <p
                  className="text-xs mt-1.5 pl-2 transition-all duration-200"
                  style={{ color: COLORS.text.muted }}
                >
                  {item.description}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Expanded Details */}
      {showDetails && (
        <div
          className="mt-4 p-4 rounded-xl border transition-all duration-300"
          style={{
            backgroundColor: `${COLORS.bg.card}`,
            borderColor: COLORS.border
          }}
        >
          <div className="space-y-3">
            {/* Monte Carlo Info */}
            <div className="flex items-center justify-between text-xs">
              <span style={{ color: COLORS.text.muted }}>
                Monte Carlo Simulation
              </span>
              <span className="font-mono" style={{ color: COLORS.primary.cyan }}>
                10,000 iterations
              </span>
            </div>

            {/* Confidence Interval */}
            <div className="flex items-center justify-between text-xs">
              <span style={{ color: COLORS.text.muted }}>
                Confidence Interval
              </span>
              <span className="font-mono" style={{ color: COLORS.primary.cyan }}>
                {confidenceInterval}%
              </span>
            </div>

            {/* Statistical Notes */}
            <div className="pt-2 border-t" style={{ borderColor: `${COLORS.border}50` }}>
              <p className="text-xs leading-relaxed" style={{ color: COLORS.text.secondary }}>
                Probabilities are derived from multi-agent consensus with confidence intervals
                calculated using bootstrap resampling of the ensemble predictions.
              </p>
            </div>

            {/* Legend */}
            <div className="pt-2 flex flex-wrap gap-3 text-xs" style={{ color: COLORS.text.muted }}>
              <div className="flex items-center gap-1.5">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: COLORS.status.success }}
                />
                <span>Positive</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: COLORS.status.warning }}
                />
                <span>Neutral</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: COLORS.status.danger }}
                />
                <span>Negative</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: COLORS.text.muted }}
                />
                <span>Uncertain</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Total Verification */}
      <div className="flex items-center justify-end text-xs pt-2">
        <span style={{ color: COLORS.text.muted }}>
          Total:
        </span>
        <span className="font-mono ml-1" style={{ color: COLORS.text.secondary }}>
          {Math.round(probabilities.reduce((sum, p) => sum + p.value, 0) * 100)}%
        </span>
      </div>
    </div>
  );
}
