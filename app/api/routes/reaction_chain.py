# 反应链API路由
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.services.reaction_chain_service import reaction_chain_service


router = APIRouter(prefix="/api/v1/analysis/reaction-chain", tags=["Reaction Chain Analysis"])


class ReactionChainRequest(BaseModel):
    """反应链分析请求"""
    event_id: str = Field(..., description="事件ID")
    title: str = Field(..., description="事件标题")
    description: str = Field(..., description="事件描述")
    category: str = Field(default="Other", description="事件类别")
    importance: int = Field(default=3, ge=1, le=5, description="重要性 1-5")
    timestamp: Optional[str] = Field(default=None, description="时间戳")
    roles: List[str] = Field(..., description="要分析的角色ID列表")
    max_rounds: int = Field(default=3, ge=2, le=5, description="最大反应轮次")
    convergence_threshold: float = Field(default=0.85, ge=0.5, le=1.0, description="收敛阈值")


class EventChainRequest(BaseModel):
    """事件链分析请求"""
    events: List[Dict[str, Any]] = Field(..., description="事件列表（按时间顺序）")
    roles: List[str] = Field(..., description="要分析的角色ID列表")
    max_rounds_per_event: int = Field(default=2, ge=1, le=3, description="每个事件的反应轮次")


class ChainEventInput(BaseModel):
    """事件链中的单个事件"""
    event_id: str
    title: str
    description: str
    category: str = "Other"
    importance: int = 3
    timestamp: str = ""


class EventChainRequestSimple(BaseModel):
    """简化的事件链请求"""
    events: List[ChainEventInput] = Field(..., description="事件列表")
    roles: List[str] = Field(..., description="要分析的角色ID列表")
    max_rounds_per_event: int = Field(default=2, ge=1, le=3, description="每个事件的反应轮次")


class TimelinePredictionRequest(BaseModel):
    """时间线预测请求"""
    event: Dict[str, Any] = Field(..., description="事件信息")
    roles: List[str] = Field(..., description="角色ID列表")
    prediction_horizon: int = Field(default=5, ge=1, le=10, description="预测时间范围（天）")


@router.post(
    "/analyze",
    summary="反应链分析",
    description="运行多方反应的迭代推演，分析各方反应如何相互影响"
)
async def analyze_reaction_chain(request: ReactionChainRequest):
    """执行反应链分析"""
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

        # 验证角色
        from app.agents.roles import ROLES
        valid_roles = [rid for rid in request.roles if rid in ROLES]
        if not valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid roles specified"
            )

        # 执行反应链分析
        result = await reaction_chain_service.run_reaction_chain(
            event=event,
            role_ids=valid_roles,
            max_rounds=request.max_rounds,
            convergence_threshold=request.convergence_threshold
        )

        # 转换为前端期望的格式
        response = {
            "event_id": request.event_id,
            "title": request.title,
            "description": request.description,
            "category": request.category,
            "total_rounds": result.get("total_rounds", 0),
            "converged": result.get("converged", False),
            "timeline": result.get("timeline", []),
            "timeline_tree": result.get("timeline_tree", {}),
            "state_evolution": result.get("state_evolution", []),
            "evolution": result.get("evolution", {}),
            "all_reactions": result.get("all_reactions", []),
            "influence_network": result.get("influence_network", {}),
            "opinion_leaders": result.get("opinion_leaders", []),
            "most_influenced": result.get("most_influenced", []),
            "convergence_trend": result.get("convergence_trend", []),
            "conclusion": result.get("conclusion", {}),
            "timestamp": result.get("timestamp", "")
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reaction chain analysis failed: {str(e)}"
        )


@router.post(
    "/event-chain",
    summary="事件链分析",
    description="分析多个相关事件的串联影响"
)
async def analyze_event_chain(request: EventChainRequestSimple):
    """执行事件链分析"""
    try:
        # 验证角色
        from app.agents.roles import ROLES
        valid_roles = [rid for rid in request.roles if rid in ROLES]
        if not valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid roles specified"
            )

        # 转换事件数据
        events = []
        for e in request.events:
            if hasattr(e, 'dict'):
                events.append(e.dict())
            else:
                events.append(e)

        # 执行事件链分析
        result = await reaction_chain_service.run_event_chain(
            events=events,
            role_ids=valid_roles,
            max_rounds_per_event=request.max_rounds_per_event
        )

        # 转换为前端期望的格式
        response = {
            "event_count": result.get("event_count", 0),
            "events": result.get("events", []),
            "chain_results": result.get("chain_results", []),
            "inter_event_analysis": result.get("inter_event_analysis", {}),
            "event_influences": result.get("event_influences", []),
            "timeline": result.get("timeline", []),
            "conclusion": result.get("conclusion", {}),
            "timestamp": result.get("timestamp", "")
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Event chain analysis failed: {str(e)}"
        )


@router.post(
    "/timeline-prediction",
    summary="时间线预测",
    description="基于当前分析预测事件发展的时间线"
)
async def predict_timeline(request: TimelinePredictionRequest):
    """执行时间线预测"""
    try:
        # 验证角色
        from app.agents.roles import ROLES
        valid_roles = [rid for rid in request.roles if rid in ROLES]
        if not valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid roles specified"
            )

        # 先运行反应链分析
        chain_result = await reaction_chain_service.run_reaction_chain(
            event=request.event,
            role_ids=valid_roles,
            max_rounds=3
        )

        # 基于分析结果生成时间线预测
        predictions = _generate_timeline_predictions(
            chain_result=chain_result,
            horizon=request.prediction_horizon
        )

        return {
            "event_id": request.event.get("id", "unknown"),
            "event_title": request.event.get("title", ""),
            "prediction_horizon": request.prediction_horizon,
            "predictions": predictions["predictions"],
            "confidence_trend": predictions["confidence_trend"],
            "key_milestones": predictions["key_milestones"],
            "potential_branches": predictions["potential_branches"],
            "overall_assessment": predictions["overall_assessment"],
            "based_on_rounds": chain_result.get("total_rounds", 0),
            "timestamp": chain_result.get("timestamp", "")
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Timeline prediction failed: {str(e)}"
        )


def _generate_timeline_predictions(
    chain_result: Dict[str, Any],
    horizon: int
) -> Dict[str, Any]:
    """生成时间线预测"""

    conclusion = chain_result.get("conclusion", {})
    evolution = chain_result.get("evolution", {})
    influence_network = chain_result.get("influence_network", {})

    # 生成预测节点
    predictions = []
    for day in range(1, horizon + 1):
        prediction = {
            "day": day,
            "time": f"T+{day}D",
            "predicted_state": _predict_state_at_day(day, conclusion, evolution),
            "confidence": _calculate_prediction_confidence(day, conclusion),
            "key_actors": _identify_key_actors_at_day(day, influence_network),
            "potential_events": _predict_potential_events(day, conclusion)
        }
        predictions.append(prediction)

    # 生成置信度趋势
    confidence_trend = [p["confidence"] for p in predictions]

    # 识别关键里程碑
    key_milestones = [
        p for p in predictions
        if p["confidence"] >= 0.7 or len(p["potential_events"]) > 0
    ][:3]

    # 识别潜在分支
    potential_branches = _identify_potential_branches(conclusion, predictions)

    # 整体评估
    overall_assessment = conclusion.get("trend_assessment", "需要进一步分析")

    return {
        "predictions": predictions,
        "confidence_trend": confidence_trend,
        "key_milestones": [m["time"] for m in key_milestones],
        "potential_branches": potential_branches,
        "overall_assessment": overall_assessment
    }


def _predict_state_at_day(
    day: int,
    conclusion: Dict[str, Any],
    evolution: Dict[str, Any]
) -> str:
    """预测某天的状态"""
    trend = conclusion.get("trend_assessment", "")

    if day <= 2:
        return "事件发酵期，各方持续关注"
    elif day <= 5:
        return "影响扩散期，相关方开始采取行动"
    else:
        return "事态稳定期，反应趋于收敛"


def _calculate_prediction_confidence(day: int, conclusion: Dict[str, Any]) -> float:
    """计算预测置信度"""
    base_confidence = 0.8
    decay_rate = 0.05

    # 随着时间推移，置信度递减
    confidence = base_confidence * (1 - decay_rate) ** day

    return round(max(confidence, 0.3), 2)


def _identify_key_actors_at_day(
    day: int,
    influence_network: Dict[str, Any]
) -> List[str]:
    """识别某天的关键行动者"""
    nodes = influence_network.get("nodes", [])

    # 按影响力排序
    sorted_nodes = sorted(
        nodes,
        key=lambda n: n.get("opinion_leadership", 0),
        reverse=True
    )

    return [n.get("name", "") for n in sorted_nodes[:3]]


def _predict_potential_events(day: int, conclusion: Dict[str, Any]) -> List[str]:
    """预测潜在事件"""
    tensions = conclusion.get("key_tensions", [])

    events = []
    if tensions and day >= 3:
        for tension in tensions[:2]:
            if tension.get("severity") == "高":
                events.append(f"可能触发{tension.get('type', '冲突')}升级")

    return events


def _identify_potential_branches(
    conclusion: Dict[str, Any],
    predictions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """识别潜在的发展分支"""
    branches = []
    tensions = conclusion.get("key_tensions", [])

    # 基于张力创建分支
    if tensions:
        branches.append({
            "id": "branch_1",
            "name": "乐观情景",
            "description": "各方达成共识，事态平稳发展",
            "probability": 0.4
        })
        branches.append({
            "id": "branch_2",
            "name": "中性情景",
            "description": "各方保持观望，事态缓慢发展",
            "probability": 0.35
        })
        branches.append({
            "id": "branch_3",
            "name": "悲观情景",
            "description": "关键张力升级，事态恶化",
            "probability": 0.25
        })
    else:
        branches.append({
            "id": "branch_1",
            "name": "平稳发展",
            "description": "事态按预期方向发展",
            "probability": 0.6
        })

    return branches


@router.get(
    "/depths",
    summary="获取反应链深度选项",
    description="获取支持的反应链轮次选项"
)
async def get_reaction_chain_depths():
    """获取支持的轮次选项"""
    return {
        "depths": [
            {
                "id": "2",
                "name": "快速分析",
                "description": "2轮反应链",
                "rounds": 2,
                "estimated_time": "30秒"
            },
            {
                "id": "3",
                "name": "标准分析",
                "description": "3轮反应链，包含迭代影响",
                "rounds": 3,
                "estimated_time": "1分钟"
            },
            {
                "id": "5",
                "name": "深度分析",
                "description": "5轮反应链，深度迭代",
                "rounds": 5,
                "estimated_time": "2分钟"
            }
        ]
    }


@router.get(
    "/modes",
    summary="获取分析模式",
    description="获取支持的分析模式"
)
async def get_analysis_modes():
    """获取分析模式"""
    return {
        "modes": [
            {
                "id": "reaction_chain",
                "name": "反应链模式",
                "description": "分析单事件中各方反应的相互影响",
                "icon": "link"
            },
            {
                "id": "event_chain",
                "name": "事件链模式",
                "description": "分析多个相关事件的串联影响",
                "icon": "sequence"
            },
            {
                "id": "timeline_prediction",
                "name": "时间线预测模式",
                "description": "基于当前分析预测事件发展的时间线",
                "icon": "timeline"
            }
        ]
    }


@router.get(
    "/convergence-info",
    summary="获取收敛信息",
    description="解释收敛机制和参数"
)
async def get_convergence_info():
    """获取收敛机制信息"""
    return {
        "description": "反应链会在各方法反应趋于稳定时自动收敛",
        "mechanism": {
            "similarity_check": "比较相邻轮次反应的相似度",
            "emotion_stability": "检测情绪是否稳定",
            "action_consistency": "检测行动是否一致"
        },
        "thresholds": {
            "0.90": "高度敏感 - 较早收敛",
            "0.85": "标准 - 平衡精度和效率",
            "0.75": "宽松 - 允许更多变化",
            "0.50": "极宽松 - 几乎不提前收敛"
        },
        "default_threshold": 0.85
    }


@router.get(
    "/influence-metrics",
    summary="获取影响力指标说明",
    description="解释影响力分析的各项指标"
)
async def get_influence_metrics_info():
    """获取影响力指标说明"""
    return {
        "metrics": {
            "opinion_leadership_score": {
                "name": "意见领袖指数",
                "description": "衡量一个角色对其他角色的影响力",
                "range": "0-1，越高表示影响力越大"
            },
            "influence_receptivity_score": {
                "name": "受影响程度指数",
                "description": "衡量一个角色被其他角色影响的程度",
                "range": "0-1，越高表示越容易被影响"
            },
            "influence_strength": {
                "name": "影响强度",
                "description": "两个角色之间的影响程度",
                "range": "0-1"
            },
            "network_density": {
                "name": "网络密度",
                "description": "影响力网络的紧密程度",
                "range": "0-1，越高表示各方联系越紧密"
            }
        },
        "influence_types": {
            "support": "支持性影响 - 角色立场趋于一致",
            "oppose": "对抗性影响 - 角色立场趋于对立",
            "neutral": "中性影响 - 角色立场保持独立"
        }
    }
