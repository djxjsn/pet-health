"""
DEV-008 工具集成模块单元测试

全面测试文件存储、配置管理、工具服务等核心功能。
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any


class TestThirdPartyConfig:
    """第三方配置管理测试"""
    
    def test_default_config_values(self):
        """测试默认配置值"""
        from src.config.third_party_config import ThirdPartyConfig
        
        config = ThirdPartyConfig()
        
        assert config.storage_provider == "local"
        assert config.max_upload_size == 10 * 1024 * 1024
        assert len(config.allowed_image_extensions) > 0
        assert "jpg" in str(config.allowed_image_extensions)
    
    def test_config_model_validation(self):
        """测试配置模型验证"""
        from src.config.third_party_config import ThirdPartyConfig
        from pydantic import ValidationError
        
        # 测试无效的分类
        with pytest.raises(ValidationError):
            ThirdPartyConfig(storage_provider="invalid")
        
        # 测试有效的配置
        config = ThirdPartyConfig(
            storage_provider="minio",
            minio_endpoint="localhost:9000",
            tavily_api_key="test_key"
        )
        
        assert config.storage_provider == "minio"
        assert config.minio_endpoint == "localhost:9000"


class TestLocalFileStorage:
    """本地文件存储服务测试"""
    
    @pytest.fixture
    def storage(self):
        """创建本地存储实例（使用临时目录）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            from src.services.tool_services.local_storage import LocalFileStorage
            storage = LocalFileStorage(base_path=tmpdir)
            storage.initialize()
            yield storage
    
    @pytest.fixture
    def sample_file(self):
        """创建临时测试文件"""
        tmp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False,
            encoding='utf-8'
        )
        tmp_file.write("这是一个测试文件内容")
        tmp_file.close()
        return tmp_file.name
    
    def test_initialize_success(self, storage):
        """测试初始化成功"""
        assert storage.is_available()
    
    def test_upload_and_get_url(self, storage, sample_file):
        """测试上传文件和获取URL"""
        file_url = storage.upload_file(sample_file, folder="test")
        
        assert file_url is not None
        assert "/uploads/test/" in file_url or "test" in file_url
        
        # 验证文件存在
        file_path = storage.get_file_path(file_url)
        assert file_path.exists()
    
    def test_upload_image(self, storage, sample_file):
        """测试上传图片"""
        image_url = storage.upload_image(sample_file, folder="images")
        
        assert image_url is not None
        assert "images" in image_url
    
    def test_delete_file(self, storage, sample_file):
        """测试删除文件"""
        file_url = storage.upload_file(sample_file)
        
        success = storage.delete_file(file_url)
        
        assert success == True
    
    def test_nonexistent_file_deletion(self, storage):
        """测试删除不存在的文件"""
        success = storage.delete_file("/uploads/nonexistent/file.txt")
        
        assert success == False


class TestMinIOFileStorage:
    """MinIO 文件存储服务测试"""
    
    def test_minio_not_available_without_installation(self):
        """测试未安装 MinIO SDK 时的行为"""
        from src.services.tool_services.minio_storage import MINIO_AVAILABLE
        
        if not MINIO_AVAILABLE:
            storage = self._create_minio_storage()
            
            result = storage.initialize()
            assert result == False
            
            assert storage.is_available() == False
        else:
            pytest.skip("Minio SDK 已安装，跳过此测试")
    
    def _create_minio_storage(self):
        """创建 MinIO 存储实例"""
        from src.services.tool_services.minio_storage import MinIOFileStorage
        return MinIOFileStorage()


class TestBaiduImageRecognition:
    """百度 AI 图像识别服务测试"""
    
    def test_service_initialization_without_config(self):
        """测试无配置时的初始化行为"""
        from src.services.tool_services.baidu_image_recognition import (
            BaiduImageRecognition,
            BAIDU_AIP_AVAILABLE
        )
        
        service = BaiduImageRecognition()
        
        if not BAIDU_AIP_AVAILABLE:
            result = service.initialize()
            assert result == False
        elif not all([service.config.baidu_app_id,
                     service.config.baidu_api_key,
                     service.config.baidu_secret_key]):
            result = service.initialize()
            assert result == False
    
    def test_service_unavailable_before_init(self):
        """测试未初始化时服务不可用"""
        from src.services.tool_services.baidu_image_recognition import BaiduImageRecognition
        
        service = BaiduImageRecognition()
        assert service.is_available() == False


class TestTavilyWebSearch:
    """Tavily 联网搜索服务测试"""
    
    def test_service_initialization_without_api_key(self):
        """测试无 API Key 时的初始化行为"""
        from src.services.tool_services.tavily_search import (
            TavilyWebSearch,
            TAVILY_AVAILABLE
        )
        
        service = TavilyWebSearch()
        
        if not TAVILY_AVAILABLE:
            result = service.initialize()
            assert result == False
        elif not service.config.tavily_api_key:
            result = service.initialize()
            assert result == False
    
    def test_search_returns_empty_when_unavailable(self):
        """测试服务不可用时返回空结果"""
        from src.services.tool_services.tavily_search import TavilyWebSearch
        
        service = TavilyWebSearch()
        
        results = service.search("宠物健康", max_results=5)
        
        assert results == []


class TestFileStorageFactory:
    """文件存储工厂测试"""
    
    def test_factory_returns_local_storage_by_default(self):
        """测试默认返回本地存储"""
        from src.services.tool_services.factory import FileStorageFactory
        
        FileStorageFactory.reset()
        
        with patch.dict(os.environ, {"STORAGE_PROVIDER": "local"}):
            storage = FileStorageFactory.get_storage()
            
            from src.services.tool_services.local_storage import LocalFileStorage
            assert isinstance(storage, LocalFileStorage)
    
    def test_factory_singleton_pattern(self):
        """测试单例模式"""
        from src.services.tool_services.factory import FileStorageFactory
        
        FileStorageFactory.reset()
        
        storage1 = FileStorageFactory.get_storage()
        storage2 = FileStorageFactory.get_storage()
        
        assert storage1 is storage2
    
    def test_factory_reset(self):
        """测试重置功能"""
        from src.services.tool_services.factory import FileStorageFactory
        
        FileStorageFactory.reset()
        storage1 = FileStorageFactory.get_storage()
        
        FileStorageFactory.reset()
        storage2 = FileStorageFactory.get_storage()
        
        assert storage1 is not storage2


class TestAsyncTaskService:
    """异步任务服务测试"""
    
    def test_service_creation(self):
        """测试服务创建"""
        from src.services.tool_services.async_task_service import (
            CeleryAsyncTaskService
        )
        
        service = CeleryAsyncTaskService()
        
        assert service._initialized == False
    
    def test_service_available_after_init_mock(self):
        """测试模拟初始化后的可用性"""
        from src.services.tool_services.async_task_service import (
            CeleryAsyncTaskService
        )
        
        service = CeleryAsyncTaskService()
        
        with patch.object(service, 'initialize', return_value=True):
            service.initialize()
            service._initialized = True
            assert service.is_available()


class TestAPIRoutesRegistration:
    """API 路由注册测试"""
    
    def test_files_router_registered(self):
        """测试文件路由已注册"""
        try:
            from src.api.v1.router import api_router
            
            routes = [route.path for route in api_router.routes]
            
            has_files_routes = any(
                "files" in route.lower() for route in routes
            ) or any(
                "/upload" in route.lower() for route in routes
            )
            
            assert has_files_routes, "文件路由未正确注册"
        except Exception as e:
            pytest.fail(f"路由注册检查失败: {e}")
    
    def test_all_tool_endpoints_exist(self):
        """测试所有工具端点都存在"""
        try:
            from src.api.v1.endpoints.files import router as files_router
            
            endpoints = []
            for route in files_router.routes:
                if hasattr(route, 'methods'):
                    for method in route.methods - {'HEAD', 'OPTIONS'}:
                        endpoints.append(f"{method} {route.path}")
            
            expected_endpoints = [
                'POST /upload',
                'POST /upload/image',
                'DELETE /delete',
                'GET /config'
            ]
            
            for endpoint in expected_endpoints:
                method_path = endpoint.split(' ')
                found = any(
                    method_path[0] in ep and method_path[1] in ep 
                    for ep in endpoints
                )
                assert found, f"缺少端点: {endpoint}"
                
        except Exception as e:
            pytest.fail(f"端点检查失败: {e}")


class TestSchemaValidation:
    """数据模型 Schema 测试"""
    
    def test_file_upload_response_schema(self):
        """测试文件上传响应模型"""
        from src.api.schemas.files import FileUploadResponse
        
        response = FileUploadResponse(
            success=True,
            file_url="/uploads/files/test.txt",
            file_name="test.txt",
            file_size=1024,
            file_type="text/plain",
            message="上传成功"
        )
        
        assert response.success == True
        assert response.file_name == "test.txt"
    
    def test_image_upload_response_schema(self):
        """测试图片上传响应模型"""
        from src.api.schemas.files import ImageUploadResponse
        
        response = ImageUploadResponse(
            success=True,
            image_url="/uploads/images/photo.jpg",
            file_name="photo.jpg",
            width=800,
            height=600
        )
        
        assert response.success == True
        assert response.width == 800
    
    def test_config_response_schema(self):
        """测试配置响应模型"""
        from src.api.schemas.files import FileUploadConfigResponse
        
        response = FileUploadConfigResponse(
            max_upload_size=10485760,
            allowed_image_extensions=[".jpg", ".png"],
            allowed_file_extensions=[".pdf"],
            storage_provider="local"
        )
        
        assert response.max_upload_size == 10485760
        assert response.storage_provider == "local"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
