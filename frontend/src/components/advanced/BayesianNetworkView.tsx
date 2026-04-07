import type { BayesianResult as BResult } from '../../services/api';

interface Props {
  result: BResult;
}

const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const nodeTypeColor = (type: string) => {
  switch (type) {
    case 'evidence': return COLORS.status.info;
    case 'hypothesis': return COLORS.primary.cyan;
    case 'factor': return COLORS.status.warning;
    default: return COLORS.text.muted;
  }
};

export default function BayesianNetworkView({ result }: Props) {
  const nodes = result.nodes || [];
  const edges = result.influence_diagram?.edges || [];

  // Layout: simple grid arrangement
  const evidenceNodes = nodes.filter(n => n.type === 'evidence');
  const factorNodes = nodes.filter(n => n.type === 'factor');
  const hypothesisNodes = nodes.filter(n => n.type === 'hypothesis');

  return (
    <div className="space-y-5">
      {/* Key stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-lg p-2.5" style={{ backgroundColor: `${COLORS.bg.card}80`, border: `1px solid ${COLORS.border}40` }}>
          <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>假设后验</div>
          <div className="text-sm font-semibold" style={{ color: COLORS.primary.cyan }}>
            {(result.main_hypothesis_posterior * 100).toFixed(1)}%
          </div>
        </div>
        <div className="rounded-lg p-2.5" style={{ backgroundColor: `${COLORS.bg.card}80`, border: `1px solid ${COLORS.border}40` }}>
          <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>节点数</div>
          <div className="text-sm font-semibold" style={{ color: COLORS.text.primary }}>{nodes.length}</div>
        </div>
        <div className="rounded-lg p-2.5" style={{ backgroundColor: `${COLORS.bg.card}80`, border: `1px solid ${COLORS.border}40` }}>
          <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>证据数</div>
          <div className="text-sm font-semibold" style={{ color: COLORS.text.primary }}>{evidenceNodes.length}</div>
        </div>
      </div>

      {/* Network Visualization - Layered layout */}
      <div className="relative rounded-lg p-4 overflow-hidden" style={{ backgroundColor: `${COLORS.bg.card}40`, border: `1px solid ${COLORS.border}40`, minHeight: '200px' }}>
        <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
          {edges.map((edge, i) => {
            const sourceIdx = nodes.findIndex(n => n.id === edge.source);
            const targetIdx = nodes.findIndex(n => n.id === edge.target);
            if (sourceIdx < 0 || targetIdx < 0) return null;
            // Simple layout: each layer has its own x range
            const sourceNode = nodes[sourceIdx];
            const targetNode = nodes[targetIdx];
            const sx = getNodeX(sourceNode, evidenceNodes, factorNodes, hypothesisNodes);
            const sy = getNodeY(sourceNode.type, evidenceNodes.length, factorNodes.length, sourceNode, evidenceNodes, factorNodes);
            const tx = getNodeX(targetNode, evidenceNodes, factorNodes, hypothesisNodes);
            const ty = getNodeY(targetNode.type, evidenceNodes.length, factorNodes.length, targetNode, evidenceNodes, factorNodes);
            return (
              <line
                key={i}
                x1={`${sx}%`} y1={`${sy}%`}
                x2={`${tx}%`} y2={`${ty}%`}
                stroke={COLORS.border}
                strokeWidth={edge.strength * 2.5}
                strokeOpacity={0.5}
                markerEnd="url(#arrowhead)"
              />
            );
          })}
          <defs>
            <marker id="arrowhead" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
              <polygon points="0 0, 6 2, 0 4" fill={COLORS.text.muted} />
            </marker>
          </defs>
        </svg>

        {/* Evidence layer */}
        {evidenceNodes.length > 0 && (
          <div className="relative z-10 mb-2">
            <div className="text-[9px] uppercase tracking-widest mb-1.5" style={{ color: COLORS.status.info }}>证据层</div>
            <div className="flex flex-wrap gap-2">
              {evidenceNodes.map(n => <NetworkNode key={n.id} node={n} />)}
            </div>
          </div>
        )}

        {/* Factor layer */}
        {factorNodes.length > 0 && (
          <div className="relative z-10 my-2">
            <div className="text-[9px] uppercase tracking-widest mb-1.5" style={{ color: COLORS.status.warning }}>因素层</div>
            <div className="flex flex-wrap gap-2">
              {factorNodes.map(n => <NetworkNode key={n.id} node={n} />)}
            </div>
          </div>
        )}

        {/* Hypothesis layer */}
        {hypothesisNodes.length > 0 && (
          <div className="relative z-10 mt-2">
            <div className="text-[9px] uppercase tracking-widest mb-1.5" style={{ color: COLORS.primary.cyan }}>假设层</div>
            <div className="flex flex-wrap gap-2">
              {hypothesisNodes.map(n => <NetworkNode key={n.id} node={n} />)}
            </div>
          </div>
        )}
      </div>

      {/* Prior vs Posterior comparison */}
      <div>
        <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>先验 → 后验对比</h4>
        <div className="space-y-2">
          {nodes.map(n => (
            <div key={n.id} className="flex items-center gap-2">
              <span className="text-xs w-20 truncate" style={{ color: COLORS.text.muted }}>{n.name}</span>
              <div className="flex-1 flex gap-1">
                <div className="flex-1 h-3 rounded-l-full overflow-hidden" style={{ backgroundColor: `${COLORS.border}40` }}>
                  <div className="h-full rounded-l-full" style={{
                    width: `${n.prior * 100}%`,
                    backgroundColor: COLORS.text.muted,
                    opacity: 0.5,
                  }} />
                </div>
                <div className="flex-1 h-3 rounded-r-full overflow-hidden" style={{ backgroundColor: `${COLORS.border}40` }}>
                  <div className="h-full rounded-r-full" style={{
                    width: `${n.posterior * 100}%`,
                    backgroundColor: nodeTypeColor(n.type),
                    opacity: 0.8,
                  }} />
                </div>
              </div>
              <span className="text-[10px] w-16 text-right" style={{ color: COLORS.text.secondary }}>
                {(n.prior * 100).toFixed(0)}% → {(n.posterior * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Evidence Impact */}
      {Object.keys(result.evidence_impact).length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>证据影响力</h4>
          <div className="space-y-1.5">
            {Object.entries(result.evidence_impact).map(([id, impact]) => {
              const node = nodes.find(n => n.id === id);
              return (
                <div key={id} className="flex items-center gap-2">
                  <span className="text-xs w-20 truncate" style={{ color: COLORS.text.muted }}>{node?.name || id}</span>
                  <div className="flex-1 h-3 rounded-full overflow-hidden" style={{ backgroundColor: `${COLORS.border}40` }}>
                    <div className="h-full rounded-full" style={{
                      width: `${Math.min(impact * 100, 100)}%`,
                      backgroundColor: COLORS.status.info,
                      opacity: 0.7,
                    }} />
                  </div>
                  <span className="text-[10px] w-10 text-right" style={{ color: COLORS.text.secondary }}>{(impact * 100).toFixed(1)}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function NetworkNode({ node }: { node: { id: string; name: string; type: string; posterior: number } }) {
  const color = nodeTypeColor(node.type);
  return (
    <div
      className="px-3 py-1.5 rounded-lg text-xs font-medium"
      style={{
        backgroundColor: `${color}15`,
        border: `1px solid ${color}40`,
        color,
      }}
    >
      <span>{node.name}</span>
      <span className="ml-1.5 opacity-70">{(node.posterior * 100).toFixed(0)}%</span>
    </div>
  );
}

// Helper functions for SVG layout
function getNodeX(
  node: { id: string; type: string },
  evidence: any[], factors: any[], hypothesis: any[]
): number {
  const layer = node.type === 'evidence' ? evidence : node.type === 'hypothesis' ? hypothesis : factors;
  const idx = layer.findIndex((n: any) => n.id === node.id);
  const count = layer.length;
  if (count <= 1) return 50;
  return 15 + (idx / (count - 1)) * 70;
}

function getNodeY(
  type: string,
  _eCount: number, _fCount: number,
  _node: any,
  _evidence: any[], _factors: any[]
): number {
  if (type === 'evidence') return 12;
  if (type === 'factor') return 50;
  return 88;
}
