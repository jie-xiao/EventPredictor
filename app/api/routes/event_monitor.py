# 事件监控API路由
"""
P2阶段功能：事件监控管理API + WebSocket
"""
import json
import uuid
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from typing import Optional, List
from pydantic import BaseModel, Field

from app.services.event_monitor_service import (
    alert_engine, websocket_manager,
    AlertRule, AlertSeverity, RuleOperator, RuleFieldType
)


router = APIRouter(prefix="/api/v1/monitor", tags=["Event Monitor"])


# ============ 请求/响应模型 ============

class RuleCreateRequest(BaseModel):
    """创建规则请求"""
    name: str = Field(..., description="规则名称")
    description: str = Field(default="", description="规则描述")
    severity: str = Field(default="medium", description="告警级别")
    field: str = Field(default="title", description="字段类型")
    operator: str = Field(default="contains", description="操作符")
    value: str = Field(default="", description="匹配值")
    cooldown_minutes: int = Field(default=30, description="冷却时间(分钟)")


class RuleUpdateRequest(BaseModel):
    """更新规则请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    severity: Optional[str] = None
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None
    cooldown_minutes: Optional[int] = None


class EventProcessRequest(BaseModel):
    """处理事件请求"""
    events: List[dict] = Field(..., description="事件列表")


# ============ 规则端点 ============

@router.get("/rules", summary="获取告警规则列表")
async def list_rules(
    enabled_only: bool = Query(default=False, description="仅启用的规则")
):
    """获取所有告警规则"""
    try:
        rules = alert_engine.list_rules(enabled_only=enabled_only)
        return {"success": True, "data": [r.to_dict() for r in rules]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取规则失败: {str(e)}")


@router.get("/rules/{rule_id}", summary="获取规则详情")
async def get_rule(rule_id: str):
    """获取单条规则"""
    rule = alert_engine.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")
    return {"success": True, "data": rule.to_dict()}


@router.post("/rules", summary="创建告警规则")
async def create_rule(request: RuleCreateRequest):
    """创建新的告警规则"""
    try:
        rule = AlertRule(
            id=f"rule_{uuid.uuid4().hex[:8]}",
            name=request.name,
            description=request.description,
            severity=AlertSeverity(request.severity),
            field=RuleFieldType(request.field),
            operator=RuleOperator(request.operator),
            value=request.value,
            cooldown_minutes=request.cooldown_minutes
        )
        created = alert_engine.add_rule(rule)
        return {"success": True, "data": created.to_dict()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建规则失败: {str(e)}")


@router.put("/rules/{rule_id}", summary="更新告警规则")
async def update_rule(rule_id: str, request: RuleUpdateRequest):
    """更新告警规则"""
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="没有需要更新的字段")
    
    rule = alert_engine.update_rule(rule_id, updates)
    if not rule:
        raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")
    return {"success": True, "data": rule.to_dict()}


@router.delete("/rules/{rule_id}", summary="删除告警规则")
async def delete_rule(rule_id: str):
    """删除告警规则"""
    success = alert_engine.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"规则不存在: {rule_id}")
    return {"success": True, "message": f"规则 {rule_id} 已删除"}


# ============ 告警端点 ============

@router.get("/alerts", summary="获取告警记录")
async def get_alerts(
    severity: Optional[str] = Query(default=None),
    acknowledged: Optional[bool] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0)
):
    """获取告警记录"""
    try:
        result = alert_engine.get_alerts(
            severity=severity,
            acknowledged=acknowledged,
            limit=limit,
            offset=offset
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取告警失败: {str(e)}")


@router.post("/alerts/{alert_id}/acknowledge", summary="确认告警")
async def acknowledge_alert(alert_id: str):
    """确认/标记已读告警"""
    success = alert_engine.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"告警不存在: {alert_id}")
    return {"success": True, "message": "告警已确认"}


@router.delete("/alerts", summary="清理告警记录")
async def clear_alerts(
    before: Optional[str] = Query(default=None, description="清理此时间之前的告警")
):
    """清理告警记录"""
    try:
        cleared = alert_engine.clear_alerts(before=before)
        return {"success": True, "data": {"cleared_count": cleared}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理告警失败: {str(e)}")


# ============ 事件处理端点 ============

@router.post("/events", summary="提交事件进行监控")
async def process_events(request: EventProcessRequest):
    """提交事件列表进行告警检测"""
    try:
        alerts = alert_engine.process_events_batch(request.events)
        
        # WebSocket广播触发的告警
        for alert in alerts:
            await websocket_manager.broadcast_alert(alert)
        
        return {
            "success": True,
            "data": {
                "processed": len(request.events),
                "alerts_triggered": len(alerts),
                "alerts": [a.to_dict() for a in alerts]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理事件失败: {str(e)}")


# ============ 统计端点 ============

@router.get("/statistics", summary="获取监控统计")
async def get_statistics():
    """获取事件监控的整体统计"""
    try:
        stats = alert_engine.get_statistics()
        stats["websocket_connections"] = websocket_manager.get_connection_count()
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


# ============ WebSocket 端点 ============

@router.websocket("/ws")
async def monitor_websocket(websocket: WebSocket):
    """WebSocket 实时监控连接"""
    client_id = f"client_{uuid.uuid4().hex[:8]}"
    await websocket.accept()
    await websocket_manager.connect(client_id, websocket)
    
    try:
        # 发送欢迎消息
        await websocket.send_text(json.dumps({
            "type": "connected",
            "client_id": client_id,
            "message": "事件监控 WebSocket 已连接"
        }, ensure_ascii=False))
        
        # 保持连接
        while True:
            data = await websocket.receive_text()
            # 处理客户端心跳
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
