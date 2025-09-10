"""
提取策略管理器
负责加载和管理不同的提取策略配置
"""

import yaml
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class GranularityConfig:
    """精细度控制配置"""
    breadth: str = "standard"      # minimal, standard, comprehensive
    depth: str = "semantic"        # surface, semantic, inferential  
    confidence: str = "medium"     # high, medium, all
    context_scope: str = "paragraph"  # local, paragraph, document


@dataclass
class ExtractionConfig:
    """提取策略配置"""
    name: str
    description: str
    version: str
    entities: List[str]
    relations: List[str]
    granularity: GranularityConfig
    extraction_rules: Dict[str, Any]
    prompt_template: str
    examples: Dict[str, Any]
    post_processing: Dict[str, Any]
    special_settings: Dict[str, Any]


class ExtractionStrategy:
    """提取策略管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__))
        
        self.config_dir = Path(config_dir)
        self.strategies_dir = self.config_dir / "strategies"
        self.schemas_dir = self.config_dir / "schemas"
        # examples目录已删除，现在使用default_examples.py
        self.examples_dir = None
        self.templates_dir = self.config_dir / "templates"
        
        # 缓存加载的配置
        self._strategies_cache = {}
        self._schemas_cache = {}
        
        # 加载schemas
        self._load_schemas()
    
    def _load_schemas(self):
        """加载实体和关系定义schemas"""
        try:
            # 加载实体定义
            entities_file = self.schemas_dir / "entities.yaml"
            if entities_file.exists():
                with open(entities_file, 'r', encoding='utf-8') as f:
                    self._schemas_cache['entities'] = yaml.safe_load(f)
            
            # 加载关系定义
            relations_file = self.schemas_dir / "relations.yaml"
            if relations_file.exists():
                with open(relations_file, 'r', encoding='utf-8') as f:
                    self._schemas_cache['relations'] = yaml.safe_load(f)
                    
        except Exception as e:
            print(f"Warning: Failed to load schemas: {e}")
            self._schemas_cache = {'entities': {}, 'relations': {}}
    
    def load_strategy(self, strategy_name: str) -> ExtractionConfig:
        """加载指定的提取策略"""
        if strategy_name in self._strategies_cache:
            return self._strategies_cache[strategy_name]
        
        strategy_file = self.strategies_dir / f"{strategy_name}.yaml"
        if not strategy_file.exists():
            raise FileNotFoundError(f"Strategy file not found: {strategy_file}")
        
        try:
            with open(strategy_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # 解析granularity配置
            granularity_data = config_data.get('granularity', {})
            granularity = GranularityConfig(
                breadth=granularity_data.get('breadth', 'standard'),
                depth=granularity_data.get('depth', 'semantic'),
                confidence=granularity_data.get('confidence', 'medium'),
                context_scope=granularity_data.get('context_scope', 'paragraph')
            )
            
            # 创建配置对象
            strategy_config = ExtractionConfig(
                name=config_data['name'],
                description=config_data['description'],
                version=config_data['version'],
                entities=config_data['entities'],
                relations=config_data['relations'],
                granularity=granularity,
                extraction_rules=config_data.get('extraction_rules', {}),
                prompt_template=config_data.get('prompt_template', 'base'),
                examples=config_data.get('examples', {}),
                post_processing=config_data.get('post_processing', {}),
                special_settings=config_data.get('special_settings', {})
            )
            
            # 缓存配置
            self._strategies_cache[strategy_name] = strategy_config
            return strategy_config
            
        except Exception as e:
            raise ValueError(f"Failed to parse strategy file {strategy_file}: {e}")
    
    def get_available_strategies(self) -> List[str]:
        """获取所有可用的策略名称"""
        if not self.strategies_dir.exists():
            return []
        
        strategies = []
        for file in self.strategies_dir.glob("*.yaml"):
            if file.is_file():
                strategies.append(file.stem)
        
        return strategies
    
    def get_entity_schema(self, strategy_name: str, entity_type: str) -> Dict[str, Any]:
        """获取指定策略和实体类型的schema定义"""
        entities_schema = self._schemas_cache.get('entities', {})
        
        # 首先尝试策略特定的定义
        strategy_entities = entities_schema.get(strategy_name, {})
        if entity_type in strategy_entities:
            return strategy_entities[entity_type]
        
        # 回退到通用定义
        common_entities = entities_schema.get('common', {})
        if entity_type in common_entities:
            return common_entities[entity_type]
        
        # 如果都找不到，返回默认结构
        return {
            'description': f'{entity_type} entity',
            'attributes': []
        }
    
    def get_relation_schema(self, strategy_name: str, relation_type: str) -> Dict[str, Any]:
        """获取指定策略和关系类型的schema定义"""
        relations_schema = self._schemas_cache.get('relations', {})
        
        # 首先尝试策略特定的定义
        strategy_relations = relations_schema.get(strategy_name, {})
        if relation_type in strategy_relations:
            return strategy_relations[relation_type]
        
        # 回退到通用定义
        common_relations = relations_schema.get('common', {})
        if relation_type in common_relations:
            return common_relations[relation_type]
        
        # 如果都找不到，返回默认结构
        return {
            'description': f'{relation_type} relation',
            'head_types': [],
            'tail_types': [],
            'attributes': []
        }
    
    def get_schemas(self) -> Dict[str, Any]:
        """获取完整的schemas缓存"""
        return self._schemas_cache
    
    def create_custom_strategy(self, 
                             name: str,
                             entities: List[str],
                             relations: List[str], 
                             description: Optional[str] = None,
                             granularity: Optional[GranularityConfig] = None,
                             **kwargs) -> ExtractionConfig:
        """动态创建自定义策略"""
        if description is None:
            description = f"Custom extraction strategy: {name}"
        
        if granularity is None:
            granularity = GranularityConfig()
        
        custom_strategy = ExtractionConfig(
            name=name,
            description=description,
            version="1.0",
            entities=entities,
            relations=relations,
            granularity=granularity,
            extraction_rules=kwargs.get('extraction_rules', {}),
            prompt_template=kwargs.get('prompt_template', 'base'),
            examples=kwargs.get('examples', {}),
            post_processing=kwargs.get('post_processing', {}),
            special_settings=kwargs.get('special_settings', {})
        )
        
        # 缓存自定义策略
        self._strategies_cache[name] = custom_strategy
        return custom_strategy


# 全局策略管理器实例
strategy_manager = ExtractionStrategy()