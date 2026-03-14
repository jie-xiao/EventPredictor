import { useRef, useState, useEffect, useCallback } from 'react';
import Globe from 'react-globe.gl';
import { WorldMonitorEvent } from '../services/api';

interface GlobeMapProps {
  events: WorldMonitorEvent[];
  selectedEvent: WorldMonitorEvent | null;
  onEventClick: (event: WorldMonitorEvent) => void;
}

// ============ 设计规范色彩 ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const getMarkerColor = (severity: number): string => {
  if (severity >= 4) return COLORS.status.danger;
  if (severity >= 3) return COLORS.status.warning;
  return COLORS.status.success;
};

const getMarkerSize = (severity: number): number => {
  return 0.3 + severity * 0.12;
};

const getSeverityLabel = (severity: number): string => {
  if (severity >= 4) return 'HIGH';
  if (severity >= 3) return 'MEDIUM';
  return 'LOW';
};

export default function GlobeMap({ events, selectedEvent, onEventClick }: GlobeMapProps) {
  const globeRef = useRef<any>(null);
  const [dimensions, setDimensions] = useState({ width: 600, height: 500 });
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredEvent, setHoveredEvent] = useState<WorldMonitorEvent | null>(null);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { offsetWidth, offsetHeight } = containerRef.current;
        setDimensions({
          width: offsetWidth || 600,
          height: offsetHeight || 500
        });
      }
    };

    updateDimensions();
    const resizeObserver = new ResizeObserver(updateDimensions);
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    return () => resizeObserver.disconnect();
  }, []);

  // Focus on selected event with smooth transition
  useEffect(() => {
    if (selectedEvent?.location?.lat && selectedEvent?.location?.lon && globeRef.current) {
      const { lat, lon } = selectedEvent.location;
      globeRef.current.pointOfView({ lat, lon, altitude: 2 }, 1500);
    }
  }, [selectedEvent]);

  const markersData = events
    .filter(event => event.location?.lat && event.location?.lon)
    .map(event => ({
      id: event.id,
      lat: event.location!.lat!,
      lng: event.location!.lon!,
      size: getMarkerSize(event.severity || 3),
      color: getMarkerColor(event.severity || 3),
      event: event
    }));

  const handleMarkerClick = useCallback((marker: any) => {
    if (marker.event) {
      onEventClick(marker.event);
    }
  }, [onEventClick]);

  const handleMarkerHover = useCallback((marker: any) => {
    setHoveredEvent(marker?.event || null);
  }, []);

  return (
    <div ref={containerRef} className="w-full h-full relative">
      <Globe
        ref={globeRef}
        width={dimensions.width}
        height={dimensions.height}
        globeImageUrl="//unpkg.com/three-globe/example/img/earth-night.jpg"
        bumpImageUrl="//unpkg.com/three-globe/example/img/earth-topology.png"
        backgroundImageUrl="//unpkg.com/three-globe/example/img/night-sky.png"
        pointsData={markersData}
        pointLat="lat"
        pointLng="lng"
        pointColor="color"
        pointRadius="size"
        pointResolution={16}
        onPointClick={handleMarkerClick}
        onPointHover={handleMarkerHover}
        pointsMerge={true}
        atmosphereColor={COLORS.primary.cyan}
        atmosphereAltitude={0.15}
        pointAltitude={0.015}
        // Custom point label with design system colors
        pointLabel={(d: any) => `
          <div style="
            background: rgba(15, 23, 42, 0.95);
            padding: 12px 16px;
            border-radius: 12px;
            border: 1px solid ${COLORS.border};
            max-width: 220px;
            backdrop-filter: blur(12px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
          ">
            <div style="color: ${d.color}; font-weight: 600; font-size: 13px; margin-bottom: 6px;">${d.event?.title || 'Event'}</div>
            <div style="color: ${COLORS.text.secondary}; font-size: 11px; margin-bottom: 4px;">${d.event?.location?.country || d.event?.location?.region || 'Unknown'}</div>
            <div style="display: flex; align-items: center; gap: 6px;">
              <div style="width: 8px; height: 8px; border-radius: 50%; background: ${d.color};"></div>
              <span style="color: ${COLORS.text.muted}; font-size: 10px; font-weight: 600;">${getSeverityLabel(d.event?.severity || 3)}</span>
              <span style="color: ${COLORS.text.muted}; font-size: 10px;">Severity ${d.event?.severity || 3}/5</span>
            </div>
          </div>
        `}
      />

      {/* Hovered Event Tooltip */}
      {hoveredEvent && (
        <div className="absolute top-4 left-4 rounded-xl p-4 max-w-xs z-10 transition-all duration-300"
          style={{
            backgroundColor: `${COLORS.bg.card}95`,
            backdropFilter: 'blur(12px)',
            border: `1px solid ${COLORS.border}`,
            boxShadow: `0 8px 32px rgba(0, 0, 0, 0.4), 0 0 20px ${getMarkerColor(hoveredEvent.severity || 3)}30`
          }}>
          <div className="flex items-start gap-3">
            <div
              className="w-4 h-4 rounded-full mt-1.5 flex-shrink-0 animate-pulse"
              style={{
                backgroundColor: getMarkerColor(hoveredEvent.severity || 3),
                boxShadow: `0 0 12px ${getMarkerColor(hoveredEvent.severity || 3)}80`
              }}
            />
            <div className="flex-1">
              <h4 className="text-[14px] font-semibold line-clamp-2" style={{ color: COLORS.text.primary }}>
                {hoveredEvent.title}
              </h4>
              <p className="text-[12px] mt-1" style={{ color: COLORS.text.secondary }}>
                {hoveredEvent.location?.country || hoveredEvent.location?.region || 'Unknown'}
              </p>
              <div className="flex items-center gap-2 mt-2">
                <span
                  className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  style={{
                    backgroundColor: `${getMarkerColor(hoveredEvent.severity || 3)}20`,
                    color: getMarkerColor(hoveredEvent.severity || 3)
                  }}
                >
                  {getSeverityLabel(hoveredEvent.severity || 3)}
                </span>
                <span className="text-[11px]" style={{ color: COLORS.text.muted }}>
                  Severity {hoveredEvent.severity || 3}/5
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 rounded-lg p-3 z-10"
        style={{
          backgroundColor: `${COLORS.bg.card}80`,
          backdropFilter: 'blur(12px)',
          border: `1px solid ${COLORS.border}`
        }}>
        <div className="text-[11px] mb-2 uppercase tracking-wider font-medium" style={{ color: COLORS.text.muted }}>
          Severity Level
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2">
            <div
              className="w-2.5 h-2.5 rounded-full transition-all duration-200"
              style={{ backgroundColor: COLORS.status.danger, boxShadow: `0 0 8px ${COLORS.status.danger}60` }}
            />
            <span className="text-[12px]" style={{ color: COLORS.text.secondary }}>High (4-5)</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-2.5 h-2.5 rounded-full transition-all duration-200"
              style={{ backgroundColor: COLORS.status.warning, boxShadow: `0 0 8px ${COLORS.status.warning}60` }}
            />
            <span className="text-[12px]" style={{ color: COLORS.text.secondary }}>Medium (3)</span>
          </div>
          <div className="flex items-center gap-2">
            <div
              className="w-2.5 h-2.5 rounded-full transition-all duration-200"
              style={{ backgroundColor: COLORS.status.success, boxShadow: `0 0 8px ${COLORS.status.success}60` }}
            />
            <span className="text-[12px]" style={{ color: COLORS.text.secondary }}>Low (1-2)</span>
          </div>
        </div>
      </div>

      {/* No events message */}
      {events.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center rounded-lg z-20"
          style={{ backgroundColor: `${COLORS.bg.dark}80` }}>
          <div className="text-center">
            <div className="w-16 h-16 mx-auto mb-4 rounded-lg flex items-center justify-center transition-all duration-300"
              style={{ backgroundColor: `${COLORS.primary.cyan}10` }}>
              <span className="text-3xl">🌍</span>
            </div>
            <p style={{ color: COLORS.text.secondary }}>No events with location data</p>
          </div>
        </div>
      )}
    </div>
  );
}
