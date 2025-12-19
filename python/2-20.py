### **Day 20 -《UI 初体验 —— 使用 Streamlit 快速验证 Agent 逻辑


import os
import streamlit as st
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



system_prompt = """
你是一个专业的华尔街投资助手。
请使用工具查询股价并计算成本。

⚠️ 关键注意事项：
1. 用户的资金如果是“人民币(CNY)”，而美股价格是“美元(USD)”。
2. 计算前，请先将人民币按汇率（假设 1 USD = 7.25 CNY）换算成美元，然后再计算能买几股。
3. 请用中文回答，并列出计算过程。
"""


# 初始化 Agent (只需要做一次)
# 为了防止每次点按钮都重新造一遍大脑，我们用 st.cache_resource 把它存起来，Streamlit 的“坏毛病”：金鱼记忆

@st.cache_resource
def get_agent():
    llm = ChatOpenAI(
        api_key = os.getenv('ALIYUN_API_KEY'),
        base_url = os.getenv('ALIYUN_MODEL_BASEURL'),
        model = 'qwen-turbo',
        temperature = 0
    )
    tools = [get_stock_price,calculate_position]
    return create_agent(
        model = llm,
        tools = tools,
        system_prompt = system_prompt
    )

agent = get_agent()

# ==========================================
# “网页界面”部分 (Frontend)
# ==========================================


# 1. 网页标题
st.title("💸 AI 首席投资顾问 v1.0")
st.caption("基于 LangChain Agent + Yahoo Finance 实时数据")


# 1. 侧边栏
with st.sidebar:
    st.info("💡 提示：支持美股代码，例如 AAPL (苹果), NVDA (英伟达), TSLA (特斯拉)")

# 3. 用户输入框
user_input = st.text_input('💰 请输入你的投资计划：", "我现在有 5000 美元，买 10 股苹果(AAPL) 够不够？')

# 4. 按钮与执行逻辑
if st.button('🚀 开始分析'):
    if not user_input:
        st.warning('请先输入问题哦！')
    else:
        # 显示一个转圈圈的加载动画，提升体验
        with st.spinner('AI 正在连接纳斯达克交易所...'):
            try:
                # 调用agent
                results = agent.invoke({"messages":[("user",user_input)]})
                final_result = results['messages'][-1].content
                
                # 显示成功提示
                st.success('分析完成！')

                # 1. 先把 AI 的详细分析写出来
                with st.expander("点击查看详细计算过程"):
                    st.write(final_result)
                # 2. 我们用“列”来布局 (Columns)
                col1,col2 = st.columns(2)    
                # 3. 在左边显示特斯拉，右边显示英伟达
                # 注意：这里的数据你可以尝试让 Agent 以 JSON 格式返回，或者手动填个大概来看看效果
                with col1:
                    st.metric(label="Tesla (TSLA)", value="$483.37" , delta = '0 股（资金不足）')
                with col2:
                    st.metric(label="NVIDIA (NVDA)", value="$174.14" , delta = '2 股 (买入)')



            except Exception as e:
                st.error(f"发生错误 {e}")



