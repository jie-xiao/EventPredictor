import { useState } from 'react';
import { Network, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp, Download } from 'lucide-react';
import { AnalysisResult, DebateResult, CrossAnalysisItem } from '../../services/api';
import AgreementMatrix from './AgreementMatrix';

interface CrossAnalysisProps {
  result: AnalysisResult | DebateResult;
  onExport?: () => void;
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const getSeverityColor = (severity?: string): string => {
  if (!severity) return COLORS.text.muted;
  const s = severity.toLowerCase();
  if (s.includes('high') || s.includes('高') || s.includes('severe')) return COLORS.status.danger;
  if (s.includes('medium') || s.includes('中') || s.includes('moderate')) return COLORS.status.warning;
  return COLORS.status.success;
};

// Conflict Item Component
const ConflictItem = ({ conflict }: { conflict: CrossAnalysisItem }) => {
  const severityColor = getSeverityColor(conflict.severity);

  return (
    <div
      className="p-4 rounded-xl border transition-all duration-200 hover:scale-[1.01]"
      style={{
        backgroundColor: `${COLORS.bg.dark}`,
        borderColor: `${COLORS.status.danger}30`
      }}
    >
      <div className="flex items-start gap-3">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
          style={{ backgroundColor: `${COLORS.status.danger}20` }}
        >
          <AlertTriangle className="w-4 h-4" style={{ color: COLORS.status.danger }} />
        </div>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-center gap-2 mb-2">
            {conflict.type && (
              <span
                className="text-[12px] font-semibold"
                style={{ color: COLORS.text.primary }}
              >
                {conflict.type}
              </span>
            )}
            {conflict.severity && (
              <span
                className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                style={{
                  backgroundColor: `${severityColor}20`,
                  color: severityColor
                }}
              >
                {conflict.severity}
              </span>
            )}
          </div>

          {/* Description */}
          {conflict.description && (
            <p className="text-[13px] leading-relaxed mb-2" style={{ color: COLORS.text.secondary }}>
              {conflict.description}
            </p>
          )}

          {/* Roles Involved */}
          {conflict.roles && conflict.roles.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {conflict.roles.map((role, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 rounded text-[10px]"
                  style={{
                    backgroundColor: `${COLORS.border}50`,
                    color: COLORS.text.muted
                  }}
                >
                  {role}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Synergy Item Component
const SynergyItem = ({ synergy }: { synergy: CrossAnalysisItem }) => {
  return (
    <div
      className="p-4 rounded-xl border transition-all duration-200 hover:scale-[1.01]"
      style={{
        backgroundColor: `${COLORS.bg.dark}`,
        borderColor: `${COLORS.status.success}30`
      }}
    >
      <div className="flex items-start gap-3">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
          style={{ backgroundColor: `${COLORS.status.success}20` }}
        >
          <CheckCircle2 className="w-4 h-4" style={{ color: COLORS.status.success }} />
        </div>

        <div className="flex-1 min-w-0">
          {/* Header */}
          {synergy.type && (
            <span
              className="text-[12px] font-semibold mb-2 block"
              style={{ color: COLORS.text.primary }}
            >
              {synergy.type}
            </span>
          )}

          {/* Description */}
          {synergy.description && (
            <p className="text-[13px] leading-relaxed" style={{ color: COLORS.text.secondary }}>
              {synergy.description}
            </p>
          )}

          {/* Potential */}
          {synergy.potential && (
            <div className="mt-2">
              <span className="text-[10px] uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
                Potential:
              </span>
              <span className="text-[11px] ml-1" style={{ color: COLORS.status.success }}>
                {synergy.potential}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Consensus Item Component
const ConsensusItem = ({ consensus }: { consensus: string }) => {
  return (
    <div
      className="flex items-start gap-3 p-3 rounded-lg transition-all duration-200 hover:scale-105"
      style={{ backgroundColor: `${COLORS.bg.dark}` }}
    >
      <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: COLORS.status.success }} />
      <p className="text-[13px] leading-relaxed" style={{ color: COLORS.text.secondary }}>
        {consensus}
      </p>
    </div>
  );
};

export default function CrossAnalysis({ result, onExport }: CrossAnalysisProps) {
  const [activeTab, setActiveTab] = useState<'network' | 'matrix' | 'list'>('matrix');
  const [expanded, setExpanded] = useState(false);

  const conflicts = result.cross_analysis?.conflicts || [];
  const synergies = result.cross_analysis?.synergies || [];
  const consensus = result.cross_analysis?.consensus || [];
  const agreements = result.cross_analysis?.agreements || [];

  const tabs = [
    { id: 'matrix' as const, label: 'Matrix', icon: Network },
    { id: 'list' as const, label: 'Conflicts', icon: AlertTriangle },
    { id: 'network' as const, label: 'Synergies', icon: CheckCircle2 },
  ];

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
        <div className="flex items-center gap-4">
          <h3 className="text-[14px] font-semibold" style={{ color: COLORS.text.primary }}>
            CROSS-ANALYSIS
          </h3>

          {/* Tabs */}
          <div className="flex items-center gap-1">
            {tabs.map((tab) => {
              const isActive = activeTab === tab.id;
              const count = tab.id === 'list' ? conflicts.length :
                           tab.id === 'network' ? synergies.length :
                           result.analyses.length;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isActive ? 'scale-105' : ''
                  }`}
                  style={{
                    backgroundColor: isActive ? `${COLORS.primary.cyan}` : `${COLORS.border}50`,
                    color: isActive ? COLORS.bg.dark : COLORS.text.secondary,
                    boxShadow: isActive ? `0 0 15px ${COLORS.primary.cyan}40` : 'none'
                  }}
                >
                  <tab.icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                  {count > 0 && (
                    <span
                      className="px-1.5 py-0.5 rounded text-[10px]"
                      style={{
                        backgroundColor: isActive ? 'rgba(0,0,0,0.2)' : `${COLORS.border}50`,
                        color: isActive ? 'rgba(255,255,255,0.8)' : COLORS.text.muted
                      }}
                    >
                      {count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {onExport && (
            <button
              onClick={onExport}
              className="p-2 rounded-lg transition-all hover:scale-105"
              style={{ backgroundColor: `${COLORS.border}50`, color: COLORS.text.secondary }}
              title="Export data"
            >
              <Download className="w-4 h-4" />
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
            <span>{expanded ? 'Collapse' : 'Expand'}</span>
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        {/* Matrix View */}
        {activeTab === 'matrix' && (
          <div className="space-y-5">
            <AgreementMatrix
              result={result}
              agreements={agreements}
              consensus={consensus}
            />

            {/* Consensus List */}
            {expanded && consensus.length > 0 && (
              <div
                className="p-4 rounded-xl space-y-2 animate-in slide-in-from-top-2 duration-300"
                style={{
                  background: `linear-gradient(135deg, ${COLORS.status.success}08 0%, ${COLORS.bg.card} 100%)`,
                  border: `1px solid ${COLORS.status.success}20`
                }}
              >
                <h4
                  className="text-[11px] font-semibold mb-3 uppercase tracking-wider flex items-center gap-2"
                  style={{ color: COLORS.status.success }}
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Consensus Points
                </h4>
                <div className="space-y-2">
                  {consensus.map((c, idx) => (
                    <ConsensusItem key={idx} consensus={c} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Conflicts List View */}
        {activeTab === 'list' && (
          <div className="grid gap-3">
            {conflicts.length > 0 ? (
              conflicts.map((conflict, idx) => (
                <ConflictItem key={idx} conflict={conflict} />
              ))
            ) : (
              <div
                className="p-8 rounded-xl text-center"
                style={{ backgroundColor: `${COLORS.bg.dark}` }}
              >
                <AlertTriangle className="w-10 h-10 mx-auto mb-3" style={{ color: COLORS.text.muted }} />
                <p className="text-sm" style={{ color: COLORS.text.secondary }}>
                  No conflicts detected
                </p>
              </div>
            )}
          </div>
        )}

        {/* Synergies View */}
        {activeTab === 'network' && (
          <div className="grid gap-3">
            {synergies.length > 0 ? (
              synergies.map((synergy, idx) => (
                <SynergyItem key={idx} synergy={synergy} />
              ))
            ) : (
              <div
                className="p-8 rounded-xl text-center"
                style={{ backgroundColor: `${COLORS.bg.dark}` }}
              >
                <CheckCircle2 className="w-10 h-10 mx-auto mb-3" style={{ color: COLORS.text.muted }} />
                <p className="text-sm" style={{ color: COLORS.text.secondary }}>
                  No synergies detected
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Stats */}
      <div
        className="px-6 py-3 border-t flex items-center justify-center gap-6 text-xs"
        style={{ borderColor: COLORS.border, backgroundColor: `${COLORS.bg.dark}` }}
      >
        <div className="flex items-center gap-1.5">
          <span style={{ color: COLORS.text.muted }}>Conflicts:</span>
          <span className="font-bold font-mono" style={{ color: COLORS.status.danger }}>
            {conflicts.length}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span style={{ color: COLORS.text.muted }}>Synergies:</span>
          <span className="font-bold font-mono" style={{ color: COLORS.status.success }}>
            {synergies.length}
          </span>
        </div>
        <div className="flex items-center gap-1.5">
          <span style={{ color: COLORS.text.muted }}>Consensus:</span>
          <span className="font-bold font-mono" style={{ color: COLORS.status.success }}>
            {consensus.length}
          </span>
        </div>
      </div>
    </div>
  );
}
