'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ModelSelector from '@/components/ModelSelector';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentModel, setCurrentModel] = useState<'claude' | 'glm' | 'mako'>('glm');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    // Check for model switching commands
    if (content.trim().toLowerCase() === '/claude') {
      setCurrentModel('claude');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '🔄 Switched to Claude 3.5 Sonnet'
      }]);
      return;
    }

    if (content.trim().toLowerCase() === '/glm') {
      setCurrentModel('glm');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '🔄 Switched to GLM-4.7 Flash'
      }]);
      return;
    }

    if (content.trim().toLowerCase() === '/mako') {
      setCurrentModel('mako');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '🔄 Switched to Mako Hybrid Mode\n\n💡 Intelligence Stack: GLM (80%) for planning + Claude (20%) for execution'
      }]);
      return;
    }

    // Add user message
    const userMessage: Message = { role: 'user', content };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({
            role: m.role,
            content: m.content
          })),
          model: currentModel,
        }),
      });

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.content
      }]);
    } catch (error: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}`
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex h-screen bg-[#0f0f0f] text-white">
      {/* Sidebar */}
      <div className="w-64 bg-[#1a1a1a] border-r border-[#2a2a2a] flex flex-col">
        <div className="p-4">
          <button
            onClick={handleNewChat}
            className="w-full bg-[#2a2a2a] hover:bg-[#3a3a3a] rounded-lg p-3 text-sm font-medium transition-colors"
          >
            + New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <ModelSelector currentModel={currentModel} onModelChange={setCurrentModel} />

          <div className="mt-6">
            <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Quick Commands</h3>
            <div className="space-y-2 text-sm text-gray-300">
              <div className="bg-[#2a2a2a] rounded p-2">
                <code>/claude</code> - Switch to Claude
              </div>
              <div className="bg-[#2a2a2a] rounded p-2">
                <code>/glm</code> - Switch to GLM
              </div>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-[#2a2a2a]">
          <div className="text-xs text-gray-400">
            <div className="font-semibold mb-1">AI Stack Desktop</div>
            <div>Dual LLM Interface</div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-14 border-b border-[#2a2a2a] flex items-center px-6">
          <h1 className="text-sm font-medium text-gray-300">
            {currentModel === 'claude' ? '🤖 Claude 3.5 Sonnet' :
             currentModel === 'glm' ? '⚡ GLM-4.7 Flash' :
             '🚀 Mako Hybrid (GLM + Claude)'}
          </h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <h2 className="text-2xl font-semibold mb-4">Welcome to AI Stack Desktop</h2>
                <p className="text-gray-400 mb-6">
                  Choose your intelligence mode:<br/>
                  <code className="bg-[#2a2a2a] px-2 py-1 rounded">/glm</code> for speed,
                  <code className="bg-[#2a2a2a] px-2 py-1 rounded ml-2">/claude</code> for power,
                  <code className="bg-[#2a2a2a] px-2 py-1 rounded ml-2">/mako</code> for hybrid intelligence
                </p>
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {isLoading && (
                <div className="flex items-center gap-2 text-gray-400">
                  <div className="animate-pulse">●</div>
                  <div className="animate-pulse delay-75">●</div>
                  <div className="animate-pulse delay-150">●</div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-[#2a2a2a] p-6">
          <ChatInput onSend={handleSendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
}
