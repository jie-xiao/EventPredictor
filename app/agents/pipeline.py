# Agent基类和Pipeline
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import uuid
from app.api.models import (
    Event, 
    CollectedInfo, 
    Analysis, 
    Prediction, 
    TrendDirection,
    CollectedInfo as CollectedInfoModel,
    Analysis as AnalysisModel
)


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description
    
    @abstractmethod
    def run(self, input_data: Any) -> Any:
        """运行Agent处理输入数据"""
        pass
    
    def __repr__(self) -> str:
        return f"{self.name}(role={self.role})"


class InfoCollectorAgent(BaseAgent):
    """信息收集Agent"""
    
    def __init__(self):
        super().__init__(
            name="InfoCollector",
            role="Information Gathering",
            description="收集事件的基本信息、背景和相关数据"
        )
    
    def run(self, event: Event) -> CollectedInfoModel:
        """收集事件相关信息"""
        # 构建基本信息
        basic_info = {
            "title": event.title,
            "description": event.description,
            "source": event.source,
            "timestamp": event.timestamp,
            "category": event.category,
            "importance": event.importance,
            "importance_label": self._get_importance_label(event.importance)
        }
        
        # 生成摘要
        summary = f"事件: {event.title}\n"
        summary += f"来源: {event.source}\n"
        summary += f"时间: {event.timestamp}\n"
        summary += f"分类: {event.category}\n"
        summary += f"重要性: {event.importance}/5"
        
        return CollectedInfoModel(
            basic_info=basic_info,
            related_events=[],
            market_data=None,
            summary=summary
        )
    
    def _get_importance_label(self, importance: int) -> str:
        labels = {1: "低", 2: "较低", 3: "中等", 4: "较高", 5: "高"}
        return labels.get(importance, "未知")


class AnalyzerAgent(BaseAgent):
    """深度分析Agent"""
    
    def __init__(self):
        super().__init__(
            name="Analyzer",
            role="Deep Analysis",
            description="分析事件的影响范围、持续时间、关键因素和市场情绪"
        )
    
    def run(self, collected_info: CollectedInfoModel) -> AnalysisModel:
        """分析事件影响"""
        event_info = collected_info.basic_info
        category = event_info.get("category", "Other")
        importance = event_info.get("importance", 3)
        
        # 基于事件分类和重要性进行基础分析
        impact_scope = self._analyze_impact_scope(category, importance)
        duration = self._analyze_duration(category)
        sentiment = self._analyze_sentiment(category, importance)
        key_factors = self._extract_key_factors(event_info)
        
        # 生成洞察
        insights = self._generate_insights(
            category, importance, impact_scope, duration, sentiment
        )
        
        # 增强分析：风险等级、机会、影响领域、情景分析
        risk_level, risk_factors = self._analyze_risk(category, importance, sentiment)
        opportunities = self._identify_opportunities(category, sentiment)
        affected_sectors = self._get_affected_sectors(category)
        scenario_analysis = self._generate_scenario_analysis(category, importance, sentiment)
        
        return AnalysisModel(
            impact_scope=impact_scope,
            duration=duration,
            key_factors=key_factors,
            sentiment=sentiment,
            insights=insights,
            risk_level=risk_level,
            risk_factors=risk_factors,
            opportunities=opportunities,
            affected_sectors=affected_sectors,
            scenario_analysis=scenario_analysis
        )
    
    def _analyze_risk(self, category: str, importance: int, sentiment: str) -> tuple:
        """分析风险等级和因素"""
        risk_factors = []
        
        # 基于分类确定风险因素
        risk_category_map = {
            "Monetary Policy": ["通胀压力", "政策不确定性", "市场波动"],
            "Geopolitical": ["地缘政治紧张", "贸易摩擦", "制裁风险"],
            "Economic": ["经济衰退", "失业率上升", "债务风险"],
            "Technology": ["技术变革", "监管风险", "网络安全"],
            "Natural Disaster": ["供应链中断", "保险损失", "人道危机"],
            "Social": ["社会稳定风险", "政策变化", "公众舆论"]
        }
        risk_factors.extend(risk_category_map.get(category, ["不确定风险"]))
        
        # 基于重要性调整
        if importance >= 4:
            risk_factors.append("高重要性事件，可能引发市场剧烈波动")
        
        # 基于情绪判断
        if "Negative" in sentiment:
            risk_factors.append("市场情绪偏空，风险偏好下降")
        
        # 确定风险等级
        if importance >= 4 or "Negative" in sentiment:
            risk_level = "高"
        elif importance >= 3:
            risk_level = "中"
        else:
            risk_level = "低"
        
        return risk_level, risk_factors
    
    def _identify_opportunities(self, category: str, sentiment: str) -> list:
        """识别潜在机会"""
        opportunities = []
        
        opportunity_map = {
            "Monetary Policy": ["债券投资机会", "流动性敏感资产", "降息受益板块"],
            "Geopolitical": ["避险资产配置", "军工板块", "黄金"],
            "Economic": ["估值修复机会", "消费复苏板块", "基建投资"],
            "Technology": ["创新技术投资", "数字化转型", "AI相关机会"],
            "Natural Disaster": ["保险行业机会", "重建相关需求", "农业板块"],
            "Social": ["政策扶持板块", "消费升级", "医疗健康"]
        }
        
        opportunities.extend(opportunity_map.get(category, []))
        
        if "Positive" in sentiment:
            opportunities.append("市场情绪积极，风险资产表现可能优于预期")
        
        return opportunities[:5]
    
    def _get_affected_sectors(self, category: str) -> list:
        """获取受影响领域"""
        sector_map = {
            "Monetary Policy": ["金融", "房地产", "股市", "债市"],
            "Geopolitical": ["能源", "国防", "贸易", "物流"],
            "Economic": ["消费", "制造业", "房地产", "就业市场"],
            "Technology": ["科技股", "互联网", "通信", "半导体"],
            "Natural Disaster": ["保险", "农业", "能源", "建筑"],
            "Social": ["消费", "医疗", "教育", "娱乐"]
        }
        return sector_map.get(category, ["综合市场"])
    
    def _generate_scenario_analysis(self, category: str, importance: int, sentiment: str) -> dict:
        """生成情景分析"""
        base_prob = 0.6 if importance >= 3 else 0.4
        
        scenarios = []
        
        # 乐观情景
        optimistic_prob = min(base_prob + 0.2, 0.95)
        scenarios.append({
            "name": "乐观情景",
            "probability": optimistic_prob,
            "description": "事件朝有利方向发展，市场积极响应",
            "trend": "UP"
        })
        
        # 中性情景
        neutral_prob = 1.0 - optimistic_prob - 0.15
        scenarios.append({
            "name": "中性情景",
            "probability": max(neutral_prob, 0.1),
            "description": "事件影响有限，市场维持震荡",
            "trend": "SIDEWAYS"
        })
        
        # 悲观情景
        pessimistic_prob = 0.15
        scenarios.append({
            "name": "悲观情景",
            "probability": pessimistic_prob,
            "description": "事件恶化，超出预期，市场大幅波动",
            "trend": "DOWN"
        })
        
        return {"scenarios": scenarios}
    
    def _analyze_impact_scope(self, category: str, importance: int) -> str:
        """分析影响范围"""
        scope_map = {
            "Monetary Policy": "Global",
            "Geopolitical": "Regional",
            "Economic": "Global",
            "Technology": "Industry",
            "Natural Disaster": "Regional",
            "Social": "Local",
            "Other": "Unknown"
        }
        base_scope = scope_map.get(category, "Unknown")
        
        if importance >= 4:
            return f"Global" if base_scope in ["Global", "Regional"] else base_scope
        return base_scope
    
    def _analyze_duration(self, category: str) -> str:
        """分析持续时间"""
        duration_map = {
            "Monetary Policy": "Medium-term (1-3 months)",
            "Geopolitical": "Long-term (3-12 months)",
            "Economic": "Medium-term (1-3 months)",
            "Technology": "Long-term (3-12 months)",
            "Natural Disaster": "Short-term (1-7 days)",
            "Social": "Short-term (1-7 days)",
            "Other": "Unknown"
        }
        return duration_map.get(category, "Unknown")
    
    def _analyze_sentiment(self, category: str, importance: int) -> str:
        """分析市场情绪"""
        # 简化逻辑：基于分类判断基本情绪
        positive_categories = ["Monetary Policy"]  # 降息通常被视为正面
        negative_categories = ["Geopolitical", "Natural Disaster"]
        
        if category in positive_categories:
            base_sentiment = "Positive"
        elif category in negative_categories:
            base_sentiment = "Negative"
        else:
            base_sentiment = "Neutral"
        
        # 重要性增强情绪强度
        if importance >= 4:
            return f"Strongly {base_sentiment}"
        return base_sentiment
    
    def _extract_key_factors(self, event_info: dict) -> list:
        """提取关键因素"""
        factors = []
        category = event_info.get("category", "")
        
        # 添加分类相关因素
        category_factors = {
            "Monetary Policy": ["Interest Rates", "Liquidity", "Market Sentiment"],
            "Geopolitical": ["Political Stability", "Trade Relations", "Security"],
            "Economic": ["GDP Growth", "Employment", "Inflation"],
            "Technology": ["Innovation", "Regulation", "Adoption"],
            "Natural Disaster": ["Supply Chain", "Insurance", "Human Impact"],
            "Social": ["Public Opinion", "Policy Changes", "Social Stability"]
        }
        
        factors.extend(category_factors.get(category, []))
        factors.append(f"Event Importance: {event_info.get('importance')}/5")
        
        return factors[:5]  # 最多5个因素
    
    def _generate_insights(self, category, importance, scope, duration, sentiment) -> str:
        """生成洞察"""
        return f"""基于对事件的初步分析：

1. **影响范围**: 该事件预计将对{scope}产生影响
2. **持续时间**: 预计影响持续{duration}
3. **市场情绪**: 当前市场情绪偏向{sentiment}
4. **重要性评分**: {importance}/5 ({'高' if importance >= 4 else '中等' if importance >= 3 else '低'})

需要进一步结合实时市场数据和市场预测进行综合判断。"""


class PredictorAgent(BaseAgent):
    """趋势预测Agent"""
    
    def __init__(self):
        super().__init__(
            name="Predictor",
            role="Trend Prediction",
            description="根据分析结果生成未来走势预测"
        )
    
    def run(self, analysis: AnalysisModel, event: Event) -> Prediction:
        """生成趋势预测"""
        # 基于分析结果确定趋势
        trend = self._determine_trend(analysis)
        
        # 计算置信度
        confidence = self._calculate_confidence(analysis)
        
        # 生成推理过程
        reasoning = self._generate_reasoning(analysis, trend)
        
        # 确定时间范围
        time_horizon = analysis.duration or "Short-term (1-7 days)"
        
        # 整理影响因素
        factors = analysis.key_factors + [f"Sentiment: {analysis.sentiment}"]
        
        return Prediction(
            id=f"pred-{uuid.uuid4().hex[:8]}",
            event_id=event.id,
            trend=trend,
            confidence=confidence,
            reasoning=reasoning,
            time_horizon=time_horizon,
            factors=factors
        )
    
    def _determine_trend(self, analysis: AnalysisModel) -> TrendDirection:
        """确定趋势方向"""
        sentiment = analysis.sentiment.lower()
        
        if "positive" in sentiment and "strongly" in sentiment:
            return TrendDirection.UP
        elif "positive" in sentiment:
            return TrendDirection.UP
        elif "negative" in sentiment and "strongly" in sentiment:
            return TrendDirection.DOWN
        elif "negative" in sentiment:
            return TrendDirection.DOWN
        else:
            return TrendDirection.SIDEWAYS
    
    def _calculate_confidence(self, analysis: AnalysisModel) -> float:
        """计算置信度"""
        # 基础置信度
        base_confidence = 0.5
        
        # 基于影响范围调整
        if analysis.impact_scope == "Global":
            base_confidence += 0.15
        elif analysis.impact_scope == "Regional":
            base_confidence += 0.1
        
        # 基于情绪强度调整
        if "strongly" in analysis.sentiment.lower():
            base_confidence += 0.15
        elif analysis.sentiment != "Neutral":
            base_confidence += 0.1
        
        # 基于关键因素数量
        if len(analysis.key_factors) >= 3:
            base_confidence += 0.1
        
        # 限制在0-1范围内
        return min(max(base_confidence, 0.3), 0.95)
    
    def _generate_reasoning(self, analysis: AnalysisModel, trend: TrendDirection) -> str:
        """生成推理过程"""
        trend_text = {
            TrendDirection.UP: "上涨",
            TrendDirection.DOWN: "下跌",
            TrendDirection.SIDEWAYS: "横盘",
            TrendDirection.UNCERTAIN: "不确定"
        }
        
        reasoning = f"""综合分析结果：

1. **趋势判断**: 基于市场情绪({analysis.sentiment})和影响范围({analysis.impact_scope})，预计走势{trend_text.get(trend, '不确定')}

2. **影响分析**: 
   - 影响范围: {analysis.impact_scope}
   - 持续时间: {analysis.duration}
   - 关键因素: {', '.join(analysis.key_factors[:3])}

3. **推理依据**:
   {analysis.insights}

4. **不确定性因素**:
   - 预测基于当前可用信息
   - 实际情况可能受突发事件影响
   - 建议结合多个数据源进行验证
"""
        return reasoning
    
    def _extract_event_from_collected(self, collected_info: CollectedInfoModel) -> Event:
        """从CollectedInfo中提取Event信息用于创建Prediction"""
        # 这是一个临时方法，在实际流程中event会被传递
        info = collected_info.basic_info
        return Event(
            id=f"evt-{uuid.uuid4().hex[:8]}",
            title=info.get("title", "Unknown"),
            description=info.get("description", ""),
            source=info.get("source", "unknown"),
            timestamp=info.get("timestamp", ""),
            category=info.get("category", "Other"),
            importance=info.get("importance", 3)
        )


class AgentPipeline:
    """AgentPipeline: 协调多个Agent完成预测流程"""
    
    def __init__(self):
        self.info_collector = InfoCollectorAgent()
        self.analyzer = AnalyzerAgent()
        self.predictor = PredictorAgent()
    
    def run(self, event: Event) -> Prediction:
        """运行完整的预测流程，返回预测结果"""
        # Step 1: 信息收集
        collected = self.info_collector.run(event)

        # Step 2: 深度分析
        analysis = self.analyzer.run(collected)

        # Step 3: 趋势预测
        prediction = self.predictor.run(analysis, event)

        return prediction

    def run_with_analysis(self, event: Event) -> tuple:
        """运行完整的预测流程，返回 (prediction, analysis)"""
        # Step 1: 信息收集
        collected = self.info_collector.run(event)

        # Step 2: 深度分析
        analysis = self.analyzer.run(collected)

        # Step 3: 趋势预测
        prediction = self.predictor.run(analysis, event)

        return prediction, analysis
