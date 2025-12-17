# **Day 17 — Function Calling（工具调用）**
# 练习：设计一个天气查询工具供模型调用



# 理解：
# 就是设计一个查询工具的函数绑定在模型身上，让模型内部去调用
# 模型负责“下令”，我的代码负责“干活”

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, ToolMessage # 👈 引入这个关键类


# --- 2. 必须先执行加载环境变量 ---
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)





def get_weather(city,days=1):
    # """ 包裹的 Docstring：是写给 AI 看的 Prompt，决定了 AI 能不能聪明地使用这个工具。
    """
    查询指定城市未来几天的天气情况。
    参数:
    - city: 城市名称 (如 "上海")
    - days: 查询天数 (默认为 1)
    """
    # 👇 我们让 Python 返回真正的结构化数据，而不是一句话
    return [
        {"day": 1, "weather": f"{city}大雨", "temp": "15°C (Python说的)"},
        {"day": 2, "weather": f"{city}中雨", "temp": "16°C (Python说的)"},
        {"day": 3, "weather": f"{city}阴天", "temp": "18°C (Python说的)"}
    ]
def get_sum(a,b):
    # """ 包裹的 Docstring：是写给 AI 看的 Prompt，决定了 AI 能不能聪明地使用这个工具。
    """
    求和,返回a+b的和
    参数:
    - a: 数值
    - b: 数值
    """
    
    return f"{a} + {b}"


llm = ChatOpenAI(
    api_key=os.getenv('ALIYUN_API_KEY'),
    base_url=os.getenv('ALIYUN_MODEL_BASEURL'),
    model='qwen-turbo',
    temperature=0.1,# 工具调用时，温度要低，越精准越好
)


# 告诉大模型：“你现在装备了一个工具，叫 get_weather
llm_with_tools = llm.bind_tools([get_weather,get_sum])





query = "帮我查一下上海和北京一周的天气"
# query = "帮我查一下上海一周的天气"
print(f"用户问题: {query}")


# 这里我们把输入包装成一个 Message 列表，方便后面追加历史
messages = [HumanMessage(content=query)]
print(f"\n✅ message 更新11: {messages}")
ai_msg_1 = llm_with_tools.invoke(messages)
messages.append(ai_msg_1)
print(f"\n✅ message 更新22: {messages}")
# 2️⃣ 解析 AI 的派工单
# 假设 AI 只调用了一个工具 (实际情况可能调用多个，这里简化处理)
for tool_call in ai_msg_1.tool_calls:
    # --- 证据提取 ---
    call_id = tool_call["id"]
    func_args = tool_call["args"]
    city_name = func_args.get("city")
    
    print(f"\n⚡️ 正在处理订单，城市: {city_name}")
    print(f"🔑 它的唯一身份证 (ID): {call_id}")  # 👈 仔细看这里，两个 ID 绝对不一样！
    
    # 执行函数
    tool_result = get_weather(**func_args)
    
    # 包装结果 (回传时带上 ID)
    tool_msg = ToolMessage(
        content=json.dumps(tool_result, ensure_ascii=False),
        tool_call_id=call_id, # 👈 必须原样贴回去，不能张冠李戴
        name=tool_call["name"] # 规范写法最好加上名字
    )
    
    # 把处理完的结果加进历史列表
    messages.append(tool_msg)
    print(f"\n✅ message 更新33: {messages}")

print(f"\n✅ message 更新44: {messages}")
# 4️⃣ 最终提交
print("\n🚀 所有单子处理完毕，提交给 AI...")
final_response = llm_with_tools.invoke(messages)

print("-" * 30)
print("🤖 最终回答:")
print(final_response.content)










# if __name__ == "__main__":
    






