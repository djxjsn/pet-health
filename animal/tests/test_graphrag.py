"""Phase 3 知识图谱融合 - 集成测试"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestGraphDatabase:
    """图数据库连接器测试"""

    def test_init_networkx_fallback(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        assert db.is_available
        assert db.backend == "networkx"

    def test_create_entity(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        result = db.create_entity("Disease", "test_dis_001", {
            "name": "犬瘟热",
            "severity": "high",
            "description": "犬瘟热是一种高度传染性的病毒性疾病",
        })
        assert result is True

        entity = db.get_entity("Disease", "test_dis_001")
        assert entity is not None
        assert entity["name"] == "犬瘟热"
        assert entity["severity"] == "high"

    def test_create_relation(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        db.create_entity("Disease", "dis_01", {"name": "犬瘟热"})
        db.create_entity("Symptom", "sym_01", {"name": "发热"})

        result = db.create_relation(
            "Disease", "dis_01",
            "HAS_SYMPTOM",
            "Symptom", "sym_01"
        )
        assert result is True

    def test_get_neighbors(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        db.create_entity("Disease", "dis_02", {"name": "猫瘟"})
        db.create_entity("Symptom", "sym_02", {"name": "呕吐"})
        db.create_entity("Symptom", "sym_03", {"name": "发热"})
        db.create_relation("Disease", "dis_02", "HAS_SYMPTOM", "Symptom", "sym_02")
        db.create_relation("Disease", "dis_02", "HAS_SYMPTOM", "Symptom", "sym_03")

        neighbors = db.get_neighbors("Disease", "dis_02", max_depth=1)
        assert len(neighbors) >= 2

        symptom_names = [n.get("name", "") for n in neighbors]
        assert "呕吐" in symptom_names or "发热" in symptom_names

    def test_get_paths(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        db.create_entity("Breed", "breed_01", {"name": "金毛寻回犬"})
        db.create_entity("Species", "spec_01", {"name": "犬"})
        db.create_entity("Disease", "dis_03", {"name": "髋关节发育不良"})
        db.create_relation("Breed", "breed_01", "BELONGS_TO", "Species", "spec_01")
        db.create_relation("Disease", "dis_03", "AFFECTS", "Breed", "breed_01")

        paths = db.get_paths("Disease", "dis_03", "Species", "spec_01", max_depth=3, max_paths=5)
        assert len(paths) > 0

    def test_search_entities(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        db.create_entity("Disease", "dis_search_01", {"name": "犬冠状病毒感染"})
        db.create_entity("Disease", "dis_search_02", {"name": "犬瘟热"})

        results = db.search_entities(entity_type="Disease", name_pattern="犬", limit=10)
        assert len(results) >= 2

    def test_clear_all(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        db.create_entity("Disease", "dis_clear", {"name": "测试疾病"})
        assert db.get_entity("Disease", "dis_clear") is not None

        db.clear_all()
        assert db.get_entity("Disease", "dis_clear") is None

    def test_get_stats(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        db.clear_all()
        db.create_entity("Disease", "d1", {"name": "病1"})
        db.create_entity("Disease", "d2", {"name": "病2"})
        db.create_entity("Symptom", "s1", {"name": "症状1"})
        db.create_relation("Disease", "d1", "HAS_SYMPTOM", "Symptom", "s1")

        stats = db.get_stats()
        assert stats["backend"] == "networkx"
        assert stats["node_count"] == 3
        assert stats["relation_count"] == 1
        assert "Disease" in stats["label_distribution"]


class TestEntityExtractor:
    """实体关系抽取测试"""

    def test_extract_disease_and_symptoms(self):
        from src.core.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        text = "犬瘟热是一种高度传染性的病毒性疾病，主要症状包括发热、咳嗽、呕吐和腹泻。幼犬发病率最高。"
        result = extractor.extract_from_text(text, known_species="犬")

        assert result["strategy"] in ("llm", "rule")
        entities = result.get("entities", [])
        entity_names = [e["name"] for e in entities]
        assert "犬瘟热" in entity_names
        assert any(s in entity_names for s in ["发热", "咳嗽", "呕吐", "腹泻"])

    def test_extract_species_and_breed(self):
        from src.core.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        text = "金毛寻回犬是大型犬品种，常见健康问题包括髋关节问题和皮肤病。"
        result = extractor.extract_from_text(text, known_species="犬", known_breed="金毛寻回犬")

        entities = result.get("entities", [])
        types = [e["type"] for e in entities]
        assert "Species" in types or "Breed" in types

    def test_extract_body_parts(self):
        from src.core.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        text = "猫咪出现皮肤红肿和脱毛，可能是皮肤病或过敏引起的。"
        result = extractor.extract_from_text(text, known_species="猫")

        entities = result.get("entities", [])
        names = [e["name"] for e in entities]
        assert "皮肤" in names or any("皮肤" in n for n in names)

    def test_batch_extraction_dedup(self):
        from src.core.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        texts = [
            "犬瘟热有发热和咳嗽症状。",
            "犬瘟热还会导致呕吐和腹泻。",
        ]
        result = extractor.extract_from_batch(texts, known_species="犬")

        entities = result.get("entities", [])
        disease_count = sum(1 for e in entities if e["type"] == "Disease" and e["name"] == "犬瘟热")
        assert disease_count == 1


class TestGraphBuilder:
    """图谱构建器测试"""

    def test_build_from_texts(self):
        from src.core.graph_builder import GraphBuilder
        builder = GraphBuilder()
        builder.graph_db.clear_all()

        texts = [
            "犬瘟热是犬类严重的病毒性传染病，症状包括发热、咳嗽、呕吐、腹泻和神经症状。治疗需要在兽医指导下使用抗病毒药物和抗生素。",
            "犬细小病毒主要影响幼犬，导致严重呕吐、血便和脱水。通过疫苗接种可以有效预防。",
        ]
        result = builder.build_from_texts(texts, species="犬", rebuild=True)

        assert result["entities_added"] > 0
        assert result["relations_added"] > 0
        assert result["stats"]["node_count"] > 0

    def test_add_structured_knowledge(self):
        from src.core.graph_builder import GraphBuilder
        builder = GraphBuilder()
        builder.graph_db.clear_all()

        breeds_data = {
            "犬": [
                {"name": "金毛寻回犬", "temperament": "温顺友善", "size": "大型", "lifespan": "10-12年"},
                {"name": "柯基犬", "temperament": "活泼勇敢", "size": "小型", "lifespan": "12-15年"},
            ],
        }
        health_data = {
            "犬": {
                "消化系统": [
                    {"name": "犬细小病毒肠炎", "description": "高度传染性", "severity": "critical",
                     "symptoms": ["呕吐", "腹泻", "便血"], "treatments": ["补液疗法", "抗生素"],
                     "preventions": ["疫苗接种"]},
                ],
            },
        }

        result = builder.add_structured_knowledge(breeds_data, health_data)

        assert result["entities_added"] > 0
        assert result["relations_added"] > 0

        dog = builder.graph_db.search_entities(entity_type="Species", name_pattern="犬", limit=5)
        assert len(dog) >= 1

        breeds = builder.graph_db.search_entities(entity_type="Breed", limit=10)
        assert len(breeds) >= 2


class TestCommunityDetector:
    """社区检测测试"""

    @pytest.fixture
    def populated_graph(self):
        from src.core.graph_db import GraphDatabase
        db = GraphDatabase()
        db.clear_all()

        db.create_entity("Species", "sp_dog", {"name": "犬"})
        db.create_entity("Species", "sp_cat", {"name": "猫"})

        breeds = [
            ("br_01", "金毛寻回犬", "sp_dog"),
            ("br_02", "柯基犬", "sp_dog"),
            ("br_03", "布偶猫", "sp_cat"),
        ]
        for bid, bname, sid in breeds:
            db.create_entity("Breed", bid, {"name": bname})
            db.create_relation("Breed", bid, "BELONGS_TO", "Species", sid)

        diseases = [
            ("dis_01", "犬瘟热", ["发热", "咳嗽", "呕吐"]),
            ("dis_02", "细小病毒", ["呕吐", "腹泻", "脱水"]),
            ("dis_03", "猫鼻支", ["打喷嚏", "流鼻涕", "眼睛发炎"]),
        ]
        for did, dname, symptoms in diseases:
            db.create_entity("Disease", did, {"name": dname})
            for i, sym in enumerate(symptoms):
                sid = f"sym_{did}_{i}"
                db.create_entity("Symptom", sid, {"name": sym})
                db.create_relation("Disease", did, "HAS_SYMPTOM", "Symptom", sid)

        return db

    def test_detect_communities_greedy(self, populated_graph):
        from src.core.community_detector import CommunityDetector
        detector = CommunityDetector()
        detector.graph_db = populated_graph

        communities = detector.detect_communities(
            algorithm="greedy_modularity",
            min_community_size=2
        )
        assert len(communities) > 0

        for cid, cdata in communities.items():
            assert cdata["size"] >= 2
            assert len(cdata["entities"]) >= 2

    def test_build_hierarchy(self, populated_graph):
        from src.core.community_detector import CommunityDetector
        detector = CommunityDetector()
        detector.graph_db = populated_graph
        detector.detect_communities(min_community_size=2)

        hierarchy = detector.build_hierarchy(levels=2)
        assert len(detector.communities) > 0

        has_level = any("level" in c for c in detector.communities.values())
        assert has_level

    def test_generate_summaries(self, populated_graph):
        from src.core.community_detector import CommunityDetector
        detector = CommunityDetector()
        detector.graph_db = populated_graph
        detector.detect_communities(min_community_size=2)
        detector.build_hierarchy(levels=2)

        summaries = detector.generate_community_summaries()
        assert len(summaries) > 0

        for cid, summary in summaries.items():
            assert isinstance(summary, str)
            assert len(summary) > 0

    def test_community_for_entity(self, populated_graph):
        from src.core.community_detector import CommunityDetector
        detector = CommunityDetector()
        detector.graph_db = populated_graph
        detector.detect_communities(min_community_size=2)

        cid = detector.get_community_for_entity("Disease", "dis_01")
        if cid is not None:
            community = detector.get_community(cid)
            assert community is not None
            assert community["size"] > 0


class TestGraphRetriever:
    """GraphRAG检索器测试"""

    @pytest.fixture
    def populated_retriever(self):
        from src.core.graph_db import get_graph_db
        from src.core.graph_retriever import GraphRetriever
        db = get_graph_db()
        db.clear_all()

        db.create_entity("Species", "sp_dog", {"name": "犬"})
        db.create_entity("Breed", "br_golden", {"name": "金毛寻回犬"})
        db.create_relation("Breed", "br_golden", "BELONGS_TO", "Species", "sp_dog")

        db.create_entity("Disease", "dis_cdv", {
            "name": "犬瘟热",
            "description": "犬瘟热是高度传染性的病毒性疾病，致死率高",
            "severity": "critical",
        })
        db.create_entity("Symptom", "sym_fever", {"name": "发热"})
        db.create_entity("Symptom", "sym_cough", {"name": "咳嗽"})
        db.create_entity("BodyPart", "bp_resp", {"name": "呼吸系统", "system": "respiratory"})

        db.create_relation("Disease", "dis_cdv", "HAS_SYMPTOM", "Symptom", "sym_fever")
        db.create_relation("Disease", "dis_cdv", "HAS_SYMPTOM", "Symptom", "sym_cough")
        db.create_relation("Disease", "dis_cdv", "AFFECTS", "BodyPart", "bp_resp")

        retriever = GraphRetriever()
        retriever.graph_db = db
        return retriever

    def test_search_with_entities(self, populated_retriever):
        retriever = populated_retriever

        entities = [
            {"type": "Disease", "name": "犬瘟热", "aliases": ["狗瘟"], "properties": {}},
        ]
        result = retriever.search("金毛犬瘟热症状", entities=entities, max_hops=2)

        assert len(result["entities"]) > 0
        assert result["total_path_count"] > 0
        assert len(result["reasoning_chains"]) > 0

    def test_search_text_only(self, populated_retriever):
        retriever = populated_retriever
        result = retriever.search("金毛狗咳嗽发热是什么病", max_hops=2)

        assert isinstance(result["entities"], list)
        assert isinstance(result["paths"], list)

    def test_format_for_llm(self, populated_retriever):
        retriever = populated_retriever
        entities = [
            {"type": "Disease", "name": "犬瘟热", "aliases": ["狗瘟"], "properties": {}},
        ]
        result = retriever.search("犬瘟热", entities=entities, max_hops=2)
        formatted = retriever.format_for_llm(result)

        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert "犬瘟热" in formatted or "相关实体" in formatted


class TestFusionRetriever:
    """融合检索器测试"""

    def test_search_fusion(self):
        from src.core.fusion_retriever import FusionRetriever
        fr = FusionRetriever()

        if not fr.is_available:
            pytest.skip("向量检索不可用，跳过融合检索测试")

        result = fr.search(
            "狗拉肚子怎么办",
            top_k=5,
            enable_quality_eval=False,
            enable_graph=True,
        )
        assert "results" in result
        assert "fusion" in result
        assert "rewrite" in result

        fusion = result["fusion"]
        assert "fused_count" in fusion

    def test_format_context(self):
        from src.core.fusion_retriever import FusionRetriever
        fr = FusionRetriever()

        if not fr.is_available:
            pytest.skip("向量检索不可用")

        result = fr.search("狗拉肚子", top_k=3, enable_quality_eval=False, enable_graph=True)
        context = fr.format_context_from_fusion(result)

        assert isinstance(context, str)


class TestGraphRAGPipeline:
    """GraphRAG全流程测试"""

    def test_end_to_end_pipeline(self):
        """端到端测试：文本→抽取→图谱→检测→检索"""
        from src.core.graph_db import get_graph_db
        from src.core.entity_extractor import get_entity_extractor
        from src.core.graph_builder import get_graph_builder
        from src.core.community_detector import get_community_detector
        from src.core.graph_retriever import get_graph_retriever

        gdb = get_graph_db()
        gdb.clear_all()

        texts = [
            "犬瘟热是犬类最严重的传染病之一，主要症状包括：发热（体温可达40℃以上）、精神萎靡、食欲不振、",
            "眼鼻分泌物增多（初期浆液性、后期脓性）、咳嗽、呼吸困难、呕吐、腹泻（有时带血）。",
            "部分患犬会出现神经症状如抽搐、共济失调。治疗包括抗病毒、抗生素防继发感染、支持疗法。",
            "预防以疫苗接种为核心，幼犬需完成3次基础免疫。金毛、拉布拉多等大型犬需特别关注髋关节健康。",
        ]
        builder = get_graph_builder()
        build_result = builder.build_from_texts(texts, species="犬", rebuild=True)
        assert build_result["entities_added"] > 0

        detector = get_community_detector()
        communities = detector.detect_communities(min_community_size=2)
        if communities:
            detector.build_hierarchy(levels=2)
            detector.generate_community_summaries()
            assert len(detector.communities) > 0

        retriever = get_graph_retriever()
        result = retriever.search("金毛犬瘟热有哪些症状", max_hops=3)
        assert len(result["entities"]) > 0

    def test_multi_hop_reasoning(self):
        """多跳推理测试"""
        from src.core.graph_db import GraphDatabase
        from src.core.graph_retriever import GraphRetriever

        db = GraphDatabase()
        db.clear_all()

        db.create_entity("Species", "sp_dog", {"name": "犬"})
        db.create_entity("Breed", "br_golden", {"name": "金毛寻回犬"})
        db.create_entity("Disease", "dis_hd", {"name": "髋关节发育不良", "description": "大型犬常见遗传性疾病"})
        db.create_entity("Symptom", "sym_limp", {"name": "跛行"})
        db.create_entity("Symptom", "sym_pain", {"name": "关节疼痛"})
        db.create_entity("Medication", "med_nsaid", {"name": "非甾体抗炎药"})
        db.create_entity("BodyPart", "bp_joint", {"name": "关节"})

        db.create_relation("Breed", "br_golden", "BELONGS_TO", "Species", "sp_dog")
        db.create_relation("Disease", "dis_hd", "AFFECTS", "Breed", "br_golden")
        db.create_relation("Disease", "dis_hd", "HAS_SYMPTOM", "Symptom", "sym_limp")
        db.create_relation("Disease", "dis_hd", "HAS_SYMPTOM", "Symptom", "sym_pain")
        db.create_relation("Disease", "dis_hd", "TREATED_BY", "Medication", "med_nsaid")
        db.create_relation("Disease", "dis_hd", "AFFECTS", "BodyPart", "bp_joint")

        retriever = GraphRetriever()
        retriever.graph_db = db

        entities = [
            {"type": "Breed", "name": "金毛寻回犬", "aliases": ["金毛"], "properties": {}},
        ]
        result = retriever.search("金毛走路瘸是什么问题", entities=entities, max_hops=3)

        disease_entities = [
            e for e in result["subgraph"]["entities"]
            if e.get("type") == "Disease"
        ]
        assert len(disease_entities) > 0

        has_hd = any("髋关节" in e["name"] for e in disease_entities)
        assert has_hd, f"应能通过多跳推理找到髋关节发育不良，实际疾病实体: {[e['name'] for e in disease_entities]}"