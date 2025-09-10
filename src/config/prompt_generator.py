"""
可配置提示词生成器
基于Jinja2模板和策略配置动态生成提示词
"""

from jinja2 import Environment, FileSystemLoader, Template
from typing import Optional
from pathlib import Path
import os

from src.config.strategy import ExtractionConfig, strategy_manager
from src.utils.logging import setup_logging

logger = setup_logging()

class ConfigurablePromptGenerator:
    """可配置提示词生成器"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        
        self.templates_dir = Path(templates_dir)
        
        # 初始化Jinja2环境
        if self.templates_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
        else:
            self.jinja_env = Environment()
    
    def generate_prompt(self, strategy: ExtractionConfig) -> str:
        """基于策略配置生成提示词"""
        try:
            # 获取模板
            template = self._get_template(strategy.prompt_template)
            
            # 准备模板变量
            template_vars = {
                'strategy': strategy,
                'schemas': strategy_manager.get_schemas()
            }
            
            # 渲染模板
            prompt = template.render(**template_vars)
            return prompt.strip()
            
        except Exception as e:
            # 如果模板渲染失败，回退到默认提示词
            logger.debug(f"Warning: Failed to generate prompt from template: {e}")
            return self._generate_fallback_prompt(strategy)
    
    def _get_template(self, template_name: str) -> Template:
        """获取指定的模板"""
        template_file = f"{template_name}.jinja2"
        
        try:
            return self.jinja_env.get_template(template_file)
        except Exception:
            # 如果找不到指定模板，使用基础模板
            try:
                return self.jinja_env.get_template("base.jinja2")
            except Exception:
                # 如果连基础模板都找不到，使用内置模板
                return self._get_builtin_template()
    
    def _get_builtin_template(self) -> Template:
        """获取内置的基础模板"""
        builtin_template = """
You are an information extraction engine for {{ strategy.description }}.
Extract the following types of items from the input text, in order of appearance:

1) ENTITIES of class:
{%- for entity in strategy.entities %}
- {{ entity }}: entity type
{%- endfor %}

2) RELATIONS of class:
{%- for relation in strategy.relations %}
- {{ relation }}: relation type
{%- endfor %}

Rules:
- Use the exact surface text from the input (no paraphrase).
- Every extraction must be grounded in the text; do not output anything not present.
- Do not create overlapping spans for different entities/relations.

Span alignment:
- The char_interval must exactly match the extraction_text.
- Do NOT include leading or trailing spaces.
- Do NOT include adjacent punctuation unless it is part of the surface form.

Output:
- Return extractions that the model can map to character-level spans.
- Keep classes strictly among: {{ strategy.entities + strategy.relations | join(', ') }}.
- Ensure attributes are JSON-compatible key-value pairs.
        """.strip()
        
        return Template(builtin_template)
    
    def _generate_fallback_prompt(self, strategy: ExtractionConfig) -> str:
        """生成回退提示词"""
        entities_list = ', '.join(strategy.entities)
        relations_list = ', '.join(strategy.relations)
        
        prompt = f"""
You are an information extraction engine for {strategy.description}.
Extract three kinds of items from the input text, in order of appearance:

1) ENTITIES of class:
{chr(10).join(f'- {entity}: a {entity} entity' for entity in strategy.entities)}

2) RELATIONS of class:
{chr(10).join(f'- {relation}: a {relation} relation' for relation in strategy.relations)}

Rules:
- Use the exact surface text from the input (no paraphrase).
- Every extraction must be grounded in the text; do not output anything not present.
- Do not create overlapping spans for different entities/relations.

Span alignment:
- The char_interval must exactly match the extraction_text.
- Do NOT include leading or trailing spaces.
- Do NOT include adjacent punctuation unless it is part of the surface form.

Entity attributes:
- Provide useful attributes for ENTITIES when obvious from text.

Relationship extraction:
- For RELATIONSHIP, always fill attributes with:
head_text, head_class, relation_type, tail_text, tail_class.

Output:
- Return extractions that the model can map to character-level spans.
- Keep classes strictly among: {entities_list}, {relations_list}.
- Ensure attributes are JSON-compatible key-value pairs.
        """.strip()
        
        return prompt
    



# 全局提示词生成器实例
prompt_generator = ConfigurablePromptGenerator()