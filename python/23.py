# Day 23: Python 界的 Next.js (FastAPI 入门)
# 任务: 搭建第一个 AI 后端服务。
# 技术: FastAPI, Pydantic (数据校验), Swagger UI (自动文档)。
# 成果: 访问 localhost:8000/docs，看到你自己写的 API 文档。



from fastapi import FastAPI
from pydantic import BaseModel
import time

# fastapi: 类似于 Express.js，负责定义路由 (/chat, /login)。
# uvicorn: 这是一个服务器（Server），类似于 Node.js 的运行时，专门用来把 FastAPI 跑起来。


# 1. 初始化 APP (类似于 const app = express())
app = FastAPI(
    title = 'MY AI BackEnd',
    description = '这是我的ai后端服务',
    version = 'V1.0.0'
)


# 2. 定义数据模型 (这就像 TypeScript 的 Interface!)
# Pydantic 是 FastAPI 的灵魂。
# 它强制规定：前端发给我的 JSON，必须包含 content 字段，且必须是 string。
# 如果前端乱发数据，FastAPI 会自动拦截并报错，不用你写 if-else 判断。
class ChatRequest(BaseModel):
    query:str # 用户的问题 (必填)
    stream: bool = False # 是否流式输出 (选填，默认 False)

class ChatResponese(BaseModel):
    answer: str
    timestamp:float


# 3. 写一个 GET 接口 (类似于 app.get('/', ...))
# 访问 http://localhost:8000/ 时触发

@app.get('/')
def read_root():
    return {"message":'API 服务已在线！请访问 /docs 查看文档'}


# 4. 写一个 POST 接口 (核心业务)
# 访问 http://localhost:8000/chat 时触发
# response_model=ChatResponse 告诉 API：我承诺返回的数据长这样
@app.post("/docs",response_model = ChatResponese)
def chat_endpoint(request:ChatRequest):
    # request 变量里已经自动装好了前端发来的 JSON 数据
    print(f"📥 后端收到请求: {request.query}")
    # --- 模拟 AI 思考过程 (今天先不接真 AI) ---
    # 假装思考了 1 秒
    time.sleep(1)

    fake_answer = f"后端成功收到了你的问题：'{request.query}'。但我现在只是个空壳API，明天我会接上大脑的🧠"

    # 返回符合 ChatResponse 格式的 JSON
    return {
        'answer': fake_answer,
        'timestamp':time.time()
    }


