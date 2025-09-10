"""
默认的few-shot示例
用于在策略配置中没有指定示例时的回退
"""
from typing import List
import langextract as lx


class DefaultExamples:
    """默认示例管理器"""
    
    @staticmethod
    def get_literary_examples() -> List[lx.data.ExampleData]:
        """获取文学文本的默认示例"""
        return [
            # 示例 1：人物 + 情绪 + 比喻关系
            lx.data.ExampleData(
                text=(
                    "ROMEO. But soft! What light through yonder window breaks? "
                    "It is the east, and Juliet is the sun."
                ),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="character",
                        extraction_text="ROMEO",
                        attributes={"role": "speaker"},
                    ),
                    lx.data.Extraction(
                        extraction_class="emotion",
                        extraction_text="But soft!",
                        attributes={"feeling": "gentle awe"},
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="is",
                        attributes={
                            "head_text": "Juliet",
                            "head_class": "character",
                            "relation_type": "metaphor",
                            "tail_text": "the sun",
                            "tail_class": "symbol",
                        },
                    ),
                ],
            ),
            
            # 示例 2：称呼/询问
            lx.data.ExampleData(
                text="JULIET. O Romeo, Romeo! wherefore art thou Romeo?",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="character",
                        extraction_text="JULIET",
                        attributes={"role": "speaker"},
                    ),
                    lx.data.Extraction(
                        extraction_class="emotion",
                        extraction_text="O Romeo, Romeo!",
                        attributes={"feeling": "longing"},
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="wherefore art thou Romeo",
                        attributes={
                            "head_text": "JULIET",
                            "head_class": "character",
                            "relation_type": "addresses",
                            "tail_text": "Romeo",
                            "tail_class": "character",
                        },
                    ),
                ],
            ),
            
            # 示例 3：出现/位移
            lx.data.ExampleData(
                text="JULIET appears at a window.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="character",
                        extraction_text="JULIET",
                        attributes={"role": "character"},
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="appears",
                        attributes={
                            "head_text": "JULIET",
                            "head_class": "character",
                            "relation_type": "appears_at",
                            "tail_text": "a window",
                            "tail_class": "location",
                        },
                    ),
                ],
            ),
        ]
    
    @staticmethod
    def get_default_examples() -> List[lx.data.ExampleData]:
        """获取通用的默认示例"""
        return DefaultExamples.get_literary_examples()


# 全局实例
default_examples = DefaultExamples()