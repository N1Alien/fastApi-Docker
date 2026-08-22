// Folder: src/components/ | Plik: Auth.jsx | CZĘŚĆ 1 Z 2
import React, { useState } from 'react';
import { API_BASE_URL } from '../config';
import { Lock, Mail, ShieldAlert, Cpu, Terminal, RefreshCw, HelpCircle, Github } from 'lucide-react';

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
    <div className="min-h-screen flex items-center justify-center bg-[#050507] p-6 font-mono relative selection:bg-[#ff0055] selection:text-white">
      {/* Cybernetic Grid Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#111118_1px,transparent_1px),linear-gradient(to_bottom,#111118_1px,transparent_1px)] bg-[size:3rem_3rem] opacity-70"></div>

      {/* Main Framework Container */}
      <div className="max-w-4xl w-full flex flex-col md:flex-row bg-[#0c0c12] border-2 border-[#ff0055] relative z-10 shadow-[0_0_40px_rgba(255,0,85,0.25)]">
        
        {/* Technical Corner Version Tag */}
        <div className="absolute top-0 right-0 bg-[#ffee00] text-black text-[11px] font-black px-3 py-1 tracking-widest uppercase z-30">
          SYS_LINK_v6.2
        </div>

        {/* LEFT COLUMN: CYBERPUNK USER MANUAL & SOURCE CODE */}
        <div className="w-full md:w-1/2 p-8 bg-[#0a0a0f] border-b-2 md:border-b-0 md:border-r-2 border-gray-900 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2 text-[#ffee00] font-black text-xs tracking-widest uppercase mb-4">
              <HelpCircle className="h-4 w-4" />
              <span>// FIRST_TIME_NETRUNNER_MANUAL</span>
            </div>
            
            <p className="text-gray-400 text-xs leading-relaxed mb-6 font-semibold">
              Welcome to the corporate RAG link interface. If this is your first breach attempt, execute the initialization script below carefully:
            </p>

            <ol className="text-xs text-gray-500 font-bold space-y-4 list-decimal pl-4">
              <li>
                <span className="text-[#00f0ff] uppercase tracking-wider block mb-0.5">Step_01 // Identity Initialization</span>
                Toggle the register protocol using the link below the mainframe console to generate a new secure account string.
              </li>
              <li>
                <span className="text-[#00f0ff] uppercase tracking-wider block mb-0.5">Step_02 // Terminal Authorization</span>
                Log in with your newly compiled profile credentials to unlock a personal, isolated cryptographical Bearer JWT token session.
              </li>
              <li>
                <span className="text-[#00f0ff] uppercase tracking-wider block mb-0.5">Step_03 // Document Data Injection</span>
                Upload proprietary PDF file shards into the secure postgresql storage vector stack.
              </li>
              <li>
                <span className="text-[#00f0ff] uppercase tracking-wider block mb-0.5">Step_04 // Multi-Tool Query</span>
                Execute cognitive prompts. The agent loop autonomously synchronizes private memories and real-time live internet nodes.
              </li>
            </ol>
          </div>

          {/* GitHub Source Code Portal Link */}
          <div className="mt-8 pt-4 border-t border-gray-900">
            <a 
              href="https://github.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-xs font-black text-[#00f0ff] hover:text-white uppercase tracking-widest transition duration-150 group"
            >
              <Github className="h-4 w-4 text-[#00f0ff] group-hover:scale-110 transition-transform" />
              <span>&gt;&gt; ACCESS REPO_MAINFRAME_SOURCE</span>
            </a>
          </div>
        </div>
// Folder: src/components/ | Plik: Auth.jsx | CZĘŚĆ 2 Z 2

        {/* RIGHT COLUMN: MAINFRAME AUTH CONSOLE */}
        <div className="w-full md:w-1/2 p-8 flex flex-col justify-center">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-3 mb-2">
              <Cpu className="h-7 w-7 text-[#00f0ff]" />
              <h2 className="text-2xl font-black text-white tracking-widest uppercase">
                NETRUNNER <span className="text-[#ffee00]">AUTH</span>
              </h2>
            </div>
            <p className="text-[10px] text-[#00f0ff] font-black uppercase tracking-widest">
              {isLogin ? 'ACCESS GATEWAY: LINK_MAINFRAME' : 'INITIALIZE PROFILE PROTOCOL'}
            </p>
          </div>

          {/* Cold Start Hypersleep Indicator */}
          {isWakingUp && (
            <div className="bg-[#201500] text-[#ffee00] p-4 border border-[#ffee00] text-xs mb-6 font-bold flex flex-col gap-2 shadow-[0_0_15px_rgba(255,238,0,0.15)] animate-pulse">
              <div className="flex items-center gap-2 text-xs font-black tracking-widest text-[#ffee00] uppercase">
                <RefreshCw className="h-3.5 w-3.5 animate-spin text-[#ffee00]" />
                <span>[WAKING UP OLLAMA & COGNITIVE CORES]</span>
              </div>
              <p className="leading-relaxed opacity-90 text-[11px]">{error}</p>
            </div>
          )}

          {/* Standard Error Display */}
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

          {/* Core Authorization Form Fields */}
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div>
              <label className="block text-[10px] font-black text-[#ffee00] tracking-widest uppercase mb-2">
                NETWORK EMAIL ADDRESS
              </label>
              <div className="relative" style={{ display: 'flex', alignItems: 'center' }}>
                <Mail className="absolute left-4 h-5 w-5 text-[#00f0ff]" style={{ zIndex: 20 }} />
                <input 
                  type="email" 
                  required 
                  value={email} 
                  onChange={(e) => setEmail(e.target.value)} 
                  placeholder="alias@nightcity.net"
                  style={{
                    width: '100%',
                    height: '56px',
                    backgroundColor: '#020204',
                    border: '2px solid #00f0ff',
                    color: '#ffffff',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    fontFamily: 'monospace',
                    paddingLeft: '48px',
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

            <div>
              <label className="block text-[10px] font-black text-[#ffee00] tracking-widest uppercase mb-2">
                SECURE ACCESS PASSWORD
              </label>
              <div className="relative" style={{ display: 'flex', alignItems: 'center' }}>
                <Lock className="absolute left-4 h-5 w-5 text-[#00f0ff]" style={{ zIndex: 20 }} />
                <input 
                  type="password" 
                  required 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  placeholder="••••••••"
                  style={{
                    width: '100%',
                    height: '56px',
                    backgroundColor: '#020204',
                    border: '2px solid #00f0ff',
                    color: '#ffffff',
                    fontSize: '16px',
                    fontWeight: 'bold',
                    fontFamily: 'monospace',
                    paddingLeft: '48px',
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
              className="w-full flex items-center justify-center gap-3 bg-[#ff0055] hover:bg-[#cc0044] text-white font-black uppercase text-xs tracking-widest cursor-pointer active:translate-y-0.5 transition-all"
              style={{
                height: '56px',
                border: '2px solid #ff0055',
                boxShadow: '0 0 20px rgba(255,0,85,0.3)',
              }}
            >
              <Terminal className="h-5 w-5" />
              {isLogin ? 'CONNECT TO MAINFRAME' : 'GENERATE CONSTRUCT'}
            </button>
          </form>

          {/* Toggle Protocol Link */}
          <div className="mt-6 text-center border-t border-gray-900 pt-4">
            <button 
              onClick={() => { setIsLogin(!isLogin); setError(''); setMessage(''); setIsWakingUp(false); }} 
              className="text-xs font-black text-[#00f0ff] hover:text-white uppercase tracking-widest transition cursor-pointer"
            >
              {isLogin ? '>> REQUEST INITIAL REGISTER' : '>> RETURN TO ACCESS GATEWAY'}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
