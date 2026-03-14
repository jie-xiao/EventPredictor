import { useState } from 'react';
import { ChevronDown, ChevronUp, Edit, Users, ChevronRight } from 'lucide-react';
import { RoleAnalysis, AnalysisResult, DebateResult } from '../../services/api';

interface RoleMatrixProps {
  result: AnalysisResult | DebateResult;
  onEditRoles?: () => void;
  onExpandDetail?: (roleId: string) => void;
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const ROLE_CATEGORY_MAP: Record<string, string> = {
  cn_gov: 'government', us_gov: 'government', eu_gov: 'government', ru_gov: 'government',
  tech_giant: 'corporation', financial_giant: 'corporation', cn_corp: 'corporation',
  common_public: 'public', intellectual: 'public', netizen: 'public',
  mainstream_media: 'media', social_media: 'media', official_media: 'media',
  institutional_investor: 'investor', retail_investor: 'investor', venture_capitalist: 'investor',
};

const ROLE_ICONS: Record<string, string> = {
  government: '🏛️', corporation: '🏢', public: '👥', media: '📰', investor: '💰', default: '🎭',
};

const ROLE_DISPLAY_NAMES: Record<string, string> = {
  cn_gov: 'CN Gov', us_gov: 'US Gov', eu_gov: 'EU Gov', ru_gov: 'RU Gov',
  tech_giant: 'Tech', financial_giant: 'Finance', cn_corp: 'CN Corp',
  common_public: 'Public', intellectual: 'Expert', netizen: 'Netizen',
  mainstream_media: 'Media', social_media: 'Social', official_media: 'Official',
  institutional_investor: 'Instit.', retail_investor: 'Retail', venture_capitalist: 'VC',
};

const getRoleIcon = (roleId: string) => {
  const category = ROLE_CATEGORY_MAP[roleId] || 'default';
  return ROLE_ICONS[category] || ROLE_ICONS.default;
};

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.8) return COLORS.status.success;
  if (confidence >= 0.6) return COLORS.status.warning;
  return COLORS.status.danger;
};

const parseImpact = (impact: string): { value: number; label: string; color: string } => {
  const str = impact.toLowerCase();
  if (str.includes('+++') || str.includes('very positive') || str.includes('非常正面')) {
    return { value: 3, label: '++', color: COLORS.status.success };
  }
  if (str.includes('++') || str.includes('strong positive') || str.includes('强正面')) {
    return { value: 2, label: '++', color: COLORS.status.success };
  }
  if (str.includes('+') || str.includes('positive') || str.includes('正面')) {
    return { value: 1, label: '+', color: COLORS.status.success };
  }
  if (str.includes('---') || str.includes('very negative') || str.includes('非常负面')) {
    return { value: -3, label: '--', color: COLORS.status.danger };
  }
  if (str.includes('--') || str.includes('strong negative') || str.includes('强负面')) {
    return { value: -2, label: '--', color: COLORS.status.danger };
  }
  if (str.includes('-') || str.includes('negative') || str.includes('负面')) {
    return { value: -1, label: '-', color: COLORS.status.danger };
  }
  return { value: 0, label: '0', color: COLORS.text.muted };
};

const getStanceLabel = (stance: string): string => {
  const s = stance.toLowerCase();
  if (s.includes('optimistic') || s.includes('positive') || s.includes('乐观') || s.includes('正面')) {
    return 'Optimistic';
  }
  if (s.includes('cautious') || s.includes('conservative') || s.includes('谨慎') || s.includes('保守')) {
    return 'Cautious';
  }
  if (s.includes('concerned') || s.includes('worried') || s.includes('担忧') || s.includes('担心')) {
    return 'Concerned';
  }
  if (s.includes('bearish') || s.includes('negative') || s.includes('悲观') || s.includes('负面')) {
    return 'Bearish';
  }
  if (s.includes('neutral') || s.includes('middle') || s.includes('中性') || s.includes('中间')) {
    return 'Neutral';
  }
  return stance;
};

// Compact Role Card Component
const CompactRoleCard = ({
  analysis,
  onExpand,
  isSelected
}: {
  analysis: RoleAnalysis;
  onExpand?: () => void;
  isSelected?: boolean;
}) => {
  const roleIcon = getRoleIcon(analysis.role_id);
  const confidenceColor = getConfidenceColor(analysis.confidence);
  const economicImpact = parseImpact(analysis.impact.economic);
  const politicalImpact = parseImpact(analysis.impact.political);
  const socialImpact = parseImpact(analysis.impact.social);
  const stanceLabel = getStanceLabel(analysis.stance);
  const displayName = ROLE_DISPLAY_NAMES[analysis.role_id] || analysis.role_name;

  return (
    <div
      className={`p-4 rounded-xl border transition-all duration-200 cursor-pointer ${
        isSelected ? 'scale-105' : 'hover:scale-[1.02]'
      }`}
      style={{
        backgroundColor: isSelected ? `${COLORS.bg.card}` : `${COLORS.bg.dark}`,
        borderColor: isSelected ? `${COLORS.primary.cyan}` : COLORS.border,
        boxShadow: isSelected ? `0 0 20px ${COLORS.primary.cyan}30` : 'none'
      }}
      onClick={onExpand}
    >
      {/* Role Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{roleIcon}</span>
          <div>
            <h4
              className="text-[13px] font-semibold"
              style={{ color: COLORS.text.primary }}
            >
              {displayName}
            </h4>
            <p className="text-[10px]" style={{ color: COLORS.text.muted }}>
              {analysis.role_id}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div
            className="text-[10px] font-medium mb-0.5"
            style={{ color: COLORS.text.muted }}
          >
            Conf.
          </div>
          <div
            className="text-lg font-bold font-mono"
            style={{ color: confidenceColor }}
          >
            {Math.round(analysis.confidence * 100)}%
          </div>
        </div>
      </div>

      {/* Stance */}
      <div className="mb-3">
        <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
          Stance
        </p>
        <p className="text-[13px] font-medium" style={{ color: COLORS.text.primary }}>
          {stanceLabel}
        </p>
      </div>

      {/* Impact Indicators */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
            Economic
          </span>
          <span
            className="text-[13px] font-bold"
            style={{ color: economicImpact.color }}
          >
            {economicImpact.label}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
            Political
          </span>
          <span
            className="text-[13px] font-bold"
            style={{ color: politicalImpact.color }}
          >
            {politicalImpact.label}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[10px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
            Social
          </span>
          <span
            className="text-[13px] font-bold"
            style={{ color: socialImpact.color }}
          >
            {socialImpact.label}
          </span>
        </div>
      </div>

      {/* View Button */}
      <button
        className="w-full mt-3 py-2 rounded-lg flex items-center justify-center gap-1.5 text-xs font-medium transition-all hover:scale-105"
        style={{
          backgroundColor: `${COLORS.border}50`,
          color: COLORS.text.secondary
        }}
      >
        View Details
        <ChevronRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

export default function RoleMatrix({ result, onEditRoles, onExpandDetail }: RoleMatrixProps) {
  const [expanded, setExpanded] = useState(false);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);

  const analyses = result.analyses;

  // Calculate aggregated impact for each dimension
  const getAggregatedImpact = (dimension: 'economic' | 'political' | 'social') => {
    let total = 0;
    analyses.forEach(a => {
      total += parseImpact(a.impact[dimension]).value;
    });
    const avg = total / analyses.length;
    if (avg >= 1) return { label: 'Positive', color: COLORS.status.success };
    if (avg <= -1) return { label: 'Negative', color: COLORS.status.danger };
    return { label: 'Neutral', color: COLORS.text.muted };
  };

  const economicAggregate = getAggregatedImpact('economic');
  const politicalAggregate = getAggregatedImpact('political');
  const socialAggregate = getAggregatedImpact('social');

  const handleExpandRole = (roleId: string) => {
    setSelectedRole(roleId);
    if (onExpandDetail) {
      onExpandDetail(roleId);
    }
  };

  return (
    <div
      className="rounded-lg overflow-hidden"
      style={{ backgroundColor: COLORS.bg.card, border: `1px solid ${COLORS.border}` }}
    >
      {/* Header */}
      <div
        className="px-6 py-4 border-b flex items-center justify-between"
        style={{ borderColor: COLORS.border }}
      >
        <div className="flex items-center gap-3">
          <Users className="w-5 h-5" style={{ color: COLORS.primary.cyan }} />
          <h3 className="text-[14px] font-semibold" style={{ color: COLORS.text.primary }}>
            ROLE ANALYSIS MATRIX
          </h3>
          <span
            className="px-2 py-0.5 rounded text-[10px] font-medium"
            style={{
              backgroundColor: `${COLORS.primary.cyan}15`,
              color: COLORS.primary.cyan
            }}
          >
            {analyses.length} Roles
          </span>
        </div>

        <div className="flex items-center gap-2">
          {onEditRoles && (
            <button
              onClick={onEditRoles}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all hover:scale-105"
              style={{
                backgroundColor: `${COLORS.border}50`,
                color: COLORS.text.secondary
              }}
            >
              <Edit className="w-3.5 h-3.5" />
              <span>Edit Roles</span>
            </button>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs transition-all hover:scale-105"
            style={{
              backgroundColor: `${COLORS.border}50`,
              color: COLORS.text.secondary
            }}
          >
            <span>{expanded ? 'Collapse' : 'Expand'} Details</span>
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Compact View */}
      <div className="p-5">
        {/* Role Cards Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3 mb-5">
          {analyses.map((analysis) => (
            <CompactRoleCard
              key={analysis.role_id}
              analysis={analysis}
              onExpand={() => handleExpandRole(analysis.role_id)}
              isSelected={selectedRole === analysis.role_id}
            />
          ))}
        </div>

        {/* Impact Legend */}
        <div
          className="p-4 rounded-xl flex items-center justify-between text-xs"
          style={{ backgroundColor: `${COLORS.bg.dark}` }}
        >
          <span style={{ color: COLORS.text.muted }}>
            Impact Legend:
          </span>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <span className="font-bold" style={{ color: COLORS.status.danger }}>--</span>
              <span style={{ color: COLORS.text.muted }}>Negative</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="font-bold" style={{ color: COLORS.text.muted }}>0</span>
              <span style={{ color: COLORS.text.muted }}>Neutral</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="font-bold" style={{ color: COLORS.status.success }}>+</span>
              <span style={{ color: COLORS.text.muted }}>Positive</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="font-bold" style={{ color: COLORS.status.success }}>++</span>
              <span style={{ color: COLORS.text.muted }}>Strong Positive</span>
            </div>
          </div>
        </div>

        {/* Aggregate Summary (only when expanded) */}
        {expanded && (
          <div
            className="mt-4 p-4 rounded-xl animate-in slide-in-from-top-2 duration-300"
            style={{
              background: `linear-gradient(135deg, ${COLORS.primary.cyan}08 0%, ${COLORS.bg.card} 100%)`,
              border: `1px solid ${COLORS.primary.cyan}20`
            }}
          >
            <h4
              className="text-[11px] font-semibold mb-3 uppercase tracking-wider"
              style={{ color: COLORS.text.muted }}
            >
              Aggregate Impact
            </h4>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 rounded-lg" style={{ backgroundColor: `${COLORS.bg.dark}` }}>
                <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
                  Economic
                </p>
                <p className="text-[14px] font-bold" style={{ color: economicAggregate.color }}>
                  {economicAggregate.label}
                </p>
              </div>
              <div className="text-center p-3 rounded-lg" style={{ backgroundColor: `${COLORS.bg.dark}` }}>
                <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
                  Political
                </p>
                <p className="text-[14px] font-bold" style={{ color: politicalAggregate.color }}>
                  {politicalAggregate.label}
                </p>
              </div>
              <div className="text-center p-3 rounded-lg" style={{ backgroundColor: `${COLORS.bg.dark}` }}>
                <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
                  Social
                </p>
                <p className="text-[14px] font-bold" style={{ color: socialAggregate.color }}>
                  {socialAggregate.label}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
