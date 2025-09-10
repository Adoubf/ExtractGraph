from src.core.extractor import extractor

input_text = (
    "ROMEO. It is my lady; O, it is my love! "
    "O, that she knew she were! JULIET appears at a window."
)

print("=" * 80)
print("测试新的可配置文本抽取系统（完全基于langextract标准API）")
print("=" * 80)

# 测试可用策略
print("\n可用策略:")
available_strategies = extractor.get_available_strategies()
print(available_strategies)

# 测试标准提取（返回AnnotatedDocument）
print("\n1. 标准提取结果（langextract AnnotatedDocument）:")
try:
    result = extractor.extract(input_text, strategy="literary")
    print(f"类型: {type(result)}")
    print(f"提取数量: {len(result.extractions)} 个")
    
    # 显示前几个提取结果
    for i, extraction in enumerate(result.extractions[:3], 1):
        print(f"  {i}. {extraction.extraction_class}: '{extraction.extraction_text}'")
        if extraction.attributes:
            print(f"     属性: {extraction.attributes}")
except Exception as e:
    print(f"标准提取失败: {e}")

print("\n" + "=" * 80)

# 测试字典格式提取
print("\n2. 字典格式提取结果:")
try:
    dict_result = extractor.extract_to_dict(input_text, strategy="literary")
    print(f"提取数量: {len(dict_result.get('extractions', []))} 个")
    
    for extraction in dict_result.get('extractions', [])[:3]:
        print(f"  - {extraction['extraction_class']}: '{extraction['extraction_text']}'")
except Exception as e:
    print(f"字典格式提取失败: {e}")

print("\n" + "=" * 80)

# 测试自定义提取
print("\n3. 自定义提取测试:")
try:
    custom_result = extractor.extract(
        input_text,
        entities=["character", "emotion", "location"],
        relations=["appears_at", "expresses"],
        breadth="comprehensive",
        depth="semantic"
    )
    print(f"自定义提取数量: {len(custom_result.extractions)} 个")
    
    for extraction in custom_result.extractions[:3]:
        print(f"  - {extraction.extraction_class}: '{extraction.extraction_text}'")
except Exception as e:
    print(f"自定义提取失败: {e}")

print("\n" + "=" * 80)

# 测试Neo4j集成
print("\n4. Neo4j集成测试:")
try:
    neo4j_result = extractor.extract_for_neo4j(input_text, strategy="literary")
    
    nodes_count = len(neo4j_result['neo4j_data']['nodes'])
    relations_count = len(neo4j_result['neo4j_data']['relationships'])
    
    print(f"Neo4j节点: {nodes_count} 个")
    print(f"Neo4j关系: {relations_count} 个")
    
    if nodes_count > 0:
        first_node = neo4j_result['neo4j_data']['nodes'][0]
        print(f"示例节点: {first_node['label']} - {first_node.get('text', 'N/A')}")
        
except Exception as e:
    print(f"Neo4j集成失败: {e}")

print("\n" + "=" * 80)
print("测试完成！新系统完全基于langextract标准API。")
print("=" * 80)