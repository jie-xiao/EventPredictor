import { useState } from 'react';
import { ChevronDown, ChevronUp, Lightbulb, ChevronRight, ExternalLink } from 'lucide-react';

interface InsightItem {
  text: string;
  confidence?: number;
  secondary?: string[];
}

interface KeyInsightsProps {
  insights?: InsightItem[];
  showAll?: boolean;
  onToggleShowAll?: () => void;
  onViewAllInsights?: () => void;
  maxVisible?: number;
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const getConfidenceColor = (confidence?: number): string => {
  if (!confidence) return COLORS.text.muted;
  if (confidence >= 0.8) return COLORS.status.success;
  if (confidence >= 0.6) return COLORS.status.warning;
  return COLORS.status.danger;
};

export default function KeyInsights({
  insights = [],
  showAll = false,
  onToggleShowAll,
  onViewAllInsights,
  maxVisible = 3
}: KeyInsightsProps) {
  const [expandedInsights, setExpandedInsights] = useState<Set<number>>(new Set());

  const toggleInsight = (idx: number) => {
    setExpandedInsights(prev => {
      const next = new Set(prev);
      if (next.has(idx)) {
        next.delete(idx);
      } else {
        next.add(idx);
      }
      return next;
    });
  };

  const visibleInsights = showAll ? insights : insights.slice(0, maxVisible);
  const hasMore = insights.length > maxVisible;

  if (insights.length === 0) {
    return (
      <div
        className="p-8 rounded-xl text-center border"
        style={{ backgroundColor: `${COLORS.bg.card}`, borderColor: COLORS.border }}
      >
        <Lightbulb className="w-8 h-8 mx-auto mb-3" style={{ color: COLORS.text.muted }} />
        <p style={{ color: COLORS.text.secondary }}>No insights available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Lightbulb className="w-4.5 h-4.5" style={{ color: COLORS.status.warning }} />
          <h3 className="text-[14px] font-semibold" style={{ color: COLORS.text.primary }}>
            KEY INSIGHTS
          </h3>
        </div>

        <div className="flex items-center gap-2">
          {onViewAllInsights && hasMore && !showAll && (
            <button
              onClick={onViewAllInsights}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all duration-200 hover:bg-[#00E5FF]10"
              style={{ color: COLORS.primary.cyan }}
            >
              <span>View All</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </button>
          )}

          {onToggleShowAll && hasMore && (
            <button
              onClick={onToggleShowAll}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all duration-200 hover:bg-[#00E5FF]10"
              style={{ color: COLORS.text.secondary }}
            >
              <span>{showAll ? 'Show Less' : 'Show More'}</span>
              {showAll ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>
          )}
        </div>
      </div>

      {/* Insights List */}
      <div className="space-y-3">
        {visibleInsights.map((insight, idx) => {
          const isExpanded = expandedInsights.has(idx);
          const hasSecondary = insight.secondary && insight.secondary.length > 0;
          const confidenceColor = getConfidenceColor(insight.confidence);

          return (
            <div
              key={idx}
              className="p-4 rounded-xl border transition-all duration-200 hover:scale-[1.01]"
              style={{
                backgroundColor: `${COLORS.bg.card}`,
                borderColor: COLORS.border
              }}
            >
              {/* Primary Insight */}
              <div className="flex items-start gap-3">
                {/* Bullet Point */}
                <div
                  className="w-2 h-2 rounded-full mt-2 flex-shrink-0 animate-pulse"
                  style={{
                    backgroundColor: COLORS.primary.cyan,
                    boxShadow: `0 0 10px ${COLORS.primary.cyan}60`
                  }}
                />

                {/* Text */}
                <div className="flex-1 min-w-0">
                  <p
                    className="text-[14px] leading-relaxed"
                    style={{ color: COLORS.text.secondary }}
                  >
                    {insight.text}
                  </p>

                  {/* Confidence Badge */}
                  {insight.confidence !== undefined && (
                    <div className="mt-2 inline-flex items-center gap-1.5">
                      <span className="text-[10px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
                        Confidence
                      </span>
                      <span
                        className="text-[11px] font-mono font-medium px-2 py-0.5 rounded"
                        style={{
                          backgroundColor: `${confidenceColor}20`,
                          color: confidenceColor
                        }}
                      >
                        {Math.round(insight.confidence * 100)}%
                      </span>
                    </div>
                  )}
                </div>

                {/* Expand Toggle */}
                {hasSecondary && (
                  <button
                    onClick={() => toggleInsight(idx)}
                    className="flex-shrink-0 w-6 h-6 rounded-lg flex items-center justify-center transition-all duration-200 hover:bg-[#00E5FF]10"
                    style={{ color: COLORS.text.muted }}
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                )}
              </div>

              {/* Secondary Insights */}
              {hasSecondary && isExpanded && (
                <div
                  className="mt-4 ml-5 pl-4 border-l-2 space-y-2 animate-in slide-in-from-top-2 duration-300"
                  style={{ borderColor: `${COLORS.primary.cyan}30` }}
                >
                  {insight.secondary!.map((secondary, sIdx) => (
                    <div key={sIdx} className="flex items-start gap-2">
                      <ChevronRight className="w-4 h-4 mt-0.5 flex-shrink-0" style={{ color: COLORS.text.muted }} />
                      <p
                        className="text-[13px] leading-relaxed"
                        style={{ color: COLORS.text.muted }}
                      >
                        {secondary}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Insight Summary Footer */}
      {hasMore && !showAll && (
        <div
          className="flex items-center justify-center gap-2 p-3 rounded-lg border cursor-pointer transition-all duration-200 hover:bg-[#00E5FF]10 hover:scale-105"
          style={{ borderColor: `${COLORS.border}50` }}
          onClick={onToggleShowAll}
        >
          <span className="text-xs" style={{ color: COLORS.text.muted }}>
            +{insights.length - maxVisible} more insights
          </span>
          <ChevronDown className="w-4 h-4" style={{ color: COLORS.primary.cyan }} />
        </div>
      )}

      {/* Total Count */}
      <div className="flex items-center justify-end text-xs pt-2">
        <span style={{ color: COLORS.text.muted }}>
          Total:
        </span>
        <span className="font-mono ml-1.5" style={{ color: COLORS.text.secondary }}>
          {insights.length} insights
        </span>
      </div>
    </div>
  );
}
