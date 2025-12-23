### **Day 15 — ChatCompletion 深入**
# 练习：做一个“多轮记忆对话”



import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_classic.chains import ConversationChain
from langchain_classic.memory import ConversationSummaryMemory
from langchain_core.prompts import PromptTemplate
import warnings



# --- 旧写法 (v0.3 以前) ---
# from langchain.chains import ConversationChain
# from langchain.memory import ConversationSummaryMemory


# --- 2. 必须先执行加载环境变量 ---
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)






# 1. 初始化大厨
llm = ChatOpenAI(
    api_key = os.getenv('ALIYUN_API_KEY'),
    base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    model = 'qwen-turbo',
    temperature = 0.7
)


# 2. 初始化记忆模块 (这是核心！)
# 注意：这就需要传一个 llm 进去，因为“写总结”这件事本身需要 AI 来做
memory = ConversationSummaryMemory(
    llm = llm,# 让 Qwen 负责写总结
    input_key = 'input',# 告诉记忆模块，哪一个是用户的新输入
)



# 3. 👇 请你来写这个 Prompt
# 思考：按照“三明治结构”，历史摘要应该放在哪里？
memory_prompt_template = """

-----------------------------------------
# === 上层面包 (立规矩) ===
 你现在是一名专业的股票交易助手
 你的回答必须简练、精准、不要废话
-----------------------------------------
# === 中间夹心 (历史摘要) ===
# 这里放 AI 总结出来的“前情提要”，相当于背景信息
这里是我们之前对话的摘要（你的记忆）：
{history}
-----------------------------------------
# === 下层面包 (当前任务) ===
# 这里才是用户此时此刻问的问题，必须放最后！
用户现在说：
{input}
-----------------------------------------
请根据最新用户说的问题进行回答：

"""



prompt = PromptTemplate(
    input_variables = ['history','input'],# 👈 必须要有这两个变量
    template = memory_prompt_template
)


# 4. 组装成“对话链”
# ConversationChain 是一个封装好的盒子，自动帮你管理“读取记忆 -> 拼接Prompt -> 保存记忆”的全过程

conversation = ConversationChain(
    llm=llm,
    memory=memory,
    prompt=prompt,
    verbose=True # 👈 开启这个，你能看到后台它是怎么悄悄写总结的！
)


# --- 测试对话 ---
# 第一句
print("User: 特斯拉现在的价格是多少？")
res1 = conversation.predict(input="特斯拉现在的价格是多少？")
print(f"AI: {res1}\n")

# 第二句 (测试它记没记住上一句)
print("User: 那我现在该买入吗？")
res2 = conversation.predict(input="那我该买入吗？") # 注意：这里没提“特斯拉”，看它知不知道
print(f"AI: {res2}\n")
print("User: 那我现在该买入吗？")
res3 = conversation.predict(input="你知道我问的是什么吗？") # 注意：这里没提“特斯拉”，看它知不知道
print(f"AI: {res3}\n")


# --- 更明显的记忆测试 ---

# 1. 挖个坑
print("User: 我想给女朋友买个LV的包，预算2万，你觉得行吗？")
conversation.predict(input="我想给女朋友买个LV的包，预算2万，你觉得行吗？")

# 2. 只有记住上下文，它才能接得住这个梗
print("\nUser: 那爱马仕呢？") 
# (如果没记忆，它会问：爱马仕什么？)
# (如果有记忆，它会说：你刚才不是说预算才2万吗？买爱马仕？做梦呢？)
res = conversation.predict(input="那爱马仕呢？")

print(f"AI: {res}")