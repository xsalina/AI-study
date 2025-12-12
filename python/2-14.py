### **Day 14 — 周总结 + 小项目**
# 输出:
# - 写《Prompt 使用手册（第一页）》
# - 小项目:**“AI 文案生成器”**




note = """

# 第一部分:什么是《Prompt 使用手册（第一页）》？
# 想象一下,你现在是“大模型提示词专家”,你要带一个刚入职的实习生。你需要在一页纸上告诉他,写 Prompt 有哪些黄金法则。
# 👉 任务目标: 总结出 3-5 条你觉得最有用、最“痛”的 Prompt 编写技巧。

1.大模型他并不是你肚子里的蛔虫,他不可能知道你想的什么,所以你要把规则、想要的格式给到他,举个few-shot例子给他,他会更容易理解你想要的是什么
2.大模型的"脑容量"也是有限的,你一下不要给他太多的数据,他可能只会记得第一条和最后一条,或者可能它会脑容量不足,会丢失数据,导致你想要的数据不完整
3.大模型的内部数据库可能最新的资料还在2年前,所以尽量不要让它去自己内部查资料去填充你想要的数据,你最好让它标注是来自内部还是你提供的资料来源,它也会有发散性思维（瞎补充）
4.写propmpt的几大要素有:角色、规则、few-shot示例、输出格式限制,以及没有的话用静默原则,让它闭嘴

总结（专业术语版）:
    1.你是肚子里的蛔虫 $\rightarrow$ 【清晰指令原则 (Clear Instructions)】
        解释:拒绝模糊指令（如“写得好一点”）,追求具象化（如“写一个 JSON,包含 key: price”）。
    2.脑容量有限/丢失数据 $\rightarrow$ 【长上下文迷失 (Lost in the Middle)】
        解释:当输入太长时,模型更容易记住开头和结尾,忽略中间。
        对策:就像 Day 12 那样,切片（Map-Reduce）或者把最重要的指令放在开头/结尾（Priming）。
    3.瞎补充/时间滞后 $\rightarrow$ 【幻觉抑制 (Hallucination Control)】
        解释:针对知识截止问题,必须明确数据源。
        对策:强制要求标记来源（如 source: knowledge）,或者明确“只基于上下文回答”。
    4.Prompt 要素/静默原则 $\rightarrow$ 【结构化提示词 (Structured Prompting)】
        解释:好 Prompt 都是有固定结构的。
        公式:Role (角色) + Context (背景) + Constraints (约束/静默) + Format (格式) + Example (示例)。
    5.【思维链 (Chain of Thought / CoT)】
        痛点:如果你直接问数学题或复杂逻辑题,AI 容易算错。
        心法:“Let's think step by step” (请一步步思考)
        用法:不要只求结果,要求 AI 展示过程。
            Bad: "特斯拉市盈率是多少？"
            Good: "请先提取特斯拉的股价,再查找每股收益,最后计算并输出市盈率。"
    6.【分隔符隔离 (Delimiters)】
        痛点:Day 12 那个“数据区”和“摘要区”混在一起的问题。
        心法:“物理隔离”。
        用法:永远不要把指令和用户数据混在一起,要用符号隔开。
            Example:
                请总结以下文本,文本被三个引号包裹:
                    {user_input}
            这能防止用户输入里包含恶意指令（Prompt Injection）




📝 我的《Prompt 手册》目录现在是这样的:
1.明确指令与示例 (Few-Shot)
2.管理上下文长度 (Context)
3.控制幻觉与来源 (Grounding)
4.结构化与静默原则 (Structure)
5.思维链引导 (CoT) —— New!
6.使用分隔符 (Delimiters) —— New!



"""




import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser 



# --- 2. 必须先执行加载环境变量 ---
current_dir = Path(__file__).parent
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)


llm = ChatOpenAI(
    api_key = os.getenv("ALIYUN_API_KEY"),
    base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    model = 'qwen-turbo',
    temperature= 0.7# 写文案要有创意，所以温度调高一点点
)



# 要是想填空，就用单层 { }； 要是想输出 JSON 符号，就用双层 {{ }} 把它包起来！
# 外面的 JSON 结构用 {{ }} 保护起来，里面的变量用 { } 留给程序填

prompt_text = """
你现在是一名精通全网各平台各类型的文案专家。
你的任务是根据用户给定的【主题】，为【{platform}】平台撰写一篇【{copy_type}】类型的文案。

---------------- 核心规则 ----------------
1.【风格适配】：必须严格遵守{platform}的社区风格（如小红书要多Emoji/种草语气，知乎要专业/逻辑严密）。
2.【内容风控】：禁止捏造事实、禁止涉黄涉政、禁止低俗营销。
3.【静默原则】：不要输出任何解释、注释、旁白（如“好的，这是您的文案”）。
4.【拒绝回答】：如果用户的主题属于违法违规范围，请在 reply 字段礼貌拒绝。

    
---------------- 格式范例 (Few-Shot) ----------------
输入：
平台：小红书
类型：产品种草
主题：一款超静音的便携风扇

输出：
{{ 
    "replay":"着风扇太静音了！🔇，办公室午睡神器，这封简直是把润物细无声刻在'DNA'里面了....(此处省略文案)",
    "tag":["#好物推荐","#静音风扇","#办公室神器"]
}}

---------------- 当前任务 ----------------
目标平台：{platform}
文案类型：{copy_type}
核心主题：{topic}

请严格按照上面输出的JSON格式输出，不得额外添加字段

"""

prompt = PromptTemplate.from_template(prompt_text)

chain = prompt | llm | JsonOutputParser()

if __name__ == '__main__':
    result = chain.invoke({
        "platform":"小红书",
        "copy_type":"种草笔记",
        "topic":"特斯拉model 2只要2.5万美元，太香了"
    })
    print(result)


    result1 = chain.invoke({
        "platform":"知乎",
        "copy_type":"行业分析",
        "topic":"特斯拉推出廉价车型对国产新能源汽车的打击"
    })
    print(result1)