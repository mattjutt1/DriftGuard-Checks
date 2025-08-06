# Railway Ollama - Debug Version to see what's happening
FROM ollama/ollama:latest

# Just run Ollama directly with PORT binding
CMD sh -c 'echo "Starting on PORT=${PORT:-11434}" && OLLAMA_HOST=0.0.0.0:${PORT:-11434} ollama serve'