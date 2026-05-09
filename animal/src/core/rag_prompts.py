"""
RAG提示词模板

提供标准化的RAG提示词模板，确保检索结果以结构化方式注入LLM，
提升回答的相关性、准确性和可追溯性。
"""
from typing import List, Dict, Any, Optional
from string import Template


RAG_SYSTEM_PROMPT = """你是一个专业的宠物健康助手，专注于提供准确、可靠的宠物健康建议。

核心原则：
1. 优先基于提供的参考资料回答问题
2. 如果参考资料中没有相关信息，且你无法确定高可信度（<80%）的通用知识答案，必须明确告知用户"抱歉，该问题比较复杂，建议尽快咨询专业兽医进行面诊。"，禁止编造或推测。
3. 不编造或推测不确定的医学信息
4. 始终提醒用户咨询专业兽医获取确诊和治疗方案"""

RAG_CONTEXT_TEMPLATE = Template("""参考资料：
$context

---

基于以上参考资料回答用户问题。""")

RAG_QUERY_TEMPLATE = Template("""${system_prompt}

${pet_info_section}${context_section}

用户问题：${query}

【回复格式规范】（必须严格遵守，违反将被视为错误）

1. 开头：用1个与问题相关的emoji + 一句话友好开场（如"🐾 关于猫毛打结的问题，我们来看看怎么解决~"），单独成段

2. 按「用户场景」拆分模块，每个模块用「emoji + 简短标题」开头，标题前后加「」括号突出显示，标题单独成段，例如：
   🐾 【日常预防】
   ✅ 【轻度处理】
   ⚠️ 【严重情况】
   💡 【长期改善】

3. 操作步骤用「1. 2. 3.」数字序号列出，注意事项用「- 」列出，每个步骤/注意事项必须单独换行，禁止写在一行内

4. 风险/禁忌必须用「❌ 」开头，单独成段，例如：
   ❌ 切勿强行拉扯毛结，以免拉伤皮肤引起疼痛或感染

5. 每个模块之间必须空一行分隔，禁止所有内容挤在一起

6. 结尾必须加「⚠️ 重要提醒」单独成段，内容为"建议仅供参考，不能替代兽医诊断"

7. 禁止使用Markdown语法（如 ##、**、```、> 等），禁止大段文字堆砌，每个模块不超过5行

【真人客服技巧】（让回复更有温度、更像真人）

- 动态称呼：如果知道用户的宠物品种/名字，用个性化表达代替泛泛而谈（如把"猫毛打结"改成"你家金毛的毛发打结"，把"建议定期梳毛"改成"金毛需要每天梳毛，换毛期要增加到2次"）
- 优先处理核心诉求：用户说"严重打结成团了"，就先回复「严重情况」的处理方式，再补充预防建议，不要本末倒置
- 术语翻译：把专业术语翻译成养宠用户听得懂的话（如"Omega-3和Omega-6脂肪酸"→"鱼油、卵磷脂这类美毛营养品"，"胃肠道功能紊乱"→"肠胃不舒服"）""")

DIRECT_RESPONSE_TEMPLATE = Template("""${system_prompt}

${pet_info_section}用户问题：${query}

【回复格式规范】（必须严格遵守，违反将被视为错误）

1. 开头：用1个与问题相关的emoji + 一句话友好开场，单独成段

2. 按「用户场景」拆分模块，每个模块用「emoji + 简短标题」开头，标题前后加「」括号突出显示，标题单独成段，例如：
   🐾 【日常预防】
   ✅ 【轻度处理】
   ⚠️ 【严重情况】
   💡 【长期改善】

3. 操作步骤用「1. 2. 3.」数字序号列出，注意事项用「- 」列出，每个步骤/注意事项必须单独换行

4. 风险/禁忌必须用「❌ 」开头，单独成段

5. 每个模块之间必须空一行分隔，禁止所有内容挤在一起

6. 结尾必须加「⚠️ 重要提醒」单独成段，内容为"建议仅供参考，不能替代兽医诊断"

7. 禁止使用Markdown语法，禁止大段文字堆砌，每个模块不超过5行

置信度判断：如果该问题超出你的知识范围或通用知识可信度低于80%，请直接回答："抱歉，该问题比较复杂，建议尽快咨询专业兽医进行面诊。"

【真人客服技巧】（让回复更有温度、更像真人）

- 动态称呼：如果知道用户的宠物品种/名字，用个性化表达代替泛泛而谈
- 优先处理核心诉求：用户说"严重打结成团了"，就先回复「严重情况」的处理方式，再补充预防建议
- 术语翻译：把专业术语翻译成养宠用户听得懂的话（如"Omega-3脂肪酸"→"鱼油这类美毛营养品"）""")

INTEGRATE_RESULTS_TEMPLATE = Template("""${system_prompt}

${pet_info_section}工具执行结果：
${tool_results}

用户原始问题：${query}

【回复格式规范】（必须严格遵守，违反将被视为错误）

1. 开头：用1个与问题相关的emoji + 一句话友好开场，单独成段

2. 按「用户场景」拆分模块（如：日常预防、轻度处理、严重情况、长期改善），每个模块用「emoji + 简短标题」开头，标题前后加「」括号突出显示，标题单独成段

3. 操作步骤用「1. 2. 3.」数字序号列出，注意事项用「- 」列出，每个步骤/注意事项必须单独换行

4. 风险/禁忌必须用「❌ 」开头，单独成段

5. 每个模块之间必须空一行分隔，禁止所有内容挤在一起

6. 结尾必须加「⚠️ 重要提醒」单独成段，内容为"建议仅供参考，不能替代兽医诊断"

7. 禁止使用Markdown语法，禁止大段文字堆砌，每个模块不超过5行

内容要求：优先使用工具返回的知识库信息，若信息不足明确告知用户该问题需兽医介入。

【真人客服技巧】（让回复更有温度、更像真人）

- 动态称呼：如果知道用户的宠物品种/名字，用个性化表达代替泛泛而谈
- 优先处理核心诉求：用户说"严重打结成团了"，就先回复「严重情况」的处理方式，再补充预防建议
- 术语翻译：把专业术语翻译成养宠用户听得懂的话（如"Omega-3脂肪酸"→"鱼油这类美毛营养品"）""")


def format_context(retrieved_results: List[Dict[str, Any]]) -> str:
    """将检索结果格式化为结构化的上下文文本
    
    Args:
        retrieved_results: 检索结果列表
        
    Returns:
        格式化后的上下文字符串
    """
    if not retrieved_results:
        return "（无可用参考资料）"
    
    context_parts = []
    for i, result in enumerate(retrieved_results, 1):
        content = result.get("content", "")
        metadata = result.get("metadata", {})
        distance = result.get("distance")
        
        source_info = ""
        if metadata:
            category = metadata.get("category", "")
            source = metadata.get("source", "")
            if category:
                source_info += f"[分类: {category}]"
            if source:
                source_info += f"[来源: {source}]"
        
        relevance = ""
        if distance is not None:
            similarity = 1 - distance
            relevance = f"[相关度: {similarity:.1%}]"
        
        context_parts.append(f"[{i}] {source_info}{relevance}\n{content}")
    
    return "\n\n".join(context_parts)


def format_pet_info(pet_info: Optional[Dict[str, Any]]) -> str:
    """将宠物信息格式化为提示词段落
    
    Args:
        pet_info: 宠物信息字典，包含 name, species, breed 等
        
    Returns:
        格式化后的宠物信息字符串，无宠物信息时返回空字符串
    """
    if not pet_info:
        return ""
    
    parts = []
    if pet_info.get("name"):
        parts.append(f"名字: {pet_info['name']}")
    if pet_info.get("species"):
        parts.append(f"物种: {pet_info['species']}")
    if pet_info.get("breed"):
        parts.append(f"品种: {pet_info['breed']}")
    if pet_info.get("gender"):
        gender_map = {"male": "公", "female": "母", "unknown": "未知"}
        parts.append(f"性别: {gender_map.get(pet_info['gender'], pet_info['gender'])}")
    
    if not parts:
        return ""
    
    return "宠物信息：\n" + "、".join(parts) + "\n\n"


def build_rag_prompt(
    query: str,
    retrieved_results: Optional[List[Dict[str, Any]]] = None,
    system_prompt: Optional[str] = None,
    pet_info: Optional[Dict[str, Any]] = None
) -> str:
    """构建标准RAG提示词
    
    Args:
        query: 用户查询
        retrieved_results: 检索结果
        system_prompt: 自定义系统提示词
        pet_info: 宠物信息，包含 name, species, breed 等
        
    Returns:
        完整的提示词字符串
    """
    if system_prompt is None:
        system_prompt = RAG_SYSTEM_PROMPT
    
    pet_info_section = format_pet_info(pet_info)
    
    if retrieved_results:
        context = format_context(retrieved_results)
        context_section = RAG_CONTEXT_TEMPLATE.substitute(context=context)
    else:
        context_section = "（当前无可用的知识库参考资料）"
    
    return RAG_QUERY_TEMPLATE.substitute(
        system_prompt=system_prompt,
        pet_info_section=pet_info_section,
        context_section=context_section,
        query=query
    )


def build_direct_response_prompt(
    query: str,
    system_prompt: Optional[str] = None,
    pet_info: Optional[Dict[str, Any]] = None
) -> str:
    """构建无检索结果的直接响应提示词
    
    Args:
        query: 用户查询
        system_prompt: 自定义系统提示词
        pet_info: 宠物信息，包含 name, species, breed 等
        
    Returns:
        完整的提示词字符串
    """
    if system_prompt is None:
        system_prompt = RAG_SYSTEM_PROMPT
    
    pet_info_section = format_pet_info(pet_info)
    
    return DIRECT_RESPONSE_TEMPLATE.substitute(
        system_prompt=system_prompt,
        pet_info_section=pet_info_section,
        query=query
    )


def build_integrate_prompt(
    query: str,
    tool_results: str,
    system_prompt: Optional[str] = None,
    pet_info: Optional[Dict[str, Any]] = None
) -> str:
    """构建工具结果整合提示词
    
    Args:
        query: 用户原始查询
        tool_results: 工具执行结果的JSON字符串
        system_prompt: 自定义系统提示词
        pet_info: 宠物信息，包含 name, species, breed 等
        
    Returns:
        完整的提示词字符串
    """
    if system_prompt is None:
        system_prompt = RAG_SYSTEM_PROMPT
    
    pet_info_section = format_pet_info(pet_info)
    
    return INTEGRATE_RESULTS_TEMPLATE.substitute(
        system_prompt=system_prompt,
        pet_info_section=pet_info_section,
        tool_results=tool_results,
        query=query
    )
