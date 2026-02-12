'use client';

import { useState } from 'react';

interface ChatMessageProps {
  message: {
    role: 'user' | 'assistant';
    content: string;
  };
}

interface CodeBlock {
  language: string;
  code: string;
}

function extractCodeBlocks(content: string): (string | CodeBlock)[] {
  const parts: (string | CodeBlock)[] = [];
  const regex = /```(\w*)\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(content)) !== null) {
    if (match.index > lastIndex) {
      parts.push(content.slice(lastIndex, match.index));
    }
    parts.push({
      language: match[1] || 'javascript',
      code: match[2].trim(),
    });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < content.length) {
    parts.push(content.slice(lastIndex));
  }

  return parts;
}

function CodeBlockView({ block }: { block: CodeBlock }) {
  const [output, setOutput] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runCode = async () => {
    setIsRunning(true);
    setOutput(null);
    setError(null);

    try {
      const res = await fetch('/api/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: block.code,
          language: block.language === 'py' ? 'python' : block.language,
        }),
      });
      const data = await res.json();

      if (data.success) {
        setOutput(data.output || '(no output)');
        if (data.error) setError(data.error);
      } else {
        setError(data.error || 'Execution failed');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to connect to execution server');
    } finally {
      setIsRunning(false);
    }
  };

  const copyCode = () => {
    navigator.clipboard.writeText(block.code);
  };

  const lang = block.language === 'py' ? 'python' : block.language;
  const canRun = ['javascript', 'js', 'python', 'py'].includes(block.language.toLowerCase());

  return (
    <div className="my-2 rounded-lg overflow-hidden border border-[#3a3a3a]">
      <div className="flex items-center justify-between bg-[#1a1a1a] px-3 py-1.5">
        <span className="text-xs text-gray-400 font-mono">{lang}</span>
        <div className="flex gap-2">
          <button
            onClick={copyCode}
            className="text-xs text-gray-400 hover:text-white transition-colors px-2 py-0.5 rounded"
          >
            Copy
          </button>
          {canRun && (
            <button
              onClick={runCode}
              disabled={isRunning}
              className="text-xs bg-green-600 hover:bg-green-500 disabled:bg-gray-600 text-white px-3 py-0.5 rounded transition-colors font-medium"
            >
              {isRunning ? 'Running...' : '▶ Run'}
            </button>
          )}
        </div>
      </div>
      <pre className="p-3 bg-[#111] text-sm font-mono text-gray-200 overflow-x-auto">
        <code>{block.code}</code>
      </pre>
      {output !== null && (
        <div className="border-t border-[#3a3a3a] bg-[#0a1a0a] p-3">
          <div className="text-xs text-green-400 font-medium mb-1">Output:</div>
          <pre className="text-sm font-mono text-green-300 whitespace-pre-wrap">{output}</pre>
        </div>
      )}
      {error && (
        <div className="border-t border-[#3a3a3a] bg-[#1a0a0a] p-3">
          <div className="text-xs text-red-400 font-medium mb-1">Error:</div>
          <pre className="text-sm font-mono text-red-300 whitespace-pre-wrap">{error}</pre>
        </div>
      )}
    </div>
  );
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const parts = extractCodeBlocks(message.content);

  return (
    <div className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
        message.role === 'user'
          ? 'bg-[#2563eb] text-white'
          : 'bg-[#2a2a2a] text-gray-100'
      }`}>
        {parts.map((part, i) =>
          typeof part === 'string' ? (
            <div key={i} className="whitespace-pre-wrap text-sm leading-relaxed">
              {part}
            </div>
          ) : (
            <CodeBlockView key={i} block={part} />
          )
        )}
      </div>
    </div>
  );
}
