// frontend/src/components/CalibrationPanel.tsx
import { useState, useEffect } from 'react';
import { X, TrendingUp } from 'lucide-react';
import { fetchCalibrationStatus, fetchCalibrationCurve, CalibrationStatus, CalibrationCurvePoint } from '../services/api';

interface Props {
  onClose: () => void;
}

export default function CalibrationPanel({ onClose }: Props) {
  const [status, setStatus] = useState<CalibrationStatus | null>(null);
  const [curve, setCurve] = useState<CalibrationCurvePoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchCalibrationStatus(),
      fetchCalibrationCurve(),
    ]).then(([s, c]) => {
      setStatus(s);
      setCurve(c.curve);
    }).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="fixed inset-0 z-[3000] flex items-center justify-center bg-black/50">
        <div className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-8 w-[500px]">
          <div className="animate-pulse text-text-muted">加载校准数据...</div>
        </div>
      </div>
    );
  }

  const maxBarHeight = 120;

  return (
    <div className="fixed inset-0 z-[3000] flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="bg-[#0F172A] border border-[#1E293B] rounded-xl p-6 w-[560px] max-h-[80vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary-cyan" />
            <h2 className="text-lg font-bold text-text-primary">预测校准面板</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-[#1E293B] rounded">
            <X className="w-5 h-5 text-text-muted" />
          </button>
        </div>

        {/* Key Metrics */}
        {status && (
          <div className="grid grid-cols-2 gap-3 mb-6">
            <MetricCard label="Brier Score" value={status.brier_score.toFixed(3)} hint="0=完美 0.25=随机" />
            <MetricCard label="方向准确率" value={`${Math.round(status.directional_accuracy * 100)}%`} hint={`${status.resolved}条已判定`} />
            <MetricCard label="追踪中" value={`${status.total_predictions}`} hint={`${status.pending}条待判定`} />
            <MetricCard label="校准评级" value={status.calibration_rating} hint="" />
          </div>
        )}

        {/* Calibration Curve */}
        <h3 className="text-sm font-semibold text-text-primary mb-3">校准曲线</h3>
        <p className="text-[11px] text-text-muted mb-4">横轴=预测置信度区间 | 纵轴=实际命中率 | 对角线=完美校准</p>

        <div className="flex items-end gap-1 h-[150px] mb-2 px-2">
          {curve.length === 0 && (
            <div className="flex-1 text-center text-text-muted text-sm">数据不足，需要更多已判定的预测</div>
          )}

          {curve.map((point) => {
            const barHeight = Math.max(4, point.avg_actual * maxBarHeight);
            const predHeight = Math.max(4, point.avg_predicted * maxBarHeight);
            return (
              <div key={point.bin_low} className="flex-1 flex flex-col items-center gap-1">
                <div className="flex items-end gap-1" style={{ height: maxBarHeight }}>
                  {/* Actual (green) */}
                  <div
                    className="w-6 rounded-t bg-green-500/60"
                    style={{ height: barHeight }}
                    title={`实际: ${Math.round(point.avg_actual * 100)}%`}
                  />
                  {/* Predicted (blue, offset) */}
                  <div
                    className="w-6 rounded-t bg-blue-500/40"
                    style={{ height: predHeight }}
                    title={`预测: ${Math.round(point.avg_predicted * 100)}%`}
                  />
                </div>
                <span className="text-[9px] text-text-muted">{point.bin_low}-{point.bin_high}</span>
                <span className="text-[8px] text-text-muted">n={point.count}</span>
              </div>
            );
          })}
        </div>

        <div className="flex items-center gap-4 mt-4 text-[11px] text-text-muted">
          <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-green-500/60" /> 实际命中率</div>
          <div className="flex items-center gap-1"><div className="w-3 h-3 rounded bg-blue-500/40" /> 预测置信度</div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="bg-[#1E293B]/50 border border-[#1E293B] rounded-lg p-3">
      <div className="text-[11px] text-text-muted mb-1">{label}</div>
      <div className="text-lg font-bold text-text-primary">{value}</div>
      {hint && <div className="text-[10px] text-text-muted mt-0.5">{hint}</div>}
    </div>
  );
}
