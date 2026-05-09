"""
购物助手服务集成测试

测试 ShoppingService 类的所有业务逻辑，包括：
- 商品创建与验证
- 商品搜索
- 购物行为记录
- 用户偏好获取
- 成分分析保存
- 商品统计
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.shopping_service import ShoppingService


class TestShoppingService:
    """购物助手服务测试类"""

    @pytest.fixture
    def service(self):
        return ShoppingService()

    @pytest.fixture
    def sample_product_data(self):
        return {
            "product_id": "prod_food_001",
            "name": "皇家狗粮成犬",
            "category": "food",
            "price": 299.0,
            "brand": "Royal Canin",
            "subcategory": "dry_food",
            "image_url": "https://example.com/dog-food.jpg",
            "description": "优质成犬粮，适合12月龄以上犬只",
            "ingredients": [
                {"name": "鸡肉", "percentage": 25.0},
                {"name": "糙米", "percentage": 20.0}
            ],
            "nutrition_info": {
                "protein": 25.0,
                "fat": 14.0,
                "carbs": 40.0
            },
            "suitable_for": ["adult_dog", "medium_breed"],
            "tags": ["天然", "无谷", "高蛋白"]
        }

    @patch("src.services.shopping_service.ProductRepository")
    def test_create_product_success(self, mock_repo, service, sample_product_data):
        """测试成功创建商品"""
        mock_repo.create.return_value = None

        product_id = service.create_product(
            name=sample_product_data["name"],
            category=sample_product_data["category"],
            price=sample_product_data["price"],
            brand=sample_product_data["brand"]
        )

        assert product_id is not None
        assert product_id.startswith("product_food_")
        
        call_args = mock_repo.create.call_args[0][0]
        assert call_args["name"] == "皇家狗粮成犬"
        assert call_args["category"] == "food"
        assert call_args["price"] == 299.0
        assert call_args["rating"] == 0.0
        assert call_args["stock_status"] == "in_stock"

    def test_create_product_invalid_category(self, service):
        """测试无效商品分类"""
        with pytest.raises(ValueError) as excinfo:
            service.create_product(
                name="测试商品",
                category="invalid_category",
                price=100.0
            )
        
        assert "无效的商品分类" in str(excinfo.value)

    def test_create_product_all_categories(self, service):
        """测试所有有效分类"""
        valid_categories = ["food", "toy", "accessory", "medicine", "hygiene", "clothing"]
        
        for category in valid_categories:
            with patch("src.services.shopping_service.ProductRepository") as mock_repo:
                mock_repo.create.return_value = None
                product_id = service.create_product(
                    name=f"测试{category}",
                    category=category,
                    price=99.9
                )
                assert product_id is not None

    @patch("src.services.shopping_service.ProductRepository")
    def test_create_product_with_optional_fields(self, mock_repo, service):
        """测试带可选字段的商品创建"""
        mock_repo.create.return_value = None

        product_id = service.create_product(
            name="高级猫粮",
            category="food",
            price=458.0,
            brand="Orijen",
            subcategory="grain_free",
            image_url="https://example.com/cat-food.jpg",
            description="无谷高蛋白猫粮",
            ingredients=[{"name": "鸡肉", "percentage": 35.0}],
            nutrition_info={"protein": 38.0},
            suitable_for=["adult_cat"],
            tags=["无谷", "高蛋白"]
        )

        call_args = mock_repo.create.call_args[0][0]
        assert call_args["brand"] == "Orijen"
        assert call_args["subcategory"] == "grain_free"
        assert len(call_args["ingredients"]) > 0
        assert call_args["tags"] == ["无谷", "高蛋白"]

    @patch("src.services.shopping_service.ProductRepository")
    def test_search_products(self, mock_repo, service):
        """测试商品搜索"""
        expected_products = [
            {"product_id": "p1", "name": "产品1"},
            {"product_id": "p2", "name": "产品2"}
        ]
        mock_repo.search.return_value = expected_products

        result = service.search_products(query="狗粮")

        mock_repo.search.assert_called_once()
        assert result == expected_products

    @patch("src.services.shopping_service.ProductRepository")
    def test_search_products_with_filters(self, mock_repo, service):
        """测试带筛选条件的搜索"""
        mock_repo.search.return_value = []

        service.search_products(
            query="玩具",
            category="toy",
            price_min=20,
            price_max=100,
            skip=0,
            limit=10
        )

        call_kwargs = mock_repo.search.call_args[1]
        assert call_kwargs["query"] == "玩具"
        assert call_kwargs["category"] == "toy"
        assert call_kwargs["price_min"] == 20
        assert call_kwargs["price_max"] == 100

    @patch("src.services.shopping_service.ProductRepository")
    def test_get_product_found(self, mock_repo, service, sample_product_data):
        """测试获取存在的商品"""
        mock_repo.get_by_id.return_value = sample_product_data

        result = service.get_product(product_id="prod_food_001")

        assert result is not None
        assert result["product_id"] == "prod_food_001"

    @patch("src.services.shopping_service.ProductRepository")
    def test_get_product_not_found(self, mock_repo, service):
        """测试获取不存在的商品"""
        mock_repo.get_by_id.return_value = None

        result = service.get_product(product_id="nonexistent")

        assert result is None

    @patch("src.services.shopping_service.ShoppingHistoryRepository")
    @patch("src.services.shopping_service.ProductRepository")
    def test_record_shopping_action_success(self, mock_product_repo, mock_history_repo, service):
        """测试成功记录购物行为"""
        mock_product_repo.get_by_id.return_value = {
            "product_id": "prod_toy_001",
            "price": 49.9
        }
        mock_history_repo.create.return_value = None

        history_id = service.record_shopping_action(
            user_id="user_001",
            product_id="prod_toy_001",
            action_type="view",
            pet_id="pet_001",
            search_query="磨牙玩具"
        )

        assert history_id is not None
        assert history_id.startswith("history_")
        
        call_args = mock_history_repo.create.call_args[0][0]
        assert call_args["user_id"] == "user_001"
        assert call_args["action_type"] == "view"
        assert call_args["price_at_time"] == 49.9

    @patch("src.services.shopping_service.ProductRepository")
    def test_record_shopping_action_product_not_exist(self, mock_product_repo, service):
        """测试记录不存在的商品行为"""
        mock_product_repo.get_by_id.return_value = None

        with pytest.raises(ValueError) as excinfo:
            service.record_shopping_action(
                user_id="user_001",
                product_id="nonexistent",
                action_type="purchase"
            )
        
        assert "商品不存在" in str(excinfo.value)

    @patch("src.services.shopping_service.ShoppingHistoryRepository")
    @patch("src.services.shopping_service.ProductRepository")
    def test_record_all_action_types(self, mock_product_repo, mock_history_repo, service):
        """测试所有操作类型"""
        action_types = ["search", "view", "cart", "purchase", "wishlist"]
        
        mock_product_repo.get_by_id.return_value = {
            "product_id": "prod_001",
            "price": 100.0
        }
        mock_history_repo.create.return_value = None

        for action_type in action_types:
            history_id = service.record_shopping_action(
                user_id="user_001",
                product_id="prod_001",
                action_type=action_type
            )
            
            assert history_id is not None

    @patch("src.services.shopping_service.ShoppingHistoryRepository")
    def test_get_user_preferences(self, mock_history_repo, service):
        """测试获取用户偏好"""
        expected_prefs = {
            "favorite_categories": ["food", "toy"],
            "preferred_brands": ["Royal Canin"],
            "avg_price_range": [50, 300]
        }
        mock_history_repo.get_user_preferences.return_value = expected_prefs

        result = service.get_user_preferences(user_id="user_001")

        mock_history_repo.get_user_preferences.assert_called_once_with("user_001")
        assert result == expected_prefs

    @patch("src.services.shopping_service.IngredientAnalysisRepository")
    def test_save_ingredient_analysis(self, mock_analysis_repo, service):
        """测试保存成分分析结果"""
        analysis_data = {
            "overall_safety": "safe",
            "safety_score": 85,
            "safe_ingredients": [{"name": "鸡肉"}],
            "unsafe_ingredients": [],
            "allergen_warnings": []
        }
        mock_analysis_repo.create.return_value = None

        analysis_id = service.save_ingredient_analysis(analysis_data)

        assert analysis_id is not None
        assert analysis_id.startswith("analysis_")
        
        call_args = mock_analysis_repo.create.call_args[0][0]
        assert call_args["overall_safety"] == "safe"
        assert call_args["analysis_id"] == analysis_id

    @patch("src.services.shopping_service.ProductRepository")
    def test_get_product_stats(self, mock_repo, service):
        """测试获取商品统计信息"""
        mock_repo.count.return_value = 10

        stats = service.get_product_stats()

        assert "total_products" in stats
        assert "by_category" in stats
        assert isinstance(stats["by_category"], dict)
        
        expected_categories = ["food", "toy", "accessory", "medicine", "hygiene", "clothing"]
        for cat in expected_categories:
            assert cat in stats["by_category"]

    def test_get_shopping_service_factory(self):
        """测试工厂函数"""
        from src.services.shopping_service import get_shopping_service
        
        instance = get_shopping_service()
        
        assert isinstance(instance, ShoppingService)


class TestShoppingServiceEdgeCases:
    """购物助手服务边界情况测试"""

    @pytest.fixture
    def service(self):
        return ShoppingService()

    def test_create_product_minimal_fields(self, service):
        """测试最小字段创建"""
        with patch("src.services.shopping_service.ProductRepository") as mock_repo:
            mock_repo.create.return_value = None
            
            product_id = service.create_product(
                name="基础商品",
                category="toy",
                price=19.9
            )
            
            assert product_id is not None
            
            call_args = mock_repo.create.call_args[0][0]
            assert call_args["brand"] is None
            assert call_args["description"] is None
            assert call_args["tags"] == []

    def test_create_product_high_price(self, service):
        """测试高价商品"""
        with patch("src.services.shopping_service.ProductRepository") as mock_repo:
            mock_repo.create.return_value = None
            
            product_id = service.create_product(
                name="豪华宠物床",
                category="accessory",
                price=9999.99
            )
            
            assert product_id is not None

    def test_create_product_zero_price(self, service):
        """测试零价格商品（免费样品）"""
        with patch("src.services.shopping_service.ProductRepository") as mock_repo:
            mock_repo.create.return_value = None
            
            product_id = service.create_product(
                name="免费试用装",
                category="food",
                price=0
            )
            
            assert product_id is not None

    @patch("src.services.shopping_service.ProductRepository")
    def test_search_empty_query(self, mock_repo, service):
        """测试空查询搜索"""
        mock_repo.search.return_value = []

        result = service.search_products()

        assert result == []

    @patch("src.services.shopping_service.ShoppingHistoryRepository")
    @patch("src.services.shopping_service.ProductRepository")
    def test_record_action_without_optional_params(self, mock_product_repo, mock_history_repo, service):
        """测试不传可选参数的购物行为记录"""
        mock_product_repo.get_by_id.return_value = {
            "product_id": "prod_001",
            "price": 88.0
        }
        mock_history_repo.create.return_value = None

        history_id = service.record_shopping_action(
            user_id="user_001",
            product_id="prod_001",
            action_type="view"
        )

        assert history_id is not None
        
        call_args = mock_history_repo.create.call_args[0][0]
        assert call_args["pet_id"] is None
        assert call_args["search_query"] is None
