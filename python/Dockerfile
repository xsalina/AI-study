# 位于 AI-LEAN-PLAN/python/Dockerfile

FROM python:3.10-slim

WORKDIR /app

# 复制当前目录(即 python 文件夹)下的 requirements.txt
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 复制当前目录下的所有文件到容器
COPY . .

EXPOSE 8000

# ⚠️ 关键修改：
# 因为你的文件名是 29.py，所以这里是 29:app
# 假设你在 29.py 里写的代码是 app = FastAPI()
CMD ["sh", "-c", "uvicorn 28:app --host 0.0.0.0 --port ${PORT:-8000}"]