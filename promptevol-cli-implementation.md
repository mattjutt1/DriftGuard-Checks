# PromptEvolver CLI Bridge Implementation Guide

## Overview

This document provides a complete implementation guide for building a CLI bridge middleware between Claude Code CLI and the PromptEvolver application, incorporating Microsoft PromptWizard evaluation standards for comprehensive prompt optimization assessment.

## System Architecture

The CLI bridge system consists of four main layers:

1. **CLI Interface Layer** - User-facing command line interface
2. **Bridge Middleware Layer** - Evaluation engine and processing logic  
3. **PromptEvolver Application Layer** - Your existing production system with Qwen3-4B
4. **PromptWizard Standards Layer** - Microsoft's evaluation methodology integration

## Installation & Setup

```bash
# Clone and setup the CLI bridge
git clone <your-cli-bridge-repo>
cd promptevol-cli-bridge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize configuration
promptevol-eval init --model qwen3-4b --endpoint http://localhost:11434
```

## Core Commands

### 1. Initialize System
```bash
promptevol-eval init --model qwen3-4b --framework promptwizard
```

### 2. Evaluate Single Prompt
```bash
promptevol-eval evaluate "Your prompt here" --standard promptwizard --metrics all
```

### 3. Optimize Prompt
```bash
promptevol-eval optimize "Your prompt" --method promptwizard --iterations 5
```

### 4. Run Benchmarks
```bash
promptevol-eval benchmark --dataset gsm8k --standard promptwizard
```

### 5. Validate Results
```bash
promptevol-eval validate --prompt optimized_prompt.txt --test-set test_data.jsonl
```

### 6. Generate Reports
```bash
promptevol-eval report --session session_id --format comprehensive
```

## PromptWizard Evaluation Standards

### Core Metrics (Weighted Scoring)
- **Accuracy (40%)**: Primary performance metric - percentage of correct answers
- **Efficiency (30%)**: API calls and token usage optimization  
- **Consistency (20%)**: Performance stability across multiple mini-batches
- **Cost Effectiveness (10%)**: Performance per dollar spent on API calls

### Evaluation Methodology
- **Mini-batch Evaluation**: 5 training examples per batch (PromptWizard standard)
- **LLM-as-a-Judge**: Automated quality assessment using natural language criteria
- **Critique Analysis**: Feedback-driven refinement recommendations
- **Performance Profiling**: Comparative analysis against baselines

### Supported Datasets
- **Mathematical Reasoning**: GSM8k, SVAMP, AQUARAT
- **Instruction Following**: BigBench Instruction Induction (BBII)
- **General Reasoning**: BigBench Hard (BBH)
- **Custom Datasets**: Task-specific evaluation sets

## Implementation Details

### Core Evaluator Class
```python
class PromptWizardCompatibleEvaluator:
    def __init__(self, promptevolver_endpoint: str, model_name: str = "qwen3-4b"):
        self.endpoint = promptevolver_endpoint
        self.model = model_name
        self.session = aiohttp.ClientSession()
        
        # PromptWizard-compatible components
        self.mini_batch_evaluator = MiniBatchEvaluator(batch_size=5)
        self.llm_judge = LLMAsJudgeEvaluator()
        self.critique_analyzer = CritiqueAnalyzer()
        self.performance_tracker = PerformanceTracker()
    
    async def evaluate_with_promptwizard_standard(
        self, 
        prompt: str, 
        mode: str = "comprehensive",
        dataset: str = None
    ) -> PromptWizardEvaluationResult:
        
        # Stage 1: Send to PromptEvolver for optimization
        optimization_result = await self.optimize_via_promptevolver(prompt)
        
        # Stage 2: PromptWizard-style mini-batch evaluation
        mini_batch_scores = await self.mini_batch_evaluator.evaluate(
            prompt=optimization_result.optimized_prompt,
            examples=self.load_evaluation_examples(dataset),
            batch_size=5
        )
        
        # Stage 3: LLM-as-judge scoring
        llm_judge_scores = await self.llm_judge.evaluate(
            original=prompt,
            optimized=optimization_result.optimized_prompt,
            criteria=self.get_task_specific_criteria(dataset)
        )
        
        # Stage 4: Critique analysis
        critique_feedback = await self.critique_analyzer.analyze(
            prompt=optimization_result.optimized_prompt,
            performance_data=mini_batch_scores,
            task_requirements=self.get_task_requirements(dataset)
        )
        
        # Stage 5: Comprehensive scoring
        overall_score = self.calculate_promptwizard_score(
            accuracy=mini_batch_scores.accuracy,
            efficiency=optimization_result.efficiency_metrics,
            consistency=mini_batch_scores.consistency,
            task_alignment=llm_judge_scores.task_alignment
        )
        
        return PromptWizardEvaluationResult(
            original_prompt=prompt,
            optimized_prompt=optimization_result.optimized_prompt,
            accuracy_score=mini_batch_scores.accuracy,
            efficiency_score=optimization_result.efficiency_metrics,
            consistency_score=mini_batch_scores.consistency,
            task_alignment_score=llm_judge_scores.task_alignment,
            overall_score=overall_score,
            critique_feedback=critique_feedback,
            api_usage=optimization_result.api_usage,
            token_usage=optimization_result.token_usage,
            processing_time=optimization_result.processing_time,
            comparison_to_baselines=self.compare_to_baselines(overall_score)
        )
```

### Mini-Batch Evaluator
```python
class MiniBatchEvaluator:
    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size
        self.max_eval_batches = 10  # PromptWizard default
        
    async def evaluate(self, prompt: str, examples: List[Dict], batch_size: int = None):
        batch_size = batch_size or self.batch_size
        batches = self.create_mini_batches(examples, batch_size)
        
        batch_scores = []
        for i, batch in enumerate(batches[:self.max_eval_batches]):
            batch_score = await self.evaluate_batch(prompt, batch)
            batch_scores.append(batch_score)
            
            # Early stopping if consistently poor performance
            if len(batch_scores) >= 3 and all(score < 0.3 for score in batch_scores[-3:]):
                break
        
        return MiniBatchResult(
            accuracy=np.mean(batch_scores),
            consistency=1.0 - np.std(batch_scores),  # Higher consistency = lower std dev
            batch_scores=batch_scores,
            total_batches=len(batch_scores)
        )
```

### LLM-as-Judge Implementation
```python
class LLMAsJudgeEvaluator:
    def __init__(self):
        self.judge_prompt_template = '''
        You are an expert evaluator for prompt optimization systems.
        
        Evaluate the following optimized prompt based on these criteria:
        1. Task Alignment: How well does the prompt align with the intended task?
        2. Instruction Quality: Are the instructions clear, specific, and actionable?
        3. Example Integration: How well are examples integrated and utilized?
        4. Reasoning Quality: Does the prompt encourage proper reasoning?
        
        Original Prompt: {original}
        Optimized Prompt: {optimized}
        Task Requirements: {task_requirements}
        
        Provide scores (0-100) for each criterion and overall assessment.
        Format your response as JSON with scores and detailed reasoning.
        '''
    
    async def evaluate(self, original: str, optimized: str, criteria: Dict):
        judge_prompt = self.judge_prompt_template.format(
            original=original,
            optimized=optimized,
            task_requirements=criteria.get('task_requirements', 'General task')
        )
        
        response = await self.call_llm_judge(judge_prompt)
        scores = self.parse_judge_response(response)
        
        return LLMJudgeResult(
            task_alignment=scores.get('task_alignment', 0),
            instruction_quality=scores.get('instruction_quality', 0),
            example_integration=scores.get('example_integration', 0),
            reasoning_quality=scores.get('reasoning_quality', 0),
            overall_score=scores.get('overall', 0),
            detailed_feedback=scores.get('reasoning', '')
        )
```

## Evaluation Workflow

1. **Initialize** - Setup evaluation environment with PromptWizard standards
2. **Optimize** - Send prompt to PromptEvolver for optimization using Qwen3-4B
3. **Mini-batch Evaluate** - Apply 5-example mini-batch evaluation methodology
4. **LLM Judge** - Run automated quality assessment with natural language criteria
5. **Critique Analysis** - Generate feedback and improvement recommendations
6. **Score Calculation** - Compute weighted overall score using PromptWizard metrics
7. **Baseline Comparison** - Compare against DSPy, PromptAgent, APO baselines
8. **Report Generation** - Export comprehensive evaluation results

## Output Formats

### JSON Format
```json
{
  "evaluation_id": "eval_12345",
  "original_prompt": "Your original prompt",
  "optimized_prompt": "Optimized version",
  "scores": {
    "accuracy": 85.2,
    "efficiency": 92.1,
    "consistency": 78.9,
    "cost_effectiveness": 94.5,
    "overall": 87.6
  },
  "metrics": {
    "api_calls": 147,
    "token_usage": 2843,
    "processing_time": 12.4,
    "improvement_percentage": 23.8
  },
  "critique_feedback": "Detailed improvement suggestions...",
  "baseline_comparison": {
    "dspy": 78.2,
    "promptagent": 68.8,
    "apo": 25.7,
    "promptwizard": 87.6
  }
}
```

### Table Format
```
┌─────────────────────┬───────────┬──────────────┬─────────────────┐
│ Metric              │ Score     │ Weight       │ Contribution    │
├─────────────────────┼───────────┼──────────────┼─────────────────┤
│ Accuracy            │ 85.2      │ 40%          │ 34.1            │
│ Efficiency          │ 92.1      │ 30%          │ 27.6            │
│ Consistency         │ 78.9      │ 20%          │ 15.8            │
│ Cost Effectiveness  │ 94.5      │ 10%          │ 9.5             │
├─────────────────────┼───────────┼──────────────┼─────────────────┤
│ Overall Score       │ 87.6      │ 100%         │ 87.6            │
└─────────────────────┴───────────┴──────────────┴─────────────────┘
```

## Configuration Files

### promptevol_config.yaml
```yaml
# PromptWizard-compatible configuration
evaluation:
  framework: "promptwizard"
  batch_size: 5
  max_eval_batches: 10
  scoring_weights:
    accuracy: 0.40
    efficiency: 0.30
    consistency: 0.20
    cost_effectiveness: 0.10

promptevolver:
  endpoint: "http://localhost:11434"
  model: "qwen3-4b"
  timeout: 30

datasets:
  gsm8k:
    path: "data/gsm8k/"
    format: "jsonl"
    answer_extraction: "numeric"
  
  bbii:
    path: "data/bbii/"
    format: "jsonl"
    answer_extraction: "custom"

output:
  formats: ["json", "table", "report"]
  export_path: "results/"
  include_graphs: true
```

## Key Features

### PromptWizard Compatibility
- ✅ Mini-batch evaluation (5 examples per batch)
- ✅ LLM-as-a-judge scoring methodology
- ✅ Critique-driven refinement analysis
- ✅ Performance profile curve generation
- ✅ Cost-effectiveness tracking (API calls + tokens)
- ✅ Task-aware synthetic example evaluation
- ✅ Chain-of-thought effectiveness measurement

### Integration Advantages
- 🔧 **Zero Additional Cost** - Uses your existing Qwen3-4B deployment
- 🚀 **Seamless Integration** - Works with your current PromptEvolver setup
- 📊 **Academic-Grade Reports** - Publication-ready evaluation results
- 🔄 **Continuous Improvement** - Feedback loops for model enhancement
- 📈 **Baseline Comparisons** - Compare against state-of-the-art methods
- 🎯 **Task-Specific** - Supports multiple domains and use cases

## Usage Examples

### Basic Evaluation
```bash
# Evaluate a single prompt
promptevol-eval evaluate "Write a professional email to a client" --standard promptwizard

# Optimize and then evaluate
promptevol-eval optimize "Solve this math problem step by step" --method promptwizard --iterations 5
```

### Benchmark Testing
```bash
# Run GSM8k benchmark
promptevol-eval benchmark --dataset gsm8k --standard promptwizard --baseline dspy

# Custom dataset evaluation
promptevol-eval benchmark --dataset custom --path ./my_dataset.jsonl --standard promptwizard
```

### Comprehensive Analysis
```bash
# Generate detailed report
promptevol-eval report --session eval_session_123 --format comprehensive --include metrics,graphs,recommendations
```

## Next Steps

1. **Implementation** - Use the provided architecture and code samples
2. **Testing** - Validate with your existing PromptEvolver deployment
3. **Integration** - Connect to your Qwen3-4B model endpoint
4. **Customization** - Adapt evaluation criteria for your specific use cases
5. **Deployment** - Set up automated evaluation pipelines
6. **Monitoring** - Track performance improvements over time

## Support

For implementation questions or technical support, refer to:
- Microsoft PromptWizard documentation
- PromptEvolver application logs
- CLI bridge middleware error handling
- Evaluation standards validation testing

---

*This implementation guide provides a complete foundation for building a CLI bridge that enhances your PromptEvolver application with Microsoft PromptWizard evaluation standards, enabling comprehensive prompt optimization assessment with zero additional API costs.*