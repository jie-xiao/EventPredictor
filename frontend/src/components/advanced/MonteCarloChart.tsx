import { useMemo } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { MonteCarloResult as MCResult } from '../../services/api';

interface Props {
  result: MCResult;
}

const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const trendIcon = (trend: string) => {
  const t = trend.toUpperCase();
  if (t === 'UP') return <TrendingUp className="w-4 h-4" style={{ color: COLORS.status.success }} />;
  if (t === 'DOWN') return <TrendingDown className="w-4 h-4" style={{ color: COLORS.status.danger }} />;
  return <Minus className="w-4 h-4" style={{ color: COLORS.status.warning }} />;
};

const trendColor = (trend: string) => {
  const t = trend.toUpperCase();
  if (t === 'UP') return COLORS.status.success;
  if (t === 'DOWN') return COLORS.status.danger;
  return COLORS.status.warning;
};

export default function MonteCarloChart({ result }: Props) {
  const distEntries = useMemo(() => Object.entries(result.probability_distribution), [result]);
  const maxDist = useMemo(() => Math.max(...distEntries.map(([, v]) => v), 0.01), [distEntries]);
  const sensitivityEntries = useMemo(
    () => Object.entries(result.sensitivity_analysis).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1])),
    [result]
  );
  const maxSens = useMemo(() => Math.max(...sensitivityEntries.map(([, v]) => Math.abs(v)), 0.01), [sensitivityEntries]);

  return (
    <div className="space-y-5">
      {/* Header stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard label="模拟次数" value={result.n_simulations.toLocaleString()} />
        <StatCard label="趋势" value={result.trend} icon={trendIcon(result.trend)} color={trendColor(result.trend)} />
        <StatCard label="置信度" value={`${(result.confidence * 100).toFixed(1)}%`} />
        <StatCard label="均值" value={result.mean.toFixed(3)} />
      </div>

      {/* Probability Distribution Histogram */}
      <div>
        <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>
          概率分布
        </h4>
        <div className="flex items-end gap-1 h-28 px-1">
          {distEntries.map(([label, value]) => (
            <div key={label} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full rounded-t transition-all duration-300"
                style={{
                  height: `${(value / maxDist) * 100}%`,
                  minHeight: '2px',
                  background: `linear-gradient(180deg, ${COLORS.primary.cyan}CC, ${COLORS.primary.blue}66)`,
                }}
                title={`${label}: ${(value * 100).toFixed(1)}%`}
              />
              <span className="text-[8px] truncate w-full text-center" style={{ color: COLORS.text.muted }}>
                {label.replace('very_', 'v').replace('_', '-').slice(0, 4)}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Confidence Intervals */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium" style={{ color: COLORS.text.secondary }}>
          置信区间
        </h4>
        <CIBar label="95% CI" low={result.CI_95[0]} high={result.CI_95[1]} color={COLORS.primary.cyan} />
        <CIBar label="80% CI" low={result.CI_80[0]} high={result.CI_80[1]} color={COLORS.primary.blue} />
      </div>

      {/* Sensitivity Analysis */}
      {sensitivityEntries.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>
            敏感性分析
          </h4>
          <div className="space-y-1.5">
            {sensitivityEntries.map(([name, value]) => (
              <div key={name} className="flex items-center gap-2">
                <span className="text-xs w-20 truncate" style={{ color: COLORS.text.muted }}>{name}</span>
                <div className="flex-1 h-4 rounded-full overflow-hidden" style={{ backgroundColor: `${COLORS.border}60` }}>
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${(Math.abs(value) / maxSens) * 100}%`,
                      backgroundColor: value >= 0 ? COLORS.status.success : COLORS.status.danger,
                      opacity: 0.7,
                    }}
                  />
                </div>
                <span className="text-xs w-12 text-right" style={{ color: COLORS.text.secondary }}>
                  {value.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Assumptions */}
      {result.assumptions.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-1" style={{ color: COLORS.text.secondary }}>
            关键假设
          </h4>
          <ul className="space-y-0.5">
            {result.assumptions.map((a, i) => (
              <li key={i} className="text-xs flex items-start gap-1.5" style={{ color: COLORS.text.muted }}>
                <span style={{ color: COLORS.primary.cyan }}>&bull;</span>
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, icon, color }: { label: string; value: string; icon?: React.ReactNode; color?: string }) {
  return (
    <div className="rounded-lg p-2.5" style={{ backgroundColor: `${COLORS.bg.card}80`, border: `1px solid ${COLORS.border}40` }}>
      <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>{label}</div>
      <div className="flex items-center gap-1">
        {icon}
        <span className="text-sm font-semibold" style={{ color: color || COLORS.text.primary }}>{value}</span>
      </div>
    </div>
  );
}

function CIBar({ label, low, high, color }: { label: string; low: number; high: number; color: string }) {
  const range = Math.max(high - low, 0.001);
  const leftPct = Math.max(0, (low + 1) / 2) * 100;
  const widthPct = Math.min(range / 2, 100 - leftPct) * 100;
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs w-12" style={{ color: COLORS.text.muted }}>{label}</span>
      <div className="flex-1 h-2 rounded-full relative" style={{ backgroundColor: `${COLORS.border}40` }}>
        <div
          className="absolute h-full rounded-full"
          style={{ left: `${leftPct}%`, width: `${widthPct}%`, backgroundColor: color, opacity: 0.6 }}
        />
      </div>
      <span className="text-[10px] w-20 text-right" style={{ color: COLORS.text.muted }}>
        [{low.toFixed(2)}, {high.toFixed(2)}]
      </span>
    </div>
  );
}
