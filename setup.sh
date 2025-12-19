
#!/usr/bin/env bash
set -e

PORT=8090
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting setup..."
echo "📂 Project directory: $PROJECT_DIR"

# -----------------------------
# Detect UV path
# -----------------------------
echo "🔍 Detecting uv installation..."
UV_PATH=$(command -v uv 2>/dev/null || echo "")

if [ -z "$UV_PATH" ]; then
    echo "❌ uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Reload shell environment
    export PATH="$HOME/.cargo/bin:$PATH"
    UV_PATH=$(command -v uv 2>/dev/null || echo "$HOME/.cargo/bin/uv")
    
    if [ ! -f "$UV_PATH" ]; then
        UV_PATH="$HOME/.local/bin/uv"
    fi
    
    if [ ! -f "$UV_PATH" ]; then
        echo "❌ Failed to install uv"
        exit 1
    fi
fi

echo "✅ Found uv at: $UV_PATH"

# -----------------------------
# Go to project directory
# -----------------------------
cd "$PROJECT_DIR" || { echo "❌ Directory $PROJECT_DIR not found"; exit 1; }

# -----------------------------
# Python dependencies
# -----------------------------
echo "📦 Installing Python dependencies..."
"$UV_PATH" sync
"$UV_PATH" add parsivar

# -----------------------------
# Generate systemd service files
# -----------------------------
echo "🧩 Generating systemd service files..."

# Create bot.service
cat > /tmp/bot.service <<EOF
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$UV_PATH run main.py
Environment="PATH=$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

[Install]
WantedBy=multi-user.target
EOF

# Create fastapi.service
cat > /tmp/fastapi.service <<EOF
[Unit]
Description=FastAPI Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$UV_PATH run uvicorn api.app:app --host 0.0.0.0 --port $PORT
Environment="PATH=$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=fastapi-app

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service files generated"

# -----------------------------
# Install systemd services
# -----------------------------
echo "🔧 Installing systemd services..."
sudo cp /tmp/bot.service /tmp/fastapi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fastapi bot
sudo systemctl start fastapi bot

# Clean up temp files
rm /tmp/bot.service /tmp/fastapi.service

# -----------------------------
# Firewall configuration
# -----------------------------
echo "🔐 Configuring firewall for port $PORT..."

if command -v ufw >/dev/null 2>&1; then
    echo "✅ UFW detected"
    sudo ufw allow "${PORT}/tcp" || true
    sudo ufw reload || true
elif command -v iptables >/dev/null 2>&1; then
    echo "⚠️  UFW not found, using iptables"
    sudo iptables -C INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT 2>/dev/null \
        || sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    sudo iptables -C INPUT -p tcp --dport "${PORT}" -j ACCEPT 2>/dev/null \
        || sudo iptables -A INPUT -p tcp --dport "${PORT}" -j ACCEPT
    
    # Persist rules
    if command -v netfilter-persistent >/dev/null 2>&1; then
        sudo netfilter-persistent save
    elif [ -f /etc/debian_version ]; then
        sudo apt-get update
        sudo apt-get install -y iptables-persistent
        sudo netfilter-persistent save
    elif [ -f /etc/redhat-release ]; then
        sudo service iptables save
    else
        echo "⚠️  Please manually save iptables rules"
    fi
else
    echo "❌ No supported firewall found (ufw or iptables)"
    exit 1
fi

# -----------------------------
# Verify services
# -----------------------------
echo ""
echo "🔍 Verifying services..."
sleep 2

echo ""
echo "📊 FastAPI status:"
sudo systemctl status fastapi --no-pager -n 5 || true

echo ""
echo "📊 Bot status:"
sudo systemctl status bot --no-pager -n 5 || true

# -----------------------------
# Done
# -----------------------------
echo ""
echo "================================================================"
echo "✅ Setup completed successfully!"
echo "================================================================"
echo ""
echo "📍 Project directory: $PROJECT_DIR"
echo "🔧 UV path: $UV_PATH"
echo "👤 Running as user: $USER"
echo ""
echo "🌐 FastAPI: http://localhost:$PORT"
echo ""
echo "📝 Useful commands:"
echo "  sudo systemctl status fastapi    # Check FastAPI status"
echo "  sudo systemctl status bot        # Check bot status"
echo "  sudo journalctl -u fastapi -f    # View FastAPI logs"
echo "  sudo journalctl -u bot -f        # View bot logs"
echo "  sudo systemctl restart fastapi   # Restart FastAPI"
echo "  sudo systemctl restart bot       # Restart bot"
echo ""
echo "================================================================"