"""
健康咨询工具单元测试
"""
import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from src.tools.health_tools import (
    HealthConsultTool,
    UrgencyAssessmentTool,
    HealthRecordTool,
)
from src.db.crud import create_user, create_pet
from src.schemas.user import UserCreate
from src.schemas.pet import PetCreate


class TestUrgencyAssessmentTool:
    """紧急度评估工具测试"""

    def test_emergency_symptoms(self):
        """测试紧急症状"""
        tool = UrgencyAssessmentTool()
        result = tool._run(symptoms=["抽搐", "呼吸困难"], pet_species="dog")
        assert result["urgency_level"] == 5
        assert "紧急" in result["reasoning"]

    def test_urgent_symptoms(self):
        """测试较急症状"""
        tool = UrgencyAssessmentTool()
        result = tool._run(symptoms=["拒食", "精神萎靡"], pet_species="dog")
        assert result["urgency_level"] == 4

    def test_moderate_symptoms(self):
        """测试中等症状"""
        tool = UrgencyAssessmentTool()
        result = tool._run(symptoms=["呕吐", "腹泻"], pet_species="cat")
        assert result["urgency_level"] == 2

    def test_mild_symptoms(self):
        """测试轻微症状"""
        tool = UrgencyAssessmentTool()
        result = tool._run(symptoms=["偶尔发呆"], pet_species="cat")
        assert result["urgency_level"] == 1

    def test_young_pet_higher_risk(self):
        """测试幼宠风险加成"""
        tool = UrgencyAssessmentTool()
        result = tool._run(symptoms=["呕吐"], pet_species="dog", pet_age_months=3)
        # 幼宠风险+1
        assert result["urgency_level"] >= 3

    def test_senior_pet_higher_risk(self):
        """测试老年宠物风险加成"""
        tool = UrgencyAssessmentTool()
        result = tool._run(symptoms=["呕吐"], pet_species="dog", pet_age_months=120)
        assert result["urgency_level"] >= 3

    def test_high_risk_breed(self):
        """测试高风险品种"""
        tool = UrgencyAssessmentTool()
        result = tool._run(symptoms=["咳嗽"], pet_species="dog", pet_breed="法斗")
        # 法斗是高风险品种
        assert result["urgency_level"] >= 3


class TestHealthRecordTool:
    """健康记录工具测试"""

    @pytest.fixture
    def test_user(self, db_session: Session):
        user_data = UserCreate(phone="13800000001", email="test@example.com", password="test1234")
        return create_user(db_session, user_data)

    @pytest.fixture
    def test_pet(self, db_session: Session, test_user):
        pet_data = PetCreate(name="旺财", species="dog", breed="金毛", gender="male")
        return create_pet(db_session, test_user.user_id, pet_data)

    def test_get_empty_health_records(self, db_session: Session, test_pet):
        """测试获取空健康记录"""
        tool = HealthRecordTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id)
        assert isinstance(result, list)
        assert len(result) == 0


class TestHealthConsultTool:
    """健康咨询工具测试"""

    @pytest.fixture
    def test_user(self, db_session: Session):
        user_data = UserCreate(phone="13800000001", email="test@example.com", password="test1234")
        return create_user(db_session, user_data)

    @pytest.fixture
    def test_pet(self, db_session: Session, test_user):
        pet_data = PetCreate(name="旺财", species="dog", breed="金毛", gender="male")
        return create_pet(db_session, test_user.user_id, pet_data)

    def test_consult_nonexistent_pet(self, db_session: Session):
        """测试咨询不存在的宠物"""
        tool = HealthConsultTool(db=db_session)
        result = tool._run(pet_id="nonexistent", symptoms=["呕吐"])
        assert "error" in result

    def test_consult_returns_urgency(self, db_session: Session, test_pet):
        """测试咨询返回紧急度"""
        tool = HealthConsultTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, symptoms=["呕吐", "腹泻"])
        assert "urgency_level" in result
        assert isinstance(result["urgency_level"], int)
        assert 1 <= result["urgency_level"] <= 5

    def test_consult_returns_disclaimer(self, db_session: Session, test_pet):
        """测试咨询返回免责声明"""
        tool = HealthConsultTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, symptoms=["呕吐"])
        assert "disclaimer" in result
        assert len(result["disclaimer"]) > 0

    def test_consult_returns_diagnosis(self, db_session: Session, test_pet):
        """测试咨询返回诊断结果"""
        tool = HealthConsultTool(db=db_session)
        result = tool._run(pet_id=test_pet.pet_id, symptoms=["咳嗽", "打喷嚏"])
        assert "diagnosis_result" in result
        assert "recommendations" in result
