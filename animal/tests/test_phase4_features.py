"""
Phase 4 功能测试

验证架构演进模块：
1. 混合检索策略（向量+关键词BM25）
2. Re-ranking机制
3. 多模态内容处理
4. 检索路由系统
"""
import pytest
from unittest.mock import Mock, patch


class TestBM25KeywordSearch:
    """BM25关键词检索测试"""

    def test_index_and_search(self):
        """验证BM25索引和检索"""
        from src.core.hybrid_retriever import BM25KeywordSearch
        bm25 = BM25KeywordSearch()
        
        docs = [
            {"content": "犬瘟热是一种严重的病毒性疾病，常见于幼犬", "metadata": {"category": "disease"}},
            {"content": "猫瘟又称猫泛白细胞减少症，是猫的常见传染病", "metadata": {"category": "disease"}},
            {"content": "金毛寻回犬需要充足的运动和均衡的营养", "metadata": {"category": "nutrition"}},
        ]
        bm25.index_documents(docs)
        
        results = bm25.search("犬瘟热", top_k=2)
        assert len(results) >= 1
        assert "犬瘟热" in results[0]["content"]

    def test_empty_index(self):
        """验证空索引检索"""
        from src.core.hybrid_retriever import BM25KeywordSearch
        bm25 = BM25KeywordSearch()
        
        results = bm25.search("测试查询", top_k=5)
        assert results == []

    def test_no_match(self):
        """验证无匹配结果"""
        from src.core.hybrid_retriever import BM25KeywordSearch
        bm25 = BM25KeywordSearch()
        bm25.index_documents([{"content": "犬瘟热症状", "metadata": {}}])
        
        results = bm25.search("量子力学", top_k=5)
        assert len(results) == 0


class TestReciprocalRankFusion:
    """RRF融合测试"""

    def test_fusion_combines_results(self):
        """验证RRF融合两个检索结果"""
        from src.core.hybrid_retriever import reciprocal_rank_fusion
        
        vector_results = [
            {"content": "犬瘟热症状描述", "distance": 0.1},
            {"content": "细小病毒感染", "distance": 0.2},
        ]
        keyword_results = [
            {"content": "犬瘟热治疗方案", "bm25_score": 2.5},
            {"content": "犬瘟热症状描述", "bm25_score": 1.8},
        ]
        
        fused = reciprocal_rank_fusion(vector_results, keyword_results, top_k=3)
        
        assert len(fused) >= 1
        contents = [r["content"] for r in fused]
        assert "犬瘟热症状描述" in contents

    def test_fusion_empty_one_side(self):
        """验证一侧为空时的融合"""
        from src.core.hybrid_retriever import reciprocal_rank_fusion
        
        vector_results = [{"content": "结果1", "distance": 0.1}]
        keyword_results = []
        
        fused = reciprocal_rank_fusion(vector_results, keyword_results, top_k=5)
        assert len(fused) >= 1


class TestRuleBasedReranker:
    """规则重排序测试"""

    def test_rerank_by_category(self):
        """验证分类加权重排序"""
        from src.core.reranker import RuleBasedReranker
        reranker = RuleBasedReranker()
        
        results = [
            {"content": "行为训练建议", "metadata": {"category": "behavior"}, "distance": 0.1},
            {"content": "急救处理方法", "metadata": {"category": "first_aid"}, "distance": 0.15},
        ]
        
        reranked = reranker.rerank("紧急处理", results, top_k=2)
        assert reranked[0]["metadata"]["category"] == "first_aid"

    def test_rerank_exact_match_bonus(self):
        """验证精确匹配加分"""
        from src.core.reranker import RuleBasedReranker
        reranker = RuleBasedReranker()
        
        results = [
            {"content": "犬瘟热是一种疾病", "metadata": {}, "distance": 0.2},
            {"content": "其他疾病信息", "metadata": {}, "distance": 0.1},
        ]
        
        reranked = reranker.rerank("犬瘟热", results, top_k=2)
        assert "犬瘟热" in reranked[0]["content"]

    def test_rerank_empty_results(self):
        """验证空结果重排序"""
        from src.core.reranker import RuleBasedReranker
        reranker = RuleBasedReranker()
        
        reranked = reranker.rerank("查询", [], top_k=5)
        assert reranked == []


class TestRetrievalRouter:
    """检索路由测试"""

    @pytest.fixture
    def router(self):
        from src.core.retrieval_router import RetrievalRouter
        return RetrievalRouter()

    def test_symptom_diagnosis_intent(self, router):
        """验证症状诊断意图识别"""
        routing = router.route("狗发烧呕吐怎么办")
        assert routing["intent"] == "symptom_diagnosis"
        assert routing["strategy"] == "hybrid"
        assert routing["category"] == "disease"

    def test_nutrition_advice_intent(self, router):
        """验证营养建议意图识别"""
        routing = router.route("金毛吃什么狗粮好")
        assert routing["intent"] == "nutrition_advice"
        assert routing["category"] == "nutrition"

    def test_first_aid_intent(self, router):
        """验证急救意图识别"""
        routing = router.route("狗中毒了怎么急救")
        assert routing["intent"] == "first_aid"
        assert routing["urgency"] == "high"

    def test_medication_intent(self, router):
        """验证用药意图识别"""
        routing = router.route("驱虫药怎么用")
        assert routing["intent"] == "medication_info"
        assert routing["category"] == "medication"

    def test_behavior_intent(self, router):
        """验证行为训练意图识别"""
        routing = router.route("狗乱叫怎么训练")
        assert routing["intent"] == "behavior_training"
        assert routing["category"] == "behavior"

    def test_greeting_routes_to_direct_llm(self, router):
        """验证问候语路由到直接LLM"""
        routing = router.route("你好")
        assert routing["strategy"] == "direct_llm"

    def test_urgency_assessment(self, router):
        """验证紧急程度评估"""
        high_routing = router.route("狗中毒了紧急")
        assert high_routing["urgency"] == "high"
        
        low_routing = router.route("猫的日常护理")
        assert low_routing["urgency"] == "low"

    def test_top_k_adjustment(self, router):
        """验证top_k动态调整"""
        high_routing = router.route("狗中毒急救")
        assert high_routing["top_k"] >= 5
        
        low_routing = router.route("猫的日常护理")
        assert low_routing["top_k"] >= 3

    def test_reranker_flag(self, router):
        """验证重排序器标志"""
        symptom_routing = router.route("狗发烧怎么办")
        assert symptom_routing["use_reranker"] is True
        
        general_routing = router.route("猫的品种介绍")
        assert general_routing["use_reranker"] is False


class TestMultimodalLoader:
    """多模态加载器测试"""

    def test_supported_extensions(self):
        """验证支持的文件格式"""
        from src.core.multimodal_loader import MultimodalDocumentLoader
        loader = MultimodalDocumentLoader()
        
        assert '.pdf' in loader.SUPPORTED_EXTENSIONS
        assert '.docx' in loader.SUPPORTED_EXTENSIONS
        assert '.png' in loader.SUPPORTED_EXTENSIONS
        assert '.txt' in loader.SUPPORTED_EXTENSIONS

    def test_load_nonexistent_file(self):
        """验证加载不存在的文件"""
        from src.core.multimodal_loader import MultimodalDocumentLoader
        loader = MultimodalDocumentLoader()
        
        result = loader.load_file("nonexistent.pdf")
        assert result is None

    def test_load_unsupported_format(self):
        """验证加载不支持的格式"""
        from src.core.multimodal_loader import MultimodalDocumentLoader
        loader = MultimodalDocumentLoader()
        
        with patch('os.path.exists', return_value=True):
            result = loader.load_file("test.xyz")
            assert result is None
