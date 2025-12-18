### **Day 19 — 工具 + Prompt 组合**
# 练习：让模型自动决定是否需要调用工具### **Day 18 — 多工具调用链**
# 练习：让模型先搜索，再总结



# 目标：
#     使用tools多工具调用链

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
import yfinance as yf


# 1. 加载环境
load_dotenv()


# 2. 定义工具
@tool
def get_stock_price(ticker: str):
    """
    【真实联网】查询股票最新的实时价格
    参数:ticker: 股票代码 (例如: AAPL, NVDA, 600519)
    """
    print(f"📡 正在连接 Yahoo Finance 查询 {ticker} 的实时价格...")
    try:
    # 1. 获取股票对象
        stock = yf.Ticker(ticker)
        # 2. 拿到最新一天的历史数据 (包含当前价格)
        # '1d' 表示最近1天
        history = stock.history(period="1d")
        if history.empty:
            return f"❌ 未找到代码为 {ticker} 的股票，请检查拼写。"
        # 3. 提取收盘价 (Close)
            # iloc[-1] 取最后一行
        current_price = history['Close'].iloc[-1]
        # 保留2位小数
        return round(current_price, 2)
    except Exception as e:
        return f"查询出错: {e}"

@tool
def calculate_position(price: float, shares: int):
    """
    计算买入股票的总金额
    参数:  
        -price:股票单价
        -shares:股票数量
    """
    return price * shares



tools = [get_stock_price, calculate_position]

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
    system_prompt="你是一个专业的华尔街投资助手。请使用工具查询股价并计算成本"
)


# 5. 运行 (直接 invoke agent，不需要 executor)
print("🚀 Agent 启动中...")
result = agent.invoke({
    "messages": [
        ("user", "我有 5000 美元，我想买 10 股苹果(AAPL) 和 5 股特斯拉(TSLA)，钱够不够？如果够，还剩多少？")
    ]
})


# 6. 打印结果
# v1.0 的返回结果通常是一个包含 'messages' 的字典，最后一条是 AI 的回答
print("-" * 30)
print(result["messages"][-1].content)








