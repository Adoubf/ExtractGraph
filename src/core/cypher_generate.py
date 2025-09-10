from typing import Dict, List, Any, Tuple


class CypherGenerator:
    """
    专门用于生成 Neo4j Cypher 导入语句的类
    """
    
    def generate_cypher_import(self, neo4j_data: Dict[str, List[Dict[str, Any]]]) -> Tuple[str, str]:
        """
        生成 Neo4j Cypher 导入语句
        
        Args:
            neo4j_data: 包含 nodes 和 relationships 的字典
            
        Returns:
            (nodes_cypher, relationships_cypher) 元组
        """
        nodes = neo4j_data.get('nodes', [])
        relationships = neo4j_data.get('relationships', [])
        
        # 生成节点导入语句
        nodes_cypher = self._generate_nodes_cypher(nodes)
        
        # 生成关系导入语句
        relationships_cypher = self._generate_relationships_cypher(relationships)
        
        return nodes_cypher, relationships_cypher

    def _generate_nodes_cypher(self, nodes: List[Dict[str, Any]]) -> str:
        """生成节点 Cypher 语句"""
        if not nodes:
            return ""
        
        cypher_statements = []
        
        for node in nodes:
            label = node.get('label', 'ENTITY')
            
            # 构建属性字符串
            props = []
            for key, value in node.items():
                if key != 'label' and value is not None:
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "\\'")
                        props.append(f"{key}: '{escaped_value}'")
                    else:
                        props.append(f"{key}: {value}")
            
            props_str = "{" + ", ".join(props) + "}"
            
            cypher = f"CREATE (n:{label} {props_str})"
            cypher_statements.append(cypher)
        
        return ";\n".join(cypher_statements) + ";"

    def _generate_relationships_cypher(self, relationships: List[Dict[str, Any]]) -> str:
        """生成关系 Cypher 语句"""
        if not relationships:
            return ""
        
        cypher_statements = []
        
        for rel in relationships:
            source_id = rel.get('source_id')
            target_id = rel.get('target_id')
            rel_type = rel.get('type', 'RELATED_TO')
            
            # 构建关系属性
            props = []
            for key, value in rel.items():
                if key not in ['source_id', 'target_id', 'type'] and value is not None:
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "\\'")
                        props.append(f"{key}: '{escaped_value}'")
                    else:
                        props.append(f"{key}: {value}")
            
            props_str = "{" + ", ".join(props) + "}" if props else ""
            
            cypher = f"""MATCH (a {{id: '{source_id}'}}), (b {{id: '{target_id}'}})
CREATE (a)-[r:{rel_type} {props_str}]->(b)"""
            cypher_statements.append(cypher)
        
        return ";\n".join(cypher_statements) + ";"

    def generate_batch_import(self, neo4j_data: Dict[str, List[Dict[str, Any]]], batch_size: int = 1000) -> List[str]:
        """
        生成批量导入的 Cypher 语句
        
        Args:
            neo4j_data: Neo4j 格式的数据
            batch_size: 每批处理的节点/关系数量
            
        Returns:
            Cypher 语句列表，每个元素是一个批次
        """
        nodes = neo4j_data.get('nodes', [])
        relationships = neo4j_data.get('relationships', [])
        
        batch_statements = []
        
        # 分批处理节点
        for i in range(0, len(nodes), batch_size):
            batch_nodes = nodes[i:i + batch_size]
            batch_data = {'nodes': batch_nodes, 'relationships': []}
            nodes_cypher, _ = self.generate_cypher_import(batch_data)
            if nodes_cypher:
                batch_statements.append(nodes_cypher)
        
        # 分批处理关系
        for i in range(0, len(relationships), batch_size):
            batch_rels = relationships[i:i + batch_size]
            batch_data = {'nodes': [], 'relationships': batch_rels}
            _, rels_cypher = self.generate_cypher_import(batch_data)
            if rels_cypher:
                batch_statements.append(rels_cypher)
        
        return batch_statements

    def generate_merge_statements(self, neo4j_data: Dict[str, List[Dict[str, Any]]]) -> Tuple[str, str]:
        """
        生成使用 MERGE 的 Cypher 语句（避免重复创建）
        
        Returns:
            (nodes_merge, relationships_merge) 元组
        """
        nodes = neo4j_data.get('nodes', [])
        relationships = neo4j_data.get('relationships', [])
        
        # 生成节点 MERGE 语句
        nodes_merge = self._generate_nodes_merge(nodes)
        
        # 生成关系 MERGE 语句
        relationships_merge = self._generate_relationships_merge(relationships)
        
        return nodes_merge, relationships_merge

    def _generate_nodes_merge(self, nodes: List[Dict[str, Any]]) -> str:
        """生成节点 MERGE 语句"""
        if not nodes:
            return ""
        
        cypher_statements = []
        
        for node in nodes:
            label = node.get('label', 'ENTITY')
            node_id = node.get('id')
            
            if not node_id:
                continue
            
            # 使用 id 作为唯一标识进行 MERGE
            merge_cypher = f"MERGE (n:{label} {{id: '{node_id}'}})"
            
            # 设置其他属性
            set_props = []
            for key, value in node.items():
                if key not in ['label', 'id'] and value is not None:
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "\\'")
                        set_props.append(f"n.{key} = '{escaped_value}'")
                    else:
                        set_props.append(f"n.{key} = {value}")
            
            if set_props:
                merge_cypher += "\nSET " + ", ".join(set_props)
            
            cypher_statements.append(merge_cypher)
        
        return ";\n".join(cypher_statements) + ";"

    def _generate_relationships_merge(self, relationships: List[Dict[str, Any]]) -> str:
        """生成关系 MERGE 语句"""
        if not relationships:
            return ""
        
        cypher_statements = []
        
        for rel in relationships:
            source_id = rel.get('source_id')
            target_id = rel.get('target_id')
            rel_type = rel.get('type', 'RELATED_TO')
            
            if not all([source_id, target_id]):
                continue
            
            # MERGE 关系
            merge_cypher = f"""MATCH (a {{id: '{source_id}'}}), (b {{id: '{target_id}'}})
MERGE (a)-[r:{rel_type}]->(b)"""
            
            # 设置关系属性
            set_props = []
            for key, value in rel.items():
                if key not in ['source_id', 'target_id', 'type'] and value is not None:
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "\\'")
                        set_props.append(f"r.{key} = '{escaped_value}'")
                    else:
                        set_props.append(f"r.{key} = {value}")
            
            if set_props:
                merge_cypher += "\nSET " + ", ".join(set_props)
            
            cypher_statements.append(merge_cypher)
        
        return ";\n".join(cypher_statements) + ";"


# 创建全局实例
cypher_generator = CypherGenerator()