interface ModelSelectorProps {
  currentModel: 'claude' | 'glm' | 'mako';
  onModelChange: (model: 'claude' | 'glm' | 'mako') => void;
}

export default function ModelSelector({ currentModel, onModelChange }: ModelSelectorProps) {
  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-400 uppercase mb-3">Model Selection</h3>
      <div className="space-y-2">
        <button
          onClick={() => onModelChange('glm')}
          className={`w-full text-left p-3 rounded-lg transition-colors ${
            currentModel === 'glm'
              ? 'bg-[#2563eb] text-white'
              : 'bg-[#2a2a2a] text-gray-300 hover:bg-[#3a3a3a]'
          }`}
        >
          <div className="font-medium text-sm">⚡ GLM-4.7 Flash</div>
          <div className="text-xs opacity-75 mt-1">Free & Fast</div>
        </button>

        <button
          onClick={() => onModelChange('claude')}
          className={`w-full text-left p-3 rounded-lg transition-colors ${
            currentModel === 'claude'
              ? 'bg-[#2563eb] text-white'
              : 'bg-[#2a2a2a] text-gray-300 hover:bg-[#3a3a3a]'
          }`}
        >
          <div className="font-medium text-sm">🤖 Claude 3 Haiku</div>
          <div className="text-xs opacity-75 mt-1">Smart & Balanced</div>
        </button>

        <button
          onClick={() => onModelChange('mako')}
          className={`w-full text-left p-3 rounded-lg transition-colors ${
            currentModel === 'mako'
              ? 'bg-gradient-to-r from-[#2563eb] to-[#7c3aed] text-white'
              : 'bg-[#2a2a2a] text-gray-300 hover:bg-[#3a3a3a]'
          }`}
        >
          <div className="font-medium text-sm">🚀 Mako Hybrid</div>
          <div className="text-xs opacity-75 mt-1">GLM Planning + Claude Execution</div>
        </button>
      </div>
    </div>
  );
}
