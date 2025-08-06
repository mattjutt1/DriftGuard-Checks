# Railway Ollama - Working version based on research
FROM ollama/ollama:latest

# Create models directory
RUN mkdir -p /root/.ollama/models

# Set working directory
WORKDIR /root

# Railway provides PORT, we need to use it with OLLAMA_HOST
# Note: Some environments need explicit 0.0.0.0 binding
ENV OLLAMA_MODELS=/root/.ollama/models

# Start Ollama with proper host binding
# Using exec form to ensure signals are properly handled
CMD ["/bin/sh", "-c", "OLLAMA_HOST=0.0.0.0:${PORT:-11434} exec ollama serve"]