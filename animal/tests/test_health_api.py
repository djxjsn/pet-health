"""
健康咨询 API 集成测试
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestHealthConsultAPI:
    """健康咨询 API 测试"""

    def test_health_consult(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试健康咨询端点"""
        with patch("src.tools.health_tools.HealthConsultTool._run") as mock_run:
            mock_run.return_value = {
                "pet_id": created_pet["pet_id"],
                "pet_name": "旺财",
                "symptoms": ["呕吐"],
                "diagnosis_result": {
                    "possible_conditions": [{"name": "消化不良", "description": "可能因饮食不当引起", "confidence": 0.7}],
                    "recommendations": ["观察饮食", "少量多餐"],
                    "severity": "中等",
                    "vet_recommended": False,
                },
                "urgency_level": 2,
                "urgency_reasoning": "检测到中等症状",
                "recommendations": ["观察饮食", "少量多餐"],
                "disclaimer": "以上建议仅供参考",
            }

            response = client.post(
                "/api/v1/health/consult",
                headers=auth_headers,
                json={
                    "pet_id": created_pet["pet_id"],
                    "symptoms": ["呕吐"],
                    "description": "今天早上开始呕吐",
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "consultation_id" in data
            assert "urgency_level" in data
            assert "diagnosis_result" in data

    def test_symptom_analysis(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试症状分析端点（不创建记录）"""
        with patch("src.tools.health_tools.HealthConsultTool._run") as mock_consult, \
             patch("src.tools.health_tools.UrgencyAssessmentTool._run") as mock_urgency:
            mock_consult.return_value = {
                "diagnosis_result": {
                    "possible_conditions": [{"name": "感冒", "confidence": 0.6}],
                    "recommendations": ["注意保暖"],
                },
                "recommendations": ["注意保暖"],
            }
            mock_urgency.return_value = {"urgency_level": 2, "reasoning": "轻微"}

            response = client.post(
                "/api/v1/health/analyze",
                headers=auth_headers,
                json={
                    "pet_id": created_pet["pet_id"],
                    "symptoms": ["打喷嚏", "流鼻涕"],
                },
            )
            assert response.status_code == 200
            data = response.json()
            assert "diagnosis_result" in data or "possible_conditions" in data
            assert "urgency_level" in data

    def test_consult_nonexistent_pet(self, client: TestClient, auth_headers: dict):
        """测试咨询不存在的宠物"""
        response = client.post(
            "/api/v1/health/consult",
            headers=auth_headers,
            json={
                "pet_id": "nonexistent-id",
                "symptoms": ["呕吐"],
            },
        )
        assert response.status_code == 404

    def test_consult_other_users_pet(self, client: TestClient, auth_headers: dict, second_auth_headers: dict):
        """测试不能咨询别人的宠物"""
        # 用第一个用户创建宠物
        pet_resp = client.post(
            "/api/v1/pets",
            headers=auth_headers,
            json={"name": "小花", "species": "cat", "breed": "英短", "gender": "female"},
        )
        pet_id = pet_resp.json()["pet_id"]

        # 用第二个用户尝试咨询
        response = client.post(
            "/api/v1/health/consult",
            headers=second_auth_headers,
            json={"pet_id": pet_id, "symptoms": ["不吃东西"]},
        )
        assert response.status_code == 403

    def test_list_consultations(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试获取咨询历史"""
        response = client.get(
            "/api/v1/health/consultations",
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_health_record(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试手动添加健康记录"""
        response = client.post(
            f"/api/v1/health/records?pet_id={created_pet['pet_id']}",
            headers=auth_headers,
            json={
                "record_type": "vaccine",
                "diagnosis": "狂犬疫苗接种",
                "vet_name": "张医生",
                "hospital": "宠物医院",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["record_type"] == "vaccine"
        assert data["diagnosis"] == "狂犬疫苗接种"

    def test_list_health_records(self, client: TestClient, auth_headers: dict, created_pet: dict):
        """测试获取健康记录列表"""
        # 先创建一条记录
        client.post(
            f"/api/v1/health/records?pet_id={created_pet['pet_id']}",
            headers=auth_headers,
            json={"record_type": "checkup", "diagnosis": "体检正常"},
        )

        response = client.get(
            f"/api/v1/health/records/{created_pet['pet_id']}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_unauthorized_health_access(self, client: TestClient):
        """测试未认证访问健康端点"""
        response = client.get("/api/v1/health/consultations")
        assert response.status_code == 401

        response = client.post(
            "/api/v1/health/consult",
            json={"pet_id": "x", "symptoms": ["x"]},
        )
        assert response.status_code == 401
