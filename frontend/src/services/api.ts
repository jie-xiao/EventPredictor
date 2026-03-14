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
