

import streamlit as st
import os
import tempfile
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



# 新增一个独立的翻译函数 (不走 RAG，直接问大模型)
# -------------------------------------------------------------
def translate_to_english(text, api_key):
    # 使用轻量级模型快速翻译
    llm_trans = ChatTongyi(model="qwen-turbo", dashscope_api_key=os.getenv('ALIYUN_API_KEY'))
    # 简单的翻译指令
    res = llm_trans.invoke(f"Translate the following Chinese text to English. Only output the translation, do not add any explanation: {text}")
    return res.content




st.set_page_config(page_title="ChatPDF Pro", layout="wide")



# --- 2. 页面基础设置 ---
# --- 3. 核心处理函数 (使用缓存加速) ---
# @st.cache_resource 保证同一个文件上传后，不会因为你每次提问都重新去切分、建库
@st.cache_resource
def process_pdf_and_build_rag(uploaded_file):
    """
    接收上传的文件对象 -> 保存临时文件 -> 读取 -> 切分 -> 建库 -> 返回检索链
    """
    # A. 处理临时文件 (PyPDFLoader 需要物理路径)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
        try:
            # B. 加载
            loader = PyPDFLoader(tmp_file_path)
            docs = loader.load()

            # C. 切分
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=250
            )
            splits = text_splitter.split_documents(docs)

            # D. 建库 (自动使用环境变量里的 Key)
            embeddings = DashScopeEmbeddings(model="text-embedding-v1",dashscope_api_key=os.getenv('ALIYUN_API_KEY'))
            vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
            # E. 构建链
            system_template = """
            你是一个专业的分析师。
            请基于以下检索到的上下文来回答问题。如果你在文中找不到答案，就说不知道。
            
            <context>
            {context}
            </context>
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                ("human", "{input}"),
            ])
            llm = ChatTongyi(model="qwen-turbo",dashscope_api_key=os.getenv('ALIYUN_API_KEY')) # 自动读取环境变量 Key
            
            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)
            
            return rag_chain

        finally:
            # 清理临时文件，保持服务器卫生
            os.remove(tmp_file_path)

# --- 4. 界面 UI 设计 ---

st.title("📄 智能文档分析助手 (ChatPDF)")
st.caption("基于阿里云通义千问 | 自动读取后台配置")
st.header("📂 第一步：上传文档")
uploaded_file = st.file_uploader("请上传 PDF 文件", type=["pdf"])
st.markdown("---")
st.markdown("**说明：**\n1. 上传后系统会自动解析\n2. 解析完成后即可在右侧提问")
# 主区域：聊天区
if uploaded_file:
    # 1. 只有上传了文件，才启动 RAG 系统
    try:
        with st.spinner("正在分析文档，建立知识库... (文档越大越慢，请耐心等待)"):
            rag_chain = process_pdf_and_build_rag(uploaded_file)
        st.success(f"✅ 文档《{uploaded_file.name}》解析完成！")
        
        # 2. 聊天界面
        st.markdown("### 💬 第二步：开始提问")
        
        # 初始化聊天历史
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 显示历史
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 处理输入
        if user_input := st.chat_input("比如：特斯拉本季度的毛利率是多少？"):
            # 显示用户问题
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            # AI 回答
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("🤔 正在思考...")
                
                # 调用 RAG
                response = rag_chain.invoke({"input": user_input})
                answer = response['answer']
                
                message_placeholder.markdown(answer)
                
                # 可选：显示参考来源 (Expander 折叠显示)
                with st.expander("查看 AI 参考的原文片段"):
                    for i, doc in enumerate(response["context"]):
                        st.markdown(f"**[片段 {i+1}] (第 {doc.metadata.get('page','?')} 页):**")
                        st.text(doc.page_content[:200] + "...")

            # 保存 AI 回答
            st.session_state.messages.append({"role": "assistant", "content": answer})
    finally:
        # 清理临时文件，保持服务器卫生
        print('失败了')

else:
    # 如果没上传文件的引导页
    st.info("👈 请先在左侧侧边栏上传一份 PDF 财报或文档。")






