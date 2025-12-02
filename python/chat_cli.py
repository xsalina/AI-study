import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


# 找到当前脚本所在目录（B 目录）
current_dir = Path(__file__).parent

# 指定 .env 路径
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)

client = OpenAI()

print('=== 欢迎使用 AI机器人聊天（gpt-3.5-turbo） ===')
print('输入 exit 退出\n')



def getResponse(value):
    try:
        respones = client.responses.create(
            model="gpt-3.5-turbo",
            input=value
        )
        return respones.output_text # 直接返回字符串
    except Exception as e:
        # 如果想特别处理额度不足，可以检查字符串
        if "insufficient_quota" in str(e):
            return "⚠️ 当前账户额度不足，请充值或等待额度刷新"
        else:
            return f"调用出错: {e}"

def inputfun():
    while True:
        user_text = input('你：')
        if(user_text.strip().lower() == 'exit'):
            print("退出聊天")
            break
        res = getResponse(user_text)
        print("AI:", res, "\n")
            
if __name__ == "__main__":
    inputfun()

