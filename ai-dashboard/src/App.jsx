import React, { useState, useEffect } from 'react';
import Auth from './components/Auth';
import SidebarFiles from './components/SidebarFiles';
import ChatInterface from './components/ChatInterface';
import { LogOut, ShieldCheck, Terminal } from 'lucide-react';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) setIsAuthenticated(true);
    setLoading(false);
  }, []);

  const handleLogOut = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0c] flex items-center justify-center font-mono text-[#ffee00]">
        <div className="text-center animate-pulse">
          <Terminal className="h-8 w-8 mx-auto mb-2 text-[#00f0ff]" />
          <p className="text-xs font-black tracking-widest uppercase">BOOTING CYBER_INTERFACE v6.1...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return <Auth onAuthSuccess={() => setIsAuthenticated(true)} />;

  return (
    <div className="h-screen bg-[#0a0a0c] flex flex-col font-mono text-gray-200 overflow-hidden">
      <header className="h-14 bg-[#0e0e13] border-b-2 border-[#00f0ff] px-6 flex items-center justify-between shadow-[0_2px_15px_rgba(0,240,255,0.1)] z-20">
        <div className="flex items-center gap-3">
          <div className="h-2 w-2 bg-[#00f0ff] animate-ping rounded-full"></div>
          <h1 className="text-base font-black tracking-widest text-white uppercase">
            NIGHT_CITY // <span className="text-[#ffee00]">AGENTIC_RAG_CORE</span>
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 bg-[#002211] border border-[#00ff55] px-2.5 py-1 text-[10px] font-black text-[#00ff55] uppercase tracking-wider">
            <ShieldCheck className="h-3.5 w-3.5" />
            <span>ICEWALL: ACTIVE</span>
          </div>
          <button onClick={handleLogOut} className="flex items-center gap-1.5 border border-[#ff0055] text-[#ff0055] hover:bg-[#ff0055] hover:text-white px-3 py-1.5 text-xs font-black uppercase tracking-widest transition-all duration-150 shadow-[0_0_8px_rgba(255,0,85,0.15)] cursor-pointer">
            <LogOut className="h-3.5 w-3.5" />
            <span>DISCONNECT LINK</span>
          </button>
        </div>
      </header>
      <div className="flex-1 flex overflow-hidden relative">
        <SidebarFiles />
        <ChatInterface />
      </div>
    </div>
  );
}
