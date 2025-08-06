# Railway Ollama - Debug Version Fixed
FROM ollama/ollama:latest

# Install debugging tools
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create startup script using echo commands (more compatible)
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'set -x' >> /start.sh && \
    echo '' >> /start.sh && \
    echo 'echo "=== RAILWAY OLLAMA DEBUG ==="' >> /start.sh && \
    echo 'echo "Date: $(date)"' >> /start.sh && \
    echo 'echo "PORT from Railway: ${PORT}"' >> /start.sh && \
    echo 'echo "Current directory: $(pwd)"' >> /start.sh && \
    echo 'echo "Current user: $(whoami)"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Check if ollama exists' >> /start.sh && \
    echo 'if command -v ollama >/dev/null 2>&1; then' >> /start.sh && \
    echo '    echo "✓ Ollama found at: $(which ollama)"' >> /start.sh && \
    echo 'else' >> /start.sh && \
    echo '    echo "✗ Ollama NOT FOUND!"' >> /start.sh && \
    echo '    exit 1' >> /start.sh && \
    echo 'fi' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Set the host binding' >> /start.sh && \
    echo 'export OLLAMA_HOST="0.0.0.0:${PORT:-11434}"' >> /start.sh && \
    echo 'echo "OLLAMA_HOST configured as: ${OLLAMA_HOST}"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Start Ollama' >> /start.sh && \
    echo 'echo "Starting Ollama server..."' >> /start.sh && \
    echo 'ollama serve &' >> /start.sh && \
    echo 'OLLAMA_PID=$!' >> /start.sh && \
    echo 'echo "Ollama started with PID: ${OLLAMA_PID}"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Give it time to start' >> /start.sh && \
    echo 'sleep 10' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Check if process is still running' >> /start.sh && \
    echo 'if ps -p ${OLLAMA_PID} > /dev/null; then' >> /start.sh && \
    echo '    echo "✓ Ollama process is running"' >> /start.sh && \
    echo 'else' >> /start.sh && \
    echo '    echo "✗ Ollama process died!"' >> /start.sh && \
    echo '    exit 1' >> /start.sh && \
    echo 'fi' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Check listening ports' >> /start.sh && \
    echo 'echo "=== LISTENING PORTS ==="' >> /start.sh && \
    echo 'netstat -tlnp 2>/dev/null || ss -tln' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Test the API' >> /start.sh && \
    echo 'echo "=== TESTING API ==="' >> /start.sh && \
    echo 'curl -v "http://localhost:${PORT:-11434}/api/tags" || echo "API test failed"' >> /start.sh && \
    echo '' >> /start.sh && \
    echo '# Keep the container running' >> /start.sh && \
    echo 'echo "=== Container ready, waiting... ==="' >> /start.sh && \
    echo 'wait ${OLLAMA_PID}' >> /start.sh

# Make the script executable
RUN chmod +x /start.sh

# Run the script
CMD ["/start.sh"]