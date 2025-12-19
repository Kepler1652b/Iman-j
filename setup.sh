#!/usr/bin/env bash
set -e

# -----------------------------
# Configuration
# -----------------------------
PORT=8090
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REAL_USER="${SUDO_USER:-$USER}"
REAL_HOME="$(getent passwd "$REAL_USER" | cut -d: -f6)"
PIPX_BIN="$REAL_HOME/.local/bin"

echo "🚀 Starting setup..."
echo "📂 Project directory: $PROJECT_DIR"
echo "👤 Running as user: $REAL_USER"

# -----------------------------
# Ensure pipx is installed
# -----------------------------
export PATH="$PIPX_BIN:$PATH"

if ! command -v pipx >/dev/null 2>&1; then
    echo "📦 Installing pipx..."
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    export PATH="$PIPX_BIN:$PATH"
fi

# -----------------------------
# Install required Python packages via pipx
# -----------------------------
install_pipx_pkg() {
    local pkg=$1
    if ! command -v "$pkg" >/dev/null 2>&1; then
        echo "📦 Installing $pkg via pipx..."
        pipx install --force "$pkg"
    else
        echo "✅ $pkg already installed"
    fi
}

install_pipx_pkg uv
install_pipx_pkg uvicorn
install_pipx_pkg fastapi

UV_PATH="$(command -v uv)"
echo "✅ uv found at: $UV_PATH"

# -----------------------------
# Generate systemd service function
# -----------------------------
generate_service() {
    local name="$1"
    local exec_cmd="$2"
    local description="$3"

    echo "🧩 Generating $name.service..."

    sudo tee "/etc/systemd/system/$name.service" > /dev/null <<EOF
[Unit]
Description=$description
After=network.target

[Service]
Type=simple
User=$REAL_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$exec_cmd
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$name

[Install]
WantedBy=multi-user.target
EOF
}

# -----------------------------
# Create Bot service
# -----------------------------
generate_service "bot" "$UV_PATH run -- python main.py" "Telegram Bot"

# -----------------------------
# Create FastAPI service
# -----------------------------
generate_service "fastapi" "$UV_PATH run -- uvicorn api.app:app --host 0.0.0.0 --port $PORT" "FastAPI Application"

echo "✅ Services generated successfully"

# -----------------------------
# Enable & start services
# -----------------------------
sudo systemctl daemon-reload
sudo systemctl enable --now bot.service fastapi.service

echo "✅ Services enabled and started"
echo "🌐 FastAPI URL: http://localhost:$PORT"
echo "📝 Check logs with: sudo journalctl -u bot -f"
echo "              or: sudo journalctl -u fastapi -f"
