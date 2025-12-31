import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm' // New: 导入 GFM 插件
import CodeBlock from './components/CodeBlock' // New: 导入刚才写的组件

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
      console.log(34578345,response)
      if(!response.body) return new Error('不支持流式传输')
      const reader = response.body.getReader();
      const decoder = new TextDecoder()
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
            // 🛑 【新增】循环结束时，看看解码器里有没有剩下的渣渣
            // 不加 {stream: true} 表示这是最后一次，强制清空缓存
            const lastChunk = decoder.decode(); 
            if (lastChunk) {
                setAnswer(prev => prev + lastChunk);
            }
            break; 
        }

        const textChunk = decoder.decode(value, { stream: true });
        // 🐞 【调试】把这行加上，看看控制台打印了什么！
        console.log("收到的碎片:", textChunk); 
        
        setAnswer(prev => prev + textChunk);
      }


    } catch (error) {
      console.error("请求出错:",error)
    }finally{
      setIsLoading(false)
    }
  }
const formatMarkdown = (content) => {
  if (content === null || content === undefined) return '';
  
  // 核心：哪怕进来的 content 是字符串，我们也防一手
  let text = content;
  
  // 如果是数组，强行拼成字符串
  if (Array.isArray(content)) {
    text = content.join('');
  } else if (typeof content !== 'string') {
    // 如果是数字或对象，转字符串
    text = String(content);
  }

  // 此时 text 100% 是字符串，再做正则替换
  return text.replace(/\n-/g, '\n\n-').replace(/\n(\d+)\./g, '\n\n$1.');
};

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🤖 React + FastAPI + SyntaxHighlighter</h1>
      
      {/* 答案显示区 */}
      <div style={{ 
        textAlign: 'left', 
        minHeight: '200px', 
        padding: '20px', 
        border: '1px solid #ddd', 
        borderRadius: '8px',
        marginBottom: '20px',
        background: '#f9f9f9',
        color:'red',
        // 这一行是为了防止表格溢出
        overflowX: 'auto'
      }}>
        {/* --- 核心修改在这里 --- */}
        <ReactMarkdown 
            remarkPlugins={[remarkGfm]} 
            // ...其他配置
        >
            {answer} 
        </ReactMarkdown>
        {/* --------------------- */}
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
