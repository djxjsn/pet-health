"""
GraphRAG 检索器

基于知识图谱的多跳推理检索引擎：
1. 实体定位 - 从查询中识别关键实体，定位图谱节点
2. 多跳推理 - 沿关系路径扩展，发现关联知识
3. 路径排序 - 基于路径长度、节点重要性、关系权重排序
4. 子图提取 - 提取推理子图作为结构化上下文
5. 社区检索 - 基于社区层级索引的全局搜索
"""
import logging
from typing import List, Dict, Any, Optional, Set, Tuple

from src.core.graph_db import get_graph_db
from src.core.community_detector import get_community_detector

logger = logging.getLogger(__name__)


class GraphRetriever:
    """GraphRAG检索器 - 基于图谱的多跳推理检索"""

    def __init__(self):
        self.graph_db = get_graph_db()
        self.community_detector = get_community_detector()
        self._max_hops = 3
        self._max_paths = 10
        self._max_results = 20

    def search(
        self,
        query: str,
        entities: Optional[List[Dict[str, Any]]] = None,
        max_hops: int = 3,
        max_results: int = 20,
        include_communities: bool = True
    ) -> Dict[str, Any]:
        """图谱检索主入口

        Args:
            query: 用户查询
            entities: 查询中已识别的实体（由QueryRewriter提供）
            max_hops: 最大跳数
            max_results: 最大结果数
            include_communities: 是否包含社区级检索

        Returns:
            {
                "entities": 匹配的图谱实体,
                "paths": 多跳推理路径,
                "subgraph": 提取的子图,
                "community_results": 社区检索结果,
                "reasoning_chains": 推理链列表,
            }
        """
        self._max_hops = max_hops
        self._max_results = max_results

        if not entities:
            entities = self._extract_query_entities(query)

        matched_entities = self._match_entities(entities)

        paths = self._multi_hop_explore(matched_entities, max_hops)

        reasoning_chains = self._build_reasoning_chains(paths, query)

        community_results = []
        if include_communities and self.community_detector.communities:
            community_results = self._community_retrieval(matched_entities, query)

        subgraph_entities, subgraph_relations = self._extract_subgraph(paths, matched_entities)

        return {
            "entities": list(matched_entities.values()),
            "paths": paths,
            "subgraph": {
                "entities": subgraph_entities,
                "relations": subgraph_relations,
            },
            "community_results": community_results,
            "reasoning_chains": reasoning_chains,
            "total_entity_count": len(matched_entities),
            "total_path_count": len(paths),
            "hop_count": max_hops,
        }

    def _extract_query_entities(self, query: str) -> List[Dict[str, Any]]:
        """从查询文本中提取关键实体（轻量级规则匹配）"""
        entities = []

        entity_patterns = [
            ("Species", [("狗", "犬"), ("猫", "猫咪"), ("兔子", "兔"), ("仓鼠",), ("鸟",), ("鱼",)]),
            ("Breed", [("金毛", "金毛寻回犬"), ("拉布拉多", "拉布拉多寻回犬"), ("布偶", "布偶猫"),
                        ("柯基",), ("哈士奇",), ("泰迪", "贵宾犬"), ("暹罗", "暹罗猫"), ("波斯", "波斯猫"),
                        ("英短", "英国短毛猫"), ("美短", "美国短毛猫"), ("中华田园猫", "田园猫"),
                        ("中华田园犬", "田园犬"), ("萨摩耶",), ("边牧", "边境牧羊犬"),
                        ("柴犬",), ("德牧", "德国牧羊犬"), ("缅因", "缅因猫"), ("斯芬克斯", "无毛猫")]),
            ("Disease", [("腹泻", "拉肚子", "拉稀"), ("呕吐",), ("感冒", "着凉"), ("皮肤病", "皮肤问题"),
                         ("耳螨",), ("寄生虫",), ("犬瘟", "犬瘟热"), ("细小", "细小病毒"), ("猫瘟",),
                         ("便秘",), ("过敏",), ("关节炎",), ("肥胖",), ("糖尿病",), ("肾衰竭", "肾衰")]),
            ("Symptom", [("发热", "发烧"), ("咳嗽",), ("打喷嚏", "喷嚏"), ("流鼻涕", "鼻涕"),
                         ("没精神", "精神萎靡"), ("不吃东西", "厌食", "拒食"), ("瘙痒", "痒"),
                         ("脱毛", "掉毛"), ("跛行", "瘸"), ("抽搐", "抽筋")]),
            ("BodyPart", [("消化", "消化道", "肠胃"), ("呼吸道", "肺"), ("皮肤", "毛发"),
                          ("泌尿", "肾", "肾脏"), ("眼睛", "眼部"), ("口腔", "牙齿", "牙龈"),
                          ("骨骼", "关节"), ("心脏", "心血管")]),
        ]

        for entity_type, patterns in entity_patterns:
            for variants in patterns:
                if any(v in query for v in variants):
                    entities.append({
                        "type": entity_type,
                        "name": variants[0],
                        "aliases": list(variants),
                        "properties": {},
                    })
                    break

        return entities

    def _match_entities(self, query_entities: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """在图谱中匹配查询实体"""
        matched = {}

        for qe in query_entities:
            etype = qe["type"]
            name = qe["name"]
            aliases = qe.get("aliases", [])

            entity_id = self._entity_name_to_id(etype, name)
            graph_entity = self.graph_db.get_entity(etype, entity_id)

            if graph_entity:
                key = f"{etype}::{name}"
                matched[key] = {
                    "type": etype,
                    "name": name,
                    "id": entity_id,
                    "properties": dict(graph_entity.items()),
                    "score": 1.0,
                }
                continue

            for alias in aliases:
                alias_id = self._entity_name_to_id(etype, alias)
                graph_entity = self.graph_db.get_entity(etype, alias_id)
                if graph_entity:
                    key = f"{etype}::{name}"
                    matched[key] = {
                        "type": etype,
                        "name": alias,
                        "id": alias_id,
                        "properties": dict(graph_entity.items()),
                        "score": 0.9,
                    }
                    break

            if f"{etype}::{name}" not in matched:
                search_results = self.graph_db.search_entities(
                    entity_type=etype, name_pattern=name, limit=5
                )
                for ge in search_results:
                    ge_id = ge.get("id", "")
                    ge_name = ge.get("name", "")
                    ge_type = ge.get("entity_type", ge.get("label", etype))
                    key = f"{ge_type}::{ge_name}"
                    if key not in matched and ge_id:
                        matched[key] = {
                            "type": ge_type,
                            "name": ge_name,
                            "id": ge_id,
                            "properties": ge,
                            "score": 0.7,
                        }

            if f"{etype}::{name}" not in matched and name:
                all_results = self.graph_db.search_entities(
                    entity_type=None, name_pattern=name, limit=10
                )
                for ge in all_results:
                    ge_id = ge.get("id", "")
                    ge_name = ge.get("name", "")
                    ge_type = ge.get("entity_type", ge.get("label", "Entity"))
                    if ge_name and ge_name in (name, *aliases):
                        key = f"{ge_type}::{ge_name}"
                        if key not in matched and ge_id:
                            matched[key] = {
                                "type": ge_type,
                                "name": ge_name,
                                "id": ge_id,
                                "properties": ge,
                                "score": 0.6,
                            }

        return matched

    def _multi_hop_explore(
        self, matched_entities: Dict[str, Dict[str, Any]], max_hops: int
    ) -> List[Dict[str, Any]]:
        """多跳扩展探索"""
        all_paths = []

        entity_list = list(matched_entities.values())

        for i, start_entity in enumerate(entity_list):
            neighbors = self.graph_db.get_neighbors(
                start_entity["type"],
                start_entity["id"],
                max_depth=max_hops
            )
            for neighbor in neighbors:
                all_paths.append({
                    "start": {
                        "type": start_entity["type"],
                        "name": start_entity["name"],
                        "id": start_entity["id"],
                    },
                    "end": {
                        "type": neighbor.get("entity_type", "Unknown"),
                        "name": neighbor.get("name", ""),
                        "id": neighbor.get("id", ""),
                    },
                    "hops": 1,
                    "score": start_entity["score"] * 0.9,
                })

            for j, other_entity in enumerate(entity_list):
                if j <= i:
                    continue
                paths = self.graph_db.get_paths(
                    start_entity["type"], start_entity["id"],
                    other_entity["type"], other_entity["id"],
                    max_depth=max_hops,
                    max_paths=5
                )
                for path in paths:
                    all_paths.append({
                        "start": {
                            "type": start_entity["type"],
                            "name": start_entity["name"],
                            "id": start_entity["id"],
                        },
                        "end": {
                            "type": other_entity["type"],
                            "name": other_entity["name"],
                            "id": other_entity["id"],
                        },
                        "path_nodes": path,
                        "hops": len(path) - 1 if len(path) > 1 else 1,
                        "score": start_entity["score"] * other_entity["score"] * (0.8 ** (len(path) - 1)),
                    })

        all_paths.sort(key=lambda x: x["score"], reverse=True)
        return all_paths[:self._max_paths]

    def _build_reasoning_chains(
        self, paths: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """构建推理链"""
        chains = []

        for path in paths[:5]:
            path_nodes = path.get("path_nodes", [path["start"], path["end"]])

            chain_steps = []
            for i, node in enumerate(path_nodes):
                if isinstance(node, dict):
                    chain_steps.append({
                        "step": i + 1,
                        "entity_type": node.get("entity_type", node.get("type", "")),
                        "entity_name": node.get("name", ""),
                        "description": node.get("description", ""),
                    })

            start_name = path["start"].get("name", "")
            end_name = path["end"].get("name", "")
            reasoning = f"从「{start_name}」出发，经过{len(chain_steps)}步关联到「{end_name}」"

            chains.append({
                "reasoning": reasoning,
                "steps": chain_steps,
                "confidence": path["score"],
                "hops": path["hops"],
            })

        return chains

    def _community_retrieval(
        self, matched_entities: Dict[str, Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """基于社区索引的检索"""
        results = []

        relevant_communities: Set[int] = set()
        for entity_info in matched_entities.values():
            cid = self.community_detector.get_community_for_entity(
                entity_info["type"], entity_info["id"]
            )
            if cid is not None:
                relevant_communities.add(cid)

        for cid in relevant_communities:
            cdata = self.community_detector.get_community(cid)
            if cdata:
                results.append({
                    "community_id": cid,
                    "level": cdata.get("level", 0),
                    "size": cdata.get("size", 0),
                    "summary": cdata.get("summary", ""),
                    "key_concepts": cdata.get("key_concepts", []),
                    "score": 0.8 if cdata.get("level", 0) == 0 else 0.6,
                })

        for cid, cdata in self.community_detector.communities.items():
            if cid not in relevant_communities and cdata.get("summary"):
                if any(kw in cdata["summary"].lower() for kw in query.lower().split() if len(kw) >= 2):
                    results.append({
                        "community_id": cid,
                        "level": cdata.get("level", 0),
                        "size": cdata.get("size", 0),
                        "summary": cdata.get("summary", ""),
                        "key_concepts": cdata.get("key_concepts", []),
                        "score": 0.4,
                    })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]

    def _extract_subgraph(
        self, paths: List[Dict[str, Any]], matched_entities: Dict[str, Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """提取推理子图"""
        seen_entities: Set[str] = set()
        subgraph_entities = []
        subgraph_relations = []

        for path in paths:
            nodes = path.get("path_nodes", [path["start"], path["end"]])
            for node in nodes:
                if isinstance(node, dict):
                    key = f"{node.get('entity_type', '')}::{node.get('name', '')}"
                    if key not in seen_entities:
                        seen_entities.add(key)
                        subgraph_entities.append({
                            "type": node.get("entity_type", node.get("type", "")),
                            "name": node.get("name", ""),
                            "id": node.get("id", ""),
                        })

            if not path.get("path_nodes"):
                subgraph_relations.append({
                    "from": path["start"]["name"],
                    "to": path["end"]["name"],
                    "type": "RELATED_TO",
                    "score": path["score"],
                })
            else:
                for i in range(len(path["path_nodes"]) - 1):
                    subgraph_relations.append({
                        "from": path["path_nodes"][i].get("name", ""),
                        "to": path["path_nodes"][i + 1].get("name", ""),
                        "type": "RELATED_TO",
                        "score": path["score"],
                    })

        return subgraph_entities, subgraph_relations

    def format_for_llm(self, search_result: Dict[str, Any]) -> str:
        """将图谱检索结果格式化为LLM可读文本"""
        parts = []

        entities = search_result.get("entities", [])
        if entities:
            parts.append("【相关实体】")
            for e in entities[:10]:
                score_str = f"{e.get('score', 0):.0%}" if isinstance(e.get('score'), (int, float)) else "N/A"
                parts.append(f"- {e['type']}: {e['name']} (置信度: {score_str})")

        reasoning = search_result.get("reasoning_chains", [])
        if reasoning:
            parts.append("\n【推理链】")
            for i, chain in enumerate(reasoning, 1):
                conf_str = f"{chain['confidence']:.0%}" if isinstance(chain.get('confidence'), (int, float)) else "N/A"
                parts.append(f"推断{i}: {chain['reasoning']} (置信度: {conf_str}, {chain['hops']}跳)")

        communities = search_result.get("community_results", [])
        if communities:
            parts.append("\n【相关知识社区】")
            for c in communities[:3]:
                concepts = ', '.join(c.get('key_concepts', []))
                parts.append(f"- {c.get('summary', '')} (关键概念: {concepts})")

        subgraph = search_result.get("subgraph", {})
        if not parts and subgraph.get("entities"):
            parts.append("【图谱检索子图】")
            for e in subgraph["entities"][:10]:
                parts.append(f"- {e.get('type', '')}: {e.get('name', '')}")

        if not parts:
            parts.append("（图谱检索无匹配结果，建议使用向量检索补充）")

        return "\n".join(parts)

    @staticmethod
    def _entity_name_to_id(entity_type: str, entity_name: str) -> str:
        import hashlib
        key = f"{entity_type}::{entity_name}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()[:12]


_graph_retriever: Optional[GraphRetriever] = None


def get_graph_retriever() -> GraphRetriever:
    global _graph_retriever
    if _graph_retriever is None:
        _graph_retriever = GraphRetriever()
    return _graph_retriever