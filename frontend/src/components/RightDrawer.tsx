import { X, TrendingUp, TrendingDown, Minus, AlertTriangle, Clock, FileText } from 'lucide-react';
import '../styles/drawer-toolbar.css';

export interface RightDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  trend?: 'up' | 'down' | 'neutral';
  confidence?: number;
  insights?: string[];
  riskLevel?: 'high' | 'medium' | 'low';
  conflictCount?: number;
  timeline?: { time: string; event: string; status: 'completed' | 'ongoing' | 'pending' }[];
  consensus?: string[];
  onDetailView?: () => void;
  children?: React.ReactNode;
}

export default function RightDrawer({
  isOpen,
  onClose,
  title = 'Trend Prediction',
  trend = 'neutral',
  confidence = 75,
  insights = [],
  riskLevel = 'medium',
  conflictCount = 0,
  timeline = [],
  consensus = [],
  onDetailView,
  children,
}: RightDrawerProps) {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-8 h-8 text-green-400" />;
      case 'down':
        return <TrendingDown className="w-8 h-8 text-red-400" />;
      default:
        return <Minus className="w-8 h-8 text-yellow-400" />;
    }
  };

  const getTrendLabel = () => {
    switch (trend) {
      case 'up':
        return 'Rising';
      case 'down':
        return 'Falling';
      default:
        return 'Stable';
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'text-green-400';
      case 'down':
        return 'text-red-400';
      default:
        return 'text-yellow-400';
    }
  };

  const getRiskColor = () => {
    switch (riskLevel) {
      case 'high':
        return 'text-red-400';
      case 'low':
        return 'text-green-400';
      default:
        return 'text-yellow-400';
    }
  };

  return (
    <>
      {/* 遮罩层 */}
      <div
        className={`drawer-overlay ${isOpen ? 'visible' : ''}`}
        onClick={onClose}
      />

      {/* 抽屉面板 */}
      <div className={`drawer-right ${isOpen ? 'open' : ''}`}>
        {/* Header */}
        <div className="drawer-header">
          <div className="flex items-center gap-3">
            <button
              className="drawer-close-btn"
              onClick={onClose}
              aria-label="Close drawer"
            >
              <X className="w-4 h-4" />
            </button>
            <span className="drawer-header-title">{title}</span>
          </div>
        </div>

        {/* Content */}
        <div className="drawer-content">
          {/* If children provided, render them */}
          {children ? (
            children
          ) : (
            <>
              {/* Section 1: Trend & Confidence */}
              <div className="drawer-section">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {getTrendIcon()}
                    <div>
                      <p className={`text-lg font-semibold ${getTrendColor()}`}>
                        {getTrendLabel()}
                      </p>
                      <p className="text-xs text-text-muted">Trend Direction</p>
                    </div>
                  </div>
                  <div className="text-center">
                    <p className="data-value-md gradient-text">{confidence}%</p>
                    <p className="data-label mt-1">Confidence</p>
                  </div>
                </div>
                {/* Confidence Progress Bar */}
                <div className="mt-4">
                  <div className="h-2 bg-[#1E293B] rounded-full overflow-hidden">
                    <div
                      className="h-full gradient-primary transition-all duration-500"
                      style={{ width: `${confidence}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Section 2: Key Insights */}
              {insights.length > 0 && (
                <div className="drawer-section">
                  <div className="drawer-section-title flex items-center gap-2">
                    <FileText className="w-3.5 h-3.5" />
                    Key Insights
                  </div>
                  <div className="drawer-card">
                    <ul className="space-y-2">
                      {insights.map((insight, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-text-secondary">
                          <span className="text-primary-cyan mt-1">•</span>
                          <span>{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Section 3: Risk & Conflict */}
              <div className="drawer-section">
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className={`w-4 h-4 ${getRiskColor()}`} />
                    <span className="text-sm text-text-secondary">Risk:</span>
                    <span className={`text-sm font-medium ${getRiskColor()}`}>
                      {riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">🔥</span>
                    <span className="text-sm text-text-secondary">Conflict:</span>
                    <span className="text-sm font-medium text-text-primary">{conflictCount}</span>
                  </div>
                </div>
              </div>

              {/* Section 4: Timeline */}
              {timeline.length > 0 && (
                <div className="drawer-section">
                  <div className="drawer-section-title flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5" />
                    Timeline
                  </div>
                  <div className="relative pl-6">
                    {/* Timeline line */}
                    <div className="absolute left-2 top-2 bottom-2 w-px bg-[#1E293B]" />
                    {/* Timeline items */}
                    <div className="space-y-3">
                      {timeline.map((item, index) => (
                        <div key={index} className="relative flex items-start gap-3">
                          <div
                            className={`absolute -left-4 w-3 h-3 rounded-full border-2 border-[#1E293B] ${
                              item.status === 'completed'
                                ? 'bg-green-500'
                                : item.status === 'ongoing'
                                ? 'bg-primary-cyan animate-pulse'
                                : 'bg-[#334155]'
                            }`}
                          />
                          <div>
                            <p className="text-xs text-text-muted">{item.time}</p>
                            <p className="text-sm text-text-primary">{item.event}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Section 5: Consensus */}
              {consensus.length > 0 && (
                <div className="drawer-section">
                  <div className="drawer-section-title">Consensus</div>
                  <div className="flex flex-wrap gap-2">
                    {consensus.map((item, index) => (
                      <span
                        key={index}
                        className="px-3 py-1.5 text-xs font-medium bg-[#1E293B] rounded-full text-text-secondary border border-[#334155]"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        {onDetailView && (
          <div className="drawer-footer">
            <button
              onClick={onDetailView}
              className="w-full py-3 px-4 gradient-primary text-white font-medium rounded-lg
                hover:shadow-lg hover:shadow-primary-cyan/25 transition-all duration-200
                flex items-center justify-center gap-2"
            >
              View Full Analysis
              <span>→</span>
            </button>
          </div>
        )}
      </div>
    </>
  );
}
