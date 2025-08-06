# Railway Ollama Deployment - Ultra Compatible Version
FROM ollama/ollama:latest

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create models directory
RUN mkdir -p /root/.ollama/models

# Create startup script with echo (most compatible)
RUN echo '#!/bin/bash' > /start.sh && \
    echo 'set -e' >> /start.sh && \
    echo '' >> /start.sh && \
    echo 'echo "========================================"' >> /start.sh && \
    echo 'echo "Railway Ollama Server Starting..."' >> /start.sh && \
    echo 'echo "========================================"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Use Railway PORT or default' >> /start.sh && \
    echo 'if [ -z "$PORT" ]; then' >> /start.sh && \
    echo '    export PORT=11434' >> /start.sh && \
    echo '    echo "No PORT set, using default: $PORT"' >> /start.sh && \
    echo 'else' >> /start.sh && \
    echo '    echo "Using Railway PORT: $PORT"' >> /start.sh && \
    echo 'fi' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Set OLLAMA_HOST to bind to all interfaces' >> /start.sh && \
    echo 'export OLLAMA_HOST="0.0.0.0:${PORT}"' >> /start.sh && \
    echo 'echo "OLLAMA_HOST set to: $OLLAMA_HOST"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Debug info' >> /start.sh && \
    echo 'echo "Current user: $(whoami)"' >> /start.sh && \
    echo 'echo "Ollama location: $(which ollama)"' >> /start.sh && \
    echo 'echo "Working directory: $(pwd)"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo 'echo "========================================"' >> /start.sh && \
    echo 'echo "Starting Ollama server..."' >> /start.sh && \
    echo 'echo "========================================"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Start Ollama in foreground' >> /start.sh && \
    echo 'exec ollama serve' >> /start.sh

# Make script executable
RUN chmod +x /start.sh

# Simple entrypoint
CMD ["/start.sh"]