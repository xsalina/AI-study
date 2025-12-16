import os
from pathlib import Path
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
from openai import OpenAI
import sys




# --- 2. 必须先执行加载环境变量 ---
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)

# ================= 配置区域 =================
# 填入你的 DeepSeek API Key
API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = "https://api.deepseek.com"

# ================= 工具函数 =================

def calculate_rsi(series, period=14):
    """计算 RSI 强弱指标"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_market_data(query_name):
    """
    智能映射：支持股票、黄金、美股
    """
    # 核心映射表
    symbol_map = {
        # === 美股 ===
        "英伟达": "NVDA",
        "特斯拉": "TSLA",
        "苹果": "AAPL",
        
        # === A股 ===
        "中国黄金": "600916.SS", # 这是中国黄金集团的股票
        
        # === 贵金属/积存金 (使用国际金价作为锚点) ===
        "浙商黄金积存金": "GC=F", 
        "浙商黄金": "GC=F",
        "积存金": "GC=F",
        "黄金": "GC=F"
    }
    
    ticker = symbol_map.get(query_name)
    if not ticker:
        # 模糊匹配尝试
        if "黄金" in query_name and "中国" not in query_name:
             ticker = "GC=F" # 只要提到黄金且不是中国黄金股票，默认看国际金价
        else:
             return None, "❌ 暂不支持该品种，请尝试：英伟达、特斯拉、中国黄金、浙商黄金"

    print(f"⏳ 正在获取 [{query_name}] 的实时行情 (锚定代码: {ticker})...")
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        
        if df.empty:
            return None, "❌ 数据获取失败（可能是休市或网络原因）"

        # === 提取数据 ===
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        ma_5 = df['Close'].rolling(window=5).mean().iloc[-1]
        rsi_14 = calculate_rsi(df['Close']).iloc[-1]

        # === 智能判断数据类型 ===
        is_gold = (ticker == "GC=F")
        currency = "USD (美元/盎司)" if is_gold or "." not in ticker else "CNY (人民币)"
        
        # 如果是积存金，给用户一个特别提示
        note = ""
        if is_gold:
            note = "(注：这是国际金价趋势，你银行App里的价格会跟随此波动，但单位不同)"

        data_summary = {
            "名称": query_name,
            "代码": ticker,
            "当前价格": f"{round(current_price, 2)} {currency}",
            "涨跌幅": f"{round(change_pct, 2)}%",
            "5日均线": round(ma_5, 2),
            "RSI指标": round(rsi_14, 2),
            "备注": note
        }
        return data_summary, None

    except Exception as e:
        return None, f"❌ 程序错误: {e}"

# ================= AI 分析核心 =================

def get_ai_analysis(data_dict):
    if API_KEY.startswith("sk-xxx"):
        return "⚠️ 别忘了填入你的 API Key！"

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 动态调整 Prompt：如果分析的是黄金，角色要变成大宗商品专家
    if "黄金" in data_dict['名称'] or "积存金" in data_dict['名称']:
        role_desc = "你是一名资深的大宗商品交易员，专注于黄金走势分析。"
        logic_desc = "黄金受美元指数和避险情绪影响大。RSI>75通常回调风险极大。"
    else:
        role_desc = "你是一名华尔街股票交易员。"
        logic_desc = "关注个股趋势和均线支撑。"

    system_prompt = f"""
    {role_desc}
    请根据传入的数据，预测今天的行情并给出操作建议（买入/卖出/观望）。
    
    分析逻辑：
    1. {logic_desc}
    2. 如果价格在5日均线之上，视为强势。
    3. 严格基于RSI指标判断超买超卖。
    
    请用口语化的中文回答，就像朋友聊天一样。最后必须加免责声明。
    """

    user_prompt = f"请分析这个品种的数据：\n{data_dict}"

    print("🧠 AI 正在分析市场数据...")
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI 罢工了: {e}"

# ================= 主程序 =================

if __name__ == "__main__":
    print("="*40)
    print("📈 全能金融分析师 (支持: 股票 / 积存金 / 美股)")
    print("="*40)

    while True:
        user_input = input("\n请输入品种 (如: 浙商黄金 / 英伟达 / 特斯拉): ").strip()
        
        if user_input.lower() in ['q', 'quit', 'exit']:
            break
            
        if not user_input:
            continue

        data, error = get_market_data(user_input)
        
        if error:
            print(error)
        else:
            print("-" * 30)
            for k, v in data.items():
                print(f"{k}: {v}")
            print("-" * 30)
            
            analysis = get_ai_analysis(data)
            print(f"\n📝 [AI 建议]\n{analysis}")
            print("\n" + "="*40)