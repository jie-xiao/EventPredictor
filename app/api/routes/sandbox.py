# 沙盘推演 API 路由 - P1阶段
"""
沙盘推演API接口

Endpoints:
- POST /api/v1/sandbox/evolve - 执行沙盘推演
- POST /api/v1/sandbox/decision - 分析决策影响
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.sandbox_service import (
    sandbox_service,
    SandboxEvolutionRequest,
    SandboxEvolutionResponse,
    DecisionImpact
)

router = APIRouter(prefix="/api/v1/sandbox", tags=["Sandbox Evolution"])


class EvolveRequest(BaseModel):
    """推演请求"""
    event_id: str = Field(..., description="事件ID")
    event_title: str = Field(..., description="事件标题")
    event_description: str = Field(..., description="事件描述")
    event_category: str = Field(default="other", description="事件类别")
    importance: int = Field(default=3, ge=1, le=5, description="事件严重程度 1-5")
    steps: int = Field(default=5, ge=1, le=10, description="推演步数 1-10")
    branches_per_step: int = Field(default=3, ge=2, le=5, description="每步分支数 2-5")
    include_decisions: bool = Field(default=True, description="是否包含决策点分析")
    time_unit: str = Field(default="day", description="时间单位: day/week/month")


class DecisionAnalysisRequest(BaseModel):
    """决策分析请求"""
    evolution_id: str = Field(..., description="推演ID")
    decision_id: str = Field(..., description="决策点ID")
    chosen_option: str = Field(..., description="选择的方案")


class EvolveResponse(BaseModel):
    """推演响应"""
    success: bool
    evolution_id: str
    event_id: str
    initial_state: Dict[str, Any]
    steps: List[Dict[str, Any]]
    branches: List[Dict[str, Any]]
    decision_points: List[Dict[str, Any]]
    final_projections: Dict[str, Any]
    recommended_path: Dict[str, Any]
    confidence: float


@router.post("/evolve", response_model=EvolveResponse)
async def evolve_scenario(request: EvolveRequest):
    """
    执行沙盘推演

    根据事件信息，进行多步推演，生成分支场景和决策点分析。

    - **event_id**: 事件唯一标识
    - **event_title**: 事件标题
    - **event_description**: 事件详细描述
    - **steps**: 推演步数（1-10）
    - **branches_per_step**: 每步生成的分支数（2-5）
    - **include_decisions**: 是否识别关键决策点
    - **time_unit**: 时间单位（day/week/month）
    """
    try:
        # 构建请求
        evolution_request = SandboxEvolutionRequest(
            event_id=request.event_id,
            event_title=request.event_title,
            event_description=request.event_description,
            event_category=request.event_category,
            importance=request.importance,
            steps=request.steps,
            branches_per_step=request.branches_per_step,
            include_decisions=request.include_decisions,
            time_unit=request.time_unit
        )

        # 执行推演
        result = await sandbox_service.evolve(evolution_request)

        return EvolveResponse(
            success=True,
            evolution_id=result.evolution_id,
            event_id=result.event_id,
            initial_state=result.initial_state,
            steps=result.steps,
            branches=result.branches,
            decision_points=result.decision_points,
            final_projections=result.final_projections,
            recommended_path=result.recommended_path,
            confidence=result.confidence
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decision/analyze")
async def analyze_decision(request: DecisionAnalysisRequest):
    """
    分析决策影响

    分析特定决策对各分支概率和结果的影响。

    - **evolution_id**: 推演ID
    - **decision_id**: 决策点ID
    - **chosen_option**: 选择的方案
    """
    try:
        result = await sandbox_service.analyze_decision_impact(
            evolution_id=request.evolution_id,
            decision_id=request.decision_id,
            chosen_option=request.chosen_option
        )

        return {
            "success": True,
            "decision_id": result.decision_id,
            "decision_description": result.decision_description,
            "affected_branches": result.affected_branches,
            "probability_changes": result.probability_changes,
            "outcome_changes": result.outcome_changes,
            "confidence": result.confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """沙盘推演服务健康检查"""
    return {
        "status": "healthy",
        "service": "sandbox_service",
        "features": [
            "multi_step_evolution",
            "branch_scenarios",
            "decision_point_analysis",
            "path_recommendation"
        ]
    }
