# Day 28: 记忆持久化 (Vector DB 云端化)
# 任务: 从本地内存向量库迁移到云端数据库。
# 技术: Pinecone 或 Supabase (pgvector)。
# 意义: 即使服务器重启，你上传过的文档索引依然存在。


import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# --- LangChain 组件 ---
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# --- 【NEW】引入 Pinecone 组件 ---
from langchain_pinecone import PineconeVectorStore

# 加载环境变量
load_dotenv()

# --- 初始化 APP ---
app = FastAPI(title='Day28 :piencone 云端知识库')

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

# --- 全局配置 ---
# 你的 Pinecone 索引名字 (必须和你在网页上创建的一模一样！)
# 比如你刚才起名叫 day28-rag，这里就填 day28-rag

PINECONE_INDEX_NAME = 'day28-rag'

class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_user"

# --- 核心逻辑 A: 上传并存入 Pinecone ---
@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...), 
    session_id: str = Form("default_user") 
):
    print(f"📥 收到文件: {file.filename}, 准备存入 Namespace: {session_id}")
    
    # 1. 保存临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name

    try:
        # 2. 加载 PDF
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        
        # 3. 切分
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # 4. 初始化 Embedding 模型
        embeddings = DashScopeEmbeddings(model="text-embedding-v1",dashscope_api_key=os.getenv('ALIYUN_API_KEY'))
        
        print("☁️ 正在把数据推送到 Pinecone 云端 (这可能需要几秒钟)...")

        # 5. 【NEW】存入 Pinecone
        # 重点：namespace=session_id 实现了用户数据隔离！
        PineconeVectorStore.from_documents(
            documents=splits,
            embedding=embeddings,
            index_name=PINECONE_INDEX_NAME,
            namespace=session_id,   # <--- 关键！数据被贴上了“属于session_id”的标签
        )
        print(f"✅ 存储成功！Namespace: {session_id}")
        return {
            "message": "PDF 已存入云端数据库，永久保存！",
            "filename": file.filename,
            "session_id": session_id
        }
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)



# --- 核心逻辑 B: 从 Pinecone 检索并回答 (流式) ---
@app.post('/chat/stream')
async def chat_stream(request:ChatRequest):
    print(f"🔍 用户 {request.session_id} 提问: {request.query}")

    try:
        # 1. 准备 Embedding
        embeddings = DashScopeEmbeddings(model="text-embedding-v1",dashscope_api_key=os.getenv('ALIYUN_API_KEY'))
        # 2. 【NEW】连接到现有的 Pinecone 索引
        # 注意：这里我们只连接，不写入。
        # 必须指定 namespace，否则查不到刚才存的数据！
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings,
            namespace=request.session_id,  # <--- 关键！只去这个用户的抽屉里找

        )
        # 3. 转换成检索器
        retriever = vectorstore.as_retriever()

        # 4. 准备大脑 (LLM)
        llm = ChatTongyi(model='qwen-turbo',dashscope_api_key=os.getenv("ALIYUN_API_KEY"))

        system_prompt = """
        你是一个智能助手。请基于 Context 回答。
        如果 Context 里没有答案，请使用你的通用知识回答。
        使用 Markdown 格式。
        
        <context>
        {context}
        </context>
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))

        # 6. 生成器函数 (流式输出)
        def generate_response():
            try:
                for chunk in rag_chain.stream({"input": request.query}):
                    if "answer" in chunk:
                        content = chunk["answer"]
                        if content:
                            # 稍微人工延迟一点点，提升体验
                            yield content
            except Exception as e:
                # 如果生成过程中断网了，在这里报错给前端
                yield f"\n[Error: {str(e)}]"

        # 3. 返回流
        return StreamingResponse(
            generate_response(), 
            media_type="text/event-stream"
        )
    except Exception as e:
        # 【修复点】如果连不上 Pinecone，直接抛出 HTTP 500 错误，而不是 yield
        print(f"❌ 检索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))