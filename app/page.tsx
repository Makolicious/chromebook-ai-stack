'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ModelSelector from '@/components/ModelSelector';
import { chatStorage, Chat, Message } from '@/lib/chatHistory';

function generateExportPlan(messages: Message[], model: string): string {
  const timestamp = new Date().toISOString();
  const conversationText = messages
    .map(msg => {
      const role = msg.role === 'user' ? 'You' : 'MAiKO';
      return `**${role}:** ${msg.content}`;
    })
    .join('\n\n');

  return `# MAiKO Export Plan
**Generated:** ${timestamp}
**Model:** ${model === 'claude' ? 'Claude 3 Haiku' : model === 'glm' ? 'GLM-4.7 Flash' : 'Fly Hybrid (GLM + Claude)'}

## Conversation Summary

${conversationText}

---

## Implementation Notes

This plan was generated using MAiKO in ${model === 'mako' ? 'fly mode (cost-optimized with GLM planning + Claude refinement)' : model === 'glm' ? 'GLM mode (fast, cost-effective)' : 'Claude mode (high-quality)'} and is ready to be used as context for Claude Desktop Code implementation.

**How to use:**
1. Copy this entire text
2. Paste it into Claude Desktop Code
3. I will execute the plan using the full context and architectural understanding

**Benefits of this workflow:**
- ✅ Cheap ideation phase (completed in MAiKO)
- ✅ Full implementation context available
- ✅ Less back-and-forth during building
- ✅ Token-efficient planning + execution separation`;
}

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentModel, setCurrentModel] = useState<'claude' | 'glm' | 'mako'>('glm');
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [chatHistory, setChatHistory] = useState<Chat[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check auth on mount
  useEffect(() => {
    const storedAuth = sessionStorage.getItem('maiko_authenticated');
    if (storedAuth === 'true') {
      setIsAuthenticated(true);
    }
  }, []);

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

    if (content.trim().toLowerCase() === '/fly') {
      setCurrentModel('mako');
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '🔄 Switched to FLY Hybrid Mode\n\n💡 Intelligence Stack: GLM (80%) for planning + Claude (20%) for execution'
      }]);
      return;
    }

    if (content.trim().toLowerCase() === '/export') {
      const exportedPlan = generateExportPlan(messages, currentModel);
      navigator.clipboard.writeText(exportedPlan).then(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: '📋 Plan exported to clipboard!\n\nYou can now paste this into Claude Desktop Code to build upon it.\n\n---\n\n' + exportedPlan
        }]);
      }).catch(() => {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: '❌ Failed to copy to clipboard. Here\'s your plan:\n\n---\n\n' + exportedPlan
        }]);
      });
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

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (loginUsername === 'mako' && loginPassword === '6996') {
      sessionStorage.setItem('maiko_authenticated', 'true');
      setIsAuthenticated(true);
      setLoginUsername('');
      setLoginPassword('');
    } else {
      alert('Invalid username or password');
      setLoginPassword('');
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('maiko_authenticated');
    setIsAuthenticated(false);
    setMessages([]);
    setCurrentChatId(null);
    handleNewChat();
  };

  // Login screen
  if (!isAuthenticated) {
    return (
      <div className="flex h-screen bg-black text-white font-mono items-center justify-center">
        <div className="border-3 border-white p-8 max-w-md w-full">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-black mb-2">MA<span className="text-red-600">i</span>KO</h1>
            <p className="text-xs mb-8">HYBRID INTELLIGENCE SYSTEM</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-xs font-bold uppercase block mb-2">USERNAME</label>
              <input
                type="text"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                className="w-full bg-black border-2 border-white text-white p-2 font-mono text-sm focus:outline-none"
                placeholder="Enter username"
              />
            </div>

            <div>
              <label className="text-xs font-bold uppercase block mb-2">PASSWORD</label>
              <input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                className="w-full bg-black border-2 border-white text-white p-2 font-mono text-sm focus:outline-none"
                placeholder="Enter password"
              />
            </div>

            <button
              type="submit"
              className="w-full bg-white text-black border-2 border-white p-3 font-bold text-sm hover:bg-gray-200 transition-none"
            >
              [ LOGIN ]
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-black text-white font-mono">
      {/* Sidebar */}
      <div className={`bg-black border-3 border-white flex flex-col transition-all ${sidebarOpen ? 'w-80' : 'w-16'}`}>
        {/* Logo + Collapse */}
        <div className="p-3 border-b-3 border-white flex items-center justify-between gap-2 h-20">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-xs font-bold border-2 border-white px-2 py-1 hover:bg-white hover:text-black transition-none flex-shrink-0"
          >
            {sidebarOpen ? '[<]' : '[>]'}
          </button>
          <div className={`border-3 border-white p-2 flex-grow flex items-center justify-center transition-transform ${!sidebarOpen ? '-rotate-90' : ''}`}>
            <div className={`font-black ${sidebarOpen ? 'text-base' : 'text-sm'}`}>MA<span className="text-red-600">i</span>KO</div>
          </div>
        </div>

        {/* Buttons */}
        {sidebarOpen && (
          <div className="p-4 space-y-2 border-b-4 border-white">
            <button
              onClick={handleNewChat}
              className="w-full bg-white text-black hover:bg-gray-200 p-3 text-sm font-bold transition-none border-2 border-white"
            >
              [ NEW CHAT ]
            </button>
            <button
              onClick={() => handleSendMessage('/export')}
              disabled={messages.length === 0}
              className="w-full bg-white text-black hover:bg-gray-200 disabled:bg-black disabled:text-gray-500 disabled:border-gray-500 p-3 text-sm font-bold transition-none border-2 border-white"
            >
              [ EXPORT ]
            </button>
          </div>
        )}

        {/* Content */}
        {sidebarOpen && (
        <div className="flex-1 overflow-y-auto p-4 border-b-4 border-white space-y-4">
          <div className="border-3 border-white p-3">
            <h2 className="text-xs font-bold uppercase mb-3 text-white">MODEL SELECTION</h2>
            <div className="space-y-2">
              {[
                { id: 'glm', label: 'GLM-4.7 FLASH', desc: 'SPEED' },
                { id: 'claude', label: 'CLAUDE 3 HAIKU', desc: 'QUALITY' },
                { id: 'mako', label: 'FLY HYBRID', desc: 'BALANCED' },
              ].map((model) => (
                <button
                  key={model.id}
                  onClick={() => setCurrentModel(model.id as any)}
                  className={`w-full p-2 border-2 text-xs font-bold text-left transition-none ${
                    currentModel === model.id
                      ? 'bg-white text-black border-white'
                      : 'bg-black text-white border-white hover:bg-gray-900'
                  }`}
                >
                  <div>{model.label}</div>
                  <div className="text-xs opacity-70">{model.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="border-3 border-white p-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xs font-bold uppercase">HISTORY</h3>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="text-xs font-bold border-2 border-white px-2 py-1 hover:bg-white hover:text-black transition-none"
              >
                {showHistory ? '[-]' : '[+]'}
              </button>
            </div>

            {showHistory && (
              <div className="space-y-2 max-h-40 overflow-y-auto">
                {chatHistory.length === 0 ? (
                  <div className="text-xs text-gray-400 text-center py-4 border-2 border-gray-600 p-2">
                    EMPTY
                  </div>
                ) : (
                  chatHistory.map((chat) => (
                    <div
                      key={chat.id}
                      className={`border-2 p-2 cursor-pointer text-xs transition-none ${
                        currentChatId === chat.id
                          ? 'bg-white text-black border-white'
                          : 'bg-black text-white border-white hover:bg-gray-900'
                      }`}
                    >
                      <div
                        onClick={() => loadChat(chat)}
                        className="truncate font-bold"
                      >
                        {chat.title}
                      </div>
                      <div className="text-xs opacity-70 mt-1">
                        {new Date(chat.updatedAt).toLocaleDateString()} • {chat.messages.length}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteChat(chat.id);
                        }}
                        className="text-xs font-bold mt-1 border-2 border-white px-2 py-1 hover:bg-white hover:text-black transition-none"
                      >
                        DEL
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          <div className="border-3 border-white p-3">
            <h3 className="text-xs font-bold uppercase mb-2">COMMANDS</h3>
            <div className="space-y-1 text-xs font-bold uppercase">
              <div className="border-2 border-white p-2">/CLAUDE - SWITCH</div>
              <div className="border-2 border-white p-2">/GLM - SWITCH</div>
              <div className="border-2 border-white p-2">/FLY - SWITCH</div>
              <div className="border-2 border-white p-2">/EXPORT - EXPORT</div>
            </div>
          </div>
        </div>
        )}

        {/* Bottom area - Logout button */}
        <div className="border-t-3 border-white p-4 mt-auto">
          <button
            onClick={handleLogout}
            className="w-full text-red-500 hover:text-red-400 text-xs font-bold uppercase border-2 border-red-500 p-2 transition-none"
          >
            [ LOGOUT ]
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col border-l-4 border-white">
        {/* Header */}
        <div className="h-20 border-b-4 border-white flex items-center px-6 bg-black ml-20">
          <h1 className="text-sm font-black uppercase">
            {currentModel === 'claude' ? 'CLAUDE 3 HAIKU' :
             currentModel === 'glm' ? 'GLM-4.7 FLASH' :
             'FLY HYBRID'}
          </h1>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-8 py-8 bg-black">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-2xl border-3 border-white p-8">
                <h2 className="text-6xl font-black mb-6">MA<span className="text-red-600">i</span>KO</h2>
                <p className="text-sm mb-8">HYBRID INTELLIGENCE SYSTEM</p>
                <p className="text-xs mb-4 font-bold uppercase">
                  SELECT MODE:
                </p>
                <p className="text-xs mb-8 font-bold uppercase">
                  <code className="border-2 border-white px-2 py-1">/GLM</code> SPEED
                  <code className="border-2 border-white px-2 py-1 ml-2">/CLAUDE</code> QUALITY
                  <code className="border-2 border-white px-2 py-1 ml-2">/FLY</code> BALANCED
                </p>
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-8">
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}
              {isLoading && (
                <div className="border-l-4 border-white pl-4 text-xs">
                  <div className="animate-pulse">█ PROCESSING...</div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t-4 border-white p-6 bg-black">
          <ChatInput onSend={handleSendMessage} disabled={isLoading} autoFocus={true} />
        </div>
      </div>
    </div>
  );
}
