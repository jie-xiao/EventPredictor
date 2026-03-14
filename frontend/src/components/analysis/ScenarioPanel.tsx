/**
 * ScenarioPanel.tsx
 *
 * 情景推演面板 - 展示多个可能的未来发展情景
 */
import { useState, useEffect } from 'react';
import {
  GitBranch,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  CheckCircle,
  Clock,
  ChevronRight,
  Lightbulb,
  Target
} from 'lucide-react';
import { api, ScenarioResult, Scenario } from '../../services/api';

interface ScenarioPanelProps {
  eventId: string;
  eventTitle: string;
  eventDescription: string;
  eventCategory?: string;
  eventImportance?: number;
  analysisResult?: any;
  onScenarioSelect?: (scenario: Scenario) => void;
}

const scenarioColors = {
  optimistic: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    text: 'text-emerald-400',
    icon: TrendingUp
  },
  baseline: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
    icon: Minus
  },
  pessimistic: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    text: 'text-red-400',
    icon: TrendingDown
  }
};

function getScenarioType(scenarioName: string): keyof typeof scenarioColors {
  const name = scenarioName.toLowerCase();
  if (name.includes('乐观') || name.includes('optimistic') || name.includes('积极')) {
    return 'optimistic';
  }
  if (name.includes('悲观') || name.includes('pessimistic') || name.includes('恶化')) {
    return 'pessimistic';
  }
  return 'baseline';
}

export default function ScenarioPanel({
  eventId,
  eventTitle,
  eventDescription,
  eventCategory = 'Other',
  eventImportance = 3,
  analysisResult,
  onScenarioSelect
}: ScenarioPanelProps) {
  const [scenarios, setScenarios] = useState<ScenarioResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<Scenario | null>(null);
  const [expandedScenario, setExpandedScenario] = useState<string | null>(null);

  useEffect(() => {
    generateScenarios();
  }, [eventId]);

  const generateScenarios = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.generateScenarios({
        event_id: eventId,
        title: eventTitle,
        description: eventDescription,
        category: eventCategory,
        importance: eventImportance,
        num_scenarios: 3,
        analysis_result: analysisResult
      });
      setScenarios(result);
      // 自动选择最可能的情景
      const mostLikely = result.scenarios.find(
        s => s.name === result.most_likely_scenario
      );
      if (mostLikely) {
        setSelectedScenario(mostLikely);
      }
    } catch (err: any) {
      setError(err.message || '情景推演生成失败');
    } finally {
      setLoading(false);
    }
  };

  const handleScenarioClick = (scenario: Scenario) => {
    setSelectedScenario(scenario);
    onScenarioSelect?.(scenario);
    setExpandedScenario(expandedScenario === scenario.id ? null : scenario.id);
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center py-12">
          <div className="flex flex-col items-center gap-4">
            <div className="relative">
              <div className="w-12 h-12 border-4 border-primary-cyan/20 border-t-primary-cyan rounded-full animate-spin" />
              <GitBranch className="absolute inset-0 m-auto w-5 h-5 text-primary-cyan" />
            </div>
            <p className="text-text-muted">正在生成情景推演...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-400">
            <AlertTriangle className="w-5 h-5" />
            <span>{error}</span>
          </div>
          <button
            onClick={generateScenarios}
            className="mt-3 text-sm text-red-400 hover:text-red-300 underline"
          >
            重试
          </button>
        </div>
      </div>
    );
  }

  if (!scenarios) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* 标题 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <GitBranch className="w-5 h-5 text-primary-cyan" />
          <h3 className="text-lg font-semibold text-text-primary">情景推演</h3>
        </div>
        <button
          onClick={generateScenarios}
          className="text-sm text-primary-cyan hover:text-primary-cyan/80 transition-colors"
        >
          重新生成
        </button>
      </div>

      {/* 整体评估 */}
      <div className="bg-[#0F172A] border border-[#1E293B] rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Target className="w-5 h-5 text-amber-400 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-text-secondary mb-2">{scenarios.overall_assessment}</p>
            <div className="flex items-center gap-4 text-xs">
              <span className="text-text-muted">
                最可能情景:
                <span className="ml-1 text-primary-cyan font-medium">
                  {scenarios.most_likely_scenario}
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* 情景卡片 */}
      <div className="space-y-3">
        {scenarios.scenarios.map((scenario) => {
          const type = getScenarioType(scenario.name);
          const colors = scenarioColors[type];
          const Icon = colors.icon;
          const isSelected = selectedScenario?.id === scenario.id;
          const isExpanded = expandedScenario === scenario.id;

          return (
            <div
              key={scenario.id}
              className={`
                ${colors.bg} ${colors.border} border rounded-lg overflow-hidden
                transition-all cursor-pointer
                ${isSelected ? 'ring-2 ring-primary-cyan/50' : ''}
              `}
              onClick={() => handleScenarioClick(scenario)}
            >
              {/* 情景头部 */}
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon className={`w-5 h-5 ${colors.text}`} />
                    <span className="font-medium text-text-primary">{scenario.name}</span>
                    {scenario.name === scenarios.most_likely_scenario && (
                      <span className="px-2 py-0.5 text-xs bg-amber-500/20 text-amber-400 rounded">
                        最可能
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="text-right">
                      <span className="text-xs text-text-muted">概率</span>
                      <span className={`ml-1 font-mono ${colors.text}`}>
                        {(scenario.probability * 100).toFixed(0)}%
                      </span>
                    </div>
                    <ChevronRight
                      className={`w-4 h-4 text-text-muted transition-transform ${isExpanded ? 'rotate-90' : ''}`}
                    />
                  </div>
                </div>
                <p className="text-sm text-text-secondary">{scenario.description}</p>
              </div>

              {/* 展开详情 */}
              {isExpanded && (
                <div className="border-t border-[#1E293B] p-4 space-y-4">
                  {/* 时间线 */}
                  <div>
                    <h4 className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">
                      发展路径
                    </h4>
                    <div className="space-y-2">
                      {scenario.steps.map((step, idx) => (
                        <div key={idx} className="flex items-start gap-3">
                          <div className="flex flex-col items-center">
                            <div className={`w-2 h-2 rounded-full ${colors.bg} ${colors.border} border`} />
                            {idx < scenario.steps.length - 1 && (
                              <div className="w-px h-6 bg-[#1E293B]" />
                            )}
                          </div>
                          <div className="flex-1 pb-2">
                            <div className="flex items-center gap-2 mb-1">
                              <Clock className="w-3 h-3 text-text-muted" />
                              <span className="text-xs text-text-muted">{step.time}</span>
                              <span className="text-xs text-text-muted">
                                ({(step.probability * 100).toFixed(0)}%)
                              </span>
                            </div>
                            <p className="text-sm text-text-secondary">{step.description}</p>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {step.key_events.map((event, i) => (
                                <span
                                  key={i}
                                  className="px-2 py-0.5 text-xs bg-[#1E293B] text-text-muted rounded"
                                >
                                  {event}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 关键因素 */}
                  <div>
                    <h4 className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">
                      关键影响因素
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {scenario.key_factors.map((factor, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 text-xs bg-[#1E293B] text-text-secondary rounded"
                        >
                          {factor}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* 潜在结果 */}
                  <div>
                    <h4 className="text-xs font-medium text-text-muted uppercase tracking-wider mb-2">
                      潜在结果
                    </h4>
                    <ul className="space-y-1">
                      {scenario.potential_outcomes.map((outcome, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm text-text-secondary">
                          <CheckCircle className="w-3 h-3 text-primary-cyan" />
                          {outcome}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* 关键不确定因素 */}
      <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-amber-400 mb-2">关键不确定因素</h4>
            <ul className="space-y-1">
              {scenarios.key_uncertainties.map((uncertainty, idx) => (
                <li key={idx} className="text-sm text-text-secondary flex items-center gap-2">
                  <span className="w-1 h-1 bg-amber-400 rounded-full" />
                  {uncertainty}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* 建议 */}
      <div className="bg-primary-cyan/5 border border-primary-cyan/20 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Lightbulb className="w-5 h-5 text-primary-cyan mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-primary-cyan mb-1">战略建议</h4>
            <p className="text-sm text-text-secondary">{scenarios.recommendation}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
