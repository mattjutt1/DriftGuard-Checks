# Railway-compatible Ollama server
FROM ollama/ollama:latest

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create Railway-compatible startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Use Railway PORT or default to 11434\n\
RAILWAY_PORT=${PORT:-11434}\n\
export OLLAMA_HOST="0.0.0.0:$RAILWAY_PORT"\n\
\n\
echo "🚂 Railway Ollama startup..."\n\
echo "Railway PORT: $RAILWAY_PORT"\n\
echo "OLLAMA_HOST: $OLLAMA_HOST"\n\
\n\
# Start ollama server\n\
echo "🚀 Starting Ollama server..."\n\
ollama serve > /tmp/ollama.log 2>&1 &\n\
OLLAMA_PID=$!\n\
\n\
# Wait for server to be ready\n\
echo "⏳ Waiting for server to respond..."\n\
for i in $(seq 1 60); do\n\
    if curl -s "http://localhost:$RAILWAY_PORT/api/tags" > /dev/null 2>&1; then\n\
        echo "✅ Server responding on port $RAILWAY_PORT"\n\
        break\n\
    fi\n\
    if [ $i -eq 60 ]; then\n\
        echo "❌ Server failed to start after 60 attempts"\n\
        echo "Ollama logs:"\n\
        cat /tmp/ollama.log || echo "No logs available"\n\
        exit 1\n\
    fi\n\
    echo "Attempt $i/60... (port $RAILWAY_PORT)"\n\
    sleep 2\n\
done\n\
\n\
# Download model in background after health check passes\n\
echo "📥 Downloading qwen3:4b model in background..."\n\
(ollama pull qwen3:4b > /tmp/model.log 2>&1 &)\n\
\n\
echo "🎉 Railway deployment ready!"\n\
echo "Health endpoint: http://0.0.0.0:$RAILWAY_PORT/api/tags"\n\
\n\
# Keep container alive\n\
wait $OLLAMA_PID\n\
' > /railway-start.sh && chmod +x /railway-start.sh

# Railway will set PORT - we don't hardcode it
# EXPOSE is for documentation but Railway uses PORT env var

CMD ["/bin/bash", "/railway-start.sh"]