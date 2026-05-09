"""
购物助手 API 端点系统测试

测试 shopping.py 中的所有 API 端点，包括：
- POST /shopping/search - 商品搜索
- GET /shopping/products/{product_id} - 获取商品详情
- POST /shopping/products - 创建商品
- POST /shopping/analyze - 成分分析
- POST /shopping/recommendations - 获取推荐
- POST /shopping/action - 记录购物行为
- GET /shopping/compare - 商品对比
- GET /shopping/categories - 分类统计
- GET /shopping/similar/{product_id} - 相似商品
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI


@pytest.fixture
def app():
    """创建测试应用"""
    from src.api.v1.endpoints.shopping import router
    
    test_app = FastAPI()
    test_app.include_router(router)
    
    return test_app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


class TestSearchEndpoint:
    """搜索端点测试"""

    def test_search_success(self, client):
        """测试成功搜索"""
        with patch("src.api.v1.endpoints.shopping.ProductSearcher") as mock_searcher_cls:
            mock_searcher = MagicMock()
            mock_searcher.search.return_value = {
                "products": [
                    {
                        "_id": "obj_001",
                        "product_id": "prod_001",
                        "name": "狗粮",
                        "category": "food",
                        "price": 299.0,
                        "brand": "Test",
                        "rating": 4.5,
                        "description": "测试狗粮",
                        "image_url": None,
                        "stock_status": "in_stock",
                        "currency": "CNY",
                        "created_at": "2026-04-17T00:00:00Z",
                        "updated_at": "2026-04-17T00:00:00Z",
                        "subcategory": None,
                        "ingredients": [],
                        "nutrition_info": {},
                        "suitable_for": [],
                        "tags": [],
                        "review_count": 0
                    }
                ],
                "total": 1,
                "returned": 1,
                "query": {"keyword": "狗粮", "category": None}
            }
            mock_searcher_cls.return_value = mock_searcher

            response = client.post("/shopping/search", json={
                "query": "狗粮"
            })

            assert response.status_code == 200
            data = response.json()
            assert "products" in data
            assert "total" in data

    def test_search_with_filters(self, client):
        """测试带筛选条件的搜索"""
        with patch("src.api.v1.endpoints.shopping.ProductSearcher") as mock_searcher_cls:
            mock_searcher = MagicMock()
            mock_searcher.search.return_value = {
                "products": [],
                "total": 0,
                "returned": 0,
                "query": {}
            }
            mock_searcher_cls.return_value = mock_searcher

            response = client.post("/shopping/search", json={
                "query": "玩具",
                "category": "toy",
                "price_min": 20,
                "price_max": 100,
                "limit": 10
            })

            assert response.status_code == 200

    def test_search_error_handling(self, client):
        """测试搜索错误处理"""
        with patch("src.api.v1.endpoints.shopping.ProductSearcher") as mock_searcher_cls:
            mock_searcher = MagicMock()
            mock_searcher.search.side_effect = Exception("数据库错误")
            mock_searcher_cls.return_value = mock_searcher

            response = client.post("/shopping/search", json={
                "query": "test"
            })

            assert response.status_code == 500


class TestProductDetailEndpoint:
    """商品详情端点测试"""

    def test_get_product_found(self, client):
        """测试获取存在的商品"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_product.return_value = {
                "_id": "obj_001",
                "product_id": "prod_001",
                "name": "测试商品",
                "category": "food",
                "price": 99.9,
                "brand": "TestBrand",
                "rating": 4.5,
                "description": "描述",
                "image_url": None,
                "stock_status": "in_stock",
                "currency": "CNY",
                "created_at": "2026-04-17T00:00:00Z",
                "updated_at": "2026-04-17T00:00:00Z",
                "subcategory": None,
                "ingredients": [],
                "nutrition_info": {},
                "suitable_for": [],
                "tags": [],
                "review_count": 10
            }
            mock_service_cls.return_value = mock_service

            response = client.get("/shopping/products/prod_001")

            assert response.status_code == 200
            data = response.json()
            assert data["product_id"] == "prod_001"

    def test_get_product_not_found(self, client):
        """测试获取不存在的商品"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_product.return_value = None
            mock_service_cls.return_value = mock_service

            response = client.get("/shopping/products/nonexistent")

            assert response.status_code == 404

    def test_get_product_server_error(self, client):
        """测试服务器错误"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_product.side_effect = Exception("服务器内部错误")
            mock_service_cls.return_value = mock_service

            response = client.get("/shopping/products/prod_001")

            assert response.status_code == 500


class TestCreateProductEndpoint:
    """创建商品端点测试"""

    def test_create_product_success(self, client):
        """测试成功创建商品"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            
            new_product_id = "prod_food_new123"
            mock_service.create_product.return_value = new_product_id
            
            created_product = {
                "_id": "obj_new",
                "product_id": new_product_id,
                "name": "新商品",
                "category": "food",
                "price": 199.0,
                "brand": "NewBrand",
                "rating": 0.0,
                "description": None,
                "image_url": None,
                "stock_status": "in_stock",
                "currency": "CNY",
                "created_at": "2026-04-17T00:00:00Z",
                "updated_at": "2026-04-17T00:00:00Z",
                "subcategory": None,
                "ingredients": [],
                "nutrition_info": {},
                "suitable_for": [],
                "tags": [],
                "review_count": 0
            }
            mock_service.get_product.return_value = created_product
            mock_service_cls.return_value = mock_service

            response = client.post("/shopping/products", json={
                "name": "新商品",
                "category": "food",
                "price": 199.0,
                "brand": "NewBrand"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "新商品"

    def test_create_product_invalid_category(self, client):
        """测试无效分类"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.create_product.side_effect = ValueError("无效的商品分类")
            mock_service_cls.return_value = mock_service

            response = client.post("/shopping/products", json={
                "name": "测试",
                "category": "invalid",
                "price": 99.9
            })

            assert response.status_code == 400

    def test_create_product_server_error(self, client):
        """测试服务器错误"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.create_product.side_effect = Exception("数据库连接失败")
            mock_service_cls.return_value = mock_service

            response = client.post("/shopping/products", json={
                "name": "测试",
                "category": "food",
                "price": 99.9
            })

            assert response.status_code == 500


class TestAnalyzeEndpoint:
    """成分分析端点测试"""

    def test_analyze_ingredients_success(self, client):
        """测试成功分析成分"""
        with patch("src.api.v1.endpoints.shopping.IngredientAnalyzer") as mock_analyzer_cls:
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = {
                "overall_safety": "safe",
                "safety_score": 85,
                "safe_ingredients": [{"name": "鸡肉"}],
                "caution_ingredients": [],
                "unsafe_ingredients": [],
                "allergen_warnings": [],
                "recommendations": ["优质成分"],
                "total_analyzed": 5,
                "parsed_ingredients": ["鸡肉", "糙米"]
            }
            mock_analyzer_cls.return_value = mock_analyzer

            response = client.post("/shopping/analyze", json={
                "ingredients_text": "鸡肉, 糙米, 鱼油",
                "pet_type": "dog"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["overall_safety"] == "safe"
            assert data["safety_score"] == 85

    def test_analyze_unsafe_ingredients(self, client):
        """测试不安全成分分析"""
        with patch("src.api.v1.endpoints.shopping.IngredientAnalyzer") as mock_analyzer_cls:
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = {
                "overall_safety": "unsafe",
                "safety_score": 30,
                "safe_ingredients": [],
                "caution_ingredients": [],
                "unsafe_ingredients": [{"name": "巧克力", "reason": "对犬类有毒", "severity": "high"}],
                "allergen_warnings": [{"category": "其他", "allergen": "巧克力", "found_in": "成分列表", "risk_level": "critical"}],
                "recommendations": ["请立即停止使用"],
                "total_analyzed": 3,
                "parsed_ingredients": ["巧克力"]
            }
            mock_analyzer_cls.return_value = mock_analyzer

            response = client.post("/shopping/analyze", json={
                "ingredients_text": "巧克力, 洋葱",
                "pet_type": "dog"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["overall_safety"] == "unsafe"

    def test_analyze_with_health_conditions(self, client):
        """测试带健康条件的成分分析"""
        with patch("src.api.v1.endpoints.shopping.IngredientAnalyzer") as mock_analyzer_cls:
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.return_value = {
                "overall_safety": "cautionary",
                "safety_score": 65,
                "safe_ingredients": [],
                "caution_ingredients": [],
                "unsafe_ingredients": [],
                "allergen_warnings": [],
                "recommendations": ["建议低脂配方"],
                "total_analyzed": 2,
                "parsed_ingredients": []
            }
            mock_analyzer_cls.return_value = mock_analyzer

            response = client.post("/shopping/analyze", json={
                "ingredients_text": "高脂肪配方",
                "pet_type": "dog",
                "age_group": "senior",
                "health_conditions": ["肥胖", "糖尿病"]
            })

            assert response.status_code == 200

    def test_analyze_error_handling(self, client):
        """测试成分分析错误处理"""
        with patch("src.api.v1.endpoints.shopping.IngredientAnalyzer") as mock_analyzer_cls:
            mock_analyzer = MagicMock()
            mock_analyzer.analyze.side_effect = Exception("分析服务异常")
            mock_analyzer_cls.return_value = mock_analyzer

            response = client.post("/shopping/analyze", json={
                "ingredients_text": "测试",
                "pet_type": "dog"
            })

            assert response.status_code == 500


class TestRecommendationsEndpoint:
    """推荐端点测试"""

    def test_get_recommendations_success(self, client):
        """测试成功获取推荐"""
        with patch("src.api.v1.endpoints.shopping.RecommendationEngine") as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine.get_recommendations.return_value = {
                "recommendations": [
                    {
                        "_id": "obj_rec_001",
                        "product_id": "prod_001",
                        "name": "推荐商品",
                        "category": "food",
                        "price": 199.0,
                        "brand": "Test",
                        "rating": 4.7,
                        "description": "描述",
                        "image_url": None,
                        "stock_status": "in_stock",
                        "currency": "CNY",
                        "created_at": "2026-04-17T00:00:00Z",
                        "updated_at": "2026-04-17T00:00:00Z",
                        "subcategory": None,
                        "ingredients": [],
                        "nutrition_info": {},
                        "suitable_for": [],
                        "tags": [],
                        "review_count": 50
                    }
                ],
                "sources": {
                    "personalized_count": 1,
                    "knowledge_based_count": 0,
                    "popular_count": 2,
                    "health_focused_count": 0
                }
            }
            mock_engine_cls.return_value = mock_engine

            response = client.post("/shopping/recommendations", json={
                "user_id": "user_001",
                "pet_type": "dog",
                "pet_age_group": "adult",
                "limit": 10
            })

            assert response.status_code == 200
            data = response.json()
            assert "recommendations" in data
            assert "sources" in data

    def test_recommendations_with_health_conditions(self, client):
        """测试带健康条件的推荐"""
        with patch("src.api.v1.endpoints.shopping.RecommendationEngine") as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine.get_recommendations.return_value = {
                "recommendations": [],
                "sources": {"personalized_count": 0, "knowledge_based_count": 0, 
                           "popular_count": 0, "health_focused_count": 2}
            }
            mock_engine_cls.return_value = mock_engine

            response = client.post("/shopping/recommendations", json={
                "user_id": "user_002",
                "pet_type": "cat",
                "pet_age_group": "senior",
                "health_conditions": ["肾病"],
                "limit": 8
            })

            assert response.status_code == 200

    def test_recommendations_error_handling(self, client):
        """测试推荐错误处理"""
        with patch("src.api.v1.endpoints.shopping.RecommendationEngine") as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine.get_recommendations.side_effect = Exception("推荐引擎故障")
            mock_engine_cls.return_value = mock_engine

            response = client.post("/shopping/recommendations", json={
                "user_id": "user_001",
                "pet_type": "dog"
            })

            assert response.status_code == 500


class TestActionEndpoint:
    """购物行为记录端点测试"""

    def test_record_action_success(self, client):
        """测试成功记录行为"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.record_shopping_action.return_value = "history_abc12345"
            mock_service_cls.return_value = mock_service

            response = client.post("/shopping/action?user_id=user_001", json={
                "product_id": "prod_toy_001",
                "action_type": "view",
                "pet_id": "pet_001",
                "search_query": "玩具"
            })

            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "history_id" in data

    def test_record_action_invalid_product(self, client):
        """测试无效商品ID"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.record_shopping_action.side_effect = ValueError("商品不存在")
            mock_service_cls.return_value = mock_service

            response = client.post("/shopping/action?user_id=user_001", json={
                "product_id": "nonexistent",
                "action_type": "purchase"
            })

            assert response.status_code == 400

    def test_record_action_error_handling(self, client):
        """测试错误处理"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.record_shopping_action.side_effect = Exception("数据库错误")
            mock_service_cls.return_value = mock_service

            response = client.post("/shopping/action?user_id=user_001", json={
                "product_id": "prod_001",
                "action_type": "view"
            })

            assert response.status_code == 500


class TestCompareEndpoint:
    """商品对比端点测试"""

    def test_compare_products_success(self, client):
        """测试成功对比商品"""
        products_to_return = [
            {
                "_id": "obj_p1",
                "product_id": "p1",
                "name": "产品A",
                "category": "food",
                "price": 299.0,
                "brand": "A",
                "rating": 4.5,
                "description": "",
                "image_url": None,
                "stock_status": "in_stock",
                "currency": "CNY",
                "created_at": "2026-04-17T00:00:00Z",
                "updated_at": "2026-04-17T00:00:00Z",
                "subcategory": None,
                "ingredients": [],
                "nutrition_info": {},
                "suitable_for": [],
                "tags": [],
                "review_count": 100
            },
            {
                "_id": "obj_p2",
                "product_id": "p2",
                "name": "产品B",
                "category": "food",
                "price": 358.0,
                "brand": "B",
                "rating": 4.7,
                "description": "",
                "image_url": None,
                "stock_status": "in_stock",
                "currency": "CNY",
                "created_at": "2026-04-17T00:00:00Z",
                "updated_at": "2026-04-17T00:00:00Z",
                "subcategory": None,
                "ingredients": [],
                "nutrition_info": {},
                "suitable_for": [],
                "tags": [],
                "review_count": 80
            }
        ]

        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_product.side_effect = lambda pid: next(
                (p for p in products_to_return if p["product_id"] == pid), None
            )
            mock_service_cls.return_value = mock_service

            response = client.get("/shopping/compare?product_ids=p1,p2")

            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["products"]) == 2

    def test_compare_too_few_products(self, client):
        """测试商品数量不足"""
        response = client.get("/shopping/compare?product_ids=p1")

        assert response.status_code == 400

    def test_compare_too_many_products(self, client):
        """测试商品数量过多"""
        ids = ",".join([f"p{i}" for i in range(6)])
        response = client.get(f"/shopping/compare?product_ids={ids}")

        assert response.status_code == 400

    def test_compare_no_valid_products(self, client):
        """测试无有效商品"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_product.return_value = None
            mock_service_cls.return_value = mock_service

            response = client.get("/shopping/compare?product_ids=invalid1,invalid2")

            assert response.status_code == 404


class TestCategoriesEndpoint:
    """分类统计端点测试"""

    def test_get_categories_success(self, client):
        """测试成功获取分类统计"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_product_stats.return_value = {
                "total_products": 150,
                "by_category": {
                    "food": 50,
                    "toy": 30,
                    "accessory": 25,
                    "medicine": 20,
                    "hygiene": 15,
                    "clothing": 10
                }
            }
            mock_service_cls.return_value = mock_service

            response = client.get("/shopping/categories")

            assert response.status_code == 200
            data = response.json()
            assert "total_products" in data
            assert "by_category" in data

    def test_categories_error_handling(self, client):
        """测试分类统计错误处理"""
        with patch("src.api.v1.endpoints.shopping.ShoppingService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service.get_product_stats.side_effect = Exception("数据库查询失败")
            mock_service_cls.return_value = mock_service

            response = client.get("/shopping/categories")

            assert response.status_code == 500


class TestSimilarProductsEndpoint:
    """相似商品端点测试"""

    def test_get_similar_success(self, client):
        """测试成功获取相似商品"""
        similar_products = [
            {
                "_id": "obj_sim_001",
                "product_id": "sim_001",
                "name": "相似商品1",
                "category": "food",
                "price": 280.0,
                "brand": "Similar",
                "rating": 4.6,
                "description": "",
                "image_url": None,
                "stock_status": "in_stock",
                "currency": "CNY",
                "created_at": "2026-04-17T00:00:00Z",
                "updated_at": "2026-04-17T00:00:00Z",
                "subcategory": None,
                "ingredients": [],
                "nutrition_info": {},
                "suitable_for": [],
                "tags": [],
                "review_count": 30
            },
            {
                "_id": "obj_sim_002",
                "product_id": "sim_002",
                "name": "相似商品2",
                "category": "food",
                "price": 320.0,
                "brand": "Similar2",
                "rating": 4.4,
                "description": "",
                "image_url": None,
                "stock_status": "in_stock",
                "currency": "CNY",
                "created_at": "2026-04-17T00:00:00Z",
                "updated_at": "2026-04-17T00:00:00Z",
                "subcategory": None,
                "ingredients": [],
                "nutrition_info": {},
                "suitable_for": [],
                "tags": [],
                "review_count": 25
            }
        ]

        with patch("src.api.v1.endpoints.shopping.ProductSearcher") as mock_searcher_cls:
            mock_searcher = MagicMock()
            mock_searcher.get_similar_products.return_value = similar_products
            mock_searcher_cls.return_value = mock_searcher

            response = client.get("/shopping/similar/prod_food_001?limit=5")

            assert response.status_code == 200
            data = response.json()
            assert data["reference_product_id"] == "prod_food_001"
            assert len(data["products"]) == 2

    def test_similar_invalid_limit(self, client):
        """测试无效的 limit 参数（超出范围）"""
        with patch("src.api.v1.endpoints.shopping.ProductSearcher") as mock_searcher_cls:
            mock_searcher = MagicMock()
            mock_searcher.get_similar_products.return_value = []
            mock_searcher_cls.return_value = mock_searcher

            response = client.get("/shopping/similar/p1?limit=15")

            assert response.status_code == 422

    def test_similar_error_handling(self, client):
        """测试相似商品错误处理"""
        with patch("src.api.v1.endpoints.shopping.ProductSearcher") as mock_searcher_cls:
            mock_searcher = MagicMock()
            mock_searcher.get_similar_products.side_effect = Exception("查询失败")
            mock_searcher_cls.return_value = mock_searcher

            response = client.get("/shopping/similar/prod_001")

            assert response.status_code == 500
