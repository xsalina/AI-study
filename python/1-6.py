from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI


# **Day 6 — 完成 CLI ChatGPT 应用**
# 内容：循环输入、流式打印
# 练习：完成 CLI 版本“ChatGPT Mini”


# 理解：
#     1️⃣.循环输入（Loop Input）本质就是：
#     程序一直等待用户输入 → AI 回复 → 再等待输入 → 再回复 → 无限循环……直到你主动退出。
#     2️⃣流式打印让 AI 的回答不是一次性出现，而是一边生成一边输出
# 目标：
#     ① 做一个命令行的循环聊天程序
#     ② 让 AI 的回答不是一次性出现，而是一边生成一边输出


current_dir = Path(__file__).parent

env_path = current_dir/".env"

load_dotenv(dotenv_path=env_path)

client = OpenAI()





messages = []


def loopGpt(value):
    try:
        stream = client.responses.create(
            model = "gpt-3.5-turbo",
            input = value,
            messages = messages,
            stream = True
        )
        # 因为是stream为true是事件流，所以返回的需要for循环 每个event对象的值如下
         # event={
        #     "type": "response.completed",//最后结束的时候才会有这个值，其他值是response.output_text.delta
        #     "data": {
        #         "delta": "",//每段流输出的文案
        #         "finish_reason": ""，//最后结束的时候才会有这个值
        #     },
        #     "response": {
        #         "output_text": ""，//最后结束的时候才会有这个值，是输出的完整的文案
        #     }
        # }
        for event in stream:
            for ch in event.data.delta:
                print(ch,end='',flush=True)
                # end:
                #     作用：控制 print() 打印完成后在结尾加什么
                #     默认值：\n（换行）
                # flush:
                #     作用：是否立即把内容输出到屏幕，而不是先缓存起来
                #     默认值：False（有缓存，Python 会自动分批输出）   
            if(event.type == 'response.completed'):
                print()  # 换行
                messages.append({"role":'assistant',"content":event.response.output_text})

    except Exception as e:
        # 如果想特别处理额度不足，可以检查字符串
        if "insufficient_quota" in str(e):
            print("⚠️ 当前账户额度不足，请充值或等待额度刷新")
        else:   
            print(f"调用出错: {e}")



def inputValue():
     while True:
        text = input('你：')
        if(text.strip().lower() == 'exit'):
            print('退出')
            break
        messages.append({"role":"user","content":text})
        loopGpt(text)


if __name__ == '__main__':
        inputValue()



        # 整句话：
        #     “我是杀马特，我住在黄土高坡上”，
        # 然后使用流之后的，每个event对象的值分3段，具体几段根据文案的AI来分，我们来举个例子，这段话分3段，event返回的三个event
        # 1.{
        #     "type": "response.output_text.delta",
        #     "data": {
        #         "delta": "我是杀马特，",
        #         "finish_reason": null
        #     },
        #     "response": {
        #         "output_text": null
        #     }
        # }
        # 2.{
        #     "type": "response.output_text.delta",
        #     "data": {
        #         "delta": "我住在",
        #         "finish_reason": null
        #     },
        #     "response": {
        #         "output_text": null
        #     }
        # }
        # 3.{
        #     "type": "response.completed",
        #     "data": {
        #         "delta": "",
        #         "finish_reason": "stop"
        #     },
        #     "response": {
        #         "output_text": "我是杀马特，我住在黄土高坡上"
        #     }
        # }



