/**
 * SentimentRadar.tsx
 *
 * 情感雷达图组件 - 可视化各角色的情感倾向
 * 显示维度：乐观、焦虑、愤怒、期待、谨慎、自信
 */
import { useMemo } from 'react';
import { AnalysisResult, RoleAnalysis } from '../../services/api';

// ============ Design System Colors ============
const COLORS = {
  primary: { cyan: '#00E5FF', blue: '#0077FF' },
  status: { success: '#10B981', warning: '#F59E0B', danger: '#EF4444', info: '#3B82F6' },
  bg: { dark: '#0A0E1A', card: '#0F172A' },
  border: '#1E293B',
  text: { primary: '#F8FAFC', secondary: '#94A3B8', muted: '#64748B' }
};

// 情感维度定义
const SENTIMENT_DIMENSIONS = [
  { key: 'optimistic', label: '乐观', color: '#10B981' },
  { key: 'anxious', label: '焦虑', color: '#F59E0B' },
  { key: 'angry', label: '愤怒', color: '#EF4444' },
  { key: 'hopeful', label: '期待', color: '#00E5FF' },
  { key: 'cautious', label: '谨慎', color: '#3B82F6' },
  { key: 'confident', label: '自信', color: '#8B5CF6' }
];

// 情感关键词映射
const EMOTION_KEYWORDS: Record<string, { dim: string; score: number }> = {
  // 正面情感
  '乐观': { dim: 'optimistic', score: 0.8 },
  '积极': { dim: 'optimistic', score: 0.7 },
  '期待': { dim: 'hopeful', score: 0.8 },
  '希望': { dim: 'hopeful', score: 0.7 },
  '自信': { dim: 'confident', score: 0.8 },
  '坚定': { dim: 'confident', score: 0.7 },
  '支持': { dim: 'optimistic', score: 0.6 },

  // 负面情感
  '焦虑': { dim: 'anxious', score: 0.8 },
  '担忧': { dim: 'anxious', score: 0.7 },
  '愤怒': { dim: 'angry', score: 0.9 },
  '不满': { dim: 'angry', score: 0.7 },
  '反对': { dim: 'angry', score: 0.6 },
  '恐惧': { dim: 'anxious', score: 0.8 },

  // 中性情感
  '谨慎': { dim: 'cautious', score: 0.7 },
  '观望': { dim: 'cautious', score: 0.6 },
  '关注': { dim: 'cautious', score: 0.5 },
  '评估': { dim: 'cautious', score: 0.4 },
  '冷静': { dim: 'cautious', score: 0.5 },

  // 英文映射
  'optimistic': { dim: 'optimistic', score: 0.8 },
  'positive': { dim: 'optimistic', score: 0.7 },
  'hopeful': { dim: 'hopeful', score: 0.8 },
  'confident': { dim: 'confident', score: 0.8 },
  'anxious': { dim: 'anxious', score: 0.8 },
  'worried': { dim: 'anxious', score: 0.7 },
  'angry': { dim: 'angry', score: 0.9 },
  'cautious': { dim: 'cautious', score: 0.7 },
  'concerned': { dim: 'cautious', score: 0.6 }
};

interface SentimentRadarProps {
  result: AnalysisResult;
  maxRoles?: number;
}

// 从角色分析中提取情感分数
const extractSentiments = (analysis: RoleAnalysis): Record<string, number> => {
  const sentiments: Record<string, number> = {};

  // 初始化所有维度
  SENTIMENT_DIMENSIONS.forEach(dim => {
    sentiments[dim.key] = 0.3; // 默认基础值
  });

  const emotion = analysis.reaction?.emotion?.toLowerCase() || '';
  const statement = analysis.reaction?.statement || analysis.reasoning || '';
  const combinedText = `${emotion} ${statement}`.toLowerCase();

  // 根据关键词计算情感分数
  Object.entries(EMOTION_KEYWORDS).forEach(([keyword, mapping]) => {
    if (combinedText.includes(keyword.toLowerCase())) {
      const currentScore = sentiments[mapping.dim] || 0.3;
      sentiments[mapping.dim] = Math.min(1, currentScore + mapping.score * 0.3);
    }
  });

  // 根据置信度调整自信度
  if (analysis.confidence > 0.7) {
    sentiments.confident = Math.min(1, sentiments.confident + 0.3);
  } else if (analysis.confidence < 0.5) {
    sentiments.anxious = Math.min(1, sentiments.anxious + 0.2);
  }

  return sentiments;
};

// 计算雷达图点位
const calculateRadarPoints = (sentiments: Record<string, number>, centerX: number, centerY: number, radius: number): string => {
  const points = SENTIMENT_DIMENSIONS.map((dim, index) => {
    const angle = (index * 60 - 90) * (Math.PI / 180); // 从顶部开始，每60度一个点
    const value = sentiments[dim.key] || 0.3;
    const r = radius * value;
    const x = centerX + r * Math.cos(angle);
    const y = centerY + r * Math.sin(angle);
    return `${x},${y}`;
  });

  return points.join(' ');
};

export default function SentimentRadar({ result, maxRoles = 5 }: SentimentRadarProps) {
  // 提取各角色的情感数据
  const roleSentiments = useMemo(() => {
    const analyses = result.analyses?.slice(0, maxRoles) || [];
    return analyses.map(analysis => ({
      role: analysis,
      sentiments: extractSentiments(analysis)
    }));
  }, [result.analyses, maxRoles]);

  // 计算平均情感
  const averageSentiments = useMemo(() => {
    const avg: Record<string, number> = {};
    SENTIMENT_DIMENSIONS.forEach(dim => {
      const values = roleSentiments.map(r => r.sentiments[dim.key] || 0.3);
      avg[dim.key] = values.reduce((a, b) => a + b, 0) / values.length;
    });
    return avg;
  }, [roleSentiments]);

  // SVG参数
  const size = 280;
  const centerX = size / 2;
  const centerY = size / 2;
  const maxRadius = 110;

  // 生成网格圆环
  const gridRings = [0.25, 0.5, 0.75, 1.0];

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
            情感雷达分析
          </h3>
          <p className="text-xs mt-1" style={{ color: COLORS.text.muted }}>
            各角色情感倾向分布
          </p>
        </div>
        <div className="px-3 py-1.5 rounded-lg text-xs font-medium"
          style={{ backgroundColor: `${COLORS.primary.cyan}15`, color: COLORS.primary.cyan }}>
          {roleSentiments.length} 个角色
        </div>
      </div>

      {/* 雷达图 SVG */}
      <div className="flex justify-center mb-5">
        <svg width={size} height={size} className="overflow-visible">
          {/* 背景网格圆环 */}
          {gridRings.map((ring, idx) => (
            <circle
              key={idx}
              cx={centerX}
              cy={centerY}
              r={maxRadius * ring}
              fill="none"
              stroke={COLORS.border}
              strokeWidth={1}
              strokeDasharray={ring === 1 ? 'none' : '4,4'}
              opacity={0.5}
            />
          ))}

          {/* 轴线 */}
          {SENTIMENT_DIMENSIONS.map((dim, idx) => {
            const angle = (idx * 60 - 90) * (Math.PI / 180);
            const endX = centerX + maxRadius * Math.cos(angle);
            const endY = centerY + maxRadius * Math.sin(angle);
            return (
              <line
                key={dim.key}
                x1={centerX}
                y1={centerY}
                x2={endX}
                y2={endY}
                stroke={COLORS.border}
                strokeWidth={1}
                opacity={0.5}
              />
            );
          })}

          {/* 维度标签 */}
          {SENTIMENT_DIMENSIONS.map((dim, idx) => {
            const angle = (idx * 60 - 90) * (Math.PI / 180);
            const labelRadius = maxRadius + 25;
            const x = centerX + labelRadius * Math.cos(angle);
            const y = centerY + labelRadius * Math.sin(angle);
            return (
              <text
                key={dim.key}
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="middle"
                fill={dim.color}
                fontSize={11}
                fontWeight={500}
              >
                {dim.label}
              </text>
            );
          })}

          {/* 平均值雷达区域 */}
          <polygon
            points={calculateRadarPoints(averageSentiments, centerX, centerY, maxRadius)}
            fill={`${COLORS.primary.cyan}25`}
            stroke={COLORS.primary.cyan}
            strokeWidth={2}
            opacity={0.8}
          />

          {/* 各角色雷达点 */}
          {roleSentiments.slice(0, 3).map((rs, idx) => {
            const colors = ['#10B981', '#F59E0B', '#EF4444'];
            return (
              <polygon
                key={rs.role.role_id}
                points={calculateRadarPoints(rs.sentiments, centerX, centerY, maxRadius)}
                fill="transparent"
                stroke={colors[idx % colors.length]}
                strokeWidth={1.5}
                strokeDasharray={idx === 0 ? 'none' : '4,2'}
                opacity={0.6}
              />
            );
          })}

          {/* 中心点 */}
          <circle
            cx={centerX}
            cy={centerY}
            r={4}
            fill={COLORS.primary.cyan}
          />
        </svg>
      </div>

      {/* 图例 */}
      <div className="space-y-3">
        <div className="text-xs font-medium mb-2" style={{ color: COLORS.text.secondary }}>
          情感维度解读
        </div>

        <div className="grid grid-cols-3 gap-2">
          {SENTIMENT_DIMENSIONS.slice(0, 6).map(dim => (
            <div key={dim.key} className="flex items-center gap-2">
              <div
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: dim.color }}
              />
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <span className="text-xs" style={{ color: COLORS.text.muted }}>
                    {dim.label}
                  </span>
                  <span className="text-xs font-mono" style={{ color: dim.color }}>
                    {Math.round((averageSentiments[dim.key] || 0) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 主导情感 */}
      <div className="mt-4 pt-4" style={{ borderTop: `1px solid ${COLORS.border}` }}>
        <div className="flex items-center justify-between">
          <span className="text-xs" style={{ color: COLORS.text.muted }}>
            主导情感
          </span>
          <div className="flex items-center gap-2">
            {(() => {
              const sortedDims = [...SENTIMENT_DIMENSIONS].sort(
                (a, b) => (averageSentiments[b.key] || 0) - (averageSentiments[a.key] || 0)
              );
              const topDim = sortedDims[0];
              return (
                <>
                  <div
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: topDim.color }}
                  />
                  <span className="text-sm font-medium" style={{ color: topDim.color }}>
                    {topDim.label} ({Math.round((averageSentiments[topDim.key] || 0) * 100)}%)
                  </span>
                </>
              );
            })()}
          </div>
        </div>
      </div>

      {/* 角色情感列表 */}
      <div className="mt-4 space-y-2">
        <div className="text-xs font-medium" style={{ color: COLORS.text.secondary }}>
          角色情感概览
        </div>
        {roleSentiments.slice(0, 4).map(rs => {
          // 找出该角色的主导情感
          const sortedDims = [...SENTIMENT_DIMENSIONS].sort(
            (a, b) => (rs.sentiments[b.key] || 0) - (rs.sentiments[a.key] || 0)
          );
          const topDim = sortedDims[0];
          const topScore = rs.sentiments[topDim.key] || 0;

          return (
            <div
              key={rs.role.role_id}
              className="flex items-center justify-between p-2 rounded-lg"
              style={{ backgroundColor: `${COLORS.bg.dark}50` }}
            >
              <div className="flex items-center gap-2">
                <div
                  className="w-2 h-2 rounded-full"
                  style={{ backgroundColor: topDim.color }}
                />
                <span className="text-xs truncate max-w-[120px]" style={{ color: COLORS.text.primary }}>
                  {rs.role.role_name}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs" style={{ color: topDim.color }}>
                  {topDim.label}
                </span>
                <span className="text-xs font-mono" style={{ color: COLORS.text.muted }}>
                  {Math.round(topScore * 100)}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
