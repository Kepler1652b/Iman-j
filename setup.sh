#!/usr/bin/env bash
set -e

# -----------------------------
# Configuration
# -----------------------------
PORT=8090
API_KEY="MY_SECRET_KEY"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FASTAPI_SERVICE="fastapi"
BOT_SERVICE="bot"

echo "🚀 Starting full server setup..."
echo "📂 Project directory: $PROJECT_DIR"

# -----------------------------
# Detect or install UV
# -----------------------------
echo "🔍 Checking for uv..."
UV_PATH=$(command -v uv 2>/dev/null || echo "")

if [ -z "$UV_PATH" ]; then
    echo "❌ uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
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
# Install Python dependencies
# -----------------------------
echo "📦 Installing Python dependencies..."
"$UV_PATH" sync
"$UV_PATH" add parsivar

# -----------------------------
# Create systemd service files
# -----------------------------
echo "🧩 Creating systemd service files..."

# FastAPI service
cat > /tmp/$FASTAPI_SERVICE.service <<EOF
[Unit]
Description=FastAPI Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$UV_PATH run uvicorn api.app:app --host 127.0.0.1 --port $PORT
Environment="PATH=$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/bin:/usr/bin:/bin"

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=fastapi-app

[Install]
WantedBy=multi-user.target
EOF

# Bot service
cat > /tmp/$BOT_SERVICE.service <<EOF
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

sudo cp /tmp/$FASTAPI_SERVICE.service /tmp/$BOT_SERVICE.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $FASTAPI_SERVICE $BOT_SERVICE
sudo systemctl start $FASTAPI_SERVICE $BOT_SERVICE
rm /tmp/$FASTAPI_SERVICE.service /tmp/$BOT_SERVICE.service

echo "✅ Systemd services installed and started"

# -----------------------------
# Nginx setup (plain text, port 443)
# -----------------------------
echo "🌀 Setting up Nginx reverse proxy (plain HTTP on port 443)..."
if ! command -v nginx >/dev/null 2>&1; then
    echo "📦 Installing Nginx..."
    sudo apt-get update
    sudo apt-get install -y nginx
fi

NGINX_CONF="/etc/nginx/sites-available/api"
sudo tee "$NGINX_CONF" > /dev/null <<EOF
map \$http_x_api_key \$api_allowed {
    default 0;
    "$API_KEY" 1;
}

server {
    listen 443;
    server_name _;

    location / {
        if (\$api_allowed = 0) {
            return 401;
        }

        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Internal-Proxy true;

        proxy_pass http://127.0.0.1:$PORT;
    }
}
EOF

sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
echo "✅ Nginx configured and restarted (plain HTTP on 443)"

# -----------------------------
# Firewall configuration
# -----------------------------
echo "🔐 Configuring UFW firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 443/tcp
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw --force enable
sudo ufw status verbose

# -----------------------------
# Verify services
# -----------------------------
echo ""
echo "🔍 Verifying services..."
sleep 2

echo "📊 FastAPI status:"
sudo systemctl status $FASTAPI_SERVICE --no-pager -n 5 || true

echo ""
echo "📊 Bot status:"
sudo systemctl status $BOT_SERVICE --no-pager -n 5 || true

# -----------------------------
# Done
# -----------------------------
echo ""
echo "================================================================"
echo "✅ Full setup completed successfully!"
echo "================================================================"
echo "📍 Project directory: $PROJECT_DIR"
echo "🔧 UV path: $UV_PATH"
echo "👤 Running as user: $USER"
echo ""
echo "🌐 FastAPI is now behind Nginx on port 443 (plain text)"
echo ""
echo "📝 Useful commands:"
echo "  sudo systemctl status $FASTAPI_SERVICE    # Check FastAPI status"
echo "  sudo systemctl status $BOT_SERVICE        # Check bot status"
echo "  sudo journalctl -u $FASTAPI_SERVICE -f    # View FastAPI logs"
echo "  sudo journalctl -u $BOT_SERVICE -f        # View bot logs"
echo "  sudo systemctl restart $FASTAPI_SERVICE   # Restart FastAPI"
echo "  sudo systemctl restart $BOT_SERVICE       # Restart bot"
echo ""
echo "================================================================"
