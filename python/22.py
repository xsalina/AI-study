# Day 22: 让对话更像人 (Memory & History)
# 任务: 给 AI 加上“短期记忆”。
# 技术: RunnableWithMessageHistory。
# 痛点解决: 解决“AI 每一句话都忘记上一句话说了啥”的问题，实现连续多轮对话。



# 📝 现在的总结
# 把代码复原，现在你再看那几行代码，它们不再是神秘的字符，而是具体的工序：

# PyPDFLoader: 搬运工，把书搬进电脑。

# RecursiveCharacterTextSplitter: 厨师，把牛排切成 AI 咬得动的小块。

# Chroma & Embeddings: 图书管理员，把文字变成数字索引，方便查找。

# history_aware_retriever: 翻译官，把你那句含糊不清的“它好吗？”，翻译成精准的搜索指令。

# ChatTongyi: 最终的考生，根据搜到的小抄写出答案。


import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

# --- 1. 基础配置 ---
load_dotenv()
st.set_page_config(page_title="ChatPDF Pro (记忆版)", layout="wide", page_icon="🧠")

# 检查 Key
if not os.getenv("ALIYUN_API_KEY"):
    st.error("❌ 未检测到 API Key，请检查 .env 文件！")
    st.stop()

# --- 2. 导入组件 ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 核心链组件
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

# 【Day 22 核心组件】历史感知检索器
from langchain_classic.chains import create_history_aware_retriever

# --- 3. 辅助函数：翻译机 ---
def translate_to_english(text):
    """把中文问题转成英文关键词，提高检索准确率"""
    llm_trans = ChatTongyi(model="qwen-turbo",dashscope_api_key=os.getenv('ALIYUN_API_KEY'))
    # 简单的翻译指令
    res = llm_trans.invoke(f"Translate the following Chinese text to English. Only output the translation, do not add any explanation: {text}")
    return res.content

# --- 4. 核心处理函数 (带记忆构建) ---
@st.cache_resource
def process_pdf_and_build_rag(uploaded_file):
    """
    加载 PDF -> 切分 -> 建库 -> 返回一个【带记忆能力】的 RAG 链
    """
    # A. 临时文件处理
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # B. 加载 & 切分
        loader = PyPDFLoader(tmp_file_path)
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=250)
        splits = text_splitter.split_documents(docs)

        # C. 建库
        embeddings = DashScopeEmbeddings(model="text-embedding-v1",dashscope_api_key=os.getenv('ALIYUN_API_KEY'))
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 6})

        llm = ChatTongyi(model="qwen-turbo",dashscope_api_key=os.getenv('ALIYUN_API_KEY')) # 或者 qwen-plus

        # --- D. 【关键升级】构建“历史感知”检索器 ---
        # 它的作用：如果用户问“它增长了吗？”，结合历史把它改成“特斯拉的营收增长了吗？”
        
        contextualize_q_system_prompt = """
        Given a chat history and the latest user question which might reference context in the chat history, 
        formulate a standalone question which can be understood without the chat history. 
        Do NOT answer the question, just reformulate it if needed and otherwise return it as is.
        """
        
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"), # 👈 这里的坑填历史记录
            ("human", "{input}"),
        ])
        
        # 这个 retriever 会先思考改写问题，再去搜索
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        # --- E. 构建回答链 ---
        
        # 这里的 Prompt 负责根据搜到的素材回答问题
        qa_system_prompt = """
        You are a professional Financial Analyst.
        Use the following pieces of retrieved context to answer the question.
        
        Important Rules:
        1. The Context is likely in English, but you MUST answer in CHINESE (中文).
        2. If you don't know the answer, say "财报中未提及".
        
        <context>
        {context}
        </context>
        """
        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"), # 👈 回答时也要看一眼历史，防止语境断裂
            ("human", "{input}"),
        ])
        
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        
        # 将“聪明检索器”和“回答链”串起来
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        return rag_chain

    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

# --- 5. 界面 UI ---

st.title("🧠 智能财报助手 (记忆+翻译版)")
st.caption("Day 22 成果：支持多轮对话、代词指代、跨语言检索")

# 侧边栏
with st.sidebar:
    st.header("📂 第一步：上传文档")
    uploaded_file = st.file_uploader("请上传 PDF 财报", type=["pdf"])

# 主逻辑
if uploaded_file:
    # 1. 启动
    try:
        with st.spinner("正在构建知识库..."):
            rag_chain = process_pdf_and_build_rag(uploaded_file)
        st.success("✅ 大脑已就绪！")
    except Exception as e:
        st.error(f"出错啦: {e}")
        st.stop()

    # 2. 初始化历史记录 (Session State)
    # 界面显示用
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # LangChain 记忆专用 (存对象)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # 3. 显示历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 4. 处理输入
    if user_input := st.chat_input("比如：特斯拉营收多少？(然后可以接着问：那比去年高吗？)"):
        # 显示用户问题
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # AI 回答
        with st.chat_message("assistant"):
            with st.status("🧠 AI 正在思考...", expanded=True) as status:
                
                # Step 1: 翻译 (为了搜得准)
                status.write("🔄 1. 正在优化搜索关键词 (中->英)...")
                english_query = translate_to_english(user_input)
                status.write(f"🇺🇸 检索词: *{english_query}*")
                
                # Step 2: 检索 + 生成 (带记忆)
                status.write("🔍 2. 结合上下文检索文档...")
                
                # --- 关键调用 ---
                # 同时传入 input (当前问题) 和 chat_history (过去的历史)
                response = rag_chain.invoke({
                    "input": english_query, 
                    "chat_history": st.session_state.chat_history
                })
                
                status.update(label="✅ 分析完成", state="complete", expanded=False)
            
            answer = response['answer']
            st.markdown(answer)

            # 引用展示
            with st.expander("查看参考原文"):
                for i, doc in enumerate(response["context"]):
                    st.markdown(f"**[片段 {i+1}]**")
                    st.caption(doc.page_content[:200] + "...")

        # 5. 更新记忆库
        # 存入界面历史
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        # 存入 LangChain 记忆 (注意：存的是英文 query 还是中文 query？)
        # 策略：为了让 AI 理解用户的中文追问，这里存【中文原话】会更自然，因为我们在内部用 LLM 做改写
        st.session_state.chat_history.extend([
            HumanMessage(content=user_input), # 存中文，因为改写器能看懂中文
            AIMessage(content=answer)
        ])

else:
    st.info("👈 请先上传 PDF 文件")