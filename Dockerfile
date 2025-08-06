# Ultra-simple Ollama for Railway
FROM ollama/ollama:latest

# Set required environment
ENV OLLAMA_HOST=0.0.0.0:11434

# Expose port for Railway
EXPOSE 11434

# Create a simple entrypoint script inline
RUN echo '#!/bin/bash\n\
echo "Starting Ollama..."\n\
ollama serve &\n\
sleep 5\n\
echo "Ollama started, pulling model in background..."\n\
(ollama pull qwen3:4b &)\n\
echo "Health endpoint should be ready"\n\
wait\n\
' > /entrypoint.sh && chmod +x /entrypoint.sh

# Use the entrypoint
ENTRYPOINT ["/entrypoint.sh"]