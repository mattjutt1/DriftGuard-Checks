"""
PromptEvolver HF Space - Working Version
"""

import gradio as gr
import json
import time

# Try to import advanced features, fallback if not available
try:
    import spaces
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    class spaces:
        @staticmethod
        def GPU(duration=60):
            def decorator(func):
                return func
            return decorator

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    MODEL_SUPPORT = True
except ImportError:
    MODEL_SUPPORT = False

# Model configuration
# Note: Qwen3-30B-A3B requires newer transformers, falling back to Qwen2.5
MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"  # Works with transformers 4.45.2

# Global model variables
model = None
tokenizer = None

def load_model():
    """Try to load the model"""
    global model, tokenizer
    
    if not MODEL_SUPPORT:
        print("Transformers not available, using mock mode")
        return False
    
    try:
        print(f"Loading {MODEL_NAME}...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
        
        # For Pro plan with GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=dtype,
            device_map="auto" if device == "cuda" else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        print(f"Model loaded on {device}!")
        return True
    except Exception as e:
        print(f"Could not load model: {e}")
        return False

# Try loading at startup
MODEL_LOADED = load_model()

@spaces.GPU(duration=60) if GPU_AVAILABLE else lambda f: f
def optimize_prompt(
    original_prompt: str,
    task_description: str = "",
    optimization_mode: str = "balanced",
    temperature: float = 0.7
):
    """Optimize prompts using AI"""
    
    start_time = time.time()
    
    # Mock implementation for testing
    if not MODEL_LOADED:
        enhanced = f"""Enhanced Prompt:

Context: {task_description if task_description else 'General task'}
Mode: {optimization_mode}

You are an expert assistant. {original_prompt}

Please provide a detailed, well-structured response that:
1. Directly addresses the request
2. Includes relevant examples
3. Maintains clarity throughout"""
        
        return {
            "status": "mock_mode" if not MODEL_LOADED else "success",
            "optimized_prompt": enhanced,
            "improvements": [
                "Added expert role context",
                "Structured output format",
                "Enhanced clarity"
            ],
            "quality_score": 0.75,
            "processing_time": f"{time.time() - start_time:.2f}s",
            "model": "Mock Mode" if not MODEL_LOADED else MODEL_NAME
        }
    
    # Real model implementation
    try:
        prompt = f"""Optimize this prompt for clarity and effectiveness:

Original: {original_prompt}
Context: {task_description}
Mode: {optimization_mode}

Provide an enhanced version that is clearer and more effective."""

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
        
        if torch.cuda.is_available():
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                temperature=temperature,
                max_new_tokens=512,
                do_sample=True,
                top_p=0.95
            )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        return {
            "status": "success",
            "optimized_prompt": response,
            "improvements": ["AI-powered optimization applied"],
            "quality_score": 0.85,
            "processing_time": f"{time.time() - start_time:.2f}s",
            "model": MODEL_NAME
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "optimized_prompt": original_prompt,
            "improvements": [],
            "quality_score": 0.0,
            "processing_time": f"{time.time() - start_time:.2f}s"
        }

# Create Gradio interface
with gr.Blocks(title="PromptEvolver") as demo:
    gr.Markdown(f"""
    # 🚀 PromptEvolver
    
    **Model**: {MODEL_NAME if MODEL_LOADED else "Mock Mode (Model not loaded)"}  
    **GPU**: {"Available" if GPU_AVAILABLE else "Not available"}  
    **Status**: {"Ready" if MODEL_LOADED else "Running in test mode"}
    """)
    
    with gr.Row():
        with gr.Column():
            prompt_input = gr.Textbox(
                label="Original Prompt",
                placeholder="Enter your prompt to optimize...",
                lines=4
            )
            task_input = gr.Textbox(
                label="Task Description (Optional)",
                placeholder="What are you trying to achieve?",
                lines=2
            )
            with gr.Row():
                mode = gr.Radio(
                    ["quick", "balanced", "thorough"],
                    value="balanced",
                    label="Mode"
                )
                temp = gr.Slider(0.1, 1.0, 0.7, label="Temperature")
            
            optimize_btn = gr.Button("Optimize Prompt", variant="primary")
        
        with gr.Column():
            output = gr.JSON(label="Optimization Results")
    
    optimize_btn.click(
        fn=optimize_prompt,
        inputs=[prompt_input, task_input, mode, temp],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch()