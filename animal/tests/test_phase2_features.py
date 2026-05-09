"""
Phase 2 功能测试

验证P1质量提升的正确性：
1. 中文嵌入模型配置
2. 相似度阈值动态调整
3. RAG提示词模板
4. 查询改写功能
"""
import pytest
from unittest.mock import Mock, MagicMock, patch


class TestChineseEmbeddingModel:
    """中文嵌入模型配置测试"""

    def test_default_model_is_chinese(self):
        """验证默认嵌入模型为中文优化模型"""
        from src.core.config import Settings
        settings = Settings()
        assert settings.EMBEDDING_MODEL == "BAAI/bge-small-zh-v1.5"

    def test_embedding_dimension_config(self):
        """验证嵌入维度配置"""
        from src.core.config import Settings
        settings = Settings()
        assert settings.EMBEDDING_DIMENSION == 512

    def test_similarity_threshold_config(self):
        """验证相似度阈值配置"""
        from src.core.config import Settings
        settings = Settings()
        assert settings.SIMILARITY_THRESHOLD == 0.5

    def test_search_top_k_config(self):
        """验证搜索top_k配置"""
        from src.core.config import Settings
        settings = Settings()
        assert settings.SEARCH_TOP_K == 5

    def test_overretrieval_factor_config(self):
        """验证过度检索因子配置"""
        from src.core.config import Settings
        settings = Settings()
        assert settings.SEARCH_OVERRETRIEVAL_FACTOR == 2


class TestSimilarityThreshold:
    """相似度阈值动态调整测试"""

    @pytest.fixture
    def mock_retriever(self):
        """创建mock检索器"""
        with patch('src.core.knowledge_retriever.get_vector_db') as mock_vdb, \
             patch('src.core.knowledge_retriever.get_query_rewriter') as mock_qr:
            mock_vdb_instance = Mock()
            mock_vdb_instance.is_available = True
            mock_vdb.return_value = mock_vdb_instance
            
            mock_qr_instance = Mock()
            mock_qr_instance.rewrite.side_effect = lambda q: q
            mock_qr_instance.generate_multi_queries.side_effect = lambda q, num_variants=2: [q]
            mock_qr.return_value = mock_qr_instance

            from src.core.knowledge_retriever import KnowledgeRetriever
            retriever = KnowledgeRetriever(enable_query_rewrite=True)
            retriever.vector_db = mock_vdb_instance
            retriever._query_rewriter = mock_qr_instance
            return retriever

    def test_default_threshold_applied(self, mock_retriever):
        """验证默认相似度阈值被应用"""
        mock_results = {
            'documents': [['高相关', '低相关']],
            'metadatas': [[{}, {}]],
            'distances': [[0.1, 0.9]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search(query="测试")

        assert all(r['distance'] <= 0.5 for r in results)

    def test_custom_threshold_override(self, mock_retriever):
        """验证自定义阈值覆盖默认值"""
        mock_results = {
            'documents': [['高相关', '中等相关', '低相关']],
            'metadatas': [[{}, {}, {}]],
            'distances': [[0.1, 0.3, 0.6]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search(query="测试", min_similarity=0.7)

        assert all(r['distance'] <= 0.3 for r in results)

    def test_zero_threshold_returns_all(self, mock_retriever):
        """验证阈值为0时返回所有结果"""
        mock_results = {
            'documents': [['结果1', '结果2', '结果3']],
            'metadatas': [[{}, {}, {}]],
            'distances': [[0.1, 0.5, 0.9]]
        }
        mock_retriever.vector_db.query.return_value = mock_results

        results = mock_retriever.search(query="测试", min_similarity=0.0)

        assert len(results) == 3


class TestRAGPromptTemplates:
    """RAG提示词模板测试"""

    def test_format_context_with_results(self):
        """验证检索结果格式化"""
        from src.core.rag_prompts import format_context
        
        results = [
            {"content": "犬瘟热是一种病毒性疾病", "metadata": {"category": "disease"}, "distance": 0.1},
            {"content": "细小病毒感染常见于幼犬", "metadata": {"category": "disease"}, "distance": 0.2}
        ]
        
        context = format_context(results)
        assert "犬瘟热" in context
        assert "细小病毒" in context
        assert "[分类: disease]" in context
        assert "[相关度:" in context

    def test_format_context_empty_results(self):
        """验证空检索结果格式化"""
        from src.core.rag_prompts import format_context
        
        context = format_context([])
        assert "无可用参考资料" in context

    def test_build_rag_prompt_with_context(self):
        """验证RAG提示词构建（有上下文）"""
        from src.core.rag_prompts import build_rag_prompt
        
        results = [
            {"content": "犬瘟热症状", "metadata": {"category": "disease"}, "distance": 0.1}
        ]
        
        prompt = build_rag_prompt(query="狗发烧怎么办", retrieved_results=results)
        
        assert "狗发烧怎么办" in prompt
        assert "犬瘟热症状" in prompt
        assert "参考资料" in prompt
        assert "咨询专业兽医" in prompt

    def test_build_rag_prompt_without_context(self):
        """验证RAG提示词构建（无上下文）"""
        from src.core.rag_prompts import build_rag_prompt
        
        prompt = build_rag_prompt(query="狗发烧怎么办")
        
        assert "狗发烧怎么办" in prompt
        assert "无可用参考资料" in prompt

    def test_build_direct_response_prompt(self):
        """验证直接响应提示词构建"""
        from src.core.rag_prompts import build_direct_response_prompt
        
        prompt = build_direct_response_prompt(query="猫能吃巧克力吗")
        
        assert "猫能吃巧克力吗" in prompt
        assert "局限性" in prompt
        assert "咨询专业兽医" in prompt

    def test_build_integrate_prompt(self):
        """验证工具结果整合提示词构建"""
        from src.core.rag_prompts import build_integrate_prompt
        
        prompt = build_integrate_prompt(
            query="狗发烧",
            tool_results='{"possible_conditions": [{"description": "犬瘟热"}]}'
        )
        
        assert "狗发烧" in prompt
        assert "犬瘟热" in prompt
        assert "工具执行结果" in prompt
        assert "咨询专业兽医" in prompt


class TestQueryRewriter:
    """查询改写功能测试"""

    @pytest.fixture
    def rewriter(self):
        from src.core.query_rewriter import QueryRewriter
        return QueryRewriter()

    def test_synonym_expansion(self, rewriter):
        """验证同义词扩展"""
        result = rewriter.rewrite("狗呕吐")
        assert "犬" in result or "狗" in result

    def test_colloquialism_normalization(self, rewriter):
        """验证口语化表达规范化"""
        result = rewriter.rewrite("猫不吃东西")
        assert "食欲不振" in result

    def test_context_injection(self, rewriter):
        """验证上下文注入"""
        context = {"species": "狗", "breed": "金毛", "age_months": 6}
        result = rewriter.rewrite("发烧", context=context)
        assert "狗" in result
        assert "金毛" in result
        assert "幼年" in result

    def test_multi_query_generation(self, rewriter):
        """验证多查询变体生成"""
        queries = rewriter.generate_multi_queries("狗拉肚子怎么办", num_variants=3)
        assert len(queries) >= 2
        assert "狗拉肚子怎么办" in queries

    def test_intent_detection(self, rewriter):
        """验证意图检测"""
        intent = rewriter._detect_intent("狗发烧怎么办")
        assert intent == "treatment"

    def test_intent_detection_symptom(self, rewriter):
        """验证症状意图检测"""
        intent = rewriter._detect_intent("犬瘟热有什么症状")
        assert intent == "symptom"

    def test_simplify_query(self, rewriter):
        """验证查询简化"""
        result = rewriter._simplify_query("请问狗发烧怎么办")
        assert "请问" not in result
        assert "狗发烧怎么办" in result

    def test_rewrite_preserves_core_meaning(self, rewriter):
        """验证改写保留核心语义"""
        original = "猫呕吐拉肚子"
        result = rewriter.rewrite(original)
        assert "呕吐" in result or "吐" in result
        assert "拉肚子" in result or "腹泻" in result

    def test_get_query_rewriter_singleton(self):
        """验证查询改写器单例"""
        from src.core.query_rewriter import get_query_rewriter
        r1 = get_query_rewriter()
        r2 = get_query_rewriter()
        assert r1 is r2
