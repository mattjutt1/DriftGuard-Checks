#!/bin/bash
# Simple local documentation server

echo "📚 Starting local documentation server..."

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo "🌐 Documentation available at: http://localhost:8081"
    echo "🛑 Press Ctrl+C to stop"
    cd docs && python3 -m http.server 8081
elif command -v python &> /dev/null; then
    echo "🌐 Documentation available at: http://localhost:8081" 
    echo "🛑 Press Ctrl+C to stop"
    cd docs && python -m SimpleHTTPServer 8081
else
    echo "❌ Python not found. Cannot start documentation server."
    exit 1
fi