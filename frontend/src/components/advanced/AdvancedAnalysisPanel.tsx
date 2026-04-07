import { useState, useCallback, lazy, Suspense } from 'react';
import { BarChart3, Network, GitBranch, Layers, Loader2, AlertCircle } from 'lucide-react';
import type { WorldMonitorEvent } from '../../services/api';
import {
  runEnsemble,
  runMonteCarlo,
  runBayesian,
  runCausal,
  type EnsembleResponse,
  type MonteCarloResponse,
  type BayesianResponse,
  type CausalResponse,
} from '../../services/api';

const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

type TabId = 'ensemble' | 'monte_carlo' | 'bayesian' | 'causal';

interface TabDef {
  id: TabId;
  name: string;
  icon: React.ReactNode;
}

const TABS: TabDef[] = [
  { id: 'ensemble', name: '集成预测', icon: <Layers className="w-4 h-4" /> },
  { id: 'monte_carlo', name: '蒙特卡洛', icon: <BarChart3 className="w-4 h-4" /> },
  { id: 'bayesian', name: '贝叶斯网络', icon: <Network className="w-4 h-4" /> },
  { id: 'causal', name: '因果推理', icon: <GitBranch className="w-4 h-4" /> },
];

interface Props {
  event: WorldMonitorEvent;
}

export default function AdvancedAnalysisPanel({ event }: Props) {
  const [activeTab, setActiveTab] = useState<TabId>('ensemble');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Results stored by method
  const [ensembleData, setEnsembleData] = useState<EnsembleResponse | null>(null);
  const [mcData, setMcData] = useState<MonteCarloResponse | null>(null);
  const [bayesData, setBayesData] = useState<BayesianResponse | null>(null);
  const [causalData, setCausalData] = useState<CausalResponse | null>(null);

  const requestPayload = {
    title: event.title,
    description: event.description,
    category: event.category,
    importance: event.severity,
    timestamp: event.timestamp,
  };

  const runAnalysis = useCallback(async (tab: TabId) => {
    setLoading(true);
    setError(null);
    try {
      switch (tab) {
        case 'ensemble': {
          if (ensembleData) break;
          const r = await runEnsemble(requestPayload);
          setEnsembleData(r);
          break;
        }
        case 'monte_carlo': {
          if (mcData) break;
          const r = await runMonteCarlo(requestPayload);
          setMcData(r);
          break;
        }
        case 'bayesian': {
          if (bayesData) break;
          const r = await runBayesian(requestPayload);
          setBayesData(r);
          break;
        }
        case 'causal': {
          if (causalData) break;
          const r = await runCausal(requestPayload);
          setCausalData(r);
          break;
        }
      }
    } catch (err: any) {
      setError(err.message || '分析失败');
    } finally {
      setLoading(false);
    }
  }, [ensembleData, mcData, bayesData, causalData, requestPayload]);

  const handleTabClick = useCallback((tab: TabId) => {
    setActiveTab(tab);
    const hasData =
      (tab === 'ensemble' && ensembleData) ||
      (tab === 'monte_carlo' && mcData) ||
      (tab === 'bayesian' && bayesData) ||
      (tab === 'causal' && causalData);
    if (!hasData) {
      runAnalysis(tab);
    }
  }, [ensembleData, mcData, bayesData, causalData, runAnalysis]);

  // Auto-load ensemble on mount
  const handleRunAll = useCallback(() => {
    runAnalysis(activeTab);
  }, [activeTab, runAnalysis]);

  return (
    <div className="rounded-xl overflow-hidden" style={{
      backgroundColor: COLORS.bg.card,
      border: `1px solid ${COLORS.border}`,
    }}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3" style={{ borderBottom: `1px solid ${COLORS.border}` }}>
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4" style={{ color: COLORS.primary.cyan }} />
          <h3 className="text-sm font-semibold" style={{ color: COLORS.text.primary }}>
            高级量化分析
          </h3>
          <span className="px-1.5 py-0.5 rounded text-[9px]" style={{ backgroundColor: `${COLORS.primary.cyan}15`, color: COLORS.primary.cyan }}>
            P2.2
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b" style={{ borderColor: COLORS.border }}>
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => handleTabClick(tab.id)}
            className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-xs font-medium transition-all duration-200"
            style={{
              color: activeTab === tab.id ? COLORS.primary.cyan : COLORS.text.muted,
              borderBottom: activeTab === tab.id ? `2px solid ${COLORS.primary.cyan}` : '2px solid transparent',
              backgroundColor: activeTab === tab.id ? `${COLORS.primary.cyan}08` : 'transparent',
            }}
          >
            {tab.icon}
            <span className="hidden sm:inline">{tab.name}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="p-4" style={{ minHeight: '300px' }}>
        {loading && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin mb-3" style={{ color: COLORS.primary.cyan }} />
            <p className="text-sm" style={{ color: COLORS.text.secondary }}>正在运行{TABS.find(t => t.id === activeTab)?.name}分析...</p>
          </div>
        )}

        {error && !loading && (
          <div className="flex flex-col items-center justify-center py-8">
            <AlertCircle className="w-8 h-8 mb-3" style={{ color: COLORS.status.danger }} />
            <p className="text-sm mb-3" style={{ color: COLORS.status.danger }}>{error}</p>
            <button
              onClick={handleRunAll}
              className="px-4 py-2 rounded-lg text-xs font-medium"
              style={{ backgroundColor: `${COLORS.primary.cyan}15`, color: COLORS.primary.cyan }}
            >
              重试
            </button>
          </div>
        )}

        {!loading && !error && activeTab === 'ensemble' && ensembleData && (
          <LazyWrapper><EnsembleDashboardLazy result={ensembleData.result} /></LazyWrapper>
        )}
        {!loading && !error && activeTab === 'monte_carlo' && mcData && (
          <LazyWrapper><MonteCarloChartLazy result={mcData.result} /></LazyWrapper>
        )}
        {!loading && !error && activeTab === 'bayesian' && bayesData && (
          <LazyWrapper><BayesianNetworkViewLazy result={bayesData.result} /></LazyWrapper>
        )}
        {!loading && !error && activeTab === 'causal' && causalData && (
          <LazyWrapper><CausalGraphViewLazy result={causalData.result} /></LazyWrapper>
        )}

        {!loading && !error && !ensembleData && !mcData && !bayesData && !causalData && (
          <div className="flex flex-col items-center justify-center py-12">
            <p className="text-sm mb-3" style={{ color: COLORS.text.muted }}>点击上方标签运行分析</p>
            <button
              onClick={handleRunAll}
              className="px-6 py-2.5 rounded-lg text-sm font-medium transition-all duration-200"
              style={{
                background: `linear-gradient(135deg, ${COLORS.primary.cyan}, ${COLORS.primary.blue})`,
                color: COLORS.bg.dark,
              }}
            >
              运行集成分析
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// Lazy-loaded components
const EnsembleDashboardLazy = lazy(() => import('./EnsembleDashboard'));
const MonteCarloChartLazy = lazy(() => import('./MonteCarloChart'));
const BayesianNetworkViewLazy = lazy(() => import('./BayesianNetworkView'));
const CausalGraphViewLazy = lazy(() => import('./CausalGraphView'));

function LazyWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin" style={{ color: COLORS.primary.cyan }} />
      </div>
    }>
      {children}
    </Suspense>
  );
}
