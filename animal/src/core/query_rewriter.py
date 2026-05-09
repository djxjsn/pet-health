"""
查询改写模块

将用户口语化查询改写为更适合知识库检索的形式，
支持同义词替换、句式转换、查询扩展等能力，
提升RAG系统的检索召回率。
"""
import re
import logging
from typing import List, Optional, Dict, Any

from src.core.config import get_settings

logger = logging.getLogger(__name__)

PET_SYNONYMS = {
    "狗": ["犬", "狗狗", "小狗", "爱犬", "宠物犬"],
    "猫": ["猫咪", "小猫", "爱猫", "宠物猫", "喵"],
    "犬": ["狗", "狗狗", "小狗", "爱犬"],
    "呕吐": ["吐", "恶心", "反胃", "干呕"],
    "拉肚子": ["腹泻", "拉稀", "便稀", "软便"],
    "发烧": ["发热", "体温高", "体温升高"],
    "咳嗽": ["咳", "干咳", "湿咳"],
    "不吃东西": ["食欲不振", "厌食", "拒食", "不进食"],
    "没精神": ["精神萎靡", "嗜睡", "乏力", "精神差"],
    "打喷嚏": ["喷嚏", "鼻塞", "流鼻涕"],
    "皮肤病": ["皮疹", "红疹", "脱毛", "瘙痒", "皮炎"],
    "疫苗": ["接种", "免疫", "打针"],
    "驱虫": ["除虫", "体内驱虫", "体外驱虫", "杀虫"],
    "绝育": ["去势", "结扎", "割蛋", "摘除"],
    "感冒": ["着凉", "受凉", "上呼吸道感染"],
}

DOMAIN_KEYWORDS = {
    "disease": ["疾病", "症状", "诊断", "治疗", "发病", "感染", "炎症", "病毒", "细菌"],
    "medication": ["药物", "用药", "剂量", "副作用", "处方", "药膏", "口服", "注射"],
    "nutrition": ["营养", "饮食", "喂食", "食物", "维生素", "蛋白质", "钙", "零食"],
    "first_aid": ["急救", "紧急", "中毒", "窒息", "出血", "骨折", "休克"],
    "behavior": ["行为", "训练", "习惯", "社交", "攻击", "焦虑", "恐惧"],
}

QUERY_INTENT_PATTERNS = [
    (r"(.+)怎么办|(.+)怎么处理|(.+)如何处理", "treatment"),
    (r"(.+)是什么|(.+)是什么原因|(.+)为什么", "diagnosis"),
    (r"(.+)能吃吗|(.+)可以喂吗|(.+)能不能", "nutrition"),
    (r"(.+)怎么预防|(.+)如何预防", "prevention"),
    (r"(.+)症状|(.+)表现|(.+)有什么症状", "symptom"),
]


class QueryRewriter:
    """查询改写器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.synonyms = PET_SYNONYMS
        self.domain_keywords = DOMAIN_KEYWORDS
        self.intent_patterns = QUERY_INTENT_PATTERNS
    
    def rewrite(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """改写查询
        
        Args:
            query: 原始查询
            context: 额外上下文（如宠物信息）
            
        Returns:
            改写后的查询
        """
        rewritten = query.strip()
        
        rewritten = self._expand_synonyms(rewritten)
        rewritten = self._normalize_colloquialisms(rewritten)
        rewritten = self._add_domain_context(rewritten)
        
        if context:
            rewritten = self._inject_context(rewritten, context)
        
        return rewritten
    
    def generate_multi_queries(self, query: str, num_variants: int = 3) -> List[str]:
        """生成多个查询变体，提升检索召回率
        
        Args:
            query: 原始查询
            num_variants: 变体数量
            
        Returns:
            查询变体列表（包含原始查询）
        """
        queries = [query]
        
        synonym_query = self._expand_synonyms(query)
        if synonym_query != query:
            queries.append(synonym_query)
        
        intent = self._detect_intent(query)
        if intent:
            intent_query = self._rewrite_by_intent(query, intent)
            if intent_query != query:
                queries.append(intent_query)
        
        simplified = self._simplify_query(query)
        if simplified != query and simplified not in queries:
            queries.append(simplified)
        
        return queries[:num_variants + 1]
    
    def _expand_synonyms(self, query: str) -> str:
        """同义词扩展"""
        expanded_parts = []
        for word, synonyms in self.synonyms.items():
            if word in query:
                primary_synonym = synonyms[0]
                if primary_synonym not in query:
                    expanded_parts.append((word, f"{word} {primary_synonym}"))
        
        result = query
        for original, expanded in expanded_parts:
            result = result.replace(original, expanded, 1)
        
        return result
    
    def _normalize_colloquialisms(self, query: str) -> str:
        """口语化表达规范化"""
        colloquial_map = {
            "不吃东西": "食欲不振",
            "不吃食": "食欲不振",
            "没精神": "精神萎靡",
            "没食欲": "食欲不振",
            "一直吐": "频繁呕吐",
            "老拉肚子": "慢性腹泻",
            "老是咳": "持续咳嗽",
            "喘不上气": "呼吸困难",
            "站不起来": "运动障碍",
            "一直挠": "频繁瘙痒",
        }
        
        result = query
        for colloquial, formal in colloquial_map.items():
            if colloquial in result:
                result = result.replace(colloquial, formal)
        
        return result
    
    def _add_domain_context(self, query: str) -> str:
        """添加领域上下文关键词"""
        for domain, keywords in self.domain_keywords.items():
            if any(kw in query for kw in keywords):
                if domain not in query:
                    domain_names = {
                        "disease": "疾病",
                        "medication": "用药",
                        "nutrition": "营养",
                        "first_aid": "急救",
                        "behavior": "行为"
                    }
                    if domain in domain_names and domain_names[domain] not in query:
                        pass
                break
        
        return query
    
    def _inject_context(self, query: str, context: Dict[str, Any]) -> str:
        """注入宠物上下文信息"""
        parts = []
        
        species = context.get("species")
        if species:
            parts.append(species)
        
        breed = context.get("breed")
        if breed:
            parts.append(breed)
        
        age = context.get("age_months")
        if age:
            if age <= 6:
                parts.append("幼年")
            elif age <= 24:
                parts.append("青年")
            else:
                parts.append("成年")
        
        if parts:
            context_prefix = " ".join(parts)
            if context_prefix not in query:
                query = f"{context_prefix} {query}"
        
        return query
    
    def _detect_intent(self, query: str) -> Optional[str]:
        """检测查询意图"""
        for pattern, intent in self.intent_patterns:
            if re.search(pattern, query):
                return intent
        return None
    
    def _rewrite_by_intent(self, query: str, intent: str) -> str:
        """根据意图改写查询"""
        intent_rewrites = {
            "treatment": f"{query} 治疗方案 处理方法",
            "diagnosis": f"{query} 病因 诊断",
            "nutrition": f"{query} 饮食 营养",
            "prevention": f"{query} 预防 措施",
            "symptom": f"{query} 症状表现 临床表现",
        }
        return intent_rewrites.get(intent, query)
    
    def _simplify_query(self, query: str) -> str:
        """简化查询，去除冗余词"""
        filler_words = ["请问", "我想知道", "帮我查一下", "能不能告诉我", "想了解"]
        result = query
        for filler in filler_words:
            result = result.replace(filler, "")
        return result.strip()


_query_rewriter: Optional[QueryRewriter] = None


def get_query_rewriter() -> QueryRewriter:
    """获取查询改写器实例（单例）"""
    global _query_rewriter
    if _query_rewriter is None:
        _query_rewriter = QueryRewriter()
    return _query_rewriter
