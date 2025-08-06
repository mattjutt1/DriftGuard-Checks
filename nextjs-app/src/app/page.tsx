"use client";

import { useState } from "react";
import { useOptimization, useOptimizationHistory } from "../hooks/useOptimization";
import { OptimizationForm } from "../components/OptimizationForm";
import { ProgressDisplay } from "../components/ProgressDisplay";
import { QualityMetrics } from "../components/QualityMetrics";
import { ErrorHandling } from "../components/ErrorHandling";
import DemoPage from "./demo-page";

// Check if Convex is available
const convexUrl = process.env.NEXT_PUBLIC_CONVEX_URL;
const isConvexAvailable = convexUrl && convexUrl.trim() !== "";

interface OptimizationResultsProps {
  isVisible: boolean;
  onClose: () => void;
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
  // Hooks must be called unconditionally
  const [showResults, setShowResults] = useState(false);
  const [useAdvancedMode, setUseAdvancedMode] = useState(false);

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

  // If no Convex, show demo page after hooks
  if (!isConvexAvailable) {
    return <DemoPage />;
  }

  const handleOptimize = async (prompt: string, contextDomain: string, useAdvancedMode: boolean, iterations: number) => {
    if (!prompt.trim()) return;
    
    try {
      await startOptimization(prompt, contextDomain, useAdvancedMode, iterations);
      setShowResults(true);
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
    <div className="min-h-screen bg-gray-50">
      {/* Optimization Progress Modal */}
      <ProgressDisplay 
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
      <ErrorHandling 
        error={error}
        onDismiss={resetOptimization}
      />

      {/* Desktop App Layout */}
      <div className="desktop-app-layout flex">
        {/* Left Sidebar - Navigation & Tools */}
        <div className="desktop-sidebar w-80 border-r border-gray-200 flex flex-col">
          {/* Sidebar Header */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">PromptEvolver</h1>
                <p className="text-sm text-gray-500">AI Prompt Optimization</p>
              </div>
            </div>
          </div>

          {/* Navigation Menu */}
          <div className="flex-1 p-6">
            <nav className="space-y-2">
              <div className="nav-item active bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 011-1h1a2 2 0 100-4H7a1 1 0 01-1-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-blue-900">Optimize</h3>
                    <p className="text-sm text-blue-700">Main workspace</p>
                  </div>
                </div>
              </div>
              
              <button className="nav-item w-full text-left p-3 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">History</h3>
                    <p className="text-sm text-gray-500">Past optimizations</p>
                  </div>
                </div>
              </button>

              <button className="nav-item w-full text-left p-3 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">Analytics</h3>
                    <p className="text-sm text-gray-500">Performance metrics</p>
                  </div>
                </div>
              </button>

              <button className="nav-item w-full text-left p-3 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">Settings</h3>
                    <p className="text-sm text-gray-500">Configuration</p>
                  </div>
                </div>
              </button>
            </nav>
          </div>

          {/* Sidebar Footer */}
          <div className="p-6 border-t border-gray-200">
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
              <div className="flex items-start space-x-3">
                <svg className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-yellow-800">Development Demo</p>
                  <p className="text-xs text-yellow-700 mt-1">
                    Local Ollama required • Processing 60-120s • System prompts only
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={checkHealth}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm font-medium">System Health</span>
            </button>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="desktop-main-content flex overflow-hidden">
          {/* Central Workspace */}
          <div className="flex-1 p-8 overflow-y-auto custom-scrollbar">
            <div className="max-w-4xl mx-auto space-y-8">
              {/* Workspace Header */}
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Prompt Optimization Workspace</h2>
                  <p className="text-gray-600 mt-1">Create and refine AI prompts using advanced optimization techniques</p>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <div className="status-dot w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Ollama Connected</span>
                </div>
              </div>

              {/* Optimization Form - Redesigned for desktop */}
              <div className="desktop-card bg-white rounded-xl shadow-sm">
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-gray-900">New Optimization</h3>
                    <div className="flex bg-gray-100 rounded-lg p-1">
                      <button
                        onClick={() => setUseAdvancedMode(false)}
                        className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all desktop-focus ${
                          !useAdvancedMode
                            ? "bg-blue-600 text-white shadow-sm"
                            : "text-gray-600 hover:text-gray-900"
                        }`}
                      >
                        Quick
                      </button>
                      <button
                        onClick={() => setUseAdvancedMode(true)}
                        className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all desktop-focus ${
                          useAdvancedMode
                            ? "bg-purple-600 text-white shadow-sm"
                            : "text-gray-600 hover:text-gray-900"
                        }`}
                      >
                        Advanced
                      </button>
                    </div>
                  </div>
                </div>

                <OptimizationForm 
                  onOptimize={handleOptimize}
                  isOptimizing={isOptimizing}
                  useAdvancedMode={useAdvancedMode}
                  setUseAdvancedMode={setUseAdvancedMode}
                />
              </div>

              {/* Quality Metrics - Only show when available */}
              {qualityMetrics && (
                <div className="desktop-card bg-white rounded-xl shadow-sm">
                  <QualityMetrics 
                    metrics={qualityMetrics} 
                    overallScore={results?.qualityMetrics.overall}
                  />
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar - Status & History */}
          <div className="w-96 bg-white border-l border-gray-200 p-6 overflow-y-auto custom-scrollbar">
            {/* Status Panel */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
              <div className="space-y-3">
                <div className="desktop-card flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-green-900">Ollama</p>
                      <p className="text-sm text-green-700">Connected</p>
                    </div>
                  </div>
                  <div className="status-dot w-2 h-2 bg-green-500 rounded-full"></div>
                </div>

                <div className="desktop-card flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-blue-900">Qwen3:4b</p>
                      <p className="text-sm text-blue-700">Ready</p>
                    </div>
                  </div>
                  <div className="status-dot w-2 h-2 bg-blue-500 rounded-full"></div>
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Overview</h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="desktop-card text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {recentSessions?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">Total</div>
                </div>
                <div className="desktop-card text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {recentSessions?.filter(s => s.status === "completed").length || 0}
                  </div>
                  <div className="text-sm text-gray-600">Completed</div>
                </div>
              </div>
            </div>

            {/* Recent Sessions */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
                <button className="text-blue-600 hover:text-blue-800 text-sm font-medium desktop-focus">
                  View All
                </button>
              </div>
              
              {historyLoading ? (
                <div className="text-center py-8">
                  <div className="loading-pulse animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                  <p className="mt-2 text-sm text-gray-600">Loading...</p>
                </div>
              ) : recentSessions.length === 0 ? (
                <div className="text-center py-8">
                  <div className="w-12 h-12 mx-auto mb-3 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className="text-gray-500 font-medium text-sm">No sessions yet</p>
                  <p className="text-xs text-gray-400 mt-1">Start optimizing to see history</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentSessions.slice(0, 4).map((session) => (
                    <div key={session._id} className="desktop-card p-3 border border-gray-200 rounded-lg cursor-pointer">
                      <div className="flex justify-between items-start mb-2">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          session.status === "completed"
                            ? "bg-green-100 text-green-800"
                            : session.status === "processing"
                            ? "bg-yellow-100 text-yellow-800"
                            : session.status === "failed"
                            ? "bg-red-100 text-red-800"
                            : "bg-gray-100 text-gray-800"
                        }`}>
                          {session.status === "completed" && "✓ "}
                          {session.status || "pending"}
                        </span>
                        {session.qualityScore && (
                          <div className="flex items-center text-xs">
                            <svg className="w-3 h-3 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                            </svg>
                            <span className="text-gray-700">{session.qualityScore.toFixed(1)}</span>
                          </div>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-700 line-clamp-2 mb-2">
                        {session.prompt?.originalPrompt.substring(0, 60)}
                        {(session.prompt?.originalPrompt.length || 0) > 60 && "..."}
                      </p>
                      
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>{new Date(session.createdAt).toLocaleDateString()}</span>
                        <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}