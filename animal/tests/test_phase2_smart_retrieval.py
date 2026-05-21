"""Phase 2 智能检索增强 - 集成测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestLLMQueryRewriter:
    """LLM查询改写器测试"""

    @pytest.fixture
    def mock_llm(self):
        mock = MagicMock()
        mock_response = MagicMock()
        mock_response.content = '{"rewritten": "狗 腹泻 排便异常", "intent": "symptom_diagnosis", "entities": ["腹泻"], "category": "disease"}'
        mock.invoke.return_value = mock_response
        return mock

    def test_rewrite_llm(self):
        with patch("src.core.llm_query_rewriter.LLMQueryRewriter._init_llm", return_value=None):
            from src.core.llm_query_rewriter import LLMQueryRewriter
            rw = LLMQueryRewriter()
            mock_llm = MagicMock()
            mock_resp = MagicMock()
            mock_resp.content = '{"rewritten":"狗 腹泻 排便异常","intent":"symptom_diagnosis","entities":["腹泻"],"category":"disease"}'
            mock_llm.invoke.return_value = mock_resp
            rw._llm = mock_llm
            rw._llm_available = True
            result = rw.rewrite("狗拉肚子怎么办")
            assert result["strategy"] == "llm"
            assert "腹泻" in result["rewritten"]
            assert result["category"] == "disease"

    def test_rewrite_fallback_rule(self):
        with patch("src.core.llm_query_rewriter.LLMQueryRewriter._init_llm", return_value=None):
            from src.core.llm_query_rewriter import LLMQueryRewriter
            rw = LLMQueryRewriter()
            rw._llm = None
            rw._llm_available = False
            result = rw.rewrite("狗拉肚子怎么办")
            assert result["strategy"] == "rule"
            assert isinstance(result["rewritten"], str)

    def test_generate_multi_queries_rule(self):
        with patch("src.core.llm_query_rewriter.LLMQueryRewriter._init_llm", return_value=None):
            from src.core.llm_query_rewriter import LLMQueryRewriter
            rw = LLMQueryRewriter()
            rw._llm = None
            rw._llm_available = False
            variants = rw.generate_multi_queries("狗拉肚子", "狗 腹泻", 3)
            assert isinstance(variants, list)

    def test_extract_json(self):
        from src.core.llm_query_rewriter import LLMQueryRewriter
        rw = LLMQueryRewriter()
        rw._llm_available = False
        assert '{"rewritten": "test"}' in rw._extract_json('json\n{"rewritten": "test"}')
        result = rw._extract_json('```json\n{"a": 1}\n```')
        assert "a" in result


class TestSelfRAG:
    """Self-RAG模块测试"""

    def test_default_retrieval_eval_with_results(self):
        from src.core.self_rag import SelfRAG
        rag = SelfRAG()
        rag._available = False
        results = [{"content": "狗腹泻常见原因", "distance": 0.15}]
        eval_result = rag.evaluate_retrieval("狗拉肚子", results)
        assert eval_result["strategy"] == "default"
        assert eval_result["is_relevant"] is True
        assert eval_result["sufficiency"] > 0.4

    def test_default_retrieval_eval_empty(self):
        from src.core.self_rag import SelfRAG
        rag = SelfRAG()
        rag._available = False
        eval_result = rag.evaluate_retrieval("狗拉肚子", [])
        assert eval_result["strategy"] == "default"
        assert eval_result["is_relevant"] is False
        assert eval_result["sufficiency"] == 0.0

    def test_default_generation_eval(self):
        from src.core.self_rag import SelfRAG
        rag = SelfRAG()
        rag._available = False
        eval_result = rag.evaluate_generation(
            [{"content": "犬瘟热是严重疾病"}],
            "犬瘟热是一种严重的犬类疾病"
        )
        assert eval_result["strategy"] == "default"
        assert eval_result["is_faithful"] is True

    def test_action_decisions(self):
        from src.core.self_rag import SelfRAG
        rag = SelfRAG()
        rag._available = False

        decision = rag.should_refuse_or_correct(
            {"is_relevant": True, "sufficiency": 0.8},
            {"is_faithful": True, "confidence": 0.9}
        )
        assert decision["action"] == "accept"

        decision = rag.should_refuse_or_correct(
            {"is_relevant": False, "sufficiency": 0.1},
            {"is_faithful": True, "confidence": 0.9}
        )
        assert decision["action"] == "refuse"

        decision = rag.should_refuse_or_correct(
            {"is_relevant": True, "sufficiency": 0.3},
            {"is_faithful": True, "confidence": 0.9}
        )
        assert decision["action"] == "supplement"


class TestCorrectiveRAG:
    """CRAG模块测试"""

    def test_high_confidence_accept(self):
        from src.core.corrective_rag import CorrectiveRAG
        crag = CorrectiveRAG()
        crag._web_available = False

        decision = crag.evaluate_and_correct(
            "狗拉肚子",
            [{"content": "狗腹泻常见原因有...", "distance": 0.2}],
            retrieval_eval={"is_relevant": True, "sufficiency": 0.8, "strategy": "llm"},
            generation_eval={"is_faithful": True, "confidence": 0.9, "strategy": "llm"},
        )
        assert decision["action"] == "accept"
        assert decision["confidence"] > 0.6

    def test_low_confidence_refuse(self):
        from src.core.corrective_rag import CorrectiveRAG
        crag = CorrectiveRAG()
        crag._web_available = False

        decision = crag.evaluate_and_correct(
            "复杂手术问题",
            [],
            retrieval_eval={"is_relevant": False, "sufficiency": 0.0, "strategy": "default"},
        )
        assert decision["action"] == "refuse"
        assert "refuse_message" in decision

    def test_compute_confidence_harmonic(self):
        from src.core.corrective_rag import CorrectiveRAG
        crag = CorrectiveRAG()
        conf = crag._compute_comprehensive_confidence(
            [{"content": "test", "distance": 0.2}],
            retrieval_eval={"is_relevant": True, "sufficiency": 0.9, "strategy": "llm"},
            generation_eval={"is_faithful": True, "confidence": 0.95, "strategy": "llm"},
        )
        assert 0.7 <= conf <= 1.0

    def test_no_eval_default_confidence(self):
        from src.core.corrective_rag import CorrectiveRAG
        crag = CorrectiveRAG()
        conf = crag._compute_comprehensive_confidence(
            [{"content": "test", "distance": 0.3}]
        )
        assert 0.2 <= conf <= 0.5


class TestRAGPromptsPhase2:
    """Phase 2 提示词测试"""

    def test_self_rag_prompts_exist(self):
        from src.core import rag_prompts
        assert hasattr(rag_prompts, 'SELF_RAG_RETRIEVAL_EVAL_PROMPT')
        assert hasattr(rag_prompts, 'SELF_RAG_GENERATION_CORRECTION_PROMPT')
        assert hasattr(rag_prompts, 'RAG_REFUSE_PROMPT')

    def test_rag_refuse_prompt_format(self):
        from src.core.rag_prompts import RAG_REFUSE_PROMPT
        formatted = RAG_REFUSE_PROMPT.format(query="测试问题")
        assert "测试问题" in formatted
        assert "面诊" in formatted
        assert "emoji" in formatted or "推荐" in formatted