"""
商品搜索引擎单元测试

测试 ProductSearcher 类的所有功能，包括：
- 关键词搜索
- 分类搜索
- 价格范围筛选
- 商品详情获取
- 相似商品推荐
- 错误处理
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.product_searcher import ProductSearcher


class TestProductSearcher:
    """商品搜索引擎测试类"""

    @pytest.fixture
    def searcher(self):
        return ProductSearcher()

    @pytest.fixture
    def sample_products(self):
        return [
            {
                "product_id": "prod_food_001",
                "name": "皇家狗粮成犬",
                "category": "food",
                "price": 299.0,
                "brand": "Royal Canin",
                "rating": 4.8,
                "description": "优质成犬粮"
            },
            {
                "product_id": "prod_toy_001",
                "name": "橡胶磨牙玩具",
                "category": "toy",
                "price": 49.9,
                "brand": "KONG",
                "rating": 4.5,
                "description": "耐咬磨牙玩具"
            },
            {
                "product_id": "prod_food_002",
                "name": "渴望天然猫粮",
                "category": "food",
                "price": 458.0,
                "brand": "Orijen",
                "rating": 4.9,
                "description": "无谷高蛋白猫粮"
            },
            {
                "product_id": "prod_medicine_001",
                "name": "体外驱虫滴剂",
                "category": "medicine",
                "price": 128.0,
                "brand": "Frontline",
                "rating": 4.7,
                "description": "月度驱虫保护"
            }
        ]

    def test_init_default_limit(self, searcher):
        """测试初始化默认限制"""
        assert searcher.default_limit == 20

    @patch("src.core.product_searcher.ProductRepository")
    def test_search_with_keyword(self, mock_repo, searcher, sample_products):
        """测试关键词搜索"""
        mock_repo.search.return_value = [sample_products[0]]
        mock_repo.count.return_value = 1

        result = searcher.search(query="狗粮")

        mock_repo.search.assert_called_once()
        assert result["products"] is not None
        assert result["total"] >= 0
        assert "query" in result
        assert result["query"]["keyword"] == "狗粮"

    @patch("src.core.product_searcher.ProductRepository")
    def test_search_with_category(self, mock_repo, searcher, sample_products):
        """测试分类搜索"""
        food_products = [p for p in sample_products if p["category"] == "food"]
        mock_repo.search.return_value = food_products
        mock_repo.count.return_value = len(food_products)

        result = searcher.search(category="food")

        call_kwargs = mock_repo.search.call_args[1]
        assert call_kwargs["category"] == "food"

    @patch("src.core.product_searcher.ProductRepository")
    def test_search_with_price_range(self, mock_repo, searcher):
        """测试价格范围筛选"""
        mock_repo.search.return_value = []
        mock_repo.count.return_value = 0

        result = searcher.search(price_min=100, price_max=300)

        call_kwargs = mock_repo.search.call_args[1]
        assert call_kwargs["price_min"] == 100
        assert call_kwargs["price_max"] == 300

    @patch("src.core.product_searcher.ProductRepository")
    def test_search_with_limit(self, mock_repo, searcher):
        """测试返回数量限制"""
        mock_repo.search.return_value = []
        mock_repo.count.return_value = 0

        result = searcher.search(limit=10)

        call_kwargs = mock_repo.search.call_args[1]
        assert call_kwargs["limit"] == 10

    @patch("src.core.product_searcher.ProductRepository")
    def test_search_empty_result(self, mock_repo, searcher):
        """测试空结果"""
        mock_repo.search.return_value = []
        mock_repo.count.return_value = 0

        result = searcher.search(query="不存在的关键词")

        assert result["products"] == []
        assert result["total"] == 0
        assert result["returned"] == 0

    @patch("src.core.product_searcher.ProductRepository")
    def test_search_error_handling(self, mock_repo, searcher):
        """测试错误处理"""
        mock_repo.search.side_effect = Exception("数据库连接失败")

        result = searcher.search(query="test")

        assert result["products"] == []
        assert result["total"] == 0
        assert "error" in result

    @patch("src.core.product_searcher.ProductRepository")
    def test_search_by_category(self, mock_repo, searcher, sample_products):
        """测试按分类搜索"""
        expected_products = [sample_products[0], sample_products[2]]
        mock_repo.list_by_category.return_value = expected_products

        result = searcher.search_by_category(category="food", limit=20)

        mock_repo.list_by_category.assert_called_once_with(
            category="food",
            limit=20
        )
        assert len(result) == 2

    @patch("src.core.product_searcher.ProductRepository")
    def test_get_product_details_success(self, mock_repo, searcher, sample_products):
        """测试获取商品详情 - 成功"""
        mock_repo.get_by_id.return_value = sample_products[0]

        result = searcher.get_product_details(product_id="prod_food_001")

        mock_repo.get_by_id.assert_called_once_with("prod_food_001")
        assert result is not None
        assert result["product_id"] == "prod_food_001"
        assert result["name"] == "皇家狗粮成犬"

    @patch("src.core.product_searcher.ProductRepository")
    def test_get_product_details_not_found(self, mock_repo, searcher):
        """测试获取商品详情 - 不存在"""
        mock_repo.get_by_id.return_value = None

        result = searcher.get_product_details(product_id="nonexistent")

        assert result is None

    @patch("src.core.product_searcher.ProductRepository")
    def test_get_similar_products(self, mock_repo, searcher, sample_products):
        """测试获取相似商品"""
        target_product = sample_products[0]
        similar_products = [
            sample_products[2],
            {"product_id": "prod_food_003", "name": "其他狗粮", "category": "food", "price": 280.0}
        ]
        
        mock_repo.get_by_id.return_value = target_product
        mock_repo.search.return_value = [target_product] + similar_products

        result = searcher.get_similar_products(
            product_id="prod_food_001",
            limit=3
        )

        assert len(result) <= 3
        for product in result:
            assert product["product_id"] != "prod_food_001"

    @patch("src.core.product_searcher.ProductRepository")
    def test_get_similar_products_not_found(self, mock_repo, searcher):
        """测试获取相似商品 - 目标商品不存在"""
        mock_repo.get_by_id.return_value = None

        result = searcher.get_similar_products(
            product_id="nonexistent",
            limit=5
        )

        assert result == []

    @patch("src.core.product_searcher.ProductRepository")
    def test_get_similar_products_price_range(self, mock_repo, searcher, sample_products):
        """测试相似商品价格范围（±30%）"""
        target_product = {**sample_products[0]}
        mock_repo.get_by_id.return_value = target_product
        
        call_args_list = []
        original_search = mock_repo.search
        
        def capture_call(**kwargs):
            call_args_list.append(kwargs)
            return []
        
        mock_repo.search.side_effect = capture_call

        searcher.get_similar_products(product_id="prod_food_001", limit=5)

        if call_args_list:
            price_kwargs = call_args_list[0]
            assert price_kwargs["price_min"] == pytest.approx(209.3, rel=0.01)
            assert price_kwargs["price_max"] == pytest.approx(388.7, rel=0.01)

    def test_get_product_searcher_factory(self):
        """测试工厂函数"""
        from src.core.product_searcher import get_product_searcher
        
        instance = get_product_searcher()
        
        assert isinstance(instance, ProductSearcher)
