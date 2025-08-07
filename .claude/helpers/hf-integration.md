# HF-INTEGRATION.md - HuggingFace Spaces Integration Specifics

## HuggingFace Spaces Integration

### **HuggingFace Spaces Configuration**
- **Space Type**: Gradio/Streamlit hybrid for optimal performance
- **Hardware**: GPU-enabled for Qwen3:4b model inference
- **Python Version**: 3.9+ for compatibility
- **Model**: Qwen3:4b (2.6GB, efficient inference)

### **Space Structure**
```
huggingface-space/
├── app.py                    # Main Gradio/Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # Space documentation
├── models/
│   └── qwen3-4b/            # Model files (if not using remote)
├── promptwizard/
│   ├── __init__.py
│   ├── optimizer.py         # PromptWizard integration
│   └── utils.py
├── api/
│   ├── __init__.py
│   ├── optimize.py          # API endpoints
│   └── health.py            # Health checks
└── static/                  # Static assets
    ├── css/
    └── js/
```

### **Key Integration Points**

#### **API Endpoints for Convex Integration**
```python
# api/optimize.py
@app.post("/api/v1/optimize")
async def optimize_prompt(request: OptimizeRequest):
    """
    Optimize prompt using PromptWizard + Qwen3:4b
    Compatible with Convex actions.optimizePromptWithOllama
    """
    try:
        # PromptWizard optimization
        optimized = await promptwizard_optimize(
            prompt=request.prompt,
            config=PROMPTWIZARD_CONFIG
        )
        
        return OptimizeResponse(
            original_prompt=request.prompt,
            optimized_prompt=optimized.prompt,
            improvements=optimized.improvements,
            quality_score=optimized.quality_score,
            processing_time=optimized.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check compatible with Convex health monitoring"""
    return {
        "status": "healthy",
        "model": "qwen3:4b",
        "promptwizard_version": PROMPTWIZARD_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### **PromptWizard Configuration for HF Spaces**
```python
# promptwizard/optimizer.py
import os
from promptwizard import PromptOptimizer

PROMPTWIZARD_CONFIG = {
    "mutate_refine_iterations": int(os.getenv("MUTATE_REFINE_ITERATIONS", 3)),
    "mutation_rounds": int(os.getenv("MUTATION_ROUNDS", 3)),
    "seen_set_size": int(os.getenv("SEEN_SET_SIZE", 25)),
    "few_shot_count": int(os.getenv("FEW_SHOT_COUNT", 3)),
    "generate_reasoning": os.getenv("GENERATE_REASONING", "true").lower() == "true",
    "generate_expert_identity": os.getenv("GENERATE_EXPERT_IDENTITY", "true").lower() == "true",
    "temperature": float(os.getenv("TEMPERATURE", 0.7)),
    "max_tokens": int(os.getenv("MAX_TOKENS", 1024)),
    "model_name": "qwen3:4b"
}

class HFSpaceOptimizer:
    def __init__(self):
        self.optimizer = PromptOptimizer(config=PROMPTWIZARD_CONFIG)
        self.model = self._load_qwen_model()
    
    def _load_qwen_model(self):
        """Load Qwen3:4b model optimized for HF Spaces"""
        # Implementation for HF Spaces model loading
        pass
    
    async def optimize(self, prompt: str) -> OptimizationResult:
        """Optimize prompt with performance monitoring"""
        start_time = time.time()
        
        result = await self.optimizer.optimize(prompt)
        
        processing_time = time.time() - start_time
        
        return OptimizationResult(
            prompt=result.optimized_prompt,
            improvements=result.improvements,
            quality_score=result.quality_score,
            processing_time=processing_time
        )
```

### **Gradio Interface for Testing**
```python
# app.py
import gradio as gr
from promptwizard.optimizer import HFSpaceOptimizer

optimizer = HFSpaceOptimizer()

def optimize_prompt_interface(prompt):
    """Gradio interface for prompt optimization"""
    if not prompt.strip():
        return "Please enter a prompt to optimize.", "", 0.0, 0.0
    
    try:
        result = await optimizer.optimize(prompt)
        return (
            result.prompt,
            "\n".join(result.improvements),
            result.quality_score,
            result.processing_time
        )
    except Exception as e:
        return f"Error: {str(e)}", "", 0.0, 0.0

# Gradio interface
interface = gr.Interface(
    fn=optimize_prompt_interface,
    inputs=[
        gr.Textbox(
            label="Original Prompt", 
            placeholder="Enter your prompt here...",
            lines=5
        )
    ],
    outputs=[
        gr.Textbox(label="Optimized Prompt", lines=5),
        gr.Textbox(label="Improvements", lines=3),
        gr.Number(label="Quality Score"),
        gr.Number(label="Processing Time (seconds)")
    ],
    title="PromptEvolver - HuggingFace Space",
    description="Optimize your prompts using Microsoft PromptWizard + Qwen3:4b"
)

if __name__ == "__main__":
    interface.launch()
```

### **Requirements and Dependencies**
```txt
# requirements.txt
gradio>=4.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
transformers>=4.35.0
torch>=2.1.0
numpy>=1.24.0
pydantic>=2.4.0
python-multipart>=0.0.6
# PromptWizard (custom install)
# Qwen model dependencies
```

### **Environment Variables for HF Spaces**
```bash
# HF Spaces environment variables
MUTATE_REFINE_ITERATIONS=3
MUTATION_ROUNDS=3
SEEN_SET_SIZE=25
FEW_SHOT_COUNT=3
GENERATE_REASONING=true
GENERATE_EXPERT_IDENTITY=true
TEMPERATURE=0.7
MAX_TOKENS=1024
CONVEX_WEBHOOK_URL=https://your-convex.convex.cloud/api/webhook
```

### **Integration with Convex Actions**
```typescript
// convex/actions.ts - Updated for HF Spaces
export const optimizePromptWithHFSpace = action({
  args: { 
    prompt: v.string(),
    sessionId: v.id("optimization_sessions")
  },
  handler: async (ctx, args) => {
    try {
      // Call HuggingFace Space API
      const response = await fetch(`${process.env.HF_SPACE_URL}/api/v1/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: args.prompt,
          session_id: args.sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HF Space optimization failed: ${response.statusText}`);
      }

      const result = await response.json();

      // Update session with results
      await ctx.db.patch(args.sessionId, {
        status: "completed",
        optimized_prompt: result.optimized_prompt,
        quality_score: result.quality_score,
        processing_time: result.processing_time,
        improvements: result.improvements
      });

      return result;
    } catch (error) {
      // Fallback to local optimization if HF Space fails
      console.error("HF Space failed, falling back to local:", error);
      return await fallbackOptimization(ctx, args);
    }
  },
});
```

### **Performance Optimization for HF Spaces**
```python
# Performance optimizations
OPTIMIZATION_CONFIG = {
    "batch_size": 1,  # HF Spaces memory constraints
    "max_concurrent": 3,  # Prevent OOM errors
    "cache_results": True,  # Cache common optimizations
    "timeout": 30,  # 30 second timeout
    "memory_limit": "8GB",  # HF Spaces limit
    "gpu_memory_fraction": 0.8  # Leave headroom
}
```

### **Monitoring and Logging**
```python
# Monitoring for HF Spaces
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class HFSpaceMonitor:
    @staticmethod
    def log_optimization(prompt_length: int, processing_time: float, quality_score: float):
        logging.info(f"Optimization completed - Length: {prompt_length}, Time: {processing_time:.2f}s, Quality: {quality_score:.2f}")
    
    @staticmethod
    def log_error(error: Exception, prompt_hash: str):
        logging.error(f"Optimization failed - Hash: {prompt_hash}, Error: {str(error)}")
```