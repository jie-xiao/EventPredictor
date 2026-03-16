# 知识图谱服务 - 实体关系存储与查询
"""
P2阶段：知识图谱 + 事件监控

知识图谱功能：
- 实体节点管理（国家、组织、人物、事件等）
- 关系边管理（敌对、盟友、制裁、合作等）
- 从事件中自动提取实体和关系
- 图查询（路径查询、影响力分析、关联发现）
"""
import os
import json
import asyncio
from typing import List, Optional, Dict, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EntityType(str, Enum):
    """实体类型"""
    COUNTRY = "country"          # 国家
    ORGANIZATION = "organization"  # 组织/机构
    COMPANY = "company"          # 公司
    PERSON = "person"            # 人物
    EVENT = "event"              # 事件
    LOCATION = "location"        # 地点
    CONCEPT = "concept"          # 概念/主题
    INDUSTRY = "industry"        # 行业
    ASSET = "asset"              # 资产（货币、商品等）


class RelationType(str, Enum):
    """关系类型"""
    # 政治关系
    ALLY = "ally"                # 盟友
    ENEMY = "enemy"              # 敌对
    SANCTION = "sanction"        # 制裁
    DIPLOMATIC = "diplomatic"    # 外交关系
    CONFLICT = "conflict"        # 冲突
    COOPERATION = "cooperation"  # 合作

    # 经济关系
    TRADE_PARTNER = "trade_partner"  # 贸易伙伴
    INVESTOR = "investor"        # 投资者
    SUPPLIER = "supplier"        # 供应商
    CUSTOMER = "customer"        # 客户
    COMPETITOR = "competitor"    # 竞争对手

    # 组织关系
    MEMBER = "member"            # 成员
    SUBSIDIARY = "subsidiary"    # 子公司
    PARENT = "parent"            # 母公司
    PARTNER = "partner"          # 合作伙伴

    # 事件关系
    CAUSED = "caused"            # 导致
    AFFECTED = "affected"        # 影响
    TRIGGERED = "triggered"      # 触发
    RESPONDED = "responded"      # 响应

    # 其他
    RELATED = "related"          # 相关
    OPPOSED = "opposed"          # 反对
    SUPPORTED = "supported"      # 支持


@dataclass
class Entity:
    """图实体节点"""
    id: str
    name: str
    type: EntityType
    aliases: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    source_events: List[str] = field(default_factory=list)  # 来源事件ID
    importance: float = 1.0  # 重要性权重

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "aliases": self.aliases,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_events": self.source_events,
            "importance": self.importance
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Entity":
        return cls(
            id=data["id"],
            name=data["name"],
            type=EntityType(data["type"]),
            aliases=data.get("aliases", []),
            properties=data.get("properties", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat() + "Z"),
            source_events=data.get("source_events", []),
            importance=data.get("importance", 1.0)
        )


@dataclass
class Relation:
    """图关系边"""
    id: str
    source_id: str
    target_id: str
    type: RelationType
    weight: float = 1.0  # 关系强度
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    source_event: Optional[str] = None  # 来源事件ID
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "weight": self.weight,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "source_event": self.source_event,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Relation":
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            type=RelationType(data["type"]),
            weight=data.get("weight", 1.0),
            properties=data.get("properties", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat() + "Z"),
            source_event=data.get("source_event"),
            valid_from=data.get("valid_from"),
            valid_to=data.get("valid_to")
        )


class KnowledgeGraphService:
    """知识图谱服务

    提供实体关系存储、查询和分析功能
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "knowledge_graph"
        )
        self.entities: Dict[str, Entity] = {}
        self.relations: Dict[str, Relation] = {}
        self.entity_index: Dict[str, Set[str]] = defaultdict(set)  # name -> entity_ids
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)  # entity_id -> relation_ids

        # 预定义的国家实体
        self._init_predefined_entities()

        # 加载已保存的数据
        self._load_data()

    def _init_predefined_entities(self):
        """初始化预定义实体"""
        predefined_countries = [
            ("cn", "中国", ["中华人民共和国", "PRC", "China"]),
            ("us", "美国", ["美利坚合众国", "USA", "United States"]),
            ("eu", "欧盟", ["欧洲联盟", "European Union"]),
            ("ru", "俄罗斯", ["俄国", "Russia"]),
            ("jp", "日本", ["Japan"]),
            ("kr", "韩国", ["南韩", "South Korea"]),
            ("kp", "朝鲜", ["北韩", "North Korea"]),
            ("in", "印度", ["India"]),
            ("gb", "英国", ["United Kingdom", "UK", "英国"]),
            ("de", "德国", ["Germany"]),
            ("fr", "法国", ["France"]),
            ("tw", "台湾", ["台湾地区", "Taiwan"]),
            ("ir", "伊朗", ["Iran"]),
            ("il", "以色列", ["Israel"]),
            ("ua", "乌克兰", ["Ukraine"]),
        ]

        for code, name, aliases in predefined_countries:
            entity = Entity(
                id=f"country_{code}",
                name=name,
                type=EntityType.COUNTRY,
                aliases=aliases,
                properties={"code": code.upper()},
                importance=2.0
            )
            self.entities[entity.id] = entity
            self.entity_index[name.lower()].add(entity.id)
            for alias in aliases:
                self.entity_index[alias.lower()].add(entity.id)

        # 预定义组织
        predefined_orgs = [
            ("nato", "北约", ["NATO", "北大西洋公约组织"]),
            ("un", "联合国", ["UN", "United Nations"]),
            ("who", "世卫组织", ["WHO", "World Health Organization"]),
            ("imf", "国际货币基金组织", ["IMF", "International Monetary Fund"]),
            ("wb", "世界银行", ["World Bank"]),
            ("wto", "世贸组织", ["WTO", "World Trade Organization"]),
            ("apec", "亚太经合组织", ["APEC"]),
            ("asean", "东盟", ["ASEAN", "东南亚国家联盟"]),
        ]

        for code, name, aliases in predefined_orgs:
            entity = Entity(
                id=f"org_{code}",
                name=name,
                type=EntityType.ORGANIZATION,
                aliases=aliases,
                properties={"code": code.upper()},
                importance=1.5
            )
            self.entities[entity.id] = entity
            self.entity_index[name.lower()].add(entity.id)
            for alias in aliases:
                self.entity_index[alias.lower()].add(entity.id)

    def _load_data(self):
        """从存储加载数据"""
        os.makedirs(self.storage_path, exist_ok=True)

        entities_file = os.path.join(self.storage_path, "entities.json")
        relations_file = os.path.join(self.storage_path, "relations.json")

        if os.path.exists(entities_file):
            try:
                with open(entities_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        entity = Entity.from_dict(item)
                        # 不覆盖预定义实体
                        if entity.id not in self.entities:
                            self.entities[entity.id] = entity
                            self.entity_index[entity.name.lower()].add(entity.id)
                            for alias in entity.aliases:
                                self.entity_index[alias.lower()].add(entity.id)
                logger.info(f"Loaded {len(self.entities)} entities from storage")
            except Exception as e:
                logger.error(f"Error loading entities: {e}")

        if os.path.exists(relations_file):
            try:
                with open(relations_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        relation = Relation.from_dict(item)
                        self.relations[relation.id] = relation
                        self.adjacency[relation.source_id].add(relation.id)
                        self.adjacency[relation.target_id].add(relation.id)
                logger.info(f"Loaded {len(self.relations)} relations from storage")
            except Exception as e:
                logger.error(f"Error loading relations: {e}")

    def _save_data(self):
        """保存数据到存储"""
        os.makedirs(self.storage_path, exist_ok=True)

        entities_file = os.path.join(self.storage_path, "entities.json")
        relations_file = os.path.join(self.storage_path, "relations.json")

        try:
            with open(entities_file, "w", encoding="utf-8") as f:
                json.dump([e.to_dict() for e in self.entities.values()], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving entities: {e}")

        try:
            with open(relations_file, "w", encoding="utf-8") as f:
                json.dump([r.to_dict() for r in self.relations.values()], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving relations: {e}")

    # ============ 实体管理 ============

    def add_entity(self, entity: Entity) -> Entity:
        """添加实体"""
        self.entities[entity.id] = entity
        self.entity_index[entity.name.lower()].add(entity.id)
        for alias in entity.aliases:
            self.entity_index[alias.lower()].add(entity.id)
        self._save_data()
        return entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """获取实体"""
        return self.entities.get(entity_id)

    def find_entity_by_name(self, name: str) -> Optional[Entity]:
        """根据名称查找实体"""
        name_lower = name.lower()
        if name_lower in self.entity_index:
            for entity_id in self.entity_index[name_lower]:
                return self.entities[entity_id]
        return None

    def search_entities(
        self,
        query: Optional[str] = None,
        entity_type: Optional[EntityType] = None,
        limit: int = 50
    ) -> List[Entity]:
        """搜索实体"""
        results = list(self.entities.values())

        if entity_type:
            results = [e for e in results if e.type == entity_type]

        if query:
            query_lower = query.lower()
            results = [
                e for e in results
                if query_lower in e.name.lower() or
                   any(query_lower in alias.lower() for alias in e.aliases)
            ]

        # 按重要性排序
        results.sort(key=lambda e: e.importance, reverse=True)
        return results[:limit]

    def update_entity(self, entity_id: str, properties: Dict[str, Any]) -> Optional[Entity]:
        """更新实体属性"""
        entity = self.entities.get(entity_id)
        if entity:
            entity.properties.update(properties)
            entity.updated_at = datetime.utcnow().isoformat() + "Z"
            self._save_data()
        return entity

    # ============ 关系管理 ============

    def add_relation(self, relation: Relation) -> Relation:
        """添加关系"""
        self.relations[relation.id] = relation
        self.adjacency[relation.source_id].add(relation.id)
        self.adjacency[relation.target_id].add(relation.id)
        self._save_data()
        return relation

    def get_relation(self, relation_id: str) -> Optional[Relation]:
        """获取关系"""
        return self.relations.get(relation_id)

    def get_entity_relations(
        self,
        entity_id: str,
        relation_type: Optional[RelationType] = None,
        direction: str = "both"  # "out", "in", "both"
    ) -> List[Relation]:
        """获取实体的所有关系"""
        if entity_id not in self.adjacency:
            return []

        relations = []
        for rel_id in self.adjacency[entity_id]:
            rel = self.relations.get(rel_id)
            if not rel:
                continue

            if relation_type and rel.type != relation_type:
                continue

            if direction == "out" and rel.source_id != entity_id:
                continue
            if direction == "in" and rel.target_id != entity_id:
                continue

            relations.append(rel)

        return relations

    def get_relations_between(self, entity_id1: str, entity_id2: str) -> List[Relation]:
        """获取两个实体之间的关系"""
        relations = []
        for rel_id in self.adjacency.get(entity_id1, set()):
            rel = self.relations.get(rel_id)
            if rel and (
                (rel.source_id == entity_id1 and rel.target_id == entity_id2) or
                (rel.source_id == entity_id2 and rel.target_id == entity_id1)
            ):
                relations.append(rel)
        return relations

    # ============ 事件提取 ============

    async def extract_from_event(self, event: Dict[str, Any]) -> Tuple[List[Entity], List[Relation]]:
        """从事件中提取实体和关系"""
        entities = []
        relations = []

        # 从事件实体列表提取
        event_entities = event.get("entities", [])
        event_id = event.get("id", "")

        for entity_name in event_entities:
            # 查找或创建实体
            entity = self.find_entity_by_name(entity_name)
            if not entity:
                # 根据名称推断类型
                entity_type = self._infer_entity_type(entity_name)
                entity = Entity(
                    id=f"{entity_type.value}_{entity_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    name=entity_name,
                    type=entity_type,
                    source_events=[event_id]
                )
                self.add_entity(entity)
            else:
                if event_id not in entity.source_events:
                    entity.source_events.append(event_id)
                    entity.updated_at = datetime.utcnow().isoformat() + "Z"

            entities.append(entity)

        # 根据事件类别推断关系
        category = event.get("category", "")
        severity = event.get("severity", 3)

        if len(entities) >= 2:
            # 根据类别确定关系类型
            rel_type = self._infer_relation_type(category, event.get("description", ""))

            if rel_type:
                # 为主要实体对创建关系
                main_entities = entities[:2]  # 取前两个实体
                relation = Relation(
                    id=f"rel_{main_entities[0].id}_{main_entities[1].id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    source_id=main_entities[0].id,
                    target_id=main_entities[1].id,
                    type=rel_type,
                    weight=severity / 5.0,
                    source_event=event_id,
                    properties={
                        "event_category": category,
                        "event_title": event.get("title", "")
                    }
                )
                self.add_relation(relation)
                relations.append(relation)

        return entities, relations

    def _infer_entity_type(self, name: str) -> EntityType:
        """根据名称推断实体类型"""
        # 国家关键词
        country_keywords = ["中国", "美国", "俄国", "日本", "韩国", "朝鲜", "印度", "英国", "法国", "德国",
                          "China", "USA", "Russia", "Japan", "Korea", "India", "UK", "France", "Germany"]

        for kw in country_keywords:
            if kw in name:
                return EntityType.COUNTRY

        # 组织关键词
        org_keywords = ["组织", "联盟", "公约", "银行", "基金", "Organization", "Union", "Bank", "NATO", "UN"]

        for kw in org_keywords:
            if kw in name:
                return EntityType.ORGANIZATION

        # 公司关键词
        company_keywords = ["公司", "集团", "企业", "Inc", "Corp", "Company", "Ltd"]

        for kw in company_keywords:
            if kw in name:
                return EntityType.COMPANY

        return EntityType.CONCEPT

    def _infer_relation_type(self, category: str, description: str) -> Optional[RelationType]:
        """根据事件类别和描述推断关系类型"""
        category_rel_map = {
            "military": RelationType.CONFLICT,
            "conflict": RelationType.CONFLICT,
            "trade": RelationType.TRADE_PARTNER,
            "economy": RelationType.RELATED,
            "politics": RelationType.DIPLOMATIC,
            "sanction": RelationType.SANCTION,
        }

        # 检查描述中的关键词
        description_lower = description.lower()

        conflict_keywords = ["冲突", "战争", "攻击", "打击", "conflict", "war", "attack", "strike"]
        for kw in conflict_keywords:
            if kw in description_lower:
                return RelationType.CONFLICT

        sanction_keywords = ["制裁", "禁令", "限制", "sanction", "ban", "restrict"]
        for kw in sanction_keywords:
            if kw in description_lower:
                return RelationType.SANCTION

        cooperation_keywords = ["合作", "协议", "条约", "cooperation", "agreement", "treaty"]
        for kw in cooperation_keywords:
            if kw in description_lower:
                return RelationType.COOPERATION

        return category_rel_map.get(category, RelationType.RELATED)

    # ============ 图查询 ============

    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 4
    ) -> List[List[str]]:
        """查找两个实体之间的路径（BFS）"""
        if start_id not in self.entities or end_id not in self.entities:
            return []

        if start_id == end_id:
            return [[start_id]]

        paths = []
        queue = [(start_id, [start_id])]
        visited = {start_id}

        while queue:
            current, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            for rel_id in self.adjacency.get(current, set()):
                rel = self.relations.get(rel_id)
                if not rel:
                    continue

                # 获取邻居节点
                neighbor = rel.target_id if rel.source_id == current else rel.source_id

                if neighbor == end_id:
                    paths.append(path + [neighbor])
                    continue

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return paths

    def get_neighborhood(
        self,
        entity_id: str,
        depth: int = 2,
        relation_types: Optional[List[RelationType]] = None
    ) -> Dict[str, Any]:
        """获取实体的邻域子图"""
        if entity_id not in self.entities:
            return {"entities": [], "relations": []}

        visited_entities = {entity_id}
        visited_relations = set()
        current_level = {entity_id}

        for _ in range(depth):
            next_level = set()
            for eid in current_level:
                for rel_id in self.adjacency.get(eid, set()):
                    if rel_id in visited_relations:
                        continue

                    rel = self.relations.get(rel_id)
                    if not rel:
                        continue

                    if relation_types and rel.type not in relation_types:
                        continue

                    visited_relations.add(rel_id)

                    # 添加邻居节点
                    if rel.source_id not in visited_entities:
                        visited_entities.add(rel.source_id)
                        next_level.add(rel.source_id)
                    if rel.target_id not in visited_entities:
                        visited_entities.add(rel.target_id)
                        next_level.add(rel.target_id)

            current_level = next_level
            if not current_level:
                break

        return {
            "entities": [self.entities[eid].to_dict() for eid in visited_entities],
            "relations": [self.relations[rid].to_dict() for rid in visited_relations]
        }

    def calculate_influence(self, entity_id: str) -> Dict[str, Any]:
        """计算实体的影响力"""
        if entity_id not in self.entities:
            return {"entity_id": entity_id, "influence_score": 0, "connections": 0}

        relations = self.get_entity_relations(entity_id)
        entity = self.entities[entity_id]

        # 计算连接数
        direct_connections = len(relations)

        # 计算二度连接
        second_degree = set()
        for rel in relations:
            neighbor_id = rel.target_id if rel.source_id == entity_id else rel.source_id
            for n_rel in self.get_entity_relations(neighbor_id):
                n_neighbor = n_rel.target_id if n_rel.source_id == neighbor_id else n_rel.source_id
                if n_neighbor != entity_id:
                    second_degree.add(n_neighbor)

        # 关系强度加权
        total_weight = sum(r.weight for r in relations)

        # 影响力分数
        influence_score = (
            entity.importance * 10 +
            direct_connections * 2 +
            len(second_degree) * 0.5 +
            total_weight
        )

        return {
            "entity_id": entity_id,
            "entity_name": entity.name,
            "influence_score": round(influence_score, 2),
            "direct_connections": direct_connections,
            "second_degree_connections": len(second_degree),
            "total_relation_weight": round(total_weight, 2)
        }

    def find_central_entities(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """查找图中的中心实体"""
        influence_scores = []
        for entity_id in self.entities:
            influence = self.calculate_influence(entity_id)
            influence_scores.append(influence)

        influence_scores.sort(key=lambda x: x["influence_score"], reverse=True)
        return influence_scores[:top_n]

    def get_statistics(self) -> Dict[str, Any]:
        """获取知识图谱统计信息"""
        type_counts = defaultdict(int)
        for entity in self.entities.values():
            type_counts[entity.type.value] += 1

        rel_type_counts = defaultdict(int)
        for rel in self.relations.values():
            rel_type_counts[rel.type.value] += 1

        return {
            "total_entities": len(self.entities),
            "total_relations": len(self.relations),
            "entity_types": dict(type_counts),
            "relation_types": dict(rel_type_counts),
            "avg_connections": len(self.relations) * 2 / len(self.entities) if self.entities else 0
        }


# 全局服务实例
knowledge_graph_service = KnowledgeGraphService()
