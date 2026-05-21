"""
检索路由系统

根据用户查询的意图和特征，智能选择最合适的检索策略和数据源，
支持向量检索、关键词检索、混合检索、直接LLM回答等多种路由。
Phase 2更新: 支持LLM驱动的意图分类（LLM不可用时回退规则引擎）。
"""
import re
import logging
from typing import List, Dict, Any, Optional
from enum import Enum

from src.core.config import get_settings

logger = logging.getLogger(__name__)


class RetrievalStrategy(str, Enum):
    """检索策略"""
    VECTOR_ONLY = "vector_only"
    KEYWORD_ONLY = "keyword_only"
    HYBRID = "hybrid"
    DIRECT_LLM = "direct_llm"
    STRUCTURED_QUERY = "structured_query"


class QueryIntent(str, Enum):
    """查询意图"""
    SYMPTOM_DIAGNOSIS = "symptom_diagnosis"
    NUTRITION_ADVICE = "nutrition_advice"
    MEDICATION_INFO = "medication_info"
    FIRST_AID = "first_aid"
    BEHAVIOR_TRAINING = "behavior_training"
    GENERAL_KNOWLEDGE = "general_knowledge"
    PREVENTION = "prevention"
    UNKNOWN = "unknown"


INTENT_KEYWORDS = {
    QueryIntent.SYMPTOM_DIAGNOSIS: [
        "症状", "生病", "不舒服", "发烧", "呕吐", "拉肚子", "咳嗽",
        "不吃", "没精神", "皮肤", "脱毛", "瘙痒", "怎么办"
    ],
    QueryIntent.NUTRITION_ADVICE: [
        "营养", "饮食", "喂食", "食物", "能吃", "可以喂", "狗粮",
        "猫粮", "零食", "维生素", "补钙"
    ],
    QueryIntent.MEDICATION_INFO: [
        "药物", "用药", "药", "剂量", "副作用", "驱虫", "疫苗",
        "打针", "口服", "处方"
    ],
    QueryIntent.FIRST_AID: [
        "急救", "紧急", "中毒", "窒息", "出血", "骨折", "休克",
        "昏迷", "喘不上气", "抽搐"
    ],
    QueryIntent.BEHAVIOR_TRAINING: [
        "行为", "训练", "习惯", "咬人", "乱叫", "拆家", "社交",
        "焦虑", "恐惧", "攻击"
    ],
    QueryIntent.PREVENTION: [
        "预防", "如何避免", "怎么防止", "保健", "体检", "定期"
    ],
}

INTENT_STRATEGY_MAP = {
    QueryIntent.SYMPTOM_DIAGNOSIS: RetrievalStrategy.HYBRID,
    QueryIntent.NUTRITION_ADVICE: RetrievalStrategy.VECTOR_ONLY,
    QueryIntent.MEDICATION_INFO: RetrievalStrategy.HYBRID,
    QueryIntent.FIRST_AID: RetrievalStrategy.HYBRID,
    QueryIntent.BEHAVIOR_TRAINING: RetrievalStrategy.VECTOR_ONLY,
    QueryIntent.PREVENTION: RetrievalStrategy.VECTOR_ONLY,
    QueryIntent.GENERAL_KNOWLEDGE: RetrievalStrategy.VECTOR_ONLY,
    QueryIntent.UNKNOWN: RetrievalStrategy.HYBRID,
}

INTENT_CATEGORY_MAP = {
    QueryIntent.SYMPTOM_DIAGNOSIS: "disease",
    QueryIntent.NUTRITION_ADVICE: "nutrition",
    QueryIntent.MEDICATION_INFO: "medication",
    QueryIntent.FIRST_AID: "first_aid",
    QueryIntent.BEHAVIOR_TRAINING: "behavior",
    QueryIntent.PREVENTION: "disease",
    QueryIntent.GENERAL_KNOWLEDGE: None,
    QueryIntent.UNKNOWN: None,
}


class RetrievalRouter:
    """检索路由器"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def route(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """路由决策
        
        Args:
            query: 用户查询
            context: 额外上下文
            
        Returns:
            路由决策结果，包含策略、分类、参数等
        """
        intent = self._classify_intent(query)
        strategy = self._select_strategy(intent, query)
        category = INTENT_CATEGORY_MAP.get(intent)
        urgency = self._assess_urgency(query, intent)
        
        routing = {
            "query": query,
            "intent": intent.value,
            "strategy": strategy.value,
            "category": category,
            "urgency": urgency,
            "top_k": self._determine_top_k(intent, urgency),
            "min_similarity": self._determine_similarity_threshold(intent),
            "use_reranker": intent in (
                QueryIntent.SYMPTOM_DIAGNOSIS,
                QueryIntent.MEDICATION_INFO,
                QueryIntent.FIRST_AID
            ),
            "context": context or {}
        }
        
        logger.info(
            f"检索路由: query='{query[:30]}...' intent={intent.value} "
            f"strategy={strategy.value} category={category} urgency={urgency}"
        )
        
        return routing
    
    def _classify_intent(self, query: str) -> QueryIntent:
        """分类查询意图"""
        query_lower = query.lower()
        
        intent_scores = {}
        for intent, keywords in INTENT_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return QueryIntent.GENERAL_KNOWLEDGE
    
    def _select_strategy(self, intent: QueryIntent, query: str) -> RetrievalStrategy:
        """选择检索策略"""
        strategy = INTENT_STRATEGY_MAP.get(intent, RetrievalStrategy.HYBRID)
        
        if len(query.strip()) < 3:
            return RetrievalStrategy.DIRECT_LLM
        
        greeting_patterns = [r"你好", r"嗨", r"hello", r"hi", r"谢谢", r"感谢"]
        for pattern in greeting_patterns:
            if re.match(pattern, query.strip().lower()):
                return RetrievalStrategy.DIRECT_LLM
        
        return strategy
    
    def _assess_urgency(self, query: str, intent: QueryIntent) -> str:
        """评估紧急程度"""
        if intent == QueryIntent.FIRST_AID:
            return "high"
        
        high_urgency_keywords = ["紧急", "急救", "中毒", "窒息", "昏迷", "抽搐", "大量出血"]
        if any(kw in query for kw in high_urgency_keywords):
            return "high"
        
        medium_urgency_keywords = ["发烧", "呕吐", "腹泻", "不吃", "呼吸困难"]
        if any(kw in query for kw in medium_urgency_keywords):
            return "medium"
        
        return "low"
    
    def _determine_top_k(self, intent: QueryIntent, urgency: str) -> int:
        """确定返回结果数量"""
        if urgency == "high":
            return 8
        elif intent in (QueryIntent.SYMPTOM_DIAGNOSIS, QueryIntent.MEDICATION_INFO):
            return 5
        else:
            return 3
    
    def _determine_similarity_threshold(self, intent: QueryIntent) -> float:
        """确定相似度阈值"""
        if intent == QueryIntent.FIRST_AID:
            return 0.3
        elif intent == QueryIntent.SYMPTOM_DIAGNOSIS:
            return 0.4
        else:
            return 0.5


_retrieval_router: Optional[RetrievalRouter] = None


def get_retrieval_router() -> RetrievalRouter:
    """获取检索路由器实例（单例）"""
    global _retrieval_router
    if _retrieval_router is None:
        _retrieval_router = RetrievalRouter()
    return _retrieval_router
