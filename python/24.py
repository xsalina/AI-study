# Day 24: 核心逻辑迁移 (Logic Porting)
# 任务: 把 Day 21-22 的 LangChain 代码搬进 FastAPI。
# 技术: 依赖注入 (Dependency Injection), 环境变量管理 (.env in Prod)。
# 成果: 用 Postman 发送请求，收到 AI 基于 PDF 的回复。


import os
import shutil
import tempfile
from fastapi import FastAPI,UploadFile,File,Form,HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv


from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


# 初始化app
app = FastAPI(
    title = 'Day 24: AI 后端架构'
)

# --- 2. 核心架构：全局仓库 (Global Storage) ---
RAG_CHAINS = { }  # 用于存储每个用户的 RAG Chain 实例   

class ChatRequest(BaseModel):
    session_id: str = "default_user"
    query: str



# --- 4. 核心逻辑函数 (只负责造大脑，不负责网络) ---
def build_rag_chain_from_file(local_pdf_path):
    print(f"⚙️ 开始处理文件: {local_pdf_path} ...")
    # A. 加载
    pdf = PyPDFLoader(local_pdf_path)
    docs = pdf.load()
    print("⚙️ 正在调用 tempfile11...")
    # 切分
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    print(f"📄 文档已切分为 {len(splits)} 段。")

    print("⚙️ 正在调用 tempfile22...")
    # 建库
    embeddings = DashScopeEmbeddings(model="text-embedding-v1", dashscope_api_key=os.getenv("ALIYUN_API_KEY"))
    vectorstore = Chroma.from_documents(documents=splits,embedding=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k":5})
    print("⚙️ 正在调用 tempfile33...")

    # D. 构建链 (简单的问答链，暂不加复杂记忆，保证先跑通)
    system_prompt ="""
    你是一个专业的分析师，请基于以下Context 回答问题。
    如果Context没有答案，请直接说未找到相关信息，不要编造答案。
    <context>
    {context}
    </context>
    """
    prompt = ChatPromptTemplate.from_messages([("system",system_prompt),("human","{input}"),])
    print("⚙️ 正在调用 tempfile44...")

    llm = ChatTongyi(model="qwen-turbo",dashscope_api_key=os.getenv("ALIYUN_API_KEY"))
    print("⚙️ 正在调用 tempfile55...")
    question_answer_chain = create_stuff_documents_chain(llm,prompt)
    rag_chain = create_retrieval_chain(retriever,question_answer_chain)

    print("✅ RAG 链构建完成！")
    return rag_chain







@app.post("/upload")

async def upload_pdf(session_id: str = Form('default_user'), file: UploadFile = File(...)):
    # 1. 保存上传的文件到临时目录
    # (FastAPI 接收的是内存流，PyPDFLoader 需要物理路径，所以要存一下)
    with tempfile.NamedTemporaryFile(delete=False,suffix='.pdf') as tmp_file:
        shutil.copyfileobj(file.file,tmp_file)
        tmp_path = tmp_file.name
    try:
        print("⚙️ 正在调用 tempfile...")
        
        # 2. 调用上面的逻辑函数，生成 AI 大脑
        rag_chain = build_rag_chain_from_file(tmp_path)
        # 3. 把造好的大脑存进全局字典
        RAG_CHAINS[session_id] = rag_chain
        return {
            "message": "PDF 处理成功！大脑已激活，可以开始提问了。",
            "filename":file.filename,
            "session_id":session_id
        }
    
    except Exception as e :
        print(f"出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 4. 清理垃圾 (删除那个临时存的 PDF)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)



@app.post("/chat")
def chat(request:ChatRequest):
    # 先查这个户口有没有上传过
    if request.session_id not in RAG_CHAINS:
        raise HTTPException(status_code = 400, detail="请先上传文件")
    
    # 取出大脑
    brain = RAG_CHAINS[request.session_id]

    print(f"💬 用户 {request.session_id} 问: {request.query}")

    # 3. 思考 (Invoke)

    response = brain.invoke({"input":request.query})


    # 3. 假装回答
    return {
        "answer": response["answer"],
        # 这里我们也把参考来源返回去，显得专业
        "sources":[doc.page_content[:50] + "..." for doc in response["context"]]
    }



