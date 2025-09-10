from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from pyvis.network import Network
from datetime import datetime

from src.core.extractor import extractor
from src.utils.logging import setup_logging

logger = setup_logging()


class VisualNodes:
    """
    节点可视化类 - 用于预览提取的节点和关系
    支持生成交互式HTML文件，便于检查导入Neo4j前的数据质量
    """
    
    def __init__(self, 
                 width: str = "100%", 
                 height: str = "600px",
                 bgcolor: str = "#ffffff",
                 font_color: Union[str, bool] = "#000000"):
        """
        初始化可视化配置
        
        Args:
            width: 网络图宽度
            height: 网络图高度 
            bgcolor: 背景颜色
            font_color: 字体颜色 (str) 或 False (不设置)
        """
        self.width = width
        self.height = height
        self.bgcolor = bgcolor
        self.font_color = font_color
        
        # 节点样式配置
        self.node_styles = {
            'CHARACTER': {
                'color': '#3498db',  # 蓝色
                'shape': 'dot',
                'size': 25,
                'border_width': 2,
                'border_color': '#2980b9'
            },
            'EMOTION': {
                'color': '#e74c3c',  # 红色
                'shape': 'triangle',
                'size': 20,
                'border_width': 2,
                'border_color': '#c0392b'
            },
            'THEME': {
                'color': '#9b59b6',  # 紫色
                'shape': 'square',
                'size': 22,
                'border_width': 2,
                'border_color': '#8e44ad'
            },
            'DEFAULT': {
                'color': '#95a5a6',  # 灰色
                'shape': 'dot',
                'size': 15,
                'border_width': 1,
                'border_color': '#7f8c8d'
            }
        }
        
        # 关系样式配置
        self.edge_styles = {
            'RELATED_TO': {'color': '#34495e', 'width': 2},
            'FEELS': {'color': '#e67e22', 'width': 3},
            'INTERACTS_WITH': {'color': '#9b59b6', 'width': 2},
            'DEFAULT': {'color': '#bdc3c7', 'width': 1}
        }
    
    def visualize_text_extraction(self, 
                                  text: str,
                                  strategy: Optional[str] = None,
                                  save_path: Optional[str] = None,
                                  show_in_notebook: bool = False,
                                  **kwargs) -> str:
        """
        直接从文本提取并可视化结果
        
        Args:
            text: 要提取的文本
            strategy: 提取策略名称
            save_path: HTML文件保存路径（可选）
            show_in_notebook: 是否在Jupyter notebook中显示
            **kwargs: 传递给提取器的其他参数
            
        Returns:
            生成的HTML文件路径
        """
        
        # 执行提取
        extraction_result = extractor.extract_for_neo4j(
            text=text, 
            strategy=strategy, 
            **kwargs
        )
        
        # 可视化Neo4j数据
        return self.visualize_neo4j_data(
            neo4j_data=extraction_result['neo4j_data'],
            save_path=save_path,
            show_in_notebook=show_in_notebook,
            title=f"Text Extraction Visualization - {strategy or 'default'}"
        )
    
    def visualize_neo4j_data(self, 
                             neo4j_data: Dict[str, List[Dict[str, Any]]],
                             save_path: Optional[str] = None,
                             show_in_notebook: bool = False,
                             title: str = "Node Visualization") -> str:
        """
        从Neo4j格式数据生成可视化
        
        Args:
            neo4j_data: 包含nodes和relationships的字典
            save_path: HTML文件保存路径（可选）
            show_in_notebook: 是否在Jupyter notebook中显示
            title: 可视化标题
            
        Returns:
            生成的HTML文件路径
        """
        
        # 创建网络图
        net = Network(
            width=self.width,
            height=self.height,
            bgcolor=self.bgcolor,
            font_color=self.font_color,
            directed=True
        )
        
        # 设置物理布局
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "stabilization": {"iterations": 100},
            "barnesHut": {
              "gravitationalConstant": -8000,
              "centralGravity": 0.3,
              "springLength": 95,
              "springConstant": 0.04,
              "damping": 0.09
            }
          },
          "interaction": {
            "hover": true,
            "hoverConnectedEdges": true,
            "selectConnectedEdges": false
          }
        }
        """)
        
        # 添加节点
        nodes = neo4j_data.get('nodes', [])
        relationships = neo4j_data.get('relationships', [])
        
        self._add_nodes_to_network(net, nodes)
        self._add_relationships_to_network(net, relationships)
        
        # 设置标题
        net.heading = title
        
        # 生成保存路径
        if not save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"visualization_{timestamp}.html"
        
        # 确保目录存在
        save_dir = Path(save_path).parent
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存HTML文件
        net.save_graph(save_path)
        
        # 在notebook中显示
        if show_in_notebook:
            try:
                from IPython.display import HTML, display
                display(HTML(save_path))
            except ImportError:
                logger.debug("IPython not available, skipping notebook display")
        
        logger.info(f"Visualization saved to: {save_path}")
        logger.info(f"Nodes: {len(nodes)}, Relationships: {len(relationships)}")
        
        return save_path
    
    def _add_nodes_to_network(self, net: Network, nodes: List[Dict[str, Any]]):
        """向网络图添加节点"""
        for node in nodes:
            node_id = node.get('id', '')
            label = node.get('label', 'UNKNOWN')
            text = node.get('text', '')
            
            # 获取节点样式
            style = self.node_styles.get(label, self.node_styles['DEFAULT'])
            
            # 构建hover信息
            hover_info = self._build_node_hover_info(node)
            
            # 节点标题（显示在图上）
            display_title = text[:20] + "..." if len(text) > 20 else text
            
            # 添加节点
            net.add_node(
                node_id,
                label=display_title,
                title=hover_info,
                color=style['color'],
                shape=style['shape'],
                size=style['size'],
                borderWidth=style['border_width'],
                borderWidthSelected=style['border_width'] + 1,
                chosen=True
            )
    
    def _add_relationships_to_network(self, net: Network, relationships: List[Dict[str, Any]]):
        """向网络图添加关系边"""
        existing_nodes = set(net.get_nodes())
        
        for rel in relationships:
            source_id = rel.get('source_id', '')
            target_id = rel.get('target_id', '')
            rel_type = rel.get('type', 'DEFAULT')
            
            # 检查节点是否存在，如果不存在则跳过这个关系
            if source_id not in existing_nodes or target_id not in existing_nodes:
                print(f"Warning: Skipping relationship {rel_type} - missing nodes: source={source_id in existing_nodes}, target={target_id in existing_nodes}")
                continue
            
            # 获取边样式
            style = self.edge_styles.get(rel_type, self.edge_styles['DEFAULT'])
            
            # 构建hover信息
            hover_info = self._build_relationship_hover_info(rel)
            
            # 添加边
            net.add_edge(
                source_id,
                target_id,
                title=hover_info,
                label=rel_type,
                color=style['color'],
                width=style['width'],
                arrows={'to': {'enabled': True, 'scaleFactor': 1.2}}
            )
    
    def _build_node_hover_info(self, node: Dict[str, Any]) -> str:
        """构建节点的hover信息"""
        info_lines = []
        
        # 基础信息
        info_lines.append(f"<b>ID:</b> {node.get('id', 'N/A')}")
        info_lines.append(f"<b>Label:</b> {node.get('label', 'N/A')}")
        info_lines.append(f"<b>Text:</b> {node.get('text', 'N/A')}")
        
        # 位置信息
        if node.get('start_pos') is not None:
            info_lines.append(f"<b>Position:</b> {node.get('start_pos')}-{node.get('end_pos')}")
        
        # 文档信息
        if node.get('document_id'):
            info_lines.append(f"<b>Document:</b> {node.get('document_id')}")
        
        # 类型特定属性
        label = node.get('label', '')
        if label == 'CHARACTER':
            if node.get('role'):
                info_lines.append(f"<b>Role:</b> {node.get('role')}")
            if node.get('alias'):
                info_lines.append(f"<b>Alias:</b> {node.get('alias')}")
            if node.get('title'):
                info_lines.append(f"<b>Title:</b> {node.get('title')}")
        elif label == 'EMOTION':
            if node.get('feeling'):
                info_lines.append(f"<b>Feeling:</b> {node.get('feeling')}")
            if node.get('category'):
                info_lines.append(f"<b>Category:</b> {node.get('category')}")
        else:
            # 对于其他类型的节点，显示所有额外属性
            excluded_keys = {'id', 'label', 'text', 'normalized_text', 'document_id', 'start_pos', 'end_pos', 'extraction_index', 'alignment_status'}
            for key, value in node.items():
                if key not in excluded_keys and value is not None:
                    info_lines.append(f"<b>{key.title()}:</b> {value}")
        
        return "<br>".join(info_lines)
    
    def _build_relationship_hover_info(self, rel: Dict[str, Any]) -> str:
        """构建关系的hover信息"""
        info_lines = []
        
        info_lines.append(f"<b>Type:</b> {rel.get('type', 'N/A')}")
        info_lines.append(f"<b>Trigger:</b> {rel.get('trigger_text', 'N/A')}")
        info_lines.append(f"<b>From:</b> {rel.get('head_text', 'N/A')} ({rel.get('head_class', 'N/A')})")
        info_lines.append(f"<b>To:</b> {rel.get('tail_text', 'N/A')} ({rel.get('tail_class', 'N/A')})")
        
        # 位置信息
        if rel.get('start_pos') is not None:
            info_lines.append(f"<b>Position:</b> {rel.get('start_pos')}-{rel.get('end_pos')}")
        
        # 文档信息
        if rel.get('document_id'):
            info_lines.append(f"<b>Document:</b> {rel.get('document_id')}")
        
        return "<br>".join(info_lines)
    
    def generate_stats_summary(self, neo4j_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        生成数据统计摘要
        
        Args:
            neo4j_data: Neo4j格式数据
            
        Returns:
            统计信息字典
        """
        nodes = neo4j_data.get('nodes', [])
        relationships = neo4j_data.get('relationships', [])
        
        # 节点统计
        node_counts = {}
        for node in nodes:
            label = node.get('label', 'UNKNOWN')
            node_counts[label] = node_counts.get(label, 0) + 1
        
        # 关系统计
        rel_counts = {}
        for rel in relationships:
            rel_type = rel.get('type', 'UNKNOWN')
            rel_counts[rel_type] = rel_counts.get(rel_type, 0) + 1
        
        return {
            'total_nodes': len(nodes),
            'total_relationships': len(relationships),
            'node_types': node_counts,
            'relationship_types': rel_counts,
            'unique_documents': len(set(node.get('document_id', '') for node in nodes if node.get('document_id')))
        }
    
    def create_comparison_view(self, 
                               data_list: List[Dict[str, Any]], 
                               titles: List[str],
                               save_dir: str = "comparisons") -> List[str]:
        """
        创建多个数据的对比视图
        
        Args:
            data_list: Neo4j数据列表
            titles: 对应的标题列表
            save_dir: 保存目录
            
        Returns:
            生成的HTML文件路径列表
        """
        if len(data_list) != len(titles):
            raise ValueError("data_list and titles must have the same length")
        
        # 创建保存目录
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)
        
        html_files = []
        
        for i, (data, title) in enumerate(zip(data_list, titles)):
            filename = f"{save_dir}/comparison_{i+1}_{title.replace(' ', '_')}.html"
            html_file = self.visualize_neo4j_data(
                neo4j_data=data,
                save_path=filename,
                title=f"Comparison {i+1}: {title}"
            )
            html_files.append(html_file)
        
        # 生成统计对比
        stats_comparison = []
        for data, title in zip(data_list, titles):
            stats = self.generate_stats_summary(data)
            stats['title'] = title
            stats_comparison.append(stats)
        
        # 保存统计对比
        stats_file = save_path / "comparison_stats.txt"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("Data Comparison Statistics\n")
            f.write("=" * 50 + "\n\n")
            
            for stats in stats_comparison:
                f.write(f"Title: {stats['title']}\n")
                f.write(f"Total Nodes: {stats['total_nodes']}\n")
                f.write(f"Total Relationships: {stats['total_relationships']}\n")
                f.write(f"Node Types: {stats['node_types']}\n")
                f.write(f"Relationship Types: {stats['relationship_types']}\n")
                f.write(f"Unique Documents: {stats['unique_documents']}\n")
                f.write("-" * 30 + "\n")
        
        logger.info(f"Comparison views saved to: {save_dir}/")
        logger.info(f"Statistics saved to: {stats_file}")
        
        return html_files


# 创建全局实例
visual_nodes = VisualNodes()