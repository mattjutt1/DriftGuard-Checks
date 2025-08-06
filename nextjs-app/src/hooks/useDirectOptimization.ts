/**
 * Direct API Optimization Hook
 * Bypasses Convex to call our local API route that connects directly to Ollama + Qwen3:4b
 */

import { useState, useCallback } from 'react';

// TypeScript interfaces
export interface OptimizationMetrics {
  clarity: number;
  specificity: number;
  engagement: number;
  structure: number;
  completeness: number;
  errorPrevention: number;
  overall: number;
}

export interface OptimizationResults {
  bestPrompt: string;
  improvements: string[];
  qualityMetrics: OptimizationMetrics;
  expertInsights: string[];
  originalPrompt: string;
  contextDomain: string;
  useAdvancedMode: boolean;
  processingTime: number;
}

export interface DirectOptimizationHookState {
  // Core state
  isOptimizing: boolean;
  error: string | null;
  
  // Progress tracking
  currentStep: number;
  totalSteps: number;
  progressMessage: string;
  currentIteration: number;
  
  // Results
  results: OptimizationResults | null;
  qualityMetrics: OptimizationMetrics | null;
  currentSession: any; // Mock session for compatibility
  
  // Actions
  startOptimization: (prompt: string, contextDomain?: string, advanced?: boolean, iterations?: number) => Promise<void>;
  resetOptimization: () => void;
  checkOllamaHealth: () => Promise<{ available: boolean; model: string; error?: string }>;
}

// Mock session data for compatibility
const createMockSession = (results: OptimizationResults) => ({
  _id: `session-${Date.now()}`,
  status: 'completed',
  iterationsCompleted: 3,
  processingTimeMs: 45000,
  qualityScore: results.qualityMetrics.overall,
  prompt: {
    originalPrompt: results.originalPrompt
  },
  createdAt: Date.now()
});

/**
 * Direct optimization hook that calls our API route instead of Convex
 */
export function useDirectOptimization(): DirectOptimizationHookState {
  // Local state
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(4);
  const [progressMessage, setProgressMessage] = useState('');
  const [currentIteration, setCurrentIteration] = useState(0);
  const [results, setResults] = useState<OptimizationResults | null>(null);
  const [qualityMetrics, setQualityMetrics] = useState<OptimizationMetrics | null>(null);
  const [currentSession, setCurrentSession] = useState<any>(null);

  // Simulate progress steps
  const simulateProgress = async (steps: string[]) => {
    setTotalSteps(steps.length);
    
    for (let i = 0; i < steps.length; i++) {
      setCurrentStep(i + 1);
      setProgressMessage(steps[i]);
      setCurrentIteration(i + 1);
      
      // Simulate processing time
      await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1500));
    }
  };

  // Start optimization function
  const startOptimization = useCallback(async (
    prompt: string,
    contextDomain = 'general',
    advanced = false,
    iterations = 2
  ) => {
    if (!prompt.trim()) {
      setError('Prompt cannot be empty');
      return;
    }

    try {
      // Reset state
      setIsOptimizing(true);
      setError(null);
      setCurrentStep(0);
      setProgressMessage('Initializing optimization...');
      setCurrentIteration(0);
      setResults(null);
      setQualityMetrics(null);
      setCurrentSession(null);

      console.log('🚀 DIRECT API: Starting real optimization');
      console.log('🚀 DIRECT API: Prompt:', prompt.substring(0, 50) + '...');
      console.log('🚀 DIRECT API: Domain:', contextDomain);
      console.log('🚀 DIRECT API: Advanced:', advanced);

      // Define progress steps based on mode
      const progressSteps = advanced ? [
        'Generating expert identity...',
        'Applying PromptWizard methodology...',
        'Processing with Qwen3:4b model...',
        'Calculating quality metrics...',
        'Finalizing optimization...'
      ] : [
        'Analyzing prompt structure...',
        'Applying critique_n_refine...',
        'Processing with Qwen3:4b...',
        'Generating improvements...'
      ];

      // Start progress simulation
      const progressPromise = simulateProgress(progressSteps);

      // Call our direct API route
      const response = await fetch('/api/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          contextDomain,
          useAdvancedMode: advanced
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'API request failed');
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || 'Optimization failed');
      }

      // Wait for progress simulation to complete
      await progressPromise;

      // Set final results
      setResults(data.result);
      setQualityMetrics(data.result.qualityMetrics);
      setCurrentSession(createMockSession(data.result));
      setProgressMessage('Optimization completed successfully!');

      console.log('🚀 DIRECT API: Optimization completed successfully');
      console.log('🚀 DIRECT API: Quality score:', data.result.qualityMetrics.overall);

    } catch (err) {
      console.error('🚀 DIRECT API: Optimization error:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setProgressMessage('Optimization failed');
    } finally {
      setIsOptimizing(false);
    }
  }, []);

  // Reset optimization state
  const resetOptimization = useCallback(() => {
    setIsOptimizing(false);
    setError(null);
    setCurrentStep(0);
    setTotalSteps(4);
    setProgressMessage('');
    setCurrentIteration(0);
    setResults(null);
    setQualityMetrics(null);
    setCurrentSession(null);
  }, []);

  // Health check function
  const checkOllamaHealth = useCallback(async () => {
    try {
      console.log('🩺 HEALTH CHECK: Testing direct API connection...');
      
      const response = await fetch('/api/optimize', {
        method: 'GET',
      });

      if (response.ok) {
        const healthData = await response.json();
        console.log('🩺 HEALTH CHECK: Success -', healthData);
        
        return {
          available: healthData.status === 'healthy',
          model: healthData.model || 'qwen3:4b',
          error: healthData.status !== 'healthy' ? healthData.error : undefined,
        };
      } else {
        throw new Error(`Health check failed: ${response.status}`);
      }
    } catch (err) {
      console.error('🩺 HEALTH CHECK: Error -', err);
      
      return {
        available: false,
        model: 'qwen3:4b',
        error: err instanceof Error ? err.message : 'Health check failed',
      };
    }
  }, []);

  return {
    // Core state
    isOptimizing,
    error,
    
    // Progress tracking
    currentStep,
    totalSteps,
    progressMessage,
    currentIteration,
    
    // Results
    results,
    qualityMetrics,
    currentSession,
    
    // Actions
    startOptimization,
    resetOptimization,
    checkOllamaHealth,
  };
}

// Mock history hook for compatibility
export function useDirectOptimizationHistory(limit = 10) {
  // Return empty array for now - could implement localStorage-based history later
  return {
    sessions: [],
    isLoading: false,
  };
}