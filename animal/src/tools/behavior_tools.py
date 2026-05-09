"""
行为分析工具集

提供行为分析、训练建议生成等工具，集成品种特性数据和RAG知识库
"""
import json
import logging
from typing import ClassVar, Dict, Any, List, Optional, Type
from datetime import date

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from langchain_core.prompts import ChatPromptTemplate

from src.tools.base import BaseTool
from src.db.crud import get_pet_by_id
from src.core.vector_db import get_vector_db

logger = logging.getLogger(__name__)


# ========== 品种特性数据库 ==========

BREED_CHARACTERISTICS = {
    "dog": {
        "哈士奇": {
            "energy": "极高",
            "traits": ["精力旺盛", "独立", "爱嚎叫", "固执"],
            "common_issues": ["拆家", "嚎叫", "逃跑", "破坏家具"],
            "exercise_need": "每日至少2小时高强度运动",
        },
        "边牧": {
            "energy": "极高",
            "traits": ["聪明", "工作欲强", "需要精神刺激", "敏感"],
            "common_issues": ["拆家", "追车", "强迫症", "过度兴奋"],
            "exercise_need": "每日至少2小时运动+智力训练",
        },
        "金毛": {
            "energy": "高",
            "traits": ["温顺", "亲人", "需要运动", "贪吃"],
            "common_issues": ["分离焦虑", "过度兴奋", "拆家"],
            "exercise_need": "每日至少1-1.5小时运动",
        },
        "拉布拉多": {
            "energy": "高",
            "traits": ["活泼", "温顺", "贪吃", "晚熟"],
            "common_issues": ["拆家", "过度兴奋", "肥胖"],
            "exercise_need": "每日至少1-1.5小时运动",
        },
        "法斗": {
            "energy": "低",
            "traits": ["安静", "粘人", "固执"],
            "common_issues": ["护食", "打鼾", "分离焦虑"],
            "exercise_need": "每日30分钟温和运动",
        },
        "柯基": {
            "energy": "中高",
            "traits": ["聪明", "倔强", "牧羊本能"],
            "common_issues": ["追脚", "吠叫", "肥胖"],
            "exercise_need": "每日至少1小时运动",
        },
        "泰迪": {
            "energy": "中",
            "traits": ["聪明", "粘人", "敏感"],
            "common_issues": ["吠叫", "分离焦虑", "标记行为"],
            "exercise_need": "每日45分钟-1小时运动",
        },
        "柴犬": {
            "energy": "中高",
            "traits": ["独立", "倔强", "爱干净"],
            "common_issues": ["固执", "逃跑", "攻击性"],
            "exercise_need": "每日至少1小时运动",
        },
        "德牧": {
            "energy": "高",
            "traits": ["忠诚", "保护欲强", "聪明"],
            "common_issues": ["过度保护", "焦虑", "追咬"],
            "exercise_need": "每日至少1.5小时运动+训练",
        },
        "萨摩耶": {
            "energy": "高",
            "traits": ["友好", "活泼", "爱叫"],
            "common_issues": ["拆家", "嚎叫", "过度兴奋"],
            "exercise_need": "每日至少1.5小时运动",
        },
    },
    "cat": {
        "布偶猫": {
            "energy": "低",
            "traits": ["温顺", "粘人", "安静"],
            "common_issues": ["分离焦虑", "过度依赖", "抑郁"],
            "exercise_need": "每日15-30分钟互动游戏",
        },
        "英短": {
            "energy": "中",
            "traits": ["独立", "安静", "慵懒"],
            "common_issues": ["肥胖", "懒惰", "攻击性（受惊时）"],
            "exercise_need": "每日20-30分钟互动游戏",
        },
        "美短": {
            "energy": "中高",
            "traits": ["活泼", "好奇", "亲人"],
            "common_issues": ["拆家", "过度活跃", "夜行活动"],
            "exercise_need": "每日30分钟互动游戏",
        },
        "折耳猫": {
            "energy": "低",
            "traits": ["安静", "温顺", "忍痛"],
            "common_issues": ["骨骼问题导致异常行为", "活动减少", "攻击性（疼痛引起）"],
            "exercise_need": "每日15分钟温和互动",
        },
        "暹罗猫": {
            "energy": "高",
            "traits": ["话多", "粘人", "聪明"],
            "common_issues": ["过度嚎叫", "分离焦虑", "拆家"],
            "exercise_need": "每日30-45分钟互动游戏",
        },
        "橘猫": {
            "energy": "中",
            "traits": ["贪吃", "亲人", "随和"],
            "common_issues": ["肥胖", "偷食", "过度乞食"],
            "exercise_need": "每日20-30分钟互动游戏",
        },
        "波斯猫": {
            "energy": "低",
            "traits": ["安静", "优雅", "敏感"],
            "common_issues": ["拒食", "过度舔毛", "应激反应"],
            "exercise_need": "每日15分钟温和互动",
        },
        "狸花猫": {
            "energy": "高",
            "traits": ["野性", "独立", "好奇", "猎手本能"],
            "common_issues": ["攻击性", "抓咬", "夜行活动", "领地标记"],
            "exercise_need": "每日30-45分钟互动游戏",
        },
    },
}

# 行为类别关键词映射
BEHAVIOR_KEYWORD_MAP = {
    "destructive": ["拆家", "咬坏", "破坏", "啃咬", "撕咬", "抓烂", "咬沙发", "咬鞋", "破坏家具"],
    "howling": ["嚎叫", "吠叫", "叫唤", "哀嚎", "过度叫", "不停叫", "夜间叫"],
    "aggression": ["攻击", "咬人", "凶", "护食", "护地盘", "对人不友好", "追咬", "攻击性"],
    "food_refusal": ["拒食", "不吃", "不吃饭", "厌食", "挑食"],
    "excessive_licking": ["过度舔毛", "舔爪", "不停舔", "舔秃", "过度梳理"],
}


def detect_behavior_category(description: str) -> str:
    """从行为描述中自动检测行为类别"""
    for category, keywords in BEHAVIOR_KEYWORD_MAP.items():
        for kw in keywords:
            if kw in description:
                return category
    return "other"


def get_breed_info(species: str, breed: Optional[str]) -> Optional[Dict[str, Any]]:
    """获取品种特性信息"""
    if not breed:
        return None
    species_data = BREED_CHARACTERISTICS.get(species, {})
    # 精确匹配
    if breed in species_data:
        return species_data[breed]
    # 模糊匹配
    for breed_name, info in species_data.items():
        if breed_name in breed or breed in breed_name:
            return info
    return None


def calculate_pet_age_months(birth_date: Optional[date]) -> Optional[int]:
    """计算宠物年龄（月）"""
    if not birth_date:
        return None
    today = date.today()
    months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)
    return max(0, months)


# ========== BehaviorAnalysisTool ==========

class BehaviorAnalysisInput(BaseModel):
    """行为分析工具输入"""
    pet_id: str = Field(..., description="宠物ID")
    behavior_description: str = Field(..., description="行为描述")
    behavior_category: Optional[str] = Field(None, description="行为类别(可选)")


class BehaviorAnalysisTool(BaseTool):
    """行为分析工具 - 编排完整行为分析流程"""

    name: str = "analyze_behavior"
    description: str = "分析宠物异常行为，结合宠物档案、品种特性和行为知识库生成原因分析和训练建议"
    args_schema: Type[BaseModel] = BehaviorAnalysisInput

    db: Session = Field(..., description="数据库会话")

    def _run(
        self,
        pet_id: str,
        behavior_description: str,
        behavior_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """执行行为分析"""
        # 1. 加载宠物档案
        pet = get_pet_by_id(self.db, pet_id)
        if not pet:
            return {"error": f"未找到ID为{pet_id}的宠物"}

        # 2. 自动检测行为类别
        if not behavior_category:
            behavior_category = detect_behavior_category(behavior_description)

        # 3. 品种特性分析
        breed_info = get_breed_info(pet.species, pet.breed)
        breed_analysis = self._analyze_breed_relevance(pet, breed_info, behavior_description)

        # 4. 年龄阶段分析
        age_months = calculate_pet_age_months(pet.birth_date)
        age_analysis = self._analyze_age_factor(age_months, behavior_description)

        # 5. 查询知识库
        query_text = f"{pet.species} {pet.breed or ''} 行为: {behavior_description}"
        vector_db = get_vector_db()
        kb_results = vector_db.query(query_texts=[query_text], n_results=5)

        knowledge_items = []
        if kb_results and kb_results.get('documents'):
            for i, doc in enumerate(kb_results['documents'][0]):
                knowledge_items.append({
                    'content': doc,
                    'relevance': 1 - kb_results['distances'][0][i] if kb_results.get('distances') else 0.5
                })

        # 6. 使用LLM生成结构化分析
        pet_info = {
            "name": pet.name,
            "species": pet.species,
            "breed": pet.breed,
            "gender": pet.gender,
            "weight": float(pet.weight) if pet.weight else None,
            "is_neutered": pet.is_neutered,
            "age_months": age_months,
        }

        analysis_result = self._analyze_with_llm(
            pet_info=pet_info,
            behavior_description=behavior_description,
            behavior_category=behavior_category,
            breed_analysis=breed_analysis,
            age_analysis=age_analysis,
            knowledge=knowledge_items,
        )

        # 7. 评估严重程度
        severity = self._assess_severity(behavior_description, behavior_category, analysis_result)

        return {
            "pet_id": pet_id,
            "pet_name": pet.name,
            "behavior_category": behavior_category,
            "possible_causes": analysis_result.get("possible_causes", []),
            "breed_analysis": breed_analysis,
            "recommendations": analysis_result.get("recommendations", []),
            "severity_level": severity,
            "disclaimer": "以上分析仅供参考，如有严重行为问题建议咨询专业宠物训练师。",
        }

    def _analyze_breed_relevance(
        self,
        pet,
        breed_info: Optional[Dict],
        behavior_description: str
    ) -> Dict[str, Any]:
        """分析品种与行为的关联"""
        if not breed_info:
            return {
                "breed": pet.breed or "未知",
                "relevance": "unknown",
                "note": "未找到该品种的特定行为特征数据",
            }

        # 检查行为描述是否与品种常见问题匹配
        matched_issues = []
        for issue in breed_info.get("common_issues", []):
            if issue in behavior_description or any(kw in behavior_description for kw in [issue]):
                matched_issues.append(issue)

        return {
            "breed": pet.breed,
            "energy_level": breed_info.get("energy", "未知"),
            "traits": breed_info.get("traits", []),
            "common_issues": breed_info.get("common_issues", []),
            "exercise_need": breed_info.get("exercise_need", ""),
            "matched_issues": matched_issues,
            "relevance": "high" if matched_issues else "low",
        }

    def _analyze_age_factor(
        self,
        age_months: Optional[int],
        behavior_description: str
    ) -> Dict[str, Any]:
        """分析年龄因素对行为的影响"""
        if age_months is None:
            return {"stage": "unknown", "factors": []}

        factors = []
        if age_months < 6:
            stage = "幼年期"
            factors.append("幼宠处于社会化关键期，行为不稳定属正常")
            if "咬" in behavior_description or "啃" in behavior_description:
                factors.append("幼宠换牙期，啃咬行为属正常")
        elif age_months < 18:
            stage = "青少年期"
            factors.append("精力旺盛期，运动需求最高")
            if "拆家" in behavior_description or "破坏" in behavior_description:
                factors.append("青少年期精力无处释放，拆家概率最高")
        elif age_months < 84:
            stage = "成年期"
            factors.append("行为相对稳定")
        else:
            stage = "老年期"
            factors.append("老年宠物可能出现认知功能下降")
            if any(kw in behavior_description for kw in ["叫", "夜间", "迷失", "乱尿"]):
                factors.append("可能存在老年认知障碍(CDS)")

        return {"stage": stage, "age_months": age_months, "factors": factors}

    def _analyze_with_llm(
        self,
        pet_info: Dict,
        behavior_description: str,
        behavior_category: str,
        breed_analysis: Dict,
        age_analysis: Dict,
        knowledge: List[Dict],
    ) -> Dict[str, Any]:
        """使用LLM进行结构化行为分析 (OPT-B-03: 结构化输出)"""
        try:
            from src.core.llm import get_llm
            llm = get_llm()
        except Exception:
            return self._fallback_analysis(breed_analysis, age_analysis, knowledge)

        knowledge_text = "\n".join(
            f"- {item['content']} (相关度: {item['relevance']:.2f})"
            for item in knowledge[:3]
        )

        # OPT-B-03: 使用Pydantic schema强制LLM返回结构化JSON
        from src.schemas.llm_output import BehaviorAnalysisResult
        from langchain_core.output_parsers import JsonOutputParser

        parser = JsonOutputParser(pydantic_object=BehaviorAnalysisResult)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一位专业的宠物行为分析师。请根据以下信息进行行为分析。

宠物信息:
{pet_info}

行为描述: {behavior_description}
行为类别: {behavior_category}

品种特性分析:
{breed_analysis}

年龄阶段分析:
{age_analysis}

相关知识:
{knowledge}

{format_instructions}"""),
            ("human", "")
        ])

        chain = prompt | llm | parser

        try:
            result = chain.invoke({
                "pet_info": json.dumps(pet_info, ensure_ascii=False),
                "behavior_description": behavior_description,
                "behavior_category": behavior_category,
                "breed_analysis": json.dumps(breed_analysis, ensure_ascii=False),
                "age_analysis": json.dumps(age_analysis, ensure_ascii=False),
                "knowledge": knowledge_text or "无相关知识点",
                "format_instructions": parser.get_format_instructions(),
            })
            return result
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"LLM行为分析失败，使用降级方案: {e}")
            return self._fallback_analysis(breed_analysis, age_analysis, knowledge)

    def _fallback_analysis(
        self,
        breed_analysis: Dict,
        age_analysis: Dict,
        knowledge: List[Dict],
    ) -> Dict[str, Any]:
        """降级方案: 无LLM时基于品种和知识库的基本分析"""
        causes = []

        # 基于品种特性
        if breed_analysis.get("relevance") == "high":
            for issue in breed_analysis.get("matched_issues", []):
                causes.append({
                    "cause": f"品种特性：{breed_analysis.get('breed', '')}常见{issue}行为",
                    "probability": 0.7,
                    "category": "breed",
                })

        # 基于年龄
        for factor in age_analysis.get("factors", []):
            causes.append({
                "cause": factor,
                "probability": 0.5,
                "category": "age",
            })

        # 基于知识库
        for item in knowledge[:2]:
            causes.append({
                "cause": item['content'][:100],
                "probability": item.get('relevance', 0.5),
                "category": "environment",
            })

        if not causes:
            causes.append({
                "cause": "需进一步观察和分析",
                "probability": 0.3,
                "category": "environment",
            })

        return {
            "possible_causes": causes,
            "recommendations": ["建议咨询专业宠物训练师进行详细行为评估"],
        }

    def _assess_severity(
        self,
        behavior_description: str,
        behavior_category: str,
        analysis_result: Dict,
    ) -> int:
        """评估行为问题严重程度 (1-5)"""
        # 严重行为关键词
        severe_keywords = ["攻击人", "咬人", "咬出血", "伤人"]
        moderate_severe_keywords = ["攻击", "护食", "咬", "破坏家具"]
        moderate_keywords = ["拆家", "嚎叫", "不停叫", "拒食", "过度舔毛"]

        for kw in severe_keywords:
            if kw in behavior_description:
                return 4

        if behavior_category == "aggression":
            return 3

        for kw in moderate_severe_keywords:
            if kw in behavior_description:
                return 3

        for kw in moderate_keywords:
            if kw in behavior_description:
                return 2

        return 1


# ========== TrainingRecommendationTool ==========

class TrainingRecommendationInput(BaseModel):
    """训练建议工具输入"""
    pet_id: str = Field(..., description="宠物ID")
    behavior_category: Optional[str] = Field(None, description="行为类别(可选)")


class TrainingRecommendationTool(BaseTool):
    """训练建议生成工具"""

    name: str = "get_training_recommendations"
    description: str = "根据宠物品种和行为类别，生成具体可操作的训练建议和计划"
    args_schema: Type[BaseModel] = TrainingRecommendationInput

    db: Session = Field(..., description="数据库会话")

    # 行为类别对应的训练方案
    TRAINING_PLANS: ClassVar[Dict[str, Any]] = {
        "destructive": {
            "methods": [
                {"name": "增加运动量", "description": "确保每日充足运动消耗精力", "duration": "持续2-4周见效"},
                {"name": "环境丰富化", "description": "提供益智玩具、嗅闻垫、漏食球等", "duration": "立即实施"},
                {"name": "行为替代训练", "description": "啃咬家具时制止并引导到磨牙玩具", "duration": "持续1-3周"},
                {"name": "笼内训练", "description": "无人看管时使用笼子防止破坏", "duration": "1-2周适应期"},
            ],
            "tips": [
                "不要事后惩罚，宠物无法关联过去的行为",
                "确保每天有足够的运动和精神刺激",
                "把贵重物品收好，减少犯错机会",
            ],
        },
        "howling": {
            "methods": [
                {"name": "脱敏训练", "description": "逐步让宠物适应独处，从短时间开始", "duration": "2-6周"},
                {"name": "忽略法", "description": "嚎叫时不予回应，安静时给予奖励", "duration": "1-3周见效"},
                {"name": "消耗精力", "description": "出门前充分运动消耗体力", "duration": "立即实施"},
                {"name": "背景音", "description": "播放轻音乐或电视声音减少孤独感", "duration": "立即实施"},
            ],
            "tips": [
                "不要在宠物嚎叫时给予关注（即使是训斥）",
                "确认嚎叫不是因疼痛或不适引起",
                "邻居投诉前主动沟通并说明正在训练",
            ],
        },
        "aggression": {
            "methods": [
                {"name": "专业评估", "description": "强烈建议先咨询专业训练师评估攻击原因", "duration": "尽快"},
                {"name": "脱敏与反条件", "description": "在安全距离下逐步接触触发因素", "duration": "4-12周"},
                {"name": "资源管理", "description": "管理食物、玩具等资源，避免护食护物", "duration": "持续实施"},
                {"name": "口令训练", "description": "强化基本服从训练（坐、等、来）", "duration": "2-4周基础"},
            ],
            "tips": [
                "攻击行为务必寻求专业帮助",
                "不要用惩罚方式处理攻击行为，可能加重",
                "确保家人和访客安全，使用嘴套等安全措施",
                "排除疼痛导致的攻击性（先做体检）",
            ],
        },
        "food_refusal": {
            "methods": [
                {"name": "定时喂食", "description": "固定时间放粮，15-20分钟未吃完即收走", "duration": "1-2周见效"},
                {"name": "减少零食", "description": "正餐之间不给零食", "duration": "立即实施"},
                {"name": "食物更换", "description": "尝试不同口味或品牌的粮食", "duration": "逐步过渡7天"},
                {"name": "增加运动", "description": "饭前运动增加食欲", "duration": "立即实施"},
            ],
            "tips": [
                "持续拒食超过24小时需要就医",
                "不要因为拒食就加零食或人食",
                "排除口腔疾病或消化问题",
            ],
        },
        "excessive_licking": {
            "methods": [
                {"name": "排除医疗原因", "description": "先检查是否有皮肤病、过敏或伤口", "duration": "尽快就医"},
                {"name": "伊丽莎白圈", "description": "严重时使用伊丽莎白圈防止继续舔", "duration": "按需使用"},
                {"name": "转移注意力", "description": "舔毛时用玩具或训练活动转移", "duration": "持续实施"},
                {"name": "环境减压", "description": "减少压力源，增加安全感", "duration": "2-4周"},
            ],
            "tips": [
                "过度舔毛常与压力或皮肤问题有关",
                "检查是否有跳蚤、螨虫等寄生虫",
                "猫咪过度舔毛需排除猫心因性脱毛",
            ],
        },
    }

    def _run(
        self,
        pet_id: str,
        behavior_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成训练建议"""
        # 1. 加载宠物档案
        pet = get_pet_by_id(self.db, pet_id)
        if not pet:
            return {"error": f"未找到ID为{pet_id}的宠物"}

        # 2. 获取品种特性
        breed_info = get_breed_info(pet.species, pet.breed)

        # 3. 生成品种特定建议
        breed_specific_advice = self._get_breed_advice(pet, breed_info)

        # 4. 获取行为类别训练方案
        training_plan = []
        tips = []
        if behavior_category and behavior_category in self.TRAINING_PLANS:
            plan_data = self.TRAINING_PLANS[behavior_category]
            training_plan = plan_data["methods"]
            tips = plan_data["tips"]
        else:
            # 综合建议
            training_plan = [
                {"name": "基本服从训练", "description": "建立基本指令响应（坐、等、来）", "duration": "2-4周基础"},
                {"name": "正向强化", "description": "用零食和表扬奖励好行为", "duration": "持续实施"},
            ]
            tips = ["持续一致的训练是关键", "保持耐心，行为改变需要时间"]

        return {
            "pet_id": pet_id,
            "pet_name": pet.name,
            "behavior_category": behavior_category,
            "breed_specific_advice": breed_specific_advice,
            "training_plan": training_plan,
            "tips": tips,
            "disclaimer": "以上训练建议仅供参考，如行为问题严重建议咨询专业宠物训练师。",
        }

    def _get_breed_advice(self, pet, breed_info: Optional[Dict]) -> List[str]:
        """生成品种特定建议"""
        advice = []
        if not breed_info:
            advice.append(f"建议了解{pet.breed or '该品种'}的特有行为特征")
            return advice

        energy = breed_info.get("energy", "")
        if energy in ("高", "极高"):
            advice.append(f"{pet.breed}精力{energy}，必须保证充足运动量")
        if energy in ("低",):
            advice.append(f"{pet.breed}精力较低，适合温和互动，避免过度刺激")

        exercise = breed_info.get("exercise_need", "")
        if exercise:
            advice.append(f"建议运动量：{exercise}")

        traits = breed_info.get("traits", [])
        if "聪明" in traits:
            advice.append("该品种聪明，需要智力训练（益智玩具、学习新指令）保持心理健康")
        if "粘人" in traits:
            advice.append("该品种容易产生分离焦虑，建议进行独处训练")
        if "独立" in traits or "倔强" in traits:
            advice.append("该品种性格独立/倔强，训练需更多耐心，避免强硬手段")
        if "敏感" in traits:
            advice.append("该品种敏感，训练时语气温和，避免大声呵斥")

        return advice
