"""
Tavily 联网搜索服务

集成 Tavily AI 搜索 API，提供实时信息检索能力。
"""
from typing import List, Dict, Any, Optional
import logging

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    TavilyClient = None

from src.services.tool_services.base import WebSearchService
from src.config.third_party_config import get_third_party_config

logger = logging.getLogger(__name__)


class TavilyWebSearch(WebSearchService):
    """Tavily 联网搜索服务"""
    
    def __init__(self):
        """初始化 Tavily 客户端"""
        self.config = get_third_party_config()
        self.client = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化 Tavily 客户端"""
        if not TAVILY_AVAILABLE:
            logger.error("Tavily SDK 未安装，请安装：pip install tavily-python")
            return False
        
        if not self.config.tavily_api_key:
            logger.warning("Tavily API Key 未配置")
            return False
        
        try:
            self.client = TavilyClient(api_key=self.config.tavily_api_key)
            self._initialized = True
            logger.info("Tavily 联网搜索初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"Tavily 初始化失败：{e}")
            return False
    
    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self._initialized and self.client is not None
    
    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """搜索网络信息
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
        
        Returns:
            搜索结果列表
        """
        if not self.is_available():
            logger.warning("Tavily 服务不可用，返回空结果")
            return []
        
        try:
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date", "")
                })
            
            logger.info(f"Tavily 搜索成功：{query}，返回{len(results)}条结果")
            return results
            
        except Exception as e:
            logger.error(f"Tavily 搜索失败：{e}")
            return []
    
    def search_with_content(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """搜索并返回完整内容
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
        
        Returns:
            搜索结果列表（包含完整内容）
        """
        if not self.is_available():
            return []
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=True
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "raw_content": result.get("raw_content", ""),
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date", ""),
                    "answer": response.get("answer", "")
                })
            
            logger.info(f"Tavily 深度搜索成功：{query}")
            return results
            
        except Exception as e:
            logger.error(f"Tavily 深度搜索失败：{e}")
            return []
    
    def get_news(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """搜索新闻
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
        
        Returns:
            新闻结果列表
        """
        if not self.is_available():
            return []
        
        try:
            # Tavily 支持时间范围搜索
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                time_range="week"  # 最近一周
            )
            
            results = []
            for result in response.get("results", []):
                if result.get("published_date"):
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "source": result.get("source", ""),
                        "published_date": result.get("published_date", ""),
                        "score": result.get("score", 0.0)
                    })
            
            logger.info(f"Tavily 新闻搜索成功：{query}")
            return results
            
        except Exception as e:
            logger.error(f"Tavily 新闻搜索失败：{e}")
            return []
    
    def search_pet_health_info(self, symptom: str, pet_type: str = "dog") -> List[Dict[str, Any]]:
        """搜索宠物健康相关信息（便捷方法）
        
        Args:
            symptom: 症状描述
            pet_type: 宠物类型
        
        Returns:
            搜索结果列表
        """
        query = f"{pet_type} {symptom} 症状 治疗 预防"
        return self.search_with_content(query, max_results=5)
    
    def search_pet_nutrition(self, topic: str) -> List[Dict[str, Any]]:
        """搜索宠物营养相关信息
        
        Args:
            topic: 营养主题（如"高蛋白饮食"、"维生素补充"）
        
        Returns:
            搜索结果列表
        """
        query = f"宠物营养 {topic} 饮食建议"
        return self.search_with_content(query, max_results=5)


def get_tavily_web_search() -> TavilyWebSearch:
    """获取 Tavily 联网搜索服务实例"""
    return TavilyWebSearch()
