import { ArrowLeft, Download, Share2, RefreshCw, Clock } from 'lucide-react';
import { WorldMonitorEvent } from '../../services/api';

interface AnalysisHeaderProps {
  event: WorldMonitorEvent | null;
  overallConfidence: number;
  analysesCount: number;
  conflictsCount: number;
  onBack: () => void;
  onRefresh?: () => void;
  onExport?: () => void;
  onShare?: () => void;
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

const formatTime = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor(diff / (1000 * 60));
  if (hours >= 24) return `${Math.floor(hours / 24)}d`;
  if (hours >= 1) return `${hours}h`;
  return `${minutes}m ago`;
};

export default function AnalysisHeader({
  event,
  overallConfidence,
  analysesCount,
  conflictsCount,
  onBack,
  onRefresh,
  onExport,
  onShare
}: AnalysisHeaderProps) {
  const config = event ? CATEGORY_CONFIG[event.category] || CATEGORY_CONFIG.other : CATEGORY_CONFIG.other;
  const severityColor = event ? getSeverityColor(event.severity || 3) : COLORS.border;

  return (
    <header
      className="sticky top-0 z-50 border-b backdrop-blur-xl h-[60px]"
      style={{
        backgroundColor: `${COLORS.bg.dark}F2`,
        borderColor: `${COLORS.border}80`
      }}
    >
      <div className="h-full px-6 flex items-center justify-between">
        {/* Left: Back Button + Event Info */}
        <div className="flex items-center gap-6 flex-1 min-w-0">
          {/* Back Button */}
          <button
            onClick={onBack}
            className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200 hover:scale-110 hover:bg-[#00E5FF]20"
            style={{ color: COLORS.text.secondary }}
            aria-label="Back to dashboard"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>

          {/* Event Title & Tags */}
          <div className="flex items-center gap-4 min-w-0">
            <div className="flex items-center gap-2 min-w-0">
              {/* Category Icon */}
              <span className="text-lg flex-shrink-0">{config.emoji}</span>

              {/* Event Title */}
              <h1
                className="text-[16px] font-semibold truncate max-w-[300px] lg:max-w-[500px]"
                style={{ color: COLORS.text.primary }}
              >
                {event?.title || 'Event Analysis'}
              </h1>
            </div>

            {/* Tags */}
            <div className="hidden sm:flex items-center gap-2 flex-shrink-0">
              {/* Severity Tag */}
              <span
                className="h-6 px-3 rounded-full text-[11px] font-bold uppercase tracking-wider flex items-center gap-1.5"
                style={{
                  backgroundColor: `${severityColor}20`,
                  color: severityColor,
                  border: `1px solid ${severityColor}40`
                }}
              >
                Severity {event?.severity || 3}/5
              </span>

              {/* Category Tag */}
              <span
                className="h-6 px-3 rounded-full text-[11px] font-medium uppercase tracking-wider"
                style={{
                  backgroundColor: `${config.color}20`,
                  color: config.color,
                  border: `1px solid ${config.color}40`
                }}
              >
                {config.label}
              </span>

              {/* Time Tag */}
              <span className="h-6 px-3 rounded-full text-[11px] text-muted flex items-center gap-1.5"
                style={{ backgroundColor: `${COLORS.border}40`, color: COLORS.text.muted }}
              >
                <Clock className="w-3 h-3" />
                {event ? formatTime(event.timestamp) : '--'}
              </span>
            </div>
          </div>
        </div>

        {/* Right: Stats + Actions */}
        <div className="flex items-center gap-4 flex-shrink-0">
          {/* Quick Stats - Hidden on small screens */}
          <div className="hidden md:flex items-center gap-4 pr-4 mr-2"
            style={{ borderRight: `1px solid ${COLORS.border}50` }}
          >
            <div className="text-center">
              <p className="text-[12px] text-muted uppercase tracking-wider">Roles</p>
              <p className="text-sm font-mono font-semibold" style={{ color: COLORS.primary.cyan }}>
                {analysesCount}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[12px] text-muted uppercase tracking-wider">Conflicts</p>
              <p className="text-sm font-mono font-semibold" style={{ color: COLORS.status.danger }}>
                {conflictsCount}
              </p>
            </div>
            <div className="text-center">
              <p className="text-[12px] text-muted uppercase tracking-wider">Confidence</p>
              <p className="text-sm font-mono font-semibold" style={{ color: getSeverityColor(Math.round(overallConfidence * 5)) }}>
                {Math.round(overallConfidence * 100)}%
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-1">
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 hover:scale-110 hover:bg-[#00E5FF]20"
                style={{ color: COLORS.text.secondary }}
                title="Refresh analysis"
              >
                <RefreshCw className="w-4.5 h-4.5" />
              </button>
            )}
            {onShare && (
              <button
                onClick={onShare}
                className="w-9 h-9 rounded-lg flex items-center justify-center transition-all duration-200 hover:scale-110 hover:bg-[#00E5FF]20"
                style={{ color: COLORS.text.secondary }}
                title="Share analysis"
              >
                <Share2 className="w-4.5 h-4.5" />
              </button>
            )}
            {onExport && (
              <button
                onClick={onExport}
                className="px-4 h-9 rounded-lg flex items-center gap-2 transition-all duration-200 hover:scale-105"
                style={{
                  background: `linear-gradient(90deg, ${COLORS.primary.cyan} 0%, ${COLORS.primary.blue} 100%)`,
                  color: COLORS.bg.dark,
                  boxShadow: `0 0 20px ${COLORS.primary.cyan}30`
                }}
                title="Export report"
              >
                <Download className="w-4 h-4" />
                <span className="text-sm font-medium">Export</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
