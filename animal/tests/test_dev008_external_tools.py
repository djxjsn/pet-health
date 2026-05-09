"""
DEV-008 外部 API 工具单元测试

测试天气查询、地图服务、网络搜索、图像识别等外部集成工具
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


class TestWeatherTool:
    """天气查询工具测试"""

    @pytest.fixture
    def tool(self):
        from src.tools.external_tools import WeatherTool
        return WeatherTool()

    def test_tool_initialization(self, tool):
        """测试工具初始化"""
        assert tool.name == "get_weather"
        assert "天气" in tool.description

    def test_weather_query_basic(self, tool):
        """测试基本天气查询"""
        result = tool._run(city="北京", days=3)

        assert result is not None
        assert result["city"] == "北京"
        assert "forecast" in result
        assert "current" in result
        assert "pet_advice" in result
        assert len(result["forecast"]) == 3

    def test_weather_query_single_day(self, tool):
        """测试单日天气预报"""
        result = tool._run(city="上海", days=1)

        assert len(result["forecast"]) == 1

    def test_weather_query_max_days(self, tool):
        """测试最大预报天数"""
        result = tool._run(city="广州", days=7)

        assert len(result["forecast"]) == 7

    def test_pet_advice_generation(self, tool):
        """测试宠物建议生成"""
        with patch.object(tool, '_fetch_weather_data') as mock_fetch:
            mock_fetch.return_value = {
                "current": {"temp": 35, "condition": "晴", "humidity": 85},
                "forecast": []
            }
            result = tool._run(city="深圳")

            advice = result["pet_advice"]
            assert isinstance(advice, list)
            assert len(advice) > 0

    def test_hot_weather_advice(self, tool):
        """测试高温天气建议"""
        with patch.object(tool, '_fetch_weather_data') as mock_fetch:
            mock_fetch.return_value = {
                "current": {"temp": 33, "condition": "晴", "humidity": 60},
                "forecast": []
            }
            result = tool._run(city="武汉")

            advice_text = " ".join(result["pet_advice"])
            assert "高温" in advice_text or "防暑" in advice_text or "饮水" in advice_text

    def test_rainy_weather_advice(self, tool):
        """测试雨天建议"""
        with patch.object(tool, '_fetch_weather_data') as mock_fetch:
            mock_fetch.return_value = {
                "current": {"temp": 22, "condition": "小雨", "humidity": 90},
                "forecast": []
            }
            result = tool._run(city="杭州")

            advice_text = " ".join(result["pet_advice"])
            assert "雨" in advice_text


class TestMapServiceTool:
    """地图/位置服务工具测试"""

    @pytest.fixture
    def tool(self):
        from src.tools.external_tools import MapServiceTool
        return MapServiceTool()

    def test_tool_initialization(self, tool):
        """测试工具初始化"""
        assert tool.name == "search_nearby"
        assert "附近" in tool.description

    def test_search_hospital(self, tool):
        """测试搜索宠物医院"""
        result = tool._run(
            location="北京市朝阳区",
            query_type="hospital",
            radius=5.0
        )

        assert result is not None
        assert result["query_type"] == "hospital"
        assert result["total"] >= 3
        assert all("name" in r for r in result["results"])

    def test_search_vet(self, tool):
        """测试搜索兽医诊所"""
        result = tool._run(
            location="上海市浦东新区",
            query_type="vet"
        )

        assert result["type_name"] == "兽医诊所"

    def test_search_shop(self, tool):
        """测试搜索宠物商店"""
        result = tool._run(
            location="广州市天河区",
            query_type="shop"
        )

        assert result["type_name"] == "宠物用品店"

    def test_result_distance_sorting(self, tool):
        """测试结果按距离排序"""
        result = tool._run(
            location="深圳市南山区",
            query_type="hospital"
        )

        distances = [r["distance_km"] for r in result["results"]]
        assert distances == sorted(distances)

    def test_radius_limit(self, tool):
        """测试搜索半径限制"""
        result = tool._run(
            location="成都市武侯区",
            query_type="park",
            radius=2.0
        )

        for r in result["results"]:
            assert r["distance_km"] <= 2.0

    def test_invalid_type_handling(self, tool):
        """测试无效类型处理"""
        result = tool._run(
            location="武汉市洪山区",
            query_type="invalid_type"
        )

        assert result is not None


class TestWebSearchTool:
    """网络搜索工具测试"""

    @pytest.fixture
    def tool(self):
        from src.tools.external_tools import WebSearchTool
        return WebSearchTool()

    def test_tool_initialization(self, tool):
        """测试工具初始化"""
        assert tool.name == "web_search"
        assert "搜索" in tool.description

    def test_basic_search(self, tool):
        """测试基本搜索"""
        result = tool._run(query="狗狗软便怎么办")

        assert result is not None
        assert result["query"] == "狗狗软便怎么办"
        assert "results" in result
        assert len(result["results"]) <= 5
        assert result["total"] == len(result["results"])

    def test_max_results_limit(self, tool):
        """测试最大结果数限制"""
        result = tool._run(query="猫咪掉毛", max_results=3)

        assert len(result["results"]) <= 3

    def test_result_structure(self, tool):
        """测试结果结构"""
        result = tool._run(query="宠物疫苗")

        if result.get("results"):
            first_result = result["results"][0]
            assert "title" in first_result
            assert "url" in first_result
            assert "snippet" in first_result
            assert "source" in first_result

    def test_relevance_score_range(self, tool):
        """测试相关度分数范围"""
        result = tool._run(query="狗粮推荐")

        for r in result.get("results", []):
            score = r.get("relevance_score", 0)
            assert 0 <= score <= 1

    def test_error_handling(self, tool):
        """测试错误处理"""
        with patch.object(tool, '_perform_search', side_effect=Exception("网络错误")):
            result = tool._run(query="test")

            assert "error" in result
            assert result["results"] == []


class TestImageRecognitionTool:
    """图像识别工具测试"""

    @pytest.fixture
    def tool(self):
        from src.tools.external_tools import ImageRecognitionTool
        return ImageRecognitionTool()

    def test_tool_initialization(self, tool):
        """测试工具初始化"""
        assert tool.name == "recognize_image"
        assert "识别" in tool.description

    def test_no_image_input(self, tool):
        """测试无图片输入"""
        result = tool._run(recognition_type="pet_breed")

        assert "error" in result
        assert "请提供" in result["error"]

    def test_breed_recognition_dog(self, tool):
        """测试犬类品种识别"""
        with patch('random.random', return_value=0.3):
            result = tool._run(
                recognition_type="pet_breed",
                image_url="https://example.com/dog.jpg"
            )

        assert result is not None
        assert result["recognition_type"] == "pet_breed"
        assert result["result"]["species"] == "dog"
        assert "breed" in result["result"]

    def test_breed_recognition_cat(self, tool):
        """测试猫类品种识别"""
        with patch('random.random', return_value=0.7):
            result = tool._run(
                recognition_type="pet_breed",
                image_url="https://example.com/cat.jpg"
            )

            assert result["result"]["species"] == "cat"

    def test_symptom_recognition(self, tool):
        """测试症状识别"""
        result = tool._run(
            recognition_type="symptom",
            image_url="https://example.com/symptom.jpg"
        )

        assert result["result"]["detected_symptom"] is not None
        assert "severity" in result["result"]

    def test_food_recognition(self, tool):
        """测试食物识别"""
        result = tool._run(
            recognition_type="food",
            image_url="https://example.com/food.jpg"
        )

        assert result["result"]["food_type"] is not None
        assert "category" in result["result"]

    def test_nutrition_label_recognition(self, tool):
        """测试营养标签识别"""
        result = tool._run(
            recognition_type="nutrition_label",
            image_url="https://example.com/label.jpg"
        )

        assert "ingredients_detected" in result["result"]
        assert "guaranteed_analysis" in result["result"]

    def test_confidence_score(self, tool):
        """测试置信度分数"""
        result = tool._run(
            recognition_type="pet_breed",
            image_url="https://example.com/test.jpg"
        )

        confidence = result.get("confidence", 0)
        assert 0 < confidence <= 1


class TestKnowledgeEnhanceTool:
    """知识库增强工具测试"""

    @pytest.fixture
    def tool(self):
        from src.tools.external_tools import KnowledgeEnhanceTool
        return KnowledgeEnhanceTool()

    def test_tool_initialization(self, tool):
        """测试工具初始化"""
        assert tool.name == "enhance_knowledge"
        assert "增强" in tool.description

    def test_basic_enhancement(self, tool):
        """测试基本知识增强"""
        with patch.object(tool, '_get_internal_knowledge', return_value=[
            {"content": "知识1", "relevance": 0.9}
        ]):
            with patch.object(tool, '_get_external_info', return_value=[]):
                result = tool._run(topic="狗狗疫苗")

                assert result is not None
                assert result["topic"] == "狗狗疫苗"
                assert "internal_knowledge" in result

    def test_deep_enhancement(self, tool):
        """测试深度增强模式"""
        with patch.object(tool, '_get_internal_knowledge', return_value=[
            {"content": "知识内容"}
        ]):
            with patch.object(tool, '_get_external_info', return_value=[{}]):
                with patch.object(tool, '_generate_expert_summary', return_value={}):
                    result = tool._run(
                        topic="猫肾病",
                        depth="deep"
                    )

                    assert result["depth"] == "deep"
                    assert "expert_summary" in result

    def test_quick_mode(self, tool):
        """测试快速模式（无外部信息）"""
        with patch.object(tool, '_get_internal_knowledge', return_value=[]):
            result = tool._run(topic="测试主题", depth="quick")

            assert result["external_info"] == []

    def test_with_context(self, tool):
        """测试带上下文的增强"""
        with patch.object(tool, '_get_internal_knowledge', return_value=[]):
            result = tool._run(
                topic="过敏",
                context="金毛犬，3岁，最近出现皮肤红肿"
            )

            assert result is not None

    def test_error_handling(self, tool):
        """测试错误处理"""
        with patch.object(tool, '_get_internal_knowledge', side_effect=Exception("DB错误")):
            result = tool._run(topic="测试")

            assert "error" in result


class TestExternalToolsIntegration:
    """外部工具集成测试"""

    def test_all_external_tools_registered(self):
        """测试所有外部工具已注册"""
        from src.tools.tool_registry import get_tool_registry
        
        registry = get_tool_registry()
        tools = registry.list_tools()
        
        external_tools = [
            "get_weather",
            "search_nearby",
            "web_search",
            "recognize_image",
            "enhance_knowledge"
        ]
        
        for tool_name in external_tools:
            assert tool_name in tools, f"外部工具 {tool_name} 未注册"

    def test_tool_schemas_valid(self):
        """测试工具 Schema 有效"""
        from src.tools.tool_registry import get_tool_registry
        
        registry = get_tool_registry()
        schemas = registry.get_tools_schema()
        
        for schema in schemas:
            assert "name" in schema
            assert "description" in schema
            assert "parameters" in schema
