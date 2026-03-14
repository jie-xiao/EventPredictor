import {
  TrendingUp, TrendingDown, Minus, Activity, Shield, Lightbulb,
  AlertTriangle, CheckCircle2, Clock, ChevronRight
} from 'lucide-react';
import { AnalysisResult, DebateResult } from '../services/api';

interface InfoPanelProps {
  result: AnalysisResult | DebateResult | null;
  loading: boolean;
  onDetailView: () => void;
}

// ============ 设计规范色彩 ============
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
      return <TrendingUp className="w-8 h-8" style={{ color: COLORS.status.success }} />;
    case '下跌':
    case 'DOWN':
      return <TrendingDown className="w-8 h-8" style={{ color: COLORS.status.danger }} />;
    default:
      return <Minus className="w-8 h-8" style={{ color: COLORS.status.warning }} />;
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

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return COLORS.status.success;
  if (confidence >= 0.6) return COLORS.status.warning;
  return COLORS.status.danger;
};

const getRiskInfo = (result: AnalysisResult | DebateResult | null) => {
  if (!result) return { level: 'Unknown', color: COLORS.text.muted };
  const conflicts = result.cross_analysis?.conflicts?.length || 0;
  const confidence = result.overall_confidence;
  if (conflicts >= 3 || confidence < 0.5) return { level: 'High', color: COLORS.status.danger };
  if (conflicts >= 1 || confidence < 0.7) return { level: 'Medium', color: COLORS.status.warning };
  return { level: 'Low', color: COLORS.status.success };
};

export default function InfoPanel({ result, loading, onDetailView }: InfoPanelProps) {
  const risk = getRiskInfo(result);
  const prediction = result?.prediction;

  if (loading) {
    return (
      <div className="h-full flex flex-col rounded-lg overflow-hidden glass-card-enhanced">
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <div className="relative animate-breathe">
              <div className="w-20 h-20 border-4 rounded-full animate-spin"
                style={{ borderColor: `${COLORS.primary.cyan}20`, borderTopColor: COLORS.primary.cyan }} />
              <div className="absolute inset-2 w-16 h-16 border-4 rounded-full animate-spin"
                style={{ borderColor: `${COLORS.primary.blue}20`, borderBottomColor: COLORS.primary.blue, animationDirection: 'reverse' }} />
              <div className="absolute inset-4 w-12 h-12 border-2 rounded-full animate-spin"
                style={{ borderColor: `${COLORS.text.secondary}20`, borderLeftColor: COLORS.text.secondary, animationDuration: '1.5s' }} />
            </div>
            <p className="text-glow" style={{ color: COLORS.primary.cyan }}>Analyzing...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="h-full flex flex-col rounded-lg overflow-hidden glass-card-enhanced">
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-20 h-20 mx-auto mb-4 rounded-2xl flex items-center justify-center animate-float"
              style={{ backgroundColor: `${COLORS.primary.cyan}10` }}>
              <Activity className="w-10 h-10" style={{ color: COLORS.text.muted }} />
            </div>
            <p className="text-lg font-medium" style={{ color: COLORS.text.secondary }}>No analysis yet</p>
            <p className="text-sm mt-2" style={{ color: COLORS.text.muted }}>Select an event to view prediction</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col rounded-lg overflow-hidden glass-card-enhanced">
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 border-b edge-highlight" style={{
        background: `linear-gradient(90deg, ${COLORS.primary.cyan}10 0%, ${COLORS.primary.blue}10 100%)`,
        borderColor: COLORS.border
      }}>
        <h2 className="text-[16px] font-semibold flex items-center gap-2" style={{ color: COLORS.text.primary }}>
          <Activity className="w-5 h-5" style={{ color: COLORS.primary.cyan }} />
          Trend Prediction
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Trend & Confidence */}
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 rounded-2xl flex items-center justify-center transition-all duration-300"
            style={{ backgroundColor: `${getTrendColor(prediction?.trend || '')}20` }}>
            {getTrendIcon(prediction?.trend || '')}
          </div>
          <div className="flex-1">
            <p className="text-[32px] font-bold leading-none font-mono transition-all duration-300"
              style={{ color: getTrendColor(prediction?.trend || '') }}>
              {prediction?.trend || 'Analyzing...'}
            </p>
            <div className="flex items-center gap-2 mt-2">
              <span style={{ color: COLORS.text.muted }}>Confidence:</span>
              <span className="font-bold font-mono" style={{ color: getConfidenceColor(result.overall_confidence) }}>
                {Math.round(result.overall_confidence * 100)}%
              </span>
            </div>
          </div>
          {/* Circular Progress */}
          <div className="w-20 h-20 relative">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="40" cy="40" r="36" stroke={COLORS.border} strokeWidth="4" fill="none" />
              <circle
                cx="40" cy="40" r="36"
                stroke={getConfidenceColor(result.overall_confidence)}
                strokeWidth="4" fill="none" strokeLinecap="round"
                strokeDasharray={`${result.overall_confidence * 226} 226`}
                style={{ transition: 'stroke-dasharray 0.5s ease' }}
              />
            </svg>
          </div>
        </div>

        {/* Confidence Progress Bar */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span style={{ color: COLORS.text.muted }}>Confidence Level</span>
            <span className="font-mono" style={{ color: getConfidenceColor(result.overall_confidence) }}>
              {Math.round(result.overall_confidence * 100)}%
            </span>
          </div>
          <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: `${COLORS.border}80` }}>
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${result.overall_confidence * 100}%`,
                background: `linear-gradient(90deg, ${getConfidenceColor(result.overall_confidence)} 0%, ${COLORS.primary.cyan} 100%)`,
                boxShadow: `0 0 10px ${getConfidenceColor(result.overall_confidence)}40`
              }}
            />
          </div>
        </div>

        {/* Summary */}
        {prediction?.summary && (
          <div className="p-4 rounded-lg border transition-all duration-200 hover:scale-[1.02]"
            style={{ backgroundColor: `${COLORS.bg.card}80`, borderColor: `${COLORS.border}50` }}>
            <p className="text-[14px] leading-relaxed" style={{ color: COLORS.text.secondary }}>
              {prediction.summary}
            </p>
          </div>
        )}

        {/* Risk & Conflicts Grid */}
        <div className="grid grid-cols-2 gap-4">
          {/* Risk Level */}
          <div className="p-4 rounded-lg border transition-all duration-200 hover:scale-[1.02]"
            style={{ backgroundColor: `${COLORS.bg.card}80`, borderColor: `${COLORS.border}50` }}>
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-4 h-4" style={{ color: COLORS.text.muted }} />
              <span className="text-[10px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>Risk Level</span>
            </div>
            <p className="text-[24px] font-bold" style={{ color: risk.color }}>{risk.level}</p>
          </div>

          {/* Conflicts */}
          <div className="p-4 rounded-lg border transition-all duration-200 hover:scale-[1.02]"
            style={{ backgroundColor: `${COLORS.bg.card}80`, borderColor: `${COLORS.border}50` }}>
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4" style={{ color: COLORS.text.muted }} />
              <span className="text-[10px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>Conflicts</span>
            </div>
            <p className="text-[24px] font-bold" style={{ color: COLORS.text.primary }}>
              {result.cross_analysis?.conflicts?.length || 0}
            </p>
          </div>
        </div>

        {/* Key Insights */}
        {prediction?.key_insights && prediction.key_insights.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-4 h-4" style={{ color: COLORS.status.warning }} />
              <span className="text-[14px] font-medium" style={{ color: COLORS.text.secondary }}>Key Insights</span>
            </div>
            <div className="space-y-2">
              {prediction.key_insights.slice(0, 3).map((insight, idx) => (
                <div key={idx} className="flex items-start gap-3 text-[14px] p-3 rounded-lg transition-all duration-200 hover:bg-[#1E293B]/30"
                  style={{ color: COLORS.text.secondary }}>
                  <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: COLORS.primary.cyan }} />
                  <span className="flex-1">{insight}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Timeline Preview */}
        {prediction?.timeline && prediction.timeline.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Clock className="w-4 h-4" style={{ color: COLORS.status.info }} />
              <span className="text-[14px] font-medium" style={{ color: COLORS.text.secondary }}>Timeline</span>
            </div>
            <div className="space-y-3">
              {prediction.timeline.slice(0, 3).map((item, idx) => (
                <div key={idx} className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <div className="w-3 h-3 rounded-full transition-all duration-300"
                      style={{
                        backgroundColor: COLORS.status.info,
                        boxShadow: `0 0 10px ${COLORS.status.info}60`
                      }} />
                    {idx < (prediction.timeline?.length ?? 0) - 1 && (
                      <div className="w-0.5 flex-1 mt-1" style={{ backgroundColor: `${COLORS.border}50` }} />
                    )}
                  </div>
                  <div className="flex-1 pb-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-[14px]" style={{ color: COLORS.text.primary }}>{item.time}</span>
                      <span className="text-[12px] font-mono px-2 py-0.5 rounded-full" style={{
                        backgroundColor: `${COLORS.status.info}20`,
                        color: COLORS.status.info
                      }}>
                        {Math.round(item.probability * 100)}%
                      </span>
                    </div>
                    <p className="text-[14px]" style={{ color: COLORS.text.secondary }}>{item.event}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Consensus */}
        {result.cross_analysis?.consensus && result.cross_analysis.consensus.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle2 className="w-4 h-4" style={{ color: COLORS.status.success }} />
              <span className="text-[14px] font-medium" style={{ color: COLORS.text.secondary }}>Consensus</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {result.cross_analysis.consensus.slice(0, 3).map((item, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1.5 rounded-full text-[12px] border transition-all duration-200 hover:scale-105"
                  style={{
                    backgroundColor: `${COLORS.status.success}20`,
                    color: COLORS.status.success,
                    borderColor: `${COLORS.status.success}40`
                  }}
                >
                  {item.length > 30 ? `${item.substring(0, 30)}...` : item}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer - Action Button */}
      <div className="flex-shrink-0 p-4 border-t" style={{ borderColor: COLORS.border }}>
        <button
          onClick={onDetailView}
          className="w-full py-4 rounded-lg font-medium flex items-center justify-center gap-2 transition-all duration-300 hover:scale-[1.02] hover-glow-strong click-feedback flowing-light"
          style={{
            background: `linear-gradient(90deg, ${COLORS.primary.cyan} 0%, ${COLORS.primary.blue} 100%)`,
            color: '#FFFFFF',
            boxShadow: `0 4px 20px ${COLORS.primary.cyan}30`
          }}
        >
          <span>View Full Analysis</span>
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
