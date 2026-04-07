// API配置
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8005';

// 事件类型
export interface WorldMonitorEvent {
  id: string;
  title: string;
  description: string;
  category: string;
  category_label?: string;  // 中文分类标签
  severity: number;
  location: {
    country: string;
    region: string;
    lat?: number;
    lon?: number;
  };
  timestamp: string;
  source: string;
  source_label?: string;  // 中文来源名称
  entities?: string[];
  sentiment?: string;
}

// 角色类型
export interface Role {
  id: string;
  name: string;
  category: string;
  description: string;
  focus_points: string[];
}

// 角色类别 - 后端返回的是roles字符串数组
export interface RoleCategory {
  id: string;
  name: string;
  description?: string;
  roles: string[];
}

// 分析请求
export interface AnalysisRequest {
  event_id: string;
  title: string;
  description: string;
  category: string;
  importance: number;
  timestamp?: string;
  roles: string[];
  depth: string;
}

// 辩论分析请求
export interface DebateRequest extends AnalysisRequest {
  // 继承自AnalysisRequest
}

// 角色分析结果
export interface RoleAnalysis {
  role_id: string;
  role_name: string;
  category?: string;
  stance: string;
  reaction: {
    emotion: string;
    action: string;
    statement: string;
  };
  impact: {
    economic: string;
    political: string;
    social: string;
  };
  timeline: {
    time: string;
    event: string;
    probability: number;
  }[];
  confidence: number;
  reasoning: string;
  supports?: string[];
  challenges?: string[];
  round?: string;
}

// 辩论轮次
export interface DebateRound {
  round_number: number;
  round_type: string;  // initial, cross_review, rebuttal, synthesis
  analyses: RoleAnalysis[];
  timestamp: string;
}

// 分析结果
export interface AnalysisResult {
  event_id: string;
  title: string;
  description: string;
  category: string;
  analyses: RoleAnalysis[];
  cross_analysis?: {
    conflicts: CrossAnalysisItem[];
    synergies: CrossAnalysisItem[];
    consensus: string[];
    agreements?: AgreementItem[];
    key_tensions?: KeyTension[];
  };
  prediction?: {
    trend: string;
    confidence: number;
    summary: string;
    timeline: { time: string; event: string; probability: number }[];
    recommended_actions?: string[];
    key_insights?: string[];
  };
  overall_confidence: number;
  timestamp?: string;
}

// 交叉分析项
export interface CrossAnalysisItem {
  type?: string;
  description: string;
  severity?: string;
  potential?: string;
  roles?: string[];
  point?: string;
}

// 共识项
export interface AgreementItem {
  role1: string;
  role2: string;
  point: string;
  strength: number;
}

// 关键张力
export interface KeyTension {
  title: string;
  description: string;
  resolution: string;
}

// 辩论分析结果
export interface DebateResult extends AnalysisResult {
  depth: string;
  rounds: DebateRound[];
  agreement_scores: Record<string, number>;
  key_conflicts: ConflictItem[];
  consensus_points: string[];
}

// 冲突项
export interface ConflictItem {
  from_role?: string;
  challenge?: string;
  type?: string;
  description?: string;
  severity?: string;
}

// 分析深度选项
export interface AnalysisDepth {
  id: string;
  name: string;
  description: string;
  rounds?: number;
  estimated_time?: string;
}

// 事件摘要
export interface EventSummary {
  id: string;
  title: string;
  description: string;
  category: string;
  severity: number;
  location: string;
  timestamp: string;
  source: string;
}

// 筛选器
export interface EventFilters {
  category: string;
  timeRange: string;
  country: string;
}

// API服务函数
export const api = {
  // 获取内置事件数据
  async getPresetEvents(limit = 50, timeRange = 'all', category?: string): Promise<WorldMonitorEvent[]> {
    const params = new URLSearchParams();
    params.set('limit', String(limit));
    params.set('time_range', timeRange);
    if (category) params.set('category', category);

    const response = await fetch(`${API_BASE_URL}/api/v1/data/events?${params}`);
    if (!response.ok) throw new Error('Failed to fetch preset events');
    const data = await response.json();
    return data.events || [];
  },

  // 获取内置事件类别
  async getPresetCategories(): Promise<{ categories: string[]; total: number }> {
    const response = await fetch(`${API_BASE_URL}/api/v1/data/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    return response.json();
  },

  // 获取WorldMonitor事件
  async getWorldMonitorEvents(filters?: Partial<EventFilters>): Promise<WorldMonitorEvent[]> {
    const params = new URLSearchParams();
    if (filters?.category) params.set('category', filters.category);
    if (filters?.timeRange) params.set('time_range', filters.timeRange);
    params.set('limit', '50');

    const response = await fetch(`${API_BASE_URL}/api/v1/worldmonitor/events?${params}`);
    if (!response.ok) throw new Error('Failed to fetch events');
    const data = await response.json();
    return data.events || [];
  },

  // 获取事件摘要列表
  async getEventList(page = 1, pageSize = 20): Promise<{ events: EventSummary[]; total: number }> {
    const response = await fetch(`${API_BASE_URL}/api/v1/events?page=${page}&page_size=${pageSize}`);
    if (!response.ok) throw new Error('Failed to fetch events');
    return response.json();
  },

  // 获取单个事件详情
  async getEvent(eventId: string): Promise<EventSummary> {
    const response = await fetch(`${API_BASE_URL}/api/v1/events/${eventId}`);
    if (!response.ok) throw new Error('Failed to fetch event');
    return response.json();
  },

  // 获取角色列表
  async getRoles(): Promise<{ roles: Role[]; categories: string[] }> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/roles`);
    if (!response.ok) throw new Error('Failed to fetch roles');
    return response.json();
  },

  // 获取角色类别
  async getRoleCategories(): Promise<RoleCategory[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    const data = await response.json();
    return data.categories;
  },

  // 执行多Agent分析
  async analyze(request: AnalysisRequest): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/multi`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Analysis failed' }));
      throw new Error(error.detail || 'Analysis failed');
    }
    return response.json();
  },

  // 执行辩论式分析
  async analyzeDebate(request: DebateRequest): Promise<DebateResult> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/debate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Debate analysis failed' }));
      throw new Error(error.detail || 'Debate analysis failed');
    }
    return response.json();
  },

  // 获取分析深度选项
  async getAnalysisDepths(): Promise<AnalysisDepth[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/depths`);
    if (!response.ok) {
      // 回退到辩论深度API
      const debateResponse = await fetch(`${API_BASE_URL}/api/v1/analysis/debate/depths`);
      if (!debateResponse.ok) {
        return [
          { id: 'simple', name: '快速分析', description: '简洁的分析要点' },
          { id: 'standard', name: '标准分析', description: '全面的分析' },
          { id: 'detailed', name: '深度分析', description: '详细的分析' }
        ];
      }
      const data = await debateResponse.json();
      return data.depths;
    }
    const data = await response.json();
    return data.depths;
  },

  // 获取辩论深度选项
  async getDebateDepths(): Promise<AnalysisDepth[]> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/debate/depths`);
    if (!response.ok) {
      return [
        { id: 'quick', name: '快速分析', description: '1轮分析', rounds: 1, estimated_time: '30秒' },
        { id: 'standard', name: '标准分析', description: '2轮分析，包含交叉审视', rounds: 2, estimated_time: '1分钟' },
        { id: 'deep', name: '深度分析', description: '3轮分析，包含反驳', rounds: 3, estimated_time: '2分钟' }
      ];
    }
    const data = await response.json();
    return data.depths;
  },

  // 获取WorldMonitor摘要
  async getWorldMonitorSummary(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/v1/worldmonitor/summary`);
    if (!response.ok) throw new Error('Failed to fetch summary');
    return response.json();
  },

  // 情景推演
  async generateScenarios(request: {
    event_id: string;
    title: string;
    description: string;
    category?: string;
    importance?: number;
    timestamp?: string;
    num_scenarios?: number;
    analysis_result?: AnalysisResult;
  }): Promise<ScenarioResult> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/scenarios`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Scenario generation failed' }));
      throw new Error(error.detail || 'Scenario generation failed');
    }
    return response.json();
  },

  // 优化情景
  async refineScenario(request: {
    event_id: string;
    title: string;
    description: string;
    scenario_id: string;
    new_information: string;
  }): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/scenarios/refine`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Scenario refinement failed' }));
      throw new Error(error.detail || 'Scenario refinement failed');
    }
    return response.json();
  },

  // 获取情景模板
  async getScenarioTemplates(): Promise<{ templates: ScenarioTemplate[] }> {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/scenarios/templates`);
    if (!response.ok) throw new Error('Failed to fetch scenario templates');
    return response.json();
  }
};

// 情景推演类型定义
export interface ScenarioStep {
  time: string;
  description: string;
  probability: number;
  key_events: string[];
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  probability: number;
  steps: ScenarioStep[];
  key_factors: string[];
  potential_outcomes: string[];
}

export interface ScenarioResult {
  event_id: string;
  scenarios: Scenario[];
  most_likely_scenario: string;
  overall_assessment: string;
  key_uncertainties: string[];
  recommendation: string;
  generated_at: string;
}

export interface ScenarioTemplate {
  id: string;
  name: string;
  description: string;
  scenarios: string[];
  timeframes: string[];
}

// ============ 反应链类型定义 ============

// 反应链请求
export interface ReactionChainRequest {
  event_id: string;
  title: string;
  description: string;
  category?: string;
  importance?: number;
  timestamp?: string;
  roles: string[];
  max_rounds?: number;
  convergence_threshold?: number;
}

// 单个反应
export interface ChainReaction {
  emotion: string;
  action: string;
  statement: string;
  stance_change?: string;
  confidence?: number;
  context_aware?: boolean;
}

// 反应轮次
export interface ReactionRoundData {
  round_number: number;
  role_id: string;
  role_name: string;
  reaction: ChainReaction;
  affected_by: string[];
  timestamp: string;
}

// 时间线事件
export interface TimelineEventData {
  id: string;
  time: string;
  event_type: string;
  description: string;
  involved_roles: string[];
  details: Record<string, any>;
  timestamp: string;
}

// 反应演变
export interface ReactionEvolution {
  role_name: string;
  rounds: number;
  emotion_evolution: string[];
  action_evolution: string[];
  confidence_evolution?: number[];
  confidence_trend?: 'increasing' | 'decreasing' | 'stable';
  stance_changes: string[];
  summary: string;
}

// 影响力网络节点
export interface InfluenceNode {
  id: string;
  name: string;
  outgoing_influence: number;
  incoming_influence: number;
  opinion_leadership: number;
  receptivity: number;
}

// 影响力网络边
export interface InfluenceEdge {
  source: string;
  target: string;
  weight: number;
  type: 'support' | 'oppose' | 'neutral';
  count: number;
}

// 影响力网络
export interface InfluenceNetwork {
  nodes: InfluenceNode[];
  edges: InfluenceEdge[];
  total_relations: number;
}

// 意见领袖
export interface OpinionLeader {
  role_id: string;
  role_name: string;
  leadership_score: number;
  outgoing_influence: number;
}

// 易受影响者
export interface MostInfluenced {
  role_id: string;
  role_name: string;
  receptivity_score: number;
  incoming_influence: number;
}

// 状态快照
export interface StateSnapshot {
  time: string;
  metrics: {
    average_confidence: number;
    positive_emotion_ratio: number;
    action_diversity: number;
    total_roles: number;
  };
  changes: string[];
}

// 反应链结论
export interface ReactionChainConclusion {
  total_reactions: number;
  rounds_executed: number;
  converged?: boolean;
  final_reactions: Record<string, { role_name: string; reaction: ChainReaction }>;
  key_tensions: { type: string; description: string; severity: string; involved_roles?: string[] }[];
  consensus: string[];
  evolution_summary: Record<string, ReactionEvolution>;
  opinion_leaders?: OpinionLeader[];
  influence_summary?: {
    total_nodes: number;
    network_density: number;
  };
  trend_assessment: string;
}

// 反应链结果
export interface ReactionChainResult {
  event_id: string;
  title: string;
  description: string;
  category: string;
  total_rounds: number;
  converged?: boolean;
  timeline: TimelineEventData[];
  timeline_tree?: any;
  state_evolution?: StateSnapshot[];
  evolution: Record<string, ReactionEvolution>;
  all_reactions: ReactionRoundData[];
  influence_network?: InfluenceNetwork;
  opinion_leaders?: OpinionLeader[];
  most_influenced?: MostInfluenced[];
  convergence_trend?: number[];
  conclusion: ReactionChainConclusion;
  timestamp: string;
}

// 事件链类型
export interface ChainEvent {
  event_id: string;
  title: string;
  description: string;
  category?: string;
  importance?: number;
  timestamp?: string;
}

export interface EventChainRequest {
  events: ChainEvent[];
  roles: string[];
  max_rounds_per_event?: number;
}

export interface EventChainResult {
  event_count: number;
  events: string[];
  chain_results: any[];
  inter_event_analysis: any;
  timeline: any[];
  conclusion: any;
  timestamp: string;
}

// 分析深度选项（反应链）
export interface ChainDepth {
  id: string;
  name: string;
  description: string;
  rounds: number;
  estimated_time: string;
}

// 分析模式
export interface AnalysisMode {
  id: string;
  name: string;
  description: string;
  icon: string;
}

// ============ 反应链API函数 ============

// 执行反应链分析
export async function analyzeReactionChain(request: ReactionChainRequest): Promise<ReactionChainResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/reaction-chain/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Reaction chain analysis failed' }));
    throw new Error(error.detail || 'Reaction chain analysis failed');
  }
  return response.json();
}

// 执行事件链分析
export async function analyzeEventChain(request: EventChainRequest): Promise<EventChainResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/reaction-chain/event-chain`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Event chain analysis failed' }));
    throw new Error(error.detail || 'Event chain analysis failed');
  }
  return response.json();
}

// 获取反应链深度选项
export async function getReactionChainDepths(): Promise<ChainDepth[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/reaction-chain/depths`);
  if (!response.ok) {
    return [
      { id: '2', name: '快速分析', description: '2轮反应链', rounds: 2, estimated_time: '30秒' },
      { id: '3', name: '标准分析', description: '3轮反应链', rounds: 3, estimated_time: '1分钟' },
      { id: '5', name: '深度分析', description: '5轮反应链', rounds: 5, estimated_time: '2分钟' }
    ];
  }
  const data = await response.json();
  return data.depths;
}

// 获取分析模式
export async function getAnalysisModes(): Promise<AnalysisMode[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/reaction-chain/modes`);
  if (!response.ok) {
    return [
      { id: 'reaction_chain', name: '反应链模式', description: '分析单事件中各方反应的相互影响', icon: 'link' },
      { id: 'event_chain', name: '事件链模式', description: '分析多个相关事件的串联影响', icon: 'sequence' }
    ];
  }
  const data = await response.json();
  return data.modes;
}

// 时间线预测请求
export interface TimelinePredictionRequest {
  event: {
    id: string;
    title: string;
    description: string;
    category?: string;
    importance?: number;
  };
  roles: string[];
  prediction_horizon?: number;
}

// 时间线预测结果
export interface TimelinePredictionResult {
  event_id: string;
  event_title: string;
  prediction_horizon: number;
  predictions: Array<{
    day: number;
    time: string;
    predicted_state: string;
    confidence: number;
    key_actors: string[];
    potential_events: string[];
  }>;
  confidence_trend: number[];
  key_milestones: string[];
  potential_branches: Array<{
    id: string;
    name: string;
    description: string;
    probability: number;
  }>;
  overall_assessment: string;
  based_on_rounds: number;
  timestamp: string;
}

// 执行时间线预测
export async function predictTimeline(request: TimelinePredictionRequest): Promise<TimelinePredictionResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/reaction-chain/timeline-prediction`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Timeline prediction failed' }));
    throw new Error(error.detail || 'Timeline prediction failed');
  }
  return response.json();
}

// 获取收敛信息
export async function getConvergenceInfo(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/reaction-chain/convergence-info`);
  if (!response.ok) {
    return {
      description: '反应链会在各方法反应趋于稳定时自动收敛',
      default_threshold: 0.85
    };
  }
  return response.json();
}

// 获取影响力指标说明
export async function getInfluenceMetricsInfo(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/reaction-chain/influence-metrics`);
  if (!response.ok) {
    return {
      metrics: {
        opinion_leadership_score: { name: '意见领袖指数', description: '衡量一个角色对其他角色的影响力' },
        influence_receptivity_score: { name: '受影响程度指数', description: '衡量一个角色被其他角色影响的程度' }
      }
    };
  }
  return response.json();
}

// ============ P2: 知识图谱 API ============

// 实体类型
export interface KnowledgeGraphEntity {
  id: string;
  name: string;
  type: string;
  aliases?: string[];
  properties?: Record<string, any>;
  importance?: number;
  created_at?: string;
}

// 关系类型
export interface KnowledgeGraphRelation {
  id: string;
  source: string;
  target: string;
  type: string;
  weight?: number;
  properties?: Record<string, any>;
}

// 获取实体列表
export async function getEntities(params?: { type?: string; search?: string; limit?: number }): Promise<{ success: boolean; data: KnowledgeGraphEntity[] }> {
  const query = new URLSearchParams();
  if (params?.type) query.set('entity_type', params.type);
  if (params?.search) query.set('search', params.search);
  if (params?.limit) query.set('limit', String(params.limit));
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graph/entities?${query}`);
  return response.json();
}

// 获取关系列表
export async function getRelations(params?: { source_id?: string; target_id?: string; limit?: number }): Promise<any> {
  const query = new URLSearchParams();
  if (params?.source_id) query.set('source_id', params.source_id);
  if (params?.target_id) query.set('target_id', params.target_id);
  if (params?.limit) query.set('limit', String(params.limit));
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graph/relations?${query}`);
  return response.json();
}

// 创建实体
export async function createEntity(entity: { name: string; type: string; aliases?: string[]; properties?: any }): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graph/entities`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(entity)
  });
  return response.json();
}

// 创建关系
export async function createRelation(relation: { source_id: string; target_id: string; type: string; weight?: number }): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graph/relations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(relation)
  });
  return response.json();
}

// 从文本提取实体
export async function extractEntities(text: string, eventId?: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graph/extract`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, event_id: eventId })
  });
  return response.json();
}

// 获取图谱统计
export async function getKnowledgeGraphStats(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/knowledge-graph/statistics`);
  return response.json();
}

// ============ P2: 事件监控 API ============

// 告警规则
export interface MonitorRule {
  id: string;
  name: string;
  description?: string;
  enabled: boolean;
  severity: string;
  field: string;
  operator: string;
  value: string;
  cooldown_minutes: number;
}

// 告警
export interface MonitorAlert {
  id: string;
  rule_id: string;
  rule_name: string;
  severity: string;
  event_data: any;
  message: string;
  created_at: string;
  acknowledged: boolean;
}

// 获取规则列表
export async function getMonitorRules(): Promise<{ success: boolean; data: MonitorRule[] }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/monitor/rules`);
  return response.json();
}

// 创建规则
export async function createMonitorRule(rule: { name: string; severity: string; field: string; operator: string; value: string }): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/monitor/rules`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rule)
  });
  return response.json();
}

// 更新规则
export async function updateMonitorRule(ruleId: string, updates: Partial<MonitorRule>): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/monitor/rules/${ruleId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  });
  return response.json();
}

// 删除规则
export async function deleteMonitorRule(ruleId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/monitor/rules/${ruleId}`, {
    method: 'DELETE'
  });
  return response.json();
}

// 获取告警列表
export async function getMonitorAlerts(params?: { severity?: string; limit?: number }): Promise<any> {
  const query = new URLSearchParams();
  if (params?.severity) query.set('severity', params.severity);
  if (params?.limit) query.set('limit', String(params.limit));
  const response = await fetch(`${API_BASE_URL}/api/v1/monitor/alerts?${query}`);
  return response.json();
}

// 确认告警
export async function acknowledgeAlert(alertId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/monitor/alerts/${alertId}/acknowledge`, {
    method: 'POST'
  });
  return response.json();
}

// 获取监控统计
export async function getMonitorStats(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/v1/monitor/statistics`);
  return response.json();
}

// ============ P2.2: 高级分析引擎 API ============

// 高级分析请求
export interface AdvancedAnalysisRequest {
  title: string;
  description: string;
  category?: string;
  importance?: number;
  timestamp?: string;
  context?: Record<string, any>;
}

// 蒙特卡洛
export interface ScenarioVariable {
  name: string;
  description: string;
  distribution_type: string;
  params: Record<string, number>;
  impact_direction: number;
  weight: number;
}

export interface MonteCarloResult {
  n_simulations: number;
  probability_distribution: Record<string, number>;
  mean: number;
  std: number;
  CI_95: number[];
  CI_80: number[];
  sensitivity_analysis: Record<string, number>;
  trend: string;
  confidence: number;
  simulation_details: Array<Record<string, any>>;
  variables_used: ScenarioVariable[];
  assumptions: string[];
}

export interface MonteCarloResponse {
  event_title: string;
  result: MonteCarloResult;
  timestamp: string;
}

// 贝叶斯
export interface BayesianNodeResult {
  id: string;
  name: string;
  type: string;
  prior: number;
  posterior: number;
}

export interface BayesianResult {
  nodes: BayesianNodeResult[];
  edges: Array<{
    source_id: string;
    target_id: string;
    conditional_probability: number;
    relationship_type: string;
  }>;
  posteriors: Record<string, number>;
  main_hypothesis_posterior: number;
  evidence_impact: Record<string, number>;
  influence_diagram: {
    nodes: BayesianNodeResult[];
    edges: Array<{ source: string; target: string; strength: number; type: string }>;
  };
  reasoning: string;
}

export interface BayesianResponse {
  event_title: string;
  result: BayesianResult;
  timestamp: string;
}

// 因果
export interface CausalFactorResult {
  id: string;
  name: string;
  description: string;
  factor_type: string;
  direction: number;
  strength: number;
}

export interface CausalLinkResult {
  source_id: string;
  target_id: string;
  mechanism: string;
  strength: number;
  lag_time: string;
}

export interface CausalResult {
  factors: CausalFactorResult[];
  links: CausalLinkResult[];
  direct_effects: Record<string, number>;
  indirect_effects: Record<string, number>;
  total_effects: Record<string, number>;
  confounders: string[];
  causal_paths: Array<{
    from: string;
    to: string;
    path: Array<{ source: string; target: string; strength: number }>;
    strength: number;
  }>;
  graph_data: {
    nodes: Array<{
      id: string;
      name: string;
      type: string;
      direction: number;
      strength: number;
      is_confounder: boolean;
    }>;
    edges: Array<{
      source: string;
      target: string;
      strength: number;
      mechanism: string;
      lag_time: string;
    }>;
  };
}

export interface CausalResponse {
  event_title: string;
  result: CausalResult;
  timestamp: string;
}

// 集成
export interface MethodResult {
  method_name: string;
  trend: string;
  confidence: number;
  key_findings: string[];
  weight: number;
}

export interface EnsembleResult {
  methods: MethodResult[];
  unified_trend: string;
  unified_confidence: number;
  CI: number[];
  agreement_score: number;
  weighted_probabilities: Record<string, number>;
  method_weights: Record<string, number>;
  uncertainty_calibration: {
    cross_method_std: number;
    trend_entropy: number;
    n_methods: number;
    agreement_ratio: number;
  };
  recommendation: string;
  detailed_results: Record<string, any>;
}

export interface EnsembleResponse {
  event_title: string;
  result: EnsembleResult;
  timestamp: string;
}

// 方法信息
export interface AnalysisMethodInfo {
  id: string;
  name: string;
  description: string;
  endpoint: string;
}

// API 函数
export async function runMonteCarlo(
  request: AdvancedAnalysisRequest,
  nSimulations = 1000
): Promise<MonteCarloResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/analysis/advanced/monte-carlo?n_simulations=${nSimulations}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    }
  );
  if (!response.ok) throw new Error('Monte Carlo analysis failed');
  return response.json();
}

export async function runBayesian(request: AdvancedAnalysisRequest): Promise<BayesianResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/advanced/bayesian`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Bayesian analysis failed');
  return response.json();
}

export async function runCausal(request: AdvancedAnalysisRequest): Promise<CausalResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/advanced/causal`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Causal analysis failed');
  return response.json();
}

export async function runEnsemble(request: AdvancedAnalysisRequest): Promise<EnsembleResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/advanced/ensemble`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error('Ensemble analysis failed');
  return response.json();
}

export async function getAdvancedMethods(): Promise<{ methods: AnalysisMethodInfo[] }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/analysis/advanced/methods`);
  if (!response.ok) throw new Error('Failed to fetch methods');
  return response.json();
}
