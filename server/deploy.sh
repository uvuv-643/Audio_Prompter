#!/bin/bash

set -e

echo "Installing Screenshot Server..."

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

apt update
apt install -y python3 python3-pip python3-venv

cd /opt
mkdir -p screenshot-server
cd screenshot-server

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install websockets==12.0 python-telegram-bot==20.7 python-dotenv==1.0.0

echo "Copying server files..."
cat > telegram_bot.py << 'EOF'
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ScreenshotTelegramBot:
    def __init__(self, screenshot_server):
        self.screenshot_server = screenshot_server
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.application = None
        
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("📸 Take Screenshot", callback_data='take_screenshot')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎬 Screenshot Control Bot\n\n"
            "Press the button below to take a screenshot:",
            reply_markup=reply_markup
        )
    
    async def pause_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.take_screenshot(update, context)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        if query.data == 'take_screenshot':
            await self.take_screenshot(update, context)
    
    async def take_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            await self.screenshot_server.broadcast_screenshot_command()
            
            message = "📸 Screenshot command sent to all connected clients!"
            if hasattr(update, 'callback_query'):
                await update.callback_query.edit_message_text(message)
            else:
                await update.message.reply_text(message)
            
            logger.info(f"Screenshot command sent via Telegram by user {update.effective_user.id}")
        
        except Exception as e:
            error_msg = f"❌ Error sending screenshot command: {str(e)}"
            if hasattr(update, 'callback_query'):
                await update.callback_query.edit_message_text(error_msg)
            else:
                await update.message.reply_text(error_msg)
            logger.error(f"Telegram bot error: {e}")
    
    async def start(self):
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return
        
        self.application = Application.builder().token(self.bot_token).build()
        
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("pause", self.pause_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("Starting Telegram bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        logger.info("Telegram bot started successfully")
    
    async def stop(self):
        if self.application:
            logger.info("Stopping Telegram bot...")
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram bot stopped")
EOF

cat > server.py << 'EOF'
import asyncio
import websockets
import json
import signal
import sys
from datetime import datetime
from typing import Set, Dict, Any
import logging
import time

class ScreenshotServer:
    def __init__(self, host='0.0.0.0', port=8765, enable_telegram=True):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.telegram_bot = None
        self.telegram_task = None
        self.is_running = False
        self.start_time = time.time()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        if enable_telegram:
            try:
                from telegram_bot import ScreenshotTelegramBot
                self.telegram_bot = ScreenshotTelegramBot(self)
                self.logger.info("Telegram bot integration enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Telegram bot: {e}")
                self.telegram_bot = None
    
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        self.clients.add(websocket)
        self.logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            await websocket.send(json.dumps({
                'type': 'connection_established',
                'timestamp': datetime.now().isoformat()
            }))
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    continue
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            self.logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
    
    async def handle_client_message(self, websocket: websockets.WebSocketServerProtocol, data: Dict[str, Any]):
        message_type = data.get('type')
        
        if message_type == 'screenshot_completed':
            client_id = data.get('client_id', 'unknown')
            result = data.get('result', {})
            self.logger.info(f"Screenshot completed by client {client_id}: {result.get('timing', 'N/A')}")
        
        elif message_type == 'heartbeat':
            await websocket.send(json.dumps({
                'type': 'heartbeat_ack',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def broadcast_screenshot_command(self):
        if not self.clients:
            self.logger.warning("No connected clients to send screenshot command to")
            return
        
        message = {
            'type': 'execute_screenshot',
            'timestamp': datetime.now().isoformat(),
            'command_id': f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        message_json = json.dumps(message)
        disconnected_clients = set()
        sent_count = 0
        
        for client in self.clients:
            try:
                await client.send(message_json)
                sent_count += 1
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                self.logger.error(f"Error sending to client: {e}")
                disconnected_clients.add(client)
        
        for client in disconnected_clients:
            self.clients.discard(client)
        
        if disconnected_clients:
            self.logger.info(f"Removed {len(disconnected_clients)} disconnected clients")
        
        self.logger.info(f"Screenshot command sent to {sent_count} clients")
        return sent_count
    
    def get_uptime(self):
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    async def restart(self):
        self.logger.info("Server restart requested")
        await self.stop()
        await asyncio.sleep(2)
        await self.start()
    
    async def start(self):
        self.is_running = True
        
        self.server = await websockets.serve(
            self.register_client,
            self.host,
            self.port
        )
        
        self.logger.info(f"Screenshot server started on {self.host}:{self.port}")
        
        if self.telegram_bot:
            self.telegram_task = asyncio.create_task(self.telegram_bot.start())
            self.logger.info("Telegram bot started")
        
        try:
            await self.server.wait_closed()
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        self.is_running = False
        
        if self.telegram_task:
            self.telegram_task.cancel()
            try:
                await self.telegram_task
            except asyncio.CancelledError:
                pass
        
        if self.telegram_bot:
            await self.telegram_bot.stop()
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        for client in list(self.clients):
            try:
                await client.close()
            except:
                pass
        
        self.clients.clear()
        self.logger.info("Server stopped")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Screenshot Server')
    parser.add_argument('--no-telegram', action='store_true', help='Disable Telegram bot')
    
    args = parser.parse_args()
    
    server = ScreenshotServer(enable_telegram=not args.no_telegram)
    
    def signal_handler(sig, frame):
        asyncio.create_task(server.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
EOF

echo "Creating systemd service..."
cat > /etc/systemd/system/screenshot-server.service << EOF
[Unit]
Description=Screenshot Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/screenshot-server
ExecStart=/opt/screenshot-server/venv/bin/python /opt/screenshot-server/server.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "Creating .env file..."
cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8765
EOF

echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable screenshot-server
systemctl start screenshot-server

echo "Installation completed!"
echo "Server is running on port 8765"
echo ""
echo "IMPORTANT: Configure your Telegram bot:"
echo "1. Edit /opt/screenshot-server/.env file"
echo "2. Set your TELEGRAM_BOT_TOKEN"
echo "3. Restart service: systemctl restart screenshot-server"
echo ""
echo "Useful commands:"
echo "  Check status: systemctl status screenshot-server"
echo "  View logs: journalctl -u screenshot-server -f"
echo "  Stop server: systemctl stop screenshot-server"
echo "  Restart server: systemctl restart screenshot-server"
echo ""
echo "Clients can connect to: $(hostname -I | awk '{print $1}'):8765" 