// Folder: ai-dashboard/src/components/ | Plik: Auth.jsx | CZĘŚĆ 1 Z 2
import React, { useState } from 'react';
import { API_BASE_URL } from '../config';
import { Lock, Mail, ShieldAlert, Cpu, Terminal, RefreshCw } from 'lucide-react';

export default function Auth({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isWakingUp, setIsWakingUp] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setIsWakingUp(false);

    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'ICEWALL ACCESS DENIED: Connection rejected by mainframe.');
      }

      if (isLogin) {
        localStorage.setItem('token', data.access_token);
        onAuthSuccess();
      } else {
        setMessage('NEW CYBER-IDENTITY REGISTERED. PROTOCOL INITIALIZED.');
        setIsLogin(true);
        setPassword('');
      }
    } catch (err) {
      if (err.message.includes('Failed to fetch') || err.message.includes('fetch')) {
        setIsWakingUp(true);
        setError('⚠️ COLD START PROTOCOL DETECTED. Free-tier cloud infrastructure is currently dormant. Waking up the core server and Ollama engine takes up to 2-3 minutes. Do not close this terminal session.');
      } else {
        setError(err.message);
      }
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#050507',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'monospace',
      padding: '20px',
      boxSizing: 'border-box',
      position: 'relative'
    }}>
      
      {/* GLÓWNY KONTENER KONSOLI */}
      <div style={{
        maxWidth: '600px',
        width: '100%',
        backgroundColor: '#0c0c12',
        border: '2px solid #ff0055',
        padding: '30px',
        boxSizing: 'border-box',
        boxShadow: '0 0 30px rgba(255,0,85,0.25)',
        position: 'relative'
      }}>
        
        {/* TECH BADGE */}
        <div style={{ position: 'absolute', top: 0, right: 0, backgroundColor: '#ffee00', color: '#000000', fontSize: '11px', fontWeight: '900', padding: '4px 10px', letterSpacing: '1px' }}>
          SYS_LINK_v6.2
        </div>

        {/* HEADER */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', marginBottom: '8px' }}>
            <Cpu style={{ color: '#00f0ff', width: '28px', height: '24px' }} />
            <h2 style={{ fontSize: '26px', fontWeight: '900', color: '#ffffff', letterSpacing: '2px', margin: 0 }}>
              NETRUNNER <span style={{ color: '#ffee00' }}>AUTH</span>
            </h2>
          </div>
          <p style={{ fontSize: '12px', color: '#00f0ff', fontWeight: '900', margin: 0, letterSpacing: '1px' }}>
            {isLogin ? '// ACCESS GATEWAY: CONNECT_MAINFRAME' : '// INITIALIZE NEW NETRUN_CONSTRUCT'}
          </p>
        </div>

        {/* COLD START PROTOCOL WARNING */}
        {isWakingUp && (
          <div style={{ backgroundColor: '#201500', border: '1px solid #ffee00', padding: '16px', fontSize: '12px', color: '#ffee00', fontWeight: 'bold', marginBottom: '24px', lineHeight: '1.5' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', fontWeight: '900', color: '#ffee00' }}>
              <RefreshCw style={{ width: '16px', height: '16px' }} />
              <span>[WAKING UP OLLAMA & COGNITIVE CORES]</span>
            </div>
            <span>{error}</span>
          </div>
        )}

        {/* STANDARD ERRORS */}
        {error && !isWakingUp && (
          <div style={{ backgroundColor: '#20000a', border: '1px solid #ff0055', padding: '16px', fontSize: '12px', color: '#ff3377', fontWeight: 'bold', marginBottom: '24px' }}>
            <ShieldAlert style={{ width: '16px', height: '16px', display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
            <span>{error}</span>
          </div>
        )}

        {message && (
          <div style={{ backgroundColor: '#002222', border: '1px solid #00f0ff', padding: '16px', fontSize: '12px', color: '#00f0ff', fontWeight: 'bold', marginBottom: '24px' }}>
            ⚡ {message}
          </div>
        )}
// Folder: ai-dashboard/src/components/ | Plik: Auth.jsx | CZĘŚĆ 2 Z 2

        {/* AUTHORIZATION FORM */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '900', color: '#ffee00', letterSpacing: '1px', marginBottom: '8px' }}>
              NETWORK EMAIL ADDRESS
            </label>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <Mail style={{ position: 'absolute', left: '16px', color: '#00f0ff', width: '20px', height: '20px' }} />
              <input 
                type="email" 
                required 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="alias@nightcity.net"
                style={{
                  width: '100%',
                  height: '60px',
                  backgroundColor: '#020204',
                  border: '2px solid #00f0ff',
                  color: '#ffffff',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  fontFamily: 'monospace',
                  paddingLeft: '52px',
                  paddingRight: '16px',
                  outline: 'none',
                  borderRadius: '0px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: '900', color: '#ffee00', letterSpacing: '1px', marginBottom: '8px' }}>
              SECURE ACCESS PASSWORD
            </label>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <Lock style={{ position: 'absolute', left: '16px', color: '#00f0ff', width: '20px', height: '20px' }} />
              <input 
                type="password" 
                required 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••••"
                style={{
                  width: '100%',
                  height: '60px',
                  backgroundColor: '#020204',
                  border: '2px solid #00f0ff',
                  color: '#ffffff',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  fontFamily: 'monospace',
                  paddingLeft: '52px',
                  paddingRight: '16px',
                  outline: 'none',
                  borderRadius: '0px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          <button 
            type="submit" 
            style={{
              width: '100%',
              height: '60px',
              backgroundColor: '#ff0055',
              color: '#ffffff',
              fontWeight: '900',
              fontSize: '14px',
              fontFamily: 'monospace',
              textTransform: 'uppercase',
              letterSpacing: '2px',
              border: '2px solid #ff0055',
              boxShadow: '0 0 20px rgba(255,0,85,0.3)',
              cursor: 'pointer'
            }}
          >
            <Terminal style={{ width: '16px', height: '16px', display: 'inline', marginRight: '8px', verticalAlign: 'middle' }} />
            {isLogin ? 'CONNECT TO MAINFRAME' : 'INITIALIZE PROFILE'}
          </button>
        </form>

        {/* TOGGLE SYSTEM PLAN LINK */}
        <div style={{ marginTop: '24px', textAlign: 'center', borderTop: '1px solid #1f293d', paddingTop: '16px' }}>
          <button 
            onClick={() => { setIsLogin(!isLogin); setError(''); setMessage(''); setIsWakingUp(false); }} 
            style={{ backgroundColor: 'transparent', border: 'none', fontSize: '11px', fontWeight: '900', color: '#00f0ff', letterSpacing: '1px', textTransform: 'uppercase', cursor: 'pointer' }}
          >
            {isLogin ? '>> REQUEST INITIAL REGISTER' : '>> RETURN TO ACCESS GATEWAY'}
          </button>
        </div>

        {/* BRIGHT & HIGHLY READABLE NETRUNNER MANUAL */}
        <div style={{ marginTop: '30px', backgroundColor: '#020204', border: '1px solid #1f293d', padding: '16px' }}>
          <div style={{ fontSize: '12px', fontStyle: 'normal', fontVariant: 'normal', fontWeight: '900', color: '#ffee00', letterSpacing: '1px', marginBottom: '10px' }}>
            // FIRST_TIME_NETRUNNER_MANUAL:
          </div>
          <div style={{ fontSize: '12px', color: '#ffffff', lineHeight: '1.6', fontWeight: 'bold' }}>
            <div style={{ marginBottom: '8px' }}><span style={{ color: '#00f0ff' }}>[01]</span> Toggle "REQUEST INITIAL REGISTER" to compile a new account profile string.</div>
            <div style={{ marginBottom: '8px' }}><span style={{ color: '#00f0ff' }}>[02]</span> Log in using credentials to unlock a personal, isolated Bearer JWT session.</div>
            <div style={{ marginBottom: '8px' }}><span style={{ color: '#00f0ff' }}>[03]</span> Upload dynamic corporate PDF shards directly into the secure pgvector matrix.</div>
            <div style={{ marginBottom: '12px' }}><span style={{ color: '#00f0ff' }}>[04]</span> Prompt the agent construct. Keywords "internet" or "today" deploy real-time feeds.</div>
            <div style={{ borderTop: '1px dashed #1f293d', paddingTop: '10px' }}>
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: '#ffee00', textDecoration: 'none', fontSize: '11px', fontWeight: '900', letterSpacing: '1px' }}
              >
                &gt;&gt; [ ACCESS REPO MAINFRAME SOURCE CODE ]
              </a>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
