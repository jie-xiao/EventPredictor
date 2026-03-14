import { useState, useMemo, useRef, useEffect } from 'react';
import { ChevronUp, X, MapPin, Clock, Search, Filter, XCircle } from 'lucide-react';
import '../styles/drawer-toolbar.css';

export interface Event {
  id: string;
  title: string;
  severity: 1 | 2 | 3 | 4 | 5;
  location?: string;
  timestamp: string;
  category?: string;
  description?: string;
}

export interface BottomDrawerProps {
  isOpen: boolean;
  onToggle: () => void;
  events?: Event[];
  selectedEventId?: string;
  onEventSelect?: (event: Event) => void;
  onClose?: () => void;
}

const severityLabels: Record<Event['severity'], { label: string; class: string }> = {
  5: { label: 'Critical', class: 'critical' },
  4: { label: 'High', class: 'critical' },
  3: { label: 'Important', class: 'warning' },
  2: { label: 'Normal', class: 'normal' },
  1: { label: 'Low', class: 'normal' },
};

const categoryLabels: Record<string, string> = {
  'military': '军事',
  'politics': '政治',
  'economy': '经济',
  'technology': '科技',
  'sports': '体育',
  'entertainment': '娱乐',
  'health': '健康',
  'science': '科学',
  'other': '其他',
  'Monetary Policy': '货币政策',
  'Geopolitical': '地缘政治',
  'Economic': '经济',
  'Technology': '科技',
  'Trade': '贸易',
  'Social': '社会'
};

export default function BottomDrawer({
  isOpen,
  onToggle,
  events = [],
  selectedEventId,
  onEventSelect,
  onClose,
}: BottomDrawerProps) {
  const [isInternalClose, setIsInternalClose] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedSeverities, setSelectedSeverities] = useState<number[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  // Debounce timer ref
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounce effect for search
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    debounceTimerRef.current = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [searchQuery]);

  // 获取所有可用类别
  const availableCategories = useMemo(() => {
    const cats = new Set(events.map(e => e.category).filter((c): c is string => Boolean(c)));
    return Array.from(cats);
  }, [events]);

  // 过滤事件
  const filteredEvents = useMemo(() => {
    return events.filter(event => {
      // 搜索过滤（使用防抖后的值）
      if (debouncedSearchQuery) {
        const query = debouncedSearchQuery.toLowerCase();
        const titleMatch = event.title.toLowerCase().includes(query);
        const descMatch = event.description?.toLowerCase().includes(query);
        const locMatch = event.location?.toLowerCase().includes(query);
        if (!titleMatch && !descMatch && !locMatch) {
          return false;
        }
      }

      // 类别过滤
      if (selectedCategories.length > 0 && event.category) {
        if (!selectedCategories.includes(event.category)) {
          return false;
        }
      }

      // 严重程度过滤
      if (selectedSeverities.length > 0) {
        if (!selectedSeverities.includes(event.severity)) {
          return false;
        }
      }

      return true;
    });
  }, [events, debouncedSearchQuery, selectedCategories, selectedSeverities]);

  const stats = {
    critical: events.filter((e) => e.severity >= 4).length,
    warning: events.filter((e) => e.severity === 3).length,
    normal: events.filter((e) => e.severity < 3).length,
  };

  const handleClose = () => {
    setIsInternalClose(true);
    onClose?.();
  };

  const handleHeaderClick = () => {
    if (!isInternalClose) {
      onToggle();
    }
    setIsInternalClose(false);
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const toggleCategory = (category: string) => {
    setSelectedCategories(prev =>
      prev.includes(category)
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const toggleSeverity = (severity: number) => {
    setSelectedSeverities(prev =>
      prev.includes(severity)
        ? prev.filter(s => s !== severity)
        : [...prev, severity]
    );
  };

  const clearFilters = () => {
    setSearchQuery('');
    setDebouncedSearchQuery('');
    setSelectedCategories([]);
    setSelectedSeverities([]);
  };

  const hasActiveFilters = debouncedSearchQuery || selectedCategories.length > 0 || selectedSeverities.length > 0;

  return (
    <div className={`drawer-bottom ${isOpen ? 'open' : ''}`}>
      {/* Header - Clickable */}
      <div className="drawer-header" onClick={handleHeaderClick}>
        <div className="header-left">
          <ChevronUp className="expand-icon w-5 h-5" />
          <span className="text-sm font-medium text-text-primary">
            Event List
          </span>
          <span className="text-sm text-text-muted">({events.length})</span>
        </div>

        <div className="event-stats">
          <div className="stat-item">
            <span className="stat-dot critical" />
            <span className="text-xs text-text-secondary">{stats.critical} Critical</span>
          </div>
          <span className="text-text-muted">·</span>
          <div className="stat-item">
            <span className="stat-dot warning" />
            <span className="text-xs text-text-secondary">{stats.warning} Important</span>
          </div>
          <span className="text-text-muted">·</span>
          <div className="stat-item">
            <span className="stat-dot normal" />
            <span className="text-xs text-text-secondary">{stats.normal} Normal</span>
          </div>
        </div>

        {isOpen && (
          <button
            className="p-1 hover:bg-[#1E293B] rounded transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              handleClose();
            }}
            aria-label="Close event list"
          >
            <X className="w-4 h-4 text-text-muted" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="drawer-content">
        {/* 搜索和筛选栏 */}
        {isOpen && (
          <div className="p-3 border-b border-[#1E293B] bg-[#0A0E1A]/50">
            {/* 搜索框 */}
            <div className="relative mb-2">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="text"
                placeholder="搜索事件..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-10 py-2 bg-[#0F172A] border border-[#1E293B] rounded-lg text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-primary-cyan/50"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-secondary"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* 筛选按钮和状态 */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg transition-colors ${
                  showFilters ? 'bg-primary-cyan/20 text-primary-cyan' : 'bg-[#1E293B] text-text-secondary hover:bg-[#2D3A4F]'
                }`}
              >
                <Filter className="w-3 h-3" />
                筛选
              </button>

              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="flex items-center gap-1 px-3 py-1.5 text-xs rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors"
                >
                  <XCircle className="w-3 h-3" />
                  清除筛选
                </button>
              )}

              {hasActiveFilters && (
                <span className="text-xs text-text-muted">
                  {filteredEvents.length} / {events.length} 条结果
                </span>
              )}
            </div>

            {/* 筛选面板 */}
            {showFilters && (
              <div className="mt-3 p-3 bg-[#0F172A] rounded-lg space-y-3">
                {/* 严重程度筛选 */}
                <div>
                  <label className="text-xs text-text-muted mb-2 block">严重程度</label>
                  <div className="flex flex-wrap gap-1">
                    {[5, 4, 3, 2, 1].map(sev => {
                      const label = severityLabels[sev as keyof typeof severityLabels];
                      const isSelected = selectedSeverities.includes(sev);
                      return (
                        <button
                          key={sev}
                          onClick={() => toggleSeverity(sev)}
                          className={`px-2 py-1 text-xs rounded transition-colors ${
                            isSelected
                              ? 'bg-primary-cyan/20 text-primary-cyan border border-primary-cyan/30'
                              : 'bg-[#1E293B] text-text-secondary border border-transparent hover:border-[#334155]'
                          }`}
                        >
                          {label.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* 类别筛选 */}
                <div>
                  <label className="text-xs text-text-muted mb-2 block">事件类别</label>
                  <div className="flex flex-wrap gap-1">
                    {availableCategories.map(cat => {
                      const isSelected = selectedCategories.includes(cat);
                      const label = categoryLabels[cat] || cat;
                      return (
                        <button
                          key={cat}
                          onClick={() => toggleCategory(cat)}
                          className={`px-2 py-1 text-xs rounded transition-colors ${
                            isSelected
                              ? 'bg-primary-cyan/20 text-primary-cyan border border-primary-cyan/30'
                              : 'bg-[#1E293B] text-text-secondary border border-transparent hover:border-[#334155]'
                          }`}
                        >
                          {label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {filteredEvents.length === 0 ? (
          <div className="flex items-center justify-center h-full text-text-muted">
            <p>{hasActiveFilters ? '没有匹配的事件' : 'No events to display'}</p>
          </div>
        ) : (
          filteredEvents.map((event) => {
            const severity = severityLabels[event.severity];
            const categoryLabel = event.category ? (categoryLabels[event.category] || event.category) : '';
            return (
              <div
                key={event.id}
                className={`event-card ${selectedEventId === event.id ? 'selected' : ''}`}
                onClick={() => onEventSelect?.(event)}
              >
                <div className="card-header">
                  <span className={`severity-badge ${severity.class}`}>
                    {severity.label}
                  </span>
                  {categoryLabel && (
                    <span className="px-2 py-0.5 text-xs bg-[#1E293B] text-text-muted rounded">
                      {categoryLabel}
                    </span>
                  )}
                </div>
                <h4 className="event-title">{event.title}</h4>
                <div className="event-meta">
                  {event.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {event.location}
                    </span>
                  )}
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatTimestamp(event.timestamp)}
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
