"""
推荐引擎单元测试

测试 RecommendationEngine 类的所有功能，包括：
- 个性化推荐（基于用户历史）
- 知识导向推荐（基于RAG）
- 热门商品推荐
- 健康问题导向推荐
- 合并去重逻辑
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.recommendation_engine import RecommendationEngine


class TestRecommendationEngine:
    """推荐引擎测试类"""

    @pytest.fixture
    def engine(self):
        return RecommendationEngine()

    @pytest.fixture
    def sample_products(self):
        return [
            {
                "product_id": "prod_food_001",
                "name": "皇家狗粮成犬",
                "category": "food",
                "price": 299.0,
                "rating": 4.8,
            },
            {
                "product_id": "prod_hygiene_001",
                "name": "宠物沐浴露",
                "category": "hygiene",
                "price": 68.0,
                "rating": 4.5,
            },
            {
                "product_id": "prod_toy_001",
                "name": "橡胶磨牙玩具",
                "category": "toy",
                "price": 49.9,
                "rating": 4.6,
            },
        ]

    def test_init(self, engine):
        """测试初始化"""
        assert engine is not None
        assert engine.product_searcher is None

    @patch("src.core.recommendation_engine.ShoppingHistoryRepository")
    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_recommendations_basic(self, mock_product_repo, mock_history_repo, engine):
        """测试基本推荐功能"""
        mock_history_repo.list_by_user.return_value = []
        mock_product_repo.search.return_value = []
        
        result = engine.get_recommendations(
            user_id="user_001",
            pet_type="dog"
        )

        assert "recommendations" in result
        assert "sources" in result
        assert isinstance(result["recommendations"], list)
        assert isinstance(result["sources"], dict)

    @patch("src.core.recommendation_engine.ShoppingHistoryRepository")
    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_recommendations_with_limit(self, mock_product_repo, mock_history_repo, engine):
        """测试限制推荐数量"""
        mock_history_repo.list_by_user.return_value = []
        mock_product_repo.search.return_value = []

        result = engine.get_recommendations(
            user_id="user_001",
            limit=5
        )

        assert len(result["recommendations"]) <= 5

    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_personalized_recommendations_with_history(self, mock_product_repo, engine, sample_products):
        """测试有历史记录的个性化推荐"""
        mock_history_items = [
            {"product_id": "prod_food_001", "action_type": "purchase"},
            {"product_id": "prod_food_002", "action_type": "view"},
        ]
        
        with patch.object(engine, '_get_popular_products', return_value=[]):
            with patch("src.core.recommendation_engine.ShoppingHistoryRepository") as mock_history:
                mock_history.list_by_user.return_value = mock_history_items
                mock_product_repo.get_by_id.return_value = sample_products[0]
                mock_product_repo.search.return_value = sample_products[:1]

                result = engine._get_personalized_recommendations(
                    user_id="user_001",
                    limit=3
                )

                assert isinstance(result, list)

    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_personalized_recommendations_no_history(self, mock_product_repo, engine, sample_products):
        """测试无历史记录时回退到热门推荐"""
        popular_products = [sample_products[0]]
        
        with patch.object(engine, '_get_popular_products', return_value=popular_products):
            with patch("src.core.recommendation_engine.ShoppingHistoryRepository") as mock_history:
                mock_history.list_by_user.return_value = []

                result = engine._get_personalized_recommendations(
                    user_id="user_new",
                    limit=3
                )

                assert result == popular_products

    @patch("src.core.recommendation_engine.KnowledgeRetriever")
    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_health_focused_recommendations_skin_issue(self, mock_product_repo, mock_knowledge, engine, sample_products):
        """测试皮肤问题的健康导向推荐"""
        mock_knowledge_instance = MagicMock()
        mock_knowledge_instance.search.return_value = []
        mock_knowledge.return_value = mock_knowledge_instance
        
        hygiene_products = [sample_products[1]]
        mock_product_repo.search.return_value = hygiene_products

        result = engine._get_health_focused_recommendations(
            conditions=["皮肤病", "过敏"],
            pet_type="dog",
            age_group="adult",
            limit=2
        )

        assert isinstance(result, list)

    @patch("src.core.recommendation_engine.KnowledgeRetriever")
    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_health_focused_recommendations_digestive_issue(self, mock_product_repo, mock_knowledge, engine, sample_products):
        """测试消化问题的健康导向推荐"""
        mock_knowledge_instance = MagicMock()
        mock_knowledge_instance.search.return_value = []
        mock_knowledge.return_value = mock_knowledge_instance
        
        food_products = [sample_products[0]]
        mock_product_repo.search.return_value = food_products

        result = engine._get_health_focused_recommendations(
            conditions=["肠胃", "腹泻"],
            pet_type="cat",
            age_group="adult",
            limit=2
        )

        assert isinstance(result, list)

    @patch("src.core.recommendation_engine.KnowledgeRetriever")
    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_health_focused_recommendations_error_handling(self, mock_product_repo, mock_knowledge, engine):
        """测试健康导向推荐的错误处理"""
        mock_knowledge_instance = MagicMock()
        mock_knowledge_instance.search.side_effect = Exception("知识库连接失败")
        mock_knowledge.return_value = mock_knowledge_instance

        result = engine._get_health_focused_recommendations(
            conditions=["测试"],
            pet_type="dog",
            age_group="adult"
        )

        assert isinstance(result, list)

    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_popular_products(self, mock_product_repo, engine, sample_products):
        """测试获取热门商品"""
        mock_product_repo.search.return_value = sample_products

        result = engine._get_popular_products(limit=5)

        mock_product_repo.search.assert_called_once()
        call_kwargs = mock_product_repo.search.call_args[1]
        assert call_kwargs.get("sort_by") == "rating"

    @patch("src.core.recommendation_engine.ProductRepository")
    def test_get_popular_products_error_handling(self, mock_product_repo, engine):
        """测试获取热门商品的错误处理"""
        mock_product_repo.search.side_effect = Exception("数据库错误")

        result = engine._get_popular_products()

        assert result == []

    def test_merge_and_deduplicate_basic(self, engine, sample_products):
        """测试合并去重基本功能"""
        recommendations = {
            "personalized": [sample_products[0]],
            "health_focused": [sample_products[1]],
            "popular": [sample_products[2]],
            "knowledge_based": []
        }

        result = engine._merge_and_deduplicate(recommendations, limit=10)

        assert len(result) == 3
        seen_ids = {p["product_id"] for p in result}
        assert len(seen_ids) == 3

    def test_merge_and_deduplicate_remove_duplicates(self, engine, sample_products):
        """测试去重功能"""
        recommendations = {
            "personalized": [sample_products[0], sample_products[1]],
            "health_focused": [sample_products[0]],
            "popular": [sample_products[1], sample_products[2]],
            "knowledge_based": []
        }

        result = engine._merge_and_deduplicate(recommendations, limit=10)

        seen_ids = [p["product_id"] for p in result]
        assert len(seen_ids) == len(set(seen_ids))

    def test_merge_and_deduplicate_limit(self, engine, sample_products):
        """测试数量限制"""
        recommendations = {
            "personalized": sample_products,
            "health_focused": sample_products,
            "popular": sample_products,
            "knowledge_based": sample_products
        }

        result = engine._merge_and_deduplicate(recommendations, limit=2)

        assert len(result) <= 2

    def test_merge_and_deduplicate_empty(self, engine):
        """测试空输入"""
        recommendations = {
            "personalized": [],
            "health_focused": [],
            "popular": [],
            "knowledge_based": []
        }

        result = engine._merge_and_deduplicate(recommendations)

        assert result == []

    def test_merge_priority_order(self, engine, sample_products):
        """测试合并优先级顺序"""
        recommendations = {
            "personalized": [sample_products[0]],
            "health_focused": [sample_products[1]],
            "popular": [sample_products[2]],
            "knowledge_based": []
        }

        result = engine._merge_and_deduplicate(recommendations, limit=3)

        assert result[0]["product_id"] == sample_products[0]["product_id"]

    def test_get_recommendation_engine_factory(self):
        """测试工厂函数"""
        from src.core.recommendation_engine import get_recommendation_engine
        
        instance = get_recommendation_engine()
        
        assert isinstance(instance, RecommendationEngine)


class TestRecommendationEngineIntegration:
    """推荐引擎集成测试"""

    @pytest.fixture
    def engine(self):
        return RecommendationEngine()

    @pytest.fixture
    def sample_products(self):
        return [
            {
                "product_id": "prod_food_001",
                "name": "皇家狗粮成犬",
                "category": "food",
                "price": 299.0,
                "rating": 4.8,
            },
            {
                "product_id": "prod_hygiene_001",
                "name": "宠物沐浴露",
                "category": "hygiene",
                "price": 68.0,
                "rating": 4.5,
            },
            {
                "product_id": "prod_toy_001",
                "name": "橡胶磨牙玩具",
                "category": "toy",
                "price": 49.9,
                "rating": 4.6,
            },
        ]

    @patch("src.core.recommendation_engine.ShoppingHistoryRepository")
    @patch("src.core.recommendation_engine.ProductRepository")
    @patch("src.core.recommendation_engine.KnowledgeRetriever")
    def test_full_recommendation_flow(
        self, 
        mock_knowledge, 
        mock_product_repo, 
        mock_history_repo, 
        engine,
        sample_products
    ):
        """完整推荐流程测试"""
        mock_history_repo.list_by_user.return_value = [
            {"product_id": "prod_food_001"}
        ]
        mock_product_repo.get_by_id.return_value = sample_products[0]
        mock_product_repo.search.return_value = sample_products[:2]
        mock_product_repo.count.return_value = 10
        
        mock_knowledge_instance = MagicMock()
        mock_knowledge_instance.search.return_value = []
        mock_knowledge.return_value = mock_knowledge_instance

        result = engine.get_recommendations(
            user_id="user_001",
            pet_type="dog",
            pet_age_group="adult",
            health_conditions=["过敏"],
            limit=8
        )

        assert "recommendations" in result
        assert "sources" in result
        assert all(key in result["sources"] for key in [
            "personalized_count",
            "knowledge_based_count",
            "popular_count",
            "health_focused_count"
        ])
