"""
行为分析 API 集成测试
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestBehaviorAnalyzeAPI:
    """行为分析 API 测试"""

    def test_behavior_analyze(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试行为分析端点"""
        with patch("src.tools.behavior_tools.BehaviorAnalysisTool._run") as mock_run:
            mock_run.return_value = {
                "pet_id": created_pet["pet_id"],
                "pet_name": "旺财",
                "behavior_category": "destructive",
                "possible_causes": [
                    {"cause": "运动量不足", "probability": 0.8, "category": "breed"},
                    {"cause": "分离焦虑", "probability": 0.5, "category": "environment"},
                ],
                "breed_analysis": {
                    "breed": "金毛寻回犬",
                    "energy_level": "高",
                    "relevance": "low",
                },
                "recommendations": ["每日至少1-1.5小时运动", "增加益智玩具"],
                "severity_level": 2,
                "disclaimer": "以上分析仅供参考",
            }

            response = client.post(
                "/api/v1/behavior/analyze",
                headers=auth_headers,
                json={
                    "pet_id": created_pet["pet_id"],
                    "behavior_description": "最近总拆家",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "analysis_id" in data
            assert "analysis_result" in data
            if "analysis_result" in data and isinstance(data["analysis_result"], dict):
                assert "possible_causes" in data["analysis_result"] or "recommendations" in data["analysis_result"]
            else:
                assert "possible_causes" in data or "recommendations" in data
            assert "recommendations" in data or ("analysis_result" in data and "recommendations" in data.get("analysis_result", {}))
            assert "severity_level" in data

    def test_behavior_analyze_with_category(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试指定行为类别的分析"""
        with patch("src.tools.behavior_tools.BehaviorAnalysisTool._run") as mock_run:
            mock_run.return_value = {
                "pet_id": created_pet["pet_id"],
                "pet_name": "旺财",
                "behavior_category": "howling",
                "possible_causes": [],
                "recommendations": ["脱敏训练"],
                "severity_level": 2,
                "disclaimer": "以上分析仅供参考",
            }

            response = client.post(
                "/api/v1/behavior/analyze",
                headers=auth_headers,
                json={
                    "pet_id": created_pet["pet_id"],
                    "behavior_description": "不停嚎叫",
                    "behavior_category": "howling",
                },
            )
            assert response.status_code == 200

    def test_analyze_nonexistent_pet(self, client: TestClient, auth_headers: dict):
        """测试分析不存在的宠物"""
        response = client.post(
            "/api/v1/behavior/analyze",
            headers=auth_headers,
            json={
                "pet_id": "nonexistent-id",
                "behavior_description": "拆家",
            },
        )
        assert response.status_code == 404

    def test_analyze_other_users_pet(self, client: TestClient, auth_headers: dict, second_auth_headers: dict):
        """测试不能分析别人的宠物"""
        pet_resp = client.post(
            "/api/v1/pets",
            headers=auth_headers,
            json={"name": "小花", "species": "cat", "breed": "英短", "gender": "female"},
        )
        pet_id = pet_resp.json()["pet_id"]

        response = client.post(
            "/api/v1/behavior/analyze",
            headers=second_auth_headers,
            json={"pet_id": pet_id, "behavior_description": "嚎叫"},
        )
        assert response.status_code == 403

    def test_list_behavior_history(self, client: TestClient, auth_headers: dict):
        """测试获取行为分析历史"""
        response = client.get(
            "/api/v1/behavior/history",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_list_pet_behavior_history(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试获取特定宠物行为分析历史"""
        response = client.get(
            f"/api/v1/behavior/history/{created_pet['pet_id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_pet_history_nonexistent_pet(self, client: TestClient, auth_headers: dict):
        """测试获取不存在宠物的历史"""
        response = client.get(
            "/api/v1/behavior/history/nonexistent",
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_pet_history_other_users_pet(self, client: TestClient, auth_headers: dict, second_auth_headers: dict):
        """测试不能获取别人宠物的历史"""
        pet_resp = client.post(
            "/api/v1/pets",
            headers=auth_headers,
            json={"name": "小花", "species": "cat", "breed": "英短", "gender": "female"},
        )
        pet_id = pet_resp.json()["pet_id"]

        response = client.get(
            f"/api/v1/behavior/history/{pet_id}",
            headers=second_auth_headers,
        )
        assert response.status_code == 403


class TestTrainingRecommendationAPI:
    """训练建议 API 测试"""

    def test_training_recommendation(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试获取训练建议"""
        with patch("src.tools.behavior_tools.TrainingRecommendationTool._run") as mock_run:
            mock_run.return_value = {
                "pet_id": created_pet["pet_id"],
                "pet_name": "旺财",
                "behavior_category": "destructive",
                "breed_specific_advice": ["金毛精力高，必须保证充足运动量"],
                "training_plan": [
                    {"name": "增加运动量", "description": "确保每日充足运动消耗精力", "duration": "持续2-4周见效"},
                ],
                "tips": ["不要事后惩罚"],
                "disclaimer": "以上训练建议仅供参考",
            }

            response = client.post(
                "/api/v1/behavior/training",
                headers=auth_headers,
                json={
                    "pet_id": created_pet["pet_id"],
                    "behavior_category": "destructive",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "training_plan" in data
            assert "breed_specific_advice" in data

    def test_training_nonexistent_pet(self, client: TestClient, auth_headers: dict):
        """测试不存在的宠物获取训练建议"""
        response = client.post(
            "/api/v1/behavior/training",
            headers=auth_headers,
            json={
                "pet_id": "nonexistent-id",
                "behavior_category": "destructive",
            },
        )
        assert response.status_code == 404

    def test_training_other_users_pet(self, client: TestClient, auth_headers: dict, second_auth_headers: dict):
        """测试不能获取别人宠物的训练建议"""
        pet_resp = client.post(
            "/api/v1/pets",
            headers=auth_headers,
            json={"name": "小花", "species": "cat", "breed": "布偶猫", "gender": "female"},
        )
        pet_id = pet_resp.json()["pet_id"]

        response = client.post(
            "/api/v1/behavior/training",
            headers=second_auth_headers,
            json={"pet_id": pet_id, "behavior_category": "howling"},
        )
        assert response.status_code == 403


class TestBehaviorAuth:
    """行为分析认证测试"""

    def test_unauthorized_analyze(self, client: TestClient):
        """测试未认证访问行为分析"""
        response = client.post(
            "/api/v1/behavior/analyze",
            json={"pet_id": "x", "behavior_description": "拆家"},
        )
        assert response.status_code == 401

    def test_unauthorized_history(self, client: TestClient):
        """测试未认证访问历史"""
        response = client.get("/api/v1/behavior/history")
        assert response.status_code == 401

    def test_unauthorized_training(self, client: TestClient):
        """测试未认证访问训练建议"""
        response = client.post(
            "/api/v1/behavior/training",
            json={"pet_id": "x"},
        )
        assert response.status_code == 401
