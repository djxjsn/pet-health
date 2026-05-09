"""
成分分析器

提供宠物食品/用品成分分析功能，检测过敏原和安全性。
"""
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class IngredientAnalyzer:
    """成分分析器"""
    
    # 犬类过敏原数据库
    DOG_ALLERGENS = {
        "谷物": ["小麦", "玉米", "大豆", "麸质", "gluten", "wheat", "corn", "soy"],
        "肉类": ["牛肉", "鸡肉", "羊肉", "lamb", "beef", "chicken"],
        "乳制品": ["牛奶", "奶酪", "乳糖", "dairy", "milk", "cheese", "lactose"],
        "其他": ["鸡蛋", "egg", "人工色素", "防腐剂", "BHA", "BHT"]
    }
    
    # 猫类过敏原数据库
    CAT_ALLERGENS = {
        "鱼类": ["金枪鱼", "三文鱼", "鳕鱼", "tuna", "salmon", "cod"],
        "肉类": ["鸡肉", "牛肉", "poultry", "chicken", "beef"],
        "谷物": ["小麦", "玉米", "大米", "wheat", "corn", "rice"],
        "其他": ["鸡蛋", "egg", "乳制品", "dairy", "人工添加剂"]
    }
    
    # 安全成分白名单
    SAFE_INGREDIENTS = [
        # 蛋白质来源
        "鸡肉", "牛肉", "鱼肉", "鸭肉", "火鸡肉",
        # 碳水化合物
        "糙米", "燕麦", "甘薯", "红薯", "南瓜",
        # 健康脂肪
        "鱼油", "亚麻籽油", "椰子油", "鸡油",
        # 维生素和矿物质
        "维生素A", "维生素B", "维生素C", "维生素D", "维生素E",
        "牛磺酸", "Omega-3", "Omega-6", "DHA", "EPA",
        # 天然成分
        "蓝莓", "蔓越莓", "胡萝卜", "菠菜", "西兰花"
    ]
    
    # 需注意成分
    CAUTION_INGREDIENTS = {
        "by-product": "肉粉副产品，营养价值较低",
        "meat meal": "肉粉，可能来源不明确",
        "animal fat": "动物脂肪，可能来源不明确",
        "BHA/BHT": "防腐剂，长期摄入可能有健康风险",
        "artificial colors": "人工色素，可能导致过敏反应",
        "sugar": "添加糖分，对宠物健康不利",
        "salt/sodium": "过量钠，可能影响肾脏"
    }
    
    # 不安全成分
    UNSAFE_INGREDIENTS = {
        "dog": [
            ("巧克力", "可可碱，致命毒性"),
            ("葡萄干", "肾衰竭"),
            ("洋葱/大蒜", "溶血性贫血"),
            ("木糖醇", "低血糖、肝衰竭"),
            ("酒精", "中枢神经抑制"),
            ("咖啡因", "咖啡因中毒"),
            ("澳洲坚果", "肌肉无力")
        ],
        "cat": [
            ("洋葱/大蒜", "溶血性贫血"),
            ("巧克力", "可可碱中毒"),
            ("酒精", "中枢神经抑制"),
            ("咖啡因", "咖啡因中毒"),
            ("百合花", "急性肾衰竭"),
            ("葡萄/葡萄干", "可能有害"),
            ("牛奶", "乳糖不耐受")
        ]
    }
    
    def analyze(
        self,
        ingredients_text: str,
        pet_type: str,
        breed: Optional[str] = None,
        age_group: Optional[str] = None,
        health_conditions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """分析成分安全性
        
        Args:
            ingredients_text: 成分文本
            pet_type: 宠物类型（dog/cat）
            breed: 品种
            age_group: 年龄阶段（puppy/adult/senior）
            health_conditions: 健康问题列表
        
        Returns:
            分析结果字典
        """
        if not ingredients_text.strip():
            return {
                "error": "成分文本为空",
                "overall_safety": "unknown",
                "safety_score": 0
            }
        
        # 解析成分列表
        parsed_ingredients = self._parse_ingredients(ingredients_text)
        
        # 分类分析
        safe, caution, unsafe = self._categorize_ingredients(
            parsed_ingredients,
            pet_type
        )
        
        # 过敏原检测
        allergen_warnings = self._detect_allergens(
            parsed_ingredients,
            pet_type
        )
        
        # 计算安全分数
        safety_score = self._calculate_safety_score(safe, caution, unsafe)
        
        # 生成建议
        recommendations = self._generate_recommendations(
            safe=safe,
            caution=caution,
            unsafe=unsafe,
            allergens=allergen_warnings,
            pet_type=pet_type,
            age_group=age_group,
            health_conditions=health_conditions or []
        )
        
        # 整体安全性判断
        overall_safety = self._determine_overall_safety(safety_score)
        
        return {
            "overall_safety": overall_safety,
            "safety_score": safety_score,
            "safe_ingredients": safe,
            "caution_ingredients": caution,
            "unsafe_ingredients": unsafe,
            "allergen_warnings": allergen_warnings,
            "recommendations": recommendations,
            "total_analyzed": len(parsed_ingredients),
            "parsed_ingredients": parsed_ingredients[:10]
        }
    
    def _parse_ingredients(self, text: str) -> List[str]:
        """解析成分文本"""
        # 按逗号、分号、换行分割
        separators = r'[,;，；\n]+'
        ingredients = [ing.strip() for ing in re.split(separators, text)]
        return [ing for ing in ingredients if ing]
    
    def _categorize_ingredients(
        self,
        ingredients: List[str],
        pet_type: str
    ) -> tuple:
        """将成分分类为安全/需注意/不安全"""
        safe = []
        caution = []
        unsafe = []
        
        for ingredient in ingredients:
            ingredient_lower = ingredient.lower()
            
            # 检查是否为不安全成分
            is_unsafe = False
            for unsafe_item, reason in self.UNSAFE_INGREDIENTS.get(pet_type, []):
                if unsafe_item.lower() in ingredient_lower:
                    unsafe.append({
                        "name": ingredient,
                        "reason": reason,
                        "severity": "high"
                    })
                    is_unsafe = True
                    break
            
            if is_unsafe:
                continue
            
            # 检查是否为需注意成分
            is_caution = False
            for caution_item, reason in self.CAUTION_INGREDIENTS.items():
                if caution_item.lower() in ingredient_lower:
                    caution.append({
                        "name": ingredient,
                        "reason": reason,
                        "severity": "medium"
                    })
                    is_caution = True
                    break
            
            if is_caution:
                continue
            
            # 检查是否在安全名单中
            is_safe = any(
                safe_item.lower() in ingredient_lower 
                for safe_item in self.SAFE_INGREDIENTS
            )
            
            if is_safe:
                safe.append({
                    "name": ingredient,
                    "benefit": self._get_ingredient_benefit(ingredient)
                })
            else:
                # 未识别的成分归入需注意
                caution.append({
                    "name": ingredient,
                    "reason": "未在已知安全成分库中找到，建议咨询兽医",
                    "severity": "low"
                })
        
        return safe, caution, unsafe
    
    def _detect_allergens(
        self,
        ingredients: List[str],
        pet_type: str
    ) -> List[Dict[str, Any]]:
        """检测潜在过敏原"""
        allergens_db = self.DOG_ALLERGENS if pet_type == "dog" else self.CAT_ALLERGENS
        warnings = []
        
        for category, allergen_list in allergens_db.items():
            for allergen in allergen_list:
                for ingredient in ingredients:
                    if allergen.lower() in ingredient.lower():
                        warnings.append({
                            "category": category,
                            "allergen": allergen,
                            "found_in": ingredient,
                            "risk_level": "high" if category in ["谷物", "肉类"] else "medium"
                        })
        
        return warnings
    
    def _calculate_safety_score(
        self,
        safe: List,
        caution: List,
        unsafe: List
    ) -> float:
        """计算安全分数（0-100）"""
        total = len(safe) + len(caution) + len(unsafe)
        if total == 0:
            return 50.0
        
        base_score = (len(safe) / total) * 100
        penalty = len(unsafe) * 20 + len(caution) * 5
        
        score = max(0, min(100, base_score - penalty))
        return round(score, 1)
    
    def _determine_overall_safety(self, score: float) -> str:
        """确定整体安全性等级"""
        if score >= 80:
            return "safe"
        elif score >= 50:
            return "cautionary"
        else:
            return "unsafe"
    
    def _get_ingredient_benefit(self, ingredient: str) -> str:
        """获取成分益处描述"""
        benefits = {
            "鱼油": "富含Omega-3，有益皮肤和毛发健康",
            "Omega-3": "抗炎作用，支持关节和大脑健康",
            "DHA/EPA": "支持视力和认知发育",
            "牛磺酸": "猫必需氨基酸，支持心脏和眼睛健康",
            "蓝莓": "抗氧化剂，增强免疫力",
            "胡萝卜": "提供β-胡萝卜素，有益视力",
            "甘薯": "优质碳水化合物来源，易消化",
            "鸡油": "天然脂肪来源，增加适口性"
        }
        
        for key, benefit in benefits.items():
            if key.lower() in ingredient.lower():
                return benefit
        
        return "营养补充成分"
    
    def _generate_recommendations(
        self,
        safe: List,
        caution: List,
        unsafe: List,
        allergens: List,
        pet_type: str,
        age_group: Optional[str],
        health_conditions: List[str]
    ) -> List[str]:
        """生成使用建议"""
        recommendations = []
        
        if unsafe:
            recommendations.append(f"⚠️ 发现{len(unsafe)}个不安全成分，强烈不建议使用此产品")
        
        if allergens:
            allergen_names = list(set([a["allergen"] for a in allergens]))
            recommendations.append(f"⚠️ 含有潜在过敏原：{', '.join(allergen_names[:5])}，如宠物有过敏史请避免")
        
        if caution and not unsafe:
            recommendations.append(f"ℹ️ 含有{len(caution)}个需注意成分，建议少量试用观察反应")
        
        if safe:
            recommendations.append(f"✅ 含有{len(safe)}个优质成分，整体配方较为健康")
        
        # 根据年龄阶段提供建议
        if age_group == "puppy" or age_group == "kitten":
            recommendations.append("💡 幼年宠物需要高蛋白、高热量配方，确保营养成分充足")
        elif age_group == "senior":
            recommendations.append("💡 老年宠物需要易消化、低脂肪配方，关注关节保健成分")
        
        # 根据健康状况提供建议
        if any(c in ["肥胖", "超重", "糖尿病"] for c in health_conditions):
            recommendations.append("💡 注意控制碳水化合物含量，选择低碳水配方")
        
        if any(c in ["皮肤病", "过敏", "掉毛"] for c in health_conditions):
            recommendations.append("💡 选择无谷、单一蛋白源配方，避免常见过敏原")
        
        if not recommendations:
            recommendations.append("建议咨询专业兽医或宠物营养师获取更详细的评估")
        
        return recommendations


def get_ingredient_analyzer() -> IngredientAnalyzer:
    """获取成分分析器实例"""
    return IngredientAnalyzer()
