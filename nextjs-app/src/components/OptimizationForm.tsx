"use client";

import { useState } from "react";

interface OptimizationFormProps {
  onOptimize: (prompt: string, contextDomain: string, useAdvancedMode: boolean, iterations: number) => Promise<void>;
  isOptimizing: boolean;
  useAdvancedMode: boolean;
  setUseAdvancedMode: (value: boolean) => void;
}

export function OptimizationForm({ onOptimize, isOptimizing, useAdvancedMode, setUseAdvancedMode }: OptimizationFormProps) {
  const [prompt, setPrompt] = useState("");
  const [contextDomain, setContextDomain] = useState("");
  const [iterations, setIterations] = useState(2);

  const handleOptimize = async (advancedMode?: boolean) => {
    if (!prompt.trim()) return;

    const isAdvanced = advancedMode ?? useAdvancedMode;
    
    try {
      await onOptimize(prompt, contextDomain, isAdvanced, iterations);
      
      // Clear form on successful start
      setPrompt("");
      setContextDomain("");
    } catch (error) {
      console.error("Failed to start optimization:", error);
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Mode Information Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className={`p-4 rounded-lg border-2 transition-all ${
          !useAdvancedMode ? "border-blue-200 bg-blue-50" : "border-gray-200 bg-gray-50"
        }`}>
          <h4 className="font-semibold text-blue-900 mb-2">Quick Optimize</h4>
          <p className="text-sm text-gray-600">Single-pass optimization with basic system prompts</p>
          <div className="mt-2 text-xs text-gray-500">⏱️ 60-90 seconds • 🔧 Development demo</div>
        </div>
        <div className={`p-4 rounded-lg border-2 transition-all ${
          useAdvancedMode ? "border-purple-200 bg-purple-50" : "border-gray-200 bg-gray-50"
        }`}>
          <h4 className="font-semibold text-purple-900 mb-2">Advanced Mode</h4>
          <p className="text-sm text-gray-600">Multi-iteration refinement with multiple system prompts</p>
          <div className="mt-2 text-xs text-gray-500">⏱️ 90-120 seconds • 🔧 Development demo</div>
        </div>
      </div>
      
      {/* Advanced Mode Controls */}
      {useAdvancedMode && (
        <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
          <label className="block text-sm font-medium text-purple-900 mb-2">
            Optimization Iterations: {iterations}
          </label>
          <input
            type="range"
            min="1"
            max="5"
            value={iterations}
            onChange={(e) => setIterations(parseInt(e.target.value))}
            className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer slider"
            disabled={isOptimizing}
          />
          <div className="flex justify-between text-xs text-purple-600 mt-1">
            <span>1 (Fast)</span>
            <span>3 (Balanced)</span>
            <span>5 (Thorough)</span>
          </div>
        </div>
      )}

      {/* Main Input Form */}
      <div className="space-y-6">
        <div>
          <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
            Original Prompt *
          </label>
          <div className="relative">
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Enter the prompt you'd like to optimize using Microsoft PromptWizard techniques..."
              className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm leading-relaxed"
              disabled={isOptimizing}
            />
            <div className="absolute bottom-3 right-3 text-xs text-gray-400">
              {prompt.length} characters
            </div>
          </div>
        </div>

        <div>
          <label htmlFor="context" className="block text-sm font-medium text-gray-700 mb-2">
            Context Domain (Optional)
          </label>
          <input
            id="context"
            type="text"
            value={contextDomain}
            onChange={(e) => setContextDomain(e.target.value)}
            placeholder="e.g., marketing, technical documentation, creative writing, data analysis..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isOptimizing}
          />
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          <button
            onClick={() => handleOptimize()}
            disabled={!prompt.trim() || isOptimizing}
            className={`w-full py-4 px-6 font-semibold rounded-lg transition-all duration-200 ${
              useAdvancedMode
                ? "bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white shadow-lg"
                : "bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white shadow-lg"
            } disabled:bg-gray-400 disabled:cursor-not-allowed disabled:shadow-none`}
          >
            {isOptimizing ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {useAdvancedMode ? "Processing Advanced Optimization..." : "Optimizing..."}
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                {useAdvancedMode ? "Start Advanced Optimization" : "Quick Optimize"}
              </div>
            )}
          </button>
          
          <div className="bg-amber-50 border border-amber-200 rounded p-3 mt-2">
            <p className="text-xs text-amber-800 text-center px-4">
              ⚠️ {useAdvancedMode 
                ? `Processing will take 90-120 seconds. This is a development demo using basic system prompts.`
                : "Processing will take 60-90 seconds. This is a development demo using basic system prompts."
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}