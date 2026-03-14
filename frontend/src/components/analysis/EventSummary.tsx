import { useState } from 'react';
import { MapPin, Clock, BarChart3, Users, AlertTriangle, Activity, ChevronRight } from 'lucide-react';
import { WorldMonitorEvent, AnalysisResult, DebateResult } from '../../services/api';

interface EventSummaryProps {
  event: WorldMonitorEvent;
  result: AnalysisResult | DebateResult;
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const CATEGORY_CONFIG: Record<string, { color: string; emoji: string; label: string }> = {
  military: { color: '#EF4444', emoji: '🎯', label: 'Military' },
  conflict: { color: '#EF4444', emoji: '⚔️', label: 'Conflict' },
  economy: { color: '#F59E0B', emoji: '📈', label: 'Economy' },
  trade: { color: '#F59E0B', emoji: '🚢', label: 'Trade' },
  politics: { color: '#8B5CF6', emoji: '🏛️', label: 'Politics' },
  disaster: { color: '#EF4444', emoji: '🔥', label: 'Disaster' },
  cyber: { color: '#06B6D4', emoji: '💻', label: 'Cyber' },
  technology: { color: '#3B82F6', emoji: '🔬', label: 'Technology' },
  'Monetary Policy': { color: '#F59E0B', emoji: '💰', label: 'Monetary' },
  Geopolitical: { color: '#8B5CF6', emoji: '🌐', label: 'Geopolitical' },
  Economic: { color: '#F59E0B', emoji: '📊', label: 'Economic' },
  Technology: { color: '#3B82F6', emoji: '🔬', label: 'Technology' },
  Trade: { color: '#F59E0B', emoji: '🚢', label: 'Trade' },
  Social: { color: '#22C55E', emoji: '👥', label: 'Social' },
  other: { color: '#22C55E', emoji: '📌', label: 'Other' },
};

const getSeverityColor = (severity: number): string => {
  if (severity >= 4) return COLORS.status.danger;
  if (severity >= 3) return COLORS.status.warning;
  return COLORS.status.success;
};

const getRiskLevel = (result: AnalysisResult | DebateResult): { level: string; color: string } => {
  const conflicts = result.cross_analysis?.conflicts?.length || 0;
  const confidence = result.overall_confidence;

  if (conflicts >= 3 || confidence < 0.5) {
    return { level: 'HIGH', color: COLORS.status.danger };
  }
  if (conflicts >= 1 || confidence < 0.7) {
    return { level: 'MEDIUM', color: COLORS.status.warning };
  }
  return { level: 'LOW', color: COLORS.status.success };
};

const getConsensusLevel = (result: AnalysisResult | DebateResult): { level: string; color: string } => {
  const consensusCount = result.cross_analysis?.consensus?.length || 0;
  const conflictsCount = result.cross_analysis?.conflicts?.length || 0;
  const ratio = consensusCount / (consensusCount + conflictsCount);

  if (ratio >= 0.7) {
    return { level: 'HIGH', color: COLORS.status.success };
  }
  if (ratio >= 0.4) {
    return { level: 'MEDIUM', color: COLORS.status.warning };
  }
  return { level: 'LOW', color: COLORS.status.danger };
};

const getDurationLabel = (prediction?: AnalysisResult['prediction']): string => {
  if (!prediction) return '--';
  // Fallback based on timeline
  if (prediction.timeline?.[0]?.time?.includes('W')) return 'Short-Term';
  if (prediction.timeline?.[0]?.time?.includes('M')) return 'Medium-Term';
  if (prediction.timeline?.[0]?.time?.includes('Y')) return 'Long-Term';
  return 'Medium-Term';
};

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor(diff / (1000 * 60));
  if (hours >= 24) return `${Math.floor(hours / 24)} days ago`;
  if (hours >= 1) return `${hours} hours ago`;
  return `${minutes} minutes ago`;
};

// Quick Metrics Grid Component
const QuickMetricsGrid = ({ result }: { result: AnalysisResult | DebateResult }) => {
  const risk = getRiskLevel(result);
  const consensus = getConsensusLevel(result);
  const duration = getDurationLabel(result.prediction);
  const impact = result.prediction?.summary?.toLowerCase().includes('global') ? 'Global' : 'Regional';

  const metrics = [
    { label: 'Risk', value: risk.level, color: risk.color, icon: AlertTriangle },
    { label: 'Consensus', value: consensus.level, color: consensus.color, icon: Users },
    { label: 'Duration', value: duration, color: COLORS.text.primary, icon: Clock },
    { label: 'Impact', value: impact, color: COLORS.text.primary, icon: BarChart3 }
  ];

  return (
    <div
      className="p-4 rounded-xl"
      style={{ backgroundColor: `${COLORS.bg.card}`, border: `1px solid ${COLORS.border}` }}
    >
      <h4
        className="text-[11px] font-semibold mb-3 uppercase tracking-wider"
        style={{ color: COLORS.text.muted }}
      >
        Quick Metrics
      </h4>
      <div className="grid grid-cols-2 gap-3">
        {metrics.map((metric, idx) => (
          <div
            key={idx}
            className="flex items-center gap-2 p-3 rounded-lg transition-all duration-200 hover:scale-105"
            style={{ backgroundColor: `${COLORS.bg.dark}` }}
          >
            <metric.icon className="w-4 h-4 flex-shrink-0" style={{ color: COLORS.text.muted }} />
            <div className="min-w-0 flex-1">
              <p className="text-[10px] uppercase tracking-wider truncate" style={{ color: COLORS.text.muted }}>
                {metric.label}
              </p>
              <p className="text-[13px] font-bold truncate" style={{ color: metric.color }}>
                {metric.value}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Timeline Mini-View Component
const TimelineMiniView = ({ result }: { result: AnalysisResult | DebateResult }) => {
  const timeline = result.prediction?.timeline || [];

  if (timeline.length === 0) {
    return (
      <div
        className="p-4 rounded-xl text-center"
        style={{ backgroundColor: `${COLORS.bg.card}`, border: `1px solid ${COLORS.border}` }}
      >
        <Clock className="w-8 h-8 mx-auto mb-2" style={{ color: COLORS.text.muted }} />
        <p className="text-xs" style={{ color: COLORS.text.secondary }}>No timeline data</p>
      </div>
    );
  }

  return (
    <div
      className="p-4 rounded-xl"
      style={{ backgroundColor: `${COLORS.bg.card}`, border: `1px solid ${COLORS.border}` }}
    >
      <div className="flex items-center justify-between mb-3">
        <h4
          className="text-[11px] font-semibold uppercase tracking-wider flex items-center gap-2"
          style={{ color: COLORS.text.muted }}
        >
          <Clock className="w-3.5 h-3.5" />
          Timeline Preview
        </h4>
        <button
          className="text-[10px] flex items-center gap-1 px-2 py-1 rounded transition-all hover:bg-[#00E5FF]10"
          style={{ color: COLORS.primary.cyan }}
        >
          View Full
          <ChevronRight className="w-3 h-3" />
        </button>
      </div>

      {/* Timeline Bar */}
      <div className="relative mb-4">
        <div
          className="h-1 rounded-full relative"
          style={{ backgroundColor: `${COLORS.border}50` }}
        >
          <div
            className="h-full rounded-full"
            style={{
              background: `linear-gradient(90deg, ${COLORS.primary.cyan} 0%, ${COLORS.primary.blue} 100%)`,
              width: '80%'
            }}
          />
        </div>
        {/* Timeline Nodes */}
        <div className="absolute top-0 left-0 w-full flex justify-between">
          {timeline.slice(0, 4).map((_, idx) => (
            <div
              key={idx}
              className="w-2 h-2 rounded-full transform -translate-y-0.5"
              style={{
                backgroundColor: COLORS.primary.cyan,
                boxShadow: `0 0 8px ${COLORS.primary.cyan}60`
              }}
            />
          ))}
        </div>
      </div>

      {/* Time Labels */}
      <div className="flex justify-between text-[10px] mb-3" style={{ color: COLORS.text.muted }}>
        {timeline.slice(0, 4).map((item, idx) => (
          <span key={idx} className="font-mono">{item.time}</span>
        ))}
      </div>

      {/* Timeline Items */}
      <div className="space-y-2">
        {timeline.slice(0, 3).map((item, idx) => (
          <div
            key={idx}
            className="flex items-start gap-3 p-2.5 rounded-lg transition-all duration-200 hover:bg-[#00E5FF]05"
          >
            <div
              className="w-1.5 h-1.5 rounded-full mt-1.5 flex-shrink-0"
              style={{ backgroundColor: COLORS.primary.cyan }}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-0.5">
                <span
                  className="text-[11px] font-medium truncate"
                  style={{ color: COLORS.text.primary }}
                >
                  {item.time}
                </span>
                <span
                  className="text-[10px] font-mono px-1.5 py-0.5 rounded"
                  style={{
                    backgroundColor: `${COLORS.primary.cyan}20`,
                    color: COLORS.primary.cyan
                  }}
                >
                  {Math.round(item.probability * 100)}%
                </span>
              </div>
              <p className="text-[12px] line-clamp-2" style={{ color: COLORS.text.muted }}>
                {item.event}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function EventSummary({ event, result }: EventSummaryProps) {
  const config = CATEGORY_CONFIG[event.category] || CATEGORY_CONFIG.other;
  const severityColor = getSeverityColor(event.severity || 3);
  const risk = getRiskLevel(result);
  const consensus = getConsensusLevel(result);

  const [expanded, setExpanded] = useState(false);

  return (
    <div
      className="h-full flex flex-col rounded-lg overflow-auto"
      style={{ backgroundColor: COLORS.bg.card, border: `1px solid ${COLORS.border}` }}
    >
      {/* Event Card */}
      <div
        className="p-5 border-l-4"
        style={{
          borderColor: COLORS.border,
          borderLeftColor: config.color
        }}
      >
        {/* Event Header */}
        <div className="flex items-start gap-3 mb-3">
          {/* Category Icon */}
          <div
            className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ backgroundColor: `${config.color}20` }}
          >
            <span className="text-xl">{config.emoji}</span>
          </div>

          {/* Title */}
          <div className="flex-1 min-w-0">
            <h2
              className="text-[16px] font-bold leading-tight line-clamp-2"
              style={{ color: COLORS.text.primary }}
            >
              {event.title}
            </h2>
            <p
              className="text-[11px] mt-1"
              style={{ color: COLORS.text.muted }}
            >
              {config.label} · {event.location?.country || 'Unknown'}
            </p>
          </div>
        </div>

        {/* Stats Row */}
        <div
          className="grid grid-cols-5 gap-2 p-3 rounded-lg mb-3"
          style={{ backgroundColor: `${COLORS.bg.dark}` }}
        >
          <div className="text-center">
            <p className="text-[9px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
              Cat.
            </p>
            <p className="text-xs font-medium" style={{ color: config.color }}>
              {config.label.substring(0, 6)}
            </p>
          </div>
          <div className="text-center">
            <p className="text-[9px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
              Severity
            </p>
            <p className="text-xs font-bold" style={{ color: severityColor }}>
              {event.severity}/5
            </p>
          </div>
          <div className="text-center">
            <p className="text-[9px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
              Risk
            </p>
            <p className="text-xs font-bold" style={{ color: risk.color }}>
              {risk.level}
            </p>
          </div>
          <div className="text-center">
            <p className="text-[9px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
              Roles
            </p>
            <p className="text-xs font-bold" style={{ color: COLORS.primary.cyan }}>
              {result.analyses.length}
            </p>
          </div>
          <div className="text-center">
            <p className="text-[9px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
              Conflict
            </p>
            <p className="text-xs font-bold" style={{ color: COLORS.status.warning }}>
              {result.cross_analysis?.conflicts?.length || 0}
            </p>
          </div>
        </div>

        {/* Description */}
        <div className="mb-3">
          <p
            className="text-[13px] leading-relaxed"
            style={{
              color: COLORS.text.secondary,
              display: expanded ? 'block' : '-webkit-box',
              WebkitLineClamp: expanded ? 'unset' : 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}
          >
            {event.description}
          </p>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 mt-2 text-xs transition-all hover:scale-105"
            style={{ color: COLORS.primary.cyan }}
          >
            <span>{expanded ? 'Show Less' : 'Read More'}</span>
            <ChevronRight
              className={`w-3.5 h-3.5 transition-transform ${expanded ? 'rotate-90' : ''}`}
            />
          </button>
        </div>

        {/* Meta Info */}
        <div
          className="flex items-center justify-between p-3 rounded-lg text-xs"
          style={{ backgroundColor: `${COLORS.bg.dark}`, color: COLORS.text.muted }}
        >
          <span className="flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5" />
            {event.location?.country || 'Unknown'}
            {event.location?.region && ` · ${event.location.region}`}
          </span>
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            {formatTime(event.timestamp)}
          </span>
          <span className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5" />
            {result.overall_confidence >= 0.7 ? 'High Impact' : 'Medium Impact'}
          </span>
        </div>
      </div>

      {/* Quick Metrics */}
      <div className="px-5 py-4">
        <QuickMetricsGrid result={result} />
      </div>

      {/* Confidence Overview */}
      <div className="px-5 pb-4">
        <div
          className="p-4 rounded-xl flex items-center gap-4"
          style={{
            background: `linear-gradient(135deg, ${COLORS.primary.cyan}10 0%, ${COLORS.bg.card} 100%)`,
            border: `1px solid ${COLORS.primary.cyan}30`
          }}
        >
          {/* Circular Progress */}
          <div className="relative w-16 h-16 flex-shrink-0">
            <svg className="w-full h-full transform -rotate-90">
              <circle cx="32" cy="32" r="28" stroke={COLORS.border} strokeWidth="3" fill="none" />
              <circle
                cx="32" cy="32" r="28"
                stroke={COLORS.primary.cyan}
                strokeWidth="3" fill="none" strokeLinecap="round"
                strokeDasharray={`${result.overall_confidence * 176} 176`}
                style={{ filter: `drop-shadow(0 0 8px ${COLORS.primary.cyan}40)` }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span
                className="text-lg font-bold font-mono"
                style={{ color: COLORS.primary.cyan }}
              >
                {Math.round(result.overall_confidence * 100)}%
              </span>
            </div>
          </div>

          {/* Confidence Info */}
          <div className="flex-1">
            <h4
              className="text-[11px] font-semibold uppercase tracking-wider mb-1"
              style={{ color: COLORS.text.muted }}
            >
              Overall Confidence
            </h4>
            <p
              className="text-[14px] font-medium"
              style={{ color: COLORS.text.primary }}
            >
              {result.overall_confidence >= 0.8 ? 'High Certainty' :
               result.overall_confidence >= 0.6 ? 'Moderate Confidence' :
               'Low Confidence'}
            </p>
            <p className="text-[11px] mt-1" style={{ color: COLORS.text.muted }}>
              Based on {result.analyses.length} role analyses with {consensus.level} consensus
            </p>
          </div>
        </div>
      </div>

      {/* Timeline Mini-View */}
      <div className="px-5 pb-5">
        <TimelineMiniView result={result} />
      </div>
    </div>
  );
}
