// 知识图谱可视化组件
import React, { useState, useEffect, useRef } from 'react';
import { Network } from 'react-vis-network';
import { AlertTriangle, Search, RefreshCw, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

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

interface KnowledgeGraphData {
  entities: EntityNode[];
  relations: RelationEdge[];
}

// ============ 节点配置 ============
const getNodeConfig = (type: string, importance: number = 1) => {
  const colors: Record<string, string> = {
    country: '#1976d2',
    organization: '#388e3c',
    company: '#7b1fa2',
    person: '#c2185b',
    event: '#f57c00',
    location: '#0097a7',
    concept: '#5d4037',
    industry: '#455a64',
    asset: '#ffc107',
  };
  
  const labels: Record<string, string> = {
    country: '🌍',
    organization: '🏢',
    company: '🏭',
    person: '👤',
    event: '📰',
    location: '📍',
    concept: '💡',
    industry: '🏭',
    asset: '💰',
  };

  const baseSize = 20 + importance * 10;
  
  return {
    color: colors[type] || '#757575',
    label: labels[type] || '📌',
    size: baseSize,
    shape: 'dot',
    font: { color: '#ffffff', size: 12, face: 'Roboto' },
    borderWidth: 2,
    shadow: true,
  };
};

const getEdgeConfig = (type: string, weight: number = 1) => {
  const colors: Record<string, string> = {
    ally: '#4caf50',
    enemy: '#f44336',
    sanction: '#ff9800',
    diplomatic: '#2196f3',
    conflict: '#e91e63',
    cooperation: '#00bcd4',
    trade_partner: '#8bc34a',
    investor: '#ffc107',
    supplier: '#9c27b0',
    competitor: '#607d8b',
    member: '#03a9f4',
    subsidiary: '#795548',
    caused: '#f44336',
    affected: '#ff9800',
    triggered: '#ffeb3b',
    responded: '#4caf50',
    related: '#9e9e9e',
    opposed: '#e91e63',
    supported: '#8bc34a',
  };

  return {
    color: colors[type] || '#9e9e9e',
    width: Math.max(1, weight),
    arrows: 'to',
    smooth: { type: 'continuous' },
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
  const networkRef = useRef<any>(null);

  // 加载知识图谱数据
  const loadGraphData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('http://127.0.0.1:8005/api/v1/knowledge-graph/entities?limit=100');
      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.detail || 'Failed to load entities');
      }

      const entities = result.data?.entities || [];
      
      // 加载关系
      const relResponse = await fetch('http://127.0.0.1:8005/api/v1/knowledge-graph/relations?limit=200');
      const relResult = await relResponse.json();
      const relations = relResult.data?.relations || [];

      // 转换为 vis.js 格式
      const nodes = entities.map((e: any) => ({
        id: e.id,
        label: e.name,
        title: `${e.name}\n类型: ${e.type}\n重要性: ${e.importance || 1}`,
        ...getNodeConfig(e.type, e.importance || 1),
      }));

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
      console.error('Load graph error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraphData();
  }, []);

  // 搜索过滤
  const filteredData = searchQuery
    ? {
        nodes: graphData.nodes.filter(
          (n) => n.label.toLowerCase().includes(searchQuery.toLowerCase())
        ),
        edges: graphData.edges.filter(
          (e) =>
            graphData.nodes.some((n) => n.id === e.from && n.label.toLowerCase().includes(searchQuery.toLowerCase())) ||
            graphData.nodes.some((n) => n.id === e.to && n.label.toLowerCase().includes(searchQuery.toLowerCase()))
        ),
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
        }
      } catch (err) {
        console.error('Failed to load node details:', err);
      }
    }
  };

  // 缩放操作
  const zoomIn = () => networkRef.current?.zoomIn();
  const zoomOut = () => networkRef.current?.zoomOut();
  const fit = () => networkRef.current?.fit();

  // 选项配置
  const options = {
    nodes: {
      borderWidth: 2,
      shadow: true,
    },
    edges: {
      smooth: { type: 'continuous' },
      arrows: { to: { enabled: true, scaleFactor: 0.5 } },
    },
    physics: {
      enabled: true,
      barnesHut: {
        gravitationalConstant: -2000,
        centralGravity: 0.3,
        springLength: 150,
        springConstant: 0.04,
        damping: 0.09,
      },
    },
    interaction: {
      hover: true,
      tooltipDelay: 200,
      zoomView: true,
      dragView: true,
    },
    manipulation: {
      enabled: false,
    },
  };

  return (
    <div className="knowledge-graph-view">
      {/* 工具栏 */}
      <div className="flex items-center gap-2 p-3 bg-[#1E293B] border-b border-[#334155]">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索实体..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-[#0F172A] border border-[#334155] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#00E5FF]"
          />
        </div>
        <button
          onClick={loadGraphData}
          disabled={loading}
          className="p-2 bg-[#00E5FF] text-[#0A0E1A] rounded-lg hover:bg-[#67E8F9] disabled:opacity-50"
          title="刷新"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
        <button onClick={zoomIn} className="p-2 bg-[#334155] text-white rounded-lg hover:bg-[#475569]" title="放大">
          <ZoomIn className="w-4 h-4" />
        </button>
        <button onClick={zoomOut} className="p-2 bg-[#334155] text-white rounded-lg hover:bg-[#475569]" title="缩小">
          <ZoomOut className="w-4 h-4" />
        </button>
        <button onClick={fit} className="p-2 bg-[#334155] text-white rounded-lg hover:bg-[#475569]" title="适应窗口">
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* 图谱区域 */}
      <div className="relative" style={{ height: 'calc(100vh - 200px)', minHeight: '400px' }}>
        {error && (
          <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 px-4 py-2 bg-red-500/20 border border-red-500 rounded-lg text-red-400 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            {error}
          </div>
        )}

        {loading && graphData.nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-400 flex items-center gap-2">
              <RefreshCw className="w-6 h-6 animate-spin" />
              加载知识图谱...
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

        {/* 统计信息 */}
        <div className="absolute bottom-4 left-4 px-3 py-2 bg-[#0F172A]/90 border border-[#334155] rounded-lg text-sm text-gray-300">
          节点: {graphData.nodes.length} | 边: {graphData.edges.length}
        </div>
      </div>

      {/* 选中节点详情面板 */}
      {selectedNode && (
        <div className="absolute top-4 right-4 w-80 bg-[#1E293B] border border-[#334155] rounded-lg shadow-xl p-4">
          <div className="flex justify-between items-start mb-3">
            <h3 className="text-lg font-semibold text-white">{selectedNode.name}</h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-400 hover:text-white"
            >
              ×
            </button>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">类型:</span>
              <span className="text-[#00E5FF]">{selectedNode.type}</span>
            </div>
            {selectedNode.importance !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-400">重要性:</span>
                <span className="text-yellow-400">{'★'.repeat(Math.min(5, Math.ceil(selectedNode.importance)))}</span>
              </div>
            )}
            {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
              <div className="mt-3 pt-3 border-t border-[#334155]">
                <span className="text-gray-400">属性:</span>
                <pre className="mt-1 text-xs text-gray-300 overflow-auto max-h-32">
                  {JSON.stringify(selectedNode.properties, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeGraphView;
