import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [cpuUsage, setCpuUsage] = useState(12);
  const [memoryUsage, setMemoryUsage] = useState(45);

  // Fake dynamic updates
  useEffect(() => {
    const interval = setInterval(() => {
      setCpuUsage(prev => Math.min(100, Math.max(0, prev + (Math.random() * 10 - 5))));
      setMemoryUsage(prev => Math.min(100, Math.max(0, prev + (Math.random() * 4 - 2))));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-purple-500/30 overflow-hidden relative">
      <div className="bg-gradient-glow"></div>
      <div className="bg-gradient-glow" style={{ top: 'auto', bottom: '-200px', left: 'auto', right: '-200px', background: 'radial-gradient(circle, rgba(56, 189, 248, 0.1) 0%, rgba(15, 23, 42, 0) 70%)' }}></div>
      
      {/* Navbar */}
      <nav className="glass-panel border-b border-slate-800/50 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-blue-500 flex items-center justify-center shadow-lg shadow-purple-500/20 animate-float">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
          <div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-blue-400">Unified Agent</h1>
            <p className="text-xs text-slate-400 font-medium tracking-wider uppercase">Control Plane</p>
          </div>
        </div>
        <div className="flex gap-4">
          <button className="px-4 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700/50 transition-all text-sm font-medium text-slate-300">Settings</button>
          <button className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white shadow-[0_0_15px_rgba(147,51,234,0.4)] transition-all text-sm font-medium">Initialize Core</button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-10">
        
        {/* Left Column */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          
          {/* Status Hero */}
          <div className="glass-panel rounded-2xl p-8 relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-semibold text-white">System Status</h2>
              <div className="flex items-center gap-2">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                <span className="text-green-400 font-medium text-sm">Online</span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 hover:border-purple-500/30 transition-colors">
                <p className="text-slate-400 text-sm mb-1">CPU Load</p>
                <div className="flex items-end gap-2">
                  <p className="text-3xl font-light text-white">{cpuUsage.toFixed(1)}%</p>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                  <div className="bg-purple-500 h-full rounded-full transition-all duration-500" style={{width: `${cpuUsage}%`}}></div>
                </div>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 hover:border-blue-500/30 transition-colors">
                <p className="text-slate-400 text-sm mb-1">Memory</p>
                <div className="flex items-end gap-2">
                  <p className="text-3xl font-light text-white">{memoryUsage.toFixed(1)}%</p>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                  <div className="bg-blue-500 h-full rounded-full transition-all duration-500" style={{width: `${memoryUsage}%`}}></div>
                </div>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 hover:border-emerald-500/30 transition-colors">
                <p className="text-slate-400 text-sm mb-1">Active Tasks</p>
                <p className="text-3xl font-light text-white">3</p>
                <div className="flex gap-1 mt-3">
                  <div className="h-1.5 flex-1 bg-emerald-500 rounded-full animate-pulse-slow"></div>
                  <div className="h-1.5 flex-1 bg-emerald-500/20 rounded-full"></div>
                  <div className="h-1.5 flex-1 bg-emerald-500/20 rounded-full"></div>
                </div>
              </div>
            </div>
          </div>

          {/* Terminal / Logs */}
          <div className="glass-panel rounded-2xl p-1 flex flex-col h-[400px]">
            <div className="flex items-center px-4 py-3 border-b border-slate-800/50 gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-slate-400"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
              <h3 className="text-sm font-medium text-slate-300">Execution Stream</h3>
            </div>
            <div className="flex-1 bg-slate-950/80 rounded-b-xl p-4 font-mono text-sm overflow-y-auto text-slate-400">
              <div className="text-emerald-400">[SYSTEM] Agent Core initialized successfully.</div>
              <div className="text-slate-500 mt-1">Loading context from polymath_agent_memory.db...</div>
              <div className="text-slate-300 mt-1">[TASK 1] Analyzing workspace constraints...</div>
              <div className="text-slate-500 mt-1">Found 3 new directories. Updating index.</div>
              <div className="text-blue-400 mt-1">[INFO] Triggering Memory Refresh...</div>
              <div className="text-purple-400 flex items-center gap-2 mt-4">
                <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping"></span> Awaiting next instruction...
              </div>
            </div>
          </div>

        </div>

        {/* Right Column */}
        <div className="flex flex-col gap-6">
          {/* Quick Actions */}
          <div className="glass-panel rounded-2xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Control Modules</h3>
            <div className="flex flex-col gap-3">
              <button className="flex items-center gap-3 w-full text-left p-3 rounded-xl hover:bg-slate-800/50 border border-transparent hover:border-slate-700 transition-all group">
                <div className="w-10 h-10 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center group-hover:bg-purple-500 group-hover:text-white transition-colors">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                </div>
                <div>
                  <h4 className="text-slate-200 font-medium">Security Guardrails</h4>
                  <p className="text-xs text-slate-500">Manage Sandbox Rules</p>
                </div>
              </button>
              
              <button className="flex items-center gap-3 w-full text-left p-3 rounded-xl hover:bg-slate-800/50 border border-transparent hover:border-slate-700 transition-all group">
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center group-hover:bg-blue-500 group-hover:text-white transition-colors">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
                </div>
                <div>
                  <h4 className="text-slate-200 font-medium">Memory Index</h4>
                  <p className="text-xs text-slate-500">View project-dir.md state</p>
                </div>
              </button>

              <button className="flex items-center gap-3 w-full text-left p-3 rounded-xl hover:bg-slate-800/50 border border-transparent hover:border-slate-700 transition-all group">
                <div className="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
                </div>
                <div>
                  <h4 className="text-slate-200 font-medium">Event Triggers</h4>
                  <p className="text-xs text-slate-500">Configure Listeners</p>
                </div>
              </button>
            </div>
          </div>
          
          {/* Agent Identity */}
          <div className="glass-panel rounded-2xl p-6 relative overflow-hidden">
             <div className="absolute top-0 right-0 p-4 opacity-10">
               <svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
             </div>
             <h3 className="text-lg font-semibold text-white mb-2">Agent Identity</h3>
             <p className="text-sm text-slate-400 leading-relaxed relative z-10">
               <strong className="text-slate-200">Unified Agent v2.0</strong><br/>
               Model: Gemini 3.1 Pro (High)<br/>
               Mode: Autonomous Workspace<br/>
               Location: Termux Native
             </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
