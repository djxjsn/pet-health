"""P2 第二阶段：工具质量门禁接入测试"""
from unittest.mock import Mock, patch


def test_symptom_analysis_tool_uses_search_with_quality():
    mock_retriever = Mock()
    mock_retriever.search_with_quality.return_value = {
        "results": [{"content": "可能是胃肠炎", "distance": 0.2}],
        "action": "accept",
        "confidence": 0.82,
    }

    with patch("src.tools.pet_health_tools.get_knowledge_retriever", return_value=mock_retriever):
        from src.tools.pet_health_tools import SymptomAnalysisTool
        tool = SymptomAnalysisTool()
        result = tool._run(symptoms=["呕吐", "腹泻"], pet_species="dog", pet_age=12)

    assert result["quality_action"] == "accept"
    assert "possible_conditions" in result
    assert len(result["possible_conditions"]) == 1
    mock_retriever.search_with_quality.assert_called_once()


def test_nutrition_advice_tool_uses_search_with_quality_and_refuse_fallback(db_session, created_pet):
    mock_retriever = Mock()
    mock_retriever.search_with_quality.return_value = {
        "results": [],
        "action": "refuse",
        "confidence": 0.12,
    }

    with patch("src.tools.pet_health_tools.get_knowledge_retriever", return_value=mock_retriever):
        from src.tools.pet_health_tools import NutritionAdviceTool
        tool = NutritionAdviceTool(db=db_session)
        result = tool._run(pet_id=created_pet["pet_id"], health_condition="慢性肠胃敏感")

    assert result["quality_action"] == "refuse"
    assert len(result["nutrition_recommendations"]) >= 1
    mock_retriever.search_with_quality.assert_called_once()
