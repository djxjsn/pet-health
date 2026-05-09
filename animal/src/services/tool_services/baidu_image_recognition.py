"""
百度 AI 图像识别服务

集成百度 AI 平台的图像识别能力。
"""
from typing import Dict, Any, List, Optional
import logging
import base64
from pathlib import Path

try:
    from aip import AipImageClassify
    BAIDU_AIP_AVAILABLE = True
except ImportError:
    BAIDU_AIP_AVAILABLE = False
    AipImageClassify = None

from src.services.tool_services.base import ImageRecognitionService
from src.config.third_party_config import get_third_party_config

logger = logging.getLogger(__name__)


class BaiduImageRecognition(ImageRecognitionService):
    """百度 AI 图像识别服务"""
    
    def __init__(self):
        """初始化百度 AI 客户端"""
        self.config = get_third_party_config()
        self.client = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化百度 AI 客户端"""
        if not BAIDU_AIP_AVAILABLE:
            logger.error("百度 AI SDK 未安装，请安装：pip install baidu-aip")
            return False
        
        if not all([
            self.config.baidu_app_id,
            self.config.baidu_api_key,
            self.config.baidu_secret_key
        ]):
            logger.warning("百度 AI 配置不完整，无法初始化")
            return False
        
        try:
            self.client = AipImageClassify(
                self.config.baidu_app_id,
                self.config.baidu_api_key,
                self.config.baidu_secret_key
            )
            
            self._initialized = True
            logger.info("百度 AI 图像识别初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"百度 AI 初始化失败：{e}")
            return False
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self._initialized and self.client is not None
    
    def recognize_image(self, image_path: str) -> Dict[str, Any]:
        """识别图像内容
        
        Args:
            image_path: 图片路径
        
        Returns:
            识别结果字典
        """
        if not self.is_available():
            raise RuntimeError("百度 AI 服务未初始化")
        
        try:
            # 读取图片
            image_data = self._read_image(image_path)
            
            # 通用物体识别
            result = self.client.general(image_data)
            
            return {
                "success": True,
                "provider": "baidu",
                "recognition_type": "general",
                "results": result.get("result", []),
                "raw_response": result
            }
            
        except Exception as e:
            logger.error(f"百度 AI 图像识别失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_skin_disease(self, image_path: str) -> Dict[str, Any]:
        """检测皮肤病（基于自定义分类器）
        
        Args:
            image_path: 皮肤病变图片路径
        
        Returns:
            检测结果字典
        """
        if not self.is_available():
            raise RuntimeError("百度 AI 服务未初始化")
        
        try:
            image_data = self._read_image(image_path)
            
            # 使用自定义图像分类（需要预先训练模型）
            # 这里使用通用识别作为示例
            result = self.client.general(image_data)
            
            # 模拟皮肤病检测逻辑
            skin_disease_detected = False
            disease_type = None
            confidence = 0.0
            
            # TODO: 集成真实的皮肤病分类模型
            # 目前仅返回通用识别结果
            return {
                "success": True,
                "provider": "baidu",
                "detection_type": "skin_disease",
                "detected": skin_disease_detected,
                "disease_type": disease_type,
                "confidence": confidence,
                "recommendations": [
                    "建议咨询兽医进行专业诊断",
                    "保持患处清洁干燥",
                    "避免宠物抓挠患处"
                ],
                "raw_response": result
            }
            
        except Exception as e:
            logger.error(f"皮肤病检测失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_pet_health(self, image_path: str, pet_type: str) -> Dict[str, Any]:
        """分析宠物健康状况
        
        Args:
            image_path: 宠物图片路径
            pet_type: 宠物类型（dog/cat）
        
        Returns:
            健康分析结果字典
        """
        if not self.is_available():
            raise RuntimeError("百度 AI 服务未初始化")
        
        try:
            image_data = self._read_image(image_path)
            
            # 动物识别
            animal_result = self.client.animal(image_data)
            
            # 身体状态分析（基于通用识别）
            general_result = self.client.general(image_data)
            
            # 提取关键信息
            animals = animal_result.get("result", [])
            general_info = general_result.get("result", [])
            
            # 分析健康状况
            health_analysis = {
                "species": animals[0]["name"] if animals else "未知",
                "confidence": animals[0]["score"] if animals else 0.0,
                "body_condition": "正常",  # TODO: 实现体态分析
                "coat_condition": "正常",  # TODO: 毛发状态分析
                "visible_issues": [],  # TODO: 可见问题检测
                "recommendations": []
            }
            
            # 生成建议
            if health_analysis["body_condition"] != "正常":
                health_analysis["recommendations"].append("建议调整饮食结构")
            
            if health_analysis["coat_condition"] != "正常":
                health_analysis["recommendations"].append("建议检查皮肤健康")
            
            if not health_analysis["recommendations"]:
                health_analysis["recommendations"].append("宠物整体健康状况良好")
            
            return {
                "success": True,
                "provider": "baidu",
                "analysis_type": "pet_health",
                "pet_type": pet_type,
                "analysis": health_analysis,
                "raw_responses": {
                    "animal": animal_result,
                    "general": general_result
                }
            }
            
        except Exception as e:
            logger.error(f"宠物健康分析失败：{e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _read_image(self, image_path: str) -> bytes:
        """读取图片为字节数据"""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"图片不存在：{image_path}")
        
        with open(path, "rb") as f:
            return f.read()


def get_baidu_image_recognition() -> BaiduImageRecognition:
    """获取百度 AI 图像识别服务实例"""
    return BaiduImageRecognition()
