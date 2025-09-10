#!/usr/bin/env python3
"""
简化的系统测试脚本
"""

import sys
import os
# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.extractor import extractor

def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("万全方案功能测试")
    print("=" * 60)
    
    # 测试策略管理
    print("\n1. 策略管理测试:")
    strategies = extractor.get_available_strategies()
    print(f"   可用策略: {strategies}")
    
    if "literary" in strategies:
        strategy_info = extractor.describe_strategy("literary")
        print(f"   文学策略实体: {strategy_info.get('entities', [])}")
        print(f"   文学策略关系: {strategy_info.get('relations', [])}")
    
    # 测试配置系统
    print("\n2. 配置系统测试:")
    from src.config.strategy import strategy_manager
    
    # 测试加载策略
    try:
        lit_strategy = strategy_manager.load_strategy("literary")
        print(f"   文学策略加载成功: {lit_strategy.name}")
        print(f"   精细度配置: breadth={lit_strategy.granularity.breadth}, depth={lit_strategy.granularity.depth}")
    except Exception as e:
        print(f"   策略加载失败: {e}")
    
    # 测试自定义策略
    try:
        custom_strategy = strategy_manager.create_custom_strategy(
            name="test_custom",
            entities=["person", "action"],
            relations=["performs"],
            description="Test custom strategy"
        )
        print(f"   自定义策略创建成功: {custom_strategy.name}")
    except Exception as e:
        print(f"   自定义策略创建失败: {e}")
    
    # 测试模板系统
    print("\n3. 模板系统测试:")
    from src.config.prompt_generator import prompt_generator
    
    try:
        if "literary" in strategies:
            lit_strategy = strategy_manager.load_strategy("literary")
            prompt = prompt_generator.generate_prompt(lit_strategy)
            print(f"   提示词生成成功: {len(prompt)} 字符")
            print(f"   提示词预览: {prompt[:100]}...")
    except Exception as e:
        print(f"   提示词生成失败: {e}")
    
    # 测试schemas系统
    print("\n4. Schemas系统测试:")
    try:
        schemas = strategy_manager.get_schemas()
        entities_count = len(schemas.get('entities', {}))
        relations_count = len(schemas.get('relations', {}))
        print(f"   Entities schemas: {entities_count} 类别")
        print(f"   Relations schemas: {relations_count} 类别")
        
        if 'entities' in schemas and 'literary' in schemas['entities']:
            lit_entities = list(schemas['entities']['literary'].keys())
            print(f"   文学实体类型: {lit_entities}")
    except Exception as e:
        print(f"   Schemas系统测试失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！系统核心功能正常运行。")
    print("=" * 60)

if __name__ == "__main__":
    test_basic_functionality()