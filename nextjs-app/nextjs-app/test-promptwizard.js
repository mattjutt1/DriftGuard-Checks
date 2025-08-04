#!/usr/bin/env node

// Manual test of PromptWizard optimization pipeline
// Test Cases: Simple, Creative, Technical, Complex

const testCases = [
  {
    id: 1,
    name: "Simple Task",
    prompt: "Write a summary",
    expectedImprovements: ["format requirements", "length specification", "audience context"]
  },
  {
    id: 2, 
    name: "Creative Prompt",
    prompt: "Write a story about a robot",
    expectedImprovements: ["character details", "setting description", "genre specification"]
  },
  {
    id: 3,
    name: "Technical Prompt", 
    prompt: "Explain machine learning",
    expectedImprovements: ["audience level", "depth specification", "examples requirement"]
  },
  {
    id: 4,
    name: "Complex Multi-step",
    prompt: "Analyze data and create presentation", 
    expectedImprovements: ["step breakdown", "deliverable specs", "format requirements"]
  }
];

async function testOllama(prompt) {
  const startTime = Date.now();
  
  try {
    const response = await fetch('http://localhost:11434/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'qwen3:4b',
        prompt: `You are PromptWizard, an advanced AI prompt optimization specialist. 

Optimize this prompt using PromptWizard methodology:

Original: "${prompt}"

Provide:
1. Optimized version with specific improvements
2. Quality scores (0-100) for: clarity, specificity, engagement, structure, completeness, error_prevention
3. List of key improvements made
4. Overall quality score improvement

Format response as JSON:
{
  "original_prompt": "${prompt}",
  "optimized_prompt": "improved version here",
  "quality_scores": {
    "clarity": 85,
    "specificity": 90, 
    "engagement": 80,
    "structure": 88,
    "completeness": 92,
    "error_prevention": 87,
    "overall": 87
  },
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "processing_time": "measured in ms"
}`,
        stream: false,
        options: {
          temperature: 0.7,
          max_tokens: 1024
        }
      })
    });

    const data = await response.json();
    const processingTime = Date.now() - startTime;
    
    return {
      success: true,
      response: data.response,
      processingTime,
      rawData: data
    };
    
  } catch (error) {
    return {
      success: false,
      error: error.message,
      processingTime: Date.now() - startTime
    };
  }
}

async function runTests() {
  console.log('🚀 PromptWizard Pipeline Testing\n');
  
  const results = [];
  
  for (const testCase of testCases) {
    console.log(`📝 Testing: ${testCase.name}`);
    console.log(`Original: "${testCase.prompt}"`);
    console.log('Processing...\n');
    
    const result = await testOllama(testCase.prompt);
    
    if (result.success) {
      console.log(`✅ Success (${result.processingTime}ms)`);
      console.log(`Response: ${result.response.substring(0, 200)}...\n`);
      
      // Try to parse JSON from response
      try {
        const jsonMatch = result.response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          console.log(`Quality Score: ${parsed.quality_scores?.overall || 'N/A'}`);
          console.log(`Improvements: ${parsed.improvements?.length || 0} identified\n`);
        }
      } catch (e) {
        console.log('Could not parse JSON response\n');
      }
      
    } else {
      console.log(`❌ Failed: ${result.error} (${result.processingTime}ms)\n`);
    }
    
    results.push({
      testCase,
      result,
      timestamp: new Date().toISOString()
    });
  }
  
  // Summary
  console.log('📊 Test Summary:');
  const successful = results.filter(r => r.result.success).length;
  const avgTime = results.reduce((sum, r) => sum + r.result.processingTime, 0) / results.length;
  
  console.log(`✅ Successful: ${successful}/${results.length}`);
  console.log(`⏱️  Average time: ${Math.round(avgTime)}ms`);
  console.log(`🎯 Sub-30s target: ${avgTime < 30000 ? 'PASS' : 'FAIL'}`);
  
  return results;
}

// Run the tests
runTests().catch(console.error);