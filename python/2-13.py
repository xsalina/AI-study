# ### **Day 13 — Prompt Debugging**
# 练习：优化 3 个坏 Prompt


import os
from pathlib import Path
from dotenv import load_dotenv
# 1. 引入 LangChain 的 OpenAI 连接器
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser # 用来把结果转成字符串

# --- A. 加载环境变量 (和你之前的作业一样) ---
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)







# ❌ 坏 Prompt 1：【拉家常型】

# map_template_1 = """
# 嗨，请阅读下面这段文字：
# "{text}"

# 请帮我看看这里面有没有讲到什么产品啊、价格之类的？
# 如果有的话就告诉我一下，顺便把这段话的大意也总结几句给我。
# 谢谢啦！
# """

map_template_1_1 = """
嗨，请阅读下面这段文字：
"{text}"

请完成以下2个任务：

任务一：
请摘取文字里面的产品、价格、时间
格式要求，以key:value的形式，如果没有相关信息，过滤掉这个字段
数据区的信息不要重复出现产品名称，重复出现就不要记录这个产品了


任务二：
请用简练的语言总一下该段文字的核心内容，不超过100个字

-----------输出格式--------
【数据区】
产品：model2
价格：2.5万美元
时间：2025年

【摘要区】
特斯拉宣布了低价车型 Model 2 的量产计划，市场反响热烈。

--------------------------

请开始输出：
"""




long_text = """
【特斯拉重磅新闻】
特斯拉今日宣布，其新款 Model 2 车型将于 2025 年正式量产。
这款车型预计售价为 2.5 万美元，旨在抢占入门级电动车市场。
马斯克在电话会议中表示：“这是特斯拉历史上最重要的时刻。”
""" * 5

llm = ChatOpenAI(
    api_key=os.getenv("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model='qwen-turbo',
    temperature=0,
)


prompt = PromptTemplate.from_template(map_template_1_1)


# 4. 直接组装流水线 (简单直接)
chain = prompt | llm | StrOutputParser()






if __name__ == "__main__":
    results = chain.invoke({"text":long_text})
    print(results)




