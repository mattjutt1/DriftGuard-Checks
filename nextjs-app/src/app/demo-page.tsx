"use client";

import { useState } from "react";
import { OptimizationForm } from "../components/OptimizationForm";
import { ProgressDisplay } from "../components/ProgressDisplay";
import { QualityMetrics } from "../components/QualityMetrics";
import { ErrorHandling } from "../components/ErrorHandling";

// Mock data for demo mode
const mockMetrics = {
  clarity: 8.5,
  specificity: 7.8,
  engagement: 9.2,
  structure: 8.0,
  completeness: 8.7,
  errorPrevention: 7.5,
  overall: 8.3
};

const mockResults = {
  bestPrompt: "Create a comprehensive guide for implementing responsive web design using CSS Grid and Flexbox, including practical examples and best practices for modern browsers.",
  improvements: [
    "Enhanced specificity with technical details",
    "Added practical examples requirement",
    "Included modern browser compatibility focus",
    "Structured for comprehensive coverage"
  ],
  qualityMetrics: mockMetrics,
  reasoning: "The prompt was optimized for clarity and actionable outcomes.",
  expertInsights: [
    "Technical specificity improves response quality",
    "Practical examples make content more valuable",
    "Modern browser focus ensures relevance"
  ]
};

const mockSessions = [
  {
    _id: "demo-1" as any,
    status: "completed" as const,
    qualityScore: 8.3,
    prompt: {
      originalPrompt: "How to make a website responsive?"
    },
    finalResults: {
      bestPrompt: "Create a comprehensive guide for implementing responsive web design..."
    },
    createdAt: Date.now() - 86400000
  },
  {
    _id: "demo-2" as any,
    status: "completed" as const,
    qualityScore: 7.9,
    prompt: {
      originalPrompt: "Write about JavaScript functions"
    },
    finalResults: {
      bestPrompt: "Explain JavaScript functions with practical examples..."
    },
    createdAt: Date.now() - 172800000
  }
];

interface OptimizationResultsProps {
  isVisible: boolean;
  onClose: () => void;
}

// Optimization Results Modal Component
function OptimizationResults({ isVisible, onClose }: OptimizationResultsProps) {
  const [showFeedback, setShowFeedback] = useState(false);
  
  if (!isVisible) return null;

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
                {mockResults.qualityMetrics.overall.toFixed(1)}
              </div>
              <div className="text-sm text-gray-600">Quality Score</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">3</div>
              <div className="text-sm text-gray-600">Iterations</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">45s</div>
              <div className="text-sm text-gray-600">Processing Time</div>
            </div>
          </div>

          {/* Final Optimized Prompt */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold mb-2">Optimized Prompt:</h3>
            <div className="bg-white rounded border p-3 text-sm">
              {mockResults.bestPrompt}
            </div>
          </div>

          {/* Improvements List */}
          <div className="space-y-4">
            <h3 className="font-semibold">Key Improvements:</h3>
            <div className="bg-white rounded-lg border p-4">
              <div className="space-y-2">
                {mockResults.improvements.map((improvement, idx) => (
                  <div key={idx} className="text-sm flex items-start">
                    <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                    {improvement}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Expert Insights */}
          <div className="space-y-4">
            <h3 className="font-semibold">Expert Insights:</h3>
            <div className="bg-indigo-50 rounded-lg p-4">
              <div className="space-y-2">
                {mockResults.expertInsights?.map((insight, idx) => (
                  <div key={idx} className="text-sm flex items-start">
                    <span className="inline-block w-2 h-2 bg-indigo-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                    {insight}
                  </div>
                ))}
              </div>
            </div>
          </div>

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

      {/* Feedback Modal */}
      {showFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Demo Mode</h3>
            <p className="text-gray-600 mb-4">This is a demo deployment. Feedback functionality requires a backend connection.</p>
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

export default function DemoPage() {
  const [showResults, setShowResults] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(4);
  const [progressMessage, setProgressMessage] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleOptimize = async (prompt: string, contextDomain: string, useAdvancedMode: boolean, iterations: number) => {
    if (!prompt.trim()) return;
    
    setIsOptimizing(true);
    setError(null);
    setCurrentStep(0);
    setTotalSteps(4);
    setProgressMessage("Starting optimization...");

    // Simulate optimization process
    const steps = [
      "Analyzing prompt structure...",
      "Generating improvements...",
      "Running quality assessment...",
      "Finalizing results..."
    ];

    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i + 1);
      setProgressMessage(steps[i]);
      await new Promise(resolve => setTimeout(resolve, 1500));
    }

    setIsOptimizing(false);
    setProgressMessage("Optimization completed!");
    setShowResults(true);
  };

  const checkHealth = async () => {
    alert(JSON.stringify({
      status: "Demo Mode",
      message: "This is a frontend-only demo deployment. Backend health check requires Convex connection.",
      available: false,
      model: "qwen3:4b"
    }, null, 2));
  };

  const resetOptimization = () => {
    setError(null);
    setIsOptimizing(false);
    setCurrentStep(0);
    setProgressMessage("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
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
            <p className="text-lg font-semibold text-yellow-800 mb-2">🎯 Demo Mode - Frontend Only</p>
            <p className="text-sm text-yellow-700">
              This is a demo deployment showing the UI and simulated functionality • No backend processing
            </p>
          </div>
          <p className="text-xl text-gray-600 mb-6 max-w-2xl mx-auto">
            Advanced Prompt Optimization Demo - UI Preview
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button
              onClick={checkHealth}
              className="inline-flex items-center px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors shadow-md"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              System Health (Demo)
            </button>
          </div>
        </header>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Left Column - Optimization Form */}
          <OptimizationForm 
            onOptimize={handleOptimize}
            isOptimizing={isOptimizing}
          />
          
          {/* Quality Metrics Dashboard */}
          <div className="xl:col-span-2">
            <QualityMetrics 
              metrics={mockMetrics} 
              overallScore={mockResults.qualityMetrics.overall}
            />
          </div>

          {/* Right Column - Recent Sessions & Stats */}
          <div className="xl:col-span-1 space-y-6">
            {/* Quick Stats */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Stats</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {mockSessions.length}
                  </div>
                  <div className="text-xs text-gray-600">Demo Sessions</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {mockSessions.filter(s => s.status === "completed").length}
                  </div>
                  <div className="text-xs text-gray-600">Completed</div>
                </div>
              </div>
            </div>

            {/* Recent Sessions */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Demo Optimizations</h3>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {mockSessions.map((session) => (
                  <div key={session._id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start mb-3">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        {session.status}
                      </span>
                      <div className="flex items-center">
                        <svg className="w-4 h-4 text-yellow-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                        <span className="text-sm font-medium text-gray-700">
                          {session.qualityScore.toFixed(1)}
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <div className="text-xs font-medium text-gray-500 mb-1">Original:</div>
                        <p className="text-sm text-gray-700 line-clamp-2">
                          {session.prompt?.originalPrompt.substring(0, 80)}
                          {(session.prompt?.originalPrompt.length || 0) > 80 && "..."}
                        </p>
                      </div>
                      
                      <div>
                        <div className="text-xs font-medium text-gray-500 mb-1">Optimized:</div>
                        <p className="text-sm text-gray-900 line-clamp-2">
                          {session.finalResults?.bestPrompt.substring(0, 80)}
                          {session.finalResults?.bestPrompt.length! > 80 && "..."}
                        </p>
                      </div>
                    </div>
                    
                    <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                      <div className="flex items-center">
                        <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {new Date(session.createdAt).toLocaleDateString()}
                      </div>
                      <button className="text-blue-600 hover:text-blue-800 font-medium">
                        Demo Data
                      </button>
                    </div>
                  </div>
                ))}
              </div>
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
                  <span>Next.js 15 + React 19</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></div>
                  <span>Demo Mode - Frontend Only</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  <span>126 kB Bundle Size</span>
                </div>
              </div>
              <div className="mt-4 text-xs text-blue-600 font-medium">
                🎯 Frontend demo deployment - Full functionality requires Convex backend
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}