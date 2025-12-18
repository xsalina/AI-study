### **Day 18 — 多工具调用链**
# 练习：让模型先搜索，再总结



# 目标：
#     使用tools多工具调用链

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent



# 1. 加载环境
load_dotenv()


# 2. 定义工具
@tool
def get_weather(city: str):
    """查询天气"""
    return f"{city}的天气是：晴天，25度"

@tool
def multiply(a: int, b: int):
    """计算乘法"""
    return a * b



tools = [get_weather, multiply]

# 3. 准备模型 (Qwen/GPT)
llm = ChatOpenAI(
    model="qwen-turbo", 
    api_key=os.getenv("ALIYUN_API_KEY"),
    base_url=os.getenv("ALIYUN_MODEL_BASEURL"),
    temperature=0
)

# 4. 创建 Agent (新版写法)
# 注意：v1.0 里的 create_agent 直接接受 model 和 tools
# 它内部已经把 "Prompt" 和 "Executor" 的逻辑全包了
print("🤖 正在构建 v1.0 新版 Agent...")

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个有用的助手，请优先使用工具解决问题。"
)


# 5. 运行 (直接 invoke agent，不需要 executor)
print("🚀 Agent 启动中...")
result = agent.invoke({
    "messages": [
        ("user", "查一下上海和北京的天气，然后算出 299 乘以 5 是多少？还要酸楚5除以1等于几")
    ]
})


# 6. 打印结果
# v1.0 的返回结果通常是一个包含 'messages' 的字典，最后一条是 AI 的回答
print("-" * 30)
print(result["messages"][-1].content)








