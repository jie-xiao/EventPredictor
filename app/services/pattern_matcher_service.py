# 历史模式匹配服务
"""
P0阶段功能：历史模式匹配
- 基于事件特征进行相似度计算
- 查找历史相似事件及其预测结果
- 支持关键词匹配和语义相似度
"""
import json
import re
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from collections import Counter


class PatternMatcherService:
    """历史模式匹配服务 - 查找相似历史事件"""

    def __init__(self, history_path: str = "data/prediction_history"):
        self.history_path = Path(history_path)
        self.history_file = self.history_path / "history.json"
        self._history_cache: Dict[str, Any] = {}
        self._pattern_index: Dict[str, List[str]] = {}  # 模式索引
        self._load_history()

    def _load_history(self):
        """加载历史数据"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self._history_cache = json.load(f)
                # 构建模式索引
                self._build_pattern_index()
            except Exception as e:
                print(f"加载历史记录失败: {e}")
                self._history_cache = {"predictions": [], "by_event": {}}
        else:
            self._history_cache = {"predictions": [], "by_event": {}}

    def _build_pattern_index(self):
        """构建模式索引，用于快速匹配"""
        self._pattern_index = {}

        for pred in self._history_cache.get("predictions", []):
            # 提取事件特征
            features = self._extract_features(pred)
            event_id = pred.get("id", "")

            # 为每个特征关键词建立索引
            for keyword in features.get("keywords", []):
                key = keyword.lower()
                if key not in self._pattern_index:
                    self._pattern_index[key] = []
                self._pattern_index[key].append(event_id)

            # 按类别索引
            category = pred.get("category", "Other").lower()
            cat_key = f"cat:{category}"
            if cat_key not in self._pattern_index:
                self._pattern_index[cat_key] = []
            self._pattern_index[cat_key].append(event_id)

    def _extract_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """提取事件特征"""
        title = event.get("event_title", event.get("title", ""))
        description = event.get("event_description", event.get("description", ""))
        category = event.get("category", "Other")

        # 合并文本
        text = f"{title} {description}"

        # 提取关键词
        keywords = self._extract_keywords(text)

        # 提取实体
        entities = self._extract_entities(text)

        # 提取数值
        numbers = self._extract_numbers(text)

        # 计算文本哈希（用于精确匹配）
        text_hash = hashlib.md5(f"{title}|{description}".encode()).hexdigest()[:16]

        return {
            "keywords": keywords,
            "entities": entities,
            "numbers": numbers,
            "category": category,
            "text_hash": text_hash,
            "title_length": len(title),
            "desc_length": len(description)
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 预定义的关键词模式（按领域分类）
        keyword_patterns = {
            # 军事类
            "military": ["军事", "军队", "航母", "导弹", "核武器", "战争", "冲突", "演习",
                        "military", "war", "missile", "nuclear", "carrier", "troops"],
            # 政治类
            "political": ["政府", "政策", "选举", "制裁", "外交", "领导人", "会议",
                         "government", "election", "sanction", "diplomatic", "policy"],
            # 经济类
            "economic": ["利率", "通胀", "GDP", "经济", "贸易", "关税", "股市",
                        "rate", "inflation", "economy", "trade", "tariff", "stock"],
            # 科技类
            "technology": ["科技", "AI", "芯片", "5G", "互联网", "软件", "数据",
                          "technology", "tech", "ai", "chip", "software", "data"],
            # 灾害类
            "disaster": ["地震", "洪水", "台风", "疫情", "火灾", "灾害",
                        "earthquake", "flood", "typhoon", "pandemic", "disaster"],
            # 能源类
            "energy": ["石油", "天然气", "能源", "原油", "OPEC", "油价",
                      "oil", "gas", "energy", "crude", "opec", "petroleum"],
            # 金融市场
            "financial": ["美联储", "央行", "加息", "降息", "量化宽松", "货币政策",
                         "fed", "central bank", "rate hike", "monetary policy"]
        }

        found_keywords = []
        text_lower = text.lower()

        for category, patterns in keyword_patterns.items():
            for pattern in patterns:
                if pattern.lower() in text_lower:
                    found_keywords.append(pattern)

        # 提取高频词
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}|[a-zA-Z]{3,}', text)
        word_freq = Counter(words)

        # 添加高频词（过滤停用词）
        stopwords = {"的", "是", "在", "有", "和", "了", "对", "这", "那", "为"}
        for word, freq in word_freq.most_common(10):
            if word.lower() not in stopwords and freq >= 2:
                found_keywords.append(word)

        return list(set(found_keywords))[:20]

    def _extract_entities(self, text: str) -> List[str]:
        """提取命名实体（国家、组织等）"""
        entities = []

        # 预定义实体
        entity_dict = {
            # 国家
            "countries": ["中国", "美国", "俄罗斯", "日本", "韩国", "朝鲜", "欧盟", "英国",
                         "China", "US", "USA", "Russia", "Japan", "Korea", "EU", "UK"],
            # 组织
            "organizations": ["联合国", "北约", "WTO", "IMF", "世界银行", "OPEC",
                             "UN", "NATO", "WTO", "World Bank"],
            # 公司
            "companies": ["苹果", "微软", "谷歌", "腾讯", "阿里巴巴", "华为",
                         "Apple", "Microsoft", "Google", "Tencent", "Alibaba", "Huawei"]
        }

        text_lower = text.lower()
        for entity_type, entity_list in entity_dict.items():
            for entity in entity_list:
                if entity.lower() in text_lower:
                    entities.append(entity)

        return entities

    def _extract_numbers(self, text: str) -> List[str]:
        """提取关键数值"""
        # 提取百分比
        percentages = re.findall(r'\d+(?:\.\d+)?%', text)

        # 提取金额
        amounts = re.findall(r'\d+(?:\.\d+)?(?:亿|万|million|billion)', text, re.IGNORECASE)

        # 提取基点
        basis_points = re.findall(r'\d+(?:\.\d+)?\s*(?:bp|基点)', text, re.IGNORECASE)

        return percentages + amounts + basis_points

    def calculate_similarity(
        self,
        event1: Dict[str, Any],
        event2: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """
        计算两个事件的相似度

        Returns:
            (总相似度, 各维度相似度详情)
        """
        features1 = self._extract_features(event1)
        features2 = self._extract_features(event2)

        scores = {}

        # 1. 关键词相似度 (权重 0.3)
        kw1 = set(features1.get("keywords", []))
        kw2 = set(features2.get("keywords", []))
        if kw1 or kw2:
            kw_score = len(kw1 & kw2) / max(len(kw1 | kw2), 1)
        else:
            kw_score = 0
        scores["keyword_similarity"] = kw_score

        # 2. 类别相似度 (权重 0.2)
        cat_score = 1.0 if features1.get("category") == features2.get("category") else 0
        scores["category_similarity"] = cat_score

        # 3. 实体重叠度 (权重 0.25)
        ent1 = set(features1.get("entities", []))
        ent2 = set(features2.get("entities", []))
        if ent1 or ent2:
            ent_score = len(ent1 & ent2) / max(len(ent1 | ent2), 1)
        else:
            ent_score = 0
        scores["entity_similarity"] = ent_score

        # 4. 数值匹配 (权重 0.15)
        num1 = set(features1.get("numbers", []))
        num2 = set(features2.get("numbers", []))
        if num1 or num2:
            num_score = len(num1 & num2) / max(len(num1 | num2), 1)
        else:
            num_score = 0
        scores["number_similarity"] = num_score

        # 5. 精确哈希匹配 (权重 0.1)
        hash_score = 1.0 if features1.get("text_hash") == features2.get("text_hash") else 0
        scores["exact_match"] = hash_score

        # 计算加权总分
        weights = {
            "keyword_similarity": 0.3,
            "category_similarity": 0.2,
            "entity_similarity": 0.25,
            "number_similarity": 0.15,
            "exact_match": 0.1
        }

        total_score = sum(scores[k] * weights[k] for k in weights)

        return total_score, scores

    async def find_similar_events(
        self,
        event: Dict[str, Any],
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        查找相似的历史事件

        Args:
            event: 当前事件
            top_k: 返回最相似的K个结果
            min_similarity: 最小相似度阈值

        Returns:
            相似事件列表，每个包含事件信息和相似度分数
        """
        # 提取当前事件特征
        features = self._extract_features(event)

        # 候选事件ID集合
        candidate_ids = set()

        # 通过关键词索引快速筛选候选
        for keyword in features.get("keywords", []):
            key = keyword.lower()
            if key in self._pattern_index:
                candidate_ids.update(self._pattern_index[key])

        # 添加同类别的候选
        category = features.get("category", "").lower()
        cat_key = f"cat:{category}"
        if cat_key in self._pattern_index:
            candidate_ids.update(self._pattern_index[cat_key])

        # 如果没有候选，使用所有历史记录
        if not candidate_ids:
            candidate_ids = {p.get("id") for p in self._history_cache.get("predictions", [])}

        # 计算相似度并排序
        similarities = []

        for pred in self._history_cache.get("predictions", []):
            if pred.get("id") not in candidate_ids:
                continue

            # 构建历史事件对象
            hist_event = {
                "title": pred.get("event_title", ""),
                "description": pred.get("event_description", ""),
                "category": pred.get("category", "Other")
            }

            score, details = self.calculate_similarity(event, hist_event)

            if score >= min_similarity:
                similarities.append({
                    "history_id": pred.get("id"),
                    "event_id": pred.get("event_id"),
                    "title": pred.get("event_title"),
                    "category": pred.get("category"),
                    "similarity_score": round(score, 3),
                    "similarity_details": details,
                    "prediction": pred.get("prediction", {}),
                    "overall_confidence": pred.get("overall_confidence"),
                    "created_at": pred.get("created_at")
                })

        # 按相似度排序
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)

        return similarities[:top_k]

    async def find_similar_patterns_by_keywords(
        self,
        keywords: List[str],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        基于关键词查找相似模式

        Args:
            keywords: 关键词列表
            top_k: 返回数量

        Returns:
            匹配的历史记录
        """
        results = []
        seen_ids = set()

        for keyword in keywords:
            key = keyword.lower()
            if key in self._pattern_index:
                for pred_id in self._pattern_index[key]:
                    if pred_id in seen_ids:
                        continue
                    seen_ids.add(pred_id)

                    # 查找完整记录
                    for pred in self._history_cache.get("predictions", []):
                        if pred.get("id") == pred_id:
                            results.append({
                                "history_id": pred.get("id"),
                                "title": pred.get("event_title"),
                                "category": pred.get("category"),
                                "matched_keyword": keyword,
                                "prediction": pred.get("prediction")
                            })
                            break

        return results[:top_k]

    async def get_pattern_statistics(self) -> Dict[str, Any]:
        """获取模式匹配统计信息"""
        predictions = self._history_cache.get("predictions", [])

        # 类别分布
        category_dist = {}
        for p in predictions:
            cat = p.get("category", "Other")
            category_dist[cat] = category_dist.get(cat, 0) + 1

        # 高频关键词
        keyword_freq = Counter()
        for pred in predictions:
            features = self._extract_features(pred)
            for kw in features.get("keywords", []):
                keyword_freq[kw] += 1

        # 趋势分布
        trend_dist = {}
        for p in predictions:
            trend = p.get("prediction", {}).get("trend", "N/A")
            trend_dist[trend] = trend_dist.get(trend, 0) + 1

        return {
            "total_predictions": len(predictions),
            "category_distribution": category_dist,
            "top_keywords": keyword_freq.most_common(20),
            "trend_distribution": trend_dist,
            "pattern_index_size": len(self._pattern_index)
        }

    async def learn_from_new_prediction(self, prediction_record: Dict[str, Any]):
        """
        从新的预测记录中学习，更新模式索引

        Args:
            prediction_record: 新的预测记录
        """
        # 提取特征
        features = self._extract_features(prediction_record)
        event_id = prediction_record.get("id", "")

        # 更新内存中的历史缓存
        if "predictions" not in self._history_cache:
            self._history_cache["predictions"] = []
        self._history_cache["predictions"].append(prediction_record)

        # 更新索引
        for keyword in features.get("keywords", []):
            key = keyword.lower()
            if key not in self._pattern_index:
                self._pattern_index[key] = []
            if event_id not in self._pattern_index[key]:
                self._pattern_index[key].append(event_id)

        # 更新类别索引
        category = features.get("category", "").lower()
        cat_key = f"cat:{category}"
        if cat_key not in self._pattern_index:
            self._pattern_index[cat_key] = []
        if event_id not in self._pattern_index[cat_key]:
            self._pattern_index[cat_key].append(event_id)


# 全局服务实例
pattern_matcher = PatternMatcherService()
