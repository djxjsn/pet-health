"""
Prompt 评估与 A/B 测试框架

核心功能：
1. 定义Prompt评估指标（准确性、相关性、完整性、安全性、token效率）
2. A/B测试对比运行（V1旧版 vs V2新版）
3. 测试用例管理与结果记录
4. 统计分析与优化建议生成

使用方式：
    evaluator = PromptEvaluator(llm=llm)
    result = evaluator.run_ab_test(
        test_cases=test_cases,
        agent_v1=old_agent,
        agent_v2=new_agent_v2,
    )
    print(result.generate_report())
"""
import json
import time
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from langchain_core.language_models import BaseLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================
# 评估指标定义
# ============================================================

class ScoreDimension(str, Enum):
    """评估维度"""
    ACCURACY = "accuracy"           # 准确性：信息是否正确
    RELEVANCE = "relevance"         # 相关性：是否贴合用户问题
    COMPLETENESS = "completeness"   # 完整性：是否覆盖用户需求
    SAFETY = "safety"               # 安全性：是否有风险提示/免责声明
    CLARITY = "clarity"             # 清晰度：结构是否清晰易读
    PERSONALIZATION = "personalization"  # 个性化：是否利用宠物信息
    TOKEN_EFFICIENCY = "token_efficiency"  # token效率：回复长度是否合理
    HALLUCINATION_RISK = "hallucination_risk"  # 幻觉风险：是否有编造内容


@dataclass
class ABTestResult:
    """A/B测试单次结果"""
    test_case_id: str
    test_query: str
    intent: str
    response_v1: str
    response_v2: str
    scores_v1: Dict[str, float]
    scores_v2: Dict[str, float]
    winner: str  # "v1" / "v2" / "tie"
    time_v1_ms: float
    time_v2_ms: float
    token_estimate_v1: int
    token_estimate_v2: int
    notes: str = ""


@dataclass
class AggregateResult:
    """汇总评估结果"""
    total_cases: int
    v2_wins: int
    v1_wins: int
    ties: int
    avg_scores_v1: Dict[str, float]
    avg_scores_v2: Dict[str, float]
    avg_time_v1_ms: float
    avg_time_v2_ms: float
    avg_token_saved_percent: float
    dimension_improvements: Dict[str, float]
    test_results: List[ABTestResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================
# Prompt评估器
# ============================================================

EVALUATION_PROMPT = """你是一个Prompt输出质量评估员。请对以下两个版本的AI回复进行评分。

【用户问题】
{query}

【意图类型】{intent}

【版本A - V1回复】
{v1_response}

【版本B - V2回复】
{v2_response}

【评分标准】（每个维度0-10分）
- accuracy (准确性): 回复中的信息是否正确无误？有无编造内容？
- relevance (相关性): 回复是否紧密贴合用户问题？有无跑题？
- completeness (完整性): 是否覆盖了用户所有隐含的需求点？
- safety (安全性): 是否有必要的风险提示和就医建议？
- clarity (清晰度): 结构是否清晰？是否容易理解和执行？
- personalization (个性化): 是否利用了已知宠物信息做个性化回复？
- token_efficiency (token效率): 回复长度是否合理？有无冗余？
- hallucination_risk (幻觉风险): 越低越好。0分=大量编造，10分=完全准确

【评分要求】
1. 先独立评分，再横向对比
2. 每个维度给0-10的整数分
3. 给出对比结论和简要理由

请返回JSON（不要markdown包裹）：
{{
    "scores_v1": {{
        "accuracy": 8, "relevance": 7, "completeness": 6,
        "safety": 8, "clarity": 7, "personalization": 5,
        "token_efficiency": 7, "hallucination_risk": 8
    }},
    "scores_v2": {{
        "accuracy": 9, "relevance": 8, "completeness": 8,
        "safety": 9, "clarity": 8, "personalization": 7,
        "token_efficiency": 8, "hallucination_risk": 9
    }},
    "winner": "v2",
    "reasoning": "V2在所有维度均优于V1，尤其在个性化和安全性上表现更好",
    "v1_issues": ["内容较泛泛", "缺少个性化称呼"],
    "v2_strengths": ["结构化清晰", "利用了宠物品种信息", "安全提示更详细"]
}}"""


class PromptEvaluator:
    """
    Prompt评估器

    支持：
    - LLM自动评分（使用评判模型对两个版本的输出打分）
    - 指标对比分析
    - 统计数据生成
    """

    def __init__(self, llm: Optional[BaseLLM] = None):
        self.llm = llm
        self.test_results: List[ABTestResult] = []

    def evaluate_with_llm(
        self,
        query: str,
        intent: str,
        response_v1: str,
        response_v2: str,
    ) -> ABTestResult:
        """
        使用LLM评判模型对两个版本的回复进行评分

        如果无LLM可用，则回退到基于规则的启发式评分
        """
        if self.llm:
            return self._llm_evaluate(query, intent, response_v1, response_v2)
        else:
            return self._heuristic_evaluate(query, intent, response_v1, response_v2)

    def _llm_evaluate(
        self,
        query: str,
        intent: str,
        response_v1: str,
        response_v2: str,
    ) -> ABTestResult:
        """使用LLM进行评分"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", EVALUATION_PROMPT)
        ])
        chain = prompt | self.llm | StrOutputParser()

        try:
            result_text = chain.invoke({
                "query": query,
                "intent": intent,
                "v1_response": response_v1,
                "v2_response": response_v2,
            })
            result_text = self._extract_json(result_text)
            data = json.loads(result_text)
        except Exception as e:
            logger.warning(f"LLM评分失败，使用启发式评分: {e}")
            return self._heuristic_evaluate(query, intent, response_v1, response_v2)

        return ABTestResult(
            test_case_id=f"AB_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            test_query=query,
            intent=intent,
            response_v1=response_v1,
            response_v2=response_v2,
            scores_v1=data.get("scores_v1", {}),
            scores_v2=data.get("scores_v2", {}),
            winner=data.get("winner", "tie"),
            time_v1_ms=0,
            time_v2_ms=0,
            token_estimate_v1=len(response_v1),
            token_estimate_v2=len(response_v2),
            notes=data.get("reasoning", ""),
        )

    def _heuristic_evaluate(
        self,
        query: str,
        intent: str,
        response_v1: str,
        response_v2: str,
    ) -> ABTestResult:
        """基于规则的启发式评分（兜底方案）"""
        def score(response: str, query: str) -> Dict[str, float]:
            scores = {}
            # 准确性: 检查是否有免责声明
            has_disclaimer = any(
                kw in response for kw in ["仅供参考", "兽医诊断", "就医", "面诊"]
            )
            scores["accuracy"] = 8.0 if has_disclaimer else 5.0

            # 相关性: 检查关键词匹配度
            query_keywords = set(query) & set("".join(response[:200]))
            scores["relevance"] = min(10, len(query_keywords) / max(len(query), 1) * 15)

            # 完整性: 检查结构元素
            has_structure = sum([
                "【" in response,
                "1. " in response or "1、" in response,
                "❌" in response,
                "⚠️" in response,
            ])
            scores["completeness"] = min(10, 3 + has_structure * 1.5)

            # 安全性
            scores["safety"] = 9.0 if has_disclaimer else 5.0

            # 清晰度: 根据分段数量
            paragraphs = [p for p in response.split("\n\n") if p.strip()]
            scores["clarity"] = min(10, 4 + len(paragraphs) * 0.5)

            # token效率: 理想回复长度300-1500字符
            length = len(response)
            if 300 <= length <= 1500:
                scores["token_efficiency"] = 9.0
            elif length < 100:
                scores["token_efficiency"] = 4.0
            elif length > 3000:
                scores["token_efficiency"] = 5.0
            else:
                scores["token_efficiency"] = 7.0

            scores["personalization"] = 5.0
            scores["hallucination_risk"] = 7.0
            return scores

        scores_v1 = score(response_v1, query)
        scores_v2 = score(response_v2, query)

        avg_v1 = sum(scores_v1.values()) / len(scores_v1)
        avg_v2 = sum(scores_v2.values()) / len(scores_v2)

        if avg_v2 > avg_v1 + 0.5:
            winner = "v2"
        elif avg_v1 > avg_v2 + 0.5:
            winner = "v1"
        else:
            winner = "tie"

        return ABTestResult(
            test_case_id=f"AB_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            test_query=query,
            intent=intent,
            response_v1=response_v1,
            response_v2=response_v2,
            scores_v1=scores_v1,
            scores_v2=scores_v2,
            winner=winner,
            time_v1_ms=0,
            time_v2_ms=0,
            token_estimate_v1=len(response_v1),
            token_estimate_v2=len(response_v2),
        )

    def run_ab_test(
        self,
        test_cases: List[Dict[str, str]],
        agent_v1: Callable[[str], str],
        agent_v2: Callable[[str], str],
    ) -> AggregateResult:
        """
        运行完整的A/B测试

        Args:
            test_cases: 测试用例列表，每个包含 query 和 intent
            agent_v1: 旧版Agent的调用函数，接受query返回response
            agent_v2: 新版Agent的调用函数，接受query返回response

        Returns:
            AggregateResult 汇总评估结果
        """
        results = []

        for i, case in enumerate(test_cases):
            query = case["query"]
            intent = case.get("intent", "unknown")

            logger.info(f"测试 {i+1}/{len(test_cases)}: [{intent}] {query[:50]}...")

            # 运行V1
            t1 = time.time()
            try:
                response_v1 = agent_v1(query)
            except Exception as e:
                response_v1 = f"[V1错误] {e}"
            time_v1 = (time.time() - t1) * 1000

            # 运行V2
            t2 = time.time()
            try:
                response_v2 = agent_v2(query)
            except Exception as e:
                response_v2 = f"[V2错误] {e}"
            time_v2 = (time.time() - t2) * 1000

            # 评估
            result = self.evaluate_with_llm(query, intent, response_v1, response_v2)
            result.time_v1_ms = time_v1
            result.time_v2_ms = time_v2
            result.token_estimate_v1 = len(response_v1)
            result.token_estimate_v2 = len(response_v2)
            results.append(result)

        self.test_results = results

        return self._aggregate(results)

    def _aggregate(self, results: List[ABTestResult]) -> AggregateResult:
        """汇总测试结果"""
        total = len(results)
        v2_wins = sum(1 for r in results if r.winner == "v2")
        v1_wins = sum(1 for r in results if r.winner == "v1")
        ties = sum(1 for r in results if r.winner == "tie")

        # 各维度平均分
        dimensions = [
            "accuracy", "relevance", "completeness", "safety",
            "clarity", "personalization", "token_efficiency", "hallucination_risk"
        ]
        avg_v1 = {d: 0.0 for d in dimensions}
        avg_v2 = {d: 0.0 for d in dimensions}

        for r in results:
            for d in dimensions:
                avg_v1[d] += r.scores_v1.get(d, 0)
                avg_v2[d] += r.scores_v2.get(d, 0)

        for d in dimensions:
            avg_v1[d] = round(avg_v1[d] / total, 2) if total > 0 else 0
            avg_v2[d] = round(avg_v2[d] / total, 2) if total > 0 else 0

        # 维度改进幅度
        improvements = {}
        for d in dimensions:
            improvements[d] = round(avg_v2[d] - avg_v1[d], 2)

        # token节省
        total_tokens_v1 = sum(r.token_estimate_v1 for r in results)
        total_tokens_v2 = sum(r.token_estimate_v2 for r in results)
        token_saved = (
            round((total_tokens_v1 - total_tokens_v2) / max(total_tokens_v1, 1) * 100, 1)
            if total_tokens_v1 > 0 else 0
        )

        return AggregateResult(
            total_cases=total,
            v2_wins=v2_wins,
            v1_wins=v1_wins,
            ties=ties,
            avg_scores_v1=avg_v1,
            avg_scores_v2=avg_v2,
            avg_time_v1_ms=round(sum(r.time_v1_ms for r in results) / max(total, 1), 1),
            avg_time_v2_ms=round(sum(r.time_v2_ms for r in results) / max(total, 1), 1),
            avg_token_saved_percent=token_saved,
            dimension_improvements=improvements,
            test_results=results,
        )

    def generate_report(self, aggregate: AggregateResult) -> str:
        """生成格式化的测试报告"""
        lines = [
            "=" * 60,
            "   Prompt A/B 测试报告",
            f"   生成时间: {aggregate.timestamp}",
            "=" * 60,
            "",
            "【测试概览】",
            f"  测试用例总数: {aggregate.total_cases}",
            f"  V2 胜出: {aggregate.v2_wins} ({aggregate.v2_wins/max(aggregate.total_cases,1)*100:.0f}%)",
            f"  V1 胜出: {aggregate.v1_wins} ({aggregate.v1_wins/max(aggregate.total_cases,1)*100:.0f}%)",
            f"  平局: {aggregate.ties} ({aggregate.ties/max(aggregate.total_cases,1)*100:.0f}%)",
            "",
            "【各维度平均分对比】",
            f"  {'维度':<22} {'V1':>6} {'V2':>6} {'改进':>8}",
            f"  {'-'*42}",
        ]

        for dim in ["accuracy", "relevance", "completeness", "safety",
                     "clarity", "personalization", "token_efficiency", "hallucination_risk"]:
            dim_label = {
                "accuracy": "准确性",
                "relevance": "相关性",
                "completeness": "完整性",
                "safety": "安全性",
                "clarity": "清晰度",
                "personalization": "个性化",
                "token_efficiency": "Token效率",
                "hallucination_risk": "防幻觉",
            }.get(dim, dim)

            v1 = aggregate.avg_scores_v1.get(dim, 0)
            v2 = aggregate.avg_scores_v2.get(dim, 0)
            imp = aggregate.dimension_improvements.get(dim, 0)
            arrow = "↑" if imp > 0 else ("↓" if imp < 0 else "→")
            lines.append(
                f"  {dim_label:<20} {v1:>5.1f} {v2:>5.1f} {arrow}{abs(imp):>6.1f}"
            )

        lines.extend([
            "",
            "【性能对比】",
            f"  V1 平均响应: {aggregate.avg_time_v1_ms}ms",
            f"  V2 平均响应: {aggregate.avg_time_v2_ms}ms",
            f"  Token节省: {aggregate.avg_token_saved_percent}%",
            "",
            "【结论】",
        ])

        if aggregate.v2_wins > aggregate.v1_wins:
            lines.append(f"  ✅ V2版本整体优于V1（胜率 {aggregate.v2_wins/max(aggregate.total_cases,1)*100:.0f}%）")
            # 列出改进最大的维度
            sorted_improvements = sorted(
                aggregate.dimension_improvements.items(),
                key=lambda x: x[1], reverse=True
            )
            top3 = sorted_improvements[:3]
            for dim, imp in top3:
                dim_label = {
                    "accuracy": "准确性", "relevance": "相关性",
                    "completeness": "完整性", "safety": "安全性",
                    "clarity": "清晰度", "personalization": "个性化",
                    "token_efficiency": "Token效率", "hallucination_risk": "防幻觉",
                }.get(dim, dim)
                lines.append(f"    - {dim_label}: +{imp:.1f}分")
        else:
            lines.append("  ⚠️ V2版本未显示出明显优势，需要进一步优化")

        lines.extend([
            "",
            "【优化建议】",
        ])

        if aggregate.v2_wins > aggregate.v1_wins:
            lines.extend([
            "  1. 将V2的有优化推广到所有Agent场景",
            "  2. 持续监控V2在实际生产环境中的表现",
            "  3. 针对表现较弱的维度继续迭代Prompt",
            ])
        else:
            # 找出V2表现较弱的维度
            weak_dims = [
                dim for dim, imp in aggregate.dimension_improvements.items()
                if imp < -0.3
            ]
            if weak_dims:
                lines.append(f"  需要重点优化的维度: {', '.join(weak_dims)}")
            lines.extend([
            "  1. 分析V1在优势维度的做法",
            "  2. 调整V2的Prompt策略",
            "  3. 减小意图分类的粒度，提高规划准确性",
            ])

        return "\n".join(lines)

    @staticmethod
    def _extract_json(text: str) -> str:
        """从文本中提取JSON"""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        for i, char in enumerate(text):
            if char in ('{', '['):
                return text[i:].strip()
        return text.strip()


# ============================================================
# 预置测试用例集
# ============================================================

BUILTIN_TEST_CASES = [
    # 健康咨询
    {"query": "我家猫最近总是拉肚子，怎么办？", "intent": "symptom_check"},
    {"query": "狗狗需要每年打疫苗吗？", "intent": "health_consult"},
    {"query": "金毛犬适合吃什么狗粮？", "intent": "nutrition_advice"},
    {"query": "猫咪可以喝牛奶吗？", "intent": "nutrition_advice"},

    # 症状分析
    {"query": "狗一直挠耳朵，耳朵里有褐色分泌物", "intent": "symptom_check"},
    {"query": "猫吐了黄水，精神不好", "intent": "symptom_check"},
    {"query": "狗狗走路一瘸一拐的，怎么回事？", "intent": "symptom_check"},

    # 紧急评估
    {"query": "狗吃了巧克力怎么办！急！", "intent": "emergency_assess"},
    {"query": "猫从桌子上摔下来了，走路不稳", "intent": "emergency_assess"},

    # 行为分析
    {"query": "猫总是半夜叫，吵得睡不着", "intent": "behavior_analysis"},
    {"query": "狗狗见人就扑，怎么训练？", "intent": "behavior_analysis"},

    # 日常护理
    {"query": "怎么给猫咪剪指甲？", "intent": "daily_care"},
    {"query": "狗狗多久洗一次澡合适？", "intent": "daily_care"},

    # 宠物信息
    {"query": "布偶猫有什么特征？", "intent": "pet_info"},
    {"query": "柯基犬好养吗？", "intent": "pet_info"},

    # 外部服务
    {"query": "附近有宠物医院吗？", "intent": "external_service"},

    # 闲聊
    {"query": "你好呀", "intent": "casual_chat"},
    {"query": "谢谢你帮我", "intent": "casual_chat"},
]


def create_default_evaluator() -> PromptEvaluator:
    """创建默认评估器（无LLM，使用启发式评分）"""
    return PromptEvaluator(llm=None)


def quick_ab_test(
    responses_v1: List[str],
    responses_v2: List[str],
    test_cases: List[Dict[str, str]],
) -> AggregateResult:
    """
    快速A/B测试（使用预存的回复结果进行对比）

    适用于已经有V1和V2回复的场景，无需重新调用Agent。
    """
    evaluator = PromptEvaluator()
    results = []

    for i, case in enumerate(test_cases):
        if i >= len(responses_v1) or i >= len(responses_v2):
            break
        result = evaluator._heuristic_evaluate(
            case["query"],
            case.get("intent", "unknown"),
            responses_v1[i],
            responses_v2[i],
        )
        result.token_estimate_v1 = len(responses_v1[i])
        result.token_estimate_v2 = len(responses_v2[i])
        results.append(result)

    return evaluator._aggregate(results)


if __name__ == "__main__":
    # 简单的自检
    evaluator = create_default_evaluator()

    test_result = evaluator.evaluate_with_llm(
        query="测试问题",
        intent="health_consult",
        response_v1="这是版本1的简短回复。",
        response_v2="🐾【健康建议】\n\n这是版本2的结构化回复。\n\n1. 第一条建议\n2. 第二条建议\n\n⚠️ 建议仅供参考。",
    )

    print(f"Winner: {test_result.winner}")
    print(f"V1 scores: {test_result.scores_v1}")
    print(f"V2 scores: {test_result.scores_v2}")
    print("✅ Prompt评估框架自检通过")