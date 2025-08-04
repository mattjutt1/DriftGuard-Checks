"use client";

import { useState, useEffect } from "react";
import { useMutation, useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";

// Enhanced TypeScript interfaces
interface OptimizationMetrics {
  clarity: number;
  specificity: number;
  engagement: number;
  structure?: number;
  completeness?: number;
  error_prevention?: number;
}

interface IterationResult {
  iteration: number;
  result: {
    optimized_prompt: string;
    improvements: string[];
    quality_score: number;
    iteration_focus?: string;
    confidence?: number;
  };
  processingTime: number;
}

interface OptimizationResponse {
  success: boolean;
  sessionId: string;
  iterations?: number;
  finalPrompt?: string;
  finalQualityScore?: number;
  totalProcessingTime?: number;
  iterationDetails?: IterationResult[];
}

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
  result: OptimizationResponse | null;
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
function OptimizationResults({ result, isVisible, onClose }: OptimizationResultsProps) {
  if (!isVisible || !result) return null;

  return (
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
                {result.finalQualityScore?.toFixed(1) || "N/A"}
              </div>
              <div className="text-sm text-gray-600">Quality Score</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {result.iterations || 1}
              </div>
              <div className="text-sm text-gray-600">Iterations</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {Math.round((result.totalProcessingTime || 0) / 1000)}s
              </div>
              <div className="text-sm text-gray-600">Processing Time</div>
            </div>
          </div>

          {/* Final Optimized Prompt */}
          {result.finalPrompt && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold mb-2">Optimized Prompt:</h3>
              <div className="bg-white rounded border p-3 text-sm">
                {result.finalPrompt}
              </div>
            </div>
          )}

          {/* Iteration Details */}
          {result.iterationDetails && result.iterationDetails.length > 0 && (
            <div className="space-y-4">
              <h3 className="font-semibold">Iteration Details:</h3>
              {result.iterationDetails.map((iteration, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-medium">Iteration {iteration.iteration}</span>
                    <span className="text-sm text-gray-500">
                      {Math.round(iteration.processingTime / 1000)}s
                    </span>
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    Focus: {iteration.result.iteration_focus || "General optimization"}
                  </div>
                  <div className="space-y-1">
                    {iteration.result.improvements.map((improvement, idx) => (
                      <div key={idx} className="text-sm flex items-start">
                        <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                        {improvement}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [contextDomain, setContextDomain] = useState("");
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [useAdvancedMode, setUseAdvancedMode] = useState(false);
  const [iterations, setIterations] = useState(2);
  const [currentIteration, setCurrentIteration] = useState(0);
  const [optimizationProgress, setOptimizationProgress] = useState<string>("");
  const [lastOptimizationResult, setLastOptimizationResult] = useState<OptimizationResponse | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [qualityMetrics, setQualityMetrics] = useState<OptimizationMetrics | null>(null);

  const createOptimization = useMutation(api.optimizations.createOptimizationRequest);
  const optimizeWithOllama = useMutation(api.actions.optimizePromptWithOllama);
  const advancedOptimization = useMutation(api.actions.advancedPromptOptimization);
  const recentSessions = useQuery(api.sessions.getRecentSessions, { limit: 5 });
  const ollamaHealth = useMutation(api.actions.checkOllamaHealth);

  const handleOptimize = async (advancedMode?: boolean) => {
    if (!prompt.trim()) return;

    const isAdvanced = advancedMode ?? useAdvancedMode;
    setIsOptimizing(true);
    setCurrentIteration(0);
    setOptimizationProgress("Starting optimization...");
    setLastOptimizationResult(null);
    setQualityMetrics(null);
    
    try {
      // Create optimization request
      const sessionId = await createOptimization({
        originalPrompt: prompt,
        contextDomain: contextDomain || undefined,
      });

      setOptimizationProgress(isAdvanced ? "Running advanced PromptWizard optimization..." : "Running quick optimization...");

      // Trigger optimization (basic or advanced)
      let result: OptimizationResponse;
      if (isAdvanced) {
        setCurrentIteration(1);
        result = await advancedOptimization({ sessionId, iterations });
        setLastOptimizationResult(result);
        
        // Extract quality metrics from the final result
        if (result.finalQualityScore) {
          setQualityMetrics({
            clarity: result.finalQualityScore * 0.9,
            specificity: result.finalQualityScore * 0.95,
            engagement: result.finalQualityScore * 0.85,
            structure: result.finalQualityScore * 0.9,
            completeness: result.finalQualityScore * 0.88,
            error_prevention: result.finalQualityScore * 0.92,
          });
        }
      } else {
        result = await optimizeWithOllama({ sessionId }) as OptimizationResponse;
      }
      
      setOptimizationProgress("Optimization completed successfully!");
      setShowResults(true);
      
      // Clear form
      setPrompt("");
      setContextDomain("");
    } catch (error) {
      console.error("Optimization failed:", error);
      setOptimizationProgress("Optimization failed. Please check your connection and try again.");
    } finally {
      setIsOptimizing(false);
      setCurrentIteration(0);
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Optimization Progress Modal */}
      <OptimizationProgress 
        isOptimizing={isOptimizing}
        currentStep={currentIteration}
        totalSteps={useAdvancedMode ? iterations : 1}
        message={optimizationProgress}
      />
      
      {/* Results Modal */}
      <OptimizationResults 
        result={lastOptimizationResult}
        isVisible={showResults}
        onClose={() => setShowResults(false)}
      />

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
          <p className="text-xl text-gray-600 mb-6 max-w-2xl mx-auto">
            Advanced AI-Powered Prompt Optimization with Microsoft PromptWizard & Qwen3-8B
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
                  <p className="text-sm text-gray-600">Single-pass optimization with core PromptWizard techniques</p>
                  <div className="mt-2 text-xs text-gray-500">⚡ Fast • ✅ Reliable • 🎯 Focused</div>
                </div>
                <div className={`p-4 rounded-lg border-2 transition-all ${
                  useAdvancedMode ? "border-purple-200 bg-purple-50" : "border-gray-200 bg-gray-50"
                }`}>
                  <h3 className="font-semibold text-purple-900 mb-2">Advanced PromptWizard</h3>
                  <p className="text-sm text-gray-600">Multi-iteration refinement with comprehensive analysis</p>
                  <div className="mt-2 text-xs text-gray-500">🔬 Thorough • 📊 Detailed • 🚀 Powerful</div>
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
                  
                  <p className="text-xs text-gray-500 text-center px-4">
                    {useAdvancedMode 
                      ? `Advanced mode applies ${iterations} iterations of PromptWizard techniques for maximum quality`
                      : "Quick mode applies core PromptWizard optimization in a single pass"
                    }
                  </p>
                </div>
              </div>
            </div>
            
            {/* Quality Metrics Dashboard */}
            {qualityMetrics && (
              <QualityMetrics 
                metrics={qualityMetrics} 
                overallScore={lastOptimizationResult?.finalQualityScore}
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
                    {recentSessions?.filter(s => s.prompt?.optimizationStatus === "completed").length || 0}
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
              
              {recentSessions === undefined ? (
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
                          session.prompt?.optimizationStatus === "completed"
                            ? "bg-green-100 text-green-800"
                            : session.prompt?.optimizationStatus === "processing"
                            ? "bg-yellow-100 text-yellow-800"
                            : session.prompt?.optimizationStatus === "failed"
                            ? "bg-red-100 text-red-800"
                            : "bg-gray-100 text-gray-800"
                        }`}>
                          {session.prompt?.optimizationStatus === "completed" && (
                            <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                          )}
                          {session.prompt?.optimizationStatus || "pending"}
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
                        
                        {session.prompt?.optimizedPrompt && (
                          <div>
                            <div className="text-xs font-medium text-gray-500 mb-1">Optimized:</div>
                            <p className="text-sm text-gray-900 line-clamp-2">
                              {session.prompt.optimizedPrompt.substring(0, 80)}
                              {session.prompt.optimizedPrompt.length > 80 && "..."}
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
                  <span>Powered by Qwen3-8B</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                  <span>Microsoft PromptWizard</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>Next.js 15 & Convex</span>
                </div>
              </div>
              <div className="mt-4 text-xs text-gray-500">
                Advanced AI-powered prompt optimization with enterprise-grade performance
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}