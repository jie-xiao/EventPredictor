# 多Agent协调分析API路由
from fastapi import APIRouter, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

from app.agents.coordinator import (
    agent_coordinator,
    CoordinationMode,
    CoordinationResult
)


router = APIRouter(prefix="/api/v1/analysis/multi-agent", tags=["Multi-Agent Coordination"])


class CoordinationModeEnum(str, Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    ITERATIVE = "iterative"


class MultiAgentAnalysisRequest(BaseModel):
    """多Agent分析请求"""
    event_id: str = Field(..., description="事件ID")
    title: str = Field(..., description="事件标题")
    description: str = Field(..., description="事件描述")
    category: str = Field(default="Other", description="事件类别")
    importance: int = Field(default=3, ge=1, le=5, description="重要性")
    timestamp: Optional[str] = Field(default=None, description="时间戳")

    # Agent配置
    agent_types: Optional[List[str]] = Field(
        default=None,
        description="要使用的Agent类型列表（null表示使用所有）"
    )
    coordination_mode: CoordinationModeEnum = Field(
        default=CoordinationModeEnum.PARALLEL,
        description="协调模式"
    )
    max_iterations: int = Field(
        default=2,
        ge=1,
        le=5,
        description="最大迭代次数"
    )

    # 事件附加信息
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="事件元数据"
    )


class AgentInsight(BaseModel):
    """Agent洞察"""
    agent_type: str
    agent_name: str
    key_findings: List[str]
    confidence: float
    importance_score: float


@router.get(
    "/agents",
    summary="获取可用Agent列表",
    description="列出所有可用的专业Agent"
)
async def get_available_agents():
    """获取可用的Agent列表"""
    agents = agent_coordinator.get_available_agents()

    return {
        "agents": agents,
        "total": len(agents),
        "categories": {
            "geopolitical": "地缘政治分析",
            "economic": "经济影响分析",
            "military": "军事安全分析",
            "social": "社会舆情分析",
            "technology": "科技产业分析"
        }
    }


@router.get(
    "/modes",
    summary="获取协调模式",
    description="列出所有可用的协调模式"
)
async def get_coordination_modes():
    """获取协调模式列表"""
    return {
        "modes": [
            {
                "id": "parallel",
                "name": "并行分析",
                "description": "所有Agent同时独立分析，适合快速获取多角度观点",
                "advantages": ["速度快", "视角独立"],
                "estimated_time": "30秒"
            },
            {
                "id": "sequential",
                "name": "顺序分析",
                "description": "Agent依次分析，后者参考前者结果",
                "advantages": ["逐步深入", "信息累积"],
                "estimated_time": "1分钟"
            },
            {
                "id": "iterative",
                "name": "迭代分析",
                "description": "多轮迭代分析，每轮Agent间交换洞察",
                "advantages": ["深度协作", "观点融合"],
                "estimated_time": "2分钟"
            }
        ]
    }


@router.post(
    "/analyze",
    summary="执行多Agent协调分析",
    description="使用多个专业Agent进行协调分析"
)
async def multi_agent_analyze(request: MultiAgentAnalysisRequest):
    """执行多Agent协调分析"""
    try:
        # 构建事件数据
        event = {
            "id": request.event_id,
            "title": request.title,
            "description": request.description,
            "category": request.category,
            "importance": request.importance,
            "timestamp": request.timestamp or ""
        }

        # 如果有元数据，合并
        if request.metadata:
            event.update(request.metadata)

        # 转换协调模式
        mode_map = {
            CoordinationModeEnum.PARALLEL: CoordinationMode.PARALLEL,
            CoordinationModeEnum.SEQUENTIAL: CoordinationMode.SEQUENTIAL,
            CoordinationModeEnum.ITERATIVE: CoordinationMode.ITERATIVE
        }
        coordination_mode = mode_map[request.coordination_mode]

        # 执行协调分析
        result = await agent_coordinator.coordinate_analysis(
            event=event,
            agent_types=request.agent_types,
            mode=coordination_mode,
            max_iterations=request.max_iterations
        )

        # 转换为响应格式
        response = {
            "event_id": request.event_id,
            "title": request.title,
            "coordination_mode": request.coordination_mode.value,
            "total_rounds": result.total_rounds,
            "agents_used": list(result.agent_results.keys()),

            # 执行摘要
            "executive_summary": result.synthesized_report.get("executive_summary", ""),

            # 关键发现
            "key_findings": result.synthesized_report.get("key_findings", []),

            # 共识和冲突
            "consensus": result.synthesized_report.get("consensus", []),
            "conflicts": result.synthesized_report.get("conflicts", []),

            # 风险评估
            "risk_assessment": result.synthesized_report.get("risk_assessment", {}),

            # 时间线预测
            "timeline_prediction": result.synthesized_report.get("timeline_prediction", {}),

            # 建议
            "recommendations": result.synthesized_report.get("recommendations", []),

            # 各Agent贡献
            "agent_contributions": result.synthesized_report.get("agent_contributions", {}),

            # 详细结果
            "detailed_results": {
                agent_type: {
                    "agent_name": r.agent_name,
                    "key_findings": r.key_findings,
                    "opportunities": r.opportunities,
                    "threats": r.threats,
                    "short_term_forecast": r.short_term_forecast,
                    "medium_term_forecast": r.medium_term_forecast,
                    "long_term_forecast": r.long_term_forecast,
                    "recommendations": r.recommendations,
                    "confidence": r.confidence,
                    "importance_score": r.importance_score
                }
                for agent_type, r in result.agent_results.items()
            },

            # 通信记录
            "communications": [
                {
                    "round": c["round"],
                    "sender": c["sender"],
                    "receiver": c["receiver"],
                    "type": c["type"],
                    "content": c["content"]
                }
                for c in result.to_dict().get("communications", [])
            ],

            # 元数据
            "metadata": result.synthesized_report.get("analysis_metadata", {}),
            "timestamp": result.timestamp
        }

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multi-agent analysis failed: {str(e)}"
        )


@router.post(
    "/compare",
    summary="对比不同Agent观点",
    description="比较不同专业Agent对同一事件的观点差异"
)
async def compare_agent_views(request: MultiAgentAnalysisRequest):
    """对比不同Agent的观点"""
    try:
        # 使用并行模式获取所有Agent的独立分析
        event = {
            "id": request.event_id,
            "title": request.title,
            "description": request.description,
            "category": request.category,
            "importance": request.importance
        }

        result = await agent_coordinator.coordinate_analysis(
            event=event,
            agent_types=request.agent_types,
            mode=CoordinationMode.PARALLEL,
            max_iterations=1
        )

        # 构建对比视图
        comparison = {
            "event_id": request.event_id,
            "event_title": request.title,

            # 观点对比矩阵
            "view_matrix": {},

            # 立场分布
            "stance_distribution": {},

            # 风险评估对比
            "risk_comparison": {},

            # 时间线预测对比
            "timeline_comparison": {},

            # 关键差异
            "key_differences": [],

            # 共同点
            "common_ground": []
        }

        # 填充对比矩阵
        for agent_type, agent_result in result.agent_results.items():
            comparison["view_matrix"][agent_type] = {
                "agent_name": agent_result.agent_name,
                "top_finding": agent_result.key_findings[0] if agent_result.key_findings else "",
                "risk_level": agent_result.risk_assessment.get("overall_risk", "未知"),
                "confidence": agent_result.confidence,
                "top_recommendation": agent_result.recommendations[0] if agent_result.recommendations else ""
            }

            comparison["risk_comparison"][agent_type] = {
                "overall": agent_result.risk_assessment.get("overall_risk", "未知"),
                "level": agent_result.risk_assessment.get("risk_level", 0.5),
                "key_risks": agent_result.risk_assessment.get("key_risks", [])[:3]
            }

            comparison["timeline_comparison"][agent_type] = {
                "short_term": agent_result.short_term_forecast,
                "medium_term": agent_result.medium_term_forecast,
                "long_term": agent_result.long_term_forecast
            }

        # 识别共同点
        all_findings = []
        for r in result.agent_results.values():
            all_findings.extend(r.key_findings)

        # 简单查找共同关键词
        from collections import Counter
        all_words = ' '.join(all_findings).split()
        word_freq = Counter(all_words)
        common_words = [w for w, c in word_freq.most_common(10) if len(w) > 2 and c > 1]
        comparison["common_ground"] = [f"多分析师共同关注'{w}'相关议题" for w in common_words[:3]]

        # 识别关键差异
        risk_values = {
            t: r.risk_assessment.get("risk_level", 0.5)
            for t, r in result.agent_results.items()
        }

        if risk_values:
            max_risk_agent = max(risk_values, key=risk_values.get)
            min_risk_agent = min(risk_values, key=risk_values.get)
            risk_gap = risk_values[max_risk_agent] - risk_values[min_risk_agent]

            if risk_gap > 0.2:
                comparison["key_differences"].append({
                    "type": "风险评估差异",
                    "description": f"{result.agent_results[max_risk_agent].agent_name}评估风险({risk_values[max_risk_agent]:.0%})明显高于{result.agent_results[min_risk_agent].agent_name}({risk_values[min_risk_agent]:.0%})",
                    "significance": "高" if risk_gap > 0.4 else "中"
                })

        comparison["timestamp"] = result.timestamp

        return comparison

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"View comparison failed: {str(e)}"
        )


@router.get(
    "/health",
    summary="检查Agent状态",
    description="检查所有Agent的健康状态"
)
async def check_agent_health():
    """检查Agent健康状态"""
    agents = agent_coordinator.get_available_agents()

    return {
        "status": "healthy",
        "total_agents": len(agents),
        "agents": [
            {
                "type": a["type"],
                "name": a["name"],
                "status": "ready"
            }
            for a in agents
        ],
        "coordinator_status": "active"
    }
