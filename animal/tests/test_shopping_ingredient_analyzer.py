"""
成分分析器单元测试
"""
import pytest
from src.core.ingredient_analyzer import IngredientAnalyzer


class TestIngredientAnalyzer:
    """成分分析器测试"""
    
    @pytest.fixture
    def analyzer(self):
        return IngredientAnalyzer()
    
    def test_safe_dog_food(self, analyzer):
        """测试安全的狗粮成分"""
        result = analyzer.analyze(
            ingredients_text="鸡肉, 糙米, 鱼油, 胡萝卜, 蓝莓, 维生素E",
            pet_type="dog"
        )
        
        assert result["overall_safety"] == "safe"
        assert result["safety_score"] >= 80
        assert len(result["unsafe_ingredients"]) == 0
    
    def test_unsafe_ingredients_dog(self, analyzer):
        """测试含不安全成分的狗粮"""
        result = analyzer.analyze(
            ingredients_text="巧克力, 洋葱, 鸡肉, 玉米",
            pet_type="dog"
        )
        
        assert result["overall_safety"] == "unsafe"
        assert result["safety_score"] < 50
        assert len(result["unsafe_ingredients"]) > 0
    
    def test_allergen_detection_dog(self, analyzer):
        """测试犬类过敏原检测"""
        result = analyzer.analyze(
            ingredients_text="小麦, 牛肉, 乳糖, 鸡肉脂肪",
            pet_type="dog"
        )
        
        assert len(result["allergen_warnings"]) > 0
        allergen_categories = [w["category"] for w in result["allergen_warnings"]]
        assert "谷物" in allergen_categories or "乳制品" in allergen_categories
    
    def test_cat_specific_allergens(self, analyzer):
        """测试猫类特定过敏原"""
        result = analyzer.analyze(
            ingredients_text="金枪鱼, 牛奶, 小麦粉, 鸡肉",
            pet_type="cat"
        )
        
        warnings = result["allergen_warnings"]
        fish_allergens = [w for w in warnings if w["category"] == "鱼类"]
        assert len(fish_allergens) > 0
    
    def test_puppy_nutrition_advice(self, analyzer):
        """测试幼年宠物营养建议"""
        result = analyzer.analyze(
            ingredients_text="高蛋白鸡肉, DHA, Omega-3, 钙磷比1.2:1",
            pet_type="dog",
            age_group="puppy"
        )
        
        recommendations = result["recommendations"]
        has_puppy_advice = any("幼年" in r or "puppy" in r.lower() for r in recommendations)
        assert has_puppy_advice or len(recommendations) > 0
    
    def test_senior_pet_advice(self, analyzer):
        """测试老年宠物建议"""
        result = analyzer.analyze(
            ingredients_text="低脂易消化配方, 关节保健葡萄糖胺",
            pet_type="dog",
            age_group="senior"
        )
        
        recommendations = result["recommendations"]
        has_senior_advice = any("老年" in r for r in recommendations)
        assert has_senior_advice or len(recommendations) > 0
    
    def test_health_condition_obesity(self, analyzer):
        """测试肥胖/糖尿病健康问题建议"""
        result = analyzer.analyze(
            ingredients_text="低碳水高蛋白配方, 无谷肉类",
            pet_type="dog",
            health_conditions=["肥胖", "超重"]
        )
        
        recommendations = result["recommendations"]
        has_diet_advice = any("碳水" in r or "肥胖" in r for r in recommendations)
        assert has_diet_advice or len(recommendations) > 0
    
    def test_empty_ingredients(self, analyzer):
        """测试空成分文本"""
        result = analyzer.analyze(
            ingredients_text="",
            pet_type="dog"
        )
        
        assert "error" in result
        assert result["overall_safety"] == "unknown"
    
    def test_cautionary_ingredients(self, analyzer):
        """测试需注意成分"""
        result = analyzer.analyze(
            ingredients_text="肉粉副产品, BHA防腐剂, 鸡肉",
            pet_type="dog"
        )
        
        assert result["overall_safety"] in ["cautionary", "unsafe"]
        assert len(result["caution_ingredients"]) > 0
