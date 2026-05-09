"""
宠物档案端点测试
"""
import pytest
from fastapi.testclient import TestClient


class TestCreatePet:
    """创建宠物档案测试"""

    def test_create_pet_success(self, client: TestClient, auth_headers: dict, test_pet_data: dict):
        response = client.post("/api/v1/pets", json=test_pet_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_pet_data["name"]
        assert data["species"] == test_pet_data["species"]
        assert data["breed"] == test_pet_data["breed"]
        assert data["gender"] == test_pet_data["gender"]
        assert data["weight"] == test_pet_data["weight"]
        assert data["is_vaccinated"] == test_pet_data["is_vaccinated"]
        assert data["is_neutered"] == test_pet_data["is_neutered"]
        assert "pet_id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_pet_minimal(self, client: TestClient, auth_headers: dict):
        minimal_data = {"name": "小黑", "species": "cat"}

        response = client.post("/api/v1/pets", json=minimal_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "小黑"
        assert data["species"] == "cat"
        assert data["gender"] == "unknown"
        assert data["is_vaccinated"] == False
        assert data["is_neutered"] == False

    def test_create_pet_without_auth(self, client: TestClient, test_pet_data: dict):
        response = client.post("/api/v1/pets", json=test_pet_data)

        assert response.status_code == 401

    def test_create_pet_invalid_species(self, client: TestClient, auth_headers: dict):
        invalid_data = {"name": "测试宠物", "species": "dragon"}

        response = client.post("/api/v1/pets", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_pet_empty_name(self, client: TestClient, auth_headers: dict):
        invalid_data = {"name": "", "species": "dog"}

        response = client.post("/api/v1/pets", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_pet_invalid_gender(self, client: TestClient, auth_headers: dict):
        invalid_data = {"name": "测试", "species": "dog", "gender": "invalid"}

        response = client.post("/api/v1/pets", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_pet_negative_weight(self, client: TestClient, auth_headers: dict):
        invalid_data = {"name": "测试", "species": "dog", "weight": "-5.0"}

        response = client.post("/api/v1/pets", json=invalid_data, headers=auth_headers)

        assert response.status_code == 422

    def test_create_pet_species_case_insensitive(self, client: TestClient, auth_headers: dict):
        data = {"name": "小花", "species": "DOG"}

        response = client.post("/api/v1/pets", json=data, headers=auth_headers)

        assert response.status_code == 201
        assert response.json()["species"] == "dog"

    def test_create_pet_missing_required_fields(self, client: TestClient, auth_headers: dict):
        response = client.post("/api/v1/pets", json={}, headers=auth_headers)

        assert response.status_code == 422


class TestListPets:
    """获取宠物列表测试"""

    def test_list_pets_empty(self, client: TestClient, auth_headers: dict):
        response = client.get("/api/v1/pets", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_pets_with_data(self, client: TestClient, auth_headers: dict, created_pet: dict):
        response = client.get("/api/v1/pets", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["pet_id"] == created_pet["pet_id"]

    def test_list_pets_pagination(self, client: TestClient, auth_headers: dict):
        for i in range(15):
            pet_data = {"name": f"宠物{i}", "species": "cat"}
            client.post("/api/v1/pets", json=pet_data, headers=auth_headers)

        response = client.get("/api/v1/pets", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1

        response_page2 = client.get("/api/v1/pets?page=2&page_size=10", headers=auth_headers)

        assert response_page2.status_code == 200
        data_page2 = response_page2.json()
        assert len(data_page2["items"]) == 5
        assert data_page2["total"] == 15
        assert data_page2["page"] == 2

    def test_list_pets_custom_page_size(self, client: TestClient, auth_headers: dict):
        for i in range(5):
            pet_data = {"name": f"宠物{i}", "species": "dog"}
            client.post("/api/v1/pets", json=pet_data, headers=auth_headers)

        response = client.get("/api/v1/pets?page_size=3", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["total"] == 5
        assert data["page_size"] == 3

    def test_list_pets_without_auth(self, client: TestClient):
        response = client.get("/api/v1/pets")

        assert response.status_code == 401

    def test_list_pets_user_isolation(self, client: TestClient, auth_headers: dict, second_auth_headers: dict, test_pet_data: dict):
        client.post("/api/v1/pets", json=test_pet_data, headers=auth_headers)

        response = client.get("/api/v1/pets", headers=second_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestGetPetDetail:
    """获取宠物详情测试"""

    def test_get_pet_detail_success(self, client: TestClient, auth_headers: dict, created_pet: dict):
        response = client.get(f"/api/v1/pets/{created_pet['pet_id']}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["pet_id"] == created_pet["pet_id"]
        assert data["name"] == created_pet["name"]
        assert data["species"] == created_pet["species"]

    def test_get_pet_not_found(self, client: TestClient, auth_headers: dict):
        fake_pet_id = "nonexistent-pet-id-1234"

        response = client.get(f"/api/v1/pets/{fake_pet_id}", headers=auth_headers)

        assert response.status_code == 404
        assert "宠物不存在" in response.json()["detail"]

    def test_get_pet_without_auth(self, client: TestClient, created_pet: dict):
        response = client.get(f"/api/v1/pets/{created_pet['pet_id']}")

        assert response.status_code == 401

    def test_get_pet_other_user_forbidden(self, client: TestClient, auth_headers: dict, second_auth_headers: dict, created_pet: dict):
        response = client.get(f"/api/v1/pets/{created_pet['pet_id']}", headers=second_auth_headers)

        assert response.status_code == 403
        assert "无权访问" in response.json()["detail"]


class TestUpdatePet:
    """更新宠物档案测试"""

    def test_update_pet_name(self, client: TestClient, auth_headers: dict, created_pet: dict):
        update_data = {"name": "新名字"}

        response = client.put(f"/api/v1/pets/{created_pet['pet_id']}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新名字"
        assert data["species"] == created_pet["species"]

    def test_update_pet_multiple_fields(self, client: TestClient, auth_headers: dict, created_pet: dict):
        update_data = {
            "weight": "30.00",
            "is_neutered": True,
            "breed": "拉布拉多",
        }

        response = client.put(f"/api/v1/pets/{created_pet['pet_id']}", json=update_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["weight"] == "30.00"
        assert data["is_neutered"] == True
        assert data["breed"] == "拉布拉多"

    def test_update_pet_not_found(self, client: TestClient, auth_headers: dict):
        fake_pet_id = "nonexistent-pet-id-1234"
        update_data = {"name": "新名字"}

        response = client.put(f"/api/v1/pets/{fake_pet_id}", json=update_data, headers=auth_headers)

        assert response.status_code == 404

    def test_update_pet_without_auth(self, client: TestClient, created_pet: dict):
        update_data = {"name": "新名字"}

        response = client.put(f"/api/v1/pets/{created_pet['pet_id']}", json=update_data)

        assert response.status_code == 401

    def test_update_pet_other_user_forbidden(self, client: TestClient, auth_headers: dict, second_auth_headers: dict, created_pet: dict):
        update_data = {"name": "被篡改的名字"}

        response = client.put(f"/api/v1/pets/{created_pet['pet_id']}", json=update_data, headers=second_auth_headers)

        assert response.status_code == 403
        assert "无权修改" in response.json()["detail"]

    def test_update_pet_invalid_species(self, client: TestClient, auth_headers: dict, created_pet: dict):
        update_data = {"species": "dinosaur"}

        response = client.put(f"/api/v1/pets/{created_pet['pet_id']}", json=update_data, headers=auth_headers)

        assert response.status_code == 422

    def test_update_pet_empty_body(self, client: TestClient, auth_headers: dict, created_pet: dict):
        response = client.put(f"/api/v1/pets/{created_pet['pet_id']}", json={}, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == created_pet["name"]


class TestDeletePet:
    """删除宠物档案测试"""

    def test_delete_pet_success(self, client: TestClient, auth_headers: dict, created_pet: dict):
        response = client.delete(f"/api/v1/pets/{created_pet['pet_id']}", headers=auth_headers)

        assert response.status_code == 204

        get_response = client.get(f"/api/v1/pets/{created_pet['pet_id']}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_pet_not_found(self, client: TestClient, auth_headers: dict):
        fake_pet_id = "nonexistent-pet-id-1234"

        response = client.delete(f"/api/v1/pets/{fake_pet_id}", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_pet_without_auth(self, client: TestClient, created_pet: dict):
        response = client.delete(f"/api/v1/pets/{created_pet['pet_id']}")

        assert response.status_code == 401

    def test_delete_pet_other_user_forbidden(self, client: TestClient, auth_headers: dict, second_auth_headers: dict, created_pet: dict):
        response = client.delete(f"/api/v1/pets/{created_pet['pet_id']}", headers=second_auth_headers)

        assert response.status_code == 403
        assert "无权删除" in response.json()["detail"]

    def test_delete_pet_reflects_in_list(self, client: TestClient, auth_headers: dict, test_pet_data: dict):
        create_resp = client.post("/api/v1/pets", json=test_pet_data, headers=auth_headers)
        pet_id = create_resp.json()["pet_id"]

        list_resp = client.get("/api/v1/pets", headers=auth_headers)
        assert list_resp.json()["total"] == 1

        client.delete(f"/api/v1/pets/{pet_id}", headers=auth_headers)

        list_resp_after = client.get("/api/v1/pets", headers=auth_headers)
        assert list_resp_after.json()["total"] == 0


class TestPetCRUDIntegration:
    """宠物档案 CRUD 集成测试"""

    def test_full_crud_lifecycle(self, client: TestClient, auth_headers: dict):
        pet_data = {"name": "小白", "species": "cat", "breed": "英短", "gender": "female", "weight": "4.50"}

        create_resp = client.post("/api/v1/pets", json=pet_data, headers=auth_headers)
        assert create_resp.status_code == 201
        pet_id = create_resp.json()["pet_id"]

        get_resp = client.get(f"/api/v1/pets/{pet_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "小白"

        update_resp = client.put(f"/api/v1/pets/{pet_id}", json={"name": "大白", "weight": "5.00"}, headers=auth_headers)
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "大白"
        assert update_resp.json()["weight"] == "5.00"

        delete_resp = client.delete(f"/api/v1/pets/{pet_id}", headers=auth_headers)
        assert delete_resp.status_code == 204

        get_after_delete = client.get(f"/api/v1/pets/{pet_id}", headers=auth_headers)
        assert get_after_delete.status_code == 404

    def test_multiple_pets_per_user(self, client: TestClient, auth_headers: dict):
        pets = [
            {"name": "猫猫", "species": "cat"},
            {"name": "狗狗", "species": "dog"},
            {"name": "兔兔", "species": "rabbit"},
        ]
        for pet_data in pets:
            resp = client.post("/api/v1/pets", json=pet_data, headers=auth_headers)
            assert resp.status_code == 201

        list_resp = client.get("/api/v1/pets", headers=auth_headers)
        assert list_resp.json()["total"] == 3


class TestPetCountSync:
    """pet_count 冗余字段同步测试"""

    def test_pet_count_increments_on_create(self, client: TestClient, auth_headers: dict):
        me_resp = client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.json()["profile"]["pet_count"] == 0

        client.post("/api/v1/pets", json={"name": "小猫", "species": "cat"}, headers=auth_headers)

        me_resp = client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.json()["profile"]["pet_count"] == 1

    def test_pet_count_decrements_on_delete(self, client: TestClient, auth_headers: dict):
        create_resp = client.post("/api/v1/pets", json={"name": "小狗", "species": "dog"}, headers=auth_headers)
        pet_id = create_resp.json()["pet_id"]

        me_resp = client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.json()["profile"]["pet_count"] == 1

        client.delete(f"/api/v1/pets/{pet_id}", headers=auth_headers)

        me_resp = client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.json()["profile"]["pet_count"] == 0

    def test_pet_count_with_multiple_pets(self, client: TestClient, auth_headers: dict):
        for i in range(3):
            client.post("/api/v1/pets", json={"name": f"宠物{i}", "species": "cat"}, headers=auth_headers)

        me_resp = client.get("/api/v1/users/me", headers=auth_headers)
        assert me_resp.json()["profile"]["pet_count"] == 3
