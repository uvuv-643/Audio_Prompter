import asyncio
import websockets
import json
import uuid
from datetime import datetime

class TestClient:
    def __init__(self, server_host='localhost', server_port=8765):
        self.server_host = server_host
        self.server_port = server_port
        self.client_id = str(uuid.uuid4())[:8]
        self.websocket = None
    
    async def connect_and_test(self):
        uri = f"ws://{self.server_host}:{self.server_port}"
        
        try:
            self.websocket = await websockets.connect(uri)
            print(f"Connected to server {uri}")
            
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type')
                    
                    if message_type == 'connection_established':
                        print(f"Connection established. Interval: {data.get('interval')}s")
                    
                    elif message_type == 'execute_screenshot':
                        command_id = data.get('command_id')
                        print(f"Received screenshot command: {command_id}")
                        
                        response = {
                            'type': 'screenshot_completed',
                            'client_id': self.client_id,
                            'command_id': command_id,
                            'timestamp': datetime.now().isoformat(),
                            'result': {
                                'timing': '00:15:30',
                                'mouse_position': {'x': 100, 'y': 200},
                                'saved_filepath': '/test/screenshot.png',
                                'crop_size': 100
                            }
                        }
                        
                        await self.websocket.send(json.dumps(response))
                        print(f"Sent completion response for command: {command_id}")
                    
                    elif message_type == 'heartbeat_ack':
                        print("Heartbeat acknowledged")
                
                except json.JSONDecodeError:
                    print(f"Invalid JSON received: {message}")
        
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Screenshot Client')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8765, help='Server port')
    
    args = parser.parse_args()
    
    client = TestClient(args.host, args.port)
    await client.connect_and_test()

if __name__ == "__main__":
    asyncio.run(main()) 