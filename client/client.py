import asyncio
import websockets
import json
import signal
import sys
import uuid
from datetime import datetime
from screenshot_workflow import ScreenshotWorkflow

class ScreenshotClient:
    def __init__(self, server_host='localhost', server_port=8765):
        self.server_host = server_host
        self.server_port = server_port
        self.websocket = None
        self.client_id = str(uuid.uuid4())[:8]
        self.workflow = ScreenshotWorkflow()
        self.is_running = False
        self.reconnect_delay = 5
        self.max_reconnect_delay = 60
    
    async def connect_to_server(self):
        uri = f"ws://{self.server_host}:{self.server_port}"
        
        while self.is_running:
            try:
                self.websocket = await websockets.connect(uri)
                await self.handle_connection()
            except websockets.exceptions.ConnectionClosed:
                pass
            except Exception as e:
                pass
            
            if self.is_running:
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
    
    async def handle_connection(self):
        self.reconnect_delay = 5
        
        async for message in self.websocket:
            try:
                data = json.loads(message)
                await self.handle_server_message(data)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                break
    
    async def handle_server_message(self, data):
        message_type = data.get('type')
        
        if message_type == 'connection_established':
            interval = data.get('interval', 15)
        
        elif message_type == 'execute_screenshot':
            command_id = data.get('command_id', 'unknown')
            await self.execute_screenshot_command(command_id)
        
        elif message_type == 'heartbeat_ack':
            pass
    
    async def execute_screenshot_command(self, command_id):
        try:
            result = self.workflow.execute_screenshot_workflow()
            
            response = {
                'type': 'screenshot_completed',
                'client_id': self.client_id,
                'command_id': command_id,
                'timestamp': datetime.now().isoformat(),
                'result': {
                    'timing': result.get('timing'),
                    'mouse_position': {
                        'x': result.get('mouse_position', {}).x if result.get('mouse_position') else None,
                        'y': result.get('mouse_position', {}).y if result.get('mouse_position') else None
                    },
                    'saved_filepath': result.get('saved_filepath'),
                    'crop_size': result.get('crop_size')
                }
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(response))
        
        except Exception as e:
            error_response = {
                'type': 'screenshot_error',
                'client_id': self.client_id,
                'command_id': command_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(error_response))
    
    async def send_heartbeat(self):
        while self.is_running and self.websocket:
            try:
                heartbeat = {
                    'type': 'heartbeat',
                    'client_id': self.client_id,
                    'timestamp': datetime.now().isoformat()
                }
                await self.websocket.send(json.dumps(heartbeat))
                await asyncio.sleep(30)
            except:
                break
    
    async def start(self):
        self.is_running = True
        
        heartbeat_task = asyncio.create_task(self.send_heartbeat())
        connection_task = asyncio.create_task(self.connect_to_server())
        
        try:
            await asyncio.gather(heartbeat_task, connection_task)
        except asyncio.CancelledError:
            pass
    
    async def stop(self):
        self.is_running = False
        
        if self.websocket:
            await self.websocket.close()

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Screenshot Client')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8765, help='Server port')
    
    args = parser.parse_args()
    
    client = ScreenshotClient(args.host, args.port)
    
    def signal_handler(sig, frame):
        asyncio.create_task(client.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await client.start()
    except KeyboardInterrupt:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main()) 