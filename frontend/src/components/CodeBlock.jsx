import React, { useState } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// 选择一款你喜欢的主题，这里用类似 VS Code 的 dark 模式
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

// 这个组件会接收 react-markdown 传来的 props
// 其中 children 就是代码内容，className 包含了语言信息 (如 "language-python")
const CodeBlock = ({ node, inline, className, children, ...props }) => {
  const [isCopied, setIsCopied] = useState(false);

  // 1. 提取语言类型 (去掉 "language-" 前缀)
  const match = /language-(\w+)/.exec(className || '');
  const language = match ? match[1] : 'text';

  // 2. 如果是行内代码 (比如 `print`), 直接渲染文本，不用高亮也不用按钮
  if (inline) {
    return <code className={className} {...props}>{children}</code>;
  }

  // 3. 处理复制代码的逻辑
  const handleCopy = () => {
    // String(children) 确保我们要复制的是纯文本
    const text = String(children).replace(/\n$/, '');
    navigator.clipboard.writeText(text);
    
    // 给个反馈，显示 "Copied!" 2秒后消失
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  // 4. 返回自定义的高亮组件结构
  return (
    <div style={{ position: 'relative', margin: '10px 0' }}>
      {/* 顶部栏：显示语言 + 复制按钮 */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '5px 10px',
        background: '#2d2d2d',
        borderTopLeftRadius: '6px',
        borderTopRightRadius: '6px',
        color: '#ccc',
        fontSize: '12px'
      }}>
        <span style={{ fontWeight: 'bold' }}>{language.toUpperCase()}</span>
        <button 
          onClick={handleCopy}
          style={{
            background: 'transparent',
            border: 'none',
            color: isCopied ? '#4caf50' : '#fff', // 复制成功变绿
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          {isCopied ? '✔ Copied!' : '📋 Copy'}
        </button>
      </div>

      {/* 核心高亮区域 */}
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={language}
        PreTag="div"
        {...props}
        customStyle={{
          margin: 0,
          borderTopLeftRadius: 0,
          borderTopRightRadius: 0,
          borderBottomLeftRadius: '6px',
          borderBottomRightRadius: '6px',
        }}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    </div>
  );
};

export default CodeBlock;