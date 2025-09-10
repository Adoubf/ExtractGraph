from typing import Dict, Optional, List, Any
import langextract as lx
from langextract.providers.openai import OpenAILanguageModel
from langextract import prompt_validation as pv

from src.config.settings import settings
from src.config.strategy import strategy_manager, ExtractionConfig, GranularityConfig
from src.config.prompt_generator import prompt_generator
from src.config.default_examples import default_examples
from src.utils.text_format import text_formatter
from src.core.cypher_generate import cypher_generator


class ConfigurableExtractor:
    """可配置信息提取器 - 基于langextract标准API"""
    
    def __init__(self):
        self._current_strategy: Optional[ExtractionConfig] = None
    
    def _build_model(self):
        """构建OpenAI兼容的语言模型"""
        return OpenAILanguageModel(
            model_id=settings.model_id,
            api_key=settings.api_key,
            base_url=getattr(settings, 'base_url', None)
        )
    
    def extract(self, 
                text: str,
                strategy: Optional[str] = None,
                entities: Optional[List[str]] = None,
                relations: Optional[List[str]] = None,
                breadth: Optional[str] = None,
                depth: Optional[str] = None, 
                confidence: Optional[str] = None,
                context_scope: Optional[str] = None,
                **kwargs) -> lx.data.AnnotatedDocument:
        """
        可配置的文本提取方法 - 直接返回langextract的AnnotatedDocument
        
        Args:
            text: 输入文本
            strategy: 策略名称 (如 'literary', 'business')
            entities: 自定义实体类型列表
            relations: 自定义关系类型列表
            breadth: 提取广度 ('minimal', 'standard', 'comprehensive')
            depth: 提取深度 ('surface', 'semantic', 'inferential')
            confidence: 置信度 ('high', 'medium', 'all')
            context_scope: 上下文范围 ('local', 'paragraph', 'document')
            **kwargs: 传递给langextract的其他参数
        
        Returns:
            langextract.data.AnnotatedDocument: 标准的langextract结果对象
        """
        
        # 确定使用的策略
        extraction_strategy = self._determine_strategy(
            strategy, entities, relations, breadth, depth, confidence, context_scope, **kwargs
        )
        
        # 生成提示词
        prompt_description = prompt_generator.generate_prompt(extraction_strategy)
        
        # 生成示例
        examples = self._get_examples(extraction_strategy)
        
        # 根据精细度调整参数
        extraction_params = self._adjust_extraction_parameters(extraction_strategy)
        
        # 合并用户传入的kwargs
        extraction_params.update(kwargs)
        
        # 构建模型对象
        model = self._build_model()
        
        # 设置标准langextract参数
        standard_params = {
            'fence_output': True,
            'use_schema_constraints': False,
            'prompt_validation_level': pv.PromptValidationLevel.OFF,
            'debug': getattr(settings, 'app_debug', False)
        }
        
        # 合并参数（用户参数优先）
        final_params = {**standard_params, **extraction_params}
        
        # 直接调用langextract标准API
        result = lx.extract(
            text_or_documents=text,
            prompt_description=prompt_description,
            examples=examples,
            model=model,
            **final_params
        )
        
        # 保存当前策略
        self._current_strategy = extraction_strategy
        
        return result
    
    def extract_to_dict(self, 
                       text: str,
                       strategy: Optional[str] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        提取并返回字典格式结果（兼容原有代码）
        """
        result = self.extract(text, strategy=strategy, **kwargs)
        return lx.data_lib.annotated_document_to_dict(result)
    
    def extract_for_neo4j(self, 
                          text: str,
                          strategy: Optional[str] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        提取并格式化为Neo4j数据结构
        """
        # 执行提取
        result = self.extract(text, strategy=strategy, **kwargs)
        
        # 转换为字典格式
        extraction_dict = lx.data_lib.annotated_document_to_dict(result)
        
        # 转换为Neo4j格式
        neo4j_data = text_formatter.format_for_neo4j(extraction_dict)
        
        # 生成Cypher语句
        nodes_cypher, relationships_cypher = cypher_generator.generate_cypher_import(neo4j_data)
        
        return {
            'raw_extraction': extraction_dict,
            'neo4j_data': neo4j_data,
            'cypher_statements': {
                'nodes': nodes_cypher,
                'relationships': relationships_cypher
            }
        }
    
    def extract_for_neo4j_merge(self, 
                                text: str,
                                strategy: Optional[str] = None,
                                **kwargs) -> Dict[str, Any]:
        """
        提取并生成Neo4j MERGE语句
        """
        # 执行提取
        result = self.extract(text, strategy=strategy, **kwargs)
        
        # 转换为字典格式
        extraction_dict = lx.data_lib.annotated_document_to_dict(result)
        
        # 转换为Neo4j格式
        neo4j_data = text_formatter.format_for_neo4j(extraction_dict)
        
        # 生成MERGE语句
        nodes_merge, relationships_merge = cypher_generator.generate_merge_statements(neo4j_data)
        
        return {
            'raw_extraction': extraction_dict,
            'neo4j_data': neo4j_data,
            'merge_statements': {
                'nodes': nodes_merge,
                'relationships': relationships_merge
            }
        }
    
    def _determine_strategy(self, 
                           strategy: Optional[str],
                           entities: Optional[List[str]],
                           relations: Optional[List[str]],
                           breadth: Optional[str],
                           depth: Optional[str],
                           confidence: Optional[str],
                           context_scope: Optional[str],
                           **kwargs) -> ExtractionConfig:
        """确定使用的提取策略"""
        if strategy:
            # 使用预定义策略
            try:
                base_strategy = strategy_manager.load_strategy(strategy)
            except FileNotFoundError:
                # 如果策略不存在，创建基础策略
                return self._create_fallback_strategy(entities, relations, breadth, depth, confidence, context_scope)
            
            # 如果有额外参数，创建修改版本
            if any([breadth, depth, confidence, context_scope, entities, relations]):
                granularity = GranularityConfig(
                    breadth=breadth or base_strategy.granularity.breadth,
                    depth=depth or base_strategy.granularity.depth,
                    confidence=confidence or base_strategy.granularity.confidence,
                    context_scope=context_scope or base_strategy.granularity.context_scope
                )
                
                # 创建自定义策略
                return strategy_manager.create_custom_strategy(
                    name=f"{strategy}_custom",
                    entities=entities or base_strategy.entities,
                    relations=relations or base_strategy.relations,
                    description=base_strategy.description,
                    granularity=granularity,
                    **kwargs
                )
            
            return base_strategy
        
        elif entities or relations:
            # 创建完全自定义策略
            granularity = GranularityConfig(
                breadth=breadth or "standard",
                depth=depth or "semantic", 
                confidence=confidence or "medium",
                context_scope=context_scope or "paragraph"
            )
            
            return strategy_manager.create_custom_strategy(
                name="custom",
                entities=entities or ["character", "emotion"],
                relations=relations or ["relationship"],
                description="Custom extraction strategy",
                granularity=granularity,
                **kwargs
            )
        
        else:
            # 使用默认策略
            return self._create_fallback_strategy(entities, relations, breadth, depth, confidence, context_scope)
    
    def _create_fallback_strategy(self, entities, relations, breadth, depth, confidence, context_scope):
        """创建回退策略"""
        granularity = GranularityConfig(
            breadth=breadth or "standard",
            depth=depth or "semantic",
            confidence=confidence or "medium", 
            context_scope=context_scope or "paragraph"
        )
        
        return strategy_manager.create_custom_strategy(
            name="fallback",
            entities=entities or ["character", "emotion"],
            relations=relations or ["relationship"],
            description="Fallback extraction strategy",
            granularity=granularity
        )
    
    def _get_examples(self, strategy: ExtractionConfig) -> List[lx.data.ExampleData]:
        """获取few-shot示例"""
        # 使用新的默认示例系统
        return default_examples.get_default_examples()
    
    def _adjust_extraction_parameters(self, strategy: ExtractionConfig) -> Dict[str, Any]:
        """根据精细度配置调整提取参数"""
        params = {}
        
        granularity = strategy.granularity
        
        # 根据广度调整
        if granularity.breadth == "minimal":
            params['extraction_passes'] = 1
            params['max_char_buffer'] = 1000
            params['temperature'] = 0.0
        elif granularity.breadth == "comprehensive":
            params['extraction_passes'] = 3
            params['max_char_buffer'] = 2000
            params['temperature'] = 0.2
        else:  # standard
            params['extraction_passes'] = 2
            params['max_char_buffer'] = 1500
            params['temperature'] = 0.1
        
        # 根据深度调整
        if granularity.depth == "inferential":
            params['temperature'] = max(params.get('temperature', 0.1), 0.3)
        elif granularity.depth == "surface":
            params['temperature'] = min(params.get('temperature', 0.1), 0.05)
        
        # 根据上下文范围调整
        if granularity.context_scope == "document":
            params['max_char_buffer'] = params.get('max_char_buffer', 1500) * 2
        elif granularity.context_scope == "local":
            params['max_char_buffer'] = params.get('max_char_buffer', 1500) // 2
        
        # 设置OpenAI兼容参数（基于langextract文档）
        if hasattr(settings, 'base_url') and settings.base_url:
            # 使用OpenAI兼容API时的设置
            params['fence_output'] = True
            params['use_schema_constraints'] = False
        
        return params
    
    # ---------- 策略管理方法 ----------
    def get_available_strategies(self) -> List[str]:
        """获取所有可用的策略"""
        return strategy_manager.get_available_strategies()
    
    def get_current_strategy(self) -> Optional[ExtractionConfig]:
        """获取当前使用的策略"""
        return self._current_strategy
    
    def describe_strategy(self, strategy_name: str) -> Dict[str, Any]:
        """描述指定策略的配置"""
        try:
            strategy = strategy_manager.load_strategy(strategy_name)
            return {
                'name': strategy.name,
                'description': strategy.description,
                'entities': strategy.entities,
                'relations': strategy.relations,
                'granularity': {
                    'breadth': strategy.granularity.breadth,
                    'depth': strategy.granularity.depth,
                    'confidence': strategy.granularity.confidence,
                    'context_scope': strategy.granularity.context_scope
                }
            }
        except FileNotFoundError:
            return {'error': f'Strategy "{strategy_name}" not found'}


# 创建全局实例
extractor = ConfigurableExtractor()
