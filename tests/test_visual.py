from src.core.visual_nodes import visual_nodes

text = "小明是一个勇敢的少年，他充满希望。小红是他的朋友，她很温柔。"

# 直接提取并可视化
html_path = visual_nodes.visualize_text_extraction(
    text=text,
    strategy="literary",
    save_path="output/demo.html"
)