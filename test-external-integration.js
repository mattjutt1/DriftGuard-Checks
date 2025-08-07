#!/usr/bin/env node

/**
 * Test External Ollama Integration
 * Creates a simple mock server to test Convex integration
 */

const express = require('express');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Mock Ollama API responses
app.get('/api/tags', (req, res) => {
  console.log('🏷️ Mock /api/tags called');
  res.json({
    models: [
      {
        name: 'qwen3:4b',
        modified_at: new Date().toISOString(),
        size: 2600000000,
        digest: 'sha256:mock-digest'
      }
    ]
  });
});

app.post('/api/generate', (req, res) => {
  const { model, prompt } = req.body;
  console.log(`🤖 Mock /api/generate called with model: ${model}`);
  console.log(`📝 Prompt: ${prompt?.substring(0, 100)}...`);

  // Simulate PromptWizard optimized response
  const mockResponse = `Based on your request, I'll provide an optimized response using Microsoft PromptWizard methodology:

**Expert Identity Applied**: ${model === 'qwen3:4b' ? 'I am an expert prompt optimization specialist with deep knowledge of AI system design and natural language processing.' : 'Generic AI assistant'}

**Step-by-Step Analysis**:
1. Your original prompt has been analyzed for clarity and specificity
2. Domain-specific optimization principles have been applied
3. Expert knowledge patterns have been integrated
4. Response structure has been optimized for effectiveness

**Optimized Response**: The enhanced prompt incorporates systematic optimization principles, expert identity framing, and clear structural guidelines that significantly improve AI response quality and accuracy.

This represents a Microsoft PromptWizard critique-and-refine optimization with quality scoring and iterative improvement methodology.`;

  res.json({
    model,
    created_at: new Date().toISOString(),
    response: mockResponse,
    done: true,
    context: [],
    total_duration: 2500000000,
    load_duration: 500000000,
    prompt_eval_count: prompt ? Math.floor(prompt.length / 4) : 50,
    prompt_eval_duration: 800000000,
    eval_count: Math.floor(mockResponse.length / 4),
    eval_duration: 1200000000
  });
});

const PORT = process.env.PORT || 11434;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Mock Ollama server running on http://0.0.0.0:${PORT}`);
  console.log(`🏷️ Test tags: curl http://localhost:${PORT}/api/tags`);
  console.log(`🤖 Test generate: curl -X POST http://localhost:${PORT}/api/generate -H "Content-Type: application/json" -d '{"model":"qwen3:4b","prompt":"Hello","stream":false}'`);
});
