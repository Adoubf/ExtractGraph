#!/usr/bin/env python3
"""
节点可视化演示
展示如何使用 VisualNodes 类预览提取的节点和关系
"""

from src.core.visual_nodes import visual_nodes
from src.core.extractor import extractor


def demo_basic_visualization():
    """基础可视化演示"""
    print("=== 基础文本提取可视化演示 ===")
    
    # 示例文本
    text = """
    小明是一个勇敢的少年，他总是充满希望。
    小红是小明的好朋友，她很温柔善良。
    当小明遇到困难时，小红总是鼓励他，让他重新燃起斗志。
    他们之间有着深厚的友谊。
    """
    
    # 直接从文本提取并可视化
    html_path = visual_nodes.visualize_text_extraction(
        text=text,
        strategy="literary",  # 使用文学策略
        save_path="output/basic_demo.html"
    )
    
    print(f"可视化文件已保存: {html_path}")
    return html_path


def demo_neo4j_data_visualization():
    """从Neo4j数据可视化演示"""
    print("\n=== Neo4j数据可视化演示 ===")
    
    # 示例文本
    text = "张三是公司的经理，他对工作很负责。李四是张三的下属，他很尊敬张三。"
    
    # 先提取数据
    extraction_result = extractor.extract_for_neo4j(
        text=text,
        strategy="business"
    )
    
    # 显示统计信息
    stats = visual_nodes.generate_stats_summary(extraction_result['neo4j_data'])
    print("数据统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 可视化Neo4j数据
    html_path = visual_nodes.visualize_neo4j_data(
        neo4j_data=extraction_result['neo4j_data'],
        save_path="output/neo4j_demo.html",
        title="Business Text Extraction"
    )
    
    print(f"可视化文件已保存: {html_path}")
    return html_path


def demo_comparison_view():
    """对比视图演示"""
    print("\n=== 对比视图演示 ===")
    
    # 相同文本，不同策略
    text = """
    王老师是学校里最受欢迎的老师，学生们都很喜欢他。
    小华是王老师班上的学生，他对学习很有热情。
    当小华遇到学习困难时，王老师总是耐心地帮助他。
    """
    
    # 使用不同策略提取
    strategies = ["literary", "business"]
    data_list = []
    titles = []
    
    for strategy in strategies:
        try:
            result = extractor.extract_for_neo4j(text=text, strategy=strategy)
            data_list.append(result['neo4j_data'])
            titles.append(f"Strategy: {strategy}")
        except Exception as e:
            print(f"策略 {strategy} 提取失败: {e}")
            # 使用默认提取
            result = extractor.extract_for_neo4j(text=text)
            data_list.append(result['neo4j_data'])
            titles.append(f"Strategy: default (failed: {strategy})")
    
    # 创建对比视图
    if data_list:
        html_files = visual_nodes.create_comparison_view(
            data_list=data_list,
            titles=titles,
            save_dir="output/comparisons"
        )
        
        print(f"对比视图已保存: {len(html_files)} 个文件")
        for file in html_files:
            print(f"  - {file}")
    
    return html_files if data_list else []


def demo_custom_styles():
    """自定义样式演示"""
    print("\n=== 自定义样式演示 ===")
    
    # 创建自定义样式的可视化实例
    custom_visual = visual_nodes.__class__(
        width="1200px",
        height="800px",
        bgcolor="#f8f9fa",
        font_color="#333333"
    )
    
    # 自定义节点样式
    custom_visual.node_styles.update({
        'CHARACTER': {
            'color': '#28a745',  # 绿色
            'shape': 'star',
            'size': 30,
            'border_width': 3,
            'border_color': '#1e7e34'
        },
        'EMOTION': {
            'color': '#ffc107',  # 黄色
            'shape': 'diamond',
            'size': 25,
            'border_width': 2,
            'border_color': '#e0a800'
        }
    })
    
    # 自定义关系样式
    custom_visual.edge_styles.update({
        'RELATED_TO': {'color': '#6f42c1', 'width': 4},
        'FEELS': {'color': '#fd7e14', 'width': 5}
    })
    
    # 示例文本
    text = "小李很开心，因为他通过了考试。小王为小李感到高兴。"
    
    # 使用自定义样式可视化
    html_path = custom_visual.visualize_text_extraction(
        text=text,
        save_path="output/custom_style_demo.html"
    )
    
    print(f"自定义样式可视化已保存: {html_path}")
    return html_path


def main():
    """主演示函数"""
    print("节点可视化功能演示")
    print("=" * 50)
    
    # 确保输出目录存在
    import os
    os.makedirs("output", exist_ok=True)
    os.makedirs("output/comparisons", exist_ok=True)
    
    try:
        # 运行各种演示
        demo_basic_visualization()
        demo_neo4j_data_visualization()
        demo_comparison_view()
        demo_custom_styles()
        
        print("\n" + "=" * 50)
        print("所有演示完成！")
        print("请查看 output/ 目录中的HTML文件")
        print("\n使用方法:")
        print("1. 在浏览器中打开HTML文件查看可视化结果")
        print("2. 鼠标悬停在节点上查看详细信息")
        print("3. 拖拽节点调整布局")
        print("4. 点击节点高亮相关连接")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()