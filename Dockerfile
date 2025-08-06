# Production-ready Ollama deployment for Railway.app
# Based on Railway's official Ollama templates and 2025 best practices
FROM ollama/ollama:latest

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create the models directory
RUN mkdir -p /root/.ollama/models

# Create a production-ready startup script that handles Railway's PORT correctly
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Railway provides a dynamic PORT that we MUST use\n\
# Ollama needs OLLAMA_HOST to bind to 0.0.0.0:PORT\n\
if [ -z "$PORT" ]; then\n\
    echo "WARNING: No PORT environment variable set, using default 11434"\n\
    export PORT=11434\n\
fi\n\
\n\
# Set OLLAMA_HOST to bind to all interfaces on Railway PORT\n\
export OLLAMA_HOST="0.0.0.0:${PORT}"\n\
\n\
echo "========================================"\n\
echo "🚂 Railway Ollama Server Starting"\n\
echo "========================================"\n\
echo "PORT: ${PORT}"\n\
echo "OLLAMA_HOST: ${OLLAMA_HOST}"\n\
echo "OLLAMA_MODELS: /root/.ollama/models"\n\
echo "========================================"\n\
\n\
# Start Ollama serve in the background\n\
echo "Starting Ollama server..."\n\
ollama serve &\n\
OLLAMA_PID=$!\n\
\n\
# Wait for Ollama to be ready\n\
echo "Waiting for Ollama to be ready..."\n\
MAX_ATTEMPTS=30\n\
ATTEMPT=0\n\
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do\n\
    if nc -z localhost ${PORT} 2>/dev/null; then\n\
        echo "✅ Ollama is listening on port ${PORT}"\n\
        break\n\
    fi\n\
    ATTEMPT=$((ATTEMPT + 1))\n\
    echo "  Attempt ${ATTEMPT}/${MAX_ATTEMPTS}..."\n\
    sleep 2\n\
done\n\
\n\
if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then\n\
    echo "❌ Ollama failed to start after ${MAX_ATTEMPTS} attempts"\n\
    exit 1\n\
fi\n\
\n\
# Verify the API endpoint is responding\n\
echo "Verifying API endpoint..."\n\
for i in {1..10}; do\n\
    if curl -s "http://localhost:${PORT}/api/tags" > /dev/null 2>&1; then\n\
        echo "✅ API endpoint verified at http://localhost:${PORT}/api/tags"\n\
        break\n\
    fi\n\
    echo "  API check attempt ${i}/10..."\n\
    sleep 1\n\
done\n\
\n\
# Start downloading the Qwen3:4b model in the background\n\
echo "Starting model download in background..."\n\
(\n\
    sleep 5\n\
    echo "📥 Downloading Qwen3:4b model (this may take 5-10 minutes)..."\n\
    if ollama pull qwen3:4b; then\n\
        echo "✅ Qwen3:4b model successfully downloaded"\n\
        ollama list\n\
    else\n\
        echo "⚠️ Model download failed but server is running"\n\
    fi\n\
) &\n\
\n\
echo "========================================"\n\
echo "🎉 Ollama server is ready!"\n\
echo "Health endpoint: http://0.0.0.0:${PORT}/api/tags"\n\
echo "Model download continuing in background..."\n\
echo "========================================"\n\
\n\
# Keep the container running\n\
wait $OLLAMA_PID\n\
' > /start.sh && chmod +x /start.sh

# Railway will provide the PORT, we don't EXPOSE a specific port
# The health check will use Railway's PORT

CMD ["/bin/bash", "/start.sh"]