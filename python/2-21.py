# Day 21: 你的 AI 会阅读了 (RAG 基础)
# 任务: 打造“ChatPDF”原型。
# 技术: PyPDFLoader (读文件) + RecursiveCharacterTextSplitter (切片) + VectorStore (向量化存储)。
# 成果: 上传一份文档，AI 能基于文档内容回答问题。

# // --- 第一部分：数据准备 ---
# 定义 PDF路径 = "python_tutorial.pdf"

# 文档 = PyPDFLoader(PDF路径).load()

# // 切分器配置：每块1000字，重叠200字
# 切分器 = RecursiveCharacterTextSplitter(size=1000, overlap=200)
# 文本块列表 = 切分器.split(文档)

# // 建库：把文本块变成向量存起来
# 向量库 = Chroma.from_documents(文本块列表, Embedding模型)


# // --- 第二部分：问答循环 ---
# 当 用户输入问题 时:
#     // 1. 去库里找答案素材
#     参考素材 = 向量库.search(用户问题, top_k=3)
    
#     // 2. 填空题模式
#     提示词 = "请根据以下素材：{参考素材}，回答问题：{用户问题}"
    
#     // 3. 让 AI 作答
#     最终答案 = ChatOpenAI.predict(提示词)DASHSCOPE_API_KEY
    
#     打印(最终答案)




import os
from dotenv import load_dotenv
# 导入我们的“解题工具”
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 加载器和向量库仍在 community 中
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi

from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
# 【重点 3】提示词模板在这里
from langchain_core.prompts import ChatPromptTemplate

# --- 修改 A 部分：加载文件 ---
# 把原来的 python_tutorial.pdf 换成你的财报文件名
# 1. 加载环境
load_dotenv()

# --- 【修改点】自动获取当前脚本所在的文件夹路径 ---
current_dir = os.path.dirname(os.path.abspath(__file__))
# 拼接成完整的绝对路径
pdf_path = os.path.join(current_dir, "TSLA-Q3-2025-Update.pdf")

print(f"📂 正在尝试加载文件: {pdf_path}")

# 检查一下文件到底在不在
if not os.path.exists(pdf_path):
    print("❌ 错误：文件不存在！请检查文件名或路径。")
else:
    loader = PyPDFLoader(pdf_path) # 这里传入绝对路径
    docs = loader.load()
    print("✅ 加载成功！")



print(f"1. 正在加载特斯拉财报: {pdf_path} ...")
loader = PyPDFLoader(pdf_path)
documents = loader.load()
print(f"   -> 加载成功！共 {len(documents)} 页。")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,# 每个碎片约 1000 字符，保证能装下一个函数
    chunk_overlap = 250,# 重叠 200 字符，防止上下文断裂
)
texts = text_splitter.split_documents(documents)
print(f"   -> 切分成功！共切成了 {len(texts)} 个碎片。")

# --- C. 建库 (Store) ---
print("正在建立向量数据库 (调用阿里云 text-embedding-v1)...")
# 【修改点 2】使用阿里云的嵌入模型
# model="text-embedding-v1" 是性价比很高的选择

embeddings = DashScopeEmbeddings(model="text-embedding-v1",dashscope_api_key=os.getenv('ALIYUN_API_KEY'))
# 将向量存入 Chroma 本地数据库
db = Chroma.from_documents(documents = texts,embedding = embeddings)

retriever = db.as_retriever(search_kwargs={"k": 6})



system_template = """
你是一个专业的特斯拉财报分析师。
请基于以下检索到的上下文来回答问题。如果你在文中找不到答案，就说不知道。

<context>
{context}
</context>
"""

# 2. 构建 ChatPromptTemplate
# system 部分只包含 {context}
# human 部分包含 {input} (你的问题)
prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", "{input}"),
])

llm = ChatTongyi(model="qwen-turbo",dashscope_api_key=os.getenv('ALIYUN_API_KEY'))

# 构建文档链 + 检索链
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 5. 提问
# 加上英文关键词 "Gross Margin"
question = "特斯拉本季度的 Gross Margin (毛利率) 是多少？请找一下 GAAP Gross Margin 的数据。"
print(f"🚀 提问: {question}")
response = rag_chain.invoke({"input": question})

print("-" * 30)
print(f"回答: {response['answer']}")
print("-" * 30)

# --- 打印 AI 参考的原文 ---
print("\n🔍 AI 参考了以下内容 (Context):")
print("-" * 30)
# 从 response 中提取 source_documents (新版链式写法会自动包含在 context 中)
for i, doc in enumerate(response["context"]):
    # 只打印前 100 个字，防止刷屏
    print(f"[片段 {i+1}] 内容摘要: {doc.page_content[:100]}...") 
    print(f"       (来自第 {doc.metadata.get('page', '?')} 页)")
    print("-" * 20)


