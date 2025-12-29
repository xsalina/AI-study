import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

function App() {
  const [input, setInput] = useState("")
  const [answer, setAnswer] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const sendQuestion = async () => {
    if(!input.trim()) return;
    //清空上一轮
    setAnswer("")
    setIsLoading(true)
    try {
      // 2. 发起 Fetch 请求
      // 注意：这里必须是 POST，且要带上 Content-Type
      const response = await fetch('http://localhost:8000/chat/stream',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({query:input,session_id:'user1'})
      })
      if(!response.body) return new Error('不支持流式传输')
      const reader = response.body.getReader();
      const decoder = new TextDecoder()
      while(true){
        // value 是二进制数据，done 标记是否结束
        const {done,value} = await reader.read()
        if(done) break;// 水流完了，收工
        // 解码：二进制 -> 文本 ("特", "斯", "拉")
        const textChunk = decoder.decode(value,{stream:true})
        // 累加答案
        setAnswer((prev) => prev + textChunk)


      }



    } catch (error) {
      console.error("请求出错:",error)
    }finally{
      setIsLoading(false)
    }
  }

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🤖 React + FastAPI 流式 AI</h1>
      
      {/* 答案显示区 */}
      <div style={{ 
        textAlign: 'left', 
        minHeight: '200px', 
        padding: '20px', 
        border: '1px solid #ddd', 
        borderRadius: '8px',
        marginBottom: '20px',
        background: '#f9f9f9',
        color:'red'
      }}>
        {/* 使用 Markdown 组件渲染 */}
        {answer ? <ReactMarkdown>{answer}</ReactMarkdown> : <span style={{color:'#ccc'}}>AI 正在待命...</span>}
      </div>

      {/* 输入框区域 */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <input 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendQuestion()}
          placeholder="问点什么，比如：特斯拉毛利率是多少？"
          style={{ flex: 1, padding: '10px', fontSize: '16px' }}
        />
        <button 
          onClick={sendQuestion} 
          disabled={isLoading}
          style={{ padding: '10px 20px', cursor: 'pointer' }}
        >
          {isLoading ? "思考中..." : "发送"}
        </button>
      </div>
    </div>
  )
}

export default App
