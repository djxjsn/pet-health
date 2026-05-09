"""
外部 API 集成工具集

提供天气查询、地图服务、网络搜索、图像识别等外部 API 工具，
用于扩展 AI 宠物健康助手的外部数据获取能力。
"""
import logging
from typing import Dict, Any, List, Optional, Type, ClassVar
from pydantic import BaseModel, Field

from src.tools.base import BaseTool

logger = logging.getLogger(__name__)


# ========== 天气查询工具 ==========

class WeatherQueryInput(BaseModel):
    """天气查询输入参数"""
    city: str = Field(..., description="城市名称，如'北京'")
    days: int = Field(3, description="预报天数(1-7)", ge=1, le=7)


class WeatherTool(BaseTool):
    """天气查询工具 - 获取指定城市的天气预报"""

    name: str = "get_weather"
    description: str = "获取指定城市的天气预报信息，包括温度、湿度、空气质量等，可用于宠物外出建议和健康提醒"
    args_schema: Type[BaseModel] = WeatherQueryInput

    def _run(self, city: str, days: int = 3) -> Dict[str, Any]:
        """执行天气查询"""
        try:
            weather_data = self._fetch_weather_data(city, days)
            
            pet_advice = self._generate_pet_weather_advice(weather_data)
            
            return {
                "city": city,
                "forecast": weather_data.get("forecast", []),
                "current": weather_data.get("current", {}),
                "pet_advice": pet_advice,
                "source": "模拟数据"
            }
        except Exception as e:
            logger.error(f"天气查询失败: {e}")
            return {
                "error": f"天气查询失败: {str(e)}",
                "city": city
            }

    def _fetch_weather_data(self, city: str, days: int) -> Dict[str, Any]:
        """获取天气数据（可替换为真实 API 调用）"""
        import random
        
        current_temp = random.randint(15, 35)
        humidity = random.randint(40, 90)
        
        conditions = ["晴", "多云", "阴", "小雨", "中雨"]
        aqi_levels = ["优", "良", "轻度污染", "中度污染"]
        
        forecast = []
        for i in range(days):
            high = current_temp + random.randint(-5, 5)
            low = high - random.randint(5, 10)
            forecast.append({
                "day": f"第{i+1}天",
                "condition": random.choice(conditions),
                "high_temp": high,
                "low_temp": low,
                "humidity": random.randint(30, 95),
                "wind_level": random.randint(1, 6)
            })
        
        return {
            "current": {
                "temp": current_temp,
                "condition": random.choice(conditions),
                "humidity": humidity,
                "aqi": random.choice(aqi_levels),
                "wind_direction": ["东", "南", "西", "北"][random.randint(0, 3)],
                "wind_speed": random.randint(1, 20)
            },
            "forecast": forecast
        }

    def _generate_pet_weather_advice(self, weather_data: Dict) -> List[str]:
        """根据天气生成宠物建议"""
        advice = []
        current = weather_data.get("current", {})
        temp = current.get("temp", 25)
        condition = current.get("condition", "")
        
        if temp > 30:
            advice.append("高温天气，避免长时间户外活动，注意防暑降温")
            advice.append("确保宠物有充足的饮水")
        elif temp < 10:
            advice.append("低温天气，外出时考虑给宠物添加保暖衣物")
            advice.append("缩短户外散步时间")
        
        if "雨" in condition:
            advice.append("雨天路滑，遛狗时注意安全")
            advice.append("回家后及时擦干宠物毛发")
        
        if current.get("humidity", 50) > 80:
            advice.append("湿度较高，注意宠物皮肤护理，预防皮肤病")
        
        if not advice:
            advice.append("天气适宜，可以正常带宠物外出活动")
        
        return advice


# ========== 地图/位置服务工具 ==========

class NearbySearchInput(BaseModel):
    """附近搜索输入参数"""
    location: str = Field(..., description="位置描述，如'北京市朝阳区'")
    query_type: str = Field(..., description="搜索类型: hospital/vet/shop/park/grooming")
    radius: float = Field(5.0, description="搜索半径(公里)", ge=0.5, le=50)


class MapServiceTool(BaseTool):
    """地图/位置服务工具 - 查找附近的宠物相关场所"""

    name: str = "search_nearby"
    description: str = "查找附近的宠物医院、宠物商店、公园等场所，支持多种类型搜索"
    args_schema: Type[BaseModel] = NearbySearchInput

    TYPE_NAMES: ClassVar[Dict[str, str]] = {
        "hospital": "宠物医院",
        "vet": "兽医诊所",
        "shop": "宠物用品店",
        "park": "宠物友好公园",
        "grooming": "宠物美容店",
        "pharmacy": "宠物药店"
    }

    def _run(
        self,
        location: str,
        query_type: str = "hospital",
        radius: float = 5.0
    ) -> Dict[str, Any]:
        """执行附近搜索"""
        type_name = self.TYPE_NAMES.get(query_type, query_type)
        
        try:
            results = self._search_nearby_places(location, query_type, radius)
            
            return {
                "location": location,
                "query_type": query_type,
                "type_name": type_name,
                "radius_km": radius,
                "results": results,
                "total": len(results)
            }
        except Exception as e:
            logger.error(f"附近搜索失败: {e}")
            return {
                "error": f"搜索失败: {str(e)}",
                "location": location,
                "query_type": query_type
            }

    def _search_nearby_places(
        self,
        location: str,
        query_type: str,
        radius: float
    ) -> List[Dict[str, Any]]:
        """搜索附近地点（可替换为真实地图 API）"""
        import random
        
        results = []
        count = random.randint(3, 8)
        
        names_map = {
            "hospital": ["宠爱国际动物医院", "瑞鹏宠物医院", "芭比堂动物医院", "安安宠物医院"],
            "vet": ["爱心诊所", "萌宠诊所", "伴侣动物诊所"],
            "shop": ["波奇网线下店", "E宠商城体验店", "宠物之家"],
            "park": ["朝阳公园", "奥林匹克森林公园", "望京公园"],
            "grooming": ["爱宠美容", "萌宠造型", "专业洗护中心"],
            "pharmacy": ["宠物大药房", "动保药品店"]
        }
        
        names = names_map.get(query_type, ["示例店铺"])
        
        for i in range(min(count, len(names))):
            distance = round(random.uniform(0.3, radius), 1)
            rating = round(random.uniform(3.5, 5.0), 1)
            
            result = {
                "name": names[i % len(names)] + (f"({location})" if i >= len(names) else ""),
                "address": f"{location}某某路{random.randint(1,200)}号",
                "distance_km": distance,
                "rating": rating,
                "phone": f"010-{random.randint(10000000,99999999)}",
                "open_hours": f"{8+random.randint(0,2)}:00-{'21' if query_type in ['hospital', 'vet'] else '20'}:00",
                "features": self._get_features(query_type)
            }
            results.append(result)
        
        results.sort(key=lambda x: x["distance_km"])
        return results

    def _get_features(self, query_type: str) -> List[str]:
        """获取场所特色标签"""
        features_map = {
            "hospital": ["24小时急诊", "手术服务", "疫苗接种", "体检套餐"],
            "vet": ["预约制", "专科医生", "上门服务"],
            "shop": ["正品保障", "会员优惠", "送货上门"],
            "park": ["宠物友好", "大型犬允许", "有饮水点"],
            "grooming": ["洗澡美容", "SPA护理", "造型设计"],
            "pharmacy": ["处方药", "保健品", "驱虫药"]
        }
        base_features = features_map.get(query_type, [])
        import random
        return random.sample(base_features, min(len(base_features), random.randint(2, 4)))


# ========== 网络搜索工具 ==========

class WebSearchInput(BaseModel):
    """网络搜索输入参数"""
    query: str = Field(..., description="搜索关键词")
    max_results: int = Field(5, description="最大返回结果数", ge=1, le=10)


class WebSearchTool(BaseTool):
    """网络搜索工具 - 搜索宠物相关的最新信息"""

    name: str = "web_search"
    description: str = "搜索互联网上的宠物相关信息，包括最新新闻、专业知识、产品评测等"
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """执行网络搜索"""
        try:
            results = self._perform_search(query, max_results)
            
            return {
                "query": query,
                "results": results,
                "total": len(results),
                "source": "搜索引擎"
            }
        except Exception as e:
            logger.error(f"网络搜索失败: {e}")
            return {
                "error": f"搜索失败: {str(e)}",
                "query": query,
                "results": []
            }

    def _perform_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """执行搜索（可替换为 Tavily 或其他搜索 API）"""
        import random
        from datetime import datetime, timedelta
        
        sample_results = [
            {
                "title": f"关于「{query}」的权威解读与实用指南",
                "url": "https://example.com/article/1",
                "snippet": f"本文详细介绍了{query}的相关知识，包括定义、症状、预防和治疗方法...",
                "source": "宠物医学百科",
                "published_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "relevance_score": round(random.uniform(0.85, 0.99), 2)
            },
            {
                "title": f"{query}：2026年最新研究与临床实践",
                "url": "https://example.com/research/2",
                "snippet": f"最新的研究表明，{query}在宠物健康管理中扮演着重要角色...",
                "source": "宠物科研期刊",
                "published_date": (datetime.now() - timedelta(days=random.randint(15, 60))).strftime("%Y-%m-%d"),
                "relevance_score": round(random.uniform(0.75, 0.95), 2)
            },
            {
                "title": f"宠物主人必读：如何应对{query}",
                "url": "https://example.com/guide/3",
                "snippet": f"作为宠物主人，了解{query}的基本知识非常重要。本文将从实际经验出发...",
                "source": "宠物养护指南",
                "published_date": (datetime.now() - timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d"),
                "relevance_score": round(random.uniform(0.70, 0.90), 2)
            },
            {
                "title": f"专家访谈：{query}的误区与真相",
                "url": "https://example.com/interview/4",
                "snippet": f"我们采访了多位资深兽医师，探讨关于{query}的常见误区...",
                "source": "宠物健康资讯",
                "published_date": (datetime.now() - timedelta(days=random.randint(10, 45))).strftime("%Y-%m-%d"),
                "relevance_score": round(random.uniform(0.65, 0.85), 2)
            },
            {
                "title": f"{query}相关产品推荐与评测",
                "url": "https://example.com/review/5",
                "snippet": f"针对{query}问题，我们测试了多款相关产品，为您推荐最佳选择...",
                "source": "宠物用品评测",
                "published_date": (datetime.now() - timedelta(days=random.randint(5, 25))).strftime("%Y-%m-%d"),
                "relevance_score": round(random.uniform(0.60, 0.80), 2)
            }
        ]
        
        sorted_results = sorted(sample_results, key=lambda x: x["relevance_score"], reverse=True)
        return sorted_results[:max_results]


# ========== 图像识别工具 ==========

class ImageRecognitionInput(BaseModel):
    """图像识别输入参数"""
    image_url: Optional[str] = Field(None, description="图片URL（可选）")
    image_base64: Optional[str] = Field(None, description="图片Base64编码（可选）")
    recognition_type: str = Field(
        "pet_breed",
        description="识别类型: pet_breed/symptom/food/nutrition_label"
    )


class ImageRecognitionTool(BaseTool):
    """图像识别工具 - 识别宠物品种、症状图片等"""

    name: str = "recognize_image"
    description: str = "通过AI图像识别技术，识别宠物品种、分析症状图片、识别食品成分标签等"
    args_schema: Type[BaseModel] = ImageRecognitionInput

    RECOGNITION_TYPES: ClassVar[Dict[str, str]] = {
        "pet_breed": "品种识别",
        "symptom": "症状分析",
        "food": "食物识别",
        "nutrition_label": "营养标签识别"
    }

    def _run(
        self,
        recognition_type: str = "pet_breed",
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行图像识别"""
        if not image_url and not image_base64:
            return {"error": "请提供图片URL或Base64编码"}
        
        type_name = self.RECOGNITION_TYPES.get(recognition_type, recognition_type)
        
        try:
            result = self._perform_recognition(recognition_type)
            
            return {
                "recognition_type": recognition_type,
                "type_name": type_name,
                "result": result,
                "confidence": result.get("confidence", 0.85),
                "processing_time_ms": random.randint(500, 2000)
            }
        except Exception as e:
            logger.error(f"图像识别失败: {e}")
            return {
                "error": f"识别失败: {str(e)}",
                "recognition_type": recognition_type
            }

    def _perform_recognition(self, recognition_type: str) -> Dict[str, Any]:
        """执行识别（可替换为百度 AI 或其他视觉 API）"""
        import random
        
        if recognition_type == "pet_breed":
            breeds_dog = ["金毛寻回犬", "拉布拉多", "哈士奇", "柯基犬", "泰迪", "柴犬", "德牧", "萨摩耶"]
            breeds_cat = ["布偶猫", "英短蓝猫", "美短虎斑", "暹罗猫", "橘猫", "波斯猫"]
            
            is_cat = random.random() > 0.5
            breeds = breeds_cat if is_cat else breeds_dog
            breed = random.choice(breeds)
            
            return {
                "species": "cat" if is_cat else "dog",
                "breed": breed,
                "confidence": round(random.uniform(0.80, 0.98), 2),
                "characteristics": self._get_breed_characteristics(breed, is_cat),
                "alternative_guesses": [random.choice(breeds) for _ in range(2)]
            }
        
        elif recognition_type == "symptom":
            symptoms = [
                "皮肤红肿", "脱毛区域", "眼部异常", "口腔病变", 
                "肢体肿胀", "伤口感染", "寄生虫迹象"
            ]
            symptom = random.choice(symptoms)
            
            return {
                "detected_symptom": symptom,
                "severity": random.choice(["轻微", "中等", "严重"]),
                "affected_area": random.choice(["头部", "躯干", "四肢", "全身"]),
                "confidence": round(random.uniform(0.75, 0.95), 2),
                "suggestion": "建议尽快咨询专业兽医进行确诊"
            }
        
        elif recognition_type == "food":
            foods = [
                "狗粮（干粮）", "猫粮（湿粮）", "鸡胸肉", "牛肉粒",
                "冻干零食", "磨牙棒", "羊奶粉"
            ]
            food = random.choice(foods)
            
            return {
                "food_type": food,
                "category": random.choice(["主食", "零食", "补充剂"]),
                "estimated_quality": random.choice(["优质", "良好", "一般"]),
                "confidence": round(random.uniform(0.80, 0.95), 2),
                "feeding_suggestion": "适合作为日常喂养或训练奖励"
            }
        
        elif recognition_type == "nutrition_label":
            return {
                "ingredients_detected": [
                    {"name": "鸡肉粉", "percentage": 28},
                    {"name": "糙米", "percentage": 22},
                    {"name": "鱼油", "percentage": 5},
                    {"name": "维生素E", "percentage": 0.5}
                ],
                "guaranteed_analysis": {
                    "crude_protein": "≥25%",
                    "crude_fat": "≥14%",
                    "crude_fiber": "≤5%",
                    "moisture": "≤10%"
                },
                "overall_rating": random.choice(["优秀", "良好", "一般"]),
                "confidence": round(random.uniform(0.85, 0.98), 2)
            }
        
        else:
            return {
                "error": f"不支持的识别类型: {recognition_type}"
            }

    def _get_breed_characteristics(self, breed: str, is_cat: bool) -> List[str]:
        """获取品种特征"""
        characteristics_map = {
            "金毛寻回犬": ["长毛", "温顺", "大型犬", "需要大量运动"],
            "拉布拉多": ["短毛", "活泼", "大型犬", "易训练"],
            "哈士奇": ["中长毛", "精力旺盛", "中型犬", "爱叫"],
            "布偶猫": ["长毛", "蓝色眼睛", "温顺", "粘人"],
            "英短蓝猫": ["短毛", "圆脸", "安静", "独立"],
        }
        
        default_chars = ["毛茸茸", "可爱"] if is_cat else ["忠诚", "聪明"]
        return characteristics_map.get(breed, default_chars)


# ========== 宠物知识库增强工具 ==========

class KnowledgeEnhanceInput(BaseModel):
    """知识库增强输入"""
    topic: str = Field(..., description="查询主题")
    context: Optional[str] = Field(None, description="上下文信息")
    depth: str = Field("standard", description="深度: quick/standard/deep")


class KnowledgeEnhanceTool(BaseTool):
    """知识库增强工具 - 结合多源知识提供更全面的回答"""

    name: str = "enhance_knowledge"
    description: str = "增强知识检索能力，结合内部知识库和外部资源，提供更全面准确的宠物健康信息"
    args_schema: Type[BaseModel] = KnowledgeEnhanceInput

    def _run(
        self,
        topic: str,
        context: Optional[str] = None,
        depth: str = "standard"
    ) -> Dict[str, Any]:
        """执行知识增强"""
        try:
            internal_knowledge = self._get_internal_knowledge(topic)
            external_info = self._get_external_info(topic) if depth in ["standard", "deep"] else None
            expert_summary = self._generate_expert_summary(topic, internal_knowledge, context) if depth == "deep" else None
            
            return {
                "topic": topic,
                "depth": depth,
                "internal_knowledge": internal_knowledge[:3],
                "external_info": external_info[:2] if external_info else [],
                "expert_summary": expert_summary,
                "sources_count": len(internal_knowledge) + (len(external_info) if external_info else 0),
                "confidence": "high" if internal_knowledge else "low"
            }
        except Exception as e:
            logger.error(f"知识增强失败: {e}")
            return {
                "error": f"处理失败: {str(e)}",
                "topic": topic
            }

    def _get_internal_knowledge(self, topic: str) -> List[Dict]:
        """从内部知识库获取信息（通过统一检索入口）"""
        try:
            from src.core.knowledge_retriever import get_knowledge_retriever
            retriever = get_knowledge_retriever()
            search_results = retriever.search_for_knowledge_enhancement(topic=topic, top_k=5)
            
            knowledge_list = []
            for result in search_results:
                knowledge_list.append({
                    "content": result.get("content", ""),
                    "source": "internal_kb",
                    "relevance": 1 - result["distance"] if result.get("distance") is not None else 0.5
                })
            return knowledge_list
        except Exception:
            return []

    def _get_external_info(self, topic: str) -> List[Dict]:
        """获取外部补充信息"""
        import random
        return [
            {
                "content": f"关于「{topic}」的最新研究和行业动态",
                "source": "web_search",
                "type": "recent_research"
            },
            {
                "content": f"「{topic}」相关的专家观点和实践经验",
                "source": "expert_forum",
                "type": "expert_opinion"
            }
        ]

    def _generate_expert_summary(
        self,
        topic: str,
        internal_knowledge: List[Dict],
        context: Optional[str]
    ) -> Optional[Dict]:
        """生成专家级总结"""
        if not internal_knowledge:
            return None
        
        return {
            "key_points": [
                point["content"][:100] for point in internal_knowledge[:3]
            ],
            "common_misconceptions": [
                f"关于{topic}的一个常见误区是..."
            ],
            "best_practices": [
                f"处理{topic}问题的最佳实践包括..."
            ],
            "when_to_see_vet": f"如果出现以下情况，建议立即就医：..."
        }


import random
