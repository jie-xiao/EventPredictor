/**
 * Home.tsx
 *
 * 全屏地球 + 抽屉系统布局
 * 包含：右侧分析抽屉、左侧角色抽屉、底部事件抽屉、悬浮工具栏
 */
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Globe, RefreshCw, X, AlertCircle, CheckCircle } from 'lucide-react';
import { api, WorldMonitorEvent, AnalysisResult, DebateResult, API_BASE_URL } from '../services/api';
import GlobeMap from '../components/GlobeMap';

// 抽屉和工具栏组件
import FloatingToolbar from '../components/FloatingToolbar';
import RightDrawer from '../components/RightDrawer';
import LeftDrawer, { Role } from '../components/LeftDrawer';
import BottomDrawer, { Event } from '../components/BottomDrawer';

const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

// Toast 组件
interface ToastProps {
  message: string;
  type: 'error' | 'success' | 'info';
  onClose: () => void;
}

function Toast({ message, type, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const bgColors = {
    error: 'bg-red-500/20 border-red-500/30',
    success: 'bg-green-500/20 border-green-500/30',
    info: 'bg-primary-cyan/20 border-primary-cyan/30'
  };

  const textColors = {
    error: 'text-red-400',
    success: 'text-green-400',
    info: 'text-primary-cyan'
  };

  const icons = {
    error: <AlertCircle className="w-5 h-5" />,
    success: <CheckCircle className="w-5 h-5" />,
    info: <AlertCircle className="w-5 h-5" />
  };

  return (
    <div className={`fixed top-4 right-4 z-[2000] flex items-center gap-3 px-4 py-3 rounded-lg border backdrop-blur-sm ${bgColors[type]} animate-slide-in`}>
      <span className={textColors[type]}>{icons[type]}</span>
      <span className="text-text-primary text-sm">{message}</span>
      <button onClick={onClose} className="ml-2 text-text-muted hover:text-text-primary">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

// 将 WorldMonitorEvent 转换为 BottomDrawer Event 格式
const convertToDrawerEvent = (event: WorldMonitorEvent): Event => ({
  id: event.id,
  title: event.title,
  severity: (event.severity || 3) as 1 | 2 | 3 | 4 | 5,
  location: event.location?.region || event.location?.country || '',
  timestamp: event.timestamp,
  category: event.category,
  description: event.description,
});

// 示例角色数据
const generateMockRoles = (): Role[] => [
  { id: 'cn_gov', name: 'Chinese Government', flag: '🇨🇳', type: 'government', stance: 'Maintaining sovereignty', confidence: 85 },
  { id: 'us_gov', name: 'US Government', flag: '🇺🇸', type: 'government', stance: 'Strategic engagement', confidence: 78 },
  { id: 'eu_gov', name: 'EU Government', flag: '🇪🇺', type: 'government', stance: 'Diplomatic resolution', confidence: 72 },
  { id: 'tech_giant', name: 'Tech Corporation', type: 'enterprise', stance: 'Market expansion', confidence: 65 },
  { id: 'financial_giant', name: 'Financial Institution', type: 'enterprise', stance: 'Risk management', confidence: 70 },
  { id: 'mainstream_media', name: 'Mainstream Media', type: 'media', stance: 'Balanced reporting', confidence: 60 },
  { id: 'intellectual', name: 'Academic Experts', type: 'public', stance: 'Evidence-based analysis', confidence: 75 },
  { id: 'common_public', name: 'General Public', type: 'public', stance: 'Concerned', confidence: 55 },
];

export default function Home() {
  const navigate = useNavigate();

  // 事件数据
  const [events, setEvents] = useState<WorldMonitorEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<WorldMonitorEvent | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | DebateResult | null>(null);

  // 加载状态
  const [eventsLoading, setEventsLoading] = useState(true);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // 时间状态
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [timeNow, setTimeNow] = useState(new Date());

  // 抽屉状态
  const [rightDrawerOpen, setRightDrawerOpen] = useState(false);
  const [leftDrawerOpen, setLeftDrawerOpen] = useState(false);
  const [bottomDrawerOpen, setBottomDrawerOpen] = useState(false);

  // 角色数据
  const [roles] = useState<Role[]>(generateMockRoles());
  const [selectedRoleId, setSelectedRoleId] = useState<string>();

  // Toast 状态
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' | 'info' } | null>(null);

  const showToast = useCallback((message: string, type: 'error' | 'success' | 'info' = 'info') => {
    setToast({ message, type });
  }, []);

  // 更新时钟
  useEffect(() => {
    const timer = setInterval(() => setTimeNow(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // 加载事件
  const loadEvents = useCallback(async () => {
    setEventsLoading(true);
    setIsRefreshing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/data/events?limit=50&time_range=all`);
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      const data = await response.json();
      const fetchedEvents = data.events || [];
      setEvents(fetchedEvents);

      // 自动选择最严重的事件
      const eventsWithLocation = fetchedEvents.filter(
        (e: WorldMonitorEvent) => e.location?.lat && e.location?.lon
      );

      if (eventsWithLocation.length > 0) {
        eventsWithLocation.sort((a: WorldMonitorEvent, b: WorldMonitorEvent) =>
          (b.severity || 3) - (a.severity || 3)
        );
        const topEvent = eventsWithLocation[0];
        if (!selectedEvent || selectedEvent.id !== topEvent.id) {
          setSelectedEvent(topEvent);
        }
      }
    } catch (error) {
      console.error('Failed to load events:', error);
      showToast('Failed to load events. Please check your connection.', 'error');
    } finally {
      setEventsLoading(false);
      setIsRefreshing(false);
      setLastUpdate(new Date());
    }
  }, [selectedEvent, showToast]);

  // 触发分析
  const triggerAnalysis = useCallback(async (event: WorldMonitorEvent) => {
    setAnalysisLoading(true);
    try {
      const categoryRoleMap: Record<string, string[]> = {
        'Monetary Policy': ['cn_gov', 'us_gov', 'institutional_investor', 'retail_investor'],
        'Geopolitical': ['cn_gov', 'us_gov', 'eu_gov', 'mainstream_media'],
        'Economic': ['institutional_investor', 'financial_giant', 'intellectual', 'mainstream_media'],
        'Technology': ['tech_giant', 'intellectual', 'venture_capitalist', 'social_media'],
        'Trade': ['cn_gov', 'us_gov', 'tech_giant', 'financial_giant'],
        'Social': ['common_public', 'intellectual', 'netizen', 'mainstream_media'],
        'default': ['cn_gov', 'us_gov', 'institutional_investor', 'intellectual', 'mainstream_media']
      };

      const selectedRoles = categoryRoleMap[event.category] || categoryRoleMap.default;

      const request = {
        event_id: event.id,
        title: event.title,
        description: event.description,
        category: event.category,
        importance: event.severity || 3,
        timestamp: event.timestamp,
        roles: selectedRoles,
        depth: 'standard'
      };

      const result = await api.analyze(request);
      setAnalysisResult(result);

      sessionStorage.setItem('analysisResult', JSON.stringify(result));
      sessionStorage.setItem('selectedEvent', JSON.stringify(event));
    } catch (error) {
      console.error('Analysis failed:', error);
      setAnalysisResult(null);
      showToast('Analysis failed. Please try again.', 'error');
    } finally {
      setAnalysisLoading(false);
    }
  }, [showToast]);

  // 初始加载
  useEffect(() => {
    loadEvents();
    const interval = setInterval(loadEvents, AUTO_REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [loadEvents]);

  // 事件选择时触发分析
  useEffect(() => {
    if (selectedEvent) {
      triggerAnalysis(selectedEvent);
      // 自动打开右侧抽屉显示分析结果
      setRightDrawerOpen(true);
    }
  }, [selectedEvent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  // 事件点击处理
  const handleEventClick = (event: WorldMonitorEvent) => {
    setSelectedEvent(event);
    sessionStorage.setItem('selectedEvent', JSON.stringify(event));
  };

  // 抽屉事件选择处理
  const handleDrawerEventSelect = (event: Event) => {
    const originalEvent = events.find(e => e.id === event.id);
    if (originalEvent) {
      handleEventClick(originalEvent);
    }
  };

  // 角色选择处理
  const handleRoleSelect = (role: Role) => {
    setSelectedRoleId(role.id);
  };

  // 查看详情
  const handleDetailView = () => {
    if (selectedEvent) {
      navigate('/analysis');
    }
  };

  // 统计数据
  const stats = {
    total: events.length,
    critical: events.filter(e => (e.severity || 3) >= 4).length,
    warning: events.filter(e => (e.severity || 3) === 3).length,
    normal: events.filter(e => (e.severity || 3) < 3).length,
  };

  // 从分析结果中提取洞察
  const extractInsights = (): string[] => {
    if (!analysisResult) return [];

    // 从 prediction.key_insights 提取
    if (analysisResult.prediction?.key_insights) {
      return analysisResult.prediction.key_insights.slice(0, 3);
    }

    // 从 cross_analysis.consensus 提取
    if (analysisResult.cross_analysis?.consensus) {
      return analysisResult.cross_analysis.consensus.slice(0, 3);
    }

    return [];
  };

  // 从分析结果中提取趋势
  const extractTrend = (): 'up' | 'down' | 'neutral' => {
    if (!analysisResult) return 'neutral';

    if (analysisResult.prediction?.trend) {
      const trend = analysisResult.prediction.trend.toLowerCase();
      if (trend === 'up' || trend === 'rising') return 'up';
      if (trend === 'down' || trend === 'falling') return 'down';
    }

    return 'neutral';
  };

  // 获取置信度
  const getConfidence = (): number => {
    if (!analysisResult) return 75;
    if (analysisResult.prediction?.confidence) {
      return analysisResult.prediction.confidence;
    }
    if (analysisResult.overall_confidence) {
      return analysisResult.overall_confidence;
    }
    return 75;
  };

  // 获取冲突数
  const getConflictCount = (): number => {
    if (!analysisResult) return 0;
    if (analysisResult.cross_analysis?.conflicts) {
      return analysisResult.cross_analysis.conflicts.length;
    }
    if ('key_conflicts' in analysisResult && analysisResult.key_conflicts) {
      return analysisResult.key_conflicts.length;
    }
    return 0;
  };

  // 获取共识点
  const getConsensusPoints = (): string[] => {
    if (!analysisResult) return [];
    if ('consensus_points' in analysisResult && analysisResult.consensus_points) {
      return analysisResult.consensus_points;
    }
    if (analysisResult.cross_analysis?.consensus) {
      return analysisResult.cross_analysis.consensus;
    }
    return [];
  };

  // 获取风险级别
  const getRiskLevel = (): 'high' | 'medium' | 'low' => {
    if (!selectedEvent) return 'low';
    const severity = selectedEvent.severity || 3;
    if (severity >= 4) return 'high';
    if (severity === 3) return 'medium';
    return 'low';
  };

  return (
    <div className="min-h-screen bg-background-dark text-text-primary font-sans">
      {/* 背景效果 */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(0,229,255,0.05),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,rgba(0,119,255,0.05),transparent_50%)]" />
        <div className="absolute inset-0 opacity-30 bg-[linear-gradient(rgba(0,229,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,229,255,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />
        <div className="absolute inset-0 bg-gradient-flow" />
      </div>

      <div className="relative z-10 flex flex-col h-screen">
        {/* Header - 48px */}
        <header className="flex-shrink-0 border-b border-b-[#1E293B] bg-[#0A0E1A]/90 backdrop-blur-xl h-[48px]">
          <div className="h-full px-6 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-cyan to-primary-blue flex items-center justify-center shadow-glow-cyan">
                    <Globe className="w-4 h-4 text-white" />
                  </div>
                  <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-[#10B981] rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                </div>
                <div>
                  <h1 className="text-[16px] font-bold text-text-primary">
                    Global Situation Prediction
                  </h1>
                </div>
              </div>

              <div className="h-6 w-px bg-[#1E293B]" />

              <div className="flex items-center gap-4">
                <div className="text-center">
                  <p className="text-sm font-mono text-text-primary">{stats.total}</p>
                  <p className="text-[9px] text-text-muted uppercase tracking-wider">Events</p>
                </div>
                <div className="w-px h-6 bg-[#1E293B]" />
                <div className="text-center">
                  <p className="text-sm font-mono text-[#EF4444]">{stats.critical}</p>
                  <p className="text-[9px] text-[#EF4444]/70 uppercase tracking-wider">Critical</p>
                </div>
                <div className="w-px h-6 bg-[#1E293B]" />
                <div className="text-center">
                  <p className="text-sm font-mono text-[#F59E0B]">{stats.warning}</p>
                  <p className="text-[9px] text-[#F59E0B]/70 uppercase tracking-wider">Warning</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-4">
                <div className="text-center">
                  <p className="text-[9px] text-text-muted uppercase tracking-wider">System</p>
                  <p className="text-xs font-mono text-primary-cyan">
                    {timeNow.toLocaleTimeString('zh-CN', { hour12: false })}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-[9px] text-text-muted uppercase tracking-wider">Updated</p>
                  <p className="text-xs font-mono text-text-secondary">
                    {lastUpdate.toLocaleTimeString('zh-CN', { hour12: false })}
                  </p>
                </div>
              </div>

              <button
                onClick={loadEvents}
                disabled={eventsLoading}
                className="p-2 bg-[#1E293B]/50 hover:bg-[#1E293B] rounded-lg transition-all disabled:opacity-50 border border-[#1E293B]"
                title="Refresh Data"
              >
                <RefreshCw className={`w-4 h-4 ${eventsLoading ? 'animate-spin' : ''} text-primary-cyan`} />
              </button>
            </div>
          </div>
        </header>

        {/* 主内容区 - 全屏地球 */}
        <div className="flex-1 relative">
          {eventsLoading && events.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="flex flex-col items-center gap-4">
                <div className="relative animate-breathe">
                  <div className="w-20 h-20 border-4 border-primary-cyan/20 border-t-primary-cyan rounded-full animate-spin" />
                  <div
                    className="absolute inset-2 w-16 h-16 border-4 border-primary-blue/20 border-b-primary-blue rounded-full animate-spin"
                    style={{ animationDirection: 'reverse' }}
                  />
                </div>
                <p className="text-primary-cyan font-medium animate-pulse">Loading global data...</p>
              </div>
            </div>
          ) : (
            <GlobeMap
              events={events}
              selectedEvent={selectedEvent}
              onEventClick={handleEventClick}
            />
          )}
        </div>
      </div>

      {/* 抽屉组件 */}
      <RightDrawer
        isOpen={rightDrawerOpen}
        onClose={() => setRightDrawerOpen(false)}
        title={selectedEvent?.title || 'Analysis'}
        trend={extractTrend()}
        confidence={getConfidence()}
        insights={extractInsights()}
        riskLevel={getRiskLevel()}
        conflictCount={getConflictCount()}
        consensus={getConsensusPoints()}
        onDetailView={handleDetailView}
      >
        {/* 加载状态 */}
        {analysisLoading && (
          <div className="drawer-section">
            <div className="flex items-center justify-center py-8">
              <div className="flex flex-col items-center gap-3">
                <div className="w-10 h-10 border-3 border-primary-cyan/20 border-t-primary-cyan rounded-full animate-spin" />
                <p className="text-sm text-text-muted">Analyzing...</p>
              </div>
            </div>
          </div>
        )}
      </RightDrawer>

      <LeftDrawer
        isOpen={leftDrawerOpen}
        onClose={() => setLeftDrawerOpen(false)}
        roles={roles}
        selectedRoleId={selectedRoleId}
        onRoleSelect={handleRoleSelect}
      />

      <BottomDrawer
        isOpen={bottomDrawerOpen}
        onToggle={() => setBottomDrawerOpen(!bottomDrawerOpen)}
        events={events.map(convertToDrawerEvent)}
        selectedEventId={selectedEvent?.id}
        onEventSelect={handleDrawerEventSelect}
        onClose={() => setBottomDrawerOpen(false)}
      />

      {/* 悬浮工具栏 */}
      <FloatingToolbar
        onToggleRightDrawer={() => setRightDrawerOpen(!rightDrawerOpen)}
        onToggleLeftDrawer={() => setLeftDrawerOpen(!leftDrawerOpen)}
        onToggleBottomDrawer={() => setBottomDrawerOpen(!bottomDrawerOpen)}
        onRefresh={loadEvents}
        rightDrawerOpen={rightDrawerOpen}
        leftDrawerOpen={leftDrawerOpen}
        bottomDrawerOpen={bottomDrawerOpen}
        isRefreshing={isRefreshing}
      />

      {/* Toast 通知 */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
