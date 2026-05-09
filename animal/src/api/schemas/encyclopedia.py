from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class BreedFeatures(BaseModel):
    origin: str = Field("", description="原产地")
    size: str = Field("", description="体型大小")
    weight: str = Field("", description="体重范围")
    lifespan: str = Field("", description="平均寿命")
    coat: str = Field("", description="被毛类型")
    colors: List[str] = Field(default_factory=list, description="毛色")


class BreedCare(BaseModel):
    exercise: str = Field("", description="运动需求")
    grooming: str = Field("", description="美容护理")
    diet: str = Field("", description="饮食建议")
    training: str = Field("", description="训练难度")


class BreedDetail(BaseModel):
    id: str = Field(..., description="品种ID")
    name: str = Field(..., description="品种名称")
    english_name: str = Field("", description="英文名称")
    species: str = Field(..., description="物种: cat/dog")
    category: str = Field("", description="品种类别")
    description: str = Field("", description="品种简介")
    summary: str = Field("", description="一句话概述")
    features: BreedFeatures = Field(default_factory=BreedFeatures, description="标准特征")
    personality: List[str] = Field(default_factory=list, description="性格特点")
    care_requirements: BreedCare = Field(default_factory=BreedCare, description="饲养要求")
    health_issues: List[str] = Field(default_factory=list, description="常见健康问题")
    suitable_for: List[str] = Field(default_factory=list, description="适合人群")
    image_emoji: str = Field("🐾", description="品种表情符号")
    popularity: int = Field(5, ge=1, le=10, description="受欢迎程度 1-10")


class BreedSummary(BaseModel):
    id: str = Field(..., description="品种ID")
    name: str = Field(..., description="品种名称")
    english_name: str = Field("", description="英文名称")
    species: str = Field(..., description="物种: cat/dog")
    summary: str = Field("", description="一句话概述")
    image_emoji: str = Field("🐾", description="品种表情符号")
    popularity: int = Field(5, ge=1, le=10, description="受欢迎程度")


class BreedListResponse(BaseModel):
    species: str = Field(..., description="物种: cat/dog")
    breeds: List[BreedSummary] = Field(..., description="品种列表")


class BreedDetailResponse(BaseModel):
    breed: BreedDetail = Field(..., description="品种详细信息")


class HealthCondition(BaseModel):
    id: str = Field(..., description="病症ID")
    name: str = Field(..., description="病症名称")
    species: str = Field(..., description="适用物种: cat/dog/both")
    category: str = Field(..., description="病症类别")
    description: str = Field("", description="病症描述")
    symptoms: List[str] = Field(default_factory=list, description="常见症状")
    urgent_symptoms: List[str] = Field(default_factory=list, description="需立即就医的症状")
    possible_causes: List[str] = Field(default_factory=list, description="可能病因")
    severity: str = Field("mild", description="严重程度: mild/moderate/severe/emergency")
    treatment: List[str] = Field(default_factory=list, description="治疗方案")
    home_care: List[str] = Field(default_factory=list, description="日常护理建议")
    prevention: List[str] = Field(default_factory=list, description="预防措施")
    image_emoji: str = Field("🏥", description="表情符号")


class HealthConditionSummary(BaseModel):
    id: str = Field(..., description="病症ID")
    name: str = Field(..., description="病症名称")
    species: str = Field(..., description="适用物种")
    category: str = Field(..., description="病症类别")
    severity: str = Field(..., description="严重程度")
    image_emoji: str = Field("🏥", description="表情符号")


class HealthCategoryGroup(BaseModel):
    category: str = Field(..., description="疾病类别")
    category_label: str = Field("", description="类别名称")
    conditions: List[HealthConditionSummary] = Field(..., description="病症列表")


class HealthListResponse(BaseModel):
    species: str = Field(..., description="物种: cat/dog/both")
    categories: List[HealthCategoryGroup] = Field(..., description="按类别分组的病症列表")


class HealthDetailResponse(BaseModel):
    condition: HealthCondition = Field(..., description="病症详细信息")


class KnowledgeCategoriesResponse(BaseModel):
    categories: List[dict] = Field(..., description="知识分类列表")


class SearchKnowledgeResponse(BaseModel):
    breeds: List[BreedSummary] = Field(default_factory=list, description="匹配的品种")
    conditions: List[HealthConditionSummary] = Field(default_factory=list, description="匹配的病症")
