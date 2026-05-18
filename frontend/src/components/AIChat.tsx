import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, X, Send, Bot, User, Sparkles } from 'lucide-react';
import axios from 'axios';
import { API_BASE } from '../config';

interface Message {
  sender: 'user' | 'bot';
  text: string;
}

export default function AIChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { sender: 'bot', text: '👋 Hi! I am PitchIQ AI Assistant. Ask me anything about Shark Tank India pitches, sharks, EBITDA definitions, or specific valuations!' }
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestedQuestions = [
    "Was Skippi Ice Pops valuation fair?",
    "Which shark invests most in D2C?",
    "Explain EBITDA with an example",
    "Compare Aman Gupta vs Namita Thapar investment patterns"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim()) return;
    
    const userMsg = textToSend;
    setInput('');
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/chat/`, {
        message: userMsg
      });
      setMessages(prev => [...prev, { sender: 'bot', text: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { sender: 'bot', text: '⚠️ Connection issue with PitchIQ backend. Please ensure the server is active.' }]);
    } finally {
      setLoading(false);
    }
  };

  const renderMarkdown = (text: string) => {
    // Escape HTML to prevent injection
    let escaped = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Replace **bold** with <strong>bold</strong>
    let formatted = escaped.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Replace line-start bullets (* or -) with clean Unicode bullets
    formatted = formatted.replace(/^\*\s+(.*)/gm, '• $1');
    formatted = formatted.replace(/^-\s+(.*)/gm, '• $1');

    // Convert newlines to HTML line breaks
    formatted = formatted.replace(/\n/g, '<br />');

    return { __html: formatted };
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Trigger Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center space-x-2 bg-accent hover:bg-accent-hover text-white px-4 py-3 rounded-full shadow-lg hover:shadow-accent/20 hover-lift transition-all duration-300"
        >
          <MessageSquare className="w-5 h-5 animate-pulse" />
          <span className="font-semibold text-sm hidden sm:inline">Ask PitchIQ AI</span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="w-80 sm:w-96 h-[500px] glass rounded-2xl flex flex-col shadow-2xl border border-accent/30 overflow-hidden animate-fadeIn">
          {/* Header */}
          <div className="bg-accent px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-2 text-white">
              <Bot className="w-5 h-5 text-text-primary" />
              <div>
                <h4 className="font-bold text-sm">PitchIQ Analyst Assistant</h4>
                <span className="text-[10px] text-text-secondary">Online • Live Data Context</span>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="text-white hover:text-text-secondary">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex items-start space-x-2 max-w-[85%] ${msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                  <div 
                    className={`p-2.5 rounded-2xl text-xs leading-relaxed ${
                      msg.sender === 'user' 
                        ? 'bg-accent text-white rounded-tr-none'
                        : 'bg-white/5 text-text-primary rounded-tl-none border border-white/5'
                    }`}
                    dangerouslySetInnerHTML={renderMarkdown(msg.text)}
                  />
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-white/5 border border-white/5 p-3 rounded-2xl rounded-tl-none flex items-center space-x-1">
                  <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Suggested Prompts */}
          {messages.length === 1 && (
            <div className="px-4 py-2 border-t border-white/5 bg-white/[0.02] space-y-1.5">
              <span className="text-[10px] uppercase tracking-wider text-text-secondary font-bold flex items-center space-x-1">
                <Sparkles className="w-3 h-3 text-accent" />
                <span>Suggested Questions</span>
              </span>
              <div className="flex flex-col space-y-1">
                {suggestedQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(q)}
                    className="text-left text-[11px] text-accent hover:text-accent-hover bg-white/5 hover:bg-white/10 p-1.5 rounded-lg border border-white/5 transition-all truncate"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Box */}
          <div className="p-3 border-t border-white/5 bg-black/40 flex items-center space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
              placeholder="Ask about Skipip Ice Pops, EBITDA, Aman Gupta..."
              className="flex-1 bg-white/5 border border-white/5 rounded-xl px-3 py-2 text-xs text-text-primary focus:outline-none focus:border-accent/50"
            />
            <button
              onClick={() => handleSend(input)}
              className="p-2 bg-accent hover:bg-accent-hover text-white rounded-xl transition-all"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
