"use client";

import { useState } from "react";
import { useMutation, useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [contextDomain, setContextDomain] = useState("");
  const [isOptimizing, setIsOptimizing] = useState(false);

  const createOptimization = useMutation(api.optimizations.createOptimizationRequest);
  const optimizeWithOllama = useMutation(api.actions.optimizePromptWithOllama);
  const recentSessions = useQuery(api.sessions.getRecentSessions, { limit: 5 });
  const ollamaHealth = useMutation(api.actions.checkOllamaHealth);

  const handleOptimize = async () => {
    if (!prompt.trim()) return;

    setIsOptimizing(true);
    try {
      // Create optimization request
      const sessionId = await createOptimization({
        originalPrompt: prompt,
        contextDomain: contextDomain || undefined,
      });

      // Trigger Ollama optimization
      await optimizeWithOllama({ sessionId });
      
      // Clear form
      setPrompt("");
      setContextDomain("");
    } catch (error) {
      console.error("Optimization failed:", error);
      alert("Optimization failed. Please check if Ollama is running and the Qwen3:8b model is available.");
    } finally {
      setIsOptimizing(false);
    }
  };

  const checkHealth = async () => {
    try {
      const health = await ollamaHealth({});
      alert(JSON.stringify(health, null, 2));
    } catch (error) {
      alert("Health check failed: " + error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            PromptEvolver
          </h1>
          <p className="text-lg text-gray-600">
            AI-Powered Prompt Optimization with Qwen3-4B
          </p>
          <button
            onClick={checkHealth}
            className="mt-4 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            Check Ollama Health
          </button>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Optimization Form */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Optimize Your Prompt</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
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
                <label htmlFor="context" className="block text-sm font-medium text-gray-700 mb-2">
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
                onClick={handleOptimize}
                disabled={!prompt.trim() || isOptimizing}
                className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isOptimizing ? "Optimizing..." : "Optimize Prompt"}
              </button>
            </div>
          </div>

          {/* Recent Sessions */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">Recent Optimizations</h2>
            
            {recentSessions === undefined ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading sessions...</p>
              </div>
            ) : recentSessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No optimizations yet.</p>
                <p className="text-sm">Start by optimizing your first prompt!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {recentSessions.map((session) => (
                  <div key={session._id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.prompt?.optimizationStatus === "completed"
                          ? "bg-green-100 text-green-800"
                          : session.prompt?.optimizationStatus === "processing"
                          ? "bg-yellow-100 text-yellow-800"
                          : session.prompt?.optimizationStatus === "failed"
                          ? "bg-red-100 text-red-800"
                          : "bg-gray-100 text-gray-800"
                      }`}>
                        {session.prompt?.optimizationStatus || "pending"}
                      </span>
                      {session.qualityScore && (
                        <span className="text-sm font-medium text-blue-600">
                          Score: {session.qualityScore.toFixed(1)}
                        </span>
                      )}
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-2">
                      Original: {session.prompt?.originalPrompt.substring(0, 100)}
                      {(session.prompt?.originalPrompt.length || 0) > 100 && "..."}
                    </p>
                    
                    {session.prompt?.optimizedPrompt && (
                      <p className="text-sm text-gray-800">
                        Optimized: {session.prompt.optimizedPrompt.substring(0, 100)}
                        {session.prompt.optimizedPrompt.length > 100 && "..."}
                      </p>
                    )}
                    
                    <div className="mt-2 text-xs text-gray-500">
                      {new Date(session.createdAt).toLocaleDateString()} at{" "}
                      {new Date(session.createdAt).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <footer className="text-center mt-8 text-gray-500 text-sm">
          <p>Powered by Qwen3-8B, Microsoft PromptWizard, Next.js, and Convex</p>
        </footer>
      </div>
    </div>
  );
}