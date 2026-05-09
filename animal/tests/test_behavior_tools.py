"""
行为分析工具单元测试
"""
import pytest
from sqlalchemy.orm import Session

from src.tools.behavior_tools import (
    BehaviorAnalysisTool,
    TrainingRecommendationTool,
    detect_behavior_category,
    get_breed_info,
    calculate_pet_age_months,
)
from src.db.crud import create_user, create_pet
from src.schemas.user import UserCreate
from src.schemas.pet import PetCreate


class TestDetectBehaviorCategory:
    """行为类别自动检测测试"""

    def test_destructive(self):
        assert detect_behavior_category("最近总拆家") == "destructive"
        assert detect_behavior_category("咬坏沙发") == "destructive"

    def test_howling(self):
        assert detect_behavior_category("不停嚎叫") == "howling"
        assert detect_behavior_category("夜间吠叫") == "howling"

    def test_aggression(self):
        assert detect_behavior_category("有攻击行为") == "aggression"
        assert detect_behavior_category("护食很凶") == "aggression"

    def test_food_refusal(self):
        assert detect_behavior_category("不吃东西") == "food_refusal"
        assert detect_behavior_category("拒食") == "food_refusal"

    def test_excessive_licking(self):
        assert detect_behavior_category("过度舔毛") == "excessive_licking"
        assert detect_behavior_category("不停舔爪子") == "excessive_licking"

    def test_other(self):
        assert detect_behavior_category("总是在角落发呆") == "other"


class TestGetBreedInfo:
    """品种特性查询测试"""

    def test_dog_breed_exact(self):
        info = get_breed_info("dog", "哈士奇")
        assert info is not None
        assert info["energy"] == "极高"
        assert "拆家" in info["common_issues"]

    def test_cat_breed_exact(self):
        info = get_breed_info("cat", "布偶猫")
        assert info is not None
        assert info["energy"] == "低"

    def test_breed_fuzzy_match(self):
        info = get_breed_info("dog", "金毛寻回犬")
        assert info is not None  # 应该模糊匹配到"金毛"

    def test_unknown_breed(self):
        info = get_breed_info("dog", "外星狗")
        assert info is None

    def test_no_breed(self):
        info = get_breed_info("dog", None)
        assert info is None


class TestCalculatePetAge:
    """宠物年龄计算测试"""

    def test_valid_birth_date(self):
        from datetime import date
        # 用一个固定日期测试
        age = calculate_pet_age_months(date(2024, 1, 1))
        assert age is not None
        assert age >= 0

    def test_none_birth_date(self):
        assert calculate_pet_age_months(None) is None


class TestBehaviorAnalysisTool:
    """行为分析工具测试"""

    @pytest.fixture
    def test_user(self, db_session: Session):
        user_data = UserCreate(phone="13800000001", email="test@example.com", password="test1234")
        return create_user(db_session, user_data)

    @pytest.fixture
    def test_pet(self, db_session: Session, test_user):
        pet_data = PetCreate(name="旺财", species="dog", breed="金毛", gender="male")
        return create_pet(db_session, test_user.user_id, pet_data)

    @pytest.fixture
    def test_cat(self, db_session: Session, test_user):
        pet_data = PetCreate(name="小花", species="cat", breed="布偶猫", gender="female")
        return create_pet(db_session, test_user.user_id, pet_data)

    def test_analyze_nonexistent_pet(self, db_session: Session):
        """测试分析不存在的宠物"""
        tool = BehaviorAnalysisTool(db=db_session)
        result = tool._run(pet_id="nonexistent", behavior_description="拆家")
        assert "error" in result

    def test_analyze_returns_structure(self, db_session: Session, test_pet):
        """测试分析返回正确结构"""
        tool = BehaviorAnalysisTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, behavior_description="最近总拆家")
        assert "possible_causes" in result
        assert "recommendations" in result
        assert "severity_level" in result
        assert "behavior_category" in result
        assert "disclaimer" in result

    def test_analyze_auto_detect_category(self, db_session: Session, test_pet):
        """测试自动检测行为类别"""
        tool = BehaviorAnalysisTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, behavior_description="最近总拆家")
        assert result["behavior_category"] == "destructive"

    def test_analyze_breed_analysis(self, db_session: Session, test_pet):
        """测试品种特性分析"""
        tool = BehaviorAnalysisTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, behavior_description="拆家")
        assert "breed_analysis" in result
        breed_analysis = result["breed_analysis"]
        assert breed_analysis["breed"] == "金毛"

    def test_analyze_cat_breed(self, db_session: Session, test_cat):
        """测试猫咪品种分析"""
        tool = BehaviorAnalysisTool(db=db_session)
        result = tool._run(pet_id=test_cat.pet_id, behavior_description="过度嚎叫")
        assert "breed_analysis" in result
        breed_analysis = result["breed_analysis"]
        assert breed_analysis["breed"] == "布偶猫"

    def test_severity_range(self, db_session: Session, test_pet):
        """测试严重程度在1-5范围"""
        tool = BehaviorAnalysisTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, behavior_description="偶尔发呆")
        assert 1 <= result["severity_level"] <= 5

    def test_aggression_high_severity(self, db_session: Session, test_pet):
        """测试攻击行为严重程度较高"""
        tool = BehaviorAnalysisTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, behavior_description="攻击行为")
        assert result["severity_level"] >= 3


class TestTrainingRecommendationTool:
    """训练建议工具测试"""

    @pytest.fixture
    def test_user(self, db_session: Session):
        user_data = UserCreate(phone="13800000001", email="test@example.com", password="test1234")
        return create_user(db_session, user_data)

    @pytest.fixture
    def test_pet(self, db_session: Session, test_user):
        pet_data = PetCreate(name="旺财", species="dog", breed="金毛", gender="male")
        return create_pet(db_session, test_user.user_id, pet_data)

    def test_nonexistent_pet(self, db_session: Session):
        """测试不存在的宠物"""
        tool = TrainingRecommendationTool(db=db_session)
        result = tool._run(pet_id="nonexistent")
        assert "error" in result

    def test_destructive_training(self, db_session: Session, test_pet):
        """测试拆家行为训练建议"""
        tool = TrainingRecommendationTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, behavior_category="destructive")
        assert "training_plan" in result
        assert len(result["training_plan"]) > 0
        assert "tips" in result

    def test_breed_specific_advice(self, db_session: Session, test_pet):
        """测试品种特定建议"""
        tool = TrainingRecommendationTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, behavior_category="destructive")
        assert "breed_specific_advice" in result
        assert len(result["breed_specific_advice"]) > 0

    def test_general_recommendation(self, db_session: Session, test_pet):
        """测试无指定类别时的综合建议"""
        tool = TrainingRecommendationTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id)
        assert "training_plan" in result
        assert len(result["training_plan"]) > 0

    def test_all_behavior_categories(self, db_session: Session, test_pet):
        """测试所有行为类别都有训练方案"""
        tool = TrainingRecommendationTool(db=db_session)
        for category in ["destructive", "howling", "aggression", "food_refusal", "excessive_licking"]:
            result = tool._run(pet_id=test_pet.pet_id, behavior_category=category)
            assert "training_plan" in result
            assert len(result["training_plan"]) > 0
