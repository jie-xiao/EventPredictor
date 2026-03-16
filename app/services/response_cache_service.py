# 响应缓存服务
"""
P0阶段功能：响应缓存
- 缓存分析结果，避免重复计算
- 基于事件特征生成缓存键
- 支持TTL过期机制
- 内存缓存 + 持久化存储
"""
import json
import hashlib
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import OrderedDict
import threading


class ResponseCacheService:
    """响应缓存服务 - 缓存分析结果，避免重复计算"""

    # 默认配置
    DEFAULT_TTL = 3600  # 默认缓存1小时
    MAX_MEMORY_CACHE_SIZE = 500  # 内存缓存最大条目数
    PERSISTENCE_ENABLED = True  # 是否启用持久化

    def __init__(
        self,
        cache_dir: str = "data/cache",
        ttl: int = DEFAULT_TTL,
        max_size: int = MAX_MEMORY_CACHE_SIZE
    ):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "response_cache.json"

        self.ttl = ttl
        self.max_size = max_size

        # 内存缓存 (使用OrderedDict实现LRU)
        self._memory_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = threading.RLock()

        # 缓存统计
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }

        # 加载持久化缓存
        self._load_from_disk()

    def _generate_cache_key(self, event: Dict[str, Any], analysis_type: str = "prediction") -> str:
        """
        生成缓存键

        Args:
            event: 事件信息
            analysis_type: 分析类型 (prediction, multi_agent, scenario等)

        Returns:
            缓存键字符串
        """
        # 提取关键字段
        key_fields = {
            "title": event.get("title", "")[:200],  # 限制长度
            "description": event.get("description", "")[:500],
            "category": event.get("category", "Other"),
            "importance": event.get("importance", 3)
        }

        # 生成规范化字符串
        normalized = json.dumps(key_fields, sort_keys=True, ensure_ascii=False)

        # 生成哈希
        hash_value = hashlib.sha256(normalized.encode()).hexdigest()[:32]

        return f"{analysis_type}:{hash_value}"

    def _generate_semantic_key(self, event: Dict[str, Any]) -> str:
        """
        生成语义缓存键（基于关键词和实体）
        用于相似事件的缓存命中
        """
        # 提取关键词和实体
        keywords = self._extract_keywords(event)
        entities = self._extract_entities(event)

        # 排序并组合
        key_components = sorted(keywords[:5]) + sorted(entities[:5])
        key_str = "|".join(key_components)

        return hashlib.md5(key_str.encode()).hexdigest()[:16]

    def _extract_keywords(self, event: Dict[str, Any]) -> List[str]:
        """提取关键词"""
        import re
        from collections import Counter

        text = f"{event.get('title', '')} {event.get('description', '')}"

        # 使用简单的关键词提取
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}|[a-zA-Z]{3,}', text.lower())
        word_freq = Counter(words)

        stopwords = {"的", "是", "在", "有", "和", "了", "对", "这", "那", "为", "the", "and", "is", "are", "was", "were"}
        keywords = [w for w, _ in word_freq.most_common(10) if w not in stopwords]

        return keywords

    def _extract_entities(self, event: Dict[str, Any]) -> List[str]:
        """提取实体"""
        text = f"{event.get('title', '')} {event.get('description', '')}".lower()

        entities = []
        entity_list = [
            "中国", "美国", "俄罗斯", "日本", "欧盟",
            "china", "us", "russia", "japan", "eu"
        ]

        for entity in entity_list:
            if entity in text:
                entities.append(entity)

        return entities

    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """检查缓存是否过期"""
        if "expires_at" not in cache_entry:
            return True

        expires_at = cache_entry.get("expires_at", 0)
        return time.time() > expires_at

    def _evict_oldest(self):
        """淘汰最旧的缓存条目（LRU）"""
        with self._lock:
            while len(self._memory_cache) > self.max_size:
                # 移除最旧的条目
                oldest_key = next(iter(self._memory_cache))
                del self._memory_cache[oldest_key]
                self._stats["evictions"] += 1

    def _load_from_disk(self):
        """从磁盘加载缓存"""
        if not self.PERSISTENCE_ENABLED:
            return

        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 加载到内存缓存，跳过过期条目
                current_time = time.time()
                for key, entry in data.get("cache", {}).items():
                    if not self._is_expired(entry):
                        self._memory_cache[key] = entry

                # 加载统计信息
                self._stats = data.get("stats", self._stats)

            except Exception as e:
                print(f"加载缓存失败: {e}")

    def _save_to_disk(self):
        """保存缓存到磁盘"""
        if not self.PERSISTENCE_ENABLED:
            return

        try:
            with self._lock:
                data = {
                    "cache": dict(self._memory_cache),
                    "stats": self._stats,
                    "updated_at": datetime.utcnow().isoformat()
                }

                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存缓存失败: {e}")

    async def get(
        self,
        event: Dict[str, Any],
        analysis_type: str = "prediction"
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存的分析结果

        Args:
            event: 事件信息
            analysis_type: 分析类型

        Returns:
            缓存的分析结果，如果不存在或过期返回None
        """
        with self._lock:
            self._stats["total_requests"] += 1

            # 生成缓存键
            cache_key = self._generate_cache_key(event, analysis_type)

            # 查找精确匹配
            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]

                if not self._is_expired(entry):
                    # 命中，移到最后（LRU）
                    self._memory_cache.move_to_end(cache_key)
                    self._stats["hits"] += 1

                    return entry.get("data")

            # 尝试语义匹配（相似事件）
            semantic_key = self._generate_semantic_key(event)
            semantic_cache_key = f"semantic:{semantic_key}:{analysis_type}"

            if semantic_cache_key in self._memory_cache:
                entry = self._memory_cache[semantic_cache_key]

                if not self._is_expired(entry):
                    self._memory_cache.move_to_end(semantic_cache_key)
                    self._stats["hits"] += 1

                    # 标记为语义匹配
                    result = entry.get("data", {}).copy()
                    result["_cache_hit_type"] = "semantic"

                    return result

            # 未命中
            self._stats["misses"] += 1
            return None

    async def set(
        self,
        event: Dict[str, Any],
        data: Dict[str, Any],
        analysis_type: str = "prediction",
        ttl: Optional[int] = None
    ) -> str:
        """
        设置缓存

        Args:
            event: 事件信息
            data: 要缓存的数据
            analysis_type: 分析类型
            ttl: 过期时间（秒），默认使用全局配置

        Returns:
            缓存键
        """
        with self._lock:
            # 生成缓存键
            cache_key = self._generate_cache_key(event, analysis_type)

            # 计算过期时间
            cache_ttl = ttl if ttl is not None else self.ttl
            expires_at = time.time() + cache_ttl

            # 创建缓存条目
            entry = {
                "key": cache_key,
                "data": data,
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": expires_at,
                "ttl": cache_ttl,
                "event_summary": {
                    "title": event.get("title", "")[:100],
                    "category": event.get("category", "Other")
                }
            }

            # 添加到内存缓存
            self._memory_cache[cache_key] = entry
            self._memory_cache.move_to_end(cache_key)

            # 同时存储语义键（用于相似事件匹配）
            semantic_key = self._generate_semantic_key(event)
            semantic_cache_key = f"semantic:{semantic_key}:{analysis_type}"
            self._memory_cache[semantic_cache_key] = entry

            # 检查是否需要淘汰
            self._evict_oldest()

            # 定期保存到磁盘
            if len(self._memory_cache) % 50 == 0:
                self._save_to_disk()

            return cache_key

    async def delete(self, event: Dict[str, Any], analysis_type: str = "prediction") -> bool:
        """删除指定缓存"""
        with self._lock:
            cache_key = self._generate_cache_key(event, analysis_type)

            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
                return True

            return False

    async def clear(self, expired_only: bool = False):
        """
        清空缓存

        Args:
            expired_only: 是否只清除过期缓存
        """
        with self._lock:
            if expired_only:
                # 只清除过期条目
                keys_to_remove = [
                    k for k, v in self._memory_cache.items()
                    if self._is_expired(v)
                ]
                for key in keys_to_remove:
                    del self._memory_cache[key]
            else:
                # 清空所有
                self._memory_cache.clear()

            self._save_to_disk()

    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total if total > 0 else 0

            return {
                "total_requests": self._stats["total_requests"],
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "hit_rate": round(hit_rate, 3),
                "cache_size": len(self._memory_cache),
                "evictions": self._stats["evictions"],
                "max_size": self.max_size,
                "ttl_seconds": self.ttl
            }

    async def get_cache_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        获取缓存键列表

        Args:
            pattern: 可选的键模式匹配

        Returns:
            缓存键列表
        """
        with self._lock:
            keys = list(self._memory_cache.keys())

            if pattern:
                import fnmatch
                keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]

            return keys

    async def get_cache_entry(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """获取单个缓存条目"""
        with self._lock:
            entry = self._memory_cache.get(cache_key)

            if entry and not self._is_expired(entry):
                return {
                    "key": cache_key,
                    "created_at": entry.get("created_at"),
                    "expires_at": entry.get("expires_at"),
                    "ttl": entry.get("ttl"),
                    "event_summary": entry.get("event_summary")
                }

            return None

    async def warm_up(self, events: List[Dict[str, Any]], analysis_func) -> int:
        """
        缓存预热 - 提前计算并缓存

        Args:
            events: 事件列表
            analysis_func: 分析函数

        Returns:
            预热的缓存数量
        """
        warmed = 0

        for event in events:
            # 检查是否已缓存
            cached = await self.get(event)
            if cached is None:
                # 执行分析并缓存
                try:
                    result = await analysis_func(event)
                    await self.set(event, result)
                    warmed += 1
                except Exception as e:
                    print(f"预热失败: {e}")

        self._save_to_disk()
        return warmed

    async def refresh_ttl(
        self,
        event: Dict[str, Any],
        analysis_type: str = "prediction",
        new_ttl: Optional[int] = None
    ) -> bool:
        """
        刷新缓存TTL

        Args:
            event: 事件信息
            analysis_type: 分析类型
            new_ttl: 新的TTL（秒）

        Returns:
            是否成功
        """
        with self._lock:
            cache_key = self._generate_cache_key(event, analysis_type)

            if cache_key in self._memory_cache:
                entry = self._memory_cache[cache_key]
                ttl = new_ttl if new_ttl is not None else self.ttl
                entry["expires_at"] = time.time() + ttl
                entry["ttl"] = ttl
                return True

            return False


# 全局服务实例
response_cache = ResponseCacheService()
