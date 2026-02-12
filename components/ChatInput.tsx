'use client';

import { useState, KeyboardEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="max-w-3xl mx-auto w-full">
      <div className="bg-[#2a2a2a] rounded-2xl border border-[#3a3a3a] focus-within:border-[#4a4a4a] transition-colors">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Message MAiKO..."
          disabled={disabled}
          rows={1}
          className="w-full bg-transparent text-white placeholder-gray-500 px-4 py-3 resize-none focus:outline-none text-sm"
          style={{ minHeight: '48px', maxHeight: '200px' }}
        />
        <div className="flex items-center justify-between px-4 pb-3">
          <div className="text-xs text-gray-500">
            Press Enter to send, Shift+Enter for new line
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            className="bg-[#2563eb] hover:bg-[#1d4ed8] disabled:bg-[#1a1a1a] disabled:text-gray-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
