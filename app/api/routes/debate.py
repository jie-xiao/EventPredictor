# Agent辩论API路由
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel, Field
import json
import asyncio
from datetime import datetime

from app.agents.debate import debate_orchestrator, DebateResult


router = APIRouter(prefix="/api/v1/analysis", tags=["Debate Analysis"])


class DebateRequest(BaseModel):
    """辩论分析请求"""
    event_id: str = Field(..., description="事件ID")
    title: str = Field(..., description="事件标题")
    description: str = Field(..., description="事件描述")
    category: str = Field(default="Other", description="事件类别")
    importance: int = Field(default=3, ge=1, le=5, description="重要性 1-5")
    timestamp: Optional[str] = Field(default=None, description="时间戳")
    roles: List[str] = Field(..., min_items=2, description="参与辩论的角色ID列表（至少2个）")
    depth: str = Field(default="standard", description="辩论深度 (quick/standard/deep)")


class DebateRoundResponse(BaseModel):
    """辩论轮次响应"""
    round_number: int
    round_type: str
    analyses: List[dict]
    timestamp: str


class DebateAnalysisResponse(BaseModel):
    """辩论分析响应"""
    event_id: str
    title: str
    description: str
    category: str
    depth: str
    rounds: List[DebateRoundResponse]
    final_synthesis: dict
    agreement_scores: dict
    key_conflicts: List[dict]
    consensus_points: List[str]
    analyses: List[dict]  # 最后一个轮次的分析结果
    cross_analysis: dict  # 从final_synthesis提取的交叉分析
    prediction: dict  # 从final_synthesis提取的预测
    overall_confidence: float
    timestamp: str


# 存储进行中的分析任务
_analysis_tasks: dict = {}


@router.post(
    "/debate",
    response_model=DebateAnalysisResponse,
    summary="辩论式多Agent分析",
    description="使用辩论模式进行多Agent分析，支持不同深度的辩论轮次"
)
async def analyze_with_debate(request: DebateRequest):
    """
    使用辩论模式进行多Agent分析

    辩论深度:
    - quick: 1轮分析，快速获取各角色观点
    - standard: 2轮分析，包含交叉审视
    - deep: 3轮分析，包含交叉审视和反驳/支持
    """
    try:
        # 构建事件数据
        event = {
            "id": request.event_id,
            "title": request.title,
            "description": request.description,
            "category": request.category,
            "importance": request.importance,
            "timestamp": request.timestamp or datetime.utcnow().isoformat()
        }

        # 执行辩论分析
        debate_result = await debate_orchestrator.run_debate(
            event=event,
            role_ids=request.roles,
            depth=request.depth
        )

        # 转换为响应格式
        response = _convert_debate_result_to_response(debate_result, request)

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debate analysis failed: {str(e)}"
        )


@router.post(
    "/debate/stream",
    summary="流式辩论分析（SSE）",
    description="使用SSE流式返回辩论分析进度"
)
async def analyze_with_debate_stream(request: DebateRequest):
    """
    使用SSE流式返回辩论分析进度

    返回格式:
    - event: progress
    - data: {"stage": "initial", "progress": 33, "message": "..."}
    - event: complete
    - data: {"result": {...}}
    """

    event_data = {
        "id": request.event_id,
        "title": request.title,
        "description": request.description,
        "category": request.category,
        "importance": request.importance,
        "timestamp": request.timestamp or datetime.utcnow().isoformat()
    }

    async def event_generator():
        try:
            # 开始事件
            yield f"event: start\ndata: {json.dumps({'message': '开始辩论分析'})}\n\n"

            # 阶段1: 初始分析
            yield f"event: progress\ndata: {json.dumps({'stage': 'initial', 'progress': 10, 'message': '正在进行初始分析...'})}\n\n"

            # 执行辩论
            debate_result = await debate_orchestrator.run_debate(
                event=event_data,
                role_ids=request.roles,
                depth=request.depth
            )

            # 根据深度发送进度
            total_rounds = {"quick": 1, "standard": 2, "deep": 3}.get(request.depth, 2)
            for i, round_obj in enumerate(debate_result.rounds):
                progress = 10 + (i + 1) * (80 // total_rounds)
                yield f"event: progress\ndata: {json.dumps({'stage': round_obj.round_type, 'progress': progress, 'message': f'完成第{round_obj.round_number}轮分析'})}\n\n"

            # 综合分析
            yield f"event: progress\ndata: {json.dumps({'stage': 'synthesis', 'progress': 95, 'message': '正在综合分析...'})}\n\n"

            # 完成事件
            response = _convert_debate_result_to_response(debate_result, request)
            yield f"event: complete\ndata: {json.dumps(response, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get(
    "/debate/depths",
    summary="获取可用的辩论深度",
    description="获取支持的辩论深度选项"
)
async def get_debate_depths():
    """获取支持的辩论深度"""
    return {
        "depths": [
            {
                "id": "quick",
                "name": "快速分析",
                "description": "1轮分析，快速获取各角色独立观点",
                "rounds": 1,
                "estimated_time": "30秒"
            },
            {
                "id": "standard",
                "name": "标准分析",
                "description": "2轮分析，包含初始分析和交叉审视",
                "rounds": 2,
                "estimated_time": "1分钟"
            },
            {
                "id": "deep",
                "name": "深度分析",
                "description": "3轮分析，包含交叉审视和反驳/支持",
                "rounds": 3,
                "estimated_time": "2分钟"
            }
        ]
    }


def _convert_debate_result_to_response(
    debate_result: DebateResult,
    request: DebateRequest
) -> dict:
    """将辩论结果转换为API响应格式"""

    # 获取最后一轮分析作为主要分析结果
    final_analyses = []
    if debate_result.rounds:
        final_analyses = debate_result.rounds[-1].analyses

    # 计算整体置信度
    if final_analyses:
        avg_confidence = sum(
            a.get("confidence", 0.5) for a in final_analyses
        ) / len(final_analyses)
    else:
        avg_confidence = 0.5

    # 格式化轮次
    rounds_response = [
        {
            "round_number": r.round_number,
            "round_type": r.round_type,
            "analyses": r.analyses,
            "timestamp": r.timestamp
        }
        for r in debate_result.rounds
    ]

    return {
        "event_id": request.event_id,
        "title": request.title,
        "description": request.description,
        "category": request.category,
        "depth": request.depth,
        "rounds": rounds_response,
        "final_synthesis": debate_result.final_synthesis,
        "agreement_scores": debate_result.agreement_scores,
        "key_conflicts": debate_result.key_conflicts,
        "consensus_points": debate_result.consensus_points,
        "analyses": final_analyses,
        "cross_analysis": {
            "conflicts": debate_result.key_conflicts,
            "synergies": debate_result.final_synthesis.get("synergies", []),
            "consensus": debate_result.consensus_points,
            "agreements": debate_result.final_synthesis.get("agreements", [])
        },
        "prediction": {
            "trend": debate_result.final_synthesis.get("overall_trend", "平稳"),
            "confidence": debate_result.final_synthesis.get("trend_confidence", avg_confidence),
            "summary": debate_result.final_synthesis.get("summary", ""),
            "timeline": debate_result.final_synthesis.get("timeline", []),
            "recommended_actions": debate_result.final_synthesis.get("recommended_actions", [])
        },
        "overall_confidence": avg_confidence,
        "timestamp": debate_result.timestamp
    }
