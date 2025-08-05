"use client";

import { useState } from "react";
import { useOptimization, useOptimizationHistory, OptimizationMetrics } from "../hooks/useOptimization";
// Note: FeedbackModal component may not exist
// import { FeedbackModal } from "../components/FeedbackModal";

// UI Component Types
interface ProgressBarProps {
  label: string;
  value: number;
  maxValue?: number;
  className?: string;
  showValue?: boolean;
}

interface QualityMetricsProps {
  metrics: OptimizationMetrics;
  overallScore?: number;
}

interface OptimizationResultsProps {
  isVisible: boolean;
  onClose: () => void;
}

// Progress Bar Component
function ProgressBar({ label, value, maxValue = 10, className = "", showValue = true }: ProgressBarProps) {
  const percentage = Math.min((value / maxValue) * 100, 100);
  
  const getColorClass = (percentage: number) => {
    if (percentage >= 80) return "bg-emerald-500";
    if (percentage >= 60) return "bg-blue-500";
    if (percentage >= 40) return "bg-yellow-500";
    return "bg-red-500";
  };

  return (
    <div className={`space-y-1 ${className}`}>
      <div className="flex justify-between items-center text-sm">
        <span className="font-medium text-gray-700">{label}</span>
        {showValue && (
          <span className="text-gray-600">{value.toFixed(1)}/{maxValue}</span>
        )}
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div 
          className={`h-2.5 rounded-full transition-all duration-500 ease-out ${getColorClass(percentage)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// Quality Metrics Dashboard Component
function QualityMetrics({ metrics, overallScore }: QualityMetricsProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Quality Metrics</h3>
        {overallScore && (
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-600">Overall Score:</span>
            <span className="text-xl font-bold text-blue-600">{overallScore.toFixed(1)}</span>
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ProgressBar label="Clarity" value={metrics.clarity} />
        <ProgressBar label="Specificity" value={metrics.specificity} />
        <ProgressBar label="Engagement" value={metrics.engagement} />
        {metrics.structure && (
          <ProgressBar label="Structure" value={metrics.structure} />
        )}
        {metrics.completeness && (
          <ProgressBar label="Completeness" value={metrics.completeness} />
        )}
        {metrics.error_prevention && (
          <ProgressBar label="Error Prevention" value={metrics.error_prevention} />
        )}
      </div>
    </div>
  );
}

// Advanced Progress Indicator Component
function OptimizationProgress({ isOptimizing, currentStep, totalSteps, message }: {
  isOptimizing: boolean;
  currentStep: number;
  totalSteps: number;
  message: string;
}) {
  if (!isOptimizing) return null;

  const progress = totalSteps > 0 ? (currentStep / totalSteps) * 100 : 0;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold mb-2">Optimizing Prompt</h3>
          <p className="text-gray-600 mb-4">{message}</p>
          
          {totalSteps > 0 && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Step {currentStep} of {totalSteps}</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Optimization Results Modal Component
function OptimizationResults({ isVisible, onClose }: OptimizationResultsProps) {
  const { results, currentSession, qualityMetrics } = useOptimization();
  const [showFeedback, setShowFeedback] = useState(false);
  
  if (!isVisible || !results) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
            <h2 className="text-xl font-semibold">Optimization Results</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
            >
              ×
            </button>
          </div>
          
          <div className="p-6 space-y-6">
          {/* Results Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {results.qualityMetrics.overall?.toFixed(1) || "N/A"}
              </div>
              <div className="text-sm text-gray-600">Quality Score</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {currentSession?.iterationsCompleted || 1}
              </div>
              <div className="text-sm text-gray-600">Iterations</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round((currentSession?.processingTimeMs || 0) / 1000)}s
              </div>
              <div className="text-sm text-gray-600">Processing Time</div>
            </div>
          </div>

          {/* Final Optimized Prompt */}
          {results.bestPrompt && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Optimized Prompt:</h3>
              <div className="bg-white rounded border p-3 text-sm">
                {results.bestPrompt}
              </div>
            </div>
          )}

          {/* Improvements List */}
          {results.improvements && results.improvements.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Key Improvements:</h3>
              <div className="bg-white rounded-lg border p-4">
                <div className="space-y-2">
                  {results.improvements.map((improvement, idx) => (
                    <div key={idx} className="text-sm flex items-start">
                      <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                      {improvement}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Expert Insights */}
          {results.expertInsights && results.expertInsights.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Expert Insights:</h3>
              <div className="bg-indigo-50 rounded-lg p-4">
                <div className="space-y-2">
                  {results.expertInsights.map((insight, idx) => (
                    <div key={idx} className="text-sm flex items-start">
                      <span className="inline-block w-2 h-2 bg-indigo-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                      {insight}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

            {/* Feedback Button */}
            <div className="mt-6 pt-6 border-t">
              <button
                onClick={() => setShowFeedback(true)}
                className="w-full px-4 py-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 transition-colors font-medium"
              >
                💬 Share Feedback on This Optimization
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Feedback Modal - Component not implemented */}
      {/* <FeedbackModal
        isVisible={showFeedback}
        onClose={() => setShowFeedback(false)}
        sessionId={currentSession?._id || null}
      /> */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Feedback Not Available</h3>
            <p className="text-gray-600 mb-4">Feedback component is not yet implemented in this development demo.</p>
            <button
              onClick={() => setShowFeedback(false)}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [contextDomain, setContextDomain] = useState("");
  const [useAdvancedMode, setUseAdvancedMode] = useState(false);
  const [iterations, setIterations] = useState(2);
  const [showResults, setShowResults] = useState(false);

  // Use our custom optimization hook
  const {
    isOptimizing,
    currentStep,
    totalSteps,
    progressMessage,
    currentIteration,
    results,
    qualityMetrics,
    error,
    startOptimization,
    resetOptimization,
    checkOllamaHealth,
  } = useOptimization();

  // Use history hook
  const { sessions: recentSessions, isLoading: historyLoading } = useOptimizationHistory(5);

  const handleOptimize = async (advancedMode?: boolean) => {
    if (!prompt.trim()) return;

    const isAdvanced = advancedMode ?? useAdvancedMode;
    
    try {
      await startOptimization(prompt, contextDomain, isAdvanced, iterations);
      setShowResults(true);
      
      // Clear form on successful start
      setPrompt("");
      setContextDomain("");
    } catch (error) {
      console.error("Failed to start optimization:", error);
    }
  };

  const checkHealth = async () => {
    try {
      const health = await checkOllamaHealth();
      alert(JSON.stringify(health, null, 2));
    } catch (error) {
      alert("Health check failed: " + error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Optimization Progress Modal */}
      <OptimizationProgress 
        isOptimizing={isOptimizing}
        currentStep={currentStep}
        totalSteps={totalSteps}
        message={progressMessage}
      />
      
      {/* Results Modal */}
      <OptimizationResults 
        isVisible={showResults}
        onClose={() => setShowResults(false)}
      />

      {/* Error Alert */}
      {error && (
        <div className="fixed top-4 right-4 z-50 max-w-md">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded shadow-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-sm">{error}</span>
              </div>
              <button
                onClick={resetOptimization}
                className="ml-2 text-red-500 hover:text-red-700"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Enhanced Header */}
        <header className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent mb-4">
            PromptEvolver
          </h1>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6 max-w-2xl mx-auto">
            <p className="text-lg font-semibold text-yellow-800 mb-2">⚠️ Development Demo - Not Production Ready</p>
            <p className="text-sm text-yellow-700">
              Processing takes 60-120 seconds • Local development only • System prompts (not actual PromptWizard)
            </p>
          </div>
          <p className="text-xl text-gray-600 mb-6 max-w-2xl mx-auto">
            Basic Prompt Optimization Demo using Ollama & Qwen3:4b
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={checkHealth}
              className="inline-flex items-center px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors shadow-md"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              System Health
            </button>
          </div>
        </header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Left Column - Optimization Form */}
          <div className="xl:col-span-2 space-y-6">
            {/* Optimization Mode Toggle */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-gray-900">Optimization Mode</h2>
                <div className="flex bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setUseAdvancedMode(false)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      !useAdvancedMode
                        ? "bg-blue-600 text-white shadow-md"
                        : "text-gray-600 hover:text-gray-900"
                    }`}
                  >
                    Quick Mode
                  </button>
                  <button
                    onClick={() => setUseAdvancedMode(true)}
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                      useAdvancedMode
                        ? "bg-purple-600 text-white shadow-md"
                        : "text-gray-600 hover:text-gray-900"
                    }`}
                  >
                    Advanced Mode
                  </button>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className={`p-4 rounded-lg border-2 transition-all ${
                  !useAdvancedMode ? "border-blue-200 bg-blue-50" : "border-gray-200 bg-gray-50"
                }`}>
                  <h3 className="font-semibold text-blue-900 mb-2">Quick Optimize</h3>
                  <p className="text-sm text-gray-600">Single-pass optimization with basic system prompts</p>
                  <div className="mt-2 text-xs text-red-600">⏱️ 60-90 seconds • 🏠 Local only • 🔧 Development demo</div>
                </div>
                <div className={`p-4 rounded-lg border-2 transition-all ${
                  useAdvancedMode ? "border-purple-200 bg-purple-50" : "border-gray-200 bg-gray-50"
                }`}>
                  <h3 className="font-semibold text-purple-900 mb-2">Advanced Mode</h3>
                  <p className="text-sm text-gray-600">Multi-iteration refinement with multiple system prompts</p>
                  <div className="mt-2 text-xs text-red-600">⏱️ 90-120 seconds • 🏠 Local only • 🔧 Development demo</div>
                </div>
              </div>
              
              {/* Advanced Mode Controls */}
              {useAdvancedMode && (
                <div className="mt-6 p-4 bg-purple-50 rounded-lg border border-purple-200">
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
            </div>

            {/* Main Input Form */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Your Prompt</h2>
              
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
            
            {/* Quality Metrics Dashboard */}
            {qualityMetrics && (
              <QualityMetrics 
                metrics={qualityMetrics} 
                overallScore={results?.qualityMetrics.overall}
              />
            )}
          </div>

          {/* Right Column - Recent Sessions & Stats */}
          <div className="xl:col-span-1 space-y-6">
            {/* Quick Stats */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Stats</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {recentSessions?.length || 0}
                  </div>
                  <div className="text-xs text-gray-600">Total Sessions</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {recentSessions?.filter(s => s.status === "completed").length || 0}
                  </div>
                  <div className="text-xs text-gray-600">Completed</div>
                </div>
              </div>
            </div>

            {/* Recent Sessions */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Recent Optimizations</h3>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              
              {historyLoading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-3 text-gray-600">Loading sessions...</p>
                </div>
              ) : recentSessions.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className="text-gray-500 font-medium">No optimizations yet</p>
                  <p className="text-sm text-gray-400 mt-1">Start by optimizing your first prompt!</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {recentSessions.map((session) => (
                    <div key={session._id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                      <div className="flex justify-between items-start mb-3">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          session.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : session.status === "processing"
                            ? "bg-yellow-100 text-yellow-800"
                            : session.status === "failed"
                            ? "bg-red-100 text-red-800"
                            : "bg-gray-100 text-gray-800"
                        }`}>
                          {session.status === "completed" && (
                            <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                          {session.status || "pending"}
                        </span>
                        {session.qualityScore && (
                          <div className="flex items-center">
                            <svg className="w-4 h-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            <span className="text-sm font-medium text-gray-700">
                              {session.qualityScore.toFixed(1)}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      <div className="space-y-2">
                        <div>
                          <div className="text-xs font-medium text-gray-500 mb-1">Original:</div>
                          <p className="text-sm text-gray-700 line-clamp-2">
                            {session.prompt?.originalPrompt.substring(0, 80)}
                            {(session.prompt?.originalPrompt.length || 0) > 80 && "..."}
                          </p>
                        </div>
                        
                        {session.finalResults?.bestPrompt && (
                          <div>
                            <div className="text-xs font-medium text-gray-500 mb-1">Optimized:</div>
                            <p className="text-sm text-gray-900 line-clamp-2">
                              {session.finalResults.bestPrompt.substring(0, 80)}
                              {session.finalResults.bestPrompt.length > 80 && "..."}
                            </p>
                          </div>
                        )}
                      </div>
                      
                      <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center">
                          <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {new Date(session.createdAt).toLocaleDateString()}
                        </div>
                        <button className="text-blue-600 hover:text-blue-800 font-medium">
                          View Details
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Enhanced Footer */}
        <footer className="text-center mt-16 pb-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-xl shadow-lg p-8">
              <div className="flex flex-wrap justify-center items-center gap-6 text-sm text-gray-600">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                  <span>Qwen3:4b (Local)</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-red-500 rounded-full mr-2"></div>
                  <span>System Prompts (Not PromptWizard)</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>Next.js 15 & Convex</span>
                </div>
              </div>
              <div className="mt-4 text-xs text-red-600 font-medium">
                ⚠️ Development demo only - Not production ready • localhost:11434 required
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}