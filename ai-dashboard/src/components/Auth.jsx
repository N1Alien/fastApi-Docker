// Plik: src/components/Auth.jsx
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
        setError('⚠️ CLOUD MAINFRAME IS CURRENTLY DORMANT. Free-tier cloud infrastructure is waking up from hypersleep. This cold start protocol can take up to 2-3 minutes. Do not disconnect.');
      } else {
        setError(err.message);
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#050507] px-4 font-mono relative selection:bg-[#ff0055] selection:text-white">
      {/* Background cyber-grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#111118_1px,transparent_1px),linear-gradient(to_bottom,#111118_1px,transparent_1px)] bg-[size:3rem_3rem] opacity-70"></div>

      <div className="max-w-xl w-full bg-[#0c0c12] p-10 border-2 border-[#ff0055] relative z-10 shadow-[0_0_35px_rgba(255,0,85,0.25)]">
        {/* Decorative corner badge */}
        <div className="absolute top-0 right-0 bg-[#ffee00] text-black text-[11px] font-black px-3 py-1 tracking-widest uppercase">
          SYS_LINK_v6.2
        </div>

        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-3 mb-3">
            <Cpu className="h-7 w-7 text-[#00f0ff]" />
            <h2 className="text-3xl font-black text-white tracking-widest uppercase">
              NETRUNNER <span className="text-[#ffee00]">AUTH</span>
            </h2>
          </div>
          <p className="text-xs text-[#00f0ff] font-black uppercase tracking-widest">
            {isLogin ? '// ACCESS GATEWAY: LOG IN' : '// REGISTER NEW CONSTRUCT PROFILE'}
          </p>
        </div>

        {/* Dynamic Cloud Hypersleep Alert (Cyberpunk Style) */}
        {isWakingUp && (
          <div className="bg-[#201500] text-[#ffee00] p-4 border border-[#ffee00] text-xs mb-6 font-bold flex flex-col gap-3 shadow-[0_0_15px_rgba(255,238,0,0.15)] animate-pulse">
            <div className="flex items-center gap-2 text-sm font-black tracking-wider text-[#ffee00]">
              <RefreshCw className="h-4 w-4 animate-spin text-[#ffee00]" />
              <span>[SYSTEM CONFIGURATION PROTOCOL: WAKING UP OLLAMA CORE]</span>
            </div>
            <p className="leading-relaxed opacity-90">{error}</p>
          </div>
        )}

        {/* Standard Errors (Distinct Magenta) */}
        {error && !isWakingUp && (
          <div className="bg-[#20000a] text-[#ff3377] p-4 border border-[#ff0055] text-xs mb-6 font-bold flex items-center gap-2 shadow-[0_0_15px_rgba(255,0,85,0.15)]">
            <ShieldAlert className="h-5 w-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {message && (
          <div className="bg-[#002222] text-[#00f0ff] p-4 border border-[#00f0ff] text-xs mb-6 font-bold">
            ⚡ {message}
          </div>
        )}

        {/* Big spaces (gap: 40px) */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
          
          {/* INPUT 1: EMAIL */}
          <div>
            <label className="block text-xs font-black text-[#ffee00] tracking-widest uppercase mb-3">
              NETWORK EMAIL ADDRESS
            </label>
            <div className="relative" style={{ display: 'flex', alignItems: 'center' }}>
              <Mail className="absolute left-4 h-6 w-6 text-[#00f0ff]" style={{ zIndex: 20 }} />
              
              {/* Massive, fully readable custom CSS input */}
              <input 
                type="email" 
                required 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                placeholder="alias@nightcity.net"
                style={{
                  width: '100%',
                  height: '68px',
                  backgroundColor: '#020204',
                  border: '2px solid #00f0ff',
                  color: '#ffffff',
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'monospace',
                  paddingLeft: '56px',
                  paddingRight: '16px',
                  outline: 'none',
                  borderRadius: '0px',
                  boxSizing: 'border-box',
                  appearance: 'none',
                  WebkitAppearance: 'none'
                }}
              />
            </div>
          </div>

          {/* INPUT 2: PASSWORD */}
          <div>
            <label className="block text-xs font-black text-[#ffee00] tracking-widest uppercase mb-3">
              SECURE ACCESS PASSWORD
            </label>
            <div className="relative" style={{ display: 'flex', alignItems: 'center' }}>
              <Lock className="absolute left-4 h-6 w-6 text-[#00f0ff]" style={{ zIndex: 20 }} />
              
              {/* Massive, fully readable custom CSS input */}
              <input 
                type="password" 
                required 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                placeholder="••••••••"
                style={{
                  width: '100%',
                  height: '68px',
                  backgroundColor: '#020204',
                  border: '2px solid #00f0ff',
                  color: '#ffffff',
                  fontSize: '20px',
                  fontWeight: 'bold',
                  fontFamily: 'monospace',
                  paddingLeft: '56px',
                  paddingRight: '16px',
                  outline: 'none',
                  borderRadius: '0px',
                  boxSizing: 'border-box',
                  appearance: 'none',
                  WebkitAppearance: 'none'
                }}
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="w-full flex items-center justify-center gap-3 bg-[#ff0055] hover:bg-[#cc0044] text-white font-black uppercase tracking-widest cursor-pointer active:translate-y-0.5"
            style={{
              height: '64px',
              fontSize: '14px',
              border: '2px solid #ff0055',
              boxShadow: '0 0 25px rgba(255,0,85,0.4)',
              transition: 'all 150ms'
            }}
          >
            <Terminal className="h-5 w-5" />
            {isLogin ? 'CONNECT TO MAINFRAME' : 'GENERATE MATRIX PROFILE'}
          </button>
        </form>

        <div className="mt-10 text-center border-t border-gray-900 pt-5">
          <button 
            onClick={() => { setIsLogin(!isLogin); setError(''); setMessage(''); setIsWakingUp(false); }} 
            className="text-xs font-black text-[#00f0ff] hover:text-white uppercase tracking-widest transition cursor-pointer"
          >
            {isLogin ? '>> REQUEST NEW IDENTITY REGISTER' : '>> RETURN TO ACCESS GATEWAY'}
          </button>
        </div>
      </div>
    </div>
  );
}
