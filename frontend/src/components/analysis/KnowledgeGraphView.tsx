// 知识图谱可视化组件 - 世界一流UI设计
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Network } from 'react-vis-network';
import { 
  AlertTriangle, Search, RefreshCw, ZoomIn, ZoomOut, Maximize2, 
  Network as NetworkIcon, Settings, X
} from 'lucide-react';

// ============ 类型定义 ============
interface EntityNode {
  id: string;
  name: string;
  type: string;
  importance?: number;
  properties?: Record<string, any>;
}

interface RelationEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  weight?: number;
}

// ============ 世界一流UI配置 ============
// 配色方案 - 深邃科技感 + 玻璃拟态
const THEME = {
  primary: '#00E5FF',
  primaryLight: '#67E8F9',
  background: '#0A0E1A',
  surface: '#111827',
  surfaceElevated: '#1F2937',
  border: '#374151',
  borderLight: '#4B5563',
  text: '#F9FAFB',
  textSecondary: '#9CA3AF',
  textMuted: '#6B7280',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
};

// 实体类型配色 - 莫兰迪色系更高级
const ENTITY_COLORS: Record<string, { bg: string; border: string; glow: string }> = {
  country:     { bg: '#1E3A5F', border: '#3B82F6', glow: 'rgba(59,130,246,0.4)' },
  organization:{ bg: '#14532D', border: '#22C55E', glow: 'rgba(34,197,94,0.4)' },
  company:     { bg: '#4C1D95', border: '#A855F7', glow: 'rgba(168,85,247,0.4)' },
  person:      { bg: '#881337', border: '#F43F5E', glow: 'rgba(244,63,94,0.4)' },
  event:       { bg: '#C2410C', border: '#F97316', glow: 'rgba(249,115,22,0.4)' },
  location:    { bg: '#0E7490', border: '#06B6D4', glow: 'rgba(6,182,212,0.4)' },
  concept:     { bg: '#713F12', border: '#EAB308', glow: 'rgba(234,179,8,0.4)' },
  industry:    { bg: '#44403C', border: '#A8A29E', glow: 'rgba(168,162,158,0.4)' },
  asset:       { bg: '#78350F', border: '#D97706', glow: 'rgba(217,119,6,0.4)' },
};

const ENTITY_LABELS: Record<string, string> = {
  country: '🌍', organization: '🏢', company: '🏭', person: '👤',
  event: '📰', location: '📍', concept: '💡', industry: '⚙️', asset: '💰',
};

// 关系类型配色
const RELATION_COLORS: Record<string, string> = {
  ally: '#22C55E', enemy: '#EF4444', sanction: '#F59E0B', diplomatic: '#3B82F6',
  conflict: '#EC4899', cooperation: '#06B6D4', trade_partner: '#84CC16',
  investor: '#FBBF24', supplier: '#A855F7', competitor: '#6B7280',
  member: '#0EA5E9', subsidiary: '#A16207', caused: '#DC2626',
  affected: '#FB923C', triggered: '#FACC15', responded: '#34D399',
  related: '#9CA3AF', opposed: '#F472B6', supported: '#4ADE80',
};

// ============ 节点配置 ============
const getNodeConfig = (type: string, importance: number = 1) => {
  const theme = ENTITY_COLORS[type] || ENTITY_COLORS.concept;
  const baseSize = 24 + importance * 12;
  
  return {
    color: {
      background: theme.bg,
      border: theme.border,
      highlight: { background: theme.bg, border: THEME.primary },
      hover: { background: theme.bg, border: THEME.primary }
    },
    label: ENTITY_LABELS[type] || '📌',
    size: baseSize,
    shape: 'dot',
    font: {
      color: THEME.text,
      size: 11,
      face: 'Inter, system-ui, sans-serif',
      strokeWidth: 0,
    },
    borderWidth: 2,
    shadow: { enabled: true, color: theme.glow, size: 15, x: 0, y: 0 },
  };
};

const getEdgeConfig = (type: string, weight: number = 1) => {
  const color = RELATION_COLORS[type] || '#6B7280';
  return {
    color: { color, highlight: THEME.primary, hover: THEME.primaryLight },
    width: Math.max(1, weight * 1.5),
    arrows: { to: { enabled: true, scaleFactor: 0.6, color: color } },
    smooth: { type: 'continuous', forceDirection: 'none', roundness: 0.3 },
    font: { color: THEME.textMuted, size: 9, strokeWidth: 0, background: 'rgba(0,0,0,0.6)' },
  };
};

// ============ 主组件 ============
const KnowledgeGraphView: React.FC = () => {
  const [graphData, setGraphData] = useState<{ nodes: any[]; edges: any[] }>({
    nodes: [],
    edges: [],
  });
  const [selectedNode, setSelectedNode] = useState<EntityNode | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showDetail, setShowDetail] = useState(false);
  const networkRef = useRef<any>(null);

  // 加载数据
  const loadGraphData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [entitiesRes, relationsRes] = await Promise.all([
        fetch('http://127.0.0.1:8005/api/v1/knowledge-graph/entities?limit=100'),
        fetch('http://127.0.0.1:8005/api/v1/knowledge-graph/relations?limit=200'),
      ]);
      
      const entitiesData = await entitiesRes.json();
      const relationsData = await relationsRes.json();
      
      if (!entitiesData.success) throw new Error(entitiesData.detail || '加载实体失败');
      
      const entities = entitiesData.data?.entities || [];
      const relations = relationsData.data?.relations || [];

      // 节点转换
      const nodes = entities.map((e: any) => ({
        id: e.id,
        label: e.name,
        title: `${e.name}\n类型: ${e.type}\n重要性: ${e.importance || 1}`,
        ...getNodeConfig(e.type, e.importance || 1),
      }));

      // 边转换
      const edges = relations.map((r: any) => ({
        id: r.id,
        from: r.source,
        to: r.target,
        label: r.type,
        title: `关系: ${r.type}\n权重: ${r.weight || 1}`,
        ...getEdgeConfig(r.type, r.weight || 1),
      }));

      setGraphData({ nodes, edges });
    } catch (err: any) {
      setError(err.message || '加载知识图谱失败');
      console.error('Load error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadGraphData(); }, [loadGraphData]);

  // 过滤
  const filteredData = searchQuery
    ? {
        nodes: graphData.nodes.filter(
          (n) => n.label.toLowerCase().includes(searchQuery.toLowerCase())
        ),
        edges: graphData.edges.filter((e) => {
          const sourceNode = graphData.nodes.find((n) => n.id === e.from);
          const targetNode = graphData.nodes.find((n) => n.id === e.to);
          return (
            sourceNode?.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
            targetNode?.label.toLowerCase().includes(searchQuery.toLowerCase())
          );
        }),
      }
    : graphData;

  // 节点点击
  const handleNodeClick = async (params: any) => {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0];
      try {
        const response = await fetch(`http://127.0.0.1:8005/api/v1/knowledge-graph/entities/${nodeId}`);
        const result = await response.json();
        if (result.success) {
          setSelectedNode(result.data);
          setShowDetail(true);
        }
      } catch (err) { console.error('Load node error:', err); }
    }
  };

  // 缩放操作
  const zoomIn = () => networkRef.current?.zoomIn({ scale: 1.2 });
  const zoomOut = () => networkRef.current?.zoomOut({ scale: 0.8 });
  const fit = () => networkRef.current?.fit({ animation: true });

  // Vis.js 配置 - 世界一流交互
  const options = {
    nodes: {
      borderWidth: 2,
      shadow: true,
      chosen: { node: true, edge: true },
    },
    edges: {
      smooth: { type: 'continuous' },
      hoverConnectedEdges: true,
      selectionWidth: 2,
    },
    physics: {
      enabled: true,
      barnesHut: {
        gravitationalConstant: -3000,
        centralGravity: 0.4,
        springLength: 180,
        springConstant: 0.05,
        damping: 0.09,
        avoidOverlap: 0.3,
      },
      stabilization: { iterations: 200 },
    },
    interaction: {
      hover: true,
      tooltipDelay: 150,
      zoomView: true,
      dragView: true,
      dragNodes: true,
      selectable: true,
      multiselect: true,
    },
  };

  return (
    <div className="h-full flex flex-col" style={{ background: THEME.background }}>
      {/* 工具栏 - 玻璃拟态设计 */}
      <div 
        className="flex items-center gap-3 px-5 py-3 border-b"
        style={{ 
          background: 'linear-gradient(180deg, rgba(31,41,55,0.9) 0%, rgba(17,24,39,0.95) 100%)',
          borderColor: THEME.border,
          backdropFilter: 'blur(12px)',
        }}
      >
        {/* 搜索框 - 悬浮效果 */}
        <div className="relative flex-1 max-w-md group">
          <div 
            className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none transition-colors group-focus-within:text-cyan-400"
            style={{ color: THEME.textMuted }}
          >
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            placeholder="搜索实体..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm transition-all duration-200"
            style={{ 
              background: 'rgba(31,41,55,0.8)',
              border: `1px solid ${THEME.border}`,
              color: THEME.text,
            }}
            onFocus={(e) => {
              e.target.style.borderColor = THEME.primary;
              e.target.style.boxShadow = '0 0 0 3px rgba(0,229,255,0.15)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = THEME.border;
              e.target.style.boxShadow = 'none';
            }}
          />
        </div>

        {/* 操作按钮 - 精致风格 */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={loadGraphData}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105"
            style={{ 
              background: 'linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%)',
              color: 'white',
              boxShadow: '0 4px 12px rgba(14,165,233,0.3)',
            }}
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            刷新
          </button>
          
          <div className="w-px h-6 mx-2" style={{ background: THEME.border }} />
          
          <button 
            onClick={zoomIn} 
            className="p-2 rounded-lg transition-all duration-200 hover:scale-110"
            style={{ background: THEME.surfaceElevated, color: THEME.textSecondary }}
            title="放大"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button 
            onClick={zoomOut} 
            className="p-2 rounded-lg transition-all duration-200 hover:scale-110"
            style={{ background: THEME.surfaceElevated, color: THEME.textSecondary }}
            title="缩小"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button 
            onClick={fit} 
            className="p-2 rounded-lg transition-all duration-200 hover:scale-110"
            style={{ background: THEME.surfaceElevated, color: THEME.textSecondary }}
            title="适应窗口"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>

        {/* 统计 */}
        <div 
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs"
          style={{ background: 'rgba(31,41,55,0.6)', color: THEME.textSecondary }}
        >
          <NetworkIcon className="w-3.5 h-3.5" style={{ color: THEME.primary }} />
          <span>{graphData.nodes.length} 节点</span>
          <span className="mx-1">•</span>
          <span>{graphData.edges.length} 边</span>
        </div>
      </div>

      {/* 图谱区域 */}
      <div className="flex-1 relative" style={{ minHeight: 0 }}>
        {/* 错误提示 */}
        {error && (
          <div 
            className="absolute top-4 left-1/2 -translate-x-1/2 z-20 px-4 py-2.5 rounded-xl flex items-center gap-2 animate-pulse"
            style={{ 
              background: 'linear-gradient(135deg, rgba(239,68,68,0.95) 0%, rgba(220,38,38,0.95) 100%)',
              color: 'white',
              boxShadow: '0 8px 24px rgba(239,68,68,0.4)',
            }}
          >
            <AlertTriangle className="w-4 h-4" />
            {error}
          </div>
        )}

        {/* 加载状态 - 骨架屏 */}
        {loading && graphData.nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl animate-pulse" style={{ background: THEME.surfaceElevated }} />
              <p className="text-sm animate-pulse" style={{ color: THEME.textMuted }}>
                加载知识图谱中...
              </p>
            </div>
          </div>
        ) : (
          <Network
            ref={networkRef}
            data={filteredData}
            options={options}
            onClick={handleNodeClick}
            style={{ width: '100%', height: '100%' }}
          />
        )}
      </div>

      {/* 详情面板 - 滑入动画 */}
      {showDetail && selectedNode && (
        <div 
          className="absolute top-4 right-4 w-80 rounded-2xl overflow-hidden z-20 animate-slide-in"
          style={{ 
            background: 'linear-gradient(180deg, rgba(31,41,55,0.98) 0%, rgba(17,24,39,0.98) 100%)',
            border: `1px solid ${THEME.border}`,
            boxShadow: '0 24px 48px rgba(0,0,0,0.5)',
            backdropFilter: 'blur(20px)',
          }}
        >
          {/* 头部 */}
          <div 
            className="flex items-center justify-between px-5 py-4 border-b"
            style={{ borderColor: THEME.border }}
          >
            <h3 className="text-lg font-semibold" style={{ color: THEME.text }}>
              {selectedNode.name}
            </h3>
            <button
              onClick={() => setShowDetail(false)}
              className="p-1.5 rounded-lg transition-colors hover:bg-white/10"
              style={{ color: THEME.textMuted }}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          {/* 内容 */}
          <div className="p-5 space-y-4">
            <div className="flex items-center gap-3">
              <span 
                className="px-2.5 py-1 rounded-md text-xs font-medium"
                style={{ 
                  background: ENTITY_COLORS[selectedNode.type]?.bg || '#374151',
                  color: THEME.text,
                  border: `1px solid ${ENTITY_COLORS[selectedNode.type]?.border || '#4B5563'}`,
                }}
              >
                {selectedNode.type}
              </span>
              {selectedNode.importance !== undefined && (
                <div className="flex items-center gap-1">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <span 
                      key={i} 
                      className="text-xs"
                      style={{ 
                        color: i < Math.ceil(selectedNode.importance) ? '#FBBF24' : '#374151' 
                      }}
                    >
                      ★
                    </span>
                  ))}
                </div>
              )}
            </div>
            
            {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
              <div className="pt-3 border-t" style={{ borderColor: THEME.border }}>
                <p className="text-xs mb-2" style={{ color: THEME.textMuted }}>属性</p>
                <pre 
                  className="text-xs p-3 rounded-lg overflow-auto max-h-32"
                  style={{ background: 'rgba(0,0,0,0.3)', color: THEME.textSecondary }}
                >
                  {JSON.stringify(selectedNode.properties, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}

      {/* CSS动画 */}
      <style>{`
        @keyframes slide-in {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
        .animate-slide-in {
          animation: slide-in 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
      `}</style>
    </div>
  );
};

export default KnowledgeGraphView;
