#!/usr/bin/env python3
"""
测试 Neo4j 格式化功能
"""

import json
from src.core.extractor import extractor
from src.utils.text_format import text_formatter
from src.core.cypher_generate import cypher_generator


def test_neo4j_formatting():
    """测试完整的提取和格式化流程"""
    
    # 测试文本
    input_text = (
        "ROMEO. It is my lady; O, it is my love! "
        "O, that she knew she were! JULIET appears at a window."
    )
    
    print("=" * 80)
    print("测试文本:")
    print(f'"{input_text}"')
    print("=" * 80)
    
    # 1. 执行抽取
    print("\n1. 执行 langextract 抽取...")
    extraction_result = extractor.extract_info(input_text)
    
    print("\n原始抽取结果:")
    print(json.dumps(extraction_result, indent=2, ensure_ascii=False))
    
    # 2. 转换为 Neo4j 格式
    print("\n" + "=" * 80)
    print("2. 转换为 Neo4j 格式...")
    neo4j_data = text_formatter.format_for_neo4j(extraction_result)
    
    print("\nNeo4j 节点:")
    for i, node in enumerate(neo4j_data['nodes'], 1):
        print(f"  节点 {i}: {json.dumps(node, indent=4, ensure_ascii=False)}")
    
    print(f"\nNeo4j 关系:")
    for i, rel in enumerate(neo4j_data['relationships'], 1):
        print(f"  关系 {i}: {json.dumps(rel, indent=4, ensure_ascii=False)}")
    
    # 3. 生成 Cypher 导入语句
    print("\n" + "=" * 80)
    print("3. 生成 Cypher 导入语句...")
    nodes_cypher, relationships_cypher = cypher_generator.generate_cypher_import(neo4j_data)
    
    print("\n节点创建语句:")
    print(nodes_cypher)
    
    print("\n关系创建语句:")
    print(relationships_cypher)
    
    # 4. 测试 MERGE 语句生成
    print("\n" + "=" * 80)
    print("4. 生成 MERGE 语句（避免重复）...")
    nodes_merge, relationships_merge = cypher_generator.generate_merge_statements(neo4j_data)
    
    print("\n节点 MERGE 语句:")
    print(nodes_merge)
    
    print("\n关系 MERGE 语句:")
    print(relationships_merge)
    
    print("\n" + "=" * 80)
    print("测试完成!")


if __name__ == "__main__":
    test_neo4j_formatting()