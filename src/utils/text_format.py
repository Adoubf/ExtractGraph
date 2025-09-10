import hashlib
from typing import Dict, List, Any


class TEXT_FORMAT:
    """
    规整 langextract 抽取结果，方便后续入库
    """
    
    # ==== 基础工具 ====
    def norm_text(self, s: str) -> str:
        return " ".join(s.strip().lower().split())

    def make_uid(self, cls: str, text: str) -> str:
        h = hashlib.md5(f"{cls}:{self.norm_text(text)}".encode()).hexdigest()[:16]
        return f"{cls}_{h}"

    def class_to_label(self, cls: str) -> str:
        # 作为 Neo4j 标签（必须字母开头）
        return cls.strip().upper()

    # ==== Neo4j 格式化方法 ====
    def format_for_neo4j(self, extraction_result: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        将 langextract 的抽取结果转换为 Neo4j 导入格式
        
        Args:
            extraction_result: langextract 返回的结果字典
            
        Returns:
            包含 nodes 和 relationships 的字典，用于 Neo4j 导入
        """
        extractions = extraction_result.get('extractions', [])
        document_id = extraction_result.get('document_id', 'unknown_doc')
        source_text = extraction_result.get('text', '')
        
        nodes = []
        relationships = []
        
        # 处理实体节点 (character, emotion)
        entity_nodes = self._extract_entity_nodes(extractions, document_id, source_text)
        nodes.extend(entity_nodes)
        
        # 处理关系
        relation_edges = self._extract_relationships(extractions, document_id, source_text)
        relationships.extend(relation_edges)
        
        return {
            'nodes': nodes,
            'relationships': relationships
        }

    def _extract_entity_nodes(self, extractions: List[Dict], document_id: str, source_text: str) -> List[Dict[str, Any]]:
        """提取实体节点 (所有非关系类型)"""
        nodes = []
        
        for extraction in extractions:
            extraction_class = extraction.get('extraction_class', '')
            
            # 处理所有实体类型，跳过关系
            if extraction_class and extraction_class != 'relationship':
                node = self._create_entity_node(extraction, document_id, source_text)
                nodes.append(node)
        
        return nodes

    def _create_entity_node(self, extraction: Dict, document_id: str, source_text: str) -> Dict[str, Any]:
        """创建单个实体节点"""
        extraction_class = extraction.get('extraction_class', '')
        extraction_text = extraction.get('extraction_text', '')
        attributes = extraction.get('attributes') or {}
        char_interval = extraction.get('char_interval') or {}
        
        # 检查attributes是否为有效字典
        if not isinstance(attributes, dict):
            attributes = {}
        
        # 生成唯一ID
        node_id = self.make_uid(extraction_class, extraction_text)
        
        # 基础节点属性
        node = {
            'id': node_id,
            'label': self.class_to_label(extraction_class),
            'text': extraction_text,
            'normalized_text': self.norm_text(extraction_text),
            'document_id': document_id,
            'start_pos': char_interval.get('start_pos') if char_interval else None,
            'end_pos': char_interval.get('end_pos') if char_interval else None,
            'extraction_index': extraction.get('extraction_index'),
            'alignment_status': extraction.get('alignment_status')
        }
        
        # 添加类型特定的属性
        if extraction_class == 'character':
            node.update({
                'role': attributes.get('role'),
                'alias': attributes.get('alias'),
                'title': attributes.get('title')
            })
        elif extraction_class == 'emotion':
            node.update({
                'feeling': attributes.get('feeling'),
                'category': attributes.get('category')
            })
        else:
            # 对于其他类型的节点，添加所有non-None的属性
            if attributes:
                for key, value in attributes.items():
                    if value is not None:
                        node[key] = value
        
        # 移除 None 值
        return {k: v for k, v in node.items() if v is not None}

    def _extract_relationships(self, extractions: List[Dict], document_id: str, source_text: str) -> List[Dict[str, Any]]:
        """提取关系边"""
        relationships = []
        
        for extraction in extractions:
            extraction_class = extraction.get('extraction_class', '')
            
            if extraction_class == 'relationship':
                relationship = self._create_relationship(extraction, document_id, source_text)
                if relationship:
                    relationships.append(relationship)
        
        return relationships

    def _create_relationship(self, extraction: Dict, document_id: str, source_text: str) -> Dict[str, Any]:
        """创建单个关系"""
        attributes = extraction.get('attributes') or {}
        extraction_text = extraction.get('extraction_text', '')
        char_interval = extraction.get('char_interval') or {}
        
        # 检查attributes是否为有效字典
        if not isinstance(attributes, dict):
            return {}
        
        # 获取关系的头尾实体信息
        head_text = attributes.get('head_text')
        head_class = attributes.get('head_class')
        tail_text = attributes.get('tail_text')
        tail_class = attributes.get('tail_class')
        relation_type = attributes.get('relation_type', 'RELATED_TO')
        
        if not all([head_text, head_class, tail_text, tail_class]):
            return {}
        
        # 生成头尾节点的ID
        head_id = self.make_uid(head_class, head_text)
        tail_id = self.make_uid(tail_class, tail_text)
        
        relationship = {
            'source_id': head_id,
            'target_id': tail_id,
            'type': relation_type.upper(),
            'trigger_text': extraction_text,
            'document_id': document_id,
            'start_pos': char_interval.get('start_pos') if char_interval else None,
            'end_pos': char_interval.get('end_pos') if char_interval else None,
            'extraction_index': extraction.get('extraction_index'),
            'head_text': head_text,
            'head_class': head_class,
            'tail_text': tail_text,
            'tail_class': tail_class
        }
        
        # 移除 None 值
        return {k: v for k, v in relationship.items() if v is not None}




# 创建全局实例
text_formatter = TEXT_FORMAT()


