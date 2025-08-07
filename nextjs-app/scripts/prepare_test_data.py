#!/usr/bin/env python3
"""
Prepare test datasets for PromptWizard evaluation
Downloads GSM8K dataset and formats it for PromptWizard
"""

import json
import os
from datasets import load_dataset

def prepare_gsm8k():
    """Download and prepare GSM8K dataset in PromptWizard format"""
    
    print("Downloading GSM8K dataset from Hugging Face...")
    dataset = load_dataset("openai/gsm8k", "main")
    
    # Create data directory
    data_dir = "/home/matt/prompt-wizard/nextjs-app/data/gsm8k"
    os.makedirs(data_dir, exist_ok=True)
    
    # Process train split
    print(f"Processing train split ({len(dataset['train'])} examples)...")
    train_data = []
    for item in dataset['train']:
        # Extract just the final answer from the solution
        answer_parts = item['answer'].split('####')
        if len(answer_parts) >= 2:
            final_answer = answer_parts[-1].strip()
        else:
            final_answer = item['answer'].strip()
            
        train_data.append({
            "question": item['question'],
            "answer": final_answer,
            "full_solution": item['answer']  # Keep full solution for reference
        })
    
    # Save train data
    train_file = os.path.join(data_dir, "train.jsonl")
    with open(train_file, 'w') as f:
        for item in train_data[:100]:  # Use first 100 for testing
            f.write(json.dumps(item) + '\n')
    print(f"Saved {min(100, len(train_data))} training examples to {train_file}")
    
    # Process test split
    print(f"Processing test split ({len(dataset['test'])} examples)...")
    test_data = []
    for item in dataset['test']:
        # Extract just the final answer from the solution
        answer_parts = item['answer'].split('####')
        if len(answer_parts) >= 2:
            final_answer = answer_parts[-1].strip()
        else:
            final_answer = item['answer'].strip()
            
        test_data.append({
            "question": item['question'],
            "answer": final_answer,
            "full_solution": item['answer']  # Keep full solution for reference
        })
    
    # Save test data
    test_file = os.path.join(data_dir, "test.jsonl")
    with open(test_file, 'w') as f:
        for item in test_data[:50]:  # Use first 50 for testing
            f.write(json.dumps(item) + '\n')
    print(f"Saved {min(50, len(test_data))} test examples to {test_file}")
    
    # Create a sample prompt template based on PromptWizard methodology
    prompt_template = {
        "task_description": "You are a mathematics expert. Your task is to solve grade school math problems step by step.",
        "base_instruction": "Let's think step by step to solve this problem.",
        "answer_format": "Provide your reasoning step by step, then give the final numerical answer only at the end.",
        "evaluation_criteria": {
            "correctness": "Does the answer match the expected numerical result?",
            "clarity": "Are the steps clearly explained?",
            "completeness": "Are all necessary steps included?",
            "efficiency": "Is the solution approach efficient?"
        }
    }
    
    # Save prompt template
    template_file = os.path.join(data_dir, "prompt_template.json")
    with open(template_file, 'w') as f:
        json.dump(prompt_template, f, indent=2)
    print(f"Saved prompt template to {template_file}")
    
    return train_data, test_data

def create_evaluation_metrics():
    """Create evaluation metrics based on PromptWizard's approach"""
    
    metrics = {
        "performance_metrics": {
            "accuracy": "Percentage of correct answers",
            "avg_steps": "Average number of reasoning steps",
            "consistency": "Consistency across similar problems"
        },
        "quality_metrics": {
            "clarity": {
                "description": "How clear and understandable is the prompt",
                "scoring": "Based on successful problem solving rate"
            },
            "specificity": {
                "description": "How specific are the instructions",
                "scoring": "Based on reduction in ambiguous responses"
            },
            "effectiveness": {
                "description": "Overall effectiveness in solving problems",
                "scoring": "Weighted combination of accuracy and efficiency"
            }
        },
        "evaluation_method": "Test prompts on sample problems and measure success rate"
    }
    
    # Save metrics definition
    metrics_dir = "/home/matt/prompt-wizard/nextjs-app/data"
    os.makedirs(metrics_dir, exist_ok=True)
    metrics_file = os.path.join(metrics_dir, "evaluation_metrics.json")
    
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Saved evaluation metrics to {metrics_file}")
    return metrics

if __name__ == "__main__":
    print("="*60)
    print("PromptWizard Test Data Preparation")
    print("="*60)
    
    # Prepare GSM8K dataset
    train_data, test_data = prepare_gsm8k()
    
    # Create evaluation metrics
    metrics = create_evaluation_metrics()
    
    print("\n" + "="*60)
    print("Data preparation complete!")
    print(f"Train examples: {min(100, len(train_data))}")
    print(f"Test examples: {min(50, len(test_data))}")
    print("\nNext steps:")
    print("1. Use train.jsonl to optimize prompts with PromptWizard")
    print("2. Evaluate optimized prompts on test.jsonl")
    print("3. Calculate real performance metrics instead of fake scores")
    print("="*60)