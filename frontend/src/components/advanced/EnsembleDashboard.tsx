import { useMemo } from 'react';
import type { EnsembleResult as EResult } from '../../services/api';

interface Props {
  result: EResult;
}

const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const methodColor: Record<string, string> = {
  monte_carlo: COLORS.status.info,
  bayesian: COLORS.status.success,
  causal: COLORS.status.warning,
  fallback: COLORS.text.muted,
};

const methodName: Record<string, string> = {
  monte_carlo: '蒙特卡洛',
  bayesian: '贝叶斯',
  causal: '因果推理',
  fallback: '备用',
};

const trendColor = (trend: string) => {
  const t = trend.toUpperCase();
  if (t === 'UP') return COLORS.status.success;
  if (t === 'DOWN') return COLORS.status.danger;
  return COLORS.status.warning;
};

export default function EnsembleDashboard({ result }: Props) {
  const probEntries = useMemo(
    () => Object.entries(result.weighted_probabilities),
    [result.weighted_probabilities]
  );
  const maxProb = useMemo(() => Math.max(...probEntries.map(([, v]) => v), 0.01), [probEntries]);

  const { methods } = result;
  const unifiedTrend = result.unified_trend;
  const calibration = result.uncertainty_calibration;

  return (
    <div className="space-y-5">
      {/* Unified prediction header */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-lg p-2.5" style={{ backgroundColor: `${COLORS.bg.card}80`, border: `1px solid ${COLORS.border}40` }}>
          <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>统一趋势</div>
          <div className="text-sm font-bold" style={{ color: trendColor(unifiedTrend) }}>{unifiedTrend}</div>
        </div>
        <div className="rounded-lg p-2.5" style={{ backgroundColor: `${COLORS.bg.card}80`, border: `1px solid ${COLORS.border}40` }}>
          <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>统一置信度</div>
          <div className="text-sm font-semibold" style={{ color: COLORS.primary.cyan }}>
            {(result.unified_confidence * 100).toFixed(1)}%
          </div>
        </div>
        <div className="rounded-lg p-2.5" style={{ backgroundColor: `${COLORS.bg.card}80`, border: `1px solid ${COLORS.border}40` }}>
          <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>一致性</div>
          <div className="text-sm font-semibold" style={{ color: COLORS.text.primary }}>
            {(result.agreement_score * 100).toFixed(0)}%
          </div>
        </div>
        <div className="rounded-lg p-2.5" style={{ backgroundColor: `${COLORS.bg.card}80`, border: `1px solid ${COLORS.border}40` }}>
          <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>方法数</div>
          <div className="text-sm font-semibold" style={{ color: COLORS.text.primary }}>{methods.length}</div>
        </div>
      </div>

      {/* Method Consistency Matrix */}
      <div>
        <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>方法一致性</h4>
        <div className="space-y-2">
          {methods.map((m) => {
            const color = methodColor[m.method_name] || COLORS.text.muted;
            const name = methodName[m.method_name] || m.method_name;
            const agrees = m.trend === unifiedTrend;
            return (
              <div key={m.method_name} className="flex items-center gap-3 px-3 py-2 rounded-lg"
                style={{ backgroundColor: `${COLORS.bg.card}60`, border: `1px solid ${COLORS.border}30` }}>
                {/* Method badge */}
                <div className="px-2 py-0.5 rounded text-[10px] font-medium" style={{
                  backgroundColor: `${color}15`, color, border: `1px solid ${color}30`,
                }}>
                  {name}
                </div>
                {/* Trend */}
                <span className="text-xs font-medium" style={{ color: trendColor(m.trend) }}>{m.trend}</span>
                {/* Confidence bar */}
                <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ backgroundColor: `${COLORS.border}40` }}>
                  <div className="h-full rounded-full" style={{
                    width: `${m.confidence * 100}%`,
                    backgroundColor: color,
                    opacity: 0.7,
                  }} />
                </div>
                <span className="text-[10px] w-10 text-right" style={{ color: COLORS.text.secondary }}>
                  {(m.confidence * 100).toFixed(0)}%
                </span>
                {/* Agreement indicator */}
                <span className="text-[10px] px-1.5 py-0.5 rounded" style={{
                  backgroundColor: agrees ? `${COLORS.status.success}15` : `${COLORS.status.warning}15`,
                  color: agrees ? COLORS.status.success : COLORS.status.warning,
                }}>
                  {agrees ? '一致' : '分歧'}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Weighted Probabilities */}
      <div>
        <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>加权概率分布</h4>
        <div className="space-y-2">
          {probEntries.map(([trend, prob]) => (
            <div key={trend} className="flex items-center gap-2">
              <span className="text-xs w-20 font-medium" style={{ color: trendColor(trend) }}>{trend}</span>
              <div className="flex-1 h-4 rounded-full overflow-hidden" style={{ backgroundColor: `${COLORS.border}40` }}>
                <div className="h-full rounded-full transition-all duration-500" style={{
                  width: `${(prob / maxProb) * 100}%`,
                  backgroundColor: trendColor(trend),
                  opacity: 0.7,
                }} />
              </div>
              <span className="text-xs w-12 text-right" style={{ color: COLORS.text.secondary }}>
                {(prob * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Uncertainty Calibration */}
      {calibration && (
        <div>
          <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>不确定性量表</h4>
          <div className="grid grid-cols-2 gap-2">
            <div className="px-2.5 py-2 rounded-lg" style={{ backgroundColor: `${COLORS.bg.card}60`, border: `1px solid ${COLORS.border}30` }}>
              <div className="text-[9px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>方法间偏差</div>
              <div className="text-sm" style={{ color: COLORS.text.primary }}>{calibration.cross_method_std.toFixed(3)}</div>
            </div>
            <div className="px-2.5 py-2 rounded-lg" style={{ backgroundColor: `${COLORS.bg.card}60`, border: `1px solid ${COLORS.border}30` }}>
              <div className="text-[9px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>趋势熵</div>
              <div className="text-sm" style={{ color: COLORS.text.primary }}>{calibration.trend_entropy.toFixed(3)} bits</div>
            </div>
          </div>
        </div>
      )}

      {/* Recommendation */}
      {result.recommendation && (
        <div className="rounded-lg p-3" style={{ backgroundColor: `${COLORS.primary.cyan}08`, border: `1px solid ${COLORS.primary.cyan}20` }}>
          <h4 className="text-xs font-medium mb-1" style={{ color: COLORS.primary.cyan }}>综合建议</h4>
          <p className="text-xs leading-relaxed" style={{ color: COLORS.text.secondary }}>
            {result.recommendation}
          </p>
        </div>
      )}
    </div>
  );
}
