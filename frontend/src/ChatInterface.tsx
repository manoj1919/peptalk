//
// REPLACE THIS FILE
// File: peptalk/frontend/src/ChatInterface.tsx
//
import React, { useState, useEffect, useRef } from 'react';

const API_URL = "/api/chat/stream";

interface Message {
  id: number;
  text: string;
  sender: 'user' | 'bot';
}

interface ChatInterfaceProps {
  initialPrompt: string;
  isPanelOpen: boolean;
}

// --- NEW ONBOARDING COMPONENT ---
function OnboardingMessage() {
  return (
    <div className="flex-1 flex flex-col justify-center items-center p-6 text-center">
      <div className="bg-blue-100 p-4 rounded-full">
        {/* Simple Highlight Icon */}
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      </div>
      <h3 className="mt-4 font-semibold text-lg text-slate-800">Welcome to PEP-talk!</h3>
      <p className="mt-1 text-sm text-slate-600">
        **Highlight any text** in the MPEP document to get an explanation or see a real-world example.
      </p>
    </div>
  );
}

export function ChatInterface({ initialPrompt, isPanelOpen }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (isPanelOpen) {
      inputRef.current?.focus();
    }
  }, [isPanelOpen]);

  useEffect(() => {
    if (initialPrompt) {
      if (initialPrompt.startsWith("PREFILL:")) {
        setInput(initialPrompt.replace("PREFILL:", "").trim());
        inputRef.current?.focus();
      } else {
        sendStreamRequest(initialPrompt);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialPrompt]);


  const sendStreamRequest = async (promptText: string) => {
    if (isLoading) return;

    setIsLoading(true);

    const userMessage: Message = {
      id: Date.now(),
      text: promptText,
      sender: 'user',
    };
    setMessages((prev) => [...prev, userMessage]);

    const botMessage: Message = {
      id: Date.now() + 1,
      text: "",
      sender: 'bot',
    };
    setMessages((prev) => [...prev, botMessage]);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: promptText }),
      });

      if (!response.body) throw new Error("Response has no body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === botMessage.id
              ? { ...msg, text: msg.text + chunk }
              : msg
          )
        );
      }
    } catch (error) {
      console.error("Fetch error:", error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === botMessage.id
            ? { ...msg, text: "Error: Could not connect to the bot." }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    sendStreamRequest(input);
    setInput("");
  };

  return (
    // Set the background for the chat panel
    <div className="flex flex-col h-full bg-slate-50">
      
      {/* --- CHAT HISTORY OR ONBOARDING --- */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <OnboardingMessage />
        ) : (
          <div className="p-6 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.sender === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`p-3 rounded-lg max-w-lg shadow-sm ${
                    msg.sender === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-slate-800' // Bot message is white
                  }`}
                  style={{ whiteSpace: 'pre-wrap' }}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Form (Polished) */}
      <form onSubmit={handleFormSubmit} className="p-4 border-t border-slate-200 bg-white">
        <div className="flex items-center space-x-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isLoading ? "Thinking..." : "Ask a follow-up..."}
            className="flex-1 p-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg disabled:bg-gray-400 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={isLoading}
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}