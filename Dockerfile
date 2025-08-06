# Railway Ollama - Debug Version
FROM ollama/ollama:latest

# Install debugging tools
RUN apt-get update && apt-get install -y \
    curl \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Create startup script with maximum debugging
RUN cat > /start.sh << 'EOF'
#!/bin/sh
set -x  # Enable command tracing

echo "=== RAILWAY OLLAMA DEBUG ==="
echo "Date: $(date)"
echo "PORT from Railway: ${PORT}"
echo "Current directory: $(pwd)"
echo "Current user: $(whoami)"

# Check if ollama exists
if command -v ollama >/dev/null 2>&1; then
    echo "✓ Ollama found at: $(which ollama)"
else
    echo "✗ Ollama NOT FOUND!"
    exit 1
fi

# Set the host binding
export OLLAMA_HOST="0.0.0.0:${PORT:-11434}"
echo "OLLAMA_HOST configured as: ${OLLAMA_HOST}"

# Start Ollama
echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!
echo "Ollama started with PID: ${OLLAMA_PID}"

# Give it time to start
sleep 10

# Check if process is still running
if ps -p ${OLLAMA_PID} > /dev/null; then
    echo "✓ Ollama process is running"
else
    echo "✗ Ollama process died!"
    exit 1
fi

# Check listening ports
echo "=== LISTENING PORTS ==="
netstat -tlnp 2>/dev/null || ss -tln

# Test the API
echo "=== TESTING API ==="
curl -v "http://localhost:${PORT:-11434}/api/tags" || echo "API test failed"

# Keep the container running
echo "=== Container ready, waiting... ==="
wait ${OLLAMA_PID}
EOF

RUN chmod +x /start.sh

CMD ["/start.sh"]