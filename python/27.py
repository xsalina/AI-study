
# Day 27: 专业的 Markdown 渲染与交互
# 任务: 让聊天气泡支持代码高亮、表格、公式。
# 技术: react-markdown, syntax-highlighter。
# 成果: 一个界面精美、交互丝滑的 AI 聊天窗口。





import os
import shutil
import tempfile
import time # <--- 新增这行
from fastapi import FastAPI,UploadFile,File,Form,HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv



from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
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
    # 找到 system_prompt，替换成下面这段：
    
    system_prompt = """
    你是一个智能助手。
    请优先基于以下 Context 回答问题。
    
    【重要规则】
    1. 如果 Context 里有答案，请依据 Context 回答。
    2. 如果 Context 里没有答案（比如用户问通用知识、代码问题），请**使用你自己的知识**回答，不要说不知道。
    3. 如果需要写代码，请使用 Markdown 代码块格式。
    4. 如果涉及对比，请尽量使用 Markdown 表格。
    
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


# --- 新增：流式提问接口 (Day 25 核心) ---
@app.post('/chat/stream')
async def chat_stream(request:ChatRequest):
    # 1. 检查 Session
    if request.session_id not in RAG_CHAINS:
        raise HTTPException(status_code=400, detail="请先上传 PDF 文件！")
    
    chain = RAG_CHAINS[request.session_id]
    
    print(f"🌊 用户 {request.session_id} 正在进行流式提问: {request.query}")
    # 2. 定义生成器函数
    def generate_response():
        # chain.stream() 会自动一个字一个字地吐数据
        for chunk in chain.stream({"input":request.query}):
            # LangChain 的 stream 返回的很碎，我们需要提取出 answer 部分
            if "answer" in chunk:
                content = chunk["answer"]
                if content:
                    # 🐌 【新增】人工延迟：每输出一个块，暂停 0.05 秒
                    # 你可以调整这个数字：0.02 很流畅，0.1 就很有“老电影打字机”的感觉
                    yield content
    # 3. 把生成器交给 FastAPI 的传送带
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream" # 告诉浏览器：我是流，别急着断开
    )



