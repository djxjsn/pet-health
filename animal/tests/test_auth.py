"""
用户认证端点测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestUserRegistration:
    """用户注册测试"""
    
    def test_register_success(self, client: TestClient, test_user_data: dict):
        """测试用户注册成功"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["phone"] == test_user_data["phone"]
        assert data["email"] == test_user_data["email"]
        assert "password_hash" not in data  # 密码不应返回
        assert "user_id" in data
    
    def test_register_duplicate_phone(self, client: TestClient, test_user_data: dict, registered_user: dict):
        """测试手机号重复注册"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "手机号已被注册" in response.json()["detail"]
    
    def test_register_duplicate_email(self, client: TestClient, test_user_data: dict, registered_user: dict):
        """测试邮箱重复注册"""
        duplicate_data = test_user_data.copy()
        duplicate_data["phone"] = "13800000003"
        
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "邮箱已被注册" in response.json()["detail"]
    
    def test_register_invalid_phone(self, client: TestClient):
        """测试无效手机号"""
        invalid_data = {
            "phone": "12345",  # 无效手机号
            "password": "test1234"
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422  # 验证错误
    
    def test_register_weak_password(self, client: TestClient):
        """测试弱密码"""
        invalid_data = {
            "phone": "13800000004",
            "password": "123456"  # 纯数字，不符合要求
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422
    
    def test_register_without_password(self, client: TestClient):
        """测试缺少密码"""
        invalid_data = {
            "phone": "13800000005"
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422


class TestUserLogin:
    """用户登录测试"""
    
    def test_login_success(self, client: TestClient, test_user_data: dict, registered_user: dict):
        """测试登录成功"""
        login_data = {
            "username": test_user_data["phone"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_with_email(self, client: TestClient, test_user_data: dict, registered_user: dict):
        """测试使用邮箱登录"""
        login_data = {
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 200
        assert "access_token" in response.json()
    
    def test_login_wrong_password(self, client: TestClient, test_user_data: dict, registered_user: dict):
        """测试密码错误"""
        login_data = {
            "username": test_user_data["phone"],
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "手机号/邮箱或密码错误" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """测试不存在的用户"""
        login_data = {
            "username": "13800000999",
            "password": "test1234"
        }
        
        response = client.post("/api/v1/auth/login", data=login_data)
        
        assert response.status_code == 401


class TestTokenRefresh:
    """令牌刷新测试"""
    
    def test_refresh_token_success(self, client: TestClient, test_user_data: dict, registered_user: dict):
        """测试刷新令牌成功"""
        # 先登录获取令牌
        login_data = {
            "username": test_user_data["phone"],
            "password": test_user_data["password"]
        }
        login_response = client.post("/api/v1/auth/login", data=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # 使用刷新令牌
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_refresh_invalid_token(self, client: TestClient):
        """测试无效刷新令牌"""
        refresh_data = {"refresh_token": "invalid_token"}
        
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert "无效的刷新令牌" in response.json()["detail"]


class TestForgotPassword:
    """忘记密码测试"""
    
    def test_forgot_password_success(self, client: TestClient, test_user_data: dict, registered_user: dict):
        """测试忘记密码请求成功"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            params={"phone": test_user_data["phone"]}
        )
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_forgot_password_nonexistent_user(self, client: TestClient):
        """测试不存在的用户忘记密码"""
        response = client.post(
            "/api/v1/auth/forgot-password",
            params={"phone": "13800000999"}
        )
        
        assert response.status_code == 200
        # 为了安全，不提示具体错误
        assert "message" in response.json()


class TestResetPassword:
    """重置密码测试"""
    
    def test_reset_password_placeholder(self, client: TestClient):
        """测试重置密码（占位测试）"""
        # TODO: 实现完整的密码重置逻辑后完善测试
        response = client.post(
            "/api/v1/auth/reset-password",
            params={
                "token": "test_reset_token",
                "new_password": "newpass123"
            }
        )
        
        assert response.status_code == 200
        assert "message" in response.json()


class TestProtectedEndpoints:
    """受保护端点测试"""
    
    def test_get_current_user_info(self, client: TestClient, auth_token: str):
        """测试获取当前用户信息"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = client.get("/api/v1/users/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "profile" in data
    
    def test_get_current_user_info_no_auth(self, client: TestClient):
        """测试未认证时获取用户信息"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 401
    
    def test_update_current_user(self, client: TestClient, auth_token: str, test_user_data: dict):
        """测试更新用户信息"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        update_data = {"email": "newemail@example.com"}
        
        response = client.put("/api/v1/users/me", json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == update_data["email"]
    
    def test_update_duplicate_email(self, client: TestClient, auth_token: str, test_user_data: dict, registered_user: dict):
        """测试更新为已被使用的邮箱"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        update_data = {"email": test_user_data["email"]}  # 使用自己的邮箱
        
        response = client.put("/api/v1/users/me", json=update_data, headers=headers)
        
        # 应该成功，因为是更新为自己的邮箱
        assert response.status_code == 200
