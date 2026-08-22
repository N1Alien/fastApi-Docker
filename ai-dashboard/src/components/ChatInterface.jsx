// Plik: src/components/ChatInterface.jsx
import React, { useState, useEffect, useRef } from 'react';
import { API_BASE_URL } from '../config';
import { Terminal, Send, Wifi } from 'lucide-react';

export default function ChatInterface() {
  const [sessionId, setSessionId] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const initSession = async () => {
      const token = localStorage.getItem('token');
      try {
        const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        if (response.ok) {
          setSessionId(data.session_id);
          setMessages([{
            role: 'assistant',
            content: `CYBERNETIC CORE ENGAGED. SECURE TUNNEL_ID: [0x00${data.session_id}] ACTIVE.\n\nMainframe is fully operational. System is monitoring database shards and global data feeds. Initialize connection protocols by firing prompts.`
          }]);
        }
      } catch (err) {
        console.error("Mainframe bridge fractured:", err);
      }
    };
    initSession();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!prompt.trim() || !sessionId || isStreaming) return;

    const userPrompt = prompt;
    setPrompt('');
    setIsStreaming(true);

    setMessages(prev => [...prev, { role: 'user', content: userPrompt }]);
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`${API_BASE_URL}/chat-with-model`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ session_id: sessionId, prompt: userPrompt })
      });

      if (!response.ok) throw new Error("Packet link rejected by cognitive layer.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const textChunk = decoder.decode(value, { stream: true });

        setMessages(prev => {
          const updated = [...prev];
          const lastMsg = updated[updated.length - 1];
          lastMsg.content += textChunk;
          return updated;
        });
      }
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1].content = `[CRITICAL TERMINAL CONFLICT: ${err.message}]`;
        return updated;
      });
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div style={{ flex: 1, backgroundColor: '#0a0a0c', display: 'flex', flexDirection: 'column', height: '100%', fontFamily: 'monospace' }}>
      
      {/* BAR STATUS */}
      <div style={{ height: '40px', backgroundColor: '#0e0e13', borderBottom: '1px solid #1e293b', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'between', fontSize: '11px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#00f0ff', fontWeight: 'bold', tracking: '2px' }}>
          <Terminal style={{ width: '16px', height: '16px' }} />
          <span>CONSTRUCT_INTERFACE // OPERATIONAL_NODE</span>
        </div>
        {sessionId && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#ffee00', fontWeight: '900', marginLeft: 'auto' }}>
            <Wifi style={{ width: '12px', height: '12px' }} />
            <span>SESSION_TUNNEL: 0x00{sessionId}</span>
          </div>
        )}
      </div>

      {/* MESSAGES SCREEN */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg, i) => {
          const isUser = msg.role === 'user';
          const isSecurityAlert = msg.content.includes('[SECURITY ALERT:');
          
          return (
            <div key={i} style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
              <div style={{
                maxWidth: '680px',
                padding: '16px',
                border: isUser ? '1px solid #ffee00' : '1px solid #00f0ff',
                backgroundColor: isUser ? '#1a1300' : '#0f141c',
                color: isUser ? '#ffee00' : isSecurityAlert ? '#ff0055' : '#00f0ff',
                boxShadow: isUser ? '0 0 10px rgba(255,238,0,0.05)' : '0 0 10px rgba(0,240,255,0.05)',
                boxSizing: 'border-box'
              }}>
                <div style={{ fontSize: '9px', fontWeight: '900', letterSpacing: '1px', textTransform: 'uppercase', marginBottom: '6px', opacity: 0.6 }}>
                  {isUser ? '📂 USER_NETRUNNER' : isSecurityAlert ? '⚠️ COGNITIVE_GUARDRAIL' : '🧠 AI_CONSTRUCT'}
                </div>
                <p style={{ fontSize: '13px', lineHeight: '1.6', margin: 0, whiteSpace: 'pre-wrap', fontWeight: '500' }}>
                  {msg.content || (isStreaming && i === messages.length - 1 ? '█' : '')}
                </p>
              </div>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* MASSIVE INPUT CONSOLE FORM */}
      <form onSubmit={handleSend} style={{ padding: '20px', backgroundColor: '#0e0e13', borderTop: '1px solid #1e293b', display: 'flex', gap: '12px', alignItems: 'center' }}>
        <div style={{ flex: 1, position: 'relative', display: 'flex', alignItems: 'center' }}>
          {/* HUGE WHITE-TEXT INPUT FIELDS */}
          <input 
            type="text" 
            value={prompt} 
            onChange={(e) => setPrompt(e.target.value)} 
            disabled={isStreaming || !sessionId} 
            placeholder={isStreaming ? "AI CONSTRUCT PROCESSING DATA PACKETS..." : "ENTER COMMAND OR PROMPT FOR CHMURA AGENT..."} 
            style={{
              width: '100%',
              height: '72px',
              backgroundColor: '#14141c',
              border: '2px solid #1e293b',
              color: '#ffffff',
              fontSize: '18px',
              fontWeight: 'bold',
              fontFamily: 'monospace',
              paddingLeft: '20px',
              paddingRight: '20px',
              outline: 'none',
              borderRadius: '0px',
              boxSizing: 'border-box',
              appearance: 'none',
              WebkitAppearance: 'none'
            }}
            onFocus={(e) => e.target.style.borderColor = '#00f0ff'}
            onBlur={(e) => e.target.style.borderColor = '#1e293b'}
          />
        </div>
        
        <button 
          type="submit" 
          disabled={isStreaming || !prompt.trim() || !sessionId} 
          style={{
            height: '72px',
            backgroundColor: '#ff0055',
            color: '#ffffff',
            fontWeight: '900',
            fontSize: '13px',
            fontFamily: 'monospace',
            textTransform: 'uppercase',
            letterSpacing: '2px',
            padding: '0 32px',
            border: '2px solid #ff0055',
            boxShadow: '0 0 15px rgba(255,0,85,0.3)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 150ms'
          }}
          onMouseOver={(e) => { if(!isStreaming && sessionId) e.target.style.backgroundColor = '#cc0044' }}
          onMouseOut={(e) => { if(!isStreaming && sessionId) e.target.style.backgroundColor = '#ff0055' }}
        >
          <span>SEND</span>
        </button>
      </form>
    </div>
  );
}
