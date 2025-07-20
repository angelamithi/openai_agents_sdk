import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const App = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem('tara_chat_history');
    return saved ? JSON.parse(saved) : [];
  });
  const [isTyping, setIsTyping] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');
  const chatRef = useRef(null);

  const threadId = 'default';
  const userId = localStorage.getItem('user_id') || generateUserId();

  function generateUserId() {
    const newId = 'user_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('user_id', newId);
    return newId;
  }

  useEffect(() => {
    localStorage.setItem('tara_chat_history', JSON.stringify(messages));
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const scrollToBottom = () => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:5000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, thread_id: threadId }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        assistantMessage += chunk.replace(/^data:\s*/gm, '');

        setMessages(prev => {
          const existing = prev.filter(msg => msg.role !== 'streaming');
          return [...existing, { role: 'streaming', content: assistantMessage }];
        });
      }

      setMessages(prev => {
        const existing = prev.filter(msg => msg.role !== 'streaming');
        return [...existing, { role: 'assistant', content: assistantMessage }];
      });

    } catch (error) {
      console.error('Streaming error:', error);
    } finally {
      setIsTyping(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem('tara_chat_history');
  };

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="emoji-header">🌍</div>
        <h1>Tara</h1>
        <p>Your Travel Mate</p>

        <button onClick={clearChat} className="clear-button">🧹 Clear Chat</button>

        <div className="theme-toggle">
          <label>
            <input type="checkbox" checked={theme === 'dark'} onChange={toggleTheme} />
            {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
          </label>
        </div>
      </div>

      <div className="chat-container">
        <div className="chat-window" ref={chatRef}>
          {messages.map((msg, index) => (
            <div key={index} className={`chat-message ${msg.role}`}>
              {msg.content}
            </div>
          ))}
          {isTyping && (
            <div className="chat-message assistant typing">Tara is typing<span className="dots">...</span></div>
          )}
        </div>

        <div className="input-area">
          <input
            type="text"
            value={input}
            placeholder="Ask Tara anything about your trip..."
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default App;
