#!/bin/bash

set -e

echo "Installing Screenshot Server..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Warning: Running as root. Consider running as regular user."
fi

# Install system dependencies
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
elif command -v yum &> /dev/null; then
    sudo yum install -y python3 python3-pip
else
    echo "Package manager not found. Please install python3 and python3-pip manually."
fi

# Use current directory
echo "Installing in current directory: $(pwd)"

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install websockets==12.0 python-telegram-bot==20.7 python-dotenv==1.0.0

echo "Creating .env file..."
cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8765
EOF

echo "Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Set your TELEGRAM_BOT_TOKEN"
echo "3. Run server: source venv/bin/activate && python main.py"
echo ""
echo "Server will be available on port 8765" 