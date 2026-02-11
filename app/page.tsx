'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ModelSelector from '@/components/ModelSelector';
import { chatStorage, Chat, Message } from '@/lib/chatHistory';

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentModel, setCurrentModel] = useState<'claude' | 'glm' | 'mako'>('glm');
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<Chat[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Load chat history on mount
  useEffect(() => {
    const chats = chatStorage.getAllChats();
    setChatHistory(chats);
  }, []);

  // Auto-scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-save current chat when messages change
  useEffect(() => {
    if (messages.length === 0) return;

    const saveCurrentChat = () => {
      const chatId = currentChatId || chatStorage.createNewChat(currentModel).id;

      const chat: Chat = {
        id: chatId,
        title: chatStorage.generateTitle(messages),
        messages,
        model: currentModel,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };

      chatStorage.saveChat(chat);

      if (!currentChatId) {
        setCurrentChatId(chatId);
      }

      // Refresh history
      setChatHistory(chatStorage.getAllChats());
    };

    saveCurrentChat();
  }, [messages, currentModel, currentChatId]);

  const handleSendMessage = async (content: string) => {
    // Check for model switching commands
    if (content.trim().toLowerCase() === '/claude') {
      setCurrentModel('claude');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '🔄 Switched to Claude 3 Haiku'
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
    setCurrentChatId(null);
    setCurrentModel('glm');
  };

  const loadChat = (chat: Chat) => {
    setMessages(chat.messages);
    setCurrentModel(chat.model);
    setCurrentChatId(chat.id);
    setShowHistory(false);
  };

  const deleteChat = (chatId: string) => {
    chatStorage.deleteChat(chatId);
    setChatHistory(chatStorage.getAllChats());

    // If we deleted the current chat, start new one
    if (chatId === currentChatId) {
      handleNewChat();
    }
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

          {/* Chat History Section */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-semibold text-gray-400 uppercase">Chat History</h3>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                {showHistory ? 'Hide' : 'Show'}
              </button>
            </div>

            {showHistory && (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {chatHistory.length === 0 ? (
                  <div className="text-xs text-gray-500 text-center py-4">
                    No saved chats yet
                  </div>
                ) : (
                  chatHistory.map((chat) => (
                    <div
                      key={chat.id}
                      className={`bg-[#2a2a2a] rounded p-2 cursor-pointer hover:bg-[#3a3a3a] transition-colors ${
                        currentChatId === chat.id ? 'ring-1 ring-blue-500' : ''
                      }`}
                    >
                      <div
                        onClick={() => loadChat(chat)}
                        className="flex-1"
                      >
                        <div className="text-sm text-gray-200 truncate">{chat.title}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          {new Date(chat.updatedAt).toLocaleDateString()} • {chat.messages.length} msgs
                        </div>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteChat(chat.id);
                        }}
                        className="text-xs text-red-400 hover:text-red-300 ml-2"
                      >
                        Delete
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          <div className="mt-6">
            <h3 className="text-xs font-semibold text-gray-400 uppercase mb-2">Quick Commands</h3>
            <div className="space-y-2 text-sm text-gray-300">
              <div className="bg-[#2a2a2a] rounded p-2">
                <code>/claude</code> - Switch to Claude
              </div>
              <div className="bg-[#2a2a2a] rounded p-2">
                <code>/glm</code> - Switch to GLM
              </div>
              <div className="bg-[#2a2a2a] rounded p-2">
                <code>/mako</code> - Switch to Hybrid
              </div>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-[#2a2a2a]">
          <div className="text-xs text-gray-400">
            <div className="font-[family-name:var(--font-jetbrains-mono)] text-lg font-bold mb-1 text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400">
              MAIKO
            </div>
            <div>Hybrid Intelligence System</div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="h-14 border-b border-[#2a2a2a] flex items-center px-6">
          <h1 className="text-sm font-medium text-gray-300">
            {currentModel === 'claude' ? '🤖 Claude 3 Haiku' :
             currentModel === 'glm' ? '⚡ GLM-4.7 Flash' :
             '🚀 Mako Hybrid (GLM + Claude)'}
          </h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-8">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <h2 className="font-[family-name:var(--font-jetbrains-mono)] text-5xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-green-400 via-cyan-400 to-blue-500">
                  MAIKO
                </h2>
                <p className="text-gray-500 text-sm mb-8 font-mono">// Hybrid Intelligence System</p>
                <p className="text-gray-400 mb-6">
                  Choose your intelligence mode:<br/>
                  <code className="bg-[#2a2a2a] px-2 py-1 rounded font-mono">/glm</code> for speed,
                  <code className="bg-[#2a2a2a] px-2 py-1 rounded ml-2 font-mono">/claude</code> for power,
                  <code className="bg-[#2a2a2a] px-2 py-1 rounded ml-2 font-mono">/mako</code> for hybrid
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
