// 事件监控面板 - 世界一流UI设计
import React, { useState, useEffect, useCallback } from 'react';
import { 
  Bell, AlertTriangle, CheckCircle, RefreshCw, Settings, Shield, 
  Activity, Clock, Filter, X, Zap, Target, TrendingUp
} from 'lucide-react';

// ============ 类型定义 ============
interface AlertRule {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  severity: string;
  field: string;
  operator: string;
  value: string;
  cooldown_minutes: number;
  created_at: string;
  last_triggered?: string;
}

interface Alert {
  id: string;
  rule_id: string;
  rule_name: string;
  severity: string;
  event_data: Record<string, any>;
  message: string;
  created_at: string;
  acknowledged: boolean;
}

interface MonitorStats {
  total_rules: number;
  enabled_rules: number;
  total_alerts: number;
  unacknowledged_alerts: number;
  websocket_connections: number;
}

// ============ 世界一流UI配置 ============
const THEME = {
  primary: '#00E5FF',
  primaryLight: '#67E8F9',
  background: '#0A0E1A',
  surface: '#111827',
  surfaceElevated: '#1F2937',
  border: '#374151',
  text: '#F9FAFB',
  textSecondary: '#9CA3AF',
  textMuted: '#6B7280',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
};

// 严重程度配色 - 渐变效果
const SEVERITY_CONFIG: Record<string, { bg: string; border: string; text: string; glow: string; icon: string }> = {
  critical: { 
    bg: 'linear-gradient(135deg, rgba(220,38,38,0.2) 0%, rgba(185,28,28,0.2) 100%)', 
    border: '#DC2626', 
    text: '#FCA5A5',
    glow: 'rgba(220,38,38,0.3)',
    icon: '🔥'
  },
  high: { 
    bg: 'linear-gradient(135deg, rgba(249,115,22,0.2) 0%, rgba(180,83,9,0.2) 100%)', 
    border: '#F97316', 
    text: '#FDBA74',
    glow: 'rgba(249,115,22,0.3)',
    icon: '⚠️'
  },
  medium: { 
    bg: 'linear-gradient(135deg, rgba(234,179,8,0.2) 0%, rgba(161,98,7,0.2) 100%)', 
    border: '#EAB308', 
    text: '#FDE047',
    glow: 'rgba(234,179,8,0.3)',
    icon: '⚡'
  },
  low: { 
    bg: 'linear-gradient(135deg, rgba(59,130,246,0.2) 0%, rgba(29,78,216,0.2) 100%)', 
    border: '#3B82F6', 
    text: '#93C5FD',
    glow: 'rgba(59,130,246,0.3)',
    icon: '💧'
  },
};

const getSeverityConfig = (severity: string) => SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.low;

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days}天前`;
  if (hours > 0) return `${hours}小时前`;
  if (minutes > 0) return `${minutes}分钟前`;
  return '刚刚';
};

// ============ 主组件 ============
const MonitorPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'alerts' | 'rules' | 'stats'>('alerts');
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [stats, setStats] = useState<MonitorStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState<string>('');

  // 加载数据
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [alertsRes, rulesRes, statsRes] = await Promise.all([
        fetch('http://127.0.0.1:8005/api/v1/monitor/alerts?limit=50'),
        fetch('http://127.0.0.1:8005/api/v1/monitor/rules'),
        fetch('http://127.0.0.1:8005/api/v1/monitor/statistics'),
      ]);

      const [alertsData, rulesData, statsData] = await Promise.all([
        alertsRes.json(),
        rulesRes.json(),
        statsRes.json(),
      ]);

      if (alertsData.success) setAlerts(alertsData.data.alerts);
      if (rulesData.success) setRules(rulesData.data);
      if (statsData.success) setStats(statsData.data);
    } catch (err) { console.error('Load error:', err); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  // 确认告警
  const acknowledgeAlert = async (alertId: string) => {
    try {
      await fetch(`http://127.0.0.1:8005/api/v1/monitor/alerts/${alertId}/acknowledge`, { method: 'POST' });
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, acknowledged: true } : a));
    } catch (err) { console.error('Ack error:', err); }
  };

  // 切换规则
  const toggleRule = async (ruleId: string, enabled: boolean) => {
    try {
      await fetch(`http://127.0.0.1:8005/api/v1/monitor/rules/${ruleId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      });
      setRules(rules.map(r => r.id === ruleId ? { ...r, enabled } : r));
    } catch (err) { console.error('Toggle error:', err); }
  };

  const filteredAlerts = filterSeverity ? alerts.filter(a => a.severity === filterSeverity) : alerts;

  // Tab配置
  const tabs = [
    { id: 'alerts', label: '告警', icon: Bell, badge: stats?.unacknowledged_alerts || 0 },
    { id: 'rules', label: '规则', icon: Settings, badge: 0 },
    { id: 'stats', label: '统计', icon: Activity, badge: 0 },
  ] as const;

  return (
    <div className="h-full flex flex-col" style={{ background: THEME.background }}>
      {/* Tab导航 - 玻璃拟态 */}
      <div 
        className="flex items-center border-b"
        style={{ 
          background: 'linear-gradient(180deg, rgba(31,41,55,0.95) 0%, rgba(17,24,39,0.98) 100%)',
          borderColor: THEME.border,
          backdropFilter: 'blur(12px)',
        }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className="relative flex items-center gap-2 px-5 py-3.5 text-sm font-medium transition-all duration-200"
            style={{
              color: activeTab === tab.id ? THEME.primary : THEME.textSecondary,
              borderBottom: activeTab === tab.id ? `2px solid ${THEME.primary}` : '2px solid transparent',
            }}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
            {tab.badge > 0 && activeTab === 'alerts' && (
              <span 
                className="px-1.5 py-0.5 text-xs font-bold rounded-full animate-pulse"
                style={{ 
                  background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)', 
                  color: 'white',
                  boxShadow: '0 2px 8px rgba(239,68,68,0.4)',
                }}
              >
                {tab.badge}
              </span>
            )}
          </button>
        ))}
        
        <div className="flex-1" />
        
        <button
          onClick={loadData}
          disabled={loading}
          className="mr-4 p-2 rounded-lg transition-all duration-200 hover:scale-105"
          style={{ 
            background: THEME.surfaceElevated, 
            color: THEME.textSecondary,
          }}
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-auto p-5">
        {activeTab === 'alerts' && (
          <div className="space-y-4">
            {/* 过滤栏 */}
            <div className="flex items-center gap-3 mb-6">
              <Filter className="w-4 h-4" style={{ color: THEME.textMuted }} />
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="px-4 py-2 rounded-xl text-sm transition-all duration-200"
                style={{ 
                  background: THEME.surfaceElevated, 
                  border: `1px solid ${THEME.border}`,
                  color: THEME.text,
                }}
              >
                <option value="">全部级别</option>
                <option value="critical">🔴 严重</option>
                <option value="high">🟠 高</option>
                <option value="medium">🟡 中</option>
                <option value="low">🔵 低</option>
              </select>
              
              <span className="text-sm" style={{ color: THEME.textMuted }}>
                共 {filteredAlerts.length} 条告警
              </span>
            </div>

            {/* 告警列表 */}
            {filteredAlerts.length === 0 ? (
              <div 
                className="flex flex-col items-center justify-center py-20 rounded-2xl"
                style={{ background: 'rgba(31,41,55,0.3)', border: `1px dashed ${THEME.border}` }}
              >
                <div className="w-20 h-20 rounded-2xl flex items-center justify-center mb-4" style={{ background: 'rgba(16,185,129,0.1)' }}>
                  <CheckCircle className="w-10 h-10" style={{ color: THEME.success }} />
                </div>
                <p className="text-lg font-medium" style={{ color: THEME.textSecondary }}>暂无告警</p>
                <p className="text-sm mt-1" style={{ color: THEME.textMuted }}>系统运行平稳</p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredAlerts.map((alert) => {
                  const severity = getSeverityConfig(alert.severity);
                  return (
                    <div
                      key={alert.id}
                      className="relative p-4 rounded-xl transition-all duration-300 hover:scale-[1.01]"
                      style={{ 
                        background: alert.acknowledged 
                          ? 'rgba(31,41,55,0.5)' 
                          : severity.bg,
                        border: `1px solid ${alert.acknowledged ? THEME.border : severity.border}`,
                        boxShadow: alert.acknowledged ? 'none' : `0 4px 20px ${severity.glow}`,
                      }}
                    >
                      {!alert.acknowledged && (
                        <div 
                          className="absolute left-0 top-0 bottom-0 w-1 rounded-l-xl"
                          style={{ background: severity.border }}
                        />
                      )}
                      
                      <div className="flex items-start justify-between">
                        <div className="flex items-start gap-4">
                          <div 
                            className="w-10 h-10 rounded-xl flex items-center justify-center text-lg"
                            style={{ background: severity.bg, border: `1px solid ${severity.border}` }}
                          >
                            {severity.icon}
                          </div>
                          
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-semibold" style={{ color: alert.acknowledged ? THEME.textSecondary : THEME.text }}>
                                {alert.rule_name}
                              </h4>
                              <span 
                                className="px-2 py-0.5 text-xs rounded-md font-medium uppercase"
                                style={{ 
                                  background: severity.bg, 
                                  color: severity.text,
                                  border: `1px solid ${severity.border}`,
                                }}
                              >
                                {alert.severity}
                              </span>
                            </div>
                            <p className="mt-1.5 text-sm" style={{ color: THEME.textSecondary }}>
                              {alert.message}
                            </p>
                            <div className="flex items-center gap-3 mt-2 text-xs" style={{ color: THEME.textMuted }}>
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {formatTime(alert.created_at)}
                              </span>
                              {alert.event_data?.source && (
                                <span>来源: {alert.event_data.source}</span>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {!alert.acknowledged && (
                          <button
                            onClick={() => acknowledgeAlert(alert.id)}
                            className="p-2 rounded-lg transition-all duration-200 hover:scale-110"
                            style={{ 
                              background: 'rgba(16,185,129,0.2)', 
                              color: THEME.success,
                              border: `1px solid ${THEME.success}`,
                            }}
                            title="确认已处理"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* 规则列表 */}
        {activeTab === 'rules' && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {rules.map((rule) => {
              const severity = getSeverityConfig(rule.severity);
              return (
                <div
                  key={rule.id}
                  className="p-5 rounded-2xl transition-all duration-300 hover:scale-[1.02]"
                  style={{ 
                    background: 'linear-gradient(180deg, rgba(31,41,55,0.8) 0%, rgba(17,24,39,0.9) 100%)',
                    border: `1px solid ${rule.enabled ? severity.border : THEME.border}`,
                    boxShadow: rule.enabled ? `0 4px 16px ${severity.glow}` : 'none',
                  }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => toggleRule(rule.id, !rule.enabled)}
                        className="relative w-11 h-6 rounded-full transition-all duration-300"
                        style={{ 
                          background: rule.enabled 
                            ? 'linear-gradient(135deg, #00E5FF 0%, #06B6D4 100%)' 
                            : THEME.surfaceElevated,
                          boxShadow: rule.enabled ? '0 2px 8px rgba(0,229,255,0.4)' : 'none',
                        }}
                      >
                        <div 
                          className="absolute top-1 w-4 h-4 rounded-full bg-white transition-all duration-300 shadow-lg"
                          style={{ 
                            left: rule.enabled ? '26px' : '4px',
                          }}
                        />
                      </button>
                      <h4 className="font-semibold" style={{ color: THEME.text }}>{rule.name}</h4>
                    </div>
                    <span 
                      className="px-2 py-0.5 text-xs rounded-md"
                      style={{ 
                        background: severity.bg, 
                        color: severity.text,
                        border: `1px solid ${severity.border}`,
                      }}
                    >
                      {rule.severity}
                    </span>
                  </div>
                  
                  <p className="text-sm mb-4" style={{ color: THEME.textSecondary }}>
                    {rule.description || `${rule.field} ${rule.operator} "${rule.value}"`}
                  </p>
                  
                  <div className="flex items-center justify-between text-xs" style={{ color: THEME.textMuted }}>
                    <span className="flex items-center gap-1">
                      <Zap className="w-3 h-3" />
                      冷却 {rule.cooldown_minutes}分钟
                    </span>
                    <span className={rule.enabled ? 'text-green-400' : 'text-gray-500'}>
                      {rule.enabled ? '● 运行中' : '○ 已禁用'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* 统计面板 */}
        {activeTab === 'stats' && stats && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* 总规则 */}
            <div 
              className="p-6 rounded-2xl relative overflow-hidden"
              style={{ 
                background: 'linear-gradient(135deg, rgba(59,130,246,0.15) 0%, rgba(29,78,216,0.15) 100%)',
                border: `1px solid rgba(59,130,246,0.3)`,
              }}
            >
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl" style={{ background: 'rgba(59,130,246,0.2)' }} />
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 rounded-xl" style={{ background: 'rgba(59,130,246,0.2)' }}>
                    <Shield className="w-6 h-6" style={{ color: '#3B82F6' }} />
                  </div>
                  <span className="text-sm" style={{ color: THEME.textSecondary }}>总规则</span>
                </div>
                <p className="text-4xl font-bold" style={{ color: THEME.text }}>{stats.total_rules}</p>
              </div>
            </div>

            {/* 已启用 */}
            <div 
              className="p-6 rounded-2xl relative overflow-hidden"
              style={{ 
                background: 'linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(5,150,105,0.15) 100%)',
                border: `1px solid rgba(16,185,129,0.3)`,
              }}
            >
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl" style={{ background: 'rgba(16,185,129,0.2)' }} />
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 rounded-xl" style={{ background: 'rgba(16,185,129,0.2)' }}>
                    <Target className="w-6 h-6" style={{ color: THEME.success }} />
                  </div>
                  <span className="text-sm" style={{ color: THEME.textSecondary }}>已启用</span>
                </div>
                <p className="text-4xl font-bold" style={{ color: THEME.text }}>{stats.enabled_rules}</p>
              </div>
            </div>

            {/* 总告警 */}
            <div 
              className="p-6 rounded-2xl relative overflow-hidden"
              style={{ 
                background: 'linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(185,28,28,0.15) 100%)',
                border: `1px solid rgba(239,68,68,0.3)`,
              }}
            >
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl" style={{ background: 'rgba(239,68,68,0.2)' }} />
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 rounded-xl" style={{ background: 'rgba(239,68,68,0.2)' }}>
                    <AlertTriangle className="w-6 h-6" style={{ color: THEME.error }} />
                  </div>
                  <span className="text-sm" style={{ color: THEME.textSecondary }}>总告警</span>
                </div>
                <p className="text-4xl font-bold" style={{ color: THEME.text }}>{stats.total_alerts}</p>
              </div>
            </div>

            {/* 未确认 */}
            <div 
              className="p-6 rounded-2xl relative overflow-hidden"
              style={{ 
                background: 'linear-gradient(135deg, rgba(249,115,22,0.15) 0%, rgba(180,83,9,0.15) 100%)',
                border: `1px solid rgba(249,115,22,0.3)`,
              }}
            >
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl" style={{ background: 'rgba(249,115,22,0.2)' }} />
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 rounded-xl" style={{ background: 'rgba(249,115,22,0.2)' }}>
                    <Bell className="w-6 h-6" style={{ color: THEME.warning }} />
                  </div>
                  <span className="text-sm" style={{ color: THEME.textSecondary }}>待确认</span>
                </div>
                <p className="text-4xl font-bold" style={{ color: THEME.text }}>{stats.unacknowledged_alerts}</p>
              </div>
            </div>

            {/* WebSocket连接 */}
            <div 
              className="p-6 rounded-2xl relative overflow-hidden md:col-span-2"
              style={{ 
                background: 'linear-gradient(135deg, rgba(168,85,247,0.15) 0%, rgba(126,34,206,0.15) 100%)',
                border: `1px solid rgba(168,85,247,0.3)`,
              }}
            >
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl" style={{ background: 'rgba(168,85,247,0.2)' }} />
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 rounded-xl" style={{ background: 'rgba(168,85,247,0.2)' }}>
                    <TrendingUp className="w-6 h-6" style={{ color: '#A855F7' }} />
                  </div>
                  <span className="text-sm" style={{ color: THEME.textSecondary }}>WebSocket 连接</span>
                </div>
                <p className="text-4xl font-bold" style={{ color: THEME.text }}>{stats.websocket_connections}</p>
                <p className="text-sm mt-2" style={{ color: THEME.textMuted }}>实时推送连接数</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MonitorPanel;
