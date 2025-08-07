#!/usr/bin/env python3
"""
Local test script for HF Space functionality
Tests the core optimization logic without requiring GPU or full model loading
"""

import json
import time
from typing import Dict, List, Any

def optimize_prompt_mock(
    original_prompt: str,
    task_description: str = "",
    optimization_mode: str = "balanced",
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> Dict[str, Any]:
    """
    Mock version of the optimization function for testing
    Simulates the response structure without loading the actual model
    """
    start_time = time.time()
    
    # Simulate processing delay
    time.sleep(0.5)
    
    # Create mock optimization based on input
    optimized = f"""[Optimized Version]

Task Context: {task_description if task_description else 'General optimization'}
Mode: {optimization_mode}

Original: {original_prompt}

Enhanced Prompt:
You are an expert assistant with deep knowledge in the relevant domain.

{original_prompt}

Please provide a comprehensive, well-structured response that:
1. Directly addresses the core request
2. Includes specific examples where relevant
3. Maintains clarity and coherence throughout
4. Concludes with actionable insights or next steps

Format your response in clear sections with appropriate headers."""
    
    # Generate mock improvements list
    improvements = [
        "Added role specification for better context",
        "Clarified expected output structure",
        "Enhanced specificity of requirements",
        "Included format guidelines",
        "Added completion criteria"
    ]
    
    # Calculate mock quality score
    base_score = 0.7
    if len(original_prompt) > 50:
        base_score += 0.05
    if task_description:
        base_score += 0.05
    if optimization_mode == "thorough":
        base_score += 0.1
    
    processing_time = time.time() - start_time
    
    return {
        "optimized_prompt": optimized,
        "improvements": improvements,
        "reasoning": f"Applied {optimization_mode} optimization strategy with focus on clarity and specificity",
        "expert_profile": "Prompt Engineering Specialist with expertise in structured communication",
        "quality_score": min(base_score, 0.95),
        "processing_time": f"{processing_time:.2f}s",
        "model": "Qwen3-30B-A3B-Instruct-2507 (Mock)",
        "mode": optimization_mode,
        "temperature": temperature
    }

def test_single_optimization():
    """Test single prompt optimization"""
    print("=" * 60)
    print("Testing Single Prompt Optimization")
    print("=" * 60)
    
    test_prompt = "Write a story about a robot"
    task_desc = "Creative writing for children's book"
    
    print(f"\nOriginal Prompt: {test_prompt}")
    print(f"Task Description: {task_desc}")
    print("\nOptimizing...")
    
    result = optimize_prompt_mock(
        test_prompt,
        task_desc,
        "balanced",
        0.7
    )
    
    print("\n✅ Optimization Complete!")
    print(f"\nQuality Score: {result['quality_score']:.2f}")
    print(f"Processing Time: {result['processing_time']}")
    print(f"\nImprovements Made:")
    for i, improvement in enumerate(result['improvements'], 1):
        print(f"  {i}. {improvement}")
    
    print(f"\nOptimized Prompt Preview:")
    print("-" * 40)
    print(result['optimized_prompt'][:300] + "...")
    
    return result

def test_batch_processing():
    """Test batch prompt processing"""
    print("\n" + "=" * 60)
    print("Testing Batch Processing")
    print("=" * 60)
    
    prompts = [
        "Explain quantum computing",
        "How to make pizza",
        "Debug this Python code"
    ]
    
    results = []
    for i, prompt in enumerate(prompts, 1):
        print(f"\nProcessing prompt {i}/{len(prompts)}: {prompt[:30]}...")
        result = optimize_prompt_mock(prompt, "", "quick", 0.7)
        result['prompt_number'] = i
        results.append(result)
        print(f"  ✓ Score: {result['quality_score']:.2f}")
    
    print(f"\n✅ Batch Complete! Processed {len(results)} prompts")
    return results

def test_api_format():
    """Test API request/response format"""
    print("\n" + "=" * 60)
    print("Testing API Format")
    print("=" * 60)
    
    # Simulate Gradio API request format
    api_request = {
        "data": [
            "Summarize this article",
            "News article summarization",
            "thorough",
            0.8
        ]
    }
    
    print("\nAPI Request:")
    print(json.dumps(api_request, indent=2))
    
    # Process request
    result = optimize_prompt_mock(*api_request["data"])
    
    # Format as Gradio API response
    api_response = {
        "data": [result],
        "is_generating": False,
        "duration": float(result["processing_time"].rstrip("s")),
        "average_duration": float(result["processing_time"].rstrip("s"))
    }
    
    print("\nAPI Response:")
    print(json.dumps(api_response, indent=2, default=str))
    
    return api_response

def main():
    """Run all tests"""
    print("\n🚀 PromptEvolver Local Test Suite")
    print("Testing HF Space functionality locally")
    print("=" * 60)
    
    try:
        # Test 1: Single optimization
        single_result = test_single_optimization()
        assert single_result is not None
        assert "optimized_prompt" in single_result
        print("✅ Single optimization test passed")
        
        # Test 2: Batch processing
        batch_results = test_batch_processing()
        assert len(batch_results) == 3
        print("✅ Batch processing test passed")
        
        # Test 3: API format
        api_result = test_api_format()
        assert "data" in api_result
        assert len(api_result["data"]) == 1
        print("✅ API format test passed")
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed successfully!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("1. Deploy to HF Spaces")
        print("2. Replace mock with actual model loading")
        print("3. Enable GPU acceleration")
        print("4. Test with live endpoint")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())