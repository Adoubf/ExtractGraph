#!/usr/bin/env python3
"""
可配置提取系统使用示例
展示万全方案的各种使用场景和API接口
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.extractor import extractor
import json


def demo_basic_usage():
    """演示基本使用方式"""
    print("=" * 80)
    print("1. 基本使用示例")
    print("=" * 80)
    
    text = "ROMEO meets JULIET at the balcony. Their love transcends family hatred."
    
    # 最简单的使用方式
    result = extractor.extract(text)
    print("\n简单提取结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def demo_strategy_usage():
    """演示策略使用"""
    print("\n" + "=" * 80)
    print("2. 策略使用示例")
    print("=" * 80)
    
    # 查看可用策略
    strategies = extractor.get_available_strategies()
    print(f"\n可用策略: {strategies}")
    
    texts = {
        "literary": "HAMLET speaks to YORICK's skull, contemplating mortality and the nature of existence.",
        "business": "Apple Inc. announced a partnership with Microsoft Corporation to develop new cloud services.",
        "news": "President Biden met with European leaders to discuss climate change policies.",
        "academic": "Dr. Smith's research validates the hypothesis that machine learning improves prediction accuracy."
    }
    
    for strategy in strategies:
        if strategy in texts:
            print(f"\n使用 {strategy} 策略处理文本:")
            print(f"文本: {texts[strategy]}")
            
            try:
                result = extractor.extract(texts[strategy], strategy=strategy)
                
                # 显示提取的实体和关系
                extractions = result.get('document', {}).get('extractions', [])
                entities = [e for e in extractions if e['extraction_class'] in ['character', 'person', 'organization', 'researcher']]
                relations = [e for e in extractions if e['extraction_class'] in ['relationship', 'meets', 'partnership', 'researches']]
                
                print(f"提取的实体: {len(entities)} 个")
                for entity in entities[:3]:  # 显示前3个
                    print(f"  - {entity['extraction_text']} ({entity['extraction_class']})")
                
                print(f"提取的关系: {len(relations)} 个")
                for relation in relations[:2]:  # 显示前2个
                    print(f"  - {relation['extraction_text']} ({relation.get('attributes', {}).get('relation_type', 'unknown')})")
                    
            except Exception as e:
                print(f"策略 {strategy} 处理失败: {e}")


def demo_granularity_control():
    """演示精细度控制"""
    print("\n" + "=" * 80)
    print("3. 精细度控制示例")
    print("=" * 80)
    
    text = "In the moonlit garden, Romeo whispers sweet words to Juliet, expressing his deep love and devotion."
    
    granularity_levels = [
        {"breadth": "minimal", "depth": "surface", "description": "最小表面提取"},
        {"breadth": "standard", "depth": "semantic", "description": "标准语义提取"},
        {"breadth": "comprehensive", "depth": "inferential", "description": "全面推理提取"}
    ]
    
    for level in granularity_levels:
        print(f"\n{level['description']}:")
        print(f"配置: breadth={level['breadth']}, depth={level['depth']}")
        
        try:
            result = extractor.extract(
                text,
                strategy="literary",
                breadth=level['breadth'],
                depth=level['depth']
            )
            
            extractions = result.get('document', {}).get('extractions', [])
            print(f"提取数量: {len(extractions)} 个")
            
            for extraction in extractions[:3]:
                print(f"  - {extraction['extraction_text']} ({extraction['extraction_class']})")
                
        except Exception as e:
            print(f"精细度控制失败: {e}")


def demo_custom_extraction():
    """演示自定义提取"""
    print("\n" + "=" * 80)
    print("4. 自定义提取示例")
    print("=" * 80)
    
    text = "The brave knight rescued the princess from the dark castle, defeating the evil dragon."
    
    # 自定义实体和关系类型
    custom_entities = ["character", "location", "creature", "action"]
    custom_relations = ["rescues", "appears_at", "defeats", "protects"]
    
    print(f"自定义实体类型: {custom_entities}")
    print(f"自定义关系类型: {custom_relations}")
    print(f"处理文本: {text}")
    
    try:
        result = extractor.extract(
            text,
            entities=custom_entities,
            relations=custom_relations,
            breadth="comprehensive"
        )
        
        extractions = result.get('document', {}).get('extractions', [])
        print(f"\n提取结果 ({len(extractions)} 个):")
        
        for extraction in extractions:
            extraction_type = extraction['extraction_class']
            extraction_text = extraction['extraction_text']
            attributes = extraction.get('attributes', {})
            
            print(f"  - {extraction_text} ({extraction_type})")
            if attributes:
                print(f"    属性: {attributes}")
                
    except Exception as e:
        print(f"自定义提取失败: {e}")


def demo_neo4j_integration():
    """演示Neo4j集成"""
    print("\n" + "=" * 80)
    print("5. Neo4j集成示例")
    print("=" * 80)
    
    text = "Shakespeare wrote Romeo and Juliet. The play explores themes of love and tragedy."
    
    print(f"处理文本: {text}")
    
    try:
        # 提取并格式化为Neo4j
        result = extractor.extract_for_neo4j(
            text,
            strategy="literary",
            entities=["character", "person", "work", "theme"],
            relations=["writes", "explores", "contains"]
        )
        
        print("\nNeo4j节点:")
        for i, node in enumerate(result['neo4j_data']['nodes'], 1):
            print(f"  节点{i}: {node['label']} - {node['properties'].get('name', 'unnamed')}")
        
        print("\nNeo4j关系:")
        for i, rel in enumerate(result['neo4j_data']['relationships'], 1):
            print(f"  关系{i}: {rel['type']} - {rel['properties'].get('relation_type', 'unknown')}")
        
        print("\nCypher CREATE语句:")
        print("节点创建:")
        print(result['cypher_statements']['nodes'][:200] + "..." if len(result['cypher_statements']['nodes']) > 200 else result['cypher_statements']['nodes'])
        
    except Exception as e:
        print(f"Neo4j集成失败: {e}")


def demo_strategy_comparison():
    """演示不同策略的对比"""
    print("\n" + "=" * 80)
    print("6. 策略对比示例")
    print("=" * 80)
    
    text = "Dr. Johnson published a research paper on artificial intelligence applications in healthcare."
    
    strategies_to_compare = ["business", "academic", "news"]
    available_strategies = extractor.get_available_strategies()
    
    print(f"对比文本: {text}")
    
    for strategy in strategies_to_compare:
        if strategy in available_strategies:
            print(f"\n使用 {strategy} 策略:")
            
            try:
                # 获取策略描述
                strategy_info = extractor.describe_strategy(strategy)
                print(f"  策略描述: {strategy_info.get('description', 'N/A')}")
                print(f"  支持实体: {strategy_info.get('entities', [])}")
                
                # 执行提取
                result = extractor.extract(text, strategy=strategy)
                extractions = result.get('document', {}).get('extractions', [])
                
                print(f"  提取结果: {len(extractions)} 个")
                for extraction in extractions[:3]:
                    print(f"    - {extraction['extraction_text']} ({extraction['extraction_class']})")
                    
            except Exception as e:
                print(f"  策略 {strategy} 失败: {e}")


def main():
    """运行所有演示"""
    print("可配置提取系统演示")
    print("展示万全方案的各种功能和使用场景")
    
    try:
        demo_basic_usage()
        demo_strategy_usage()
        demo_granularity_control()
        demo_custom_extraction()
        demo_neo4j_integration()
        demo_strategy_comparison()
        
        print("\n" + "=" * 80)
        print("演示完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()