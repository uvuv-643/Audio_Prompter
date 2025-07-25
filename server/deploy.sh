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
pip install websockets==12.0

echo "Copying server files..."
cat > server.py << 'EOF'
import asyncio
import websockets
import json
import signal
import sys
from datetime import datetime
from typing import Set, Dict, Any
import logging

class ScreenshotServer:
    def __init__(self, host='0.0.0.0', port=8765, interval_seconds=15):
        self.host = host
        self.port = port
        self.interval_seconds = interval_seconds
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None
        self.scheduler_task = None
        self.is_running = False
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        self.clients.add(websocket)
        self.logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            await websocket.send(json.dumps({
                'type': 'connection_established',
                'interval': self.interval_seconds,
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
            return
        
        message = {
            'type': 'execute_screenshot',
            'timestamp': datetime.now().isoformat(),
            'command_id': f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        message_json = json.dumps(message)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                await client.send(message_json)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                self.logger.error(f"Error sending to client: {e}")
                disconnected_clients.add(client)
        
        for client in disconnected_clients:
            self.clients.discard(client)
        
        if disconnected_clients:
            self.logger.info(f"Removed {len(disconnected_clients)} disconnected clients")
    
    async def scheduler_loop(self):
        while self.is_running:
            await asyncio.sleep(self.interval_seconds)
            if self.is_running:
                await self.broadcast_screenshot_command()
    
    async def start(self):
        self.is_running = True
        self.server = await websockets.serve(
            self.register_client,
            self.host,
            self.port
        )
        
        self.scheduler_task = asyncio.create_task(self.scheduler_loop())
        
        self.logger.info(f"Screenshot server started on {self.host}:{self.port}")
        self.logger.info(f"Broadcasting screenshot commands every {self.interval_seconds} seconds")
        
        await self.server.wait_closed()
    
    async def stop(self):
        self.is_running = False
        
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
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
    server = ScreenshotServer()
    
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

echo "Enabling and starting service..."
systemctl daemon-reload
systemctl enable screenshot-server
systemctl start screenshot-server

echo "Installation completed!"
echo "Server is running on port 8765"
echo ""
echo "Useful commands:"
echo "  Check status: systemctl status screenshot-server"
echo "  View logs: journalctl -u screenshot-server -f"
echo "  Stop server: systemctl stop screenshot-server"
echo "  Restart server: systemctl restart screenshot-server"
echo ""
echo "Clients can connect to: $(hostname -I | awk '{print $1}'):8765" 