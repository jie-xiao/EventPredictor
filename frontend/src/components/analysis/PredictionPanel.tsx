import { useState } from 'react';
import { AnalysisResult, DebateResult } from '../../services/api';
import TrendGauge from './TrendGauge';
import ProbabilityBar from './ProbabilityBar';
import KeyInsights from './KeyInsights';

// InsightItem interface (internal)
interface InsightItem {
  text: string;
  confidence?: number;
  secondary?: string[];
}

interface PredictionPanelProps {
  result: AnalysisResult | DebateResult;
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const getRiskLevel = (result: AnalysisResult | DebateResult): string => {
  const conflicts = result.cross_analysis?.conflicts?.length || 0;
  const confidence = result.overall_confidence;

  if (conflicts >= 3 || confidence < 0.5) return 'HIGH';
  if (conflicts >= 1 || confidence < 0.7) return 'MEDIUM';
  return 'LOW';
};

const getVolatility = (trend?: string): string => {
  if (!trend) return 'MEDIUM';
  const t = trend.toUpperCase();
  if (t.includes('UNCERTAIN') || t.includes('不确定')) return 'HIGH';
  if (t.includes('SIDEWAYS') || t.includes('横盘')) return 'LOW';
  return 'MEDIUM';
};

const getImpactLevel = (result: AnalysisResult | DebateResult): string => {
  const highImpacts = result.analyses.filter(a =>
    a.impact.economic?.includes('++') ||
    a.impact.political?.includes('++') ||
    a.impact.social?.includes('++')
  ).length;

  if (highImpacts >= 3) return 'Global';
  if (highImpacts >= 2) return 'Regional';
  return 'Local';
};

const getInsightsFromResult = (result: AnalysisResult | DebateResult): InsightItem[] => {
  const insights: InsightItem[] = [];

  // Add prediction key insights
  if (result.prediction?.key_insights) {
    result.prediction.key_insights.forEach(insight => {
      insights.push({
        text: insight,
        confidence: result.overall_confidence
      });
    });
  }

  // Add consensus points if available
  if (result.cross_analysis?.consensus) {
    result.cross_analysis.consensus.slice(0, 2).forEach(consensus => {
      insights.push({
        text: consensus,
        confidence: result.overall_confidence * 0.9
      });
    });
  }

  // Add synergy insights
  if (result.cross_analysis?.synergies) {
    result.cross_analysis.synergies.slice(0, 2).forEach(synergy => {
      insights.push({
        text: synergy.description || synergy.type || 'Synergistic alignment detected',
        confidence: result.overall_confidence * 0.85
      });
    });
  }

  return insights.slice(0, 6);
};

const getProbabilityDistribution = (prediction?: AnalysisResult['prediction']) => {
  if (!prediction) return undefined;

  const trend = prediction.trend.toUpperCase();
  const mainProb = prediction.confidence || 0.7;

  return [
    {
      label: 'UP',
      value: trend === 'UP' || trend === '上涨' ? mainProb : 0.05,
      description: 'Positive trend expected'
    },
    {
      label: 'SIDEWAYS',
      value: trend === 'SIDEWAYS' || trend === '横盘' ? mainProb : 0.15,
      description: 'No significant change'
    },
    {
      label: 'DOWN',
      value: trend === 'DOWN' || trend === '下跌' ? mainProb : 0.1,
      description: 'Negative trend possible'
    },
    {
      label: 'UNCERTAIN',
      value: 0.05,
      description: 'Insufficient data'
    },
    {
      label: 'OTHER',
      value: 0.05,
      description: 'Unforeseen factors'
    }
  ];
};

export default function PredictionPanel({ result }: PredictionPanelProps) {
  const [showProbabilityDetails, setShowProbabilityDetails] = useState(false);

  const prediction = result.prediction;
  const riskLevel = getRiskLevel(result);
  const volatility = getVolatility(prediction?.trend);
  const impact = getImpactLevel(result);
  const insights = getInsightsFromResult(result);
  const probabilities = getProbabilityDistribution(prediction);

  const handleExport = () => {
    console.log('Export prediction panel');
  };

  const handleShare = () => {
    console.log('Share prediction panel');
  };

  return (
    <div
      className="h-full flex flex-col rounded-lg overflow-hidden"
      style={{ backgroundColor: COLORS.bg.card, border: `1px solid ${COLORS.border}` }}
    >
      {/* Header */}
      <div
        className="flex-shrink-0 px-6 py-4 border-b flex items-center justify-between"
        style={{
          background: `linear-gradient(90deg, ${COLORS.primary.cyan}10 0%, ${COLORS.primary.blue}10 100%)`,
          borderColor: COLORS.border
        }}
      >
        <div className="flex items-center gap-2">
          <div
            className="w-8 h-8 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: `${COLORS.primary.cyan}20` }}
          >
            <svg
              className="w-4.5 h-4.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              style={{ color: COLORS.primary.cyan }}
            >
              <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
          </div>
          <h2 className="text-[16px] font-semibold" style={{ color: COLORS.text.primary }}>
            PREDICTION PANEL
          </h2>
        </div>

        {/* Action Icons */}
        <div className="flex items-center gap-1">
          <button
            onClick={handleShare}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200 hover:bg-[#00E5FF]20"
            style={{ color: COLORS.text.secondary }}
            title="Share"
          >
            <svg
              className="w-4 h-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="18" cy="5" r="3" />
              <circle cx="6" cy="12" r="3" />
              <circle cx="18" cy="19" r="3" />
              <path d="M8.59 13.51l6.83 3.98" />
              <path d="M15.41 6.51l-6.82 3.98" />
            </svg>
          </button>
          <button
            onClick={handleExport}
            className="w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200 hover:bg-[#00E5FF]20"
            style={{ color: COLORS.text.secondary }}
            title="Export"
          >
            <svg
              className="w-4 h-4"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7,10 12,15 17,10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Trend Gauge */}
        {prediction && (
          <div
            className="p-5 rounded-xl"
            style={{
              background: `linear-gradient(135deg, ${COLORS.bg.card} 0%, ${COLORS.bg.dark} 100%)`,
              border: `1px solid ${COLORS.border}`
            }}
          >
            <h3
              className="text-[13px] font-semibold mb-4 uppercase tracking-wider"
              style={{ color: COLORS.text.muted }}
            >
              Trend Prediction
            </h3>
            <TrendGauge
              trend={prediction.trend}
              confidence={prediction.confidence || result.overall_confidence}
              riskLevel={riskLevel}
              volatility={volatility}
              impact={impact}
            />
          </div>
        )}

        {/* Probability Distribution */}
        <div
          className="p-5 rounded-xl"
          style={{
            background: `linear-gradient(135deg, ${COLORS.bg.card} 0%, ${COLORS.bg.dark} 100%)`,
            border: `1px solid ${COLORS.border}`
          }}
        >
          <ProbabilityBar
            probabilities={probabilities}
            confidenceInterval={95}
            showDetails={showProbabilityDetails}
            onToggleDetails={() => setShowProbabilityDetails(!showProbabilityDetails)}
          />
        </div>

        {/* Summary Text */}
        {prediction?.summary && (
          <div
            className="p-4 rounded-xl border transition-all duration-200 hover:scale-[1.01]"
            style={{
              backgroundColor: `${COLORS.bg.card}`,
              borderColor: `${COLORS.border}50`
            }}
          >
            <h3
              className="text-[12px] font-semibold mb-2 uppercase tracking-wider"
              style={{ color: COLORS.text.muted }}
            >
              Summary
            </h3>
            <p
              className="text-[14px] leading-relaxed"
              style={{ color: COLORS.text.secondary }}
            >
              {prediction.summary}
            </p>
          </div>
        )}

        {/* Key Insights */}
        <KeyInsights
          insights={insights}
          maxVisible={3}
          onViewAllInsights={() => console.log('View all insights')}
        />

        {/* Recommended Actions */}
        {prediction?.recommended_actions && prediction.recommended_actions.length > 0 && (
          <div
            className="p-5 rounded-xl"
            style={{
              background: `linear-gradient(135deg, ${COLORS.status.warning}08 0%, ${COLORS.bg.card} 100%)`,
              border: `1px solid ${COLORS.status.warning}30`
            }}
          >
            <h3
              className="text-[13px] font-semibold mb-3 uppercase tracking-wider flex items-center gap-2"
              style={{ color: COLORS.status.warning }}
            >
              <svg
                className="w-4 h-4"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2" />
              </svg>
              Recommended Actions
            </h3>
            <div className="space-y-2">
              {prediction.recommended_actions.slice(0, 4).map((action, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3 rounded-lg transition-all duration-200 hover:bg-[#F59E0B]10"
                  style={{ backgroundColor: `${COLORS.bg.card}80` }}
                >
                  <div
                    className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5"
                    style={{ backgroundColor: `${COLORS.status.warning}20` }}
                  >
                    <span className="text-[10px] font-bold" style={{ color: COLORS.status.warning }}>
                      {idx + 1}
                    </span>
                  </div>
                  <p
                    className="text-[13px] leading-relaxed"
                    style={{ color: COLORS.text.secondary }}
                  >
                    {action}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
