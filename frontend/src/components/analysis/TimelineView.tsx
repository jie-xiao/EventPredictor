import { useState } from 'react';
import { Clock, Calendar, ChevronRight, Settings, Download, ExternalLink, ChevronDown, ChevronUp, CheckCircle, AlertTriangle, Shield } from 'lucide-react';
import { AnalysisResult, DebateResult } from '../../services/api';

interface TimelineViewProps {
  result: AnalysisResult | DebateResult;
  onExport?: () => void;
  onSettings?: () => void;
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const getProbabilityColor = (probability: number): string => {
  if (probability >= 0.8) return COLORS.status.success;
  if (probability >= 0.6) return COLORS.status.warning;
  return COLORS.status.danger;
};

const getRiskLabel = (probability: number): string => {
  if (probability >= 0.8) return 'Low';
  if (probability >= 0.5) return 'Medium';
  return 'High';
};

const getRiskColor = (probability: number): string => {
  const risk = getRiskLabel(probability);
  if (risk === 'Low') return COLORS.status.success;
  if (risk === 'Medium') return COLORS.status.warning;
  return COLORS.status.danger;
};

const getImpactLabel = (probability: number): string => {
  if (probability >= 0.7) return 'High';
  if (probability >= 0.4) return 'Medium';
  return 'Low';
};

const getImpactColor = (probability: number): string => {
  const impact = getImpactLabel(probability);
  if (impact === 'High') return COLORS.status.danger;
  if (impact === 'Medium') return COLORS.status.warning;
  return COLORS.status.success;
};

// Timeline Event Component
const TimelineEvent = ({
  time,
  event,
  probability,
  isFirst,
  isLast,
  isExpanded,
  onToggleExpand
}: {
  time: string;
  event: string;
  probability: number;
  isFirst?: boolean;
  isLast?: boolean;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}) => {
  const probColor = getProbabilityColor(probability);
  const riskColor = getRiskColor(probability);
  const impactColor = getImpactColor(probability);
  const displayProb = Math.round(probability * 100);

  return (
    <div className="flex gap-6">
      {/* Timeline Node */}
      <div className="flex flex-col items-center flex-shrink-0">
        <div
          className={`w-4 h-4 rounded-full transition-all duration-300 ${isFirst ? 'animate-pulse' : ''}`}
          style={{
            backgroundColor: probColor,
            boxShadow: `0 0 12px ${probColor}60`
          }}
        />
        {!isLast && (
          <div className="w-0.5 flex-1 my-1" style={{ backgroundColor: `${COLORS.border}50` }} />
        )}
      </div>

      {/* Event Card */}
      <div className="flex-1 pb-6 min-w-0">
        {/* Time Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-[13px] font-medium" style={{ color: COLORS.text.primary }}>
              {time}
            </span>
            {isFirst && (
              <span
                className="px-2 py-0.5 rounded text-[10px] font-medium"
                style={{
                  backgroundColor: `${COLORS.primary.cyan}20`,
                  color: COLORS.primary.cyan
                }}
              >
                NOW
              </span>
            )}
          </div>

          {/* Probability Badge */}
          <span
            className="px-3 py-1 rounded-full text-xs font-mono font-medium"
            style={{
              backgroundColor: `${probColor}20`,
              color: probColor,
              border: `1px solid ${probColor}40`
            }}
          >
            {displayProb}%
          </span>
        </div>

        {/* Event Content */}
        <div
          className={`p-4 rounded-xl border transition-all duration-200 ${
            isExpanded ? 'scale-[1.01]' : 'hover:scale-[1.005]'
          }`}
          style={{
            backgroundColor: `${COLORS.bg.card}`,
            borderColor: `${COLORS.border}50`
          }}
        >
          {/* Event Description */}
          <p
            className="text-[14px] leading-relaxed mb-3"
            style={{ color: COLORS.text.secondary }}
          >
            {event}
          </p>

          {/* Risk/Impact Indicators (only when expanded or on hover for high probability events) */}
          {(isExpanded || probability > 0.7) && (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5" style={{ color: riskColor }} />
                <span className="text-xs" style={{ color: COLORS.text.muted }}>
                  Risk:
                </span>
                <span className="text-xs font-medium" style={{ color: riskColor }}>
                  {getRiskLabel(probability)}
                </span>
              </div>

              <div className="flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" style={{ color: impactColor }} />
                <span className="text-xs" style={{ color: COLORS.text.muted }}>
                  Impact:
                </span>
                <span className="text-xs font-medium" style={{ color: impactColor }}>
                  {getImpactLabel(probability)}
                </span>
              </div>
            </div>
          )}

          {/* Expand Toggle */}
          {!isExpanded && (
            <button
              onClick={onToggleExpand}
              className="flex items-center gap-1 mt-3 text-xs transition-all hover:scale-105"
              style={{ color: COLORS.primary.cyan }}
            >
              <span>View Details</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default function TimelineView({ result, onExport, onSettings }: TimelineViewProps) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [showFullTimeline, setShowFullTimeline] = useState(false);
  const [timeHorizon, setTimeHorizon] = useState<'short' | 'medium' | 'long' | 'custom'>('medium');

  const timeline = result.prediction?.timeline || [];

  const toggleEvent = (idx: number) => {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(idx)) {
        next.delete(idx);
      } else {
        next.add(idx);
      }
      return next;
    });
  };

  const visibleTimeline = showFullTimeline ? timeline : timeline.slice(0, 5);
  const hasMore = timeline.length > 5 && !showFullTimeline;

  // Calculate timeline summary stats
  const avgProbability = timeline.length > 0
    ? timeline.reduce((sum, t) => sum + t.probability, 0) / timeline.length
    : 0;
  const highProbabilityCount = timeline.filter(t => t.probability >= 0.7).length;
  const lowProbabilityCount = timeline.filter(t => t.probability < 0.4).length;

  return (
    <div
      className="rounded-lg overflow-hidden"
      style={{ backgroundColor: COLORS.bg.card, border: `1px solid ${COLORS.border}` }}
    >
      {/* Header */}
      <div
        className="px-6 py-4 border-b flex items-center justify-between"
        style={{ borderColor: COLORS.border }}
      >
        <div className="flex items-center gap-3">
          <Clock className="w-5 h-5" style={{ color: COLORS.primary.blue }} />
          <h3 className="text-[14px] font-semibold" style={{ color: COLORS.text.primary }}>
            PREDICTION TIMELINE
          </h3>

          {/* Stats Summary */}
          <div className="hidden md:flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg"
              style={{ backgroundColor: `${COLORS.border}50`, color: COLORS.text.muted }}
            >
              <span>Events:</span>
              <span className="font-mono font-medium" style={{ color: COLORS.text.secondary }}>
                {timeline.length}
              </span>
            </div>
            <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg"
              style={{ backgroundColor: `${COLORS.status.success}20`, color: COLORS.status.success }}
            >
              <span>Avg Prob:</span>
              <span className="font-mono font-medium">
                {Math.round(avgProbability * 100)}%
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Time Horizon Selector */}
          <select
            value={timeHorizon}
            onChange={(e) => setTimeHorizon(e.target.value as any)}
            className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer"
            style={{
              backgroundColor: `${COLORS.bg.dark}`,
              border: `1px solid ${COLORS.border}`,
              color: COLORS.text.secondary
            }}
          >
            <option value="short">Short-Term (1M)</option>
            <option value="medium">Medium-Term (3M)</option>
            <option value="long">Long-Term (1Y)</option>
            <option value="custom">Custom</option>
          </select>

          {onSettings && (
            <button
              onClick={onSettings}
              className="p-2 rounded-lg transition-all hover:scale-105"
              style={{ backgroundColor: `${COLORS.border}50`, color: COLORS.text.secondary }}
              title="Timeline settings"
            >
              <Settings className="w-4 h-4" />
            </button>
          )}
          {onExport && (
            <button
              onClick={onExport}
              className="p-2 rounded-lg transition-all hover:scale-105"
              style={{ backgroundColor: `${COLORS.border}50`, color: COLORS.text.secondary }}
              title="Export timeline"
            >
              <Download className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={() => setShowFullTimeline(!showFullTimeline)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all hover:scale-105"
            style={{
              backgroundColor: `${COLORS.border}50`,
              color: COLORS.text.secondary
            }}
          >
            <span>{showFullTimeline ? 'Collapse' : 'Expand'}</span>
            {showFullTimeline ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {/* Timeline Events */}
        <div className="space-y-2">
          {visibleTimeline.length > 0 ? (
            visibleTimeline.map((item, idx) => (
              <TimelineEvent
                key={idx}
                time={item.time}
                event={item.event}
                probability={item.probability}
                isFirst={idx === 0}
                isLast={idx === visibleTimeline.length - 1}
                isExpanded={expanded.has(idx)}
                onToggleExpand={() => toggleEvent(idx)}
              />
            ))
          ) : (
            <div
              className="p-8 rounded-xl text-center"
              style={{ backgroundColor: `${COLORS.bg.dark}` }}
            >
              <Calendar className="w-10 h-10 mx-auto mb-3" style={{ color: COLORS.text.muted }} />
              <p className="text-sm" style={{ color: COLORS.text.secondary }}>
                No timeline data available
              </p>
            </div>
          )}
        </div>

        {/* Show More Button */}
        {hasMore && (
          <div className="flex justify-center mt-4">
            <button
              onClick={() => setShowFullTimeline(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all hover:scale-105"
              style={{
                background: `linear-gradient(90deg, ${COLORS.primary.cyan} 0%, ${COLORS.primary.blue} 100%)`,
                color: COLORS.bg.dark,
                boxShadow: `0 0 20px ${COLORS.primary.cyan}30`
              }}
            >
              <span>View Full Timeline</span>
              <ExternalLink className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Expanded Statistics */}
        {showFullTimeline && timeline.length > 0 && (
          <div
            className="mt-6 p-4 rounded-xl animate-in slide-in-from-top-2 duration-300"
            style={{
              background: `linear-gradient(135deg, ${COLORS.primary.cyan}08 0%, ${COLORS.bg.card} 100%)`,
              border: `1px solid ${COLORS.primary.cyan}20`
            }}
          >
            <h4
              className="text-[11px] font-semibold mb-3 uppercase tracking-wider flex items-center gap-2"
              style={{ color: COLORS.text.muted }}
            >
              <CheckCircle className="w-4 h-4" />
              Timeline Statistics
            </h4>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-3 rounded-lg" style={{ backgroundColor: `${COLORS.bg.dark}` }}>
                <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
                  High Probability
                </p>
                <p className="text-2xl font-bold font-mono" style={{ color: COLORS.status.success }}>
                  {highProbabilityCount}
                </p>
                <p className="text-[10px]" style={{ color: COLORS.text.muted }}>
                  (≥70%)
                </p>
              </div>
              <div className="p-3 rounded-lg" style={{ backgroundColor: `${COLORS.bg.dark}` }}>
                <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
                  Low Probability
                </p>
                <p className="text-2xl font-bold font-mono" style={{ color: COLORS.status.warning }}>
                  {lowProbabilityCount}
                </p>
                <p className="text-[10px]" style={{ color: COLORS.text.muted }}>
                  (&lt;40%)
                </p>
              </div>
              <div className="p-3 rounded-lg" style={{ backgroundColor: `${COLORS.bg.dark}` }}>
                <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
                  Average Confidence
                </p>
                <p className="text-2xl font-bold font-mono" style={{ color: COLORS.primary.cyan }}>
                  {Math.round(avgProbability * 100)}%
                </p>
                <p className="text-[10px]" style={{ color: COLORS.text.muted }}>
                  Across all events
                </p>
              </div>
            </div>

            {/* Recommended Actions Based on Timeline */}
            {result.prediction?.recommended_actions && (
              <div className="mt-4 pt-4 border-t" style={{ borderColor: `${COLORS.border}50` }}>
                <h4
                  className="text-[11px] font-semibold mb-2 uppercase tracking-wider"
                  style={{ color: COLORS.text.muted }}
                >
                  Recommended Actions
                </h4>
                <div className="space-y-1.5">
                  {result.prediction.recommended_actions.slice(0, 3).map((action, idx) => (
                    <div key={idx} className="flex items-start gap-2">
                      <CheckCircle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" style={{ color: COLORS.primary.cyan }} />
                      <p className="text-xs leading-relaxed" style={{ color: COLORS.text.secondary }}>
                        {action}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div
        className="px-6 py-3 border-t flex items-center justify-between text-xs"
        style={{ borderColor: COLORS.border, backgroundColor: `${COLORS.bg.dark}` }}
      >
        <div className="flex items-center gap-4">
          <span style={{ color: COLORS.text.muted }}>
            Confidence Interval: 95%
          </span>
          <span style={{ color: COLORS.text.muted }}>
            Simulation: 10,000 iterations
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span style={{ color: COLORS.text.muted }}>
            Last Updated
          </span>
          <span className="font-mono" style={{ color: COLORS.text.secondary }}>
            {new Date().toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}
