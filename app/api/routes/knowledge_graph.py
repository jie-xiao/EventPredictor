# 知识图谱API路由
"""
P2阶段功能：知识图谱管理API
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from pydantic import BaseModel, Field

from app.services.knowledge_graph_service import (
    knowledge_graph_service,
    Entity, Relation, EntityType, RelationType
)


router = APIRouter(prefix="/api/v1/knowledge-graph", tags=["Knowledge Graph"])


# ============ 请求/响应模型 ============

class EntityCreateRequest(BaseModel):
    """创建实体请求"""
    name: str = Field(..., description="实体名称")
    type: str = Field(..., description="实体类型")
    aliases: List[str] = Field(default_factory=list, description="别名列表")
    properties: dict = Field(default_factory=dict, description="自定义属性")
    importance: float = Field(default=1.0, description="重要性权重")


class RelationCreateRequest(BaseModel):
    """创建关系请求"""
    source_id: str = Field(..., description="源实体ID")
    target_id: str = Field(..., description="目标实体ID")
    type: str = Field(..., description="关系类型")
    properties: dict = Field(default_factory=dict, description="自定义属性")
    weight: float = Field(default=1.0, description="关系权重")
    source_event_id: Optional[str] = Field(default=None, description="来源事件ID")


class EntityExtractRequest(BaseModel):
    """从文本提取实体请求"""
    text: str = Field(..., description="待提取的文本")
    event_id: Optional[str] = Field(default=None, description="关联事件ID")


class PathQueryRequest(BaseModel):
    """路径查询请求"""
    source_id: str = Field(..., description="起始实体ID")
    target_id: str = Field(..., description="目标实体ID")
    max_depth: int = Field(default=5, ge=1, le=10, description="最大搜索深度")


class RelationSearchRequest(BaseModel):
    """关系搜索请求"""
    entity_id: str = Field(..., description="实体ID")
    direction: str = Field(default="both", description="方向: incoming/outgoing/both")
    relation_type: Optional[str] = Field(default=None, description="关系类型过滤")


# ============ 实体端点 ============

@router.get("/entities", summary="获取实体列表")
async def list_entities(
    entity_type: Optional[str] = Query(default=None, description="按类型过滤"),
    search: Optional[str] = Query(default=None, description="搜索关键词"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """获取实体列表，支持类型过滤和关键词搜索"""
    try:
        result = knowledge_graph_service.search_entities(
            query=search or "",
            entity_type=entity_type,
            limit=limit,
            offset=offset
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实体列表失败: {str(e)}")


@router.get("/entities/{entity_id}", summary="获取实体详情")
async def get_entity(entity_id: str):
    """获取单个实体的详细信息"""
    entity = knowledge_graph_service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"实体不存在: {entity_id}")
    return {"success": True, "data": entity.to_dict()}


@router.post("/entities", summary="创建实体")
async def create_entity(request: EntityCreateRequest):
    """创建新的实体节点"""
    try:
        entity_type = EntityType(request.type)
        entity = knowledge_graph_service.add_entity(
            name=request.name,
            entity_type=entity_type,
            aliases=request.aliases,
            properties=request.properties,
            importance=request.importance
        )
        return {"success": True, "data": entity.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建实体失败: {str(e)}")


@router.delete("/entities/{entity_id}", summary="删除实体")
async def delete_entity(entity_id: str):
    """删除实体及其所有关系"""
    try:
        success = knowledge_graph_service.remove_entity(entity_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"实体不存在: {entity_id}")
        return {"success": True, "message": f"实体 {entity_id} 已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除实体失败: {str(e)}")


# ============ 关系端点 ============

@router.get("/relations", summary="获取关系列表")
async def list_relations(
    source_id: Optional[str] = Query(default=None),
    target_id: Optional[str] = Query(default=None),
    relation_type: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """获取关系列表"""
    try:
        relations = []
        for rel in knowledge_graph_service.relations.values():
            if source_id and rel.source != source_id:
                continue
            if target_id and rel.target != target_id:
                continue
            if relation_type and rel.type.value != relation_type:
                continue
            relations.append(rel.to_dict())
        
        total = len(relations)
        paginated = relations[offset:offset + limit]
        return {"success": True, "data": {"relations": paginated, "total": total}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关系列表失败: {str(e)}")


@router.post("/relations", summary="创建关系")
async def create_relation(request: RelationCreateRequest):
    """创建新的关系边"""
    try:
        rel_type = RelationType(request.type)
        relation = knowledge_graph_service.add_relation(
            source_id=request.source_id,
            target_id=request.target_id,
            relation_type=rel_type,
            properties=request.properties,
            weight=request.weight,
            source_event_id=request.source_event_id
        )
        return {"success": True, "data": relation.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建关系失败: {str(e)}")


@router.delete("/relations/{relation_id}", summary="删除关系")
async def delete_relation(relation_id: str):
    """删除关系"""
    try:
        success = knowledge_graph_service.remove_relation(relation_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"关系不存在: {relation_id}")
        return {"success": True, "message": f"关系 {relation_id} 已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除关系失败: {str(e)}")


# ============ 查询端点 ============

@router.post("/query/path", summary="路径查询")
async def query_path(request: PathQueryRequest):
    """查询两个实体之间的关系路径"""
    try:
        path = knowledge_graph_service.find_path(
            start_id=request.source_id,
            end_id=request.target_id,
            max_depth=request.max_depth
        )
        return {"success": True, "data": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"路径查询失败: {str(e)}")


@router.post("/query/neighbors", summary="查询邻居实体")
async def query_neighbors(request: RelationSearchRequest):
    """查询实体的邻居节点"""
    try:
        neighbors = knowledge_graph_service.get_neighbors(
            entity_id=request.entity_id,
            direction=request.direction
        )
        if request.relation_type:
            neighbors = [n for n in neighbors if n.get("relation_type") == request.relation_type]
        return {"success": True, "data": neighbors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"邻居查询失败: {str(e)}")


@router.post("/extract", summary="从文本提取实体")
async def extract_entities(request: EntityExtractRequest):
    """从文本中提取实体和关系"""
    try:
        result = knowledge_graph_service.extract_from_text(
            text=request.text,
            event_id=request.event_id
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"实体提取失败: {str(e)}")


# ============ 统计端点 ============

@router.get("/statistics", summary="获取图谱统计")
async def get_statistics():
    """获取知识图谱的整体统计信息"""
    try:
        stats = knowledge_graph_service.get_statistics()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.get("/central", summary="获取中心实体")
async def get_central_entities(
    top_n: int = Query(default=10, ge=1, le=50)
):
    """获取影响力最大的中心实体"""
    try:
        entities = knowledge_graph_service.find_central_entities(top_n=top_n)
        return {"success": True, "data": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取中心实体失败: {str(e)}")


@router.get("/entity-types", summary="获取实体类型")
async def get_entity_types():
    """获取所有可用的实体类型"""
    types = [{"value": t.value, "label": t.value} for t in EntityType]
    return {"success": True, "data": types}


@router.get("/relation-types", summary="获取关系类型")
async def get_relation_types():
    """获取所有可用的关系类型"""
    types = [{"value": t.value, "label": t.value} for t in RelationType]
    return {"success": True, "data": types}
