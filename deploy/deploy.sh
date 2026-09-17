#!/bin/bash
# Tanzania Problem Finder - Deployment Script
# Run this on a fresh Ubuntu/Debian server

set -e

APP_DIR="/opt/tanzania-problem-finder"
APP_USER="tanzania-finder"

echo "=== Tanzania Problem Finder Deployment ==="

# Create service user
if ! id "$APP_USER" &>/dev/null; then
    sudo useradd --system --shell /bin/false "$APP_USER"
    echo "Created user: $APP_USER"
fi

# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip

# Setup application directory
sudo mkdir -p "$APP_DIR"
sudo cp -r . "$APP_DIR/"
sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# Create virtual environment
sudo -u "$APP_USER" python3 -m venv "$APP_DIR/venv"
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# Create data directory
sudo -u "$APP_USER" mkdir -p "$APP_DIR/data/logs"

# Install systemd service
sudo cp "$APP_DIR/deploy/tanzania-finder.service" /etc/systemd/system/
sudo cp "$APP_DIR/deploy/tanzania-finder.timer" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tanzania-finder.timer

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and fill in your API keys:"
echo "   sudo -u $APP_USER nano $APP_DIR/.env"
echo ""
echo "2. Start the timer:"
echo "   sudo systemctl start tanzania-finder.timer"
echo ""
echo "3. Check status:"
echo "   sudo systemctl status tanzania-finder.timer"
echo "   sudo journalctl -u tanzania-finder -f"
echo ""
echo "4. Test a manual run:"
echo "   sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/run_agent.py"
