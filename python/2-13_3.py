# ### **Day 13 — Prompt Debugging**
# 练习：优化 3 个坏 Prompt








# ❌ 坏 Prompt 3：【过早优化型】

# map_template_3 = """
# 阅读文本："{text}"

# 请直接输出一个标准的 JSON 对象，包含 keys: product, price, date。
# 不要输出任何其他文字。
# """

# 为什么叫过早，因为可能是文案太长了，可能需要先切割分段再喂给AI，
# 她直接让它输出一个标准的JSON对象，会导致文案没读完，生成的JSON独享不完整





map_template_3 = """
阅读文本："{text}"

任务：
1. 提取文中所有的产品信息（产品名、价格、日期）。
2. 直接输出一个标准的 **JSON 数组 (List of Objects)**。
3. 如果有产品名的情况下，价格或日期没有提及的情况下，请直接赋值 null (JSON null 值)。
4. 如果文章多次重复提到同一个产品，则只记录一次即可 (合并去重)。
5. 如果文中没有提及任何产品，输出空数组 []。

示例格式：
[
  {{
    "product": "Model 2", 
    "price": "2.5w", 
    "date": "2025"
  }},
  {{
    "product": "Cybertruck", 
    "price": null, 
    "date": "2023"
  }}
]

不要输出任何其他文字（不要 markdown 标记）。
"""
