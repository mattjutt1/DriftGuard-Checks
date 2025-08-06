#!/bin/bash

# Deploy Ollama + Qwen3:4b to External Server
# This script sets up Ollama on a cloud VPS for Convex integration

set -e

echo "🚀 PromptEvolver External Ollama Deployment Script"
echo "=================================================="

# Configuration
OLLAMA_VERSION="0.1.26"
MODEL_NAME="qwen3:4b"
SERVER_PORT="11434"
INSTALL_DIR="/opt/ollama"

echo "📋 Deployment Configuration:"
echo "   - Ollama Version: $OLLAMA_VERSION"
echo "   - Model: $MODEL_NAME"  
echo "   - Port: $SERVER_PORT"
echo "   - Install Directory: $INSTALL_DIR"
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y curl wget unzip systemd

# Create ollama user
echo "👤 Creating ollama system user..."
if ! id "ollama" &>/dev/null; then
    useradd -r -s /bin/false -d /opt/ollama -m ollama
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p $INSTALL_DIR
chown ollama:ollama $INSTALL_DIR

# Download and install Ollama
echo "⬇️ Downloading Ollama..."
cd $INSTALL_DIR
wget -q https://github.com/ollama/ollama/releases/download/v$OLLAMA_VERSION/ollama-linux-amd64 -O ollama
chmod +x ollama
chown ollama:ollama ollama

# Create systemd service
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/ollama.service << EOF
[Unit]
Description=Ollama Server
After=network-online.target

[Service]
ExecStart=$INSTALL_DIR/ollama serve
User=ollama
Group=ollama
Restart=always
RestartSec=3
Environment="OLLAMA_HOST=0.0.0.0:$SERVER_PORT"
Environment="OLLAMA_MODELS=/opt/ollama/models"

[Install]
WantedBy=default.target
EOF

# Create models directory
echo "📁 Creating models directory..."
mkdir -p /opt/ollama/models
chown -R ollama:ollama /opt/ollama/models

# Enable and start service
echo "🔄 Enabling and starting Ollama service..."
systemctl daemon-reload
systemctl enable ollama
systemctl start ollama

# Wait for service to start
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if service is running
if systemctl is-active --quiet ollama; then
    echo "✅ Ollama service started successfully"
else
    echo "❌ Failed to start Ollama service"
    systemctl status ollama
    exit 1
fi

# Pull the Qwen3:4b model
echo "⬇️ Pulling $MODEL_NAME model (this may take several minutes)..."
sudo -u ollama OLLAMA_HOST=0.0.0.0:$SERVER_PORT $INSTALL_DIR/ollama pull $MODEL_NAME

# Test the installation
echo "🧪 Testing Ollama installation..."
sleep 2
if curl -s http://localhost:$SERVER_PORT/api/tags | grep -q "qwen3"; then
    echo "✅ Ollama and $MODEL_NAME model installed successfully!"
else
    echo "❌ Installation test failed"
    exit 1
fi

# Configure firewall (if UFW is available)
if command -v ufw &> /dev/null; then
    echo "🔥 Configuring firewall..."
    ufw allow $SERVER_PORT/tcp
    echo "✅ Firewall configured to allow port $SERVER_PORT"
fi

# Display final information
echo
echo "🎉 External Ollama Deployment Complete!"
echo "========================================"
echo "   - Service Status: $(systemctl is-active ollama)"
echo "   - Port: $SERVER_PORT"
echo "   - Model: $MODEL_NAME"
echo "   - Test URL: http://YOUR_SERVER_IP:$SERVER_PORT/api/tags"
echo
echo "📋 Next Steps:"
echo "   1. Note your server's public IP address"
echo "   2. Update OLLAMA_SERVER_URL in your Convex environment"
echo "   3. Test the integration with: curl http://YOUR_IP:$SERVER_PORT/api/tags"
echo
echo "🔧 Service Management Commands:"
echo "   - Status: systemctl status ollama"
echo "   - Restart: systemctl restart ollama"
echo "   - Logs: journalctl -u ollama -f"
echo