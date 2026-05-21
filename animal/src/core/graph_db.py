"""
图数据库连接器

封装 Neo4j 图数据库交互，当 Neo4j 不可用时自动回退到内存图（networkx）。
支持：实体CRUD、关系CRUD、社区检测、多跳路径查询。
"""
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

DEFAULT_NEO4J_URI = "bolt://localhost:7687"
DEFAULT_NEO4J_USER = "neo4j"
DEFAULT_NEO4J_PASSWORD = "password"

ENTITY_LABELS = [
    "Species", "Breed", "Disease", "Symptom", "Medication",
    "BodyPart", "NutritionElement", "Behavior", "FirstAidMeasure",
    "DiagnosticMethod", "TreatmentMethod", "PreventionMeasure",
]

RELATION_TYPES = [
    "HAS_SYMPTOM",
    "BELONGS_TO",
    "TREATED_BY",
    "AFFECTS",
    "RELATED_TO",
    "CAUSES",
    "PREVENTS",
    "CONTAINS",
    "RECOMMENDS",
    "COMPLICATES",
]


class GraphDatabase:
    """图数据库统一接口（Neo4j优先，networkx兜底）"""

    def __init__(self, uri: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None):
        self._neo4j_driver = None
        self._nx_graph = None
        self._backend = "networkx"
        self._init_neo4j(uri, user, password)
        if self._backend == "networkx":
            self._init_networkx()

    def _init_neo4j(self, uri: Optional[str], user: Optional[str], password: Optional[str]):
        try:
            from neo4j import GraphDatabase as Neo4jDriver
            uri = uri or DEFAULT_NEO4J_URI
            user = user or DEFAULT_NEO4J_USER
            password = password or DEFAULT_NEO4J_PASSWORD
            self._neo4j_driver = Neo4jDriver.driver(uri, auth=(user, password))
            self._neo4j_driver.verify_connectivity()
            self._backend = "neo4j"
            logger.info("Neo4j图数据库连接成功")
        except ImportError:
            logger.info("neo4j-driver未安装，使用networkx内存图")
        except Exception as e:
            logger.warning(f"Neo4j连接失败({e})，使用networkx内存图")

    def _init_networkx(self):
        try:
            import networkx as nx
            self._nx_graph = nx.MultiDiGraph()
            logger.info("NetworkX内存图初始化成功")
        except ImportError:
            logger.error("networkx未安装，图功能不可用")
            raise

    @property
    def is_available(self) -> bool:
        return self._neo4j_driver is not None or self._nx_graph is not None

    @property
    def backend(self) -> str:
        return self._backend

    def create_entity(self, entity_type: str, entity_id: str, properties: Dict[str, Any]) -> bool:
        if self._backend == "neo4j":
            return self._neo4j_create_entity(entity_type, entity_id, properties)
        return self._nx_create_entity(entity_type, entity_id, properties)

    def create_relation(
        self,
        from_type: str, from_id: str,
        relation_type: str,
        to_type: str, to_id: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        if self._backend == "neo4j":
            return self._neo4j_create_relation(from_type, from_id, relation_type, to_type, to_id, properties)
        return self._nx_create_relation(from_type, from_id, relation_type, to_type, to_id, properties)

    def get_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        if self._backend == "neo4j":
            return self._neo4j_get_entity(entity_type, entity_id)
        return self._nx_get_entity(entity_type, entity_id)

    def get_neighbors(
        self, entity_type: str, entity_id: str,
        relation_types: Optional[List[str]] = None,
        max_depth: int = 1
    ) -> List[Dict[str, Any]]:
        if self._backend == "neo4j":
            return self._neo4j_get_neighbors(entity_type, entity_id, relation_types, max_depth)
        return self._nx_get_neighbors(entity_type, entity_id, relation_types, max_depth)

    def get_paths(
        self,
        from_type: str, from_id: str,
        to_type: str, to_id: str,
        max_depth: int = 3,
        max_paths: int = 10
    ) -> List[List[Dict[str, Any]]]:
        if self._backend == "neo4j":
            return self._neo4j_get_paths(from_type, from_id, to_type, to_id, max_depth, max_paths)
        return self._nx_get_paths(from_type, from_id, to_type, to_id, max_depth, max_paths)

    def search_entities(
        self,
        entity_type: Optional[str] = None,
        name_pattern: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        if self._backend == "neo4j":
            return self._neo4j_search_entities(entity_type, name_pattern, properties, limit)
        return self._nx_search_entities(entity_type, name_pattern, properties, limit)

    def delete_entity(self, entity_type: str, entity_id: str) -> bool:
        if self._backend == "neo4j":
            return self._neo4j_delete_entity(entity_type, entity_id)
        return self._nx_delete_entity(entity_type, entity_id)

    def clear_all(self) -> bool:
        if self._backend == "neo4j":
            return self._neo4j_clear_all()
        return self._nx_clear_all()

    def get_stats(self) -> Dict[str, Any]:
        if self._backend == "neo4j":
            return self._neo4j_get_stats()
        return self._nx_get_stats()

    # ===== Neo4j 实现 =====

    def _neo4j_create_entity(self, entity_type: str, entity_id: str, properties: Dict[str, Any]) -> bool:
        try:
            safe_props = self._sanitize_props(properties)
            safe_props["id"] = entity_id
            safe_props["entity_type"] = entity_type
            query = (
                f"MERGE (n:{entity_type} {{id: $id}}) "
                "SET n += $props"
            )
            with self._neo4j_driver.session() as session:
                session.run(query, id=entity_id, props=safe_props)
            return True
        except Exception as e:
            logger.error(f"Neo4j创建实体失败: {e}")
            return False

    def _neo4j_create_relation(self, from_type, from_id, rel_type, to_type, to_id, props) -> bool:
        try:
            props = props or {}
            query = (
                f"MATCH (a:{from_type} {{id: $from_id}}) "
                f"MATCH (b:{to_type} {{id: $to_id}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) "
                "SET r += $props"
            )
            with self._neo4j_driver.session() as session:
                session.run(query, from_id=from_id, to_id=to_id, props=props)
            return True
        except Exception as e:
            logger.error(f"Neo4j创建关系失败: {e}")
            return False

    def _neo4j_get_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        try:
            query = f"MATCH (n:{entity_type} {{id: $id}}) RETURN n"
            with self._neo4j_driver.session() as session:
                result = session.run(query, id=entity_id)
                record = result.single()
                if record:
                    node = record["n"]
                    return dict(node.items())
            return None
        except Exception as e:
            logger.error(f"Neo4j查询实体失败: {e}")
            return None

    def _neo4j_get_neighbors(self, entity_type, entity_id, rel_types, max_depth) -> List[Dict[str, Any]]:
        try:
            rel_filter = ""
            if rel_types:
                rel_list = "|".join(rel_types)
                rel_filter = f":[r:{rel_list}]"
            query = (
                f"MATCH (n:{entity_type} {{id: $id}})"
                f"-[r{rel_filter}*1..{max_depth}]-(m) "
                "RETURN DISTINCT m, r"
            )
            with self._neo4j_driver.session() as session:
                result = session.run(query, id=entity_id)
                neighbors = []
                for record in result:
                    node = record["m"]
                    neighbors.append(dict(node.items()))
                return neighbors
        except Exception as e:
            logger.error(f"Neo4j查询邻居失败: {e}")
            return []

    def _neo4j_get_paths(self, from_type, from_id, to_type, to_id, max_depth, max_paths) -> List[List[Dict]]:
        try:
            query = (
                f"MATCH path = (a:{from_type} {{id: $from_id}})"
                f"-[*1..{max_depth}]-(b:{to_type} {{id: $to_id}}) "
                "RETURN path LIMIT $max_paths"
            )
            with self._neo4j_driver.session() as session:
                result = session.run(query, from_id=from_id, to_id=to_id, max_paths=max_paths)
                paths = []
                for record in result:
                    path = record["path"]
                    path_nodes = []
                    for node in path.nodes:
                        path_nodes.append(dict(node.items()))
                    paths.append(path_nodes)
                return paths
        except Exception as e:
            logger.error(f"Neo4j路径查询失败: {e}")
            return []

    def _neo4j_search_entities(self, entity_type, name_pattern, props, limit) -> List[Dict[str, Any]]:
        try:
            label = entity_type or "Entity"
            conditions = []
            params = {"limit": limit}
            if name_pattern:
                conditions.append("n.name CONTAINS $name")
                params["name"] = name_pattern
            if props:
                for k, v in props.items():
                    conditions.append(f"n.{k} = $prop_{k}")
                    params[f"prop_{k}"] = v
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            query = f"MATCH (n:{label}) WHERE {where_clause} RETURN n LIMIT $limit"
            with self._neo4j_driver.session() as session:
                result = session.run(query, **params)
                return [dict(record["n"].items()) for record in result]
        except Exception as e:
            logger.error(f"Neo4j实体搜索失败: {e}")
            return []

    def _neo4j_delete_entity(self, entity_type: str, entity_id: str) -> bool:
        try:
            query = f"MATCH (n:{entity_type} {{id: $id}}) DETACH DELETE n"
            with self._neo4j_driver.session() as session:
                session.run(query, id=entity_id)
            return True
        except Exception as e:
            logger.error(f"Neo4j删除实体失败: {e}")
            return False

    def _neo4j_clear_all(self) -> bool:
        try:
            with self._neo4j_driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            return True
        except Exception as e:
            logger.error(f"Neo4j清空失败: {e}")
            return False

    def _neo4j_get_stats(self) -> Dict[str, Any]:
        try:
            with self._neo4j_driver.session() as session:
                nodes = session.run("MATCH (n) RETURN count(n) as c").single()
                edges = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()
                labels = session.run("MATCH (n) RETURN DISTINCT labels(n)[0] as label, count(n) as c").data()
                return {
                    "backend": "neo4j",
                    "node_count": nodes["c"],
                    "relation_count": edges["c"],
                    "label_distribution": {r["label"]: r["c"] for r in labels},
                }
        except Exception as e:
            logger.error(f"Neo4j统计失败: {e}")
            return {"backend": "neo4j", "error": str(e)}

    # ===== NetworkX 实现 =====

    def _node_key(self, entity_type: str, entity_id: str) -> str:
        return f"{entity_type}::{entity_id}"

    def _nx_create_entity(self, entity_type: str, entity_id: str, properties: Dict[str, Any]) -> bool:
        key = self._node_key(entity_type, entity_id)
        props = self._sanitize_props(properties)
        props["id"] = entity_id
        props["entity_type"] = entity_type
        props["label"] = entity_type
        self._nx_graph.add_node(key, **props)
        return True

    def _nx_create_relation(self, from_type, from_id, rel_type, to_type, to_id, props) -> bool:
        from_key = self._node_key(from_type, from_id)
        to_key = self._node_key(to_type, to_id)
        self._nx_graph.add_edge(from_key, to_key, type=rel_type, **(props or {}))
        return True

    def _nx_get_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        key = self._node_key(entity_type, entity_id)
        if key in self._nx_graph.nodes:
            return dict(self._nx_graph.nodes[key])
        return None

    def _nx_get_neighbors(self, entity_type, entity_id, rel_types, max_depth) -> List[Dict[str, Any]]:
        import networkx as nx
        key = self._node_key(entity_type, entity_id)
        if key not in self._nx_graph:
            return []
        neighbors = []
        try:
            undirected = self._nx_graph.to_undirected()
            paths = nx.single_source_shortest_path_length(undirected, key, cutoff=max_depth)
            for nk in paths:
                if nk != key:
                    node_data = dict(self._nx_graph.nodes[nk])
                    neighbors.append(node_data)
        except Exception as e:
            logger.error(f"NX邻居查询失败: {e}")
        return neighbors

    def _nx_get_paths(self, from_type, from_id, to_type, to_id, max_depth, max_paths) -> List[List[Dict]]:
        try:
            from_key = self._node_key(from_type, from_id)
            to_key = self._node_key(to_type, to_id)
            undirected = self._nx_graph.to_undirected()
            if from_key not in undirected or to_key not in undirected:
                return []
            paths = []
            import networkx as nx
            for path in nx.all_simple_paths(undirected, from_key, to_key, cutoff=max_depth):
                path_data = [dict(self._nx_graph.nodes[n]) for n in path]
                paths.append(path_data)
                if len(paths) >= max_paths:
                    break
            return paths
        except Exception:
            return []

    def _nx_search_entities(self, entity_type, name_pattern, props, limit) -> List[Dict[str, Any]]:
        results = []
        prefix = f"{entity_type}::" if entity_type else ""
        for node_key, node_data in self._nx_graph.nodes(data=True):
            if entity_type and not node_key.startswith(prefix):
                continue
            if name_pattern:
                name = node_data.get("name", "")
                if name_pattern.lower() not in name.lower():
                    continue
            if props:
                if not all(node_data.get(k) == v for k, v in props.items()):
                    continue
            results.append(dict(node_data.items()))
            if len(results) >= limit:
                break
        return results

    def _nx_delete_entity(self, entity_type: str, entity_id: str) -> bool:
        key = self._node_key(entity_type, entity_id)
        if key in self._nx_graph:
            self._nx_graph.remove_node(key)
            return True
        return False

    def _nx_clear_all(self) -> bool:
        self._nx_graph.clear()
        return True

    def _nx_get_stats(self) -> Dict[str, Any]:
        if self._nx_graph is None:
            return {"backend": "networkx", "error": "未初始化"}
        label_dist = {}
        for node_key, node_data in self._nx_graph.nodes(data=True):
            label = node_data.get("label", node_data.get("entity_type", "Unknown"))
            label_dist[label] = label_dist.get(label, 0) + 1
        rel_dist = {}
        for _, _, edge_data in self._nx_graph.edges(data=True):
            rtype = edge_data.get("type", "Unknown")
            rel_dist[rtype] = rel_dist.get(rtype, 0) + 1
        return {
            "backend": "networkx",
            "node_count": self._nx_graph.number_of_nodes(),
            "relation_count": self._nx_graph.number_of_edges(),
            "label_distribution": label_dist,
            "relation_distribution": rel_dist,
        }

    @staticmethod
    def _sanitize_props(props: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = {}
        for k, v in props.items():
            if v is None:
                continue
            if isinstance(v, (str, int, float, bool)):
                cleaned[k] = v
            elif isinstance(v, (list, tuple)):
                cleaned[k] = [str(item) if not isinstance(item, (str, int, float, bool)) else item for item in v]
            else:
                cleaned[k] = str(v)
        return cleaned


_graph_db: Optional[GraphDatabase] = None


def get_graph_db() -> GraphDatabase:
    global _graph_db
    if _graph_db is None:
        _graph_db = GraphDatabase()
    return _graph_db