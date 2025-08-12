#!/bin/bash

# Test script for Railway Ollama deployment
RAILWAY_URL="${1:-https://prompt-wizard-production.up.railway.app}"

echo "Testing Ollama deployment at: $RAILWAY_URL"
echo "========================================"

# Test 1: Basic connectivity
echo "1. Testing basic connectivity..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" "$RAILWAY_URL"

# Test 2: Health endpoint
echo ""
echo "2. Testing /api/tags endpoint..."
curl -s "$RAILWAY_URL/api/tags" | head -n 5

# Test 3: Check if Ollama is responding
echo ""
echo "3. Testing Ollama version..."
curl -s "$RAILWAY_URL/api/version"

# Test 4: List models
echo ""
echo "4. Listing available models..."
curl -s "$RAILWAY_URL/api/tags" | jq -r '.models[].name' 2>/dev/null || echo "No models found or jq not installed"

echo ""
echo "========================================"
echo "If you see HTTP 200 and JSON responses, Ollama is working!"
