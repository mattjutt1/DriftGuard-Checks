/**
 * Feedback Modal Component
 * Allows users to provide feedback on optimization results
 */

import React, { useState } from 'react';
import { useFeedback } from '../hooks/useOptimization';
import { Id } from '../../convex/_generated/dataModel';

interface FeedbackModalProps {
  isVisible: boolean;
  onClose: () => void;
  sessionId: Id<'optimizationSessions'> | null;
}

export function FeedbackModal({ isVisible, onClose, sessionId }: FeedbackModalProps) {
  const [rating, setRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [improvementSuggestions, setImprovementSuggestions] = useState<string[]>(['']);
  const [isHelpful, setIsHelpful] = useState<boolean | undefined>(undefined);
  
  const { submitOptimizationFeedback, isSubmitting, error } = useFeedback();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!sessionId || rating === 0) return;

    const suggestions = improvementSuggestions.filter(s => s.trim() !== '');
    
    const success = await submitOptimizationFeedback(
      sessionId,
      rating,
      feedbackText || undefined,
      suggestions.length > 0 ? suggestions : undefined,
      isHelpful
    );

    if (success) {
      // Reset form
      setRating(0);
      setFeedbackText('');
      setImprovementSuggestions(['']);
      setIsHelpful(undefined);
      onClose();
    }
  };

  const addSuggestion = () => {
    setImprovementSuggestions([...improvementSuggestions, '']);
  };

  const updateSuggestion = (index: number, value: string) => {
    const updated = [...improvementSuggestions];
    updated[index] = value;
    setImprovementSuggestions(updated);
  };

  const removeSuggestion = (index: number) => {
    setImprovementSuggestions(improvementSuggestions.filter((_, i) => i !== index));
  };

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-semibold">Share Your Feedback</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Rating */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Overall Rating *
            </label>
            <div className="flex space-x-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setRating(star)}
                  className={`text-2xl transition-colors ${
                    star <= rating ? 'text-yellow-400' : 'text-gray-300'
                  } hover:text-yellow-400`}
                >
                  ★
                </button>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {rating === 0 && "Click to rate"}
              {rating === 1 && "Poor"}
              {rating === 2 && "Fair"}
              {rating === 3 && "Good"}
              {rating === 4 && "Very Good"}
              {rating === 5 && "Excellent"}
            </p>
          </div>

          {/* Helpfulness */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Was this optimization helpful?
            </label>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setIsHelpful(true)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isHelpful === true
                    ? 'bg-green-100 text-green-800 border border-green-300'
                    : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                }`}
              >
                👍 Yes, helpful
              </button>
              <button
                type="button"
                onClick={() => setIsHelpful(false)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isHelpful === false
                    ? 'bg-red-100 text-red-800 border border-red-300'
                    : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                }`}
              >
                👎 Not helpful
              </button>
            </div>
          </div>

          {/* Feedback Text */}
          <div>
            <label htmlFor="feedback" className="block text-sm font-medium text-gray-700 mb-2">
              Additional Comments
            </label>
            <textarea
              id="feedback"
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              rows={4}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Tell us what you liked or what could be improved..."
            />
          </div>

          {/* Improvement Suggestions */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Specific Improvement Suggestions
              </label>
              <button
                type="button"
                onClick={addSuggestion}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                + Add Suggestion
              </button>
            </div>
            <div className="space-y-2">
              {improvementSuggestions.map((suggestion, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={suggestion}
                    onChange={(e) => updateSuggestion(index, e.target.value)}
                    className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    placeholder="Suggest a specific improvement..."
                  />
                  {improvementSuggestions.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeSuggestion(index)}
                      className="text-red-500 hover:text-red-700 p-1"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex">
                <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="text-sm text-red-700">{error}</span>
              </div>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={rating === 0 || isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
            >
              {isSubmitting && (
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              )}
              {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}