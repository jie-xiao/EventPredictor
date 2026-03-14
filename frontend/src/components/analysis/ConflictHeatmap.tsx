/**
 * ConflictHeatmap.tsx
 *
 * 冲突热力图组件 - 可视化角色间的冲突强度矩阵
 * 基于交叉分析数据生成热力图
 */
import { useMemo, useState } from 'react';
import { AnalysisResult } from '../../services/api';

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

// 冲突严重程度颜色
const getConflictColor = (intensity: number): string => {
  if (intensity >= 0.8) return '#EF4444'; // 高冲突 - 红色
  if (intensity >= 0.6) return '#F97316'; // 中高冲突 - 橙色
  if (intensity >= 0.4) return '#F59E0B'; // 中等冲突 - 黄色
  if (intensity >= 0.2) return '#84CC16'; // 低冲突 - 黄绿色
  return '#10B981'; // 无冲突 - 绿色
};

// 冲突严重程度背景
const getConflictBg = (intensity: number): string => {
  const baseColor = getConflictColor(intensity);
  return `${baseColor}${Math.round(intensity * 40 + 20).toString(16).padStart(2, '0')}`;
};

interface ConflictHeatmapProps {
  result: AnalysisResult;
  onCellClick?: (role1: string, role2: string, intensity: number) => void;
}

interface ConflictCell {
  role1: string;
  role1Name: string;
  role2: string;
  role2Name: string;
  intensity: number;
  description?: string;
}

export default function ConflictHeatmap({ result, onCellClick }: ConflictHeatmapProps) {
  const [hoveredCell, setHoveredCell] = useState<ConflictCell | null>(null);
  const [selectedCell, setSelectedCell] = useState<ConflictCell | null>(null);

  // 获取角色列表
  const roles = useMemo(() => {
    return result.analyses || [];
  }, [result.analyses]);

  // 从交叉分析中提取冲突数据
  const conflictData = useMemo(() => {
    const matrix: Record<string, Record<string, ConflictCell>> = {};

    // 初始化矩阵
    roles.forEach(r1 => {
      matrix[r1.role_id] = {};
      roles.forEach(r2 => {
        matrix[r1.role_id][r2.role_id] = {
          role1: r1.role_id,
          role1Name: r1.role_name,
          role2: r2.role_id,
          role2Name: r2.role_name,
          intensity: r1.role_id === r2.role_id ? 0 : 0.1 // 对角线为0，默认低冲突
        };
      });
    });

    // 从交叉分析中填充冲突数据
    const conflicts = result.cross_analysis?.conflicts || [];

    conflicts.forEach(conflict => {
      // 尝试从冲突类型中提取角色信息
      const typeStr = conflict.type || '';
      const roleIds = typeStr.split('-').filter(s => s);

      if (roleIds.length >= 2) {
        const r1 = roleIds[0];
        const r2 = roleIds[1];

        // 计算冲突强度
        let intensity = 0.5;
        const severity = (conflict.severity || '').toLowerCase();
        if (severity.includes('高') || severity === 'high') intensity = 0.9;
        else if (severity.includes('中') || severity === 'medium') intensity = 0.6;
        else if (severity.includes('低') || severity === 'low') intensity = 0.3;

        // 更新矩阵（对称）
        if (matrix[r1]?.[r2]) {
          matrix[r1][r2] = {
            ...matrix[r1][r2],
            intensity,
            description: conflict.description
          };
        }
        if (matrix[r2]?.[r1]) {
          matrix[r2][r1] = {
            ...matrix[r2][r1],
            intensity,
            description: conflict.description
          };
        }
      }
    });

    // 如果没有明确的冲突数据，基于角色类别计算潜在冲突
    if (conflicts.length === 0 && roles.length > 1) {
      const categoryConflicts: Record<string, Record<string, number>> = {
        'government': { 'public': 0.5, 'corporation': 0.3, 'investor': 0.2 },
        'public': { 'government': 0.5, 'corporation': 0.4 },
        'corporation': { 'government': 0.3, 'public': 0.4 },
        'investor': { 'government': 0.4, 'public': 0.2 },
        'media': { 'government': 0.3 }
      };

      roles.forEach(r1 => {
        roles.forEach(r2 => {
          if (r1.role_id !== r2.role_id) {
            const cat1 = r1.category || '';
            const cat2 = r2.category || '';
            const potential = categoryConflicts[cat1]?.[cat2] || 0.1;

            if (matrix[r1.role_id]?.[r2.role_id]) {
              matrix[r1.role_id][r2.role_id].intensity = Math.max(
                matrix[r1.role_id][r2.role_id].intensity,
                potential
              );
            }
          }
        });
      });
    }

    return matrix;
  }, [roles, result.cross_analysis]);

  // 计算统计信息
  const stats = useMemo((): { total: number; high: number; medium: number; low: number; maxCell: ConflictCell | null; maxIntensity: number } => {
    let total = 0;
    let high = 0;
    let medium = 0;
    let low = 0;
    let maxIntensity = 0;
    let maxCell: ConflictCell | null = null;

    roles.forEach(r1 => {
      roles.forEach(r2 => {
        if (r1.role_id < r2.role_id) { // 只统计上三角
          const cell = conflictData[r1.role_id]?.[r2.role_id];
          if (cell) {
            total++;
            if (cell.intensity >= 0.7) high++;
            else if (cell.intensity >= 0.4) medium++;
            else low++;

            if (cell.intensity > maxIntensity) {
              maxIntensity = cell.intensity;
              maxCell = cell;
            }
          }
        }
      });
    });

    return { total, high, medium, low, maxCell, maxIntensity };
  }, [roles, conflictData]);

  // 处理单元格点击
  const handleCellClick = (cell: ConflictCell) => {
    setSelectedCell(cell);
    onCellClick?.(cell.role1, cell.role2, cell.intensity);
  };

  // 角色名称缩写
  const getRoleAbbr = (name: string): string => {
    const words = name.split(' ');
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const cellSize = 36;
  const labelWidth = 80;
  const padding = 20;

  return (
    <div
      className="rounded-xl p-5"
      style={{
        backgroundColor: COLORS.bg.card,
        border: `1px solid ${COLORS.border}`
      }}
    >
      {/* 标题 */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <h3 className="text-base font-semibold" style={{ color: COLORS.text.primary }}>
            冲突热力图
          </h3>
          <p className="text-xs mt-1" style={{ color: COLORS.text.muted }}>
            角色间观点冲突强度分布
          </p>
        </div>

        {/* 图例 */}
        <div className="flex items-center gap-1.5">
          <span className="text-xs mr-2" style={{ color: COLORS.text.muted }}>强度:</span>
          {['#10B981', '#84CC16', '#F59E0B', '#F97316', '#EF4444'].map((color, idx) => (
            <div
              key={idx}
              className="w-4 h-4 rounded"
              style={{ backgroundColor: color }}
              title={['无', '低', '中', '中高', '高'][idx]}
            />
          ))}
        </div>
      </div>

      {/* 热力图矩阵 */}
      <div className="flex justify-center mb-5 overflow-auto">
        <div style={{ minWidth: `${labelWidth + roles.length * cellSize + padding * 2}px` }}>
          <svg
            width={labelWidth + roles.length * cellSize + padding * 2}
            height={labelWidth + roles.length * cellSize + padding * 2}
          >
            {/* 左侧角色标签 */}
            {roles.map((role, idx) => (
              <g key={`row-${role.role_id}`}>
                <text
                  x={labelWidth - 8}
                  y={padding + idx * cellSize + cellSize / 2 + 4}
                  textAnchor="end"
                  fill={COLORS.text.secondary}
                  fontSize={10}
                >
                  {getRoleAbbr(role.role_name)}
                </text>
              </g>
            ))}

            {/* 顶部角色标签 */}
            {roles.map((role, idx) => (
              <g key={`col-${role.role_id}`}>
                <text
                  x={labelWidth + idx * cellSize + cellSize / 2}
                  y={padding - 8}
                  textAnchor="middle"
                  fill={COLORS.text.secondary}
                  fontSize={10}
                  transform={`rotate(-45, ${labelWidth + idx * cellSize + cellSize / 2}, ${padding - 8})`}
                >
                  {getRoleAbbr(role.role_name)}
                </text>
              </g>
            ))}

            {/* 热力图单元格 */}
            {roles.map((r1, rowIdx) =>
              roles.map((r2, colIdx) => {
                const cell = conflictData[r1.role_id]?.[r2.role_id];
                if (!cell) return null;

                const isHovered = hoveredCell?.role1 === r1.role_id && hoveredCell?.role2 === r2.role_id;
                const isSelected = selectedCell?.role1 === r1.role_id && selectedCell?.role2 === r2.role_id;
                const isDiagonal = r1.role_id === r2.role_id;

                return (
                  <g
                    key={`${r1.role_id}-${r2.role_id}`}
                    style={{ cursor: isDiagonal ? 'default' : 'pointer' }}
                    onMouseEnter={() => !isDiagonal && setHoveredCell(cell)}
                    onMouseLeave={() => setHoveredCell(null)}
                    onClick={() => !isDiagonal && handleCellClick(cell)}
                  >
                    <rect
                      x={labelWidth + colIdx * cellSize + 1}
                      y={padding + rowIdx * cellSize + 1}
                      width={cellSize - 2}
                      height={cellSize - 2}
                      rx={4}
                      fill={isDiagonal ? `${COLORS.border}30` : getConflictBg(cell.intensity)}
                      stroke={isSelected ? COLORS.primary.cyan : isHovered ? COLORS.text.secondary : 'transparent'}
                      strokeWidth={isSelected ? 2 : isHovered ? 1 : 0}
                    />
                    {/* 显示强度数值 */}
                    {!isDiagonal && cell.intensity > 0.2 && (
                      <text
                        x={labelWidth + colIdx * cellSize + cellSize / 2}
                        y={padding + rowIdx * cellSize + cellSize / 2 + 3}
                        textAnchor="middle"
                        fill={cell.intensity > 0.5 ? '#fff' : COLORS.text.primary}
                        fontSize={9}
                        fontWeight={500}
                      >
                        {Math.round(cell.intensity * 100)}
                      </text>
                    )}
                  </g>
                );
              })
            )}
          </svg>
        </div>
      </div>

      {/* 统计信息 */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        <div className="text-center p-2 rounded-lg" style={{ backgroundColor: `${COLORS.bg.dark}50` }}>
          <div className="text-lg font-bold" style={{ color: COLORS.text.primary }}>
            {stats.total}
          </div>
          <div className="text-xs" style={{ color: COLORS.text.muted }}>总对数</div>
        </div>
        <div className="text-center p-2 rounded-lg" style={{ backgroundColor: `${COLORS.status.danger}15` }}>
          <div className="text-lg font-bold" style={{ color: COLORS.status.danger }}>
            {stats.high}
          </div>
          <div className="text-xs" style={{ color: COLORS.status.danger }}>高冲突</div>
        </div>
        <div className="text-center p-2 rounded-lg" style={{ backgroundColor: `${COLORS.status.warning}15` }}>
          <div className="text-lg font-bold" style={{ color: COLORS.status.warning }}>
            {stats.medium}
          </div>
          <div className="text-xs" style={{ color: COLORS.status.warning }}>中等冲突</div>
        </div>
        <div className="text-center p-2 rounded-lg" style={{ backgroundColor: `${COLORS.status.success}15` }}>
          <div className="text-lg font-bold" style={{ color: COLORS.status.success }}>
            {stats.low}
          </div>
          <div className="text-xs" style={{ color: COLORS.status.success }}>低冲突</div>
        </div>
      </div>

      {/* 悬停/选中详情 */}
      {(hoveredCell || selectedCell) && (
        <div
          className="p-3 rounded-lg mb-4"
          style={{ backgroundColor: `${COLORS.bg.dark}80`, border: `1px solid ${COLORS.border}` }}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>
              冲突详情
            </span>
            <div
              className="px-2 py-0.5 rounded text-xs"
              style={{
                backgroundColor: getConflictBg((hoveredCell || selectedCell)!.intensity),
                color: '#fff'
              }}
            >
              {Math.round((hoveredCell || selectedCell)!.intensity * 100)}% 强度
            </div>
          </div>
          <div className="text-sm" style={{ color: COLORS.text.primary }}>
            {(hoveredCell || selectedCell)!.role1Name} ↔ {(hoveredCell || selectedCell)!.role2Name}
          </div>
          {(hoveredCell || selectedCell)!.description && (
            <p className="text-xs mt-1" style={{ color: COLORS.text.muted }}>
              {(hoveredCell || selectedCell)!.description}
            </p>
          )}
        </div>
      )}

      {/* 最高冲突 */}
      {stats.maxCell && (
        <div className="pt-4" style={{ borderTop: `1px solid ${COLORS.border}` }}>
          <div className="flex items-center justify-between">
            <span className="text-xs" style={{ color: COLORS.text.muted }}>
              最高冲突
            </span>
            <div className="flex items-center gap-2">
              <span className="text-sm" style={{ color: COLORS.text.primary }}>
                {stats.maxCell.role1Name} vs {stats.maxCell.role2Name}
              </span>
              <span
                className="px-2 py-0.5 rounded text-xs font-medium"
                style={{
                  backgroundColor: getConflictBg(stats.maxIntensity),
                  color: '#fff'
                }}
              >
                {Math.round(stats.maxIntensity * 100)}%
              </span>
            </div>
          </div>
        </div>
      )}

      {/* 角色列表 */}
      <div className="mt-4 pt-4 space-y-1.5" style={{ borderTop: `1px solid ${COLORS.border}` }}>
        <div className="text-xs font-medium mb-2" style={{ color: COLORS.text.secondary }}>
          角色图例
        </div>
        <div className="flex flex-wrap gap-2">
          {roles.slice(0, 8).map((role, idx) => (
            <div
              key={role.role_id}
              className="px-2 py-1 rounded text-xs"
              style={{ backgroundColor: `${COLORS.bg.dark}50`, color: COLORS.text.secondary }}
            >
              <span className="font-mono mr-1">{idx + 1}.</span>
              {getRoleAbbr(role.role_name)} = {role.role_name}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
