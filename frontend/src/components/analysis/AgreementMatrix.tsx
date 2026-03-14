import { useState } from 'react';
import { AnalysisResult, DebateResult, AgreementItem } from '../../services/api';

interface AgreementMatrixProps {
  result: AnalysisResult | DebateResult;
  agreements?: AgreementItem[];
  consensus?: string[];
}

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

const ROLE_DISPLAY_NAMES: Record<string, string> = {
  cn_gov: 'CN Gov', us_gov: 'US Gov', eu_gov: 'EU Gov', ru_gov: 'RU Gov',
  tech_giant: 'Tech', financial_giant: 'Finance', cn_corp: 'CN Corp',
  common_public: 'Public', intellectual: 'Expert', netizen: 'Netizen',
  mainstream_media: 'Media', social_media: 'Social', official_media: 'Official',
  institutional_investor: 'Instit.', retail_investor: 'Retail', venture_capitalist: 'VC',
};

const getRoleDisplayName = (roleId: string): string => {
  return ROLE_DISPLAY_NAMES[roleId] || roleId;
};

const getAgreementColor = (percentage: number): string => {
  if (percentage >= 0.67) return COLORS.status.success;
  if (percentage >= 0.34) return COLORS.status.warning;
  return COLORS.status.danger;
};

const getAgreementLabel = (percentage: number): string => {
  if (percentage >= 0.8) return 'Strong';
  if (percentage >= 0.67) return 'High';
  if (percentage >= 0.5) return 'Moderate';
  if (percentage >= 0.34) return 'Low';
  return 'Very Low';
};

// Build agreement matrix from agreements or consensus
const buildAgreementMatrix = (
  result: AnalysisResult | DebateResult,
  agreements?: AgreementItem[]
): Map<string, Map<string, number>> => {
  const matrix = new Map<string, Map<string, number>>();
  const roleIds = result.analyses.map(a => a.role_id);

  // Initialize matrix with diagonal = 100%
  roleIds.forEach(role1 => {
    matrix.set(role1, new Map());
    roleIds.forEach(role2 => {
      matrix.get(role1)!.set(role2, role1 === role2 ? 1 : 0);
    });
  });

  // Fill in from agreements if available
  if (agreements && agreements.length > 0) {
    agreements.forEach(agreement => {
      const role1Key = agreement.role1;
      const role2Key = agreement.role2;
      if (matrix.has(role1Key) && matrix.get(role1Key)!.has(role2Key)) {
        matrix.get(role1Key)!.set(role2Key, agreement.strength);
        matrix.get(role2Key)!.set(role1Key, agreement.strength);
      }
    });
  } else {
    // Calculate approximate agreement based on stance similarity
    result.analyses.forEach((a1, idx1) => {
      result.analyses.forEach((a2, idx2) => {
        if (idx1 >= idx2) return;
        const stance1 = a1.stance.toLowerCase();
        const stance2 = a2.stance.toLowerCase();

        let similarity = 0.5; // Base similarity

        // Check stance keywords
        const positiveKeywords = ['optimistic', 'positive', 'bullish', 'support', '乐观', '正面', '支持'];
        const negativeKeywords = ['pessimistic', 'negative', 'bearish', 'oppose', '悲观', '负面', '反对'];
        const neutralKeywords = ['neutral', 'cautious', 'conservative', '中性', '谨慎', '保守'];

        const bothPositive = positiveKeywords.some(k => stance1.includes(k)) && positiveKeywords.some(k => stance2.includes(k));
        const bothNegative = negativeKeywords.some(k => stance1.includes(k)) && negativeKeywords.some(k => stance2.includes(k));
        const bothNeutral = neutralKeywords.some(k => stance1.includes(k)) && neutralKeywords.some(k => stance2.includes(k));

        if (bothPositive || bothNegative || bothNeutral) {
          similarity = 0.85;
        } else if ((positiveKeywords.some(k => stance1.includes(k)) && negativeKeywords.some(k => stance2.includes(k))) ||
                   (negativeKeywords.some(k => stance1.includes(k)) && positiveKeywords.some(k => stance2.includes(k)))) {
          similarity = 0.25;
        }

        // Adjust by confidence
        const avgConfidence = (a1.confidence + a2.confidence) / 2;
        similarity *= avgConfidence;

        matrix.get(a1.role_id)!.set(a2.role_id, similarity);
        matrix.get(a2.role_id)!.set(a1.role_id, similarity);
      });
    });
  }

  return matrix;
};

// Cell Component
const MatrixCell = ({
  percentage,
  onClick
}: {
  percentage: number;
  onClick?: () => void;
}) => {
  const color = getAgreementColor(percentage);
  const displayPercentage = Math.round(percentage * 100);
  const label = getAgreementLabel(percentage);

  return (
    <div
      onClick={onClick}
      className="relative w-14 h-14 flex items-center justify-center rounded transition-all duration-200 cursor-pointer hover:scale-110"
      style={{
        backgroundColor: color + '20',
        border: `1px solid ${color}40`,
        opacity: percentage === 0 ? 0.3 : 1
      }}
    >
      <div className="text-center">
        <div
          className="text-sm font-bold font-mono"
          style={{ color: color }}
        >
          {displayPercentage}%
        </div>
        <div
          className="text-[8px] leading-none"
          style={{ color: `${color}cc` }}
        >
          {label}
        </div>
      </div>
    </div>
  );
};

export default function AgreementMatrix({
  result,
  agreements
}: AgreementMatrixProps) {
  const [selectedCell, setSelectedCell] = useState<{ role1: string; role2: string } | null>(null);
  const [sortBy, setSortBy] = useState<'similarity' | 'alphabetical'>('similarity');

  const roleIds = result.analyses.map(a => a.role_id);
  const matrix = buildAgreementMatrix(result, agreements);

  // Calculate average agreement per role for sorting
  const getRoleAverageAgreement = (roleId: string): number => {
    let sum = 0;
    let count = 0;
    roleIds.forEach(otherId => {
      if (otherId !== roleId) {
        sum += matrix.get(roleId)?.get(otherId) || 0;
        count++;
      }
    });
    return count > 0 ? sum / count : 0;
  };

  // Sort roles if needed
  const sortedRoleIds = [...roleIds].sort((a, b) => {
    if (sortBy === 'similarity') {
      return getRoleAverageAgreement(b) - getRoleAverageAgreement(a);
    }
    return a.localeCompare(b);
  });

  const handleCellClick = (role1: string, role2: string) => {
    if (role1 !== role2) {
      setSelectedCell(selectedCell?.role1 === role1 && selectedCell?.role2 === role2 ? null : { role1, role2 });
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h4
          className="text-[11px] font-semibold uppercase tracking-wider"
          style={{ color: COLORS.text.muted }}
        >
          AGREEMENT MATRIX
        </h4>

        <div className="flex items-center gap-2">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'similarity' | 'alphabetical')}
            className="px-3 py-1.5 rounded-lg text-xs transition-all cursor-pointer"
            style={{
              backgroundColor: `${COLORS.bg.dark}`,
              border: `1px solid ${COLORS.border}`,
              color: COLORS.text.secondary
            }}
          >
            <option value="similarity">Sort by Similarity</option>
            <option value="alphabetical">Sort Alphabetically</option>
          </select>
        </div>
      </div>

      {/* Matrix */}
      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          {/* Header Row */}
          <div className="flex">
            <div className="w-14" /> {/* Corner cell */}
            {sortedRoleIds.map(roleId => (
              <div
                key={roleId}
                className="w-14 h-8 flex items-center justify-center text-[10px] font-medium"
                style={{ color: COLORS.text.muted }}
              >
                {getRoleDisplayName(roleId)}
              </div>
            ))}
          </div>

          {/* Matrix Rows */}
          {sortedRoleIds.map((rowRole, rowIdx) => (
            <div key={rowRole} className="flex">
              {/* Row Label */}
              <div
                className="w-14 h-14 flex items-center justify-center text-[10px] font-medium"
                style={{ color: COLORS.text.muted }}
              >
                {getRoleDisplayName(rowRole)}
              </div>

              {/* Matrix Cells */}
              {sortedRoleIds.map((colRole, colIdx) => {
                const percentage = matrix.get(rowRole)?.get(colRole) || 0;
                const isSelected = selectedCell?.role1 === rowRole && selectedCell?.role2 === colRole;
                const isDiagonal = rowIdx === colIdx;

                return (
                  <div key={`${rowRole}-${colRole}`} className="relative">
                    {isDiagonal ? (
                      <div
                        className="w-14 h-14 flex items-center justify-center rounded"
                        style={{
                          backgroundColor: `${COLORS.primary.cyan}30`,
                          border: `1px solid ${COLORS.primary.cyan}50`
                        }}
                      >
                        <span className="text-2xl opacity-50">✓</span>
                      </div>
                    ) : (
                      <div
                        className={isSelected ? 'scale-110' : ''}
                        style={{
                          position: 'absolute',
                          top: isSelected ? -2 : 0,
                          left: isSelected ? -2 : 0,
                          zIndex: isSelected ? 10 : 1
                        }}
                      >
                        <MatrixCell
                          percentage={percentage}
                          onClick={() => handleCellClick(rowRole, colRole)}
                        />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Selected Cell Details */}
      {selectedCell && (
        <div
          className="p-4 rounded-xl animate-in fade-in duration-200"
          style={{
            background: `linear-gradient(135deg, ${COLORS.primary.cyan}08 0%, ${COLORS.bg.card} 100%)`,
            border: `1px solid ${COLORS.primary.cyan}30`
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider" style={{ color: COLORS.text.muted }}>
              Comparison Details
            </span>
            <button
              onClick={() => setSelectedCell(null)}
              className="text-xs transition-all hover:scale-110"
              style={{ color: COLORS.text.muted }}
            >
              Close
            </button>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-center">
              <p className="text-lg font-bold" style={{ color: COLORS.text.primary }}>
                {getRoleDisplayName(selectedCell.role1)}
              </p>
              <span className="text-xs" style={{ color: COLORS.text.muted }}>
                vs
              </span>
              <p className="text-lg font-bold" style={{ color: COLORS.text.primary }}>
                {getRoleDisplayName(selectedCell.role2)}
              </p>
            </div>
            <div className="h-8 w-px" style={{ backgroundColor: COLORS.border }} />
            <div className="text-center">
              <p className="text-xs uppercase tracking-wider mb-1" style={{ color: COLORS.text.muted }}>
                Agreement
              </p>
              <p
                className="text-2xl font-bold font-mono"
                style={{ color: getAgreementColor(matrix.get(selectedCell.role1)?.get(selectedCell.role2) || 0) }}
              >
                {Math.round((matrix.get(selectedCell.role1)?.get(selectedCell.role2) || 0) * 100)}%
              </p>
              <p className="text-xs mt-1" style={{ color: COLORS.text.secondary }}>
                {getAgreementLabel(matrix.get(selectedCell.role1)?.get(selectedCell.role2) || 0)} Consensus
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Color Legend */}
      <div className="flex items-center justify-center gap-4 text-xs pt-2">
        <span style={{ color: COLORS.text.muted }}>Color Scale:</span>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: COLORS.status.danger }}
            />
            <span>0-33% (Low)</span>
          </div>
          <div className="flex items-center gap-1">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: COLORS.status.warning }}
            />
            <span>34-66% (Medium)</span>
          </div>
          <div className="flex items-center gap-1">
            <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: COLORS.status.success }}
            />
            <span>67-100% (High)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
