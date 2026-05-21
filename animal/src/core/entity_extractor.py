"""
实体关系抽取模块

从宠物健康知识库文本中提取：
1. 实体识别：物种、品种、疾病、症状、药物、身体部位等
2. 关系抽取：HAS_SYMPTOM、TREATED_BY、BELONGS_TO、AFFECTS 等
3. 实体消歧与标准化

支持LLM驱动抽取和规则驱动抽取两种模式。
"""
import json
import re
import logging
from typing import List, Dict, Any, Optional, Set, Tuple

from src.core.config import get_settings

logger = logging.getLogger(__name__)

ENTITY_EXTRACTION_PROMPT = """从以下宠物健康文本中提取实体和关系。

文本：{text}

请提取以下类型的实体：
- Species: 物种（狗/猫/其他）
- Breed: 品种
- Disease: 疾病名称
- Symptom: 症状
- Medication: 药物/治疗方法
- BodyPart: 身体部位/器官系统
- NutritionElement: 营养元素
- Behavior: 行为问题

关系类型：
- HAS_SYMPTOM: 疾病→症状
- BELONGS_TO: 品种→物种、症状→身体部位
- TREATED_BY: 疾病→药物
- AFFECTS: 疾病→身体部位
- CAUSES: 原因→疾病
- PREVENTS: 预防措施→疾病
- RELATED_TO: 疾病→疾病

输出JSON格式：
{{
  "entities": [
    {{"type": "Disease", "name": "犬瘟热", "aliases": ["狗瘟"], "properties": {{"severity": "high"}}}},
    {{"type": "Symptom", "name": "发热", "aliases": ["发烧", "体温升高"], "properties": {{}}}}
  ],
  "relations": [
    {{"from_type": "Disease", "from_name": "犬瘟热", "relation": "HAS_SYMPTOM", "to_type": "Symptom", "to_name": "发热"}},
    {{"from_type": "Symptom", "from_name": "发热", "relation": "BELONGS_TO", "to_type": "BodyPart", "to_name": "全身"}}
  ]
}}

只输出JSON，不加解释。"""


class EntityExtractor:
    """实体关系抽取器"""

    def __init__(self):
        self.settings = get_settings()
        self._llm = None
        self._llm_available = False
        self._init_llm()
        self._species_keywords = {"狗", "犬", "猫", "rabbit", "兔子", "仓鼠", "龙猫", "豚鼠", "鸟", "鱼"}
        self._body_parts = self._init_body_parts()
        self._disease_keywords = self._init_disease_keywords()

    def _init_llm(self):
        try:
            from src.core.llm import get_llm
            self._llm = get_llm()
            self._llm_available = True
        except Exception:
            self._llm_available = False

    @staticmethod
    def _init_body_parts() -> Dict[str, str]:
        return {
            "消化系统": "digestive",
            "肠胃": "digestive",
            "胃": "digestive",
            "肠道": "digestive",
            "呼吸系统": "respiratory",
            "肺": "respiratory",
            "呼吸道": "respiratory",
            "皮肤": "skin",
            "毛发": "skin",
            "泌尿系统": "urinary",
            "肾脏": "urinary",
            "膀胱": "urinary",
            "眼睛": "eye",
            "口腔": "oral",
            "牙齿": "oral",
            "牙龈": "oral",
            "骨骼": "skeletal",
            "关节": "skeletal",
            "心脏": "cardiovascular",
            "神经系统": "nervous",
            "免疫系统": "immune",
            "耳朵": "ear",
            "肝": "liver",
            "肝脏": "liver",
            "全身": "systemic",
        }

    @staticmethod
    def _init_disease_keywords() -> Dict[str, List[str]]:
        return {
            "犬瘟热": ["犬瘟"],
            "细小病毒": ["细小", "细小病毒肠炎"],
            "犬冠状病毒": ["冠状"],
            "狂犬病": ["疯狗病"],
            "犬传染性肝炎": ["传染性肝炎"],
            "猫瘟": ["猫泛白细胞减少症"],
            "猫杯状病毒": ["杯状病毒"],
            "猫疱疹病毒": ["疱疹病毒", "猫鼻支"],
            "猫传染性腹膜炎": ["传腹", "FIP"],
            "皮肤病": ["皮肤感染", "皮炎", "皮肤炎症"],
            "耳螨": ["耳疥虫"],
            "消化不良": ["消化问题", "肠胃不适"],
            "腹泻": ["拉肚子", "拉稀", "软便", "稀便"],
            "便秘": ["排便困难", "大便干结"],
            "呕吐": ["吐"],
            "感冒": ["上呼吸道感染"],
            "肺炎": ["肺部感染"],
            "关节炎": ["关节疼痛", "关节炎症"],
            "肥胖": ["超重", "体重过重"],
            "糖尿病": ["高血糖"],
            "猫下泌尿道疾病": ["FLUTD", "下泌尿道", "尿闭"],
            "肾衰竭": ["肾病", "肾脏疾病"],
            "心脏病": ["心脏疾病"],
            "寄生虫感染": ["体内寄生虫", "蛔虫", "绦虫", "钩虫"],
            "过敏": ["过敏反应", "食物过敏"],
            "口腔疾病": ["牙周病", "牙龈炎", "口炎"],
            "眼部疾病": ["结膜炎", "角膜炎", "白内障"],
            "耳部感染": ["中耳炎", "外耳炎"],
            "骨折": ["骨裂"],
            "脱毛": ["掉毛严重", "秃斑"],
        }

    def extract_from_text(
        self,
        text: str,
        known_species: str = "",
        known_breed: str = ""
    ) -> Dict[str, Any]:
        """从文本中提取实体和关系"""
        if self._llm_available and len(text) > 50:
            result = self._llm_extract(text, known_species, known_breed)
            if result.get("entities"):
                result["strategy"] = "llm"
                return result

        result = self._rule_extract(text, known_species, known_breed)
        result["strategy"] = "rule"
        return result

    def _llm_extract(self, text: str, species: str, breed: str) -> Dict[str, Any]:
        try:
            prompt = ENTITY_EXTRACTION_PROMPT.format(text=text[:1500])
            response = self._llm.invoke(prompt)
            resp_text = response.content if hasattr(response, "content") else str(response)
            resp_text = self._extract_json(resp_text)
            data = json.loads(resp_text)
            return {
                "entities": data.get("entities", []),
                "relations": data.get("relations", []),
            }
        except Exception as e:
            logger.warning(f"LLM实体抽取失败: {e}")
            return {"entities": [], "relations": []}

    def _rule_extract(self, text: str, species: str, breed: str) -> Dict[str, Any]:
        entities: List[Dict[str, Any]] = []
        relations: List[Dict[str, Any]] = []
        entity_map: Dict[str, Dict[str, Any]] = {}

        def add_entity(etype: str, name: str, aliases: List[str] = None, props: Dict = None):
            key = f"{etype}::{name}"
            if key not in entity_map:
                ent = {"type": etype, "name": name, "aliases": aliases or [], "properties": props or {}}
                entity_map[key] = ent
                entities.append(ent)
            return entity_map[key]

        def add_relation(f_type, f_name, rel, t_type, t_name):
            relations.append({
                "from_type": f_type, "from_name": f_name,
                "relation": rel,
                "to_type": t_type, "to_name": t_name,
            })

        if species:
            add_entity("Species", species, [species])
        if breed:
            brd = add_entity("Breed", breed, [breed])
            if species:
                add_relation("Breed", breed, "BELONGS_TO", "Species", species)

        if not species:
            if "猫" in text:
                species = "猫"
                add_entity("Species", "猫", ["猫", "猫咪"])
            elif "狗" in text or "犬" in text:
                species = "犬"
                add_entity("Species", "犬", ["狗", "犬", "狗狗"])

        for disease, aliases in self._disease_keywords.items():
            if disease in text or any(a in text for a in aliases):
                d = add_entity("Disease", disease, aliases)
                dis = None
                if species:
                    sp = entity_map.get(f"Species::{species}", add_entity("Species", species, [species]))
                if not any(r["from_type"] == "Disease" and r["from_name"] == disease and r["relation"] == "AFFECTS"
                           for r in relations):
                    pass

        for bp, bp_type in self._body_parts.items():
            if bp in text:
                add_entity("BodyPart", bp, [bp], {"system": bp_type})

        symptom_patterns = [
            r'(发热|发烧|体温升高|高烧|低烧)',
            r'(呕吐|恶心|干呕)',
            r'(腹泻|拉稀|拉肚子|软便|稀便|水样便)',
            r'(咳嗽|干咳|湿咳|咳痰)',
            r'(喷嚏|打喷嚏|流鼻涕|鼻塞)',
            r'(厌食|食欲不振|不吃东西|拒食)',
            r'(精神萎靡|精神不振|嗜睡|没精神)',
            r'(脱水|口干|皮肤弹性差)',
            r'(消瘦|体重下降|体重减轻)',
            r'(瘙痒|皮肤痒|抓挠)',
            r'(红肿|发红|肿胀|发肿)',
            r'(溃疡|溃烂|糜烂)',
            r'(出血|流血|便血|尿血)',
            r'(跛行|瘸|腿瘸|走路不正常)',
            r'(抽搐|痉挛|颤抖|发抖)',
            r'(呼吸困难|喘气|呼吸急促|气喘)',
            r'(流泪|眼睛流泪|泪痕)',
            r'(口臭|口腔异味)',
            r'(脱毛|掉毛|秃毛|斑秃)',
            r'(便秘|排便困难|不拉屎)',
        ]
        found_symptoms = set()
        for pattern in symptom_patterns:
            match = re.search(pattern, text)
            if match:
                symptom_name = match.group(1)
                if symptom_name not in found_symptoms:
                    found_symptoms.add(symptom_name)
                    add_entity("Symptom", symptom_name, list(match.groups()))

        medication_patterns = [
            r'(抗生素|阿莫西林|头孢|恩诺沙星|多西环素)',
            r'(驱虫药|吡喹酮|芬苯达唑|伊维菌素|阿苯达唑)',
            r'(止泻药|蒙脱石散|白陶土|益生菌)',
            r'(消炎药|泼尼松|地塞米松)',
            r'(眼药水|眼膏|氯霉素|妥布霉素)',
            r'(皮肤病药|药浴|药膏|喷剂)',
            r'(疫苗|免疫|接种|三联|五联|狂犬疫苗)',
            r'(营养品|维生素|钙片|鱼油|卵磷脂)',
        ]
        for pattern in medication_patterns:
            match = re.search(pattern, text)
            if match:
                med_name = match.group(1)
                add_entity("Medication", med_name, list(match.groups()))

        nutrition_keywords = ["蛋白质", "脂肪", "碳水", "维生素", "矿物质", "纤维", "Omega", "牛磺酸", "钙", "磷"]
        for nk in nutrition_keywords:
            if nk in text:
                add_entity("NutritionElement", nk, [nk])

        for disease_info in entities:
            if disease_info["type"] != "Disease":
                continue
            disease_name = disease_info["name"]
            for symptom_info in entities:
                if symptom_info["type"] == "Symptom":
                    add_relation("Disease", disease_name, "HAS_SYMPTOM", "Symptom", symptom_info["name"])
            for bp_info in entities:
                if bp_info["type"] == "BodyPart":
                    add_relation("Disease", disease_name, "AFFECTS", "BodyPart", bp_info["name"])
            for med_info in entities:
                if med_info["type"] == "Medication":
                    add_relation("Disease", disease_name, "TREATED_BY", "Medication", med_info["name"])
            for symptom_info in entities:
                if symptom_info["type"] == "Symptom":
                    for bp_info in entities:
                        if bp_info["type"] == "BodyPart":
                            add_relation("Symptom", symptom_info["name"], "BELONGS_TO", "BodyPart", bp_info["name"])

        for i, d1 in enumerate(entities):
            for d2 in entities[i + 1:]:
                if d1["type"] == "Disease" and d2["type"] == "Disease":
                    add_relation("Disease", d1["name"], "RELATED_TO", "Disease", d2["name"])

        return {
            "entities": entities,
            "relations": relations,
        }

    def extract_from_batch(self, texts: List[str], **kwargs) -> Dict[str, Any]:
        all_entities = []
        all_relations = []
        seen_entities = set()
        seen_relations = set()

        for text in texts:
            result = self.extract_from_text(text, **kwargs)
            for e in result.get("entities", []):
                key = f"{e['type']}::{e['name']}"
                if key not in seen_entities:
                    seen_entities.add(key)
                    all_entities.append(e)
            for r in result.get("relations", []):
                key = f"{r['from_type']}::{r['from_name']}::{r['relation']}::{r['to_type']}::{r['to_name']}"
                if key not in seen_relations:
                    seen_relations.add(key)
                    all_relations.append(r)

        return {
            "entities": all_entities,
            "relations": all_relations,
            "strategy": result.get("strategy", "rule"),
        }

    @staticmethod
    def _extract_json(text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group()
        return text


_entity_extractor: Optional[EntityExtractor] = None


def get_entity_extractor() -> EntityExtractor:
    global _entity_extractor
    if _entity_extractor is None:
        _entity_extractor = EntityExtractor()
    return _entity_extractor