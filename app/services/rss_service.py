# RSS 数据源服务 - 从多个RSS源获取实时新闻
import os
import httpx
import asyncio
import feedparser
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse
from deep_translator import GoogleTranslator

# 翻译器实例（懒加载）
_translator = None


def _get_translator():
    """获取翻译器实例（懒加载）"""
    global _translator
    if _translator is None:
        try:
            _translator = GoogleTranslator(source='auto', target='zh-CN')
        except Exception as e:
            print(f"[翻译] 初始化翻译器失败: {e}")
    return _translator


# 常用英文词汇翻译字典（作为后备和快速翻译）
TRANSLATION_DICT = {
    # 军事相关
    "war": "战争", "military": "军事", "army": "军队", "navy": "海军", "air force": "空军",
    "missile": "导弹", "nuclear": "核", "weapon": "武器", "attack": "攻击", "defense": "防御",
    "soldier": "士兵", "troops": "部队", "combat": "战斗", "invasion": "入侵", "strike": "打击",
    "bomb": "炸弹", "explosion": "爆炸", "drone": "无人机", "tank": "坦克", "fighter": "战斗机",
    "submarine": "潜艇", "aircraft carrier": "航母", "naval": "海军的", "artillery": "火炮",
    "battle": "战役", "offensive": "进攻", "retreat": "撤退", "ceasefire": "停火",
    "nuclear weapons": "核武器", "ballistic": "弹道", "cruise missile": "巡航导弹",

    # 政治相关
    "president": "总统", "government": "政府", "election": "选举", "vote": "投票",
    "congress": "国会", "senate": "参议院", "parliament": "议会", "minister": "部长",
    "diplomat": "外交官", "diplomacy": "外交", "treaty": "条约", "sanctions": "制裁",
    "summit": "峰会", "policy": "政策", "law": "法律", "reform": "改革", "protest": "抗议",
    "democracy": "民主", "republic": "共和国", "communist": "共产党", "party": "政党",
    "prime minister": "总理", "secretary": "部长", "official": "官员", "leader": "领导人",
    "administration": "政府", "white house": "白宫", "kremlin": "克里姆林宫",

    # 经济相关
    "economy": "经济", "market": "市场", "stock": "股票", "trade": "贸易", "tariff": "关税",
    "bank": "银行", "currency": "货币", "dollar": "美元", "yuan": "人民币", "euro": "欧元",
    "inflation": "通胀", "recession": "衰退", "growth": "增长", "investment": "投资",
    "gdp": "GDP", "federal reserve": "美联储", "interest rate": "利率", "debt": "债务",
    "cryptocurrency": "加密货币", "bitcoin": "比特币", "oil": "石油", "gas": "天然气",
    "prices": "价格", "exports": "出口", "imports": "进口", "supply chain": "供应链",

    # 科技相关
    "technology": "科技", "ai": "人工智能", "artificial intelligence": "人工智能",
    "chip": "芯片", "semiconductor": "半导体", "software": "软件", "hardware": "硬件",
    "cyber": "网络", "hacker": "黑客", "data": "数据", "cloud": "云", "5g": "5G",
    "quantum": "量子", "robot": "机器人", "automation": "自动化", "digital": "数字",
    "internet": "互联网", "smartphone": "智能手机", "battery": "电池", "electric vehicle": "电动车",
    "tech giant": "科技巨头", "startup": "初创公司", "innovation": "创新",

    # 国际关系
    "china": "中国", "usa": "美国", "united states": "美国", "russia": "俄罗斯",
    "ukraine": "乌克兰", "japan": "日本", "korea": "韩国", "north korea": "朝鲜",
    "taiwan": "台湾", "india": "印度", "europe": "欧洲", "middle east": "中东",
    "israel": "以色列", "iran": "伊朗", "pakistan": "巴基斯坦", "nato": "北约",
    "united nations": "联合国", "eu": "欧盟", "asean": "东盟", "g20": "G20",
    "asia": "亚洲", "africa": "非洲", "america": "美洲", "australia": "澳大利亚",
    "germany": "德国", "france": "法国", "uk": "英国", "britain": "英国",

    # 灾难/事件
    "earthquake": "地震", "flood": "洪水", "hurricane": "飓风", "typhoon": "台风",
    "fire": "火灾", "pandemic": "大流行", "virus": "病毒", "covid": "新冠",
    "accident": "事故", "crash": "坠毁", "disaster": "灾难", "emergency": "紧急",
    "casualties": "伤亡", "killed": "死亡", "injured": "受伤", "missing": "失踪",

    # 时间词
    "today": "今天", "yesterday": "昨天", "tomorrow": "明天", "week": "周", "month": "月",
    "year": "年", "latest": "最新", "breaking": "突发", "update": "更新",
    "monday": "周一", "tuesday": "周二", "wednesday": "周三", "thursday": "周四",
    "friday": "周五", "saturday": "周六", "sunday": "周日",

    # 动词
    "says": "称", "announces": "宣布", "reports": "报道", "warns": "警告",
    "confirms": "确认", "reveals": "披露", "launches": "启动", "signs": "签署",
    "agrees": "同意", "rejects": "拒绝", "threatens": "威胁", "accuses": "指控",
    "claims": "声称", "urges": "敦促", "calls for": "呼吁", "discusses": "讨论",
    "meets": "会晤", "visits": "访问", "returns": "返回", "leaves": "离开",
    "begins": "开始", "ends": "结束", "continues": "继续", "stops": "停止",
    "hits": "袭击", "kills": "杀死", "destroys": "摧毁", "damages": "损坏",

    # 形容词/副词
    "new": "新", "major": "重大", "critical": "关键", "important": "重要",
    "urgent": "紧急", "global": "全球", "international": "国际", "national": "国家",
    "tensions": "紧张局势", "crisis": "危机", "conflict": "冲突",
    "significant": "重大", "historic": "历史性", "unprecedented": "前所未有",
    "near": "附近", "amid": "在...之中", "after": "之后", "before": "之前",
    "during": "期间", "following": "随后", "over": "关于",
}


# 解决HTTP代理问题
_no_proxy_hosts = [
    "localhost", "127.0.0.1", "0.0.0.0", "::1",
    # 国际源
    "feeds.bbci.co.uk", "rss.cnn.com", "news.google.com",
    "www.reuters.com", "rss.nytimes.com", "feeds.washingtonpost.com",
    # 中文源 - 原有
    "news.sina.com.cn", "mil.news.sina.com.cn", "finance.sina.com.cn", "tech.sina.com.cn",
    "news.qq.com", "www.sohu.com", "www.people.com.cn",
    "world.huanqiu.com", "mil.huanqiu.com", "news.cctv.com",
    "www.cankaoxiaoxi.com", "www.guancha.cn", "news.ifeng.com",
    "news.163.com", "36kr.com", "www.huxiu.com",
    # 中文源 - 新增
    "rsshub.app", "www.caixin.com", "www.thepaper.cn", "www.yicai.com",
    "www.chinanews.com", "www.news.cn", "www.ithome.com", "www.tmtpost.com",
    "xueqiu.com", "www.eastmoney.com", "www.jiemian.com", "www.zhihu.com",
    "weibo.com", "www.douyin.com", "www.cnr.cn", "www.gmw.cn", "www.81.cn"
]
_no_proxy_value = ",".join(_no_proxy_hosts)
os.environ["NO_PROXY"] = _no_proxy_value
os.environ["no_proxy"] = _no_proxy_value
# 清除代理设置
for proxy_var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(proxy_var, None)


# 中文分类标签映射
CATEGORY_LABELS = {
    "military": "军事",
    "politics": "政治",
    "economy": "经济",
    "technology": "科技",
    "sports": "体育",
    "entertainment": "娱乐",
    "health": "健康",
    "science": "科学",
    "other": "其他"
}

# RSS 数据源配置 - 多语言新闻源（优先中文源）
RSS_FEEDS = {
    # ============ 中文新闻源 ============
    # 新浪新闻
    "sina_news": {
        "url": "https://news.sina.com.cn/roll/index.d.html",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "sina_mil": {
        "url": "https://mil.news.sina.com.cn/roll/index.d.html",
        "category": "military",
        "language": "zh",
        "priority": 1
    },
    "sina_finance": {
        "url": "https://finance.sina.com.cn/7x24/",
        "category": "economy",
        "language": "zh",
        "priority": 1
    },
    "sina_tech": {
        "url": "https://tech.sina.com.cn/roll/index.d.html",
        "category": "technology",
        "language": "zh",
        "priority": 1
    },
    # 腾讯新闻
    "tencent_news": {
        "url": "https://news.qq.com/newsgj/rss_newswj.xml",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "tencent_mil": {
        "url": "https://news.qq.com/newsgj/rss_military.xml",
        "category": "military",
        "language": "zh",
        "priority": 1
    },
    "tencent_finance": {
        "url": "https://news.qq.com/newsgj/rss_finance.xml",
        "category": "economy",
        "language": "zh",
        "priority": 1
    },
    "tencent_tech": {
        "url": "https://news.qq.com/newsgj/rss_tech.xml",
        "category": "technology",
        "language": "zh",
        "priority": 1
    },
    # 搜狐新闻
    "sohu_news": {
        "url": "https://www.sohu.com/rss",
        "category": "politics",
        "language": "zh",
        "priority": 2
    },
    # 人民日报/人民网
    "people_daily": {
        "url": "http://www.people.com.cn/rss/politics.xml",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "people_mil": {
        "url": "http://www.people.com.cn/rss/mil.xml",
        "category": "military",
        "language": "zh",
        "priority": 1
    },
    "people_finance": {
        "url": "http://www.people.com.cn/rss/finance.xml",
        "category": "economy",
        "language": "zh",
        "priority": 1
    },
    "people_tech": {
        "url": "http://www.people.com.cn/rss/it.xml",
        "category": "technology",
        "language": "zh",
        "priority": 1
    },
    # 环球网
    "huanqiu_world": {
        "url": "https://world.huanqiu.com/rss/world.xml",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "huanqiu_mil": {
        "url": "https://mil.huanqiu.com/rss/milsite.xml",
        "category": "military",
        "language": "zh",
        "priority": 1
    },
    # 央视新闻
    "cctv_news": {
        "url": "https://news.cctv.com/world/rss.xml",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "cctv_finance": {
        "url": "https://news.cctv.com/finance/rss.xml",
        "category": "economy",
        "language": "zh",
        "priority": 1
    },
    # 参考消息
    "cankao": {
        "url": "http://www.cankaoxiaoxi.com/rss/cankao.xml",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    # 观察者网
    "guancha": {
        "url": "https://www.guancha.cn/rss/",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    # 凤凰网
    "ifeng_news": {
        "url": "https://news.ifeng.com/rss/index.xml",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "ifeng_mil": {
        "url": "https://news.ifeng.com/military/rss/index.xml",
        "category": "military",
        "language": "zh",
        "priority": 1
    },
    # 网易新闻
    "163_news": {
        "url": "https://news.163.com/special/00011K6L/rss_newstop.xml",
        "category": "politics",
        "language": "zh",
        "priority": 2
    },
    "163_mil": {
        "url": "https://news.163.com/special/00011K6L/rss_war.xml",
        "category": "military",
        "language": "zh",
        "priority": 2
    },
    # 36氪（科技财经）
    "36kr": {
        "url": "https://36kr.com/feed",
        "category": "technology",
        "language": "zh",
        "priority": 2
    },
    # 虎嗅
    "huxiu": {
        "url": "https://www.huxiu.com/rss/0.xml",
        "category": "technology",
        "language": "zh",
        "priority": 2
    },
    # ============ 新增中文新闻源 ============
    # 财新网
    "caixin_finance": {
        "url": "https://rsshub.app/caixin/finance",
        "category": "economy",
        "language": "zh",
        "priority": 1
    },
    "caixin_politics": {
        "url": "https://rsshub.app/caixin/politics",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    # 澎湃新闻
    "thepaper_china": {
        "url": "https://rsshub.app/thepaper/featured",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "thepaper_world": {
        "url": "https://rsshub.app/thepaper/world",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    # 第一财经
    "yicai": {
        "url": "https://rsshub.app/yicai/brief",
        "category": "economy",
        "language": "zh",
        "priority": 1
    },
    # 中国新闻网
    "chinanews_china": {
        "url": "https://rsshub.app/chinanews/china",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "chinanews_world": {
        "url": "https://rsshub.app/chinanews/world",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    # 新华网
    "xinhua_world": {
        "url": "http://www.news.cn/world/news_world.xml",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    "xinhua_finance": {
        "url": "http://www.news.cn/fortune/news_fortune.xml",
        "category": "economy",
        "language": "zh",
        "priority": 1
    },
    # IT之家
    "ithome": {
        "url": "https://rsshub.app/ithome/ranking/7days",
        "category": "technology",
        "language": "zh",
        "priority": 2
    },
    # 钛媒体
    "tmtpost": {
        "url": "https://rsshub.app/tmtpost",
        "category": "technology",
        "language": "zh",
        "priority": 2
    },
    # 雪球热榜
    "xueqiu_hot": {
        "url": "https://rsshub.app/xueqiu/hotstock",
        "category": "economy",
        "language": "zh",
        "priority": 2
    },
    # 东方财富
    "eastmoney": {
        "url": "https://rsshub.app/eastmoney/important",
        "category": "economy",
        "language": "zh",
        "priority": 2
    },
    # 界面新闻
    "jiemian": {
        "url": "https://rsshub.app/jiemian",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    # 知乎热榜
    "zhihu_hot": {
        "url": "https://rsshub.app/zhihu/hotlist",
        "category": "other",
        "language": "zh",
        "priority": 3
    },
    # 微博热搜
    "weibo_hot": {
        "url": "https://rsshub.app/weibo/search/hot",
        "category": "other",
        "language": "zh",
        "priority": 3
    },
    # 抖音热点
    "douyin_hot": {
        "url": "https://rsshub.app/douyin/trending",
        "category": "other",
        "language": "zh",
        "priority": 3
    },
    # 央广网
    "cnr_news": {
        "url": "https://rsshub.app/cnr/index",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    # 光明网
    "gmw_news": {
        "url": "https://rsshub.app/gmw/news",
        "category": "politics",
        "language": "zh",
        "priority": 1
    },
    # 中国军网
    "81_cn": {
        "url": "https://rsshub.app/81/jqkx",
        "category": "military",
        "language": "zh",
        "priority": 1
    },
    # ============ 国际新闻源（作为补充）============
    "bbc_world": {
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "politics",
        "language": "en",
        "priority": 3
    },
    "bbc_chinese": {
        "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "category": "politics",
        "language": "zh",
        "priority": 2
    },
    "dw_chinese": {
        "url": "https://rss.dw.com/rdf/rss-chi-all",
        "category": "politics",
        "language": "zh",
        "priority": 2
    },
    "cnn_world": {
        "url": "http://rss.cnn.com/rss/edition_world.rss",
        "category": "politics",
        "language": "en",
        "priority": 3
    },
    "techcrunch": {
        "url": "https://techcrunch.com/feed/",
        "category": "technology",
        "language": "en",
        "priority": 3
    },
    "defense_news": {
        "url": "https://www.defensenews.com/arc/outboundfeeds/rss/",
        "category": "military",
        "language": "en",
        "priority": 3
    },
    "janes": {
        "url": "https://www.janes.com/rss/feed",
        "category": "military",
        "language": "en",
        "priority": 3
    }
}


def _is_english(text: str) -> bool:
    """检测文本是否主要为英文"""
    if not text:
        return False
    # 统计英文字符比例
    english_chars = sum(1 for c in text if c.isascii() and c.isalpha())
    total_alpha = sum(1 for c in text if c.isalpha())
    if total_alpha == 0:
        return False
    return english_chars / total_alpha > 0.7


def _translate_with_dict(text: str) -> str:
    """使用字典进行快速翻译（替换已知词汇）"""
    result = text
    text_lower = text.lower()

    # 按词汇长度排序，优先匹配长词组
    sorted_dict = sorted(TRANSLATION_DICT.items(), key=lambda x: -len(x[0]))

    for eng, chn in sorted_dict:
        # 使用正则表达式进行不区分大小写的替换
        pattern = re.compile(re.escape(eng), re.IGNORECASE)
        if pattern.search(result):
            result = pattern.sub(chn, result)

    return result


def translate_to_chinese(text: str, use_api: bool = True) -> tuple:
    """
    将文本翻译成中文
    返回: (翻译后的文本, 是否使用了API翻译)
    """
    if not text or not _is_english(text):
        return text, False

    # 首先尝试使用Google Translate API
    if use_api:
        translator = _get_translator()
        if translator:
            try:
                translated = translator.translate(text)
                if translated and translated != text:
                    print(f"[翻译] API翻译成功: '{text[:50]}...' -> '{translated[:50]}...'")
                    return translated, True
            except Exception as e:
                print(f"[翻译] API翻译失败: {e}")

    # 后备方案：使用字典翻译
    dict_translated = _translate_with_dict(text)
    if dict_translated != text:
        print(f"[翻译] 字典翻译: '{text[:50]}...' -> '{dict_translated[:50]}...'")
        return dict_translated, False

    return text, False


class RSSService:
    """RSS 数据获取服务 - 优先级最高的实时数据源"""

    def __init__(self):
        self.timeout = 15.0
        self._cache: Dict[str, Any] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 300  # 5分钟缓存
        self._translation_enabled = True  # 翻译功能开关

    def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        return httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            trust_env=False,
            proxy=None
        )

    async def fetch_feed(self, feed_key: str, feed_config: Dict) -> List[Dict[str, Any]]:
        """获取单个RSS feed - 先直接访问，失败则使用代理"""
        events = []
        
        # 尝试直接访问
        proxy = None
        
        # 首先尝试直接访问
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, trust_env=False) as client:
                response = await client.get(feed_config["url"])
                if response.status_code == 200:
                    feed = feedparser.parse(response.text)
                    for entry in feed.entries[:20]:
                        event = self._convert_entry(entry, feed_config)
                        if event:
                            events.append(event)
                    if events:
                        print(f"[RSS] {feed_key}: 直接访问成功，获取 {len(events)} 条")
                        return events
        except Exception as e:
            print(f"[RSS] {feed_key}: 直接访问失败: {e}")
        
        # 直接访问失败，尝试使用代理
        # 默认代理地址（可配置）
        proxy = os.environ.get("RSS_PROXY") or os.environ.get("HTTP_PROXY") or "http://192.168.2.115:10811"
        if proxy:
            proxies = {"http://": proxy, "https://": proxy}
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, trust_env=False, proxies=proxies) as client:
                    response = await client.get(feed_config["url"])
                    if response.status_code == 200:
                        feed = feedparser.parse(response.text)
                        for entry in feed.entries[:20]:
                            event = self._convert_entry(entry, feed_config)
                            if event:
                                events.append(event)
                        if events:
                            print(f"[RSS] {feed_key}: 代理访问成功，获取 {len(events)} 条")
                        return events
            except Exception as e:
                print(f"[RSS] {feed_key}: 代理访问失败: {e}")
        
        return events

    def _convert_entry(self, entry: Any, feed_config: Dict) -> Optional[Dict[str, Any]]:
        """将RSS entry转换为事件格式"""
        try:
            # 解析发布时间
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            if published:
                timestamp = datetime(*published[:6]).isoformat() + "Z"
            else:
                timestamp = datetime.utcnow().isoformat() + "Z"

            # 提取原始标题和摘要
            original_title = entry.get("title", "未命名")
            summary = entry.get("summary", "")
            if len(summary) > 300:
                summary = summary[:300] + "..."

            # 翻译英文标题（如果是英文源且启用了翻译）
            title = original_title
            is_english = feed_config.get("language", "en") == "en" and self._translation_enabled
            if is_english and _is_english(original_title):
                translated_title, used_api = translate_to_chinese(original_title)
                title = translated_title

            # 翻译英文摘要（可选，如果需要）
            if is_english and _is_english(summary):
                translated_summary, _ = translate_to_chinese(summary)
                summary = translated_summary

            # 计算严重程度（基于关键词）
            severity = self._calculate_severity(title, summary)

            # 获取分类
            category = feed_config.get("category", "other")

            # 获取来源域名
            source_url = urlparse(entry.get("link", "")).netloc or "RSS Feed"

            return {
                "id": f"rss-{hash(entry.get('link', ''))}",
                "title": title,
                "original_title": original_title if title != original_title else None,  # 保存原始标题
                "description": summary,
                "category": category,
                "category_label": CATEGORY_LABELS.get(category, "其他"),  # 中文分类标签
                "severity": severity,
                "location": {"country": "全球", "region": "", "lat": 0, "lon": 0},
                "timestamp": timestamp,
                "source": source_url,
                "source_label": self._get_source_label(source_url),  # 中文来源名称
                "entities": [],
                "sentiment": self._detect_sentiment(title),
                "language": feed_config.get("language", "en"),
                "translated": title != original_title  # 标记是否已翻译
            }
        except Exception as e:
            print(f"Error converting RSS entry: {e}")
            return None

    def _get_source_label(self, source_url: str) -> str:
        """获取新闻来源的中文名称"""
        source_mapping = {
            # 中文源 - 原有
            "news.sina.com.cn": "新浪新闻",
            "mil.news.sina.com.cn": "新浪军事",
            "finance.sina.com.cn": "新浪财经",
            "tech.sina.com.cn": "新浪科技",
            "news.qq.com": "腾讯新闻",
            "www.sohu.com": "搜狐新闻",
            "www.people.com.cn": "人民网",
            "world.huanqiu.com": "环球网",
            "mil.huanqiu.com": "环球军事",
            "news.cctv.com": "央视新闻",
            "www.cankaoxiaoxi.com": "参考消息",
            "www.guancha.cn": "观察者网",
            "news.ifeng.com": "凤凰网",
            "news.163.com": "网易新闻",
            "36kr.com": "36氪",
            "www.huxiu.com": "虎嗅",
            # 中文源 - 新增
            "caixin": "财新网",
            "thepaper": "澎湃新闻",
            "yicai": "第一财经",
            "chinanews": "中国新闻网",
            "news.cn": "新华网",
            "ithome": "IT之家",
            "tmtpost": "钛媒体",
            "xueqiu": "雪球",
            "eastmoney": "东方财富",
            "jiemian": "界面新闻",
            "zhihu": "知乎",
            "weibo": "微博",
            "douyin": "抖音",
            "cnr": "央广网",
            "gmw": "光明网",
            "81.cn": "中国军网",
            "rsshub.app": "RSSHub聚合",
            # 国际源
            "feeds.bbci.co.uk": "BBC",
            "rss.cnn.com": "CNN",
            "www.reuters.com": "路透社",
            "techcrunch.com": "TechCrunch",
            "www.defensenews.com": "防务新闻",
            "www.janes.com": "简氏防务",
            "rss.dw.com": "德国之声"
        }
        for key, label in source_mapping.items():
            if key in source_url:
                return label
        return source_url

    def _calculate_severity(self, title: str, summary: str) -> int:
        """基于关键词计算严重程度"""
        text = (title + " " + summary).lower()

        # 高严重性关键词
        high_keywords = ["war", "attack", "nuclear", "missile", "invasion", "crisis",
                        "战争", "攻击", "核", "导弹", "入侵", "危机"]
        for kw in high_keywords:
            if kw in text:
                return 5

        # 中高严重性
        medium_high = ["military", "conflict", "sanctions", "emergency", "terror",
                      "军事", "冲突", "制裁", "紧急", "恐怖"]
        for kw in medium_high:
            if kw in text:
                return 4

        # 中等严重性
        medium = ["tension", "dispute", "protest", "election", "trade",
                 "紧张", "争议", "抗议", "选举", "贸易"]
        for kw in medium:
            if kw in text:
                return 3

        return 2

    def _detect_sentiment(self, title: str) -> str:
        """检测情感倾向"""
        negative = ["war", "crisis", "attack", "death", "crash", "collapse",
                   "战争", "危机", "攻击", "死亡", "崩溃"]
        positive = ["peace", "agreement", "growth", "success", "breakthrough",
                   "和平", "协议", "增长", "成功", "突破"]

        text = title.lower()
        for word in negative:
            if word in text:
                return "negative"
        for word in positive:
            if word in text:
                return "positive"
        return "neutral"

    async def fetch_all_feeds(
        self,
        categories: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取所有RSS feeds"""
        # 检查缓存
        if self._cache_time and (datetime.now() - self._cache_time).seconds < self._cache_ttl:
            cached = self._cache.get("events", [])
            if categories:
                cached = [e for e in cached if e.get("category") in categories]
            return cached[:limit]

        all_events = []
        tasks = []

        for feed_key, feed_config in RSS_FEEDS.items():
            if categories and feed_config.get("category") not in categories:
                continue
            tasks.append(self.fetch_feed(feed_key, feed_config))

        # 并行获取所有feeds
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_events.extend(result)

        # 按时间排序
        all_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        # 更新缓存
        self._cache["events"] = all_events
        self._cache_time = datetime.now()

        return all_events[:limit]

    async def get_source_status(self) -> Dict[str, Any]:
        """获取RSS数据源状态"""
        status = {}
        for feed_key, feed_config in RSS_FEEDS.items():
            try:
                async with self._get_client() as client:
                    response = await client.head(feed_config["url"])
                    status[feed_key] = {
                        "url": feed_config["url"],
                        "available": response.status_code == 200,
                        "category": feed_config.get("category")
                    }
            except Exception:
                status[feed_key] = {
                    "url": feed_config["url"],
                    "available": False,
                    "category": feed_config.get("category")
                }

        return {
            "sources": status,
            "total_sources": len(RSS_FEEDS),
            "available_sources": sum(1 for s in status.values() if s["available"])
        }


# 全局服务实例
rss_service = RSSService()
