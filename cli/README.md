# PromptEvolver CLI

A simple, beautiful command-line interface for PromptEvolver that connects to your existing Convex backend to provide terminal access to prompt optimization features using Microsoft PromptWizard.

## ✨ Features

- **Beautiful Terminal UI** - Rich progress indicators, panels, and colored output
- **Simple Commands** - Intuitive interface following KISS principles  
- **Batch Processing** - Optimize multiple prompts from files
- **Configurable** - Flexible optimization settings and output formats
- **Real-time Progress** - Live progress tracking with spinners and status updates
- **Error Handling** - Graceful error handling with helpful messages

## 🚀 Quick Start

### Installation

```bash
cd /home/matt/prompt-wizard/cli

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the CLI
pip install -e .
```

### Test the Installation

```bash
# Test all basic functionality
python test_cli.py

# View CLI demo with mock responses
python promptevolver_cli/test_example.py
```

## 📖 Usage

### Check System Health
```bash
promptevolver health
```

### Optimize a Single Prompt
```bash
# Quick optimization (1 iteration)
promptevolver optimize "Your prompt here"

# Advanced optimization (3 iterations)  
promptevolver optimize "Your prompt here" --mode advanced

# Customize settings
promptevolver optimize "Your prompt here" \
  --mode advanced \
  --rounds 5 \
  --no-reasoning \
  --no-expert-identity
```

### Batch Optimization
```bash
# Create a file with prompts (one per line)
echo "What is the capital of France?" > prompts.txt
echo "Explain quantum computing" >> prompts.txt

# Batch optimize
promptevolver batch prompts.txt

# Specify output file
promptevolver batch prompts.txt --output my_results.json
```

## 🎯 Commands

- `promptevolver health` - Check Ollama health and PromptWizard availability
- `promptevolver optimize PROMPT` - Optimize a single prompt
- `promptevolver batch FILE` - Batch optimize prompts from a file

## ⚙️ Options

### Optimize Command
- `--mode`, `-m` - Optimization mode: `quick` (1 iteration) or `advanced` (3 iterations)
- `--reasoning/--no-reasoning` - Generate expert reasoning (default: enabled)
- `--expert-identity/--no-expert-identity` - Generate expert identity (default: enabled) 
- `--rounds`, `-r` - Number of mutation rounds (default: 3)

### Batch Command
- `--output`, `-o` - Output file for results (default: results.json)
- `--mode`, `-m` - Optimization mode: `quick` or `advanced`

## 🔧 Configuration

The CLI connects to your Convex deployment at `https://resilient-guanaco-29.convex.cloud` by default. You can override this with the `CONVEX_URL` environment variable:

```bash
export CONVEX_URL="https://your-deployment.convex.cloud"
promptevolver health
```

## 🏗️ Architecture

This CLI is built with:
- **Click** - Command-line interface framework following 2025 best practices
- **Rich** - Beautiful terminal output and progress indicators
- **Requests** - HTTP client for Convex API calls
- **Python 3.8+** - Modern Python with type hints

The CLI connects directly to your existing Convex actions via HTTP API:
- `actions:checkOllamaHealth` - Health checks
- `actions:testOptimizationPipeline` - Prompt optimization
- `actions:optimizePromptWithOllama` - Session-based optimization

### API Integration

The CLI uses the Convex HTTP API format:
```python
POST /api/action
{
  "path": "actions:functionName",
  "args": {...},
  "format": "json"
}
```

Response format:
```python
{
  "status": "success",
  "value": {...}
}
```

## 📋 File Structure

```
cli/
├── promptevolver_cli/
│   ├── __init__.py          # Package info
│   ├── main.py              # Click CLI commands
│   ├── client.py            # Convex HTTP client
│   ├── config.py            # Configuration settings
│   └── test_example.py      # Demo with mock responses
├── setup.py                 # Package setup
├── test_cli.py             # Installation tests
├── test_prompts.txt        # Example prompts for testing
├── README.md               # This file
└── venv/                   # Virtual environment
```

## 🎬 Examples

### Health Check
```bash
$ promptevolver health

Checking PromptWizard Health...
⠙ Connecting to backend...

✅ Service Available
🤖 Model: Microsoft PromptWizard + Qwen3:4b
```

### Single Prompt Optimization
```bash
$ promptevolver optimize "Write a Python function"

Optimizing Prompt (quick mode)...
╭─────────────── Original Prompt ───────────────╮
│ Write a Python function                       │
╰───────────────────────────────────────────────╯

✅ Optimization Complete!

╭─────────────── ✨ Optimized Prompt ───────────────╮
│ You are a Python programming expert...        │
╰───────────────────────────────────────────────────╯

📊 Quality Score: 8.7
```

### Batch Processing
```bash
$ promptevolver batch test_prompts.txt

Batch Optimization (quick mode)
📄 Input: test_prompts.txt
📝 Output: results.json

📊 Found 5 prompts to optimize
⠙ Optimizing prompt 3/5...

┏━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric        ┃ Count ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Total Prompts │ 5     │
│ Successful    │ 5     │
│ Failed        │ 0     │
│ Output File   │ results.json │
└───────────────┴───────┘

✅ Results saved to results.json
```

## 🐛 Troubleshooting

### API Connection Issues
The CLI currently expects specific Convex function names. If you get "function not found" errors:

1. Check your Convex deployment is running
2. Verify function names match in your `convex/actions.ts`
3. Try the demo mode: `python promptevolver_cli/test_example.py`

### Missing Dependencies
```bash
# Reinstall dependencies
pip install click requests rich python-dotenv typing-extensions
```

## 🚧 Current Status

**Working Features:**
- ✅ CLI structure and commands
- ✅ Beautiful terminal interface
- ✅ Batch processing logic
- ✅ Configuration system
- ✅ Error handling

**In Progress:**
- 🔄 API authentication
- 🔄 Function name resolution
- 🔄 Real Convex integration

**Demo Mode Available:** Run `python promptevolver_cli/test_example.py` to see the complete interface working with mock data.

## 🎯 Next Steps

1. **Fix API Authentication** - Resolve Convex function calling
2. **Add Session Management** - Implement proper session handling
3. **Add More Output Formats** - CSV, YAML, etc.
4. **Add Configuration File** - Support for `.promptevolver.yaml` config files
5. **Add Caching** - Cache optimization results for faster re-runs

---

**Built with ❤️ following KISS principles and modern Python best practices.**