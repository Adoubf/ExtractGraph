# 🕸️ ExtractGraph

<div align="center">

**English | [中文](README_zh.md)**

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Built with Love](https://img.shields.io/badge/Built%20with-❤️-red.svg)](https://github.com/Adoubf/extractGraph)

**A powerful, configurable text extraction system for building knowledge graphs**

*Built on top of [langextract](https://github.com/google/langextract) with advanced configuration management and visualization capabilities*

[🚀 Quick Start](#quick-start) • [📖 Documentation](#documentation) • [🎯 Examples](#examples) • [🤝 Contributing](#contributing)

</div>

---

## ✨ Features

### 🎛️ **Highly Configurable Extraction**
- **Strategy-based extraction** with YAML configuration files
- **Multi-dimensional granularity control** (breadth, depth, confidence, context scope)
- **Dynamic prompt generation** using Jinja2 templates
- **Few-shot learning** with customizable examples

### 🎨 **Interactive Visualization**
- **Real-time node visualization** with pyvis integration
- **Pre-import data quality checks** before Neo4j insertion
- **Multi-strategy comparison views** for analysis
- **Customizable styling** for different node types

### 🗄️ **Database Integration**
- **Neo4j-ready data formatting** with automatic Cypher generation
- **Flexible schema support** for various entity types
- **Relationship mapping** with configurable properties
- **Batch import capabilities** with MERGE statements

### 🔧 **Developer-Friendly**
- **Type-safe configuration** with Pydantic models
- **Comprehensive logging** and debugging support
- **Extensible architecture** for custom strategies
- **Rich examples** and documentation

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ 
- OpenAI-compatible API (OpenAI, Azure OpenAI, local models, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/Adoubf/extractGraph.git
cd extractGraph

# Install with uv (recommended)
uv sync

# Or use pip
pip install -e .
```

### Basic Setup

1. **Configure your API credentials:**
```bash
cp .env.example .env
# Edit .env with your API settings
```

2. **Run a quick extraction:**
```python
from src.core.extractor import extractor

text = "Alice is a data scientist at TechCorp. She feels excited about the new AI project."

# Extract with default strategy
result = extractor.extract_for_neo4j(text)
print(f"Found {len(result['neo4j_data']['nodes'])} nodes and {len(result['neo4j_data']['relationships'])} relationships")
```

3. **Visualize the results:**
```python
from src.core.visual_nodes import visual_nodes

# Generate interactive visualization
html_path = visual_nodes.visualize_text_extraction(
    text=text,
    strategy="literary",
    save_path="output/demo.html"
)
# Open the HTML file in your browser!
```

---

## 🏗️ Architecture

```
extractGraph/
├── 🎛️ Strategy Layer      # YAML-based extraction strategies
├── 🔧 Configuration Layer # Dynamic prompt generation with Jinja2  
├── 📊 Granularity Layer   # Multi-dimensional extraction control
├── 🎨 Visualization Layer # Interactive node preview and analysis
└── 🗄️ Database Layer      # Neo4j integration with Cypher generation
```

### Core Components

| Component | Description | Key Features |
|-----------|-------------|--------------|
| **ConfigurableExtractor** | Main extraction engine | Strategy management, dynamic prompting |
| **VisualNodes** | Visualization engine | Interactive graphs, comparison views |
| **StrategyManager** | Configuration management | YAML loading, custom strategy creation |
| **CypherGenerator** | Database integration | CREATE/MERGE statement generation |

---

## 📖 Documentation

### 🎯 Extraction Strategies

Create custom extraction strategies with YAML configuration:

```yaml
# strategies/custom_strategy.yaml
name: "scientific_papers"
description: "Extract entities from scientific literature"
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

### 🎨 Visualization Options

```python
# Basic visualization
visual_nodes.visualize_text_extraction(text, strategy="scientific")

# Custom styling
custom_visual = VisualNodes(
    width="1200px", 
    height="800px",
    bgcolor="#f8f9fa"
)

# Comparison analysis  
visual_nodes.create_comparison_view(
    data_list=[result1, result2],
    titles=["Strategy A", "Strategy B"]
)
```

### 🗄️ Neo4j Integration

```python
# Generate Cypher statements
result = extractor.extract_for_neo4j_merge(text, strategy="business")

# Get CREATE statements
nodes_cypher = result['merge_statements']['nodes']
relationships_cypher = result['merge_statements']['relationships']

# Execute in Neo4j
# driver.session().run(nodes_cypher)
# driver.session().run(relationships_cypher)
```

---

## 🎯 Examples

### 📝 Text Analysis Pipeline

```python
from src.core.extractor import extractor
from src.core.visual_nodes import visual_nodes

# Multi-step analysis pipeline
text = """
Dr. Sarah Chen, a machine learning researcher at Stanford University, 
published groundbreaking work on neural networks. She collaborates 
with Dr. Mike Johnson from MIT on deep learning applications.
"""

# 1. Extract with academic strategy
result = extractor.extract_for_neo4j(text, strategy="academic")

# 2. Visualize for quality check
visual_nodes.visualize_neo4j_data(
    result['neo4j_data'], 
    title="Academic Knowledge Graph"
)

# 3. Generate database import
cypher_statements = result['cypher_statements']
print("Ready for Neo4j import!")
```

### 🔍 Strategy Comparison

```python
# Compare different extraction approaches
strategies = ["literary", "business", "academic"]
results = []

for strategy in strategies:
    result = extractor.extract_for_neo4j(text, strategy=strategy)
    results.append(result['neo4j_data'])

# Generate comparison visualization
visual_nodes.create_comparison_view(
    data_list=results,
    titles=[f"Strategy: {s}" for s in strategies],
    save_dir="analysis/strategy_comparison"
)
```

### 🎛️ Custom Configuration

```python
# Create custom extraction with granular control
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

## 🛠️ Advanced Usage

### Custom Strategy Development

1. **Create strategy file:**
```yaml
# strategies/my_domain.yaml  
name: "my_domain"
entities: ["entity1", "entity2"]
relations: ["relation1"]
# ... configuration
```

2. **Load and use:**
```python
strategy = strategy_manager.load_strategy("my_domain")
result = extractor.extract(text, strategy="my_domain")
```

### Visualization Customization

```python
# Custom node styles
visual_nodes.node_styles.update({
    'RESEARCHER': {
        'color': '#e74c3c',
        'shape': 'star', 
        'size': 30
    }
})

# Custom relationship styles  
visual_nodes.edge_styles.update({
    'COLLABORATES_WITH': {
        'color': '#3498db',
        'width': 4
    }
})
```

---

## 📊 Performance & Scalability

- **Efficient processing:** Optimized for large documents with configurable chunking
- **Memory management:** Streaming processing for large datasets  
- **Parallel extraction:** Multi-strategy concurrent processing
- **Caching:** Built-in result caching for repeated analyses

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite:** `python -m pytest`
5. **Submit a pull request**

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/Adoubf/extractGraph.git
cd extractGraph
uv sync --dev

# Run tests
python -m pytest tests/

# Run examples
python -m code_examples.configurable_extraction_demo
python -m code_examples.visual_nodes_demo
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[langextract](https://github.com/aurelio-labs/langextract)** - The powerful extraction engine that powers this project
- **[pyvis](https://github.com/WestHealth/pyvis)** - Interactive network visualization
- **[Neo4j](https://neo4j.com/)** - Graph database platform
- **[Pydantic](https://pydantic.dev/)** - Data validation and settings management

---

## 📞 Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/Adoubf/extractGraph/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/Adoubf/extractGraph/discussions)
- 📧 **Email:** haoyue@coralera.org

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ by [Haoyue](https://github.com/Adoubf)

</div>