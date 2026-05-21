"""
宠物知识科普模块 - 服务层单元测试

测试范围：
- 品种列表获取（cat/dog/无效物种）
- 品种详情获取（有效ID/无效ID/空ID）
- 健康知识列表（cat/dog/both/无效物种）
- 病症详情获取（有效ID/无效ID）
- 搜索功能（中文搜索/英文搜索/空搜索/特殊字符/无匹配）
- 数据完整性（字段完整性/数据类型/数据量验证）
- 边界条件测试
"""
import pytest
import time


class TestEncyclopediaServiceUnit:
    """百科全书服务层单元测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        from src.services.encyclopedia_service import EncyclopediaService
        self.service = EncyclopediaService

    # ============================================================
    # 品种列表测试
    # ============================================================

    def test_get_cat_breeds_returns_10(self):
        """猫品种列表应返回10个品种"""
        result = self.service.get_breeds("cat")
        assert len(result) == 10

    def test_get_dog_breeds_returns_10(self):
        """狗品种列表应返回10个品种"""
        result = self.service.get_breeds("dog")
        assert len(result) == 10

    def test_breed_list_has_required_fields(self):
        """品种列表元素应包含所有必要字段"""
        result = self.service.get_breeds("cat")
        required_fields = {"id", "name", "english_name", "species", "summary", "image_emoji", "popularity"}
        for breed in result:
            assert required_fields.issubset(breed.keys()), f"缺少字段: {required_fields - set(breed.keys())}"

    def test_breed_list_popularity_range(self):
        """品种popularity应在1-10范围内"""
        for species in ("cat", "dog"):
            result = self.service.get_breeds(species)
            for breed in result:
                assert 1 <= breed["popularity"] <= 10

    def test_breed_list_species_matches(self):
        """品种列表所有元素species应与查询一致"""
        result = self.service.get_breeds("cat")
        for breed in result:
            assert breed["species"] == "cat"

        result = self.service.get_breeds("dog")
        for breed in result:
            assert breed["species"] == "dog"

    def test_breed_list_sorted_by_popularity(self):
        """品种列表应按popularity降序排列"""
        result = self.service.get_breeds("dog")
        popularities = [b["popularity"] for b in result]
        assert popularities == sorted(popularities, reverse=True), "品种列表未按popularity降序排列"

    # ============================================================
    # 品种详情测试
    # ============================================================

    def test_get_breed_detail_valid_cat(self):
        """获取有效猫品种详情"""
        breed = self.service.get_breed_detail("cat_ragdoll")
        assert breed is not None
        assert breed["name"] == "布偶猫"
        assert breed["species"] == "cat"
        assert breed["english_name"] == "Ragdoll"

    def test_get_breed_detail_valid_dog(self):
        """获取有效狗品种详情"""
        breed = self.service.get_breed_detail("dog_golden_retriever")
        assert breed is not None
        assert breed["name"] == "金毛寻回犬"
        assert breed["species"] == "dog"

    def test_get_breed_detail_invalid_id(self):
        """无效品种ID应返回None"""
        breed = self.service.get_breed_detail("invalid_breed_id")
        assert breed is None

    def test_get_breed_detail_empty_id(self):
        """空品种ID应返回None"""
        breed = self.service.get_breed_detail("")
        assert breed is None

    def test_breed_detail_has_complete_fields(self):
        """品种详情应包含所有必要字段"""
        breed = self.service.get_breed_detail("cat_british_shorthair")
        assert breed is not None
        required = {"id", "name", "english_name", "species", "category", "description",
                     "summary", "features", "personality", "care_requirements",
                     "health_issues", "suitable_for", "image_emoji", "popularity"}
        assert required.issubset(breed.keys()), f"缺少: {required - set(breed.keys())}"

    def test_breed_detail_features_structure(self):
        """品种详情features子结构应完整"""
        breed = self.service.get_breed_detail("cat_ragdoll")
        assert breed is not None
        features = breed["features"]
        assert set(features.keys()) == {"origin", "size", "weight", "lifespan", "coat", "colors"}
        assert isinstance(features["colors"], list)

    def test_breed_detail_care_structure(self):
        """品种详情care_requirements子结构应完整"""
        breed = self.service.get_breed_detail("dog_labrador")
        assert breed is not None
        care = breed["care_requirements"]
        assert set(care.keys()) == {"exercise", "grooming", "diet", "training"}

    def test_breed_detail_personality_is_list(self):
        """品种详情personality应为列表"""
        for species_id in ("cat_ragdoll", "dog_labrador"):
            breed = self.service.get_breed_detail(species_id)
            assert isinstance(breed["personality"], list)
            assert len(breed["personality"]) > 0

    def test_breed_detail_health_issues_is_list(self):
        """品种详情health_issues应为列表"""
        for species_id in ("cat_persian", "dog_corgi"):
            breed = self.service.get_breed_detail(species_id)
            assert isinstance(breed["health_issues"], list)
            assert len(breed["health_issues"]) > 0

    # ============================================================
    # 健康知识列表测试
    # ============================================================

    def test_get_health_cat_conditions(self):
        """获取猫咪健康知识"""
        categories = self.service.get_health_conditions("cat")
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_get_health_dog_conditions(self):
        """获取狗狗健康知识"""
        categories = self.service.get_health_conditions("dog")
        assert isinstance(categories, list)
        assert len(categories) > 0

    def test_get_health_both_conditions(self):
        """获取综合（both）健康知识"""
        categories = self.service.get_health_conditions("both")
        assert isinstance(categories, list)
        all_count = sum(len(c["conditions"]) for c in categories)
        assert all_count >= 13  # at least all cat conditions

    def test_get_health_cat_13_conditions(self):
        """猫咪应有15个病症"""
        categories = self.service.get_health_conditions("cat")
        total = sum(len(c["conditions"]) for c in categories)
        assert total == 15

    def test_get_health_dog_14_conditions(self):
        """狗狗应有13个病症"""
        categories = self.service.get_health_conditions("dog")
        total = sum(len(c["conditions"]) for c in categories)
        assert total == 13

    def test_health_category_group_structure(self):
        """健康知识列表分组结构应完整"""
        categories = self.service.get_health_conditions("cat")
        for group in categories:
            assert "category" in group
            assert "category_label" in group
            assert "conditions" in group
            assert isinstance(group["conditions"], list)

    def test_health_condition_summary_fields(self):
        """健康知识摘要应包含必要字段"""
        categories = self.service.get_health_conditions("cat")
        required = {"id", "name", "species", "category", "severity", "image_emoji"}
        for group in categories:
            for condition in group["conditions"]:
                assert required.issubset(condition.keys()), f"缺少: {required - set(condition.keys())}"

    def test_health_severity_valid_values(self):
        """严重程度应为合法值"""
        valid = {"mild", "moderate", "severe", "emergency"}
        for species in ("cat", "dog"):
            categories = self.service.get_health_conditions(species)
            for group in categories:
                for condition in group["conditions"]:
                    assert condition["severity"] in valid

    def test_health_must_have_emergency_conditions(self):
        """必须包含emergency级别病症"""
        for species in ("cat", "dog"):
            categories = self.service.get_health_conditions(species)
            all_severities = []
            for group in categories:
                for c in group["conditions"]:
                    all_severities.append(c["severity"])
            assert "emergency" in all_severities, f"{species}缺少emergency级别"

    # ============================================================
    # 病症详情测试
    # ============================================================

    def test_get_health_detail_valid_cat(self):
        """获取有效猫咪病症详情"""
        condition = self.service.get_health_detail("cat_diarrhea")
        assert condition is not None
        assert condition["name"] == "软便/腹泻"
        assert condition["species"] == "cat"

    def test_get_health_detail_valid_dog(self):
        """获取有效狗狗病症详情"""
        condition = self.service.get_health_detail("dog_parvovirus")
        assert condition is not None
        assert condition["name"] == "犬细小病毒病"
        assert condition["severity"] == "emergency"

    def test_get_health_detail_invalid_id(self):
        """无效病症ID应返回None"""
        condition = self.service.get_health_detail("invalid_condition")
        assert condition is None

    def test_get_health_detail_empty_id(self):
        """空病症ID应返回None"""
        condition = self.service.get_health_detail("")
        assert condition is None

    def test_health_detail_has_complete_fields(self):
        """病症详情应包含所有必要字段"""
        condition = self.service.get_health_detail("cat_uti")
        assert condition is not None
        required = {"id", "name", "species", "category", "description", "symptoms",
                     "urgent_symptoms", "possible_causes", "severity", "treatment",
                     "home_care", "prevention", "image_emoji"}
        assert required.issubset(condition.keys()), f"缺少: {required - set(condition.keys())}"

    def test_health_detail_must_have_urgent_warning(self):
        """emergency级别病症必须有urgent_symptoms"""
        condition = self.service.get_health_detail("cat_fpv")
        assert condition is not None
        assert condition["severity"] == "emergency"
        assert len(condition["urgent_symptoms"]) > 0

    def test_health_detail_symptoms_is_list(self):
        """病症detail的symptoms应为非空列表"""
        for condition_id in ("cat_diarrhea", "dog_hip_dysplasia", "cat_uti"):
            condition = self.service.get_health_detail(condition_id)
            assert isinstance(condition["symptoms"], list)
            assert len(condition["symptoms"]) > 0

    # ============================================================
    # 搜索功能测试
    # ============================================================

    def test_search_chinese_breed_name(self):
        """中文品种名搜索"""
        result = self.service.search_knowledge("布偶猫")
        assert len(result["breeds"]) > 0
        assert result["breeds"][0]["name"] == "布偶猫"

    def test_search_english_breed_name(self):
        """英文品种名搜索（不区分大小写）"""
        result = self.service.search_knowledge("Ragdoll")
        assert len(result["breeds"]) > 0

    def test_search_disease_name(self):
        """病症名称搜索"""
        result = self.service.search_knowledge("腹泻")
        assert len(result["conditions"]) > 0

    def test_search_symptom_keyword(self):
        """症状关键词搜索"""
        result = self.service.search_knowledge("呕吐")
        assert len(result["conditions"]) > 0

    def test_search_max_results_capped(self):
        """搜索结果每种类型最多5条"""
        result = self.service.search_knowledge("c")
        assert len(result["breeds"]) <= 5
        assert len(result["conditions"]) <= 5

    def test_search_no_results(self):
        """无匹配搜索应返回空列表"""
        result = self.service.search_knowledge("xyzabc_nonexistent")
        assert result["breeds"] == []
        assert result["conditions"] == []

    def test_search_empty_string(self):
        """空字符串搜索（应无结果或返回部分）"""
        result = self.service.search_knowledge("")
        assert isinstance(result["breeds"], list)
        assert isinstance(result["conditions"], list)

    def test_search_special_characters(self):
        """特殊字符搜索应不崩溃"""
        result = self.service.search_knowledge("@#$%")
        assert isinstance(result, dict)
        assert "breeds" in result
        assert "conditions" in result

    def test_search_case_insensitive(self):
        """搜索不区分大小写"""
        r1 = self.service.search_knowledge("RAGDOLL")
        r2 = self.service.search_knowledge("ragdoll")
        assert len(r1["breeds"]) == len(r2["breeds"])

    def test_search_breeds_limit_5(self):
        """品种搜索结果限制5条"""
        result = self.service.search_knowledge("猫")
        assert len(result["breeds"]) <= 5

    def test_search_conditions_limit_5(self):
        """病症搜索结果限制5条"""
        result = self.service.search_knowledge("感染")
        assert len(result["conditions"]) <= 5

    # ============================================================
    # 数据完整性测试
    # ============================================================

    def test_all_breeds_have_unique_ids(self):
        """所有品种ID应唯一"""
        from src.services.encyclopedia_service import CAT_BREEDS, DOG_BREEDS
        all_ids = [b["id"] for b in CAT_BREEDS + DOG_BREEDS]
        assert len(all_ids) == len(set(all_ids)), "品种ID重复!"

    def test_all_conditions_have_unique_ids(self):
        """所有病症ID应唯一"""
        from src.services.encyclopedia_service import CAT_HEALTH_CONDITIONS, DOG_HEALTH_CONDITIONS
        all_ids = [c["id"] for c in CAT_HEALTH_CONDITIONS + DOG_HEALTH_CONDITIONS]
        assert len(all_ids) == len(set(all_ids)), "病症ID重复!"

    def test_every_breed_retrievable(self):
        """每个品种都能通过get_breed_detail检索到"""
        from src.services.encyclopedia_service import CAT_BREEDS, DOG_BREEDS
        for breed in CAT_BREEDS + DOG_BREEDS:
            result = self.service.get_breed_detail(breed["id"])
            assert result is not None, f"无法检索品种: {breed['id']}"
            assert result["name"] == breed["name"]

    def test_every_condition_retrievable(self):
        """每个病症都能通过get_health_detail检索到"""
        from src.services.encyclopedia_service import CAT_HEALTH_CONDITIONS, DOG_HEALTH_CONDITIONS
        for condition in CAT_HEALTH_CONDITIONS + DOG_HEALTH_CONDITIONS:
            result = self.service.get_health_detail(condition["id"])
            assert result is not None, f"无法检索病症: {condition['id']}"
            assert result["name"] == condition["name"]

    def test_cat_breeds_have_correct_species(self):
        """猫品种的species字段必须是cat"""
        from src.services.encyclopedia_service import CAT_BREEDS
        for breed in CAT_BREEDS:
            assert breed["species"] == "cat"

    def test_dog_breeds_have_correct_species(self):
        """狗品种的species字段必须是dog"""
        from src.services.encyclopedia_service import DOG_BREEDS
        for breed in DOG_BREEDS:
            assert breed["species"] == "dog"

    def test_cat_conditions_have_valid_species(self):
        """猫病症的species字段必须是cat"""
        from src.services.encyclopedia_service import CAT_HEALTH_CONDITIONS
        for c in CAT_HEALTH_CONDITIONS:
            assert c["species"] == "cat"

    def test_dog_conditions_have_valid_species(self):
        """狗病症的species字段必须是dog"""
        from src.services.encyclopedia_service import DOG_HEALTH_CONDITIONS
        for c in DOG_HEALTH_CONDITIONS:
            assert c["species"] == "dog"

    def test_all_popularity_in_range(self):
        """所有品种popularity在1-10范围内"""
        from src.services.encyclopedia_service import CAT_BREEDS, DOG_BREEDS
        for breed in CAT_BREEDS + DOG_BREEDS:
            assert 1 <= breed["popularity"] <= 10, f"{breed['name']} popularity={breed['popularity']}"

    # ============================================================
    # 性能测试
    # ============================================================

    def test_service_response_time_breeds(self):
        """品种列表查询应在0.01秒内完成（纯内存查询）"""
        start = time.perf_counter()
        self.service.get_breeds("cat")
        self.service.get_breeds("dog")
        elapsed = time.perf_counter() - start
        assert elapsed < 0.01, f"品种查询耗时过长: {elapsed:.4f}s"

    def test_service_response_time_search(self):
        """搜索应在0.01秒内完成"""
        start = time.perf_counter()
        self.service.search_knowledge("腹泻")
        self.service.search_knowledge("金毛")
        elapsed = time.perf_counter() - start
        assert elapsed < 0.01, f"搜索耗时过长: {elapsed:.4f}s"

    def test_bulk_detail_retrieval(self):
        """批量查询20个品种详情应在0.02秒内"""
        from src.services.encyclopedia_service import CAT_BREEDS, DOG_BREEDS
        all_breeds = CAT_BREEDS + DOG_BREEDS
        start = time.perf_counter()
        for breed in all_breeds:
            self.service.get_breed_detail(breed["id"])
        elapsed = time.perf_counter() - start
        assert elapsed < 0.02, f"批量品种查询耗时过长: {elapsed:.4f}s"


class TestEncyclopediaBoundaryConditions:
    """边界条件与异常测试"""

    @pytest.fixture(autouse=True)
    def setup(self):
        from src.services.encyclopedia_service import EncyclopediaService
        self.service = EncyclopediaService

    def test_species_case_sensitive(self):
        """品种查询species参数区分大小写，大写/大小写混合应返回空"""
        result_cat = self.service.get_breeds("cat")
        assert len(result_cat) == 10
        result_mixed = self.service.get_breeds("CAT")
        assert len(result_mixed) == 0

    def test_health_species_case_sensitive(self):
        """健康知识species参数区分大小写"""
        result_cat = self.service.get_health_conditions("cat")
        assert len(result_cat) > 0
        result_mixed = self.service.get_health_conditions("CAT")
        assert len(result_mixed) == 0

    def test_nonexistent_species_breeds(self):
        """不存在的物种返回空列表"""
        result = self.service.get_breeds("bird")
        assert result == []

    def test_nonexistent_species_health(self):
        """不存在的物种返回空列表"""
        result = self.service.get_health_conditions("bird")
        assert result == []

    def test_special_species_values(self):
        """特殊species值不崩溃"""
        for species in ("", " ", "123", "cat;drop table", "🐱"):
            try:
                result = self.service.get_breeds(species)
                assert isinstance(result, list)
            except Exception as e:
                pytest.fail(f"species='{species}' 导致异常: {e}")

    def test_unicode_breed_id(self):
        """Unicode品种ID不崩溃"""
        result = self.service.get_breed_detail("🐱🐶")
        assert result is None

    def test_very_long_search_query(self):
        """超长搜索词不应导致崩溃"""
        long_query = "a" * 10000
        result = self.service.search_knowledge(long_query)
        assert isinstance(result, dict)

    def test_search_with_whitespace_only(self):
        """仅空格搜索"""
        result = self.service.search_knowledge("   ")
        assert isinstance(result, dict)

    def test_get_health_both_has_correct_groups(self):
        """both模式应包含猫和狗所有的病症分组"""
        categories = self.service.get_health_conditions("both")
        category_labels = [c["category_label"] for c in categories]
        assert "消化系统" in category_labels
        assert "传染病" in category_labels

    def test_both_has_all_conditions(self):
        """both模式应返回猫和狗所有病症（15+13=28）"""
        from src.services.encyclopedia_service import CAT_HEALTH_CONDITIONS, DOG_HEALTH_CONDITIONS
        categories = self.service.get_health_conditions("both")
        total = sum(len(c["conditions"]) for c in categories)
        assert total == len(CAT_HEALTH_CONDITIONS) + len(DOG_HEALTH_CONDITIONS)


class TestPydanticSchemaValidation:
    """Pydantic Schema 验证测试"""

    def test_breed_summary_schema(self):
        """BreedSummary schema验证"""
        from src.api.schemas.encyclopedia import BreedSummary
        data = {"id": "test", "name": "测试", "species": "cat"}
        model = BreedSummary(**data)
        assert model.id == "test"
        assert model.popularity == 5  # default

    def test_breed_summary_popularity_bounds(self):
        """popularity边界值验证"""
        from src.api.schemas.encyclopedia import BreedSummary
        with pytest.raises(Exception):
            BreedSummary(id="t", name="t", species="cat", popularity=0)
        with pytest.raises(Exception):
            BreedSummary(id="t", name="t", species="cat", popularity=11)
        # 边界值通过
        assert BreedSummary(id="t", name="t", species="cat", popularity=1)
        assert BreedSummary(id="t", name="t", species="cat", popularity=10)

    def test_breed_detail_schema(self):
        """BreedDetail schema验证"""
        from src.api.schemas.encyclopedia import BreedDetail
        data = {"id": "test", "name": "测试", "species": "cat"}
        model = BreedDetail(**data)
        assert model.features.origin == ""

    def test_health_condition_severity_default(self):
        """HealthCondition severity默认值"""
        from src.api.schemas.encyclopedia import HealthCondition
        data = {"id": "test", "name": "测试", "species": "cat", "category": "test"}
        model = HealthCondition(**data)
        assert model.severity == "mild"

    def test_breed_list_response_schema(self):
        """BreedListResponse schema验证"""
        from src.api.schemas.encyclopedia import BreedListResponse, BreedSummary
        response = BreedListResponse(
            species="cat",
            breeds=[BreedSummary(id="t", name="t", species="cat")]
        )
        assert response.species == "cat"
        assert len(response.breeds) == 1

    def test_health_list_response_schema(self):
        """HealthListResponse schema验证"""
        from src.api.schemas.encyclopedia import HealthListResponse, HealthCategoryGroup, HealthConditionSummary
        response = HealthListResponse(
            species="cat",
            categories=[HealthCategoryGroup(
                category="test",
                category_label="测试",
                conditions=[HealthConditionSummary(id="t", name="t", species="cat", category="test", severity="mild")]
            )]
        )
        assert response.species == "cat"

    def test_search_response_default_empty(self):
        """SearchKnowledgeResponse默认空列表"""
        from src.api.schemas.encyclopedia import SearchKnowledgeResponse
        response = SearchKnowledgeResponse()
        assert response.breeds == []
        assert response.conditions == []