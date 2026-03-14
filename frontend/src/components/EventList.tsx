import { useRef, useEffect } from 'react';
import { Clock, MapPin, Zap, ChevronRight, Filter } from 'lucide-react';
import { WorldMonitorEvent } from '../services/api';

interface EventListProps {
  events: WorldMonitorEvent[];
  selectedEvent: WorldMonitorEvent | null;
  onEventClick: (event: WorldMonitorEvent) => void;
  loading: boolean;
}

// ============ 设计规范色彩 ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const CATEGORY_CONFIG: Record<string, { color: string; emoji: string; label: string }> = {
  military: { color: '#EF4444', emoji: '🎯', label: '军事' },
  conflict: { color: '#EF4444', emoji: '⚔️', label: '冲突' },
  economy: { color: '#F59E0B', emoji: '📈', label: '经济' },
  trade: { color: '#F59E0B', emoji: '🚢', label: '贸易' },
  politics: { color: '#8B5CF6', emoji: '🏛️', label: '政治' },
  disaster: { color: '#EF4444', emoji: '🔥', label: '灾难' },
  cyber: { color: '#06B6D4', emoji: '💻', label: '网络' },
  technology: { color: '#3B82F6', emoji: '🔬', label: '科技' },
  'Monetary Policy': { color: '#F59E0B', emoji: '💰', label: '货币政策' },
  Geopolitical: { color: '#8B5CF6', emoji: '🌐', label: '地缘政治' },
  Economic: { color: '#F59E0B', emoji: '📊', label: '经济' },
  Technology: { color: '#3B82F6', emoji: '🔬', label: '科技' },
  Trade: { color: '#F59E0B', emoji: '🚢', label: '贸易' },
  Social: { color: '#22C55E', emoji: '👥', label: '社会' },
  other: { color: '#22C55E', emoji: '📌', label: '其他' },
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
  return `${minutes}m`;
};

// Severity Bar Component
const SeverityBar = ({ level }: { level: number }) => (
  <div className="flex items-center gap-0.5 h-2">
    {[1, 2, 3, 4, 5].map((i) => (
      <div
        key={i}
        className="w-1 rounded-sm transition-all duration-200"
        style={{
          height: i <= level ? '100%' : '40%',
          backgroundColor: i <= level ? getSeverityColor(level) : `${COLORS.border}50`
        }}
      />
    ))}
  </div>
);

export default function EventList({ events, selectedEvent, onEventClick, loading }: EventListProps) {
  const listRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to selected event
  useEffect(() => {
    if (selectedEvent && listRef.current) {
      const selectedElement = listRef.current.querySelector(`[data-event-id="${selectedEvent.id}"]`);
      if (selectedElement) {
        selectedElement.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    }
  }, [selectedEvent]);

  if (loading) {
    return (
      <div className="h-[180px] flex flex-col rounded-lg overflow-hidden glass-card-enhanced">
        {/* Header */}
        <div className="px-4 py-3 border-b flex items-center justify-between" style={{ borderColor: COLORS.border, backgroundColor: `${COLORS.bg.card}80` }}>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 animate-wave" style={{ color: COLORS.primary.cyan }} />
            <span className="text-[14px] font-medium" style={{ color: COLORS.text.primary }}>实时事件流</span>
          </div>
        </div>

        {/* Loading State */}
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="relative animate-breathe">
              <div className="w-12 h-12 border-3 rounded-full animate-spin"
                style={{ borderColor: `${COLORS.primary.cyan}20`, borderTopColor: COLORS.primary.cyan, borderWidth: '3px' }} />
              <div className="absolute inset-1.5 w-9 h-9 border-3 rounded-full animate-spin"
                style={{ borderColor: `${COLORS.primary.blue}20`, borderBottomColor: COLORS.primary.blue, borderWidth: '3px', animationDirection: 'reverse' }} />
            </div>
            <span className="text-[12px] animate-pulse" style={{ color: COLORS.text.secondary }}>加载事件中...</span>
          </div>
        </div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="h-[180px] flex flex-col rounded-lg overflow-hidden glass-card-enhanced">
        {/* Header */}
        <div className="px-4 py-3 border-b flex items-center justify-between" style={{ borderColor: COLORS.border, backgroundColor: `${COLORS.bg.card}80` }}>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4" style={{ color: COLORS.primary.cyan }} />
            <span className="text-[14px] font-medium" style={{ color: COLORS.text.primary }}>实时事件流</span>
          </div>
        </div>

        {/* Empty State */}
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <span className="text-5xl mb-2 block animate-bounce-in">📭</span>
            <span style={{ color: COLORS.text.secondary }}>暂无事件数据</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[180px] flex flex-col rounded-lg overflow-hidden glass-card-enhanced">
      {/* Header */}
      <div className="px-4 py-3 border-b flex items-center justify-between flex-shrink-0" style={{ borderColor: COLORS.border, backgroundColor: `${COLORS.bg.card}80` }}>
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 animate-pulse" style={{ color: COLORS.primary.cyan }} />
          <span className="text-[14px] font-medium" style={{ color: COLORS.text.primary }}>实时事件流</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[12px] font-mono data-tag-cyan" style={{ padding: '2px 8px', borderRadius: '4px' }}>{events.length} 条事件</span>
          <button
            className="p-1.5 rounded transition-all duration-200 hover:scale-110 hover-glow"
            style={{ backgroundColor: `${COLORS.border}50` }}
            title="筛选事件"
          >
            <Filter className="w-3.5 h-3.5" style={{ color: COLORS.text.secondary }} />
          </button>
        </div>
      </div>

      {/* Horizontal Scrollable Event List */}
      <div ref={listRef} className="flex-1 overflow-x-auto overflow-y-hidden">
        <div className="flex gap-4 p-4 h-full">
          {events.map((event) => {
            const config = CATEGORY_CONFIG[event.category] || CATEGORY_CONFIG.other;
            const isSelected = selectedEvent?.id === event.id;
            const isHighSeverity = (event.severity || 3) >= 4;
            const severityColor = getSeverityColor(event.severity || 3);
            // 优先使用后端返回的中文标签，否则使用配置中的标签
            const categoryLabel = event.category_label || config.label;

            return (
              <div
                key={event.id}
                data-event-id={event.id}
                onClick={() => onEventClick(event)}
                className="flex-shrink-0 w-[280px] p-4 rounded-lg cursor-pointer transition-all duration-300 border relative group click-feedback hover-scale"
                style={{
                  backgroundColor: isSelected ? `${COLORS.primary.cyan}10` : `${COLORS.bg.card}80`,
                  borderColor: isSelected ? `${COLORS.primary.cyan}50` : `${COLORS.border}50`,
                  boxShadow: isSelected ? `0 0 20px ${COLORS.primary.cyan}20` : 'none'
                }}
              >
                {/* High Severity Indicator */}
                {isHighSeverity && (
                  <div className="absolute top-0 right-0 w-12 h-12 overflow-hidden">
                    <div
                      className="absolute top-2 -right-4 text-white text-[8px] font-bold px-4 py-0.5 rotate-45"
                      style={{ backgroundColor: severityColor }}
                    >
                      高危
                    </div>
                  </div>
                )}

                {/* Left Border Indicator */}
                <div
                  className="absolute left-0 top-0 bottom-0 w-1 rounded-l-lg transition-all duration-200"
                  style={{
                    backgroundColor: severityColor,
                    opacity: isSelected ? 1 : 0.5,
                    boxShadow: `0 0 10px ${severityColor}`
                  }}
                />

                <div className="flex items-start gap-3 pl-2">
                  {/* Category Icon */}
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 transition-transform duration-200 group-hover:scale-110"
                    style={{ backgroundColor: `${config.color}20` }}
                  >
                    <span className="text-lg">{config.emoji}</span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    {/* Category Badge */}
                    <div className="flex items-center gap-2 mb-1.5">
                      <span
                        className="px-2 py-0.5 rounded text-[10px] font-medium tracking-wider"
                        style={{
                          backgroundColor: `${config.color}20`,
                          color: config.color,
                          border: `1px solid ${config.color}30`
                        }}
                      >
                        {categoryLabel}
                      </span>
                    </div>

                    {/* Title */}
                    <h4 className="text-[14px] font-medium mb-2 line-clamp-2 transition-all duration-200 group-hover:text-cyan-300"
                      style={{ color: COLORS.text.primary }}>
                      {event.title}
                    </h4>

                    {/* Severity Bar */}
                    <div className="mb-2">
                      <SeverityBar level={event.severity || 3} />
                    </div>

                    {/* Meta Info */}
                    <div className="flex items-center gap-4 text-[11px]" style={{ color: COLORS.text.muted }}>
                      <span className="flex items-center gap-1.5">
                        <MapPin className="w-3 h-3" />
                        <span className="truncate max-w-[70px]">
                          {event.location?.country || event.location?.region || '未知'}
                        </span>
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Clock className="w-3 h-3" />
                        <span className="font-mono">{formatTime(event.timestamp)}前</span>
                      </span>
                    </div>
                  </div>

                  {/* Arrow */}
                  <ChevronRight
                    className="w-5 h-5 flex-shrink-0 transition-all duration-200"
                    style={{
                      color: isSelected ? COLORS.primary.cyan : COLORS.border,
                      transform: isSelected ? 'translateX(2px)' : 'translateX(0)'
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
