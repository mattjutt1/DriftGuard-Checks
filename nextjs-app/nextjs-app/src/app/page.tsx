"use client";

import { useState } from "react";
import { useMutation, useQuery, useAction } from "convex/react";
import { api } from "../../convex/_generated/api";
import OptimizationForm from "../components/OptimizationForm";
import ProgressDisplay from "../components/ProgressDisplay";
import QualityMetrics from "../components/QualityMetrics";
import ErrorHandling from "../components/ErrorHandling";

interface HealthResult {
  healthy: boolean;
  service?: { running: boolean; responseTime: number; url?: string };
  model?: { available: boolean; name: string; size?: string | null; quantization?: string | null };
  capabilities?: { generation: boolean; streaming: boolean };
  recommendations?: string[];
  error?: string | null;
  message?: string;
}

interface TestResult {
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
}

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [contextDomain, setContextDomain] = useState("");
  const [isOptimizing, setIsOptimizing] = useState(false);

  const createOptimization = useMutation(
    api.optimizations.createOptimizationRequest,
  );
  const optimizeWithOllama = useAction(api.actions.optimizePromptWithOllama);
  const recentSessions = useQuery(api.sessions.getRecentSessions, { limit: 5 });
  const ollamaHealth = useAction(api.actions.checkOllamaHealth);
  const testPipeline = useAction(api.actions.testOptimizationPipeline);

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

  const [healthResult, setHealthResult] = useState<HealthResult | null>(null);
  const [testResult, setTestResult] = useState<TestResult | null>(null);

  const checkHealth = async () => {
    try {
      const health = await ollamaHealth({});
      setHealthResult(health);
      console.log("Health check result:", health);
    } catch (error) {
      console.error("Health check failed:", error);
      setHealthResult({ error: "Health check failed: " + error, healthy: false });
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
      setTestResult({ success: false, error: "Test failed: " + error });
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
          <OptimizationForm
            prompt={prompt}
            setPrompt={setPrompt}
            contextDomain={contextDomain}
            setContextDomain={setContextDomain}
            isOptimizing={isOptimizing}
            onOptimize={handleOptimize}
          />
          <ProgressDisplay recentSessions={recentSessions} />
        </div>

        <QualityMetrics healthResult={healthResult} />

        <ErrorHandling testResult={testResult} />

        <footer className="text-center mt-8 text-gray-500 text-sm">
          <p>
            Powered by Qwen3-4B, Microsoft PromptWizard, Next.js, and Convex
          </p>
        </footer>
      </div>
    </div>
  );
}
