/**
 * HistoryPanel.tsx
 *
 * 预测历史记录面板 - 展示过去的预测和分析记录
 */
import { useState, useEffect } from 'react';
import {
  History,
  Clock,
  TrendingUp,
  TrendingDown,
  Minus,
  Trash2,
  Download,
  ChevronLeft,
  ChevronRight,
  Filter,
  FileText
} from 'lucide-react';

interface PredictionRecord {
  id: string;
  event_id: string;
  event_title: string;
  event_description: string;
  category: string;
  prediction: {
    trend: string;
    confidence: number;
    summary: string;
    key_insights: string[];
  };
  scenario?: any;
  overall_confidence: number;
  created_at: string;
  updated_at: string;
}

interface HistoryStats {
  total: number;
  categories: Record<string, number>;
  avg_confidence: number;
  recent_count: number;
}

interface HistoryListResponse {
  predictions: PredictionRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const API_BASE_URL = 'http://127.0.0.1:8005';

const categoryLabels: Record<string, string> = {
  'military': '军事',
  'politics': '政治',
  'economy': '经济',
  'technology': '科技',
  'Monetary Policy': '货币政策',
  'Geopolitical': '地缘政治',
  'Economic': '经济',
  'Technology': '科技',
  'Trade': '贸易',
  'Social': '社会',
  'Other': '其他'
};

export default function HistoryPanel() {
  const [history, setHistory] = useState<HistoryListResponse | null>(null);
  const [stats, setStats] = useState<HistoryStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<PredictionRecord | null>(null);

  useEffect(() => {
    loadHistory();
    loadStats();
  }, [page, selectedCategory]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('page', String(page));
      params.set('page_size', '10');
      if (selectedCategory) {
        params.set('category', selectedCategory);
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/history/list?${params}`);
      if (!response.ok) throw new Error('Failed to load history');

      const data = await response.json();
      setHistory(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/history/statistics/summary`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const deleteRecord = async (recordId: string) => {
    if (!confirm('确定要删除这条记录吗？')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/history/${recordId}`, {
        method: 'DELETE'
      });
      if (response.ok) {
        loadHistory();
        loadStats();
        if (selectedRecord?.id === recordId) {
          setSelectedRecord(null);
        }
      }
    } catch (err) {
      console.error('Failed to delete:', err);
    }
  };

  const exportHistory = async (format: 'json' | 'csv') => {
    window.open(`${API_BASE_URL}/api/v1/history/export/${format}`, '_blank');
  };

  const getTrendIcon = (trend: string) => {
    const t = trend.toLowerCase();
    if (t === 'up' || t === 'rising' || t === '上涨' || t === '乐观') {
      return <TrendingUp className="w-4 h-4 text-emerald-400" />;
    }
    if (t === 'down' || t === 'falling' || t === '下跌' || t === '悲观') {
      return <TrendingDown className="w-4 h-4 text-red-400" />;
    }
    return <Minus className="w-4 h-4 text-blue-400" />;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && !history) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="w-8 h-8 border-2 border-primary-cyan/20 border-t-primary-cyan rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 text-red-400">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 标题和操作栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-primary-cyan" />
          <h3 className="text-lg font-semibold text-text-primary">预测历史</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => exportHistory('json')}
            className="flex items-center gap-1 px-3 py-1.5 text-xs bg-[#1E293B] text-text-secondary rounded-lg hover:bg-[#2D3A4F] transition-colors"
          >
            <Download className="w-3 h-3" />
            导出JSON
          </button>
          <button
            onClick={() => exportHistory('csv')}
            className="flex items-center gap-1 px-3 py-1.5 text-xs bg-[#1E293B] text-text-secondary rounded-lg hover:bg-[#2D3A4F] transition-colors"
          >
            <FileText className="w-3 h-3" />
            导出CSV
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      {stats && (
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-lg p-3">
            <div className="text-xs text-text-muted mb-1">总预测数</div>
            <div className="text-xl font-bold text-text-primary">{stats.total}</div>
          </div>
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-lg p-3">
            <div className="text-xs text-text-muted mb-1">24小时内</div>
            <div className="text-xl font-bold text-primary-cyan">{stats.recent_count}</div>
          </div>
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-lg p-3">
            <div className="text-xs text-text-muted mb-1">平均置信度</div>
            <div className="text-xl font-bold text-amber-400">
              {(stats.avg_confidence * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-[#0F172A] border border-[#1E293B] rounded-lg p-3">
            <div className="text-xs text-text-muted mb-1">类别数</div>
            <div className="text-xl font-bold text-emerald-400">
              {Object.keys(stats.categories).length}
            </div>
          </div>
        </div>
      )}

      {/* 类别筛选 */}
      {stats && Object.keys(stats.categories).length > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="w-4 h-4 text-text-muted" />
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              !selectedCategory
                ? 'bg-primary-cyan/20 text-primary-cyan'
                : 'bg-[#1E293B] text-text-secondary hover:bg-[#2D3A4F]'
            }`}
          >
            全部
          </button>
          {Object.entries(stats.categories).map(([cat, count]) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-2 py-1 text-xs rounded transition-colors ${
                selectedCategory === cat
                  ? 'bg-primary-cyan/20 text-primary-cyan'
                  : 'bg-[#1E293B] text-text-secondary hover:bg-[#2D3A4F]'
              }`}
            >
              {categoryLabels[cat] || cat} ({count})
            </button>
          ))}
        </div>
      )}

      {/* 历史记录列表 */}
      <div className="space-y-2">
        {history?.predictions.map((record) => (
          <div
            key={record.id}
            className={`bg-[#0F172A] border rounded-lg p-4 cursor-pointer transition-all ${
              selectedRecord?.id === record.id
                ? 'border-primary-cyan/50 ring-1 ring-primary-cyan/30'
                : 'border-[#1E293B] hover:border-[#334155]'
            }`}
            onClick={() => setSelectedRecord(selectedRecord?.id === record.id ? null : record)}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {getTrendIcon(record.prediction.trend)}
                  <span className="text-sm font-medium text-text-primary truncate">
                    {record.event_title}
                  </span>
                </div>
                <p className="text-xs text-text-muted line-clamp-2">
                  {record.event_description}
                </p>
              </div>
              <div className="flex items-center gap-2 ml-2">
                <span className="px-2 py-0.5 text-xs bg-[#1E293B] text-text-secondary rounded">
                  {categoryLabels[record.category] || record.category}
                </span>
                <span className="text-xs text-text-muted">
                  {(record.overall_confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-text-muted">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatDate(record.created_at)}
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  deleteRecord(record.id);
                }}
                className="p-1 text-text-muted hover:text-red-400 transition-colors"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>

            {/* 展开详情 */}
            {selectedRecord?.id === record.id && (
              <div className="mt-4 pt-4 border-t border-[#1E293B] space-y-3">
                <div>
                  <h4 className="text-xs font-medium text-text-muted mb-1">预测摘要</h4>
                  <p className="text-sm text-text-secondary">{record.prediction.summary}</p>
                </div>

                {record.prediction.key_insights.length > 0 && (
                  <div>
                    <h4 className="text-xs font-medium text-text-muted mb-1">关键洞察</h4>
                    <ul className="space-y-1">
                      {record.prediction.key_insights.map((insight, idx) => (
                        <li key={idx} className="text-sm text-text-secondary flex items-start gap-2">
                          <span className="w-1 h-1 bg-primary-cyan rounded-full mt-2" />
                          {insight}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {record.scenario && (
                  <div>
                    <h4 className="text-xs font-medium text-text-muted mb-1">情景推演</h4>
                    <div className="flex flex-wrap gap-2">
                      {record.scenario.scenarios?.map((s: any) => (
                        <span
                          key={s.id}
                          className="px-2 py-1 text-xs bg-[#1E293B] text-text-secondary rounded"
                        >
                          {s.name} ({(s.probability * 100).toFixed(0)}%)
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 分页 */}
      {history && history.total_pages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="p-2 bg-[#1E293B] text-text-secondary rounded-lg disabled:opacity-50 hover:bg-[#2D3A4F] transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-sm text-text-secondary">
            {page} / {history.total_pages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(history.total_pages, p + 1))}
            disabled={page === history.total_pages}
            className="p-2 bg-[#1E293B] text-text-secondary rounded-lg disabled:opacity-50 hover:bg-[#2D3A4F] transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 空状态 */}
      {history && history.predictions.length === 0 && (
        <div className="text-center py-12 text-text-muted">
          <History className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>暂无预测历史记录</p>
        </div>
      )}
    </div>
  );
}
