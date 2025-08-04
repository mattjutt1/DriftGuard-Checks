"use client";

import { useState } from "react";
import { useMutation, useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [contextDomain, setContextDomain] = useState("");
  const [isOptimizing, setIsOptimizing] = useState(false);

  const createOptimization = useMutation(
    api.optimizations.createOptimizationRequest,
  );
  const optimizeWithOllama = useMutation(api.actions.optimizePromptWithOllama);
  const recentSessions = useQuery(api.sessions.getRecentSessions, { limit: 5 });
  const ollamaHealth = useMutation(api.actions.checkOllamaHealth);
  const testPipeline = useMutation(api.actions.testOptimizationPipeline);

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
      alert(
        "Optimization failed. Please check if Ollama is running and the Qwen3:8b model is available.",
      );
    } finally {
      setIsOptimizing(false);
    }
  };

  const [healthResult, setHealthResult] = useState<{
    healthy: boolean;
    service?: { running: boolean; responseTime: number };
    model?: { available: boolean; name: string; size?: string };
    recommendations?: string[];
    error?: string;
    message?: string;
  } | null>(null);
  const [testResult, setTestResult] = useState<{
    success: boolean;
    testResults?: {
      originalPrompt: string;
      optimizedPrompt: string;
      qualityScore: number;
      processingTime: number;
      expertIdentity: string;
      reasoning: string;
    };
    error?: string;
  } | null>(null);

  const checkHealth = async () => {
    try {
      const health = await ollamaHealth({});
      setHealthResult(health);
      console.log("Health check result:", health);
    } catch (error) {
      console.error("Health check failed:", error);
      setHealthResult({ error: "Health check failed: " + error });
    }
  };

  const runTest = async () => {
    try {
      setIsOptimizing(true);
      const result = await testPipeline({
        testPrompt:
          "Write a compelling product description for a new smartwatch",
        contextDomain: "marketing",
      });
      setTestResult(result);
      console.log("Test result:", result);
    } catch (error) {
      console.error("Test failed:", error);
      setTestResult({ error: "Test failed: " + error });
    } finally {
      setIsOptimizing(false);
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
            AI-Powered Prompt Optimization with Qwen3-4B & PromptWizard
          </p>
          <div className="mt-4 space-x-4">
            <button
              onClick={checkHealth}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Check Ollama Health
            </button>
            <button
              onClick={runTest}
              disabled={isOptimizing}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 transition-colors"
            >
              {isOptimizing ? "Testing..." : "Test Integration"}
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Optimization Form */}
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
            <h2 className="text-2xl font-semibold mb-4">
              Recent Optimizations
            </h2>

            {recentSessions === undefined ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading sessions...</p>
              </div>
            ) : recentSessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No optimizations yet.</p>
                <p className="text-sm">
                  Start by optimizing your first prompt!
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {recentSessions.map((session) => (
                  <div
                    key={session._id}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          session.prompt?.optimizationStatus === "completed"
                            ? "bg-green-100 text-green-800"
                            : session.prompt?.optimizationStatus ===
                                "processing"
                              ? "bg-yellow-100 text-yellow-800"
                              : session.prompt?.optimizationStatus === "failed"
                                ? "bg-red-100 text-red-800"
                                : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {session.prompt?.optimizationStatus || "pending"}
                      </span>
                      {session.qualityScore && (
                        <span className="text-sm font-medium text-blue-600">
                          Score: {session.qualityScore.toFixed(1)}
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-gray-600 mb-2">
                      Original:{" "}
                      {session.prompt?.originalPrompt.substring(0, 100)}
                      {(session.prompt?.originalPrompt.length || 0) > 100 &&
                        "..."}
                    </p>

                    {session.prompt?.optimizedPrompt && (
                      <p className="text-sm text-gray-800">
                        Optimized:{" "}
                        {session.prompt.optimizedPrompt.substring(0, 100)}
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

        {/* Health Check Results */}
        {healthResult && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <span className="mr-2">System Health Status</span>
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  healthResult.healthy
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {healthResult.healthy ? "Healthy" : "Issues Detected"}
              </span>
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  Service Status
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Running:</span>
                    <span
                      className={
                        healthResult.service?.running
                          ? "text-green-600"
                          : "text-red-600"
                      }
                    >
                      {healthResult.service?.running ? "✅ Yes" : "❌ No"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Response Time:</span>
                    <span
                      className={
                        healthResult.service?.responseTime > 2000
                          ? "text-yellow-600"
                          : "text-green-600"
                      }
                    >
                      {healthResult.service?.responseTime}ms
                    </span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  Model Status
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Available:</span>
                    <span
                      className={
                        healthResult.model?.available
                          ? "text-green-600"
                          : "text-red-600"
                      }
                    >
                      {healthResult.model?.available ? "✅ Yes" : "❌ No"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Model:</span>
                    <span className="text-gray-600">
                      {healthResult.model?.name}
                    </span>
                  </div>
                  {healthResult.model?.size && (
                    <div className="flex justify-between">
                      <span>Size:</span>
                      <span className="text-gray-600">
                        {healthResult.model.size}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {healthResult.recommendations &&
              healthResult.recommendations.length > 0 && (
                <div className="mt-4">
                  <h3 className="font-semibold text-gray-800 mb-2">
                    Recommendations
                  </h3>
                  <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
                    {healthResult.recommendations.map(
                      (rec: string, idx: number) => (
                        <li key={idx}>{rec}</li>
                      ),
                    )}
                  </ul>
                </div>
              )}

            {healthResult.error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-700 text-sm">{healthResult.error}</p>
              </div>
            )}
          </div>
        )}

        {/* Test Results */}
        {testResult && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center">
              <span className="mr-2">Integration Test Results</span>
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${
                  testResult.success
                    ? "bg-green-100 text-green-800"
                    : "bg-red-100 text-red-800"
                }`}
              >
                {testResult.success ? "Passed" : "Failed"}
              </span>
            </h2>

            {testResult.success ? (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">
                    Test Prompt
                  </h3>
                  <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    {testResult.testResults?.originalPrompt}
                  </p>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-800 mb-2">
                    Optimized Result
                  </h3>
                  <p className="text-sm text-gray-800 bg-blue-50 p-3 rounded">
                    {testResult.testResults?.optimizedPrompt}
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2">
                      Metrics
                    </h3>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span>Quality Score:</span>
                        <span className="font-medium">
                          {testResult.testResults?.qualityScore}/10
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Processing Time:</span>
                        <span className="font-medium">
                          {testResult.testResults?.processingTime}ms
                        </span>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2">
                      Expert Identity
                    </h3>
                    <p className="text-sm text-gray-600">
                      {testResult.testResults?.expertIdentity}
                    </p>
                  </div>
                </div>

                {testResult.testResults?.reasoning && (
                  <div>
                    <h3 className="font-semibold text-gray-800 mb-2">
                      PromptWizard Analysis
                    </h3>
                    <p className="text-sm text-gray-600">
                      {testResult.testResults.reasoning}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-700 text-sm">{testResult.error}</p>
              </div>
            )}
          </div>
        )}

        <footer className="text-center mt-8 text-gray-500 text-sm">
          <p>
            Powered by Qwen3-4B, Microsoft PromptWizard, Next.js, and Convex
          </p>
        </footer>
      </div>
    </div>
  );
}
