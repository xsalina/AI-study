import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import CodeBlock from './components/CodeBlock'

// --- 🎨 定义专业风格常量 ---
const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f4f6f9', // 更现代的浅灰背景
    padding: '40px 20px',
    display: 'flex',
    justifyContent: 'center',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
  },
  card: {
    width: '100%',
    maxWidth: '900px', // 加宽一点，更大气
    backgroundColor: '#ffffff',
    borderRadius: '16px', // 更大的圆角
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)', // 微妙的高级阴影
    padding: '35px',
    display: 'flex',
    flexDirection: 'column',
    gap: '25px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '10px',
  },
  title: {
    fontSize: '1.8rem',
    fontWeight: '700',
    color: '#1a1a1a',
    margin: '0 0 10px 0',
  },
  subtitle: {
    color: '#666',
    fontSize: '0.95rem',
  },
  uploadSection: {
    paddingBottom: '20px',
    borderBottom: '1px solid #eaeaea', // 用细线分隔，代替粗糙的背景框
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '15px'
  },
  uploadLabel: {
    fontSize: '1.1rem',
    fontWeight: '600',
    color: '#333',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  },
  fileInputWrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: '15px',
    backgroundColor: '#f9fafb',
    padding: '8px 15px',
    borderRadius: '8px',
    border: '1px solid #e5e7eb'
  },
  button: {
    padding: '10px 24px',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontSize: '0.95rem',
    boxShadow: '0 2px 5px rgba(0,0,0,0.1)'
  },
  primaryButton: {
    backgroundColor: '#0066FF', // 专业科技蓝
    color: 'white',
  },
  successButton: {
    backgroundColor: '#10B981', // 现代绿
    color: 'white',
  },
  disabledButton: {
    backgroundColor: '#e5e7eb',
    color: '#9ca3af',
    cursor: 'not-allowed',
    boxShadow: 'none'
  },
  chatWindow: {
    flexGrow: 1,
    minHeight: '400px', // 增加高度
    backgroundColor: '#fcfcfd', // 极淡的背景色区分
    border: '1px solid #edeff2',
    borderRadius: '12px',
    padding: '30px',
    overflowY: 'auto',
    position: 'relative',
  },
  emptyState: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    color: '#aaa',
    textAlign: 'center',
    pointerEvents: 'none',
  },
  inputArea: {
    display: 'flex',
    gap: '15px',
    marginTop: 'auto', // 将输入框推到底部
    paddingTop: '20px',
    borderTop: '1px solid #eaeaea'
  },
  inputField: {
    flex: 1,
    padding: '14px 20px',
    fontSize: '1rem',
    border: '1px solid #e5e7eb',
    borderRadius: '10px',
    outline: 'none',
    transition: 'border-color 0.2s',
    boxShadow: '0 2px 5px rgba(0,0,0,0.03) inset'
  },
};


function App() {
  const [input, setInput] = useState("")
  const [answer, setAnswer] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [isUploading, setIsUploading] = useState(false)

  // 这里的 session_id 必须和下面聊天时的一致，才能查到数据
  const SESSION_ID = 'user1'

  const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0])
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("请先选择一个 PDF 文件！")
      return
    }
    setIsUploading(true)

    const formData = new FormData()
    formData.append("file", selectedFile)
    formData.append("session_id", SESSION_ID)

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
      })
      if (response.ok) {
        alert("✅ 上传成功！知识库已更新。")
        setSelectedFile(null)
        // 重置 file input
        document.getElementById('fileInput').value = '';
      } else {
        alert("❌ 上传失败")
      }
    } catch (error) {
      console.error("上传错误:", error)
      alert("网络错误")
    } finally {
      setIsUploading(false)
    }
  }

  const sendQuestion = async () => {
    if (!input.trim()) return;
    setAnswer("")
    setIsLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input, session_id: SESSION_ID })
      })

      if (!response.body) return new Error('不支持流式传输')
      const reader = response.body.getReader();
      const decoder = new TextDecoder()
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          const lastChunk = decoder.decode();
          if (lastChunk) {
            setAnswer(prev => prev + lastChunk);
          }
          break;
        }
        const textChunk = decoder.decode(value, { stream: true });
        setAnswer(prev => prev + textChunk);
      }
    } catch (error) {
      console.error("请求出错:", error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div style={styles.container}>
        {/* 添加一个全局样式来优化 Markdown 的显示效果 */}
        <style>{`
            .markdown-body { line-height: 1.7; color: #333; }
            .markdown-body h1, .markdown-body h2, .markdown-body h3 { margin-top: 1.5em; margin-bottom: 0.8em; color: #111; }
            .markdown-body p { margin-bottom: 1.2em; }
            .markdown-body ul, .markdown-body ol { padding-left: 1.5em; margin-bottom: 1.2em; }
            .markdown-body li { margin-bottom: 0.5em; }
            .markdown-body strong { color: #000; font-weight: 600; }
        `}</style>

      <div style={styles.card}>
        {/* Header */}
        <div style={styles.header}>
          <h1 style={styles.title}>✨ AI 智能知识库</h1>
          <p style={styles.subtitle}>基于您的私有文档，进行精准问答</p>
        </div>

        {/* 上传区域 - 简化设计 */}
        <div style={styles.uploadSection}>
          <div style={styles.uploadLabel}>
            <span style={{fontSize: '1.3rem'}}>📚</span>
            <span>文档管理</span>
          </div>
          <div style={styles.fileInputWrapper}>
            <input
              id="fileInput"
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              style={{ fontSize: '0.9rem', color: '#555' }}
            />
            <button
              onClick={handleUpload}
              disabled={isUploading || !selectedFile}
              style={{
                ...styles.button,
                ...(isUploading || !selectedFile ? styles.disabledButton : styles.successButton)
              }}
            >
              {isUploading ? "⏳ 上传中..." : "🚀 上传至云端"}
            </button>
          </div>
        </div>

        {/* 答案显示区 - 增加高度和留白 */}
        <div style={styles.chatWindow} className="markdown-body">
          {!answer && !isLoading && (
            <div style={styles.emptyState}>
              <p style={{fontSize: '3rem', margin: 0}}>🤖</p>
              <p>请在下方输入问题，开始对话</p>
            </div>
          )}
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code: CodeBlock
            }}
          >
            {answer}
          </ReactMarkdown>
        </div>

        {/* 输入框区域 - 更现代的样式 */}
        <div style={styles.inputArea}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendQuestion()}
            placeholder="💡 请输入您的问题，例如：这份文档的核心观点是什么？"
            style={styles.inputField}
            onFocus={(e) => e.target.style.borderColor = '#0066FF'}
            onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
          />
          <button
            onClick={sendQuestion}
            disabled={isLoading || !input.trim()}
            style={{
              ...styles.button,
              ...(isLoading || !input.trim() ? styles.disabledButton : styles.primaryButton),
               padding: '10px 30px' // 发送按钮稍微宽一点
            }}
          >
            {isLoading ? "🤔 思考中..." : "发送"}
          </button>
        </div>
      </div>
    </div>
  )
}

export default App