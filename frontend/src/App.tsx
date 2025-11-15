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
    // Outer Container (Full screen)
    <div className="flex h-screen bg-gray-mint-50 text-gray-mint-900 overflow-hidden">
      
      {/* --- Fixed Header (Simulating Mintlify's top bar) --- */}
      <div className="fixed top-0 w-full h-14 bg-white border-b border-gray-mint-200 z-30">
        <div className="flex items-center h-full px-4">
          <h2 className="font-bold text-lg text-primary-mint">PEP-talk</h2>
        </div>
      </div>
      
      {/* --- Main Layout Wrapper (Pads content away from the fixed header) --- */}
      <div className="flex-1 mt-14 p-4 lg:p-3">
        
        {/* --- Rounded Content Container (The large rounded box holding the layout) --- */}
        <div 
          className="flex h-[calc(100vh-5.5rem)] lg:h-[calc(100vh-4.5rem)] rounded-2xl border border-gray-mint-200/70 shadow-lg overflow-hidden"
        >
          {/* Column 1: Sidebar (Fixed width w-16.5, matching inspiration) */}
          <nav className="w-16.5 shrink-0 bg-white border-r border-gray-mint-200/70 p-2 overflow-y-auto">
            
            {/* Search Bar Placeholder matching the inspiration design */}
            <div className="flex items-center justify-center p-2">
              <button 
                type="button" 
                className="flex rounded-xl w-full items-center text-sm leading-6 h-9 pl-3.5 pr-3 text-gray-mint-700 bg-gray-mint-50 ring-1 ring-gray-mint-200 justify-between truncate gap-2"
              >
                <div className="flex items-center gap-2">
                  <span className="text-gray-mint-700">🔍</span>
                  <div className="truncate">Search...</div>
                </div>
                <span className="flex-none text-xs font-semibold">⌘K</span>
              </button>
            </div>

            <ul className="space-y-px p-2 pt-4">
              {/* Active Link Example (Mimics Mintlify's filled/rounded active link) */}
              <li className="relative">
                <Link 
                  to="/mpep/2141" 
                  className="group flex items-center pr-3 py-1.5 cursor-pointer gap-x-3 text-left rounded-xl w-full outline-offset-[-1px] bg-primary-mint/10 text-primary-mint [text-shadow:-0.2px_0_0_currentColor,0.2px_0_0_currentColor] font-medium"
                >
                  MPEP 2141
                </Link>
              </li>
              {/* Inactive Links (Mimics Mintlify's rounded hover/inactive state) */}
              <li className="relative">
                <Link to="/mpep/2142" className="group flex items-center pr-3 py-1.5 cursor-pointer gap-x-3 text-left rounded-xl w-full outline-offset-[-1px] hover:bg-gray-mint-100/50 text-gray-mint-700 hover:text-gray-mint-900">MPEP 2142</Link>
              </li>
              <li className="relative">
                <Link to="/mpep/2143" className="group flex items-center pr-3 py-1.5 cursor-pointer gap-x-3 text-left rounded-xl w-full outline-offset-[-1px] hover:bg-gray-mint-100/50 text-gray-mint-700 hover:text-gray-mint-900">MPEP 2143</Link>
              </li>
              <li className="relative">
                <Link to="/mpep/2144" className="group flex items-center pr-3 py-1.5 cursor-pointer gap-x-3 text-left rounded-xl w-full outline-offset-[-1px] hover:bg-gray-mint-100/50 text-gray-mint-700 hover:text-gray-mint-900">MPEP 2144</Link>
              </li>
              <li className="relative">
                <Link to="/mpep/2145" className="group flex items-center pr-3 py-1.5 cursor-pointer gap-x-3 text-left rounded-xl w-full outline-offset-[-1px] hover:bg-gray-mint-100/50 text-gray-mint-700 hover:text-gray-mint-900">MPEP 2145</Link>
              </li>
            </ul>
          </nav>

          {/* Column 2: Main Content (The core reading area) */}
          <main className="flex-1 flex flex-col overflow-hidden relative bg-background-light-mint">
            <Routes>
              <Route path="/mpep/:sectionId" element={<MpepPage onTriggerAI={handleAITrigger} />} />
              <Route path="/" element={<Navigate to="/mpep/2141" replace />} />
            </Routes>
          </main>

          {/* Column 3: Contextual Panel (AI Companion) */}
          <aside 
            className={`flex flex-col h-full border-l border-gray-mint-200/70 shadow-lg transition-all duration-300 ease-in-out ${
              isAiPanelOpen ? 'w-96' : 'w-0'
            } bg-background-light-mint`}
          >
            {/* Header/Close Button */}
            <div className="flex-shrink-0 p-4 border-b border-gray-mint-200/70 flex justify-between items-center">
                <h3 className="font-semibold text-lg text-primary-mint">AI Study Companion</h3>
                <button 
                  onClick={() => setIsAiPanelOpen(false)} 
                  className="text-gray-mint-400 hover:text-gray-mint-800"
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
      </div>
      
    </div>
  );
}

export default App;