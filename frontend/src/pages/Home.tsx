/**
 * Home.tsx
 *
 * 全屏地球 + 抽屉系统布局
 * 包含：右侧分析抽屉、左侧角色抽屉、底部事件抽屉、悬浮工具栏
 *
 * 设计方向：极简初始状态 + 抽屉展开 + 深色科技风格
 * 功能：页面加载时自动批量分析所有事件
 */
import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Globe, RefreshCw, X, AlertCircle, CheckCircle, Loader2, Play, Pause } from 'lucide-react';
import { api, WorldMonitorEvent, AnalysisResult, DebateResult, API_BASE_URL, analyzeReactionChain, ReactionChainResult } from '../services/api';
import GlobeMap from '../components/GlobeMap';
import ReactionChainView from '../components/analysis/ReactionChainView';

// 抽屉和工具栏组件
import FloatingToolbar from '../components/FloatingToolbar';
import RightDrawer from '../components/RightDrawer';
import LeftDrawer, { Role } from '../components/LeftDrawer';
import BottomDrawer, { Event } from '../components/BottomDrawer';

const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

// 分析状态类型
type AnalysisStatus = 'pending' | 'analyzing' | 'completed' | 'error';

// 事件分析状态映射
interface EventAnalysisState {
  eventId: string;
  status: AnalysisStatus;
  result?: AnalysisResult | DebateResult;
  error?: string;
}

// 批量分析进度
interface BatchAnalysisProgress {
  total: number;
  completed: number;
  current: string | null;
  isRunning: boolean;
}

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

  // 抽屉状态 - 极简初始状态：所有抽屉默认关闭
  const [rightDrawerOpen, setRightDrawerOpen] = useState(false);
  const [leftDrawerOpen, setLeftDrawerOpen] = useState(false);
  const [bottomDrawerOpen, setBottomDrawerOpen] = useState(false);

  // 角色数据
  const [roles] = useState<Role[]>(generateMockRoles());
  const [selectedRoleId, setSelectedRoleId] = useState<string>();

  // 反应链分析状态
  const [reactionChainResult, setReactionChainResult] = useState<ReactionChainResult | null>(null);
  const [reactionChainLoading, setReactionChainLoading] = useState(false);
  const [analysisMode, setAnalysisMode] = useState<'standard' | 'reaction_chain'>('standard');

  // Toast 状态
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' | 'info' } | null>(null);

  // 批量分析状态
  const [eventAnalysisStates, setEventAnalysisStates] = useState<Map<string, EventAnalysisState>>(new Map());
  const [batchProgress, setBatchProgress] = useState<BatchAnalysisProgress>({
    total: 0,
    completed: 0,
    current: null,
    isRunning: false
  });

  // 批量分析控制
  const batchAnalysisRef = useRef<{ abort: boolean }>({ abort: false });

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
      console.log('[Home] Fetched events:', fetchedEvents.length);
      if (fetchedEvents.length > 0) {
        console.log('[Home] Sample event location:', fetchedEvents[0]?.location);
      }
      setEvents(fetchedEvents);

      // 初始化所有事件的分析状态为 pending
      const newStates = new Map<string, EventAnalysisState>();
      fetchedEvents.forEach((event: WorldMonitorEvent) => {
        newStates.set(event.id, {
          eventId: event.id,
          status: 'pending'
        });
      });
      setEventAnalysisStates(newStates);

      // 极简初始状态：不自动选择事件
      // 用户需要主动点击地球或打开底部抽屉选择事件
    } catch (error) {
      console.error('Failed to load events:', error);
      showToast('Failed to load events. Please check your connection.', 'error');
    } finally {
      setEventsLoading(false);
      setIsRefreshing(false);
      setLastUpdate(new Date());
    }
  }, [showToast]);

  // 触发单个事件分析
  const triggerAnalysis = useCallback(async (event: WorldMonitorEvent) => {
    setAnalysisLoading(true);
    // 更新该事件的分析状态为 analyzing
    setEventAnalysisStates(prev => {
      const newMap = new Map(prev);
      const currentState = newMap.get(event.id);
      if (currentState) {
        newMap.set(event.id, { ...currentState, status: 'analyzing' });
      }
      return newMap;
    });

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

      // 更新该事件的分析状态为 completed
      setEventAnalysisStates(prev => {
        const newMap = new Map(prev);
        const currentState = newMap.get(event.id);
        if (currentState) {
          newMap.set(event.id, { ...currentState, status: 'completed', result });
        }
        return newMap;
      });

      sessionStorage.setItem('analysisResult', JSON.stringify(result));
      sessionStorage.setItem('selectedEvent', JSON.stringify(event));
    } catch (error) {
      console.error('Analysis failed:', error);
      setAnalysisResult(null);
      // 更新该事件的分析状态为 error
      setEventAnalysisStates(prev => {
        const newMap = new Map(prev);
        const currentState = newMap.get(event.id);
        if (currentState) {
          newMap.set(event.id, {
            ...currentState,
            status: 'error',
            error: error instanceof Error ? error.message : 'Analysis failed'
          });
        }
        return newMap;
      });
      showToast('Analysis failed. Please try again.', 'error');
    } finally {
      setAnalysisLoading(false);
    }
  }, [showToast]);

  // 触发反应链分析
  const triggerReactionChainAnalysis = useCallback(async (event: WorldMonitorEvent) => {
    setReactionChainLoading(true);

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
        max_rounds: 3,
        convergence_threshold: 0.85
      };

      const result = await analyzeReactionChain(request);
      setReactionChainResult(result);
      setAnalysisMode('reaction_chain');
      sessionStorage.setItem('reactionChainResult', JSON.stringify(result));
      showToast('Reaction chain analysis completed!', 'success');
    } catch (error) {
      console.error('Reaction chain analysis failed:', error);
      setReactionChainResult(null);
      showToast('Reaction chain analysis failed. Please try again.', 'error');
    } finally {
      setReactionChainLoading(false);
    }
  }, [showToast]);

  // 批量分析所有事件
  const startBatchAnalysis = useCallback(async () => {
    if (batchProgress.isRunning) return;

    // 获取所有待分析的事件（优先分析高严重度的）
    const pendingEvents = events
      .filter(e => {
        const state = eventAnalysisStates.get(e.id);
        return state?.status === 'pending' || state?.status === 'error';
      })
      .sort((a, b) => (b.severity || 3) - (a.severity || 3));

    if (pendingEvents.length === 0) {
      showToast('All events have been analyzed', 'info');
      return;
    }

    batchAnalysisRef.current.abort = false;
    setBatchProgress({
      total: events.length,
      completed: events.length - pendingEvents.length,
      current: null,
      isRunning: true
    });

    showToast(`Starting batch analysis of ${pendingEvents.length} events...`, 'info');

    for (let i = 0; i < pendingEvents.length; i++) {
      if (batchAnalysisRef.current.abort) {
        showToast('Batch analysis stopped', 'info');
        break;
      }

      const event = pendingEvents[i];
      setBatchProgress(prev => ({
        ...prev,
        current: event.title,
        completed: prev.completed
      }));

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

        // 更新状态为 analyzing
        setEventAnalysisStates(prev => {
          const newMap = new Map(prev);
          const currentState = newMap.get(event.id);
          if (currentState) {
            newMap.set(event.id, { ...currentState, status: 'analyzing' });
          }
          return newMap;
        });

        const result = await api.analyze({
          event_id: event.id,
          title: event.title,
          description: event.description,
          category: event.category,
          importance: event.severity || 3,
          timestamp: event.timestamp,
          roles: selectedRoles,
          depth: 'standard'
        });

        // 更新状态为 completed
        setEventAnalysisStates(prev => {
          const newMap = new Map(prev);
          const currentState = newMap.get(event.id);
          if (currentState) {
            newMap.set(event.id, { ...currentState, status: 'completed', result });
          }
          return newMap;
        });

        setBatchProgress(prev => ({
          ...prev,
          completed: prev.completed + 1
        }));
      } catch (error) {
        console.error(`Failed to analyze event ${event.id}:`, error);
        // 更新状态为 error
        setEventAnalysisStates(prev => {
          const newMap = new Map(prev);
          const currentState = newMap.get(event.id);
          if (currentState) {
            newMap.set(event.id, {
              ...currentState,
              status: 'error',
              error: error instanceof Error ? error.message : 'Analysis failed'
            });
          }
          return newMap;
        });

        setBatchProgress(prev => ({
          ...prev,
          completed: prev.completed + 1
        }));
      }

      // 添加短暂延迟避免请求过快
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    setBatchProgress(prev => ({
      ...prev,
      isRunning: false,
      current: null
    }));

    if (!batchAnalysisRef.current.abort) {
      showToast('Batch analysis completed!', 'success');
    }
  }, [events, eventAnalysisStates, batchProgress.isRunning, showToast]);

  // 停止批量分析
  const stopBatchAnalysis = useCallback(() => {
    batchAnalysisRef.current.abort = true;
    setBatchProgress(prev => ({
      ...prev,
      isRunning: false,
      current: null
    }));
  }, []);

  // 页面加载后自动开始批量分析
  useEffect(() => {
    if (events.length > 0 && !batchProgress.isRunning && batchProgress.completed === 0) {
      // 延迟 2 秒后自动开始批量分析，给用户时间看到初始界面
      const timer = setTimeout(() => {
        startBatchAnalysis();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [events.length]); // eslint-disable-line react-hooks/exhaustive-deps

  // 初始加载
  useEffect(() => {
    loadEvents();
    const interval = setInterval(loadEvents, AUTO_REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [loadEvents]);

  // 事件选择时触发分析（仅在用户主动点击时）
  // 不再自动打开右侧抽屉，保持极简状态
  useEffect(() => {
    if (selectedEvent) {
      const state = eventAnalysisStates.get(selectedEvent.id);
      // 如果该事件已有分析结果，直接使用
      if (state?.status === 'completed' && state.result) {
        setAnalysisResult(state.result);
      } else if (state?.status !== 'analyzing') {
        // 如果没有分析结果且不在分析中，则触发分析
        triggerAnalysis(selectedEvent);
      }
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
              {/* 批量分析进度 */}
              {batchProgress.isRunning && (
                <div className="flex items-center gap-3 px-3 py-1.5 bg-primary-cyan/10 border border-primary-cyan/20 rounded-lg">
                  <Loader2 className="w-4 h-4 text-primary-cyan animate-spin" />
                  <div className="text-xs">
                    <span className="text-primary-cyan font-medium">
                      {batchProgress.completed}/{batchProgress.total}
                    </span>
                    <span className="text-text-muted ml-1">analyzing...</span>
                  </div>
                  <button
                    onClick={stopBatchAnalysis}
                    className="p-1 hover:bg-primary-cyan/20 rounded transition-colors"
                    title="Stop analysis"
                  >
                    <Pause className="w-3 h-3 text-primary-cyan" />
                  </button>
                </div>
              )}

              {/* 分析完成统计 */}
              {!batchProgress.isRunning && batchProgress.completed > 0 && (
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-lg">
                  <CheckCircle className="w-4 h-4 text-green-400" />
                  <span className="text-xs text-green-400">
                    {batchProgress.completed}/{batchProgress.total} analyzed
                  </span>
                  <button
                    onClick={startBatchAnalysis}
                    className="p-1 hover:bg-green-500/20 rounded transition-colors ml-1"
                    title="Re-analyze remaining"
                  >
                    <Play className="w-3 h-3 text-green-400" />
                  </button>
                </div>
              )}

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
        {/* 分析模式切换 */}
        {selectedEvent && (
          <div className="mb-4 flex gap-2">
            <button
              onClick={() => setAnalysisMode('standard')}
              className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                analysisMode === 'standard'
                  ? 'bg-primary-cyan text-black'
                  : 'bg-[#1E293B] text-text-muted hover:text-text-primary'
              }`}
            >
              标准分析
            </button>
            <button
              onClick={() => {
                if (!reactionChainResult && selectedEvent) {
                  triggerReactionChainAnalysis(selectedEvent);
                }
                setAnalysisMode('reaction_chain');
                if (!rightDrawerOpen) setRightDrawerOpen(true);
              }}
              disabled={reactionChainLoading}
              className={`px-3 py-1.5 text-xs rounded-lg transition-colors flex items-center gap-1 ${
                analysisMode === 'reaction_chain'
                  ? 'bg-[#9c27b0] text-white'
                  : 'bg-[#1E293B] text-text-muted hover:text-text-primary'
              }`}
            >
              {reactionChainLoading ? (
                <>
                  <div className="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin" />
                  分析中...
                </>
              ) : (
                '🔗 反应链'
              )}
            </button>
          </div>
        )}

        {/* 加载状态 */}
        {(analysisLoading || reactionChainLoading) && (
          <div className="drawer-section">
            <div className="flex items-center justify-center py-8">
              <div className="flex flex-col items-center gap-3">
                <div className="w-10 h-10 border-3 border-primary-cyan/20 border-t-primary-cyan rounded-full animate-spin" />
                <p className="text-sm text-text-muted">
                  {reactionChainLoading ? 'Running reaction chain analysis...' : 'Analyzing...'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 反应链分析结果 */}
        {!analysisLoading && !reactionChainLoading && analysisMode === 'reaction_chain' && reactionChainResult && (
          <div className="max-h-[70vh] overflow-y-auto">
            <ReactionChainView result={reactionChainResult as any} />
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
        analysisStates={eventAnalysisStates}
        batchProgress={batchProgress}
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
