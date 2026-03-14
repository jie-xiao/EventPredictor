import { useState } from 'react';
import '../styles/drawer-toolbar.css';

export interface EventMarkerProps {
  severity: 1 | 2 | 3 | 4 | 5;
  x: number;
  y: number;
  isSelected?: boolean;
  onClick?: () => void;
  onHover?: (isHovering: boolean) => void;
  tooltip?: {
    title: string;
    description?: string;
    time?: string;
  };
}

export default function EventMarker({
  severity,
  x,
  y,
  isSelected = false,
  onClick,
  onHover,
  tooltip,
}: EventMarkerProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div
      className={`event-marker ${isSelected ? 'selected' : ''}`}
      style={{ left: x, top: y }}
      data-severity={severity}
      onClick={onClick}
      onMouseEnter={() => {
        setShowTooltip(true);
        onHover?.(true);
      }}
      onMouseLeave={() => {
        setShowTooltip(false);
        onHover?.(false);
      }}
    >
      {/* Core point */}
      <div className="core" />

      {/* Inner pulse */}
      <div className="pulse-inner" />

      {/* Outer pulse */}
      <div className="pulse-outer" />

      {/* Tooltip */}
      {tooltip && showTooltip && (
        <div
          className="absolute z-[500] left-1/2 -translate-x-1/2 bottom-full mb-3
            px-3 py-2 min-w-[160px] max-w-[240px]
            bg-[#0F172A]/95 backdrop-blur-md rounded-lg
            border border-[#1E293B] shadow-lg
            pointer-events-none animate-fade-in"
        >
          {/* Arrow */}
          <div
            className="absolute left-1/2 -translate-x-1/2 top-full
              w-0 h-0 border-l-[6px] border-r-[6px] border-t-[6px]
              border-l-transparent border-r-transparent border-t-[#1E293B]"
          />
          <h4 className="text-sm font-medium text-text-primary mb-1">
            {tooltip.title}
          </h4>
          {tooltip.description && (
            <p className="text-xs text-text-secondary line-clamp-2 mb-1">
              {tooltip.description}
            </p>
          )}
          {tooltip.time && (
            <p className="text-[10px] text-text-muted">{tooltip.time}</p>
          )}
        </div>
      )}
    </div>
  );
}

// 严重程度颜色映射
export const severityColors: Record<EventMarkerProps['severity'], { main: string; glow: string }> = {
  5: { main: '#EF4444', glow: 'rgba(239, 68, 68, 0.6)' },
  4: { main: '#F97316', glow: 'rgba(249, 115, 22, 0.6)' },
  3: { main: '#F59E0B', glow: 'rgba(245, 158, 11, 0.6)' },
  2: { main: '#22C55E', glow: 'rgba(34, 197, 94, 0.6)' },
  1: { main: '#3B82F6', glow: 'rgba(59, 130, 246, 0.6)' },
};

// 严重程度标签
export const severityLabels: Record<EventMarkerProps['severity'], string> = {
  5: 'Critical',
  4: 'High',
  3: 'Important',
  2: 'Normal',
  1: 'Low',
};
