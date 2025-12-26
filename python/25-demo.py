import time 
import requests
def ai_talking():
   print('🤖 我开始思考了')
   sentence = '我是特斯拉财报'
   for word in sentence:
      time.sleep(0.3)
      yield word

print('前端准备接收')


# generator = ai_talking()


# # 从循环带上拿上东西
# for chunk in generator:
#    print(chunk,end='',flush=True)


print('✅ 接收完毕')



url = 'http://localhost:8000/chat/stream'
data = {
   "query":'特斯拉毛利率是多少',
   "session_id":"user1"
}

print("开始请求。。。")

# stream=True 是关键！告诉 requests 库不要等结果，要建立长连接
with requests.post(url,json=data,stream=True) as response:
   for chunk in response.iter_content(chunk_size=1024):
      if chunk:
         # end='' 表示不换行，模拟打字机效果
         print(chunk.decode('utf-8'),end='',flush=True)



