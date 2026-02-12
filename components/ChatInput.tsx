'use client';

import { useState, KeyboardEvent, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  autoFocus?: boolean;
}

export default function ChatInput({ onSend, disabled, autoFocus }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (autoFocus && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [autoFocus]);

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
    <div className="w-full">
      <div className="bg-black border-3 border-white font-mono">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="> INPUT..."
          disabled={disabled}
          rows={1}
          className="w-full bg-black text-white placeholder-gray-500 px-4 py-3 resize-none focus:outline-none text-sm font-mono border-b-4 border-white"
          style={{ minHeight: '48px', maxHeight: '200px' }}
        />
        <div className="flex items-center justify-between px-4 py-3">
          <div className="text-xs text-gray-400 font-mono">
            [ENTER] SEND | [SHIFT+ENTER] LINE
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            className="bg-white text-black hover:bg-gray-200 disabled:bg-black disabled:text-gray-500 disabled:border-gray-500 px-6 py-2 text-sm font-black transition-none border-2 border-white"
          >
            SEND
          </button>
        </div>
      </div>
    </div>
  );
}
