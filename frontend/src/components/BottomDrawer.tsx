import { useState } from 'react';
import { ChevronUp, X, MapPin, Clock } from 'lucide-react';
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

export default function BottomDrawer({
  isOpen,
  onToggle,
  events = [],
  selectedEventId,
  onEventSelect,
  onClose,
}: BottomDrawerProps) {
  const [isInternalClose, setIsInternalClose] = useState(false);

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
        {events.length === 0 ? (
          <div className="flex items-center justify-center h-full text-text-muted">
            <p>No events to display</p>
          </div>
        ) : (
          events.map((event) => {
            const severity = severityLabels[event.severity];
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
