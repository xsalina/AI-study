### **Day 16 — Streaming 流式输出**
# 练习：实现像 ChatGPT 一样“打字机输出”




import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI





# --- 2. 必须先执行加载环境变量 ---
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)

llm = ChatOpenAI(
    api_key = os.getenv('ALIYUN_API_KEY'),
    base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    model = 'qwen-turbo',
    temperature=0.7,
)

print("🤖 AI 正在思考中... (注意看下面字是怎么出来的)\n")


chunks = llm.stream("请背诵白居易的《长恨歌》，只背前4句即可。")


for chunk in chunks:
    print(chunk.content, end="", flush=True)

