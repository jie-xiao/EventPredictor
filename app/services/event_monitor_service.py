# 事件监控服务
"""
P2阶段功能：事件监控 + 告警引擎

核心功能：
1. 事件监控 - 定期检查新事件
2. 告警规则引擎 - 灵活的告警规则配置
3. WebSocket 实时推送
"""
import asyncio
import json
import re
import time
import logging
import uuid
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


# ============ 告警规则模型 ============

class AlertSeverity(str, Enum):
    """告警级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RuleOperator(str, Enum):
    """规则操作符"""
    CONTAINS = "contains"          # 包含
    NOT_CONTAINS = "not_contains"  # 不包含
    MATCHES = "matches"            # 正则匹配
    EXACT = "exact"                # 精确匹配
    GREATER_THAN = "gt"            # 大于
    LESS_THAN = "lt"               # 小于
    EQUALS = "eq"                  # 等于
    CATEGORY = "category"          # 类别匹配


class RuleFieldType(str, Enum):
    """规则字段类型"""
    TITLE = "title"
    DESCRIPTION = "description"
    CATEGORY = "category"
    SEVERITY = "severity"
    SOURCE = "source"
    COUNTRY = "country"


@dataclass
class AlertRule:
    """告警规则"""
    id: str
    name: str
    description: str = ""
    enabled: bool = True
    severity: AlertSeverity = AlertSeverity.MEDIUM
    field: RuleFieldType = RuleFieldType.TITLE
    operator: RuleOperator = RuleOperator.CONTAINS
    value: Any = ""
    # 高级：组合规则
    group_id: Optional[str] = None  # 规则组
    cooldown_minutes: int = 30      # 冷却时间（分钟）
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    last_triggered: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "severity": self.severity.value,
            "field": self.field.value,
            "operator": self.operator.value,
            "value": self.value,
            "group_id": self.group_id,
            "cooldown_minutes": self.cooldown_minutes,
            "created_at": self.created_at,
            "last_triggered": self.last_triggered
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertRule":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
            severity=AlertSeverity(data.get("severity", "medium")),
            field=RuleFieldType(data.get("field", "title")),
            operator=RuleOperator(data.get("operator", "contains")),
            value=data.get("value", ""),
            group_id=data.get("group_id"),
            cooldown_minutes=data.get("cooldown_minutes", 30),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            last_triggered=data.get("last_triggered")
        )


@dataclass
class Alert:
    """告警记录"""
    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    event_data: Dict[str, Any]
    message: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "event_data": self.event_data,
            "message": self.message,
            "created_at": self.created_at,
            "acknowledged": self.acknowledged
        }


@dataclass
class MonitoredEvent:
    """被监控的事件"""
    id: str
    title: str
    description: str = ""
    category: str = ""
    severity: int = 0
    source: str = ""
    country: str = ""
    timestamp: str = ""
    processed: bool = False
    matched_rules: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "source": self.source,
            "country": self.country,
            "timestamp": self.timestamp,
            "processed": self.processed,
            "matched_rules": self.matched_rules,
            "created_at": self.created_at
        }


# ============ 告警引擎 ============

class AlertEngine:
    """告警规则引擎"""

    def __init__(self, storage_path: str = "data/event_monitor"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.rules_file = self.storage_path / "rules.json"
        self.alerts_file = self.storage_path / "alerts.json"
        self.events_file = self.storage_path / "events.json"

        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.monitored_events: Dict[str, MonitoredEvent] = {}
        self._last_check: Optional[str] = None

        self._load_rules()
        self._load_alerts()
        self._load_events()

        # 初始化默认规则
        if not self.rules:
            self._init_default_rules()

    def _load_rules(self):
        """加载规则"""
        try:
            if self.rules_file.exists():
                data = json.loads(self.rules_file.read_text(encoding="utf-8"))
                self.rules = {r["id"]: AlertRule.from_dict(r) for r in data}
                logger.info(f"[监控] 加载了 {len(self.rules)} 条规则")
        except Exception as e:
            logger.error(f"[监控] 加载规则失败: {e}")

    def _save_rules(self):
        """保存规则"""
        try:
            data = [r.to_dict() for r in self.rules.values()]
            self.rules_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"[监控] 保存规则失败: {e}")

    def _load_alerts(self):
        """加载告警记录"""
        try:
            if self.alerts_file.exists():
                data = json.loads(self.alerts_file.read_text(encoding="utf-8"))
                self.alerts = [Alert(**a) for a in data]
                logger.info(f"[监控] 加载了 {len(self.alerts)} 条告警记录")
        except Exception as e:
            logger.error(f"[监控] 加载告警失败: {e}")

    def _save_alerts(self):
        """保存告警记录"""
        try:
            data = [a.to_dict() for a in self.alerts]
            self.alerts_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"[监控] 保存告警失败: {e}")

    def _load_events(self):
        """加载监控事件"""
        try:
            if self.events_file.exists():
                data = json.loads(self.events_file.read_text(encoding="utf-8"))
                self.monitored_events = {e["id"]: MonitoredEvent(**e) for e in data}
        except Exception as e:
            logger.error(f"[监控] 加载事件失败: {e}")

    def _save_events(self):
        """保存监控事件"""
        try:
            data = [e.to_dict() for e in self.monitored_events.values()]
            self.events_file.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"[监控] 保存事件失败: {e}")

    def _init_default_rules(self):
        """初始化默认告警规则"""
        default_rules = [
            AlertRule(
                id="rule_war", name="战争/军事冲突", description="检测战争、军事行动相关事件",
                severity=AlertSeverity.CRITICAL, field=RuleFieldType.TITLE,
                operator=RuleOperator.CONTAINS, value="war"
            ),
            AlertRule(
                id="rule_nuclear", name="核武器", description="检测核武器相关事件",
                severity=AlertSeverity.CRITICAL, field=RuleFieldType.TITLE,
                operator=RuleOperator.CONTAINS, value="nuclear"
            ),
            AlertRule(
                id="rule_attack", name="袭击/攻击", description="检测袭击事件",
                severity=AlertSeverity.HIGH, field=RuleFieldType.TITLE,
                operator=RuleOperator.CONTAINS, value="attack"
            ),
            AlertRule(
                id="rule_oil", name="石油/油价", description="检测石油相关经济事件",
                severity=AlertSeverity.HIGH, field=RuleFieldType.TITLE,
                operator=RuleOperator.CONTAINS, value="oil"
            ),
            AlertRule(
                id="rule_sanctions", name="制裁", description="检测制裁相关事件",
                severity=AlertSeverity.MEDIUM, field=RuleFieldType.TITLE,
                operator=RuleOperator.CONTAINS, value="sanction"
            ),
            AlertRule(
                id="rule_military_exercise", name="军事演习", description="检测军事演习",
                severity=AlertSeverity.MEDIUM, field=RuleFieldType.TITLE,
                operator=RuleOperator.MATCHES, value="(?i)military exercise|troops deploy"
            ),
            AlertRule(
                id="rule_iran", name="伊朗相关", description="检测伊朗相关高关注度事件",
                severity=AlertSeverity.HIGH, field=RuleFieldType.DESCRIPTION,
                operator=RuleOperator.CONTAINS, value="Iran"
            ),
            AlertRule(
                id="rule_high_severity", name="高严重性事件", description="严重性等级>=4的事件",
                severity=AlertSeverity.HIGH, field=RuleFieldType.SEVERITY,
                operator=RuleOperator.GREATER_THAN, value=3
            ),
        ]
        for rule in default_rules:
            self.rules[rule.id] = rule
        self._save_rules()
        logger.info(f"[监控] 初始化 {len(default_rules)} 条默认规则")

    def _evaluate_rule(self, rule: AlertRule, event: MonitoredEvent) -> bool:
        """评估单条规则"""
        if not rule.enabled:
            return False

        # 冷却检查
        if rule.last_triggered:
            last = datetime.fromisoformat(rule.last_triggered.replace("Z", "+00:00"))
            cooldown = timedelta(minutes=rule.cooldown_minutes)
            if datetime.utcnow() + timedelta(hours=0) - last.replace(tzinfo=None) < cooldown:
                return False

        # 获取字段值
        field_map = {
            RuleFieldType.TITLE: event.title,
            RuleFieldType.DESCRIPTION: event.description,
            RuleFieldType.CATEGORY: event.category,
            RuleFieldType.SEVERITY: event.severity,
            RuleFieldType.SOURCE: event.source,
            RuleFieldType.COUNTRY: event.country,
        }
        field_value = field_map.get(rule.field, "")
        target_value = str(rule.value).lower()
        field_str = str(field_value).lower()

        # 操作符匹配
        try:
            if rule.operator == RuleOperator.CONTAINS:
                return target_value in field_str
            elif rule.operator == RuleOperator.NOT_CONTAINS:
                return target_value not in field_str
            elif rule.operator == RuleOperator.MATCHES:
                return bool(re.search(target_value, field_str, re.IGNORECASE))
            elif rule.operator == RuleOperator.EXACT:
                return target_value == field_str
            elif rule.operator == RuleOperator.GREATER_THAN:
                return float(field_value) > float(rule.value)
            elif rule.operator == RuleOperator.LESS_THAN:
                return float(field_value) < float(rule.value)
            elif rule.operator == RuleOperator.EQUALS:
                return str(field_value) == str(rule.value)
            elif rule.operator == RuleOperator.CATEGORY:
                return target_value in field_str
        except (ValueError, TypeError):
            return False

        return False

    def process_event(self, event_data: Dict[str, Any]) -> List[Alert]:
        """处理单个事件，返回触发的告警列表"""
        event_id = event_data.get("id", str(uuid.uuid4()))
        
        # 跳过已处理的事件
        if event_id in self.monitored_events and self.monitored_events[event_id].processed:
            return []

        monitored_event = MonitoredEvent(
            id=event_id,
            title=event_data.get("title", ""),
            description=event_data.get("description", ""),
            category=event_data.get("category", ""),
            severity=event_data.get("severity", 0),
            source=event_data.get("source", ""),
            country=event_data.get("country", event_data.get("location", {}).get("country", "")),
            timestamp=event_data.get("timestamp", datetime.utcnow().isoformat() + "Z")
        )

        triggered_alerts = []
        for rule in self.rules.values():
            if self._evaluate_rule(rule, monitored_event):
                alert = Alert(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    event_data=monitored_event.to_dict(),
                    message=f"[{rule.severity.value}] {rule.name}: {monitored_event.title}"
                )
                triggered_alerts.append(alert)
                self.alerts.insert(0, alert)  # 最新的在前
                monitored_event.matched_rules.append(rule.id)

                # 更新规则最后触发时间
                rule.last_triggered = datetime.utcnow().isoformat() + "Z"

        monitored_event.processed = True
        self.monitored_events[event_id] = monitored_event

        # 限制告警和事件数量
        self.alerts = self.alerts[:1000]
        if len(self.monitored_events) > 5000:
            oldest = sorted(
                self.monitored_events.items(),
                key=lambda x: x[1].created_at
            )[:1000]
            for eid, _ in oldest:
                del self.monitored_events[eid]

        self._save_alerts()
        self._save_events()
        self._save_rules()

        return triggered_alerts

    def process_events_batch(self, events: List[Dict[str, Any]]) -> List[Alert]:
        """批量处理事件"""
        all_alerts = []
        for event in events:
            alerts = self.process_event(event)
            all_alerts.extend(alerts)
        return all_alerts

    # ============ 规则 CRUD ============

    def add_rule(self, rule: AlertRule) -> AlertRule:
        """添加规则"""
        self.rules[rule.id] = rule
        self._save_rules()
        return rule

    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> Optional[AlertRule]:
        """更新规则"""
        if rule_id not in self.rules:
            return None
        rule = self.rules[rule_id]
        for key, value in updates.items():
            if hasattr(rule, key):
                if key == "severity":
                    setattr(rule, key, AlertSeverity(value))
                elif key == "field":
                    setattr(rule, key, RuleFieldType(value))
                elif key == "operator":
                    setattr(rule, key, RuleOperator(value))
                else:
                    setattr(rule, key, value)
        self._save_rules()
        return rule

    def delete_rule(self, rule_id: str) -> bool:
        """删除规则"""
        if rule_id not in self.rules:
            return False
        del self.rules[rule_id]
        self._save_rules()
        return True

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """获取规则"""
        return self.rules.get(rule_id)

    def list_rules(self, enabled_only: bool = False) -> List[AlertRule]:
        """列出所有规则"""
        rules = list(self.rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return rules

    # ============ 告警查询 ============

    def get_alerts(
        self,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """获取告警记录"""
        filtered = self.alerts
        if severity:
            filtered = [a for a in filtered if a.severity.value == severity]
        if acknowledged is not None:
            filtered = [a for a in filtered if a.acknowledged == acknowledged]

        total = len(filtered)
        paginated = filtered[offset:offset + limit]
        return {
            "alerts": [a.to_dict() for a in paginated],
            "total": total,
            "unacknowledged": sum(1 for a in self.alerts if not a.acknowledged)
        }

    def acknowledge_alert(self, alert_id: str) -> bool:
        """确认告警"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self._save_alerts()
                return True
        return False

    def clear_alerts(self, before: Optional[str] = None) -> int:
        """清理告警"""
        if before:
            cutoff = datetime.fromisoformat(before.replace("Z", "+00:00"))
            original = len(self.alerts)
            self.alerts = [
                a for a in self.alerts
                if datetime.fromisoformat(a.created_at.replace("Z", "+00:00")) >= cutoff
            ]
        else:
            original = len(self.alerts)
            self.alerts = []
        self._save_alerts()
        return original - len(self.alerts)

    def get_statistics(self) -> Dict[str, Any]:
        """获取监控统计"""
        severity_counts = defaultdict(int)
        rule_trigger_counts = defaultdict(int)
        for alert in self.alerts:
            severity_counts[alert.severity.value] += 1
            rule_trigger_counts[alert.rule_id] += 1

        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
            "total_alerts": len(self.alerts),
            "unacknowledged_alerts": sum(1 for a in self.alerts if not a.acknowledged),
            "total_events_processed": len(self.monitored_events),
            "severity_distribution": dict(severity_counts),
            "top_triggered_rules": dict(
                sorted(rule_trigger_counts.items(), key=lambda x: -x[1])[:10]
            )
        }


# ============ WebSocket 管理 ============

class WebSocketManager:
    """WebSocket 连接管理"""

    def __init__(self):
        self.connections: Dict[str, Any] = {}  # client_id -> websocket

    async def connect(self, client_id: str, websocket):
        """接受新连接"""
        self.connections[client_id] = websocket
        logger.info(f"[WebSocket] 客户端 {client_id} 已连接，当前 {len(self.connections)} 个连接")

    def disconnect(self, client_id: str):
        """断开连接"""
        self.connections.pop(client_id, None)
        logger.info(f"[WebSocket] 客户端 {client_id} 已断开，当前 {len(self.connections)} 个连接")

    async def broadcast_alert(self, alert: Alert):
        """广播告警到所有连接"""
        message = json.dumps({
            "type": "alert",
            "data": alert.to_dict()
        }, ensure_ascii=False)
        
        disconnected = []
        for client_id, ws in self.connections.items():
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)

    async def broadcast_event(self, event_data: Dict[str, Any]):
        """广播事件更新"""
        message = json.dumps({
            "type": "event",
            "data": event_data
        }, ensure_ascii=False)
        
        disconnected = []
        for client_id, ws in self.connections.items():
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)

    def get_connection_count(self) -> int:
        """获取当前连接数"""
        return len(self.connections)


# ============ 全局实例 ============

alert_engine = AlertEngine()
websocket_manager = WebSocketManager()
