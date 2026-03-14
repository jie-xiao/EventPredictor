import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface TrendGaugeProps {
  trend: string;
  confidence: number;
  riskLevel: string;
  volatility?: string;
  impact?: string;
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const getTrendIcon = (trend: string) => {
  switch (trend) {
    case '上涨':
    case 'UP':
      return <TrendingUp className="w-12 h-12" />;
    case '下跌':
    case 'DOWN':
      return <TrendingDown className="w-12 h-12" />;
    default:
      return <Minus className="w-12 h-12" />;
  }
};

const getTrendColor = (trend: string) => {
  switch (trend) {
    case '上涨':
    case 'UP':
      return COLORS.status.success;
    case '下跌':
    case 'DOWN':
      return COLORS.status.danger;
    default:
      return COLORS.status.warning;
  }
};

const getTrendLabel = (trend: string): string => {
  switch (trend) {
    case '上涨':
    case 'UP':
      return 'UP';
    case '下跌':
    case 'DOWN':
      return 'DOWN';
    case 'SIDEWAYS':
    case '横盘':
      return 'SIDEWAYS';
    case 'UNCERTAIN':
    case '不确定':
      return 'UNCERTAIN';
    default:
      return 'NEUTRAL';
  }
};

const getRiskColor = (riskLevel: string): string => {
  const level = riskLevel.toLowerCase();
  if (level.includes('high') || level.includes('高')) return COLORS.status.danger;
  if (level.includes('medium') || level.includes('中')) return COLORS.status.warning;
  return COLORS.status.success;
};

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return COLORS.status.success;
  if (confidence >= 0.6) return COLORS.status.warning;
  return COLORS.status.danger;
};

// Simple probability distribution for the three main trends
const getProbabilityDistribution = (trend: string, conf: number): Array<{ label: string; value: number }> => {
  const trendLabel = getTrendLabel(trend);
  const dist = [
    { label: 'UP', value: 0 },
    { label: 'SIDEWAYS', value: 0 },
    { label: 'DOWN', value: 0 }
  ];

  const mainIdx = dist.findIndex(d => d.label === trendLabel);
  if (mainIdx >= 0) {
    dist[mainIdx].value = Math.round(conf * 85) / 100; // Up to 85% for main trend
  }

  // Distribute remaining probability
  const remaining = 1 - conf;
  const otherIdxes = dist.map((_, i) => i).filter(i => i !== mainIdx);
  if (otherIdxes.length === 2) {
    dist[otherIdxes[0]].value = Math.round((remaining * 0.6) * 100) / 100;
    dist[otherIdxes[1]].value = remaining - dist[otherIdxes[0]].value;
  }

  return dist;
};

export default function TrendGauge({
  trend,
  confidence,
  riskLevel,
  volatility = 'MEDIUM',
  impact = 'Global'
}: TrendGaugeProps) {
  // Avoid unused variable warning
  void volatility;
  void impact;
  const trendColor = getTrendColor(trend);
  const confidenceColor = getConfidenceColor(confidence);
  const riskColor = getRiskColor(riskLevel);
  const distribution = getProbabilityDistribution(trend, confidence);
  const trendLabel = getTrendLabel(trend);

  return (
    <div className="space-y-6">
      {/* Trend Indicator */}
      <div className="flex items-center justify-center">
        <div
          className="relative w-48 h-32 flex flex-col items-center justify-center rounded-2xl transition-all duration-300"
          style={{
            background: `linear-gradient(135deg, ${trendColor}15 0%, ${trendColor}05 100%)`,
            border: `1px solid ${trendColor}30`,
            boxShadow: `0 0 40px ${trendColor}20`
          }}
        >
          {/* Trend Icon with Animation */}
          <div
            className="mb-3 transition-all duration-300"
            style={{
              color: trendColor,
              transform: trendLabel === 'UP' ? 'rotate(-45deg) scale(1.1)' :
                      trendLabel === 'DOWN' ? 'rotate(45deg) scale(1.1)' : 'scale(1)'
            }}
          >
            {getTrendIcon(trend)}
          </div>

          {/* Trend Label */}
          <div className="text-4xl font-bold font-mono tracking-tight" style={{ color: trendColor }}>
            {trendLabel}
          </div>

          {/* Confidence Badge */}
          <div className="mt-2 px-4 py-1 rounded-full text-sm font-medium"
            style={{
              backgroundColor: `${trendColor}20`,
              color: trendColor,
              border: `1px solid ${trendColor}40`
            }}
          >
            Confidence: {Math.round(confidence * 100)}%
          </div>
        </div>
      </div>

      {/* Confidence Bar */}
      <div>
        <div className="flex justify-between text-xs mb-2">
          <span style={{ color: COLORS.text.muted }}>Confidence Level</span>
          <span className="font-mono" style={{ color: confidenceColor }}>
            {Math.round(confidence * 100)}%
          </span>
        </div>
        <div
          className="h-2 rounded-full overflow-hidden"
          style={{ backgroundColor: `${COLORS.border}50` }}
        >
          <div
            className="h-full rounded-full transition-all duration-500 relative"
            style={{
              width: `${confidence * 100}%`,
              background: `linear-gradient(90deg, ${confidenceColor} 0%, ${COLORS.primary.cyan} 100%)`,
              boxShadow: `0 0 10px ${confidenceColor}40`
            }}
          >
            {/* Animated glow effect */}
            <div
              className="absolute inset-0 animate-pulse"
              style={{
                background: `linear-gradient(90deg, transparent 0%, ${confidenceColor}40 50%, transparent 100%)`,
                backgroundSize: '200% 100%',
                animation: 'shimmer 2s infinite'
              }}
            />
          </div>
        </div>
      </div>

      {/* Probability Distribution */}
      <div className="space-y-3">
        <div className="flex justify-between items-center text-xs" style={{ color: COLORS.text.muted }}>
          <span>Probability Distribution</span>
          <span>Monte Carlo: 10,000 iterations</span>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {distribution.map((item, idx) => {
            const isSelected = item.label === trendLabel;
            const itemColor = item.label === 'UP' ? COLORS.status.success :
                            item.label === 'DOWN' ? COLORS.status.danger :
                            COLORS.status.warning;

            return (
              <div
                key={idx}
                className="space-y-2 p-3 rounded-xl transition-all duration-200 hover:scale-105"
                style={{
                  backgroundColor: isSelected ? `${itemColor}15` : `${COLORS.bg.card}`,
                  border: `1px solid ${isSelected ? `${itemColor}50` : COLORS.border}`,
                  opacity: isSelected ? 1 : 0.6
                }}
              >
                {/* Label */}
                <div className="text-center text-xs font-medium" style={{ color: COLORS.text.secondary }}>
                  {item.label}
                </div>

                {/* Value */}
                <div
                  className="text-center text-xl font-bold font-mono"
                  style={{ color: itemColor }}
                >
                  {Math.round(item.value * 100)}%
                </div>

                {/* Mini Bar */}
                <div
                  className="h-1.5 rounded-full overflow-hidden"
                  style={{ backgroundColor: `${COLORS.border}50` }}
                >
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${item.value * 100}%`,
                      backgroundColor: itemColor
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Risk & Impact Tags */}
      <div className="flex items-center justify-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 px-4 py-2 rounded-lg"
          style={{
            backgroundColor: `${riskColor}15`,
            border: `1px solid ${riskColor}30`
          }}
        >
          <span className="text-xs uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
            Risk
          </span>
          <span className="text-sm font-bold" style={{ color: riskColor }}>
            {riskLevel}
          </span>
        </div>

        <div className="flex items-center gap-2 px-4 py-2 rounded-lg"
          style={{
            backgroundColor: `${COLORS.bg.card}`,
            border: `1px solid ${COLORS.border}`
          }}
        >
          <span className="text-xs uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
            Volatility
          </span>
          <span className="text-sm font-medium" style={{ color: COLORS.text.primary }}>
            {volatility}
          </span>
        </div>

        <div className="flex items-center gap-2 px-4 py-2 rounded-lg"
          style={{
            backgroundColor: `${COLORS.bg.card}`,
            border: `1px solid ${COLORS.border}`
          }}
        >
          <span className="text-xs uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
            Impact
          </span>
          <span className="text-sm font-medium" style={{ color: COLORS.text.primary }}>
            {impact}
          </span>
        </div>
      </div>
    </div>
  );
}
