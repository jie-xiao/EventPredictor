// 事件监控面板组件
import React, { useState, useEffect } from 'react';
import { 
  Bell, AlertTriangle, CheckCircle, Trash2, RefreshCw, 
  Plus, Settings, Shield, Activity, Clock, Filter
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

// ============ 工具函数 ============
const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical': return 'bg-red-600';
    case 'high': return 'bg-orange-500';
    case 'medium': return 'bg-yellow-500';
    case 'low': return 'bg-blue-500';
    default: return 'bg-gray-500';
  }
};

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
  const loadData = async () => {
    setLoading(true);
    try {
      // 加载告警
      const alertsRes = await fetch('http://127.0.0.1:8005/api/v1/monitor/alerts?limit=50');
      const alertsData = await alertsRes.json();
      if (alertsData.success) {
        setAlerts(alertsData.data.alerts);
      }

      // 加载规则
      const rulesRes = await fetch('http://127.0.0.1:8005/api/v1/monitor/rules');
      const rulesData = await rulesRes.json();
      if (rulesData.success) {
        setRules(rulesData.data);
      }

      // 加载统计
      const statsRes = await fetch('http://127.0.0.1:8005/api/v1/monitor/statistics');
      const statsData = await statsRes.json();
      if (statsData.success) {
        setStats(statsData.data);
      }
    } catch (err) {
      console.error('Load monitor data error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // 定时刷新
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  // 确认告警
  const acknowledgeAlert = async (alertId: string) => {
    try {
      await fetch(`http://127.0.0.1:8005/api/v1/monitor/alerts/${alertId}/acknowledge`, {
        method: 'POST',
      });
      setAlerts(alerts.map(a => 
        a.id === alertId ? { ...a, acknowledged: true } : a
      ));
    } catch (err) {
      console.error('Acknowledge error:', err);
    }
  };

  // 切换规则启用状态
  const toggleRule = async (ruleId: string, enabled: boolean) => {
    try {
      await fetch(`http://127.0.0.1:8005/api/v1/monitor/rules/${ruleId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled }),
      });
      setRules(rules.map(r => 
        r.id === ruleId ? { ...r, enabled } : r
      ));
    } catch (err) {
      console.error('Toggle rule error:', err);
    }
  };

  // 过滤告警
  const filteredAlerts = filterSeverity
    ? alerts.filter(a => a.severity === filterSeverity)
    : alerts;

  return (
    <div className="monitor-panel">
      {/* 标签页导航 */}
      <div className="flex border-b border-[#334155] bg-[#1E293B]">
        <button
          onClick={() => setActiveTab('alerts')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'alerts' 
              ? 'text-[#00E5FF] border-b-2 border-[#00E5FF]' 
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Bell className="w-4 h-4" />
          告警
          {stats && stats.unacknowledged_alerts > 0 && (
            <span className="px-1.5 py-0.5 text-xs bg-red-500 text-white rounded-full">
              {stats.unacknowledged_alerts}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('rules')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'rules' 
              ? 'text-[#00E5FF] border-b-2 border-[#00E5FF]' 
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Settings className="w-4 h-4" />
          规则
        </button>
        <button
          onClick={() => setActiveTab('stats')}
          className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
            activeTab === 'stats' 
              ? 'text-[#00E5FF] border-b-2 border-[#00E5FF]' 
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Activity className="w-4 h-4" />
          统计
        </button>
        <div className="flex-1" />
        <button
          onClick={loadData}
          disabled={loading}
          className="px-4 py-2 text-gray-400 hover:text-white disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* 告警列表 */}
      {activeTab === 'alerts' && (
        <div className="p-4 space-y-3">
          {/* 过滤栏 */}
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              className="bg-[#0F172A] border border-[#334155] rounded px-3 py-1 text-sm text-white"
            >
              <option value="">全部级别</option>
              <option value="critical">严重</option>
              <option value="high">高</option>
              <option value="medium">中</option>
              <option value="low">低</option>
            </select>
          </div>

          {filteredAlerts.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              <CheckCircle className="w-12 h-12 mx-auto mb-3 opacity-50" />
              暂无告警
            </div>
          ) : (
            filteredAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`p-3 rounded-lg border ${
                  alert.acknowledged 
                    ? 'bg-[#1E293B] border-[#334155]' 
                    : 'bg-[#1E293B] border-l-4 border-l-red-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    <span className={`px-2 py-0.5 text-xs rounded ${getSeverityColor(alert.severity)} text-white`}>
                      {alert.severity}
                    </span>
                    <div>
                      <h4 className="text-white font-medium">{alert.rule_name}</h4>
                      <p className="text-gray-400 text-sm mt-1">{alert.message}</p>
                      <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatTime(alert.created_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                  {!alert.acknowledged && (
                    <button
                      onClick={() => acknowledgeAlert(alert.id)}
                      className="p-1.5 text-gray-400 hover:text-[#00E5FF] hover:bg-[#334155] rounded"
                      title="确认"
                    >
                      <CheckCircle className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* 规则列表 */}
      {activeTab === 'rules' && (
        <div className="p-4 space-y-3">
          {rules.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
              暂无规则
            </div>
          ) : (
            rules.map((rule) => (
              <div
                key={rule.id}
                className="p-3 rounded-lg bg-[#1E293B] border border-[#334155]"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <button
                      onClick={() => toggleRule(rule.id, !rule.enabled)}
                      className={`w-10 h-5 rounded-full transition-colors ${
                        rule.enabled ? 'bg-[#00E5FF]' : 'bg-gray-600'
                      }`}
                    >
                      <div className={`w-4 h-4 rounded-full bg-white transition-transform ${
                        rule.enabled ? 'translate-x-5' : 'translate-x-0.5'
                      }`} />
                    </button>
                    <div>
                      <h4 className="text-white font-medium">{rule.name}</h4>
                      <p className="text-gray-400 text-sm">{rule.description || rule.field} {rule.operator} "{rule.value}"</p>
                    </div>
                  </div>
                  <span className={`px-2 py-0.5 text-xs rounded ${getSeverityColor(rule.severity)} text-white`}>
                    {rule.severity}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* 统计面板 */}
      {activeTab === 'stats' && stats && (
        <div className="p-4 grid grid-cols-2 gap-4">
          <div className="p-4 rounded-lg bg-[#1E293B] border border-[#334155]">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-[#00E5FF]/20 rounded-lg">
                <Shield className="w-6 h-6 text-[#00E5FF]" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">总规则数</p>
                <p className="text-2xl font-bold text-white">{stats.total_rules}</p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-[#1E293B] border border-[#334155]">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <CheckCircle className="w-6 h-6 text-green-500" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">已启用规则</p>
                <p className="text-2xl font-bold text-white">{stats.enabled_rules}</p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-[#1E293B] border border-[#334155]">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-500/20 rounded-lg">
                <AlertTriangle className="w-6 h-6 text-red-500" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">总告警数</p>
                <p className="text-2xl font-bold text-white">{stats.total_alerts}</p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-[#1E293B] border border-[#334155]">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-500/20 rounded-lg">
                <Bell className="w-6 h-6 text-orange-500" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">未确认告警</p>
                <p className="text-2xl font-bold text-white">{stats.unacknowledged_alerts}</p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-[#1E293B] border border-[#334155] col-span-2">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Activity className="w-6 h-6 text-purple-500" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">WebSocket 连接数</p>
                <p className="text-2xl font-bold text-white">{stats.websocket_connections}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MonitorPanel;
