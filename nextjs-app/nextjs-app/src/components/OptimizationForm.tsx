"use client";

interface OptimizationFormProps {
  prompt: string;
  setPrompt: (prompt: string) => void;
  contextDomain: string;
  setContextDomain: (domain: string) => void;
  isOptimizing: boolean;
  onOptimize: () => void;
}

export default function OptimizationForm({
  prompt,
  setPrompt,
  contextDomain,
  setContextDomain,
  isOptimizing,
  onOptimize,
}: OptimizationFormProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold mb-4">
        Optimize Your Prompt
      </h2>

      <div className="space-y-4">
        <div>
          <label
            htmlFor="prompt"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Original Prompt
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter your prompt to optimize..."
            className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            disabled={isOptimizing}
          />
        </div>

        <div>
          <label
            htmlFor="context"
            className="block text-sm font-medium text-gray-700 mb-2"
          >
            Context Domain (Optional)
          </label>
          <input
            id="context"
            type="text"
            value={contextDomain}
            onChange={(e) => setContextDomain(e.target.value)}
            placeholder="e.g., marketing, technical, creative writing..."
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isOptimizing}
          />
        </div>

        <button
          onClick={onOptimize}
          disabled={!prompt.trim() || isOptimizing}
          className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {isOptimizing ? "Optimizing..." : "Optimize Prompt"}
        </button>
      </div>
    </div>
  );
}