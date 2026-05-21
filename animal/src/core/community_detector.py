"""
社区检测与层级索引

使用Louvain/Leiden算法对知识图谱进行社区划分，
构建层级社区结构，支持从粗粒度到细粒度的知识检索。

核心功能：
1. 社区检测 - 基于模块度优化的图划分
2. 层级社区 - 多级聚合形成层级索引
3. 社区摘要 - 为每个社区生成LLM摘要描述
4. 全局摘要 - 顶层社区聚合生成全局概览
"""
import logging
from typing import List, Dict, Any, Optional, Set, Tuple

from src.core.graph_db import get_graph_db

logger = logging.getLogger(__name__)

COMMUNITY_SUMMARY_PROMPT = """为以下宠物健康知识图谱社区生成摘要。

社区包含的实体：
{entities}

社区包含的关系模式：
{relations}

请为这个社区生成：
1. community_title: 社区标题（10字以内）
2. summary: 社区内容摘要（50-100字，描述该社区覆盖的知识主题和关键信息）
3. key_concepts: 关键概念列表（3-5个最重要的实体名称）
4. cross_references: 与其他社区的可能关联方向

输出JSON格式：
{{
  "community_title": "...",
  "summary": "...",
  "key_concepts": ["...", "..."],
  "cross_references": ["..."]
}}"""


class CommunityDetector:
    """社区检测器"""

    def __init__(self):
        self.graph_db = get_graph_db()
        self._communities: Dict[int, Dict[str, Any]] = {}
        self._node_to_community: Dict[str, int] = {}
        self._hierarchy: Dict[int, List[int]] = {}
        self._llm = None
        self._llm_available = False
        self._init_llm()

    def _init_llm(self):
        try:
            from src.core.llm import get_llm
            self._llm = get_llm()
            self._llm_available = True
        except Exception:
            self._llm_available = False

    def detect_communities(
        self,
        algorithm: str = "greedy_modularity",
        min_community_size: int = 3
    ) -> Dict[int, Dict[str, Any]]:
        """检测图谱社区结构"""
        if self.graph_db.backend == "networkx":
            return self._detect_nx_communities(algorithm, min_community_size)
        return self._detect_neo4j_communities(min_community_size)

    def _detect_nx_communities(
        self, algorithm: str, min_size: int
    ) -> Dict[int, Dict[str, Any]]:
        try:
            import networkx as nx
            from networkx.algorithms.community import greedy_modularity_communities
        except ImportError:
            logger.error("networkx未安装，社区检测不可用")
            return {}

        graph = self.graph_db._nx_graph
        if graph is None or graph.number_of_nodes() == 0:
            logger.warning("图为空，无法检测社区")
            return {}

        undirected = graph.to_undirected()

        if algorithm == "greedy_modularity":
            communities_iter = greedy_modularity_communities(undirected)
            raw_communities = [list(c) for c in communities_iter if len(c) >= min_size]
        else:
            raw_communities = list(nx.connected_components(undirected))
            raw_communities = [list(c) for c in raw_communities if len(c) >= min_size]

        self._communities = {}
        self._node_to_community = {}

        for i, community_nodes in enumerate(raw_communities):
            node_data_list = []
            for node_key in community_nodes:
                if node_key in graph.nodes:
                    node_data = dict(graph.nodes[node_key])
                    node_data_list.append(node_data)
                    self._node_to_community[node_key] = i

            self._communities[i] = {
                "id": i,
                "size": len(community_nodes),
                "nodes": community_nodes,
                "entities": node_data_list,
                "summary": "",
                "key_concepts": [],
            }

        logger.info(f"社区检测完成: {len(self._communities)}个社区")
        return self._communities

    def _detect_neo4j_communities(self, min_size: int) -> Dict[int, Dict[str, Any]]:
        try:
            with self.graph_db._neo4j_driver.session() as session:
                result = session.run(
                    "CALL gds.louvain.stream('pet-health-graph') "
                    "YIELD nodeId, communityId "
                    "RETURN communityId, collect(nodeId) as nodes "
                    "ORDER BY size(nodes) DESC"
                )
                self._communities = {}
                self._node_to_community = {}
                for i, record in enumerate(result):
                    nodes = record["nodes"]
                    if len(nodes) >= min_size:
                        self._communities[i] = {
                            "id": i,
                            "size": len(nodes),
                            "nodes": nodes,
                            "entities": [],
                            "summary": "",
                            "key_concepts": [],
                        }
                logger.info(f"Neo4j社区检测完成: {len(self._communities)}个社区")
                return self._communities
        except Exception as e:
            logger.warning(f"Neo4j社区检测失败({e})，回退到连通分量")
            return {}

    def build_hierarchy(self, levels: int = 3) -> Dict[int, List[int]]:
        """构建层级社区结构"""
        if not self._communities:
            logger.warning("尚未检测社区，无法构建层级")
            return {}

        self._hierarchy = {}

        communities_by_size = sorted(
            self._communities.items(),
            key=lambda x: x[1]["size"],
            reverse=True
        )

        top_level_size = max(1, len(communities_by_size) // levels)
        if top_level_size == 0:
            top_level_size = 1

        level_assignments = {}
        for i, (cid, cdata) in enumerate(communities_by_size):
            level = min(i // top_level_size, levels - 1)
            level_assignments[cid] = level
            parent_level = level - 1 if level > 0 else -1
            if parent_level >= 0:
                parent_idx = (i // top_level_size - 1) if i >= top_level_size else 0
                if parent_idx < len(communities_by_size):
                    parent_cid = communities_by_size[parent_idx][0]
                    self._hierarchy.setdefault(parent_cid, []).append(cid)

        for cid in self._communities:
            self._communities[cid]["level"] = level_assignments.get(cid, 0)
            self._communities[cid]["parent"] = None
            self._communities[cid]["children"] = []

        for parent_cid, children in self._hierarchy.items():
            if parent_cid in self._communities:
                self._communities[parent_cid]["children"] = children
            for child_cid in children:
                if child_cid in self._communities:
                    self._communities[child_cid]["parent"] = parent_cid

        logger.info(f"层级结构构建完成: {levels}层, {len(self._communities)}个社区")
        return self._hierarchy

    def generate_community_summaries(self) -> Dict[int, str]:
        """生成社区摘要"""
        for cid, cdata in self._communities.items():
            if self._llm_available and self._llm:
                summary = self._llm_summarize_community(cdata)
            else:
                summary = self._rule_summarize_community(cdata)
            self._communities[cid]["summary"] = summary
            self._communities[cid]["key_concepts"] = self._extract_key_concepts(cdata)

        logger.info(f"社区摘要生成完成: {len(self._communities)}个社区")
        return {cid: cdata.get("summary", "") for cid, cdata in self._communities.items()}

    def _llm_summarize_community(self, cdata: Dict[str, Any]) -> str:
        try:
            entity_names = []
            for e in cdata.get("entities", [])[:20]:
                entity_names.append(f"{e.get('type', '')}/{e.get('name', '')}")

            from collections import Counter
            edge_types = []
            for node_key in cdata.get("nodes", []):
                if self.graph_db.backend == "networkx":
                    for _, neighbor, edge_data in self.graph_db._nx_graph.edges(node_key, data=True):
                        edge_types.append(edge_data.get("type", ""))

            rel_summary = ", ".join([f"{k}({v})" for k, v in Counter(edge_types).most_common(5)])

            prompt = COMMUNITY_SUMMARY_PROMPT.format(
                entities=", ".join(entity_names),
                relations=rel_summary or "无",
            )
            response = self._llm.invoke(prompt)
            text = response.content if hasattr(response, "content") else str(response)
            text = self._extract_json(text)
            data = __import__("json").loads(text)
            return data.get("summary", "")
        except Exception as e:
            logger.warning(f"LLM社区摘要生成失败: {e}")
            return self._rule_summarize_community(cdata)

    def _rule_summarize_community(self, cdata: Dict[str, Any]) -> str:
        entity_types = {}
        for e in cdata.get("entities", []):
            etype = e.get("type", "Unknown")
            entity_types[etype] = entity_types.get(etype, 0) + 1

        type_summary = ", ".join(f"{k}({v})" for k, v in sorted(entity_types.items(), key=lambda x: -x[1])[:5])
        return f"该社区包含{cdata.get('size', 0)}个节点，主要实体类型: {type_summary}"

    def _extract_key_concepts(self, cdata: Dict[str, Any]) -> List[str]:
        entities = cdata.get("entities", [])
        diseases = [e["name"] for e in entities if e.get("type") == "Disease"][:3]
        symptoms = [e["name"] for e in entities if e.get("type") == "Symptom"][:2]
        return diseases + symptoms

    def get_community_for_entity(self, entity_type: str, entity_id: str) -> Optional[int]:
        """获取实体所属社区"""
        node_key = self.graph_db._node_key(entity_type, entity_id)
        return self._node_to_community.get(node_key)

    def get_community(self, community_id: int) -> Optional[Dict[str, Any]]:
        """获取社区详情"""
        return self._communities.get(community_id)

    def get_communities_at_level(self, level: int) -> List[Dict[str, Any]]:
        """获取指定层级的所有社区"""
        return [
            cdata for cdata in self._communities.values()
            if cdata.get("level") == level
        ]

    @property
    def communities(self) -> Dict[int, Dict[str, Any]]:
        return self._communities

    @property
    def hierarchy(self) -> Dict[int, List[int]]:
        return self._hierarchy

    @staticmethod
    def _extract_json(text: str) -> str:
        import re
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


_community_detector: Optional[CommunityDetector] = None


def get_community_detector() -> CommunityDetector:
    global _community_detector
    if _community_detector is None:
        _community_detector = CommunityDetector()
    return _community_detector