#!/usr/bin/env bash
set -e

PORT=8090
PROJECT_DIR="."

echo "🚀 Starting setup..."

# -----------------------------
# Go to project directory
# -----------------------------
cd "$PROJECT_DIR" || { echo "❌ Directory $PROJECT_DIR not found"; exit 1; }

# -----------------------------
# Python dependencies
# -----------------------------
echo "📦 Installing Python dependencies..."
uv sync
uv add parsivar

# -----------------------------
# Install systemd services
# -----------------------------
echo "🧩 Installing systemd services..."
sudo cp bot.service fastapi.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable fastapi bot
sudo systemctl start fastapi bot

# -----------------------------
# Firewall configuration
# -----------------------------
echo "🔐 Configuring firewall for port $PORT..."

if command -v ufw >/dev/null 2>&1; then
    echo "✅ UFW detected"
    sudo ufw allow "${PORT}/tcp" || true
    sudo ufw reload || true

elif command -v iptables >/dev/null 2>&1; then
    echo "⚠️ UFW not found, using iptables"

    sudo iptables -C INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null \
        || sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

    sudo iptables -C INPUT -p tcp --dport "${PORT}" -j ACCEPT 2>/dev/null \
        || sudo iptables -A INPUT -p tcp --dport "${PORT}" -j ACCEPT

    # Persist rules
    if command -v netfilter-persistent >/dev/null 2>&1; then
        sudo netfilter-persistent save
    else
        sudo apt-get update
        sudo apt-get install -y iptables-persistent
        sudo netfilter-persistent save
    fi
else
    echo "❌ No supported firewall found (ufw or iptables)"
    exit 1
fi

# -----------------------------
# Done
# -----------------------------
echo "✅ Setup completed successfully!"
echo "🌐 FastAPI should now be accessible on port $PORT"
