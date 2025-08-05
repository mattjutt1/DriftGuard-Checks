/**
 * Custom React Hook for Prompt Optimization
 * Provides complete integration with Convex backend for PromptWizard optimization
 */

import { useState, useCallback, useEffect } from 'react';
import { useMutation, useQuery } from 'convex/react';
import { api } from '../../convex/_generated/api';
import { Id } from '../../convex/_generated/dataModel';

// TypeScript interfaces matching backend schema
export interface OptimizationMetrics {
  clarity: number;
  specificity: number;
  engagement: number;
  structure: number;
  completeness: number;
  errorPrevention: number;
  overall: number;
}

export interface ProgressStep {
  step: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  timestamp: number;
  details?: string;
}

export interface MutationHistoryItem {
  iteration: number;
  round: number;
  mutationType: 'specific' | 'engaging' | 'structured';
  originalPrompt: string;
  mutatedPrompt: string;
  qualityScores: OptimizationMetrics;
  timestamp: number;
}

export interface OptimizationResults {
  bestPrompt: string;
  improvements: string[];
  qualityMetrics: OptimizationMetrics;
  reasoning?: string;
  expertInsights?: string[];
}

export interface OptimizationSession {
  _id: Id<'optimizationSessions'>;
  promptId: Id<'prompts'>;
  userId: Id<'users'>;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  processingTimeMs?: number;
  qualityScore?: number;
  iterationsCompleted?: number;
  currentIteration?: number;
  errorMessage?: string;
  expertIdentity?: string;
  progressSteps?: ProgressStep[];
  mutationHistory?: MutationHistoryItem[];
  finalResults?: OptimizationResults;
  createdAt: number;
  updatedAt?: number;
}

export interface OptimizationHookState {
  // Core state
  isOptimizing: boolean;
  currentSession: OptimizationSession | null;
  error: string | null;
  
  // Progress tracking
  currentStep: number;
  totalSteps: number;
  progressMessage: string;
  currentIteration: number;
  
  // Results
  results: OptimizationResults | null;
  qualityMetrics: OptimizationMetrics | null;
  
  // Actions
  startOptimization: (prompt: string, contextDomain?: string, advanced?: boolean, iterations?: number) => Promise<void>;
  resetOptimization: () => void;
  retryOptimization: () => Promise<void>;
  
  // Health check
  checkOllamaHealth: () => Promise<{ available: boolean; model: string; error?: string }>;
}

/**
 * Main optimization hook
 */
export function useOptimization(): OptimizationHookState {
  // Local state
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<Id<'optimizationSessions'> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps, setTotalSteps] = useState(0);
  const [progressMessage, setProgressMessage] = useState('');
  const [currentIteration, setCurrentIteration] = useState(0);
  const [results, setResults] = useState<OptimizationResults | null>(null);
  const [qualityMetrics, setQualityMetrics] = useState<OptimizationMetrics | null>(null);
  const [lastOptimizationParams, setLastOptimizationParams] = useState<{
    prompt: string;
    contextDomain?: string;
    advanced?: boolean;
    iterations?: number;
  } | null>(null);

  // Convex mutations
  const createOptimization = useMutation(api.optimizations.createOptimizationRequest);
  const quickOptimize = useMutation(api.actions.quickOptimize);
  const advancedOptimize = useMutation(api.actions.advancedOptimize);
  const ollamaHealth = useMutation(api.actions.checkOllamaHealth);

  // Convex queries - get current session data
  const currentSession = useQuery(
    api.optimizations.getSession,
    currentSessionId ? { sessionId: currentSessionId } : 'skip'
  );

  // Real-time progress tracking
  useEffect(() => {
    if (currentSession && isOptimizing) {
      // Update progress based on session state
      if (currentSession.progressSteps) {
        const completedSteps = currentSession.progressSteps.filter(step => step.status === 'completed').length;
        const processingSteps = currentSession.progressSteps.filter(step => step.status === 'processing').length;
        
        setCurrentStep(completedSteps + processingSteps);
        setTotalSteps(currentSession.progressSteps.length);
        
        // Find current processing step for message
        const processingStep = currentSession.progressSteps.find(step => step.status === 'processing');
        if (processingStep) {
          setProgressMessage(processingStep.step);
        }
      }

      // Update current iteration
      if (currentSession.currentIteration) {
        setCurrentIteration(currentSession.currentIteration);
      }

      // Check if optimization completed
      if (currentSession.status === 'completed') {
        setIsOptimizing(false);
        if (currentSession.finalResults) {
          setResults(currentSession.finalResults);
          setQualityMetrics(currentSession.finalResults.qualityMetrics);
        }
        setProgressMessage('Optimization completed successfully!');
      }

      // Check if optimization failed
      if (currentSession.status === 'failed') {
        setIsOptimizing(false);
        setError(currentSession.errorMessage || 'Optimization failed');
        setProgressMessage('Optimization failed');
      }
    }
  }, [currentSession, isOptimizing]);

  // Start optimization function
  const startOptimization = useCallback(async (
    prompt: string,
    contextDomain?: string,
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
      setTotalSteps(0);
      setProgressMessage('Starting optimization...');
      setCurrentIteration(0);
      setResults(null);
      setQualityMetrics(null);
      
      // Store params for retry
      setLastOptimizationParams({ prompt, contextDomain, advanced, iterations });

      // Create optimization session
      const sessionId = await createOptimization({
        originalPrompt: prompt,
        contextDomain: contextDomain || undefined,
      });

      setCurrentSessionId(sessionId);
      setProgressMessage(advanced ? 'Running advanced PromptWizard optimization...' : 'Running quick optimization...');

      // Start optimization
      let result;
      if (advanced) {
        setTotalSteps(3); // expert identity, iterations, finalization
        result = await advancedOptimize({ 
          sessionId, 
          maxIterations: iterations 
        });
      } else {
        setTotalSteps(4); // expert identity, mutations, selection, improvements
        result = await quickOptimize({ sessionId });
      }

      if (!result.success) {
        throw new Error(result.error || 'Optimization failed');
      }

    } catch (err) {
      console.error('Optimization error:', err);
      setIsOptimizing(false);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      setProgressMessage('Optimization failed');
    }
  }, [createOptimization, quickOptimize, advancedOptimize]);

  // Reset optimization state
  const resetOptimization = useCallback(() => {
    setIsOptimizing(false);
    setCurrentSessionId(null);
    setError(null);
    setCurrentStep(0);
    setTotalSteps(0);
    setProgressMessage('');
    setCurrentIteration(0);
    setResults(null);
    setQualityMetrics(null);
    setLastOptimizationParams(null);
  }, []);

  // Retry last optimization
  const retryOptimization = useCallback(async () => {
    if (lastOptimizationParams) {
      await startOptimization(
        lastOptimizationParams.prompt,
        lastOptimizationParams.contextDomain,
        lastOptimizationParams.advanced,
        lastOptimizationParams.iterations
      );
    }
  }, [lastOptimizationParams, startOptimization]);

  // Health check function
  const checkOllamaHealth = useCallback(async () => {
    try {
      const health = await ollamaHealth({});
      return health;
    } catch (err) {
      return {
        available: false,
        model: 'qwen3:4b',
        error: err instanceof Error ? err.message : 'Health check failed',
      };
    }
  }, [ollamaHealth]);

  return {
    // Core state
    isOptimizing,
    currentSession,
    error,
    
    // Progress tracking
    currentStep,
    totalSteps,
    progressMessage,
    currentIteration,
    
    // Results
    results,
    qualityMetrics,
    
    // Actions
    startOptimization,
    resetOptimization,
    retryOptimization,
    checkOllamaHealth,
  };
}

/**
 * Hook for accessing optimization history
 */
export function useOptimizationHistory(limit = 10) {
  const recentSessions = useQuery(api.sessions.getRecentSessions, { limit });
  
  return {
    sessions: recentSessions || [],
    isLoading: recentSessions === undefined,
  };
}

/**
 * Hook for managing user feedback
 */
export function useFeedback() {
  const submitFeedback = useMutation(api.sessions.submitFeedback);
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitOptimizationFeedback = useCallback(async (
    sessionId: Id<'optimizationSessions'>,
    rating: number,
    feedbackText?: string,
    improvementSuggestions?: string[],
    isHelpful?: boolean
  ) => {
    try {
      setIsSubmitting(true);
      setError(null);
      
      await submitFeedback({
        sessionId,
        rating,
        feedbackText,
        improvementSuggestions,
        isHelpful,
      });
      
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit feedback');
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }, [submitFeedback]);

  return {
    submitOptimizationFeedback,
    isSubmitting,
    error,
  };
}

/**
 * Hook for error handling with automatic retry logic
 */
export function useOptimizationErrorHandler() {
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);
  
  const handleError = useCallback((error: string, retryFunction?: () => Promise<void>) => {
    console.error('Optimization error:', error);
    
    // Auto-retry logic for transient errors
    const isTransientError = error.includes('connection') || 
                           error.includes('timeout') || 
                           error.includes('network');
    
    if (isTransientError && retryCount < 3 && retryFunction) {
      setTimeout(async () => {
        setIsRetrying(true);
        setRetryCount(prev => prev + 1);
        
        try {
          await retryFunction();
          setRetryCount(0);
        } catch (err) {
          console.error('Retry failed:', err);
        } finally {
          setIsRetrying(false);
        }
      }, Math.pow(2, retryCount) * 1000); // Exponential backoff
    }
  }, [retryCount]);

  const resetRetry = useCallback(() => {
    setRetryCount(0);
    setIsRetrying(false);
  }, []);

  return {
    handleError,
    retryCount,
    isRetrying,
    resetRetry,
  };
}