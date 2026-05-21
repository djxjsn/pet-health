"""
知识图谱构建器

将实体关系抽取结果构建为知识图谱：
1. 实体节点创建与合并
2. 关系边创建与去重
3. 层级索引构建（品种→物种，症状→身体部位→系统）
4. 社区检测与摘要生成
"""
import hashlib
import logging
from typing import List, Dict, Any, Optional, Set

from src.core.graph_db import get_graph_db
from src.core.entity_extractor import get_entity_extractor

logger = logging.getLogger(__name__)


class GraphBuilder:
    """知识图谱构建器"""

    def __init__(self):
        self.graph_db = get_graph_db()
        self.extractor = get_entity_extractor()

    def build_from_texts(
        self,
        texts: List[str],
        species: str = "",
        breed: str = "",
        rebuild: bool = False
    ) -> Dict[str, Any]:
        """从文本列表构建知识图谱"""
        if rebuild:
            self.graph_db.clear_all()
            logger.info("已清空现有图谱")

        extraction = self.extractor.extract_from_batch(texts, known_species=species, known_breed=breed)

        entity_count = 0
        relation_count = 0

        for entity in extraction.get("entities", []):
            eid = self._generate_entity_id(entity["type"], entity["name"])
            props = {
                "name": entity["name"],
                "aliases": entity.get("aliases", []),
            }
            props.update(entity.get("properties", {}))
            if self.graph_db.create_entity(entity["type"], eid, props):
                entity_count += 1

        for relation in extraction.get("relations", []):
            from_id = self._generate_entity_id(relation["from_type"], relation["from_name"])
            to_id = self._generate_entity_id(relation["to_type"], relation["to_name"])
            if self.graph_db.create_relation(
                relation["from_type"], from_id,
                relation["relation"],
                relation["to_type"], to_id
            ):
                relation_count += 1

        stats = self.graph_db.get_stats()

        logger.info(f"图谱构建完成: {entity_count}实体, {relation_count}关系")
        return {
            "entities_added": entity_count,
            "relations_added": relation_count,
            "stats": stats,
            "strategy": extraction.get("strategy", "rule"),
        }

    def build_from_knowledge_base(
        self,
        documents: List[Dict[str, Any]],
        rebuild: bool = False
    ) -> Dict[str, Any]:
        """从已有知识库文档构建图谱"""
        texts = []
        species = ""
        breed = ""

        for doc in documents:
            content = doc.get("content", "")
            if content:
                texts.append(content)
            metadata = doc.get("metadata", {})
            doc_species = metadata.get("species", "")
            doc_breed = metadata.get("breed", "")
            if doc_species and not species:
                species = doc_species
            if doc_breed and not breed:
                breed = doc_breed

        return self.build_from_texts(texts, species=species, breed=breed, rebuild=rebuild)

    def add_structured_knowledge(
        self,
        breeds_data: Dict[str, Any],
        health_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """从结构化百科数据构建图谱"""
        entity_count = 0
        relation_count = 0

        for species_name, breeds in breeds_data.items():
            sp_id = self._generate_entity_id("Species", species_name)
            if self.graph_db.create_entity("Species", sp_id, {"name": species_name}):
                entity_count += 1

            for breed_info in breeds:
                breed_name = breed_info.get("name", "")
                breed_id = self._generate_entity_id("Breed", breed_name)
                if self.graph_db.create_entity("Breed", breed_id, {
                    "name": breed_name,
                    "temperament": breed_info.get("temperament", ""),
                    "size": breed_info.get("size", ""),
                    "lifespan": breed_info.get("lifespan", ""),
                }):
                    entity_count += 1
                if self.graph_db.create_relation("Breed", breed_id, "BELONGS_TO", "Species", sp_id):
                    relation_count += 1

        for species_name, disease_categories in health_data.items():
            sp_id = self._generate_entity_id("Species", species_name)

            for category_name, diseases in disease_categories.items():
                bp_id = self._generate_entity_id("BodyPart", category_name)
                if self.graph_db.create_entity("BodyPart", bp_id, {
                    "name": category_name,
                    "system": category_name,
                }):
                    entity_count += 1

                for disease_info in diseases:
                    disease_name = disease_info.get("name", "")
                    dis_id = self._generate_entity_id("Disease", disease_name)
                    if self.graph_db.create_entity("Disease", dis_id, {
                        "name": disease_name,
                        "description": disease_info.get("description", ""),
                        "severity": disease_info.get("severity", "medium"),
                    }):
                        entity_count += 1

                    if self.graph_db.create_relation("Disease", dis_id, "AFFECTS", "BodyPart", bp_id):
                        relation_count += 1

                    for symptom in disease_info.get("symptoms", []):
                        sym_id = self._generate_entity_id("Symptom", symptom)
                        if self.graph_db.create_entity("Symptom", sym_id, {"name": symptom}):
                            entity_count += 1
                        if self.graph_db.create_relation("Disease", dis_id, "HAS_SYMPTOM", "Symptom", sym_id):
                            relation_count += 1
                        if self.graph_db.create_relation("Symptom", sym_id, "BELONGS_TO", "BodyPart", bp_id):
                            relation_count += 1

                    for treatment in disease_info.get("treatments", []):
                        tr_id = self._generate_entity_id("Medication", treatment)
                        if self.graph_db.create_entity("Medication", tr_id, {"name": treatment}):
                            entity_count += 1
                        if self.graph_db.create_relation("Disease", dis_id, "TREATED_BY", "Medication", tr_id):
                            relation_count += 1

                    for prevention in disease_info.get("preventions", []):
                        prev_id = self._generate_entity_id("PreventionMeasure", prevention)
                        if self.graph_db.create_entity("PreventionMeasure", prev_id, {"name": prevention}):
                            entity_count += 1
                        if self.graph_db.create_relation("PreventionMeasure", prev_id, "PREVENTS", "Disease", dis_id):
                            relation_count += 1

        stats = self.graph_db.get_stats()
        logger.info(f"结构化知识导入完成: {entity_count}实体, {relation_count}关系")
        return {
            "entities_added": entity_count,
            "relations_added": relation_count,
            "stats": stats,
        }

    @staticmethod
    def _generate_entity_id(entity_type: str, entity_name: str) -> str:
        key = f"{entity_type}::{entity_name}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()[:12]


_graph_builder: Optional[GraphBuilder] = None


def get_graph_builder() -> GraphBuilder:
    global _graph_builder
    if _graph_builder is None:
        _graph_builder = GraphBuilder()
    return _graph_builder