/**
 * PromptWizard Core Implementation
 * Microsoft PromptWizard algorithm adapted for Qwen3:4b via Ollama
 */

import { ollamaClient, OllamaResponse } from "./ollama";

// PromptWizard configuration matching CLAUDE.md requirements
export const PROMPTWIZARD_CONFIG = {
  mutateRefineIterations: 3,
  mutationRounds: 3,
  seenSetSize: 25,
  fewShotCount: 3,
  generateReasoning: true,
  generateExpertIdentity: true,
  temperature: 0.7,
  maxTokens: 1024,
} as const;

export type MutationType = "specific" | "engaging" | "structured";

export interface QualityScores {
  clarity: number;
  specificity: number;
  engagement: number;
  structure: number;
  completeness: number;
  errorPrevention: number;
  overall: number;
}

export interface MutationResult {
  mutatedPrompt: string;
  qualityScores: QualityScores;
  reasoning?: string;
}

export interface OptimizationResult {
  bestPrompt: string;
  improvements: string[];
  qualityMetrics: QualityScores;
  reasoning?: string;
  expertInsights?: string[];
}

/**
 * System prompts optimized for Qwen3:4b model
 */
export const SYSTEM_PROMPTS = {
  /**
   * Expert Identity Generation
   * Generates domain-specific expert persona for the given prompt
   */
  EXPERT_IDENTITY: `You are an AI system specializing in creating expert identities for prompt optimization.

Your task: Analyze the given prompt and generate a concise expert identity (2-3 sentences) that would be most qualified to improve this prompt.

Focus on:
- Relevant domain expertise
- Specific skills needed for this prompt type
- Professional background that adds credibility

Format your response as a direct expert identity statement.

Example: "I am a senior UX researcher with 10 years of experience in user behavior analysis and conversion optimization. I specialize in crafting clear, actionable prompts that drive specific user behaviors."`,

  /**
   * Prompt Mutation - Specificity Focus
   * Makes prompts more specific and detailed
   */
  MUTATION_SPECIFIC: `You are an expert prompt engineer specializing in making prompts more specific and detailed.

Your task: Take the given prompt and create a more specific version that:
- Adds concrete details and examples
- Specifies desired output format
- Includes relevant constraints or parameters
- Eliminates ambiguity

Keep the core intent but make everything more precise and actionable.

Return only the improved prompt, no explanations.`,

  /**
   * Prompt Mutation - Engagement Focus
   * Makes prompts more engaging and compelling
   */
  MUTATION_ENGAGING: `You are an expert prompt engineer specializing in creating engaging and compelling prompts.

Your task: Take the given prompt and create a more engaging version that:
- Uses active, compelling language
- Adds motivation or urgency where appropriate
- Makes the request more interesting or appealing
- Maintains professionalism while increasing engagement

Keep the core intent but make it more compelling and motivating.

Return only the improved prompt, no explanations.`,

  /**
   * Prompt Mutation - Structure Focus
   * Improves prompt organization and clarity
   */
  MUTATION_STRUCTURED: `You are an expert prompt engineer specializing in prompt structure and organization.

Your task: Take the given prompt and create a better structured version that:
- Organizes information in logical sections
- Uses clear formatting (bullet points, numbers, sections)
- Separates context, task, and requirements clearly
- Improves overall readability and flow

Keep the core intent but make the structure much clearer.

Return only the improved prompt, no explanations.`,

  /**
   * Quality Scoring System
   * Evaluates prompts across 6 dimensions
   */
  QUALITY_SCORER: `You are an expert prompt evaluator. Rate the given prompt on these 6 dimensions (0-100 scale):

1. CLARITY: How clear and understandable is the prompt?
2. SPECIFICITY: How specific and detailed is the request?
3. ENGAGEMENT: How engaging and compelling is the language?
4. STRUCTURE: How well organized and formatted is the prompt?
5. COMPLETENESS: Does it include all necessary information?
6. ERROR_PREVENTION: How well does it prevent misunderstandings?

Respond ONLY in this exact JSON format:
{
  "clarity": 85,
  "specificity": 70,
  "engagement": 65,
  "structure": 80,
  "completeness": 75,
  "errorPrevention": 90,
  "overall": 77
}

The overall score should be the weighted average with clarity and specificity being most important.`,

  /**
   * Improvement Analysis
   * Analyzes what improvements were made
   */
  IMPROVEMENT_ANALYZER: `You are an expert prompt analyst. Compare the original prompt with the optimized version and identify the key improvements made.

List 3-5 specific improvements in this format:
- Improvement description

Focus on concrete changes that make the prompt more effective.

Return only the bullet-pointed list of improvements, no other text.`,

  /**
   * Expert Insights Generator
   * Provides domain-specific insights based on expert identity
   */
  EXPERT_INSIGHTS: `Based on your expert identity, provide 2-3 professional insights about this optimized prompt.

Focus on:
- Why these changes make the prompt more effective
- Domain-specific best practices applied
- Potential impact on results

Format as bullet points starting with "•"

Return only the insights, no other text.`,
} as const;

/**
 * PromptWizard Core Class
 */
export class PromptWizard {
  private config: typeof PROMPTWIZARD_CONFIG;

  constructor(config: Partial<typeof PROMPTWIZARD_CONFIG> = {}) {
    this.config = { ...PROMPTWIZARD_CONFIG, ...config };
  }

  /**
   * Generate expert identity for the given prompt
   */
  async generateExpertIdentity(prompt: string): Promise<string> {
    try {
      const response = await ollamaClient.generate(
        `PROMPT TO ANALYZE:\n"${prompt}"`,
        {
          system: SYSTEM_PROMPTS.EXPERT_IDENTITY,
          temperature: this.config.temperature,
          max_tokens: 200,
        }
      );

      return response.response.trim();
    } catch (error) {
      throw new Error(`Failed to generate expert identity: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Mutate prompt based on type
   */
  async mutatePrompt(
    prompt: string,
    mutationType: MutationType,
    expertIdentity?: string
  ): Promise<string> {
    const systemPrompts = {
      specific: SYSTEM_PROMPTS.MUTATION_SPECIFIC,
      engaging: SYSTEM_PROMPTS.MUTATION_ENGAGING,
      structured: SYSTEM_PROMPTS.MUTATION_STRUCTURED,
    };

    const systemPrompt = expertIdentity 
      ? `${expertIdentity}\n\n${systemPrompts[mutationType]}`
      : systemPrompts[mutationType];

    try {
      const response = await ollamaClient.generate(
        `PROMPT TO IMPROVE:\n"${prompt}"`,
        {
          system: systemPrompt,
          temperature: this.config.temperature,
          max_tokens: this.config.maxTokens,
        }
      );

      return response.response.trim();
    } catch (error) {
      throw new Error(`Failed to mutate prompt: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Score prompt quality across all dimensions
   */
  async scorePrompt(prompt: string): Promise<QualityScores> {
    try {
      const response = await ollamaClient.generate(
        `PROMPT TO EVALUATE:\n"${prompt}"`,
        {
          system: SYSTEM_PROMPTS.QUALITY_SCORER,
          temperature: 0.1, // Low temperature for consistent scoring
          max_tokens: 200,
        }
      );

      // Parse JSON response
      const scoreText = response.response.trim();
      let scores: QualityScores;

      try {
        scores = JSON.parse(scoreText);
      } catch (parseError) {
        // Fallback: try to extract numbers from response
        const numbers = scoreText.match(/\d+/g);
        if (numbers && numbers.length >= 6) {
          scores = {
            clarity: parseInt(numbers[0]),
            specificity: parseInt(numbers[1]),
            engagement: parseInt(numbers[2]),
            structure: parseInt(numbers[3]),
            completeness: parseInt(numbers[4]),
            errorPrevention: parseInt(numbers[5]),
            overall: Math.round((
              parseInt(numbers[0]) * 0.2 +
              parseInt(numbers[1]) * 0.2 +
              parseInt(numbers[2]) * 0.15 +
              parseInt(numbers[3]) * 0.15 +
              parseInt(numbers[4]) * 0.15 +
              parseInt(numbers[5]) * 0.15
            )),
          };
        } else {
          throw new Error('Could not parse quality scores');
        }
      }

      // Validate scores are in range
      const validatedScores: QualityScores = {
        clarity: Math.max(0, Math.min(100, scores.clarity || 50)),
        specificity: Math.max(0, Math.min(100, scores.specificity || 50)),
        engagement: Math.max(0, Math.min(100, scores.engagement || 50)),
        structure: Math.max(0, Math.min(100, scores.structure || 50)),
        completeness: Math.max(0, Math.min(100, scores.completeness || 50)),
        errorPrevention: Math.max(0, Math.min(100, scores.errorPrevention || 50)),
        overall: Math.max(0, Math.min(100, scores.overall || 50)),
      };

      return validatedScores;
    } catch (error) {
      throw new Error(`Failed to score prompt: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Analyze improvements between original and optimized prompt
   */
  async analyzeImprovements(originalPrompt: string, optimizedPrompt: string): Promise<string[]> {
    try {
      const response = await ollamaClient.generate(
        `ORIGINAL PROMPT:\n"${originalPrompt}"\n\nOPTIMIZED PROMPT:\n"${optimizedPrompt}"`,
        {
          system: SYSTEM_PROMPTS.IMPROVEMENT_ANALYZER,
          temperature: 0.3,
          max_tokens: 300,
        }
      );

      // Parse bullet points
      const improvements = response.response
        .split('\n')
        .filter(line => line.trim().startsWith('-') || line.trim().startsWith('•'))
        .map(line => line.replace(/^[-•]\s*/, '').trim())
        .filter(line => line.length > 0);

      return improvements.length > 0 ? improvements : ['General prompt optimization applied'];
    } catch (error) {
      throw new Error(`Failed to analyze improvements: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Generate expert insights
   */
  async generateExpertInsights(
    optimizedPrompt: string,
    expertIdentity: string
  ): Promise<string[]> {
    try {
      const response = await ollamaClient.generate(
        `OPTIMIZED PROMPT:\n"${optimizedPrompt}"`,
        {
          system: `${expertIdentity}\n\n${SYSTEM_PROMPTS.EXPERT_INSIGHTS}`,
          temperature: 0.5,
          max_tokens: 300,
        }
      );

      // Parse bullet points
      const insights = response.response
        .split('\n')
        .filter(line => line.trim().startsWith('•') || line.trim().startsWith('-'))
        .map(line => line.replace(/^[•-]\s*/, '').trim())
        .filter(line => line.length > 0);

      return insights.length > 0 ? insights : ['Prompt has been optimized for better performance'];
    } catch (error) {
      throw new Error(`Failed to generate expert insights: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  /**
   * Perform single mutation round with scoring
   */
  async performMutationRound(
    prompt: string,
    mutationType: MutationType,
    expertIdentity?: string
  ): Promise<MutationResult> {
    const mutatedPrompt = await this.mutatePrompt(prompt, mutationType, expertIdentity);
    const qualityScores = await this.scorePrompt(mutatedPrompt);

    return {
      mutatedPrompt,
      qualityScores,
    };
  }

  /**
   * Find best prompt from multiple candidates based on quality scores
   */
  selectBestPrompt(candidates: Array<{ prompt: string; scores: QualityScores }>): {
    prompt: string;
    scores: QualityScores;
  } {
    if (candidates.length === 0) {
      throw new Error('No candidates provided');
    }

    // Find candidate with highest overall score
    let bestCandidate = candidates[0];
    let highestScore = bestCandidate.scores.overall;

    for (const candidate of candidates.slice(1)) {
      if (candidate.scores.overall > highestScore) {
        bestCandidate = candidate;
        highestScore = candidate.scores.overall;
      }
    }

    return bestCandidate;
  }

  /**
   * Check Ollama health
   */
  async checkHealth(): Promise<{ available: boolean; model: string; error?: string }> {
    return await ollamaClient.healthCheck();
  }
}

// Export default instance
export const promptWizard = new PromptWizard();