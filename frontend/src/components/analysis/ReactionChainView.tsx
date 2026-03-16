// 反应链展示组件 - 增强版
import React, { useState } from 'react';
import {
  ReactionChainResult,
  ReactionRoundData,
  TimelineEventData,
  ReactionEvolution,
  ReactionChainConclusion,
  InfluenceNetwork,
  StateSnapshot
} from '../../services/api';

// 使用 any 来避免类型不匹配问题
type EnhancedReactionChainResult = ReactionChainResult & {
  converged?: boolean;
  timeline_tree?: any;
  state_evolution?: StateSnapshot[];
  convergence_trend?: number[];
};

// ============ 时间线节点组件 ============
const TimelineNode: React.FC<{
  event: TimelineEventData;
  isActive: boolean;
  onClick: () => void;
}> = ({ event, isActive, onClick }) => {
  const getIcon = () => {
    switch (event.event_type) {
      case 'initial_event':
        return '🎯';
      case 'reaction':
        return '💬';
      case 'state_change':
        return '📊';
      case 'influence':
        return '🔗';
      case 'convergence':
        return '✅';
      default:
        return '📌';
    }
  };

  const getTypeColor = () => {
    switch (event.event_type) {
      case 'initial_event':
        return '#1976d2';
      case 'reaction':
        return '#2196f3';
      case 'state_change':
        return '#ff9800';
      case 'influence':
        return '#9c27b0';
      case 'convergence':
        return '#4caf50';
      default:
        return '#9e9e9e';
    }
  };

  return (
    <div
      className={`timeline-node ${isActive ? 'active' : ''}`}
      onClick={onClick}
      style={{
        padding: '12px 16px',
        margin: '8px 0',
        borderRadius: '8px',
        background: isActive ? '#e3f2fd' : '#f5f5f5',
        borderLeft: `4px solid ${isActive ? '#1976d2' : getTypeColor()}`,
        cursor: 'pointer',
        transition: 'all 0.2s ease'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ fontSize: '20px' }}>{getIcon()}</span>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 'bold', fontSize: '14px', color: getTypeColor() }}>
            {event.time} - {event.event_type}
          </div>
          <div style={{ fontSize: '13px', color: '#666', marginTop: '4px' }}>
            {event.description}
          </div>
          {event.involved_roles && event.involved_roles.length > 0 && (
            <div style={{ fontSize: '12px', color: '#888', marginTop: '4px' }}>
              涉及: {event.involved_roles.join(', ')}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ============ 角色反应卡片组件 ============
const ReactionCard: React.FC<{
  reaction: ReactionRoundData;
  isExpanded: boolean;
  onToggle: () => void;
}> = ({ reaction, isExpanded, onToggle }) => {
  const r = reaction.reaction;

  const getEmotionColor = (emotion: string) => {
    const lower = emotion.toLowerCase();
    if (lower.includes('高') || lower.includes('强') || lower.includes('积极') || lower.includes('乐观')) return '#4caf50';
    if (lower.includes('担') || lower.includes('负面') || lower.includes('反对')) return '#f44336';
    if (lower.includes('谨') || lower.includes('观')) return '#ff9800';
    return '#9e9e9e';
  };

  return (
    <div
      onClick={onToggle}
      style={{
        padding: '16px',
        margin: '8px 0',
        borderRadius: '12px',
        background: '#fff',
        border: '1px solid #e0e0e0',
        cursor: 'pointer',
        boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontWeight: 'bold', fontSize: '16px', color: '#1976d2' }}>
            {reaction.role_name}
          </div>
          <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
            第 {reaction.round_number} 轮
          </div>
        </div>
        <div style={{
          padding: '4px 12px',
          borderRadius: '16px',
          background: getEmotionColor(r.emotion) + '20',
          color: getEmotionColor(r.emotion),
          fontSize: '12px',
          fontWeight: 'bold'
        }}>
          {r.emotion}
        </div>
      </div>

      {isExpanded && (
        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #eee' }}>
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>采取的行动</div>
            <div style={{ fontSize: '14px', color: '#333' }}>{r.action}</div>
          </div>
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>发表的声明</div>
            <div style={{ fontSize: '14px', color: '#333', fontStyle: 'italic' }}>
              "{r.statement}"
            </div>
          </div>
          {r.stance_change && (
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>立场变化</div>
              <div style={{ fontSize: '14px', color: '#ff9800' }}>{r.stance_change}</div>
            </div>
          )}
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>置信度</div>
            <div style={{
              height: '8px',
              background: '#e0e0e0',
              borderRadius: '4px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${(r.confidence ?? 0.7) * 100}%`,
                height: '100%',
                background: (r.confidence ?? 0.7) >= 0.8 ? '#4caf50' : (r.confidence ?? 0.7) >= 0.6 ? '#ff9800' : '#f44336'
              }} />
            </div>
            <span style={{ fontSize: '12px', color: '#666' }}>
              {(r.confidence ?? 0.7) * 100}%
            </span>
          </div>
          {reaction.affected_by && reaction.affected_by.length > 0 && (
            <div>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px' }}>受以下方影响</div>
              <div style={{ fontSize: '14px', color: '#666' }}>
                {reaction.affected_by.join(', ')}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ============ 演变趋势组件 ============
const EvolutionChart: React.FC<{
  evolution: Record<string, ReactionEvolution>;
}> = ({ evolution }) => {
  const entries = Object.entries(evolution);

  if (entries.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
        暂无演变数据
      </div>
    );
  }

  return (
    <div style={{ padding: '16px' }}>
      {entries.map(([roleId, evo]) => (
        <div key={roleId} style={{ marginBottom: '24px', padding: '16px', background: '#fafafa', borderRadius: '8px' }}>
          <div style={{ fontWeight: 'bold', fontSize: '15px', marginBottom: '12px', color: '#1976d2' }}>
            {evo.role_name}
          </div>

          {/* 情绪演变 */}
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '12px', color: '#888', marginBottom: '6px' }}>情绪演变</div>
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {evo.emotion_evolution.map((emotion, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '16px',
                    background: idx === evo.emotion_evolution.length - 1 ? '#e3f2fd' : '#f0f0f0',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    border: idx === evo.emotion_evolution.length - 1 ? '1px solid #1976d2' : 'none'
                  }}
                >
                  <span style={{ color: '#888' }}>R{idx + 1}:</span>
                  <span>{emotion}</span>
                  {idx < evo.emotion_evolution.length - 1 && <span style={{ color: '#ccc' }}>→</span>}
                </div>
              ))}
            </div>
          </div>

          {/* 置信度趋势 */}
          {evo.confidence_evolution && evo.confidence_evolution.length > 1 && (
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '12px', color: '#888', marginBottom: '6px' }}>置信度趋势</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', height: '40px' }}>
                {evo.confidence_evolution.map((conf, idx) => (
                  <div key={idx} style={{
                    width: '30px',
                    height: `${conf * 100}%`,
                    background: conf >= 0.8 ? '#4caf50' : conf >= 0.6 ? '#ff9800' : '#f44336',
                    borderRadius: '4px 4px 0 0',
                    display: 'flex',
                    alignItems: 'flex-end',
                    justifyContent: 'center'
                  }}>
                    <span style={{ fontSize: '9px', color: 'white', marginBottom: '2px' }}>
                      {Math.round(conf * 100)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 汇总 */}
          <div style={{ fontSize: '12px', color: '#666', marginTop: '8px', padding: '8px', background: '#fff', borderRadius: '4px' }}>
            📈 {evo.summary}
          </div>
        </div>
      ))}
    </div>
  );
};

// ============ 影响力网络组件 ============
const InfluenceNetworkView: React.FC<{
  network: InfluenceNetwork;
  opinionLeaders: Array<{ role_id: string; role_name: string; leadership_score: number }>;
  mostInfluenced: Array<{ role_id: string; role_name: string; receptivity_score: number }>;
}> = ({ network, opinionLeaders, mostInfluenced }) => {
  if (!network || !network.nodes || network.nodes.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
        暂无影响力数据
      </div>
    );
  }

  return (
    <div style={{ padding: '16px' }}>
      {/* 意见领袖 */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '12px', color: '#9c27b0' }}>
          🏆 意见领袖 (影响力最强的角色)
        </div>
        {opinionLeaders.map((leader, idx) => (
          <div key={leader.role_id} style={{
            display: 'flex',
            alignItems: 'center',
            padding: '12px',
            marginBottom: '8px',
            borderRadius: '8px',
            background: `linear-gradient(90deg, #f3e5f5 ${leader.leadership_score * 100}%, #fafafa ${leader.leadership_score * 100}%)`,
            border: '1px solid #e1bee7'
          }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              background: idx === 0 ? '#ffd700' : idx === 1 ? '#c0c0c0' : '#cd7f32',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '12px',
              fontSize: '14px',
              fontWeight: 'bold',
              color: '#fff'
            }}>
              {idx + 1}
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{leader.role_name}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                领袖指数: {(leader.leadership_score * 100).toFixed(1)}%
              </div>
            </div>
            <div style={{
              padding: '4px 8px',
              borderRadius: '12px',
              background: '#9c27b0',
              color: 'white',
              fontSize: '11px'
            }}>
              指数: {(leader.leadership_score * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>

      {/* 最易受影响 */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '12px', color: '#ff9800' }}>
          🎯 易受影响者 (最容易被影响的角色)
        </div>
        {mostInfluenced.map((influenced) => (
          <div key={influenced.role_id} style={{
            display: 'flex',
            alignItems: 'center',
            padding: '12px',
            marginBottom: '8px',
            borderRadius: '8px',
            background: '#fff3e0',
            border: '1px solid #ffcc80'
          }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{influenced.role_name}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                受影响程度: {(influenced.receptivity_score * 100).toFixed(1)}%
              </div>
            </div>
            <div style={{
              padding: '4px 8px',
              borderRadius: '12px',
              background: '#ff9800',
              color: 'white',
              fontSize: '11px'
            }}>
              指数: {(influenced.receptivity_score * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>

      {/* 影响力矩阵 */}
      <div>
        <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '12px', color: '#1976d2' }}>
          🔗 影响力关系
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {network.edges.slice(0, 10).map((edge, idx) => {
            const source = network.nodes.find(n => n.id === edge.source);
            const target = network.nodes.find(n => n.id === edge.target);
            return (
              <div key={idx} style={{
                padding: '8px 12px',
                borderRadius: '8px',
                background: edge.type === 'support' ? '#e8f5e9' : edge.type === 'oppose' ? '#ffebee' : '#f5f5f5',
                fontSize: '12px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <span style={{ fontWeight: 'bold' }}>{source?.name || edge.source}</span>
                <span style={{ color: edge.type === 'support' ? '#4caf50' : edge.type === 'oppose' ? '#f44336' : '#666' }}>
                  {edge.type === 'support' ? '→' : edge.type === 'oppose' ? '⇥' : '―'}
                </span>
                <span>{target?.name || edge.target}</span>
                <span style={{ color: '#999', fontSize: '10px' }}>({(edge.weight * 100).toFixed(0)}%)</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// ============ 收敛趋势组件 ============
const ConvergenceTrendView: React.FC<{
  trend: number[];
  converged: boolean;
}> = ({ trend, converged }) => {
  if (!trend || trend.length === 0) {
    return (
      <div style={{ padding: '20px', textAlign: 'center', color: '#888' }}>
        暂无收敛趋势数据
      </div>
    );
  }

  const maxVal = Math.max(...trend, 0.85);
  const height = 120;

  return (
    <div style={{ padding: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '16px' }}>
        {converged ? (
          <span style={{
            padding: '4px 12px',
            borderRadius: '16px',
            background: '#4caf50',
            color: 'white',
            fontSize: '12px',
            fontWeight: 'bold'
          }}>
            ✓ 已收敛
          </span>
        ) : (
          <span style={{
            padding: '4px 12px',
            borderRadius: '16px',
            background: '#ff9800',
            color: 'white',
            fontSize: '12px'
          }}>
            迭代中
          </span>
        )}
      </div>

      {/* 趋势图 */}
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: '8px', height: `${height}px`, padding: '8px 0' }}>
        {trend.map((val, idx) => (
          <div key={idx} style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '4px'
          }}>
            <div style={{
              width: '100%',
              height: `${(val / maxVal) * (height - 30)}px`,
              background: val >= 0.85 ? '#4caf50' : val >= 0.7 ? '#ff9800' : '#2196f3',
              borderRadius: '4px 4px 0 0',
              transition: 'height 0.3s ease'
            }} />
            <span style={{ fontSize: '10px', color: '#666' }}>R{idx + 2}</span>
          </div>
        ))}
      </div>

      {/* 阈值线说明 */}
      <div style={{ marginTop: '12px', fontSize: '12px', color: '#666' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '12px', height: '12px', background: '#4caf50', borderRadius: '2px' }} />
          <span>≥ 85% (收敛)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '12px', height: '12px', background: '#ff9800', borderRadius: '2px' }} />
          <span>≥ 70% (接近收敛)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '12px', height: '12px', background: '#2196f3', borderRadius: '2px' }} />
          <span>&lt; 70% (继续迭代)</span>
        </div>
      </div>
    </div>
  );
};

// ============ 结论组件 ============
const ConclusionPanel: React.FC<{
  conclusion: ReactionChainConclusion;
}> = ({ conclusion }) => {
  return (
    <div style={{ padding: '16px' }}>
      {/* 统计信息 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '20px' }}>
        <div style={{
          padding: '16px',
          borderRadius: '8px',
          background: '#e3f2fd',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
            {conclusion.total_reactions}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>总反应数</div>
        </div>
        <div style={{
          padding: '16px',
          borderRadius: '8px',
          background: '#e8f5e9',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#388e3c' }}>
            {conclusion.rounds_executed}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>执行轮次</div>
        </div>
        <div style={{
          padding: '16px',
          borderRadius: '8px',
          background: conclusion.converged ? '#e8f5e9' : '#fff3e0',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: conclusion.converged ? '#388e3c' : '#ff9800' }}>
            {conclusion.converged ? '✓' : '○'}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {conclusion.converged ? '已收敛' : '未收敛'}
          </div>
        </div>
      </div>

      {/* 意见领袖 */}
      {conclusion.opinion_leaders && conclusion.opinion_leaders.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '12px', color: '#9c27b0' }}>
            🏆 意见领袖
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {conclusion.opinion_leaders.map((leader: any, idx: number) => (
              <div key={idx} style={{
                padding: '8px 12px',
                borderRadius: '8px',
                background: '#f3e5f5',
                fontSize: '12px'
              }}>
                {leader.role_name} ({(leader.leadership_score * 100).toFixed(0)}%)
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 关键张力 */}
      {conclusion.key_tensions && conclusion.key_tensions.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '12px', color: '#f44336' }}>
            ⚡ 关键张力
          </div>
          {conclusion.key_tensions.map((tension, idx) => (
            <div key={idx} style={{
              padding: '12px',
              marginBottom: '8px',
              borderRadius: '8px',
              background: '#ffebee',
              borderLeft: `3px solid ${tension.severity === '高' ? '#f44336' : '#ff9800'}`
            }}>
              <div style={{ fontWeight: 'bold', fontSize: '13px', color: '#333' }}>
                {tension.type}
              </div>
              <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                {tension.description}
              </div>
              {tension.involved_roles && (
                <div style={{ fontSize: '11px', color: '#888', marginTop: '4px' }}>
                  涉及: {tension.involved_roles.slice(0, 5).join(', ')}
                  {tension.involved_roles.length > 5 && ` +${tension.involved_roles.length - 5}`}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* 共识 */}
      {conclusion.consensus && conclusion.consensus.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '12px', color: '#4caf50' }}>
            ✓ 共识点
          </div>
          {conclusion.consensus.map((point, idx) => (
            <div key={idx} style={{
              padding: '8px 12px',
              marginBottom: '4px',
              borderRadius: '4px',
              background: '#e8f5e9',
              fontSize: '13px',
              color: '#333'
            }}>
              {point}
            </div>
          ))}
        </div>
      )}

      {/* 趋势评估 */}
      <div>
        <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '8px', color: '#1976d2' }}>
          📈 趋势评估
        </div>
        <div style={{
          padding: '12px',
          borderRadius: '8px',
          background: '#f5f5f5',
          fontSize: '13px',
          color: '#666'
        }}>
          {conclusion.trend_assessment}
        </div>
      </div>
    </div>
  );
};

// ============ 状态演变组件 ============
const StateEvolutionView: React.FC<{
  stateEvolution: StateSnapshot[];
}> = ({ stateEvolution }) => {
  if (!stateEvolution || stateEvolution.length === 0) {
    return null;
  }

  return (
    <div style={{ padding: '16px' }}>
      <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '12px', color: '#1976d2' }}>
        📊 状态演变
      </div>
      {stateEvolution.map((snapshot, idx) => (
        <div key={idx} style={{
          padding: '12px',
          marginBottom: '8px',
          borderRadius: '8px',
          background: '#f5f5f5',
          borderLeft: '3px solid #1976d2'
        }}>
          <div style={{ fontWeight: 'bold', fontSize: '13px', color: '#1976d2', marginBottom: '8px' }}>
            {snapshot.time}
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginBottom: '8px' }}>
            <div style={{ fontSize: '11px' }}>
              平均置信度: <b>{(snapshot.metrics.average_confidence * 100).toFixed(1)}%</b>
            </div>
            <div style={{ fontSize: '11px' }}>
              积极情绪比例: <b>{(snapshot.metrics.positive_emotion_ratio * 100).toFixed(1)}%</b>
            </div>
          </div>
          {snapshot.changes.length > 0 && (
            <div style={{ fontSize: '11px', color: '#666' }}>
              变化: {snapshot.changes.slice(0, 3).join('; ')}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

// ============ 主组件 ============
export const ReactionChainView: React.FC<{
  result: EnhancedReactionChainResult;
}> = ({ result }) => {
  const [activeTab, setActiveTab] = useState<'timeline' | 'reactions' | 'evolution' | 'influence' | 'convergence' | 'conclusion'>('timeline');
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
  const [expandedReactions, setExpandedReactions] = useState<Set<string>>(new Set());

  const toggleReaction = (id: string) => {
    const newSet = new Set(expandedReactions);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setExpandedReactions(newSet);
  };

  const tabs = [
    { id: 'timeline', label: '时间线', count: result.timeline?.length || 0 },
    { id: 'reactions', label: '各方反应', count: result.all_reactions?.length || 0 },
    { id: 'evolution', label: '演变趋势', count: Object.keys(result.evolution || {}).length },
    { id: 'influence', label: '影响力', count: result.influence_network?.total_relations || 0 },
    { id: 'convergence', label: '收敛', count: result.convergence_trend?.length || 0 },
    { id: 'conclusion', label: '结论', count: 0 }
  ] as const;

  return (
    <div style={{ padding: '20px' }}>
      {/* 标题 */}
      <div style={{ marginBottom: '20px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#333', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
          🔗 反应链分析
          {result.converged && (
            <span style={{
              padding: '2px 8px',
              borderRadius: '12px',
              background: '#4caf50',
              color: 'white',
              fontSize: '12px',
              fontWeight: 'normal'
            }}>
              已收敛
            </span>
          )}
        </h2>
        <div style={{ fontSize: '14px', color: '#666', marginTop: '4px' }}>
          {result.title} - 共 {result.total_rounds} 轮迭代
        </div>
      </div>

      {/* 标签页 */}
      <div style={{
        display: 'flex',
        gap: '8px',
        marginBottom: '20px',
        borderBottom: '1px solid #e0e0e0',
        paddingBottom: '12px',
        overflowX: 'auto'
      }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderRadius: '20px',
              background: activeTab === tab.id ? '#1976d2' : '#f0f0f0',
              color: activeTab === tab.id ? '#fff' : '#666',
              fontSize: '13px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              whiteSpace: 'nowrap'
            }}
          >
            {tab.label}
            {tab.count > 0 && (
              <span style={{
                marginLeft: '6px',
                padding: '2px 6px',
                borderRadius: '10px',
                background: activeTab === tab.id ? 'rgba(255,255,255,0.3)' : '#ccc',
                fontSize: '11px'
              }}>
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* 内容区域 */}
      <div style={{ minHeight: '400px' }}>
        {activeTab === 'timeline' && (
          <div>
            {/* 状态演变概览 */}
            {result.state_evolution && result.state_evolution.length > 0 && (
              <StateEvolutionView stateEvolution={result.state_evolution} />
            )}
            {/* 时间线详情 */}
            {result.timeline?.map(event => (
              <TimelineNode
                key={event.id}
                event={event}
                isActive={selectedEvent === event.id}
                onClick={() => setSelectedEvent(selectedEvent === event.id ? null : event.id)}
              />
            ))}
          </div>
        )}

        {activeTab === 'reactions' && (
          <div>
            {/* 按轮次分组显示 */}
            {Array.from({ length: result.total_rounds }, (_, i) => i + 1).map(roundNum => (
              <div key={roundNum} style={{ marginBottom: '24px' }}>
                <div style={{
                  fontWeight: 'bold',
                  fontSize: '14px',
                  color: '#1976d2',
                  marginBottom: '12px',
                  paddingBottom: '8px',
                  borderBottom: '1px solid #e0e0e0'
                }}>
                  第 {roundNum} 轮反应
                </div>
                {result.all_reactions
                  ?.filter(r => r.round_number === roundNum)
                  .map(reaction => (
                    <ReactionCard
                      key={`${reaction.role_id}-${reaction.round_number}`}
                      reaction={reaction}
                      isExpanded={expandedReactions.has(`${reaction.role_id}-${reaction.round_number}`)}
                      onToggle={() => toggleReaction(`${reaction.role_id}-${reaction.round_number}`)}
                    />
                  ))}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'evolution' && (
          <EvolutionChart evolution={result.evolution || {}} />
        )}

        {activeTab === 'influence' && (
          <InfluenceNetworkView
            network={result.influence_network || { nodes: [], edges: [], total_relations: 0 }}
            opinionLeaders={result.opinion_leaders || []}
            mostInfluenced={result.most_influenced || []}
          />
        )}

        {activeTab === 'convergence' && (
          <ConvergenceTrendView
            trend={result.convergence_trend || []}
            converged={result.converged || false}
          />
        )}

        {activeTab === 'conclusion' && (
          <ConclusionPanel conclusion={result.conclusion || {}} />
        )}
      </div>
    </div>
  );
};

export default ReactionChainView;
