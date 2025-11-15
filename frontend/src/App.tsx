//
// REPLACE THIS FILE
// File: peptalk/frontend/src/App.tsx
//
import React, { useState } from 'react';
import { Routes, Route, Link, Navigate } from 'react-router-dom';
import { MpepPage } from './pages/MpepPage'; 
import { ChatInterface } from './ChatInterface';

function App() {
  const [isAiPanelOpen, setIsAiPanelOpen] = useState(false);
  const [chatPrompt, setChatPrompt] = useState("");

  const handleAITrigger = (text: string, type: 'explain' | 'example' | 'ask') => {
    let prompt = "";
    if (type === 'explain') {
      prompt = `Explain the following concept: "${text}"`;
    } else if (type === 'example') {
      prompt = `Generate a simple example of: "${text}"`;
    } else {
      prompt = `PREFILL: Tell me more about "${text}"`;
    }
    
    setChatPrompt(prompt + `_SEP_${Date.now()}`);
    setIsAiPanelOpen(true);
  };

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 overflow-hidden">
      
      {/* Column 1: Sidebar (Polished, bg-white for clear definition) */}
      <nav className="w-64 shrink-0 bg-white border-r border-slate-200 p-4 overflow-y-auto">
        <h2 className="font-bold text-lg mb-4 text-blue-600">PEP-talk</h2>
        <ul className="space-y-2">
          {/* REAL LINKS using React Router Link */}
          <li className="font-semibold text-slate-700 hover:text-blue-600">
            <Link to="/mpep/2141">MPEP 2141</Link>
          </li>
          <li className="font-semibold text-slate-700 hover:text-blue-600">
            <Link to="/mpep/2142">MPEP 2142</Link>
          </li>
          <li className="font-semibold text-slate-700 hover:text-blue-600">
            <Link to="/mpep/2143">MPEP 2143</Link>
          </li>
          <li className="font-semibold text-slate-700 hover:text-blue-600">
            <Link to="/mpep/2144">MPEP 2144</Link>
          </li>
          <li className="font-semibold text-slate-700 hover:text-blue-600">
            <Link to="/mpep/2145">MPEP 2145</Link>
          </li>
        </ul>
      </nav>

      {/* Column 2: Main Content (The primary reading area) */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative bg-white shadow-lg">
        <Routes>
          <Route path="/mpep/:sectionId" element={<MpepPage onTriggerAI={handleAITrigger} />} />
          <Route path="/" element={<Navigate to="/mpep/2141" replace />} />
        </Routes>
      </main>

      {/* Column 3: Contextual Panel (AI Companion) */}
      <aside 
        className={`bg-white flex flex-col h-screen border-l border-slate-200 shadow-lg transition-all duration-300 ease-in-out ${
          isAiPanelOpen ? 'w-96' : 'w-0'
        }`}
      >
        <div className="flex-shrink-0 p-4 border-b border-slate-200 flex justify-between items-center">
            <h3 className="font-semibold text-lg text-blue-600">AI Study Companion</h3>
            <button 
              onClick={() => setIsAiPanelOpen(false)} 
              className="text-slate-400 hover:text-slate-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
        </div>
        {isAiPanelOpen && (
          <ChatInterface 
            initialPrompt={chatPrompt}
            isPanelOpen={isAiPanelOpen}
          />
        )}
      </aside>
      
    </div>
  );
}

export default App;