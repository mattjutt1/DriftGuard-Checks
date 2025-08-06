#!/bin/bash

# Start Ollama server and pull Qwen3:4b model
set -e

echo "🚀 Starting external Ollama server for PromptEvolver"
echo "=================================================="

# Ensure OLLAMA_HOST is set
export OLLAMA_HOST=${OLLAMA_HOST:-0.0.0.0:11434}

# Start Ollama in background
/usr/bin/ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Ollama failed to start after 30 seconds"
        exit 1
    fi
    sleep 1
done

# Pull Qwen3:4b model if not already present
echo "📥 Checking for Qwen3:4b model..."
if ! /usr/bin/ollama list | grep -q "qwen3:4b"; then
    echo "⬇️ Pulling Qwen3:4b model (this may take several minutes)..."
    /usr/bin/ollama pull qwen3:4b
    echo "✅ Qwen3:4b model downloaded successfully!"
else
    echo "✅ Qwen3:4b model already available!"
fi

# Test the model
echo "🧪 Testing model availability..."
if /usr/bin/ollama list | grep -q "qwen3:4b"; then
    echo "✅ External Ollama server ready with Qwen3:4b!"
    echo "🌐 Server accessible at: http://0.0.0.0:11434"
    echo "📊 Available models:"
    /usr/bin/ollama list
else
    echo "❌ Model test failed"
    exit 1
fi

# Keep the container running
echo "🔄 Server running. Press Ctrl+C to stop."
wait $OLLAMA_PID