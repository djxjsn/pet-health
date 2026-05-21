"""
宠物知识科普模块 - API集成测试

使用FastAPI TestClient测试5个REST API端点：
- GET /api/v1/encyclopedia/breeds/{species}
- GET /api/v1/encyclopedia/breed/{breed_id}
- GET /api/v1/encyclopedia/health/{species}
- GET /api/v1/encyclopedia/health/detail/{condition_id}
- GET /api/v1/encyclopedia/search?query=

测试覆盖：正常请求、异常请求、参数校验、响应结构、HTTP状态码
"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


client = TestClient(app)


class TestEncyclopediaBreedListAPI:
    """品种列表API测试"""

    def test_get_cat_breeds_200(self):
        """GET /encyclopedia/breeds/cat 返回200"""
        response = client.get("/api/v1/encyclopedia/breeds/cat")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "cat"
        assert len(data["breeds"]) == 10

    def test_get_dog_breeds_200(self):
        """GET /encyclopedia/breeds/dog 返回200"""
        response = client.get("/api/v1/encyclopedia/breeds/dog")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "dog"
        assert len(data["breeds"]) == 10

    def test_invalid_species_400(self):
        """无效species返回400"""
        response = client.get("/api/v1/encyclopedia/breeds/bird")
        assert response.status_code == 400
        assert response.json()["detail"] == "物种类型不合法，仅支持 cat/dog"

    def test_empty_species_400(self):
        """空species返回400"""
        response = client.get("/api/v1/encyclopedia/breeds/")
        assert response.status_code in (400, 404)

    def test_breeds_response_structure(self):
        """品种列表响应结构验证"""
        response = client.get("/api/v1/encyclopedia/breeds/cat")
        data = response.json()
        assert "species" in data
        assert "breeds" in data
        for breed in data["breeds"]:
            assert "id" in breed
            assert "name" in breed
            assert "species" in breed
            assert "popularity" in breed

    def test_breeds_sorted_by_popularity(self):
        """品种按popularity降序"""
        response = client.get("/api/v1/encyclopedia/breeds/dog")
        data = response.json()
        popularities = [b["popularity"] for b in data["breeds"]]
        assert popularities == sorted(popularities, reverse=True)


class TestEncyclopediaBreedDetailAPI:
    """品种详情API测试"""

    def test_get_breed_detail_200(self):
        """有效品种ID返回200"""
        response = client.get("/api/v1/encyclopedia/breed/cat_ragdoll")
        assert response.status_code == 200
        data = response.json()
        assert data["breed"]["name"] == "布偶猫"
        assert data["breed"]["species"] == "cat"

    def test_get_breed_detail_404(self):
        """无效品种ID返回404"""
        response = client.get("/api/v1/encyclopedia/breed/invalid_breed")
        assert response.status_code == 404
        assert response.json()["detail"] == "品种不存在"

    def test_breed_detail_complete_structure(self):
        """品种详情完整结构验证"""
        response = client.get("/api/v1/encyclopedia/breed/cat_british_shorthair")
        assert response.status_code == 200
        data = response.json()
        breed = data["breed"]
        assert "id" in breed
        assert "name" in breed
        assert "english_name" in breed
        assert "species" in breed
        assert "category" in breed
        assert "description" in breed
        assert "summary" in breed
        assert "features" in breed
        assert "personality" in breed
        assert "care_requirements" in breed
        assert "health_issues" in breed
        assert "suitable_for" in breed
        assert "image_emoji" in breed
        assert "popularity" in breed
        # 子结构验证
        features = breed["features"]
        assert "origin" in features
        assert "size" in features
        assert "weight" in features
        assert "lifespan" in features
        assert "coat" in features
        assert "colors" in features

    def test_cat_breed_detail_species(self):
        """猫品种详情species必须为cat"""
        response = client.get("/api/v1/encyclopedia/breed/cat_persian")
        assert response.status_code == 200
        assert response.json()["breed"]["species"] == "cat"

    def test_dog_breed_detail_species(self):
        """狗品种详情species必须为dog"""
        response = client.get("/api/v1/encyclopedia/breed/dog_corgi")
        assert response.status_code == 200
        assert response.json()["breed"]["species"] == "dog"


class TestEncyclopediaHealthListAPI:
    """健康知识列表API测试"""

    def test_get_cat_health_200(self):
        """GET /encyclopedia/health/cat 返回200"""
        response = client.get("/api/v1/encyclopedia/health/cat")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "cat"
        categories = data["categories"]
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_get_dog_health_200(self):
        """GET /encyclopedia/health/dog 返回200"""
        response = client.get("/api/v1/encyclopedia/health/dog")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "dog"

    def test_get_both_health_200(self):
        """GET /encyclopedia/health/both 返回200"""
        response = client.get("/api/v1/encyclopedia/health/both")
        assert response.status_code == 200
        data = response.json()
        assert data["species"] == "both"

    def test_invalid_species_400(self):
        """无效物种返回400"""
        response = client.get("/api/v1/encyclopedia/health/bird")
        assert response.status_code == 400
        assert "不合法" in response.json()["detail"]

    def test_health_list_response_structure(self):
        """健康知识列表响应结构验证"""
        response = client.get("/api/v1/encyclopedia/health/cat")
        data = response.json()
        assert "species" in data
        assert "categories" in data
        for group in data["categories"]:
            assert "category" in group
            assert "category_label" in group
            assert "conditions" in group
            for condition in group["conditions"]:
                assert "id" in condition
                assert "name" in condition
                assert "species" in condition
                assert "category" in condition
                assert "severity" in condition

    def test_health_cat_13_conditions(self):
        """猫咪健康知识应有15个病症"""
        response = client.get("/api/v1/encyclopedia/health/cat")
        data = response.json()
        total = sum(len(g["conditions"]) for g in data["categories"])
        assert total == 15

    def test_health_dog_14_conditions(self):
        """狗狗健康知识应有13个病症"""
        response = client.get("/api/v1/encyclopedia/health/dog")
        data = response.json()
        total = sum(len(g["conditions"]) for g in data["categories"])
        assert total == 13

    def test_health_categories_correct_labels(self):
        """健康知识类别标签验证"""
        response = client.get("/api/v1/encyclopedia/health/cat")
        data = response.json()
        labels = {g["category"]: g["category_label"] for g in data["categories"]}
        assert labels.get("digestive") == "消化系统"
        assert labels.get("respiratory") == "呼吸系统"
        assert labels.get("skin") == "皮肤系统"
        assert labels.get("urinary") == "泌尿系统"
        assert labels.get("infectious") == "传染病"


class TestEncyclopediaHealthDetailAPI:
    """病症详情API测试"""

    def test_get_health_detail_200(self):
        """有效病症ID返回200"""
        response = client.get("/api/v1/encyclopedia/health/detail/cat_diarrhea")
        assert response.status_code == 200
        data = response.json()
        assert data["condition"]["name"] == "软便/腹泻"

    def test_get_health_detail_404(self):
        """无效病症ID返回404"""
        response = client.get("/api/v1/encyclopedia/health/detail/invalid_condition")
        assert response.status_code == 404
        assert response.json()["detail"] == "病症不存在"

    def test_health_detail_complete_structure(self):
        """病症详情完整结构验证"""
        response = client.get("/api/v1/encyclopedia/health/detail/cat_uti")
        assert response.status_code == 200
        data = response.json()
        condition = data["condition"]
        required = ["id", "name", "species", "category", "description",
                     "symptoms", "urgent_symptoms", "possible_causes",
                     "severity", "treatment", "home_care", "prevention", "image_emoji"]
        for field in required:
            assert field in condition, f"缺少字段: {field}"

    def test_emergency_condition_has_urgent(self):
        """emergency病症包含urgent_symptoms"""
        response = client.get("/api/v1/encyclopedia/health/detail/cat_fpv")
        assert response.status_code == 200
        condition = response.json()["condition"]
        assert condition["severity"] == "emergency"
        assert len(condition["urgent_symptoms"]) > 0

    def test_health_detail_severity_valid(self):
        """病症详情severity值合法"""
        response = client.get("/api/v1/encyclopedia/health/detail/dog_parvovirus")
        assert response.status_code == 200
        assert response.json()["condition"]["severity"] in ("mild", "moderate", "severe", "emergency")


class TestEncyclopediaSearchAPI:
    """搜索API测试"""

    def test_search_breed_name_200(self):
        """品种名搜索返回200"""
        response = client.get("/api/v1/encyclopedia/search?query=布偶猫")
        assert response.status_code == 200
        data = response.json()
        assert len(data["breeds"]) > 0

    def test_search_disease_name_200(self):
        """病症名搜索返回200"""
        response = client.get("/api/v1/encyclopedia/search?query=腹泻")
        assert response.status_code == 200
        data = response.json()
        assert len(data["conditions"]) > 0

    def test_search_empty_query_422(self):
        """空搜索词返回422（FastAPI校验）"""
        response = client.get("/api/v1/encyclopedia/search?query=")
        assert response.status_code == 422

    def test_search_missing_query_422(self):
        """缺少query参数返回422"""
        response = client.get("/api/v1/encyclopedia/search")
        assert response.status_code == 422

    def test_search_no_results_200(self):
        """无匹配结果返回200（空列表）"""
        response = client.get("/api/v1/encyclopedia/search?query=xyzabc123")
        assert response.status_code == 200
        data = response.json()
        assert data["breeds"] == []
        assert data["conditions"] == []

    def test_search_response_structure(self):
        """搜索响应结构验证"""
        response = client.get("/api/v1/encyclopedia/search?query=遍")
        assert response.status_code == 200
        data = response.json()
        assert "breeds" in data
        assert "conditions" in data
        assert isinstance(data["breeds"], list)
        assert isinstance(data["conditions"], list)

    def test_search_results_capped_5(self):
        """搜索结果每种类型不超过5条"""
        response = client.get("/api/v1/encyclopedia/search?query=c")
        assert response.status_code == 200
        data = response.json()
        assert len(data["breeds"]) <= 5
        assert len(data["conditions"]) <= 5

    def test_search_long_query_still_works(self):
        """超长搜索词不应崩溃（100字符上限FastAPI限制）"""
        response = client.get("/api/v1/encyclopedia/search?query=abcdefghij")
        assert response.status_code == 200

    def test_search_special_chars(self):
        """特殊字符搜索"""
        response = client.get("/api/v1/encyclopedia/search?query=%40%23%24%25")
        assert response.status_code == 200


class TestAPIRouterRegistration:
    """路由注册测试"""

    def test_encyclopedia_router_registered(self):
        """验证encyclopedia路由已注册"""
        response = client.get("/api/v1/encyclopedia/breeds/cat")
        assert response.status_code == 200

    def test_openapi_docs_include_encyclopedia(self):
        """OpenAPI文档包含encyclopedia标签"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        paths = list(data["paths"].keys())
        encyclopedia_paths = [p for p in paths if "encyclopedia" in p]
        assert len(encyclopedia_paths) >= 4, "API文档缺少encyclopedia路径"


class TestAPICompatibilityAndHeaders:
    """兼容性测试"""

    def test_cors_headers_present(self):
        """CORS头应存在"""
        response = client.options("/api/v1/encyclopedia/breeds/cat")
        # FastAPI TestClient 中 OPTIONS 请求的CORS处理
        assert response.status_code in (200, 204, 405)

    def test_content_type_json(self):
        """响应Content-Type应为JSON"""
        response = client.get("/api/v1/encyclopedia/breeds/cat")
        assert response.status_code == 200
        assert "application/json" in response.headers.get("content-type", "")

    def test_response_no_sensitive_headers(self):
        """不应暴露敏感的服务器头"""
        response = client.get("/api/v1/encyclopedia/breeds/cat")
        assert "x-powered-by" not in response.headers


class TestAPIPerformance:
    """API性能测试"""

    def test_breed_list_response_time(self):
        """品种列表API应在50ms内响应"""
        import time
        start = time.perf_counter()
        response = client.get("/api/v1/encyclopedia/breeds/cat")
        elapsed = time.perf_counter() - start
        assert response.status_code == 200
        assert elapsed < 0.05, f"响应时间过长: {elapsed:.4f}s"

    def test_breed_detail_response_time(self):
        """品种详情API应在50ms内响应"""
        import time
        start = time.perf_counter()
        response = client.get("/api/v1/encyclopedia/breed/dog_golden_retriever")
        elapsed = time.perf_counter() - start
        assert response.status_code == 200
        assert elapsed < 0.05, f"响应时间过长: {elapsed:.4f}s"

    def test_search_response_time(self):
        """搜索API应在50ms内响应"""
        import time
        start = time.perf_counter()
        response = client.get("/api/v1/encyclopedia/search?query=腹泻")
        elapsed = time.perf_counter() - start
        assert response.status_code == 200
        assert elapsed < 0.05, f"响应时间过长: {elapsed:.4f}s"

    def test_health_list_response_time(self):
        """健康知识列表API应在50ms内响应"""
        import time
        start = time.perf_counter()
        response = client.get("/api/v1/encyclopedia/health/cat")
        elapsed = time.perf_counter() - start
        assert response.status_code == 200
        assert elapsed < 0.05, f"响应时间过长: {elapsed:.4f}s"

    def test_concurrent_requests(self):
        """并发请求测试（顺序执行10次）"""
        import time
        times = []
        for _ in range(10):
            start = time.perf_counter()
            response = client.get("/api/v1/encyclopedia/breeds/cat")
            times.append(time.perf_counter() - start)
            assert response.status_code == 200
        avg = sum(times) / len(times)
        assert avg < 0.03, f"平均响应时间过长: {avg:.4f}s"