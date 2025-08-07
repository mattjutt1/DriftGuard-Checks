# Railway Ollama - Simplest Possible Version
FROM ollama/ollama:latest

# Just run Ollama with PORT binding - no scripts
ENTRYPOINT ["/bin/sh", "-c", "OLLAMA_HOST=0.0.0.0:${PORT:-11434} ollama serve"]
