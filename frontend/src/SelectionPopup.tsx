//
// REPLACE THIS FILE
// File: peptalk/frontend/src/SelectionPopup.tsx
//
import React from 'react';

interface SelectionPopupProps {
  top: number;
  left: number;
  onExplain: () => void;
  onExample: () => void;
  onAsk: () => void;
}

export function SelectionPopup({ top, left, onExplain, onExample, onAsk }: SelectionPopupProps) {
  return (
    <div
      className="absolute z-10 bg-white border border-slate-200 rounded-lg shadow-xl flex animate-fade-in"
      style={{ 
        top: top, 
        left: left,
      }}
    >
      <button
        onClick={onExplain}
        className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-l-lg"
      >
        Explain
      </button>
      <button
        onClick={onExample}
        className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 border-l border-slate-200"
      >
        Example
      </button>
      <button
        onClick={onAsk}
        className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 border-l border-slate-200 rounded-r-lg"
      >
        Ask
      </button>
    </div>
  );
}