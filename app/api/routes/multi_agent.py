# 多Agent角色分析API
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.multi_agent_service import multi_agent_service
from app.agents.roles import get_all_role_ids, get_role, ROLES


router = APIRouter(prefix="/api/v1/analysis", tags=["Multi-Agent Analysis"])


class MultiAgentAnalyzeRequest(BaseModel):
    """多Agent分析请求"""
    event_id: str = Field(..., description="事件ID")
    title: str = Field(..., description="事件标题")
    description: str = Field(..., description="事件描述")
    category: str = Field(default="Other", description="事件类别")
    importance: int = Field(default=3, ge=1, le=5, description="重要性 1-5")
    timestamp: Optional[str] = Field(default=None, description="时间戳")
    roles: List[str] = Field(..., description="要分析的角色ID列表")
    depth: str = Field(default="standard", description="分析深度 (simple/standard/detailed)")


class RoleListResponse(BaseModel):
    """角色列表响应"""
    roles: List[dict]
    categories: List[str]


@router.get(
    "/roles",
    response_model=RoleListResponse,
    summary="获取可用角色列表",
    description="获取所有可用的分析角色"
)
async def list_roles():
    """获取所有可用角色"""
    roles_data = []
    for role_id, role in ROLES.items():
        roles_data.append({
            "id": role.id,
            "name": role.name,
            "category": role.category.value if hasattr(role.category, 'value') else role.category,
            "description": role.description,
            "focus_points": role.focus_points
        })

    return RoleListResponse(
        roles=roles_data,
        categories=["government", "corporation", "public", "media", "investor"]
    )


@router.get(
    "/roles/{role_id}",
    summary="获取角色详情",
    description="获取指定角色的详细信息"
)
async def get_role_detail(role_id: str):
    """获取角色详情"""
    role = get_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role {role_id} not found"
        )

    return {
        "id": role.id,
        "name": role.name,
        "category": role.category.value if hasattr(role.category, 'value') else role.category,
        "description": role.description,
        "stance": role.stance,
        "decision_traits": role.decision_traits,
        "language_style": role.language_style,
        "focus_points": role.focus_points,
        "system_prompt": role.system_prompt[:200] + "..."  # 限制显示长度
    }


@router.post(
    "/multi",
    summary="多Agent角色分析",
    description="使用多个角色进行并行分析"
)
async def analyze_multi_agent(request: MultiAgentAnalyzeRequest):
    """使用多个角色进行多角度分析"""
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

        # 验证角色ID
        valid_roles = [rid for rid in request.roles if rid in ROLES]
        if not valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid roles specified"
            )

        # 执行多Agent分析
        result = await multi_agent_service.analyze_with_roles(
            event=event,
            role_ids=valid_roles,
            depth=request.depth
        )

        # 获取角色分析结果
        role_analyses = result.get("role_analyses", [])

        # 计算整体置信度
        if role_analyses:
            avg_confidence = sum(
                a.get("confidence", 0.5) for a in role_analyses
            ) / len(role_analyses)
        else:
            avg_confidence = 0.5

        # 从synthesis获取预测数据
        synthesis = result.get("synthesis", {})
        cross_analysis = result.get("cross_analysis", {})

        # 转换为前端期望的格式
        response = {
            "event_id": request.event_id,
            "title": request.title,
            "description": request.description,
            "category": request.category,
            "analyses": role_analyses,
            "cross_analysis": {
                "conflicts": cross_analysis.get("conflicts", []),
                "synergies": cross_analysis.get("synergies", []),
                "consensus": cross_analysis.get("consensus", []),
                "agreements": cross_analysis.get("agreements", []),
                "key_tensions": cross_analysis.get("key_tensions", [])
            },
            "prediction": {
                "trend": synthesis.get("overall_trend", "平稳"),
                "confidence": synthesis.get("confidence", avg_confidence),
                "summary": synthesis.get("summary", ""),
                "timeline": synthesis.get("timeline", []),
                "recommended_actions": synthesis.get("recommended_actions", []),
                "key_insights": synthesis.get("key_insights", [])
            },
            "overall_confidence": avg_confidence,
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
            detail=f"Multi-agent analysis failed: {str(e)}"
        )


@router.get(
    "/categories",
    summary="获取角色类别",
    description="获取所有角色类别"
)
async def get_categories():
    """获取角色类别"""
    return {
        "categories": [
            {
                "id": "government",
                "name": "政府",
                "description": "各国政府机构代表",
                "roles": ["cn_gov", "us_gov", "eu_gov", "ru_gov"]
            },
            {
                "id": "corporation",
                "name": "企业",
                "description": "各类企业组织代表",
                "roles": ["tech_giant", "financial_giant", "cn_corp"]
            },
            {
                "id": "public",
                "name": "民众",
                "description": "普通民众和社会群体",
                "roles": ["common_public", "intellectual", "netizen"]
            },
            {
                "id": "media",
                "name": "媒体",
                "description": "各类媒体机构",
                "roles": ["mainstream_media", "social_media", "official_media"]
            },
            {
                "id": "investor",
                "name": "投资者",
                "description": "各类投资者群体",
                "roles": ["institutional_investor", "retail_investor", "venture_capitalist"]
            }
        ]
    }


@router.get(
    "/presets/{preset_name}",
    summary="获取预设角色组合",
    description="获取常用的角色组合预设"
)
async def get_role_preset(preset_name: str):
    """获取预设角色组合"""
    presets = {
        "full": {
            "name": "完整分析",
            "description": "包含所有角色类型",
            "roles": ["cn_gov", "us_gov", "tech_giant", "common_public", "mainstream_media", "institutional_investor"]
        },
        "government": {
            "name": "政府视角",
            "description": "政府机构分析",
            "roles": ["cn_gov", "us_gov", "eu_gov", "ru_gov"]
        },
        "market": {
            "name": "市场视角",
            "description": "投资者和企业视角",
            "roles": ["tech_giant", "financial_giant", "institutional_investor", "retail_investor"]
        },
        "public": {
            "name": "社会视角",
            "description": "民众和媒体视角",
            "roles": ["common_public", "intellectual", "netizen", "mainstream_media", "social_media"]
        }
    }

    if preset_name not in presets:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset {preset_name} not found"
        )

    return presets[preset_name]


@router.get(
    "/depths",
    summary="获取可用的分析深度",
    description="获取支持的分析深度选项"
)
async def get_analysis_depths():
    """获取支持的分析深度"""
    return {
        "depths": [
            {
                "id": "simple",
                "name": "简单分析",
                "description": "快速分析，提供简洁的要点"
            },
            {
                "id": "standard",
                "name": "标准分析",
                "description": "全面分析，包括影响和行动建议"
            },
            {
                "id": "detailed",
                "name": "详细分析",
                "description": "深入分析，包括详细推理和时间线"
            }
        ]
    }
