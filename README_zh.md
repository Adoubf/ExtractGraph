# 🕸️ ExtractGraph

<div align="center">

**[English](README.md) | 中文**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Built with Love](https://img.shields.io/badge/Built%20with-❤️-red.svg)](https://github.com/Adoubf/extractGraph)

**强大的、可配置的文本提取系统，用于构建知识图谱**

*基于 [langextract](https://github.com/google/langextract) 构建，具备先进的配置管理和可视化功能*

[🚀 快速开始](#快速开始) • [📖 文档](#文档) • [🎯 示例](#示例) • [🤝 贡献](#贡献)

</div>

---

## ✨ 特性

### 🎛️ **高度可配置的提取**
- **基于策略的提取**，使用 YAML 配置文件
- **多维度粒度控制**（广度、深度、置信度、上下文范围）
- **动态提示词生成**，使用 Jinja2 模板
- **少样本学习**，支持自定义示例

### 🎨 **交互式可视化**
- **实时节点可视化**，集成 pyvis
- **导入前数据质量检查**，在 Neo4j 插入前进行预览
- **多策略对比视图**，用于分析
- **可定制样式**，支持不同节点类型

### 🗄️ **数据库集成**
- **Neo4j 就绪的数据格式化**，自动生成 Cypher 语句
- **灵活的模式支持**，适用于各种实体类型
- **关系映射**，支持可配置属性
- **批量导入功能**，使用 MERGE 语句

### 🔧 **开发者友好**
- **类型安全配置**，使用 Pydantic 模型
- **全面的日志记录**和调试支持
- **可扩展架构**，支持自定义策略
- **丰富的示例**和文档

---

## 🚀 快速开始

### 前置条件

- Python 3.11+ 
- OpenAI 兼容 API（OpenAI、Azure OpenAI、本地模型等）

### 安装

```bash
# 克隆仓库
git clone https://github.com/Adoubf/extractGraph.git
cd extractGraph

# 使用 uv 安装（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 基础设置

1. **配置你的 API 凭据：**
```bash
cp .env.example .env
# 编辑 .env 文件设置你的 API 配置
```

2. **运行快速提取：**
```python
from src.core.extractor import extractor

text = "Alice 是 TechCorp 的数据科学家。她对新的 AI 项目感到兴奋。"

# 使用默认策略提取
result = extractor.extract_for_neo4j(text)
print(f"发现 {len(result['neo4j_data']['nodes'])} 个节点和 {len(result['neo4j_data']['relationships'])} 个关系")
```

3. **可视化结果：**
```python
from src.core.visual_nodes import visual_nodes

# 生成交互式可视化
html_path = visual_nodes.visualize_text_extraction(
    text=text,
    strategy="literary",
    save_path="output/demo.html"
)
# 在浏览器中打开 HTML 文件！
```

---

## 🏗️ 架构

```
extractGraph/
├── 🎛️ 策略层          # 基于 YAML 的提取策略
├── 🔧 配置层          # 使用 Jinja2 的动态提示词生成  
├── 📊 粒度层          # 多维度提取控制
├── 🎨 可视化层        # 交互式节点预览和分析
└── 🗄️ 数据库层        # Neo4j 集成与 Cypher 生成
```

### 核心组件

| 组件 | 描述 | 主要特性 |
|------|------|----------|
| **ConfigurableExtractor** | 主要提取引擎 | 策略管理、动态提示 |
| **VisualNodes** | 可视化引擎 | 交互式图表、对比视图 |
| **StrategyManager** | 配置管理 | YAML 加载、自定义策略创建 |
| **CypherGenerator** | 数据库集成 | CREATE/MERGE 语句生成 |

---

## 📖 文档

### 🎯 提取策略

使用 YAML 配置创建自定义提取策略：

```yaml
# strategies/custom_strategy.yaml
name: "scientific_papers"
description: "从科学文献中提取实体"
entities:
  - "researcher"
  - "institution" 
  - "concept"
  - "method"
relations:
  - "affiliated_with"
  - "researches"  
  - "cites"
granularity:
  breadth: "comprehensive"
  depth: "inferential"
  confidence: "high"
  context_scope: "document"
```

### 🎨 可视化选项

```python
# 基础可视化
visual_nodes.visualize_text_extraction(text, strategy="scientific")

# 自定义样式
custom_visual = VisualNodes(
    width="1200px", 
    height="800px",
    bgcolor="#f8f9fa"
)

# 对比分析  
visual_nodes.create_comparison_view(
    data_list=[result1, result2],
    titles=["策略 A", "策略 B"]
)
```

### 🗄️ Neo4j 集成

```python
# 生成 Cypher 语句
result = extractor.extract_for_neo4j_merge(text, strategy="business")

# 获取 CREATE 语句
nodes_cypher = result['merge_statements']['nodes']
relationships_cypher = result['merge_statements']['relationships']

# 在 Neo4j 中执行
# driver.session().run(nodes_cypher)
# driver.session().run(relationships_cypher)
```

---

## 🎯 示例

### 📝 文本分析流水线

```python
from src.core.extractor import extractor
from src.core.visual_nodes import visual_nodes

# 多步骤分析流水线
text = """
陈博士是斯坦福大学的机器学习研究员，
发表了关于神经网络的突破性工作。她与
来自 MIT 的约翰逊博士在深度学习应用方面合作。
"""

# 1. 使用学术策略提取
result = extractor.extract_for_neo4j(text, strategy="academic")

# 2. 可视化质量检查
visual_nodes.visualize_neo4j_data(
    result['neo4j_data'], 
    title="学术知识图谱"
)

# 3. 生成数据库导入
cypher_statements = result['cypher_statements']
print("准备导入 Neo4j！")
```

### 🔍 策略对比

```python
# 比较不同的提取方法
strategies = ["literary", "business", "academic"]
results = []

for strategy in strategies:
    result = extractor.extract_for_neo4j(text, strategy=strategy)
    results.append(result['neo4j_data'])

# 生成对比可视化
visual_nodes.create_comparison_view(
    data_list=results,
    titles=[f"策略: {s}" for s in strategies],
    save_dir="analysis/strategy_comparison"
)
```

### 🎛️ 自定义配置

```python
# 创建具有粒度控制的自定义提取
result = extractor.extract(
    text=text,
    entities=["person", "organization", "project"],
    relations=["works_at", "collaborates_with"],
    breadth="comprehensive",
    depth="inferential", 
    confidence="medium",
    context_scope="document"
)
```

---

## 🛠️ 高级用法

### 自定义策略开发

1. **创建策略文件：**
```yaml
# strategies/my_domain.yaml  
name: "my_domain"
entities: ["entity1", "entity2"]
relations: ["relation1"]
# ... 配置
```

2. **加载并使用：**
```python
strategy = strategy_manager.load_strategy("my_domain")
result = extractor.extract(text, strategy="my_domain")
```

### 可视化自定义

```python
# 自定义节点样式
visual_nodes.node_styles.update({
    'RESEARCHER': {
        'color': '#e74c3c',
        'shape': 'star', 
        'size': 30
    }
})

# 自定义关系样式  
visual_nodes.edge_styles.update({
    'COLLABORATES_WITH': {
        'color': '#3498db',
        'width': 4
    }
})
```

---

## 📊 性能与可扩展性

- **高效处理：** 针对大文档优化，支持可配置分块
- **内存管理：** 大数据集流式处理  
- **并行提取：** 多策略并发处理
- **缓存：** 内置结果缓存，用于重复分析

---

## 🤝 贡献

我们欢迎贡献！以下是开始的方式：

1. **Fork 仓库**
2. **创建功能分支：** `git checkout -b feature/amazing-feature`
3. **进行更改**并添加测试
4. **运行测试套件：** `python -m pytest`
5. **提交拉取请求**

### 开发环境设置

```bash
# 克隆并设置开发环境
git clone https://github.com/Adoubf/extractGraph.git
cd extractGraph
uv sync --dev

# 运行测试
python -m pytest tests/

# 运行示例
python -m code_examples.configurable_extraction_demo
python -m code_examples.visual_nodes_demo
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- **[langextract](https://github.com/aurelio-labs/langextract)** - 为本项目提供强大提取引擎的核心库
- **[pyvis](https://github.com/WestHealth/pyvis)** - 交互式网络可视化
- **[Neo4j](https://neo4j.com/)** - 图数据库平台
- **[Pydantic](https://pydantic.dev/)** - 数据验证和设置管理

---

## 📞 支持

- 🐛 **问题反馈：** [GitHub Issues](https://github.com/Adoubf/extractGraph/issues)
- 💬 **讨论：** [GitHub Discussions](https://github.com/Adoubf/extractGraph/discussions)
- 📧 **邮箱：** haoyue@coralera.org

---

<div align="center">

**⭐ 如果这个仓库对你有帮助，请给它一个星标！**

用 ❤️ 制作，作者：[Haoyue](https://github.com/Adoubf)

</div>