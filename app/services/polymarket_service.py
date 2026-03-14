# Polymarket 直接 API 服务 - 获取预测市场实时数据
import os
import httpx
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta


# 解决HTTP代理问题
_no_proxy_hosts = [
    "localhost", "127.0.0.1",
    "gamma-api.polymarket.com",
    "clob.polymarket.com",
    "data-api.polymarket.com"
]
_no_proxy_value = ",".join(_no_proxy_hosts)
os.environ["NO_PROXY"] = _no_proxy_value
os.environ["no_proxy"] = _no_proxy_value
for proxy_var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(proxy_var, None)


class PolymarketService:
    """Polymarket 预测市场服务 - 直接调用 Polymarket 公开API"""

    def __init__(self):
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.clob_api = "https://clob.polymarket.com"
        self.timeout = 15.0
        self._cache: Dict[str, Any] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 180  # 3分钟缓存

    def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        return httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            trust_env=False,
            proxy=None,
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )

    async def get_markets(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 20,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取预测市场数据

        Args:
            category: 市场类别 (politics, crypto, sports, etc.)
            query: 搜索关键词
            limit: 返回数量限制
            active_only: 仅返回活跃市场
        """
        try:
            async with self._get_client() as client:
                # 使用 Gamma API 获取市场
                params = {
                    "limit": limit,
                    "offset": 0
                }

                if active_only:
                    params["active"] = "true"

                if query:
                    params["tag"] = query

                # 按交易量排序
                params["_s"] = "volume24hr"
                params["_sd"] = "desc"

                response = await client.get(
                    f"{self.gamma_api}/markets",
                    params=params
                )

                if response.status_code == 200:
                    markets = response.json()
                    return self._convert_markets(markets, category)

        except Exception as e:
            print(f"Error fetching Polymarket data: {e}")

        return []

    async def get_trending_markets(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取热门预测市场"""
        try:
            async with self._get_client() as client:
                response = await client.get(
                    f"{self.gamma_api}/markets",
                    params={
                        "limit": limit,
                        "active": "true",
                        "_s": "volume24hr",
                        "_sd": "desc"
                    }
                )

                if response.status_code == 200:
                    markets = response.json()
                    return self._convert_markets(markets)

        except Exception as e:
            print(f"Error fetching trending markets: {e}")

        return []

    async def get_politics_markets(self, limit: int = 15) -> List[Dict[str, Any]]:
        """获取政治类预测市场"""
        return await self.get_markets(category="politics", limit=limit)

    async def get_geopolitics_markets(self, limit: int = 15) -> List[Dict[str, Any]]:
        """获取地缘政治相关预测市场"""
        # 搜索关键词
        keywords = ["war", "conflict", "election", "government", "country", "military"]
        results = []

        try:
            async with self._get_client() as client:
                for keyword in keywords[:3]:  # 限制搜索数量
                    response = await client.get(
                        f"{self.gamma_api}/markets",
                        params={
                            "limit": 10,
                            "active": "true",
                            "_q": keyword
                        }
                    )

                    if response.status_code == 200:
                        markets = response.json()
                        results.extend(self._convert_markets(markets, "politics"))

            # 去重
            seen = set()
            unique_results = []
            for r in results:
                if r["id"] not in seen:
                    seen.add(r["id"])
                    unique_results.append(r)

            return unique_results[:limit]

        except Exception as e:
            print(f"Error fetching geopolitics markets: {e}")

        return []

    def _convert_markets(
        self,
        markets: List[Dict],
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """将 Polymarket 数据转换为事件格式"""
        events = []

        for market in markets:
            try:
                # 解析价格
                tokens = market.get("tokens", [])
                yes_price = 0.5
                for token in tokens:
                    if token.get("outcome", "").upper() == "YES":
                        yes_price = float(token.get("price", 0.5))
                        break

                # 如果没有tokens，尝试从outcome_prices解析
                if not tokens and market.get("outcome_prices"):
                    try:
                        prices = market.get("outcome_prices", [])
                        if prices:
                            yes_price = float(prices[0])
                    except (ValueError, IndexError):
                        yes_price = 0.5

                # 确定类别
                category = self._map_category(market.get("tags", []))
                if category_filter and category != category_filter:
                    continue

                # 计算严重程度（基于概率极端程度）
                severity = self._calculate_severity(yes_price, market)

                # 解析时间
                end_date = market.get("end_date_iso")
                if end_date:
                    timestamp = end_date
                else:
                    timestamp = datetime.utcnow().isoformat() + "Z"

                event = {
                    "id": f"pm-{market.get('condition_id', market.get('id', ''))}",
                    "title": market.get("question", market.get("name", "")),
                    "description": f"预测市场: {yes_price*100:.1f}% 概率",
                    "category": category,
                    "severity": severity,
                    "location": {"country": "Global", "region": "", "lat": 0, "lon": 0},
                    "timestamp": timestamp,
                    "source": "Polymarket",
                    "entities": market.get("tags", []),
                    "sentiment": "neutral",
                    "prediction_data": {
                        "yes_price": yes_price,
                        "volume": float(market.get("volume", 0) or 0),
                        "liquidity": float(market.get("liquidity", 0) or 0),
                        "url": f"https://polymarket.com/event/{market.get('slug', '')}"
                    }
                }
                events.append(event)

            except Exception as e:
                print(f"Error converting market: {e}")
                continue

        return events

    def _map_category(self, tags: List[str]) -> str:
        """映射市场标签到事件类别"""
        if not tags:
            return "other"

        tags_lower = [t.lower() for t in tags]

        if any(t in tags_lower for t in ["politics", "election", "government"]):
            return "politics"
        if any(t in tags_lower for t in ["crypto", "finance", "economy"]):
            return "economy"
        if any(t in tags_lower for t in ["sports", "football", "basketball"]):
            return "other"  # 体育类不纳入主要事件
        if any(t in tags_lower for t in ["technology", "tech"]):
            return "technology"
        if any(t in tags_lower for t in ["war", "military", "conflict"]):
            return "military"

        return "other"

    def _calculate_severity(self, yes_price: float, market: Dict) -> int:
        """计算事件严重程度"""
        # 基于交易量
        volume = float(market.get("volume", 0) or 0)

        # 高交易量且概率极端
        if volume > 1000000 and (yes_price > 0.8 or yes_price < 0.2):
            return 5
        if volume > 500000 and (yes_price > 0.7 or yes_price < 0.3):
            return 4
        if volume > 100000:
            return 3

        return 2

    async def check_connection(self) -> bool:
        """检查 Polymarket API 连接"""
        try:
            async with self._get_client() as client:
                response = await client.get(f"{self.gamma_api}/markets", params={"limit": 1})
                return response.status_code == 200
        except Exception:
            return False

    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        connected = await self.check_connection()
        return {
            "service": "Polymarket",
            "connected": connected,
            "api_base": self.gamma_api,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# 全局服务实例
polymarket_service = PolymarketService()
