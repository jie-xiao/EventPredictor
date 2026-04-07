import { useMemo } from 'react';
import { AlertTriangle } from 'lucide-react';
import type { CausalResult as CResult } from '../../services/api';

interface Props {
  result: CResult;
}

const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const factorColor = (type: string, isConfounder: boolean) => {
  if (isConfounder) return COLORS.status.danger;
  switch (type) {
    case 'cause': return COLORS.status.success;
    case 'effect': return COLORS.status.info;
    case 'mediator': return COLORS.status.warning;
    default: return COLORS.text.muted;
  }
};

export default function CausalGraphView({ result }: Props) {
  const graphNodes = result.graph_data?.nodes || [];
  const graphEdges = result.graph_data?.edges || [];
  const effectEntries = useMemo(
    () => Object.entries(result.total_effects).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1])),
    [result.total_effects]
  );

  const nodeMap = useMemo(() => {
    const m: Record<string, { name: string; type: string }> = {};
    for (const f of result.factors) m[f.id] = { name: f.name, type: f.factor_type };
    return m;
  }, [result.factors]);

  // Layout nodes in a simple force-like arrangement
  const positions = useMemo(() => {
    const pos: Record<string, { x: number; y: number }> = {};
    const causes = graphNodes.filter(n => n.type === 'cause');
    const mediators = graphNodes.filter(n => n.type === 'mediator');
    const effects = graphNodes.filter(n => n.type === 'effect');
    const others = graphNodes.filter(n => !['cause', 'mediator', 'effect'].includes(n.type));

    causes.forEach((n, i) => { pos[n.id] = { x: 15 + (i / Math.max(causes.length - 1, 1)) * 30, y: 15 }; });
    mediators.forEach((n, i) => { pos[n.id] = { x: 20 + (i / Math.max(mediators.length - 1, 1)) * 60, y: 50 }; });
    effects.forEach((n, i) => { pos[n.id] = { x: 35 + (i / Math.max(effects.length - 1, 1)) * 30, y: 85 }; });
    others.forEach((n, i) => { pos[n.id] = { x: 70 + (i / Math.max(others.length - 1, 1)) * 20, y: 30 + i * 20 }; });

    return pos;
  }, [graphNodes]);

  return (
    <div className="space-y-5">
      {/* Graph Visualization */}
      <div className="relative rounded-lg overflow-hidden" style={{ backgroundColor: `${COLORS.bg.card}40`, border: `1px solid ${COLORS.border}40`, height: '220px' }}>
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          {/* Edges */}
          {graphEdges.map((edge, i) => {
            const sp = positions[edge.source];
            const tp = positions[edge.target];
            if (!sp || !tp) return null;
            return (
              <g key={i}>
                <line
                  x1={sp.x} y1={sp.y} x2={tp.x} y2={tp.y}
                  stroke={COLORS.border}
                  strokeWidth={edge.strength * 0.8}
                  strokeOpacity={0.6}
                />
                <circle cx={tp.x} cy={tp.y} r="0.8" fill={COLORS.text.muted} />
              </g>
            );
          })}
          {/* Nodes */}
          {graphNodes.map((node) => {
            const p = positions[node.id];
            if (!p) return null;
            const color = factorColor(node.type, node.is_confounder);
            return (
              <g key={node.id}>
                {node.is_confounder && (
                  <AlertTriangle x={p.x - 4} y={p.y - 5} width="2" height="2" fill={COLORS.status.danger} />
                )}
                <circle
                  cx={p.x} cy={p.y} r="3"
                  fill={`${color}30`}
                  stroke={color}
                  strokeWidth="0.4"
                />
                <text
                  x={p.x} y={p.y + 6}
                  textAnchor="middle"
                  fill={COLORS.text.muted}
                  fontSize="2.5"
                >
                  {node.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Effect Breakdown */}
      <div>
        <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>效应分解</h4>
        <div className="space-y-2">
          {effectEntries.map(([id, total]) => {
            const direct = result.direct_effects[id] || 0;
            const indirect = result.indirect_effects[id] || 0;
            const info = nodeMap[id];
            const maxVal = Math.max(...effectEntries.map(([, v]) => Math.abs(v)), 0.01);
            return (
              <div key={id} className="space-y-0.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs" style={{ color: COLORS.text.muted }}>{info?.name || id}</span>
                  <span className="text-xs" style={{ color: COLORS.text.secondary }}>总效应: {total.toFixed(3)}</span>
                </div>
                <div className="flex gap-0.5 h-2">
                  {/* Direct */}
                  <div
                    className="rounded-l"
                    style={{
                      width: `${(Math.abs(direct) / maxVal) * 60}%`,
                      backgroundColor: COLORS.status.info,
                      opacity: 0.7,
                      minWidth: direct !== 0 ? '2px' : '0px',
                    }}
                    title={`直接效应: ${direct.toFixed(3)}`}
                  />
                  {/* Indirect */}
                  <div
                    className="rounded-r"
                    style={{
                      width: `${(Math.abs(indirect) / maxVal) * 60}%`,
                      backgroundColor: COLORS.status.warning,
                      opacity: 0.7,
                      minWidth: indirect !== 0 ? '2px' : '0px',
                    }}
                    title={`间接效应: ${indirect.toFixed(3)}`}
                  />
                </div>
                <div className="flex gap-3 text-[9px]" style={{ color: COLORS.text.muted }}>
                  <span><span style={{ color: COLORS.status.info }}>■</span> 直接: {direct.toFixed(3)}</span>
                  <span><span style={{ color: COLORS.status.warning }}>■</span> 间接: {indirect.toFixed(3)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Confounders Warning */}
      {result.confounders.length > 0 && (
        <div className="rounded-lg p-3" style={{ backgroundColor: `${COLORS.status.danger}10`, border: `1px solid ${COLORS.status.danger}30` }}>
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-3.5 h-3.5" style={{ color: COLORS.status.danger }} />
            <span className="text-xs font-medium" style={{ color: COLORS.status.danger }}>混杂因素</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {result.confounders.map(id => {
              const info = nodeMap[id];
              return (
                <span key={id} className="px-2 py-0.5 rounded text-[10px]" style={{
                  backgroundColor: `${COLORS.status.danger}15`,
                  color: COLORS.status.danger,
                }}>
                  {info?.name || id}
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Causal Paths */}
      {result.causal_paths.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2" style={{ color: COLORS.text.secondary }}>因果路径</h4>
          <div className="space-y-1.5 max-h-32 overflow-y-auto">
            {result.causal_paths.slice(0, 8).map((path, i) => {
              const fromInfo = nodeMap[path.from];
              return (
                <div key={i} className="text-xs px-2 py-1 rounded" style={{ backgroundColor: `${COLORS.bg.card}60` }}>
                  <span style={{ color: COLORS.text.muted }}>{fromInfo?.name || path.from}</span>
                  {path.path.map((step, j) => (
                    <span key={j}>
                      <span style={{ color: COLORS.primary.cyan }}> → </span>
                      <span style={{ color: COLORS.text.muted }}>{nodeMap[step.target]?.name || step.target}</span>
                    </span>
                  ))}
                  <span className="ml-2" style={{ color: COLORS.text.muted }}>({path.strength.toFixed(3)})</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
