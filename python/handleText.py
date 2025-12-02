def handleText(text):
# 字符串处理空格以及统计字符串的长度
 newText = text.replace(" ","")
 textLength = len(newText)
 return newText,textLength

demo = handleText('我是小猪   时代峰峻客户端  是的粉丝的饭')
print(demo)