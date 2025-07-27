import asyncio
import websockets
import json
import signal
import sys
import uuid
import logging
from datetime import datetime
from screenshot_workflow import ScreenshotWorkflow

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class ScreenshotClient:
    def __init__(self, server_host='localhost', server_port=8765, vtt_url=None, enable_tts=True):
        self.server_host = server_host
        self.server_port = server_port
        self.websocket = None
        self.client_id = str(uuid.uuid4())[:8]
        self.workflow = ScreenshotWorkflow(vtt_url=vtt_url, enable_tts=enable_tts)
        self.is_running = False
        self.reconnect_delay = 5
        self.max_reconnect_delay = 60
    
    async def connect_to_server(self):
        uri = f"ws://{self.server_host}:{self.server_port}"
        
        while self.is_running:
            try:
                logger.info(f"Connecting to server: {uri}")
                self.websocket = await websockets.connect(uri)
                logger.info(f"Successfully connected to server")
                await self.handle_connection()
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection to server closed")
            except Exception as e:
                logger.error(f"Connection error: {e}")
            
            if self.is_running:
                logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
    
    async def handle_connection(self):
        self.reconnect_delay = 5
        logger.info("Connection established, waiting for server messages...")
        
        async for message in self.websocket:
            try:
                data = json.loads(message)
                logger.debug(f"Received message from server: {data.get('type', 'unknown')}")
                await self.handle_server_message(data)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {message[:100]}...")
                continue
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                break
    
    async def handle_server_message(self, data):
        message_type = data.get('type')
        
        if message_type == 'connection_established':
            logger.info(f"Connection established with server. Ready for manual screenshot commands.")
        
        elif message_type == 'execute_screenshot':
            command_id = data.get('command_id', 'unknown')
            telegram_user_id = data.get('telegram_user_id')
            logger.info(f"Executing screenshot command: {command_id}")
            await self.execute_screenshot_command(command_id, telegram_user_id)
        
        elif message_type == 'execute_left_key':
            command_id = data.get('command_id', 'unknown')
            telegram_user_id = data.get('telegram_user_id')
            logger.info(f"Executing left key command: {command_id}")
            await self.execute_left_key_command(command_id, telegram_user_id)
        
        elif message_type == 'execute_space_key':
            command_id = data.get('command_id', 'unknown')
            telegram_user_id = data.get('telegram_user_id')
            logger.info(f"Executing space key command: {command_id}")
            await self.execute_space_key_command(command_id, telegram_user_id)
        
        elif message_type == 'heartbeat_ack':
            logger.debug("Heartbeat acknowledged by server")
        
        else:
            logger.warning(f"Unknown message type received: {message_type}")
    
    async def execute_screenshot_command(self, command_id, telegram_user_id=None):
        try:
            logger.info(f"Starting screenshot workflow for command: {command_id}")
            result = self.workflow.execute_screenshot_workflow()
            
            timing = result.get('timing')
            if timing:
                logger.info(f"Screenshot completed. Timing detected: {timing}")
            else:
                logger.warning("Screenshot completed but no timing detected")
            
            subtitle_text = result.get('subtitle_text', '')
            
            response = {
                'type': 'screenshot_completed',
                'client_id': self.client_id,
                'command_id': command_id,
                'telegram_user_id': telegram_user_id,
                'timestamp': datetime.now().isoformat(),
                'subtitle_text': subtitle_text,
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
                logger.info(f"Sent completion response to server for command: {command_id}")
        
        except Exception as e:
            logger.error(f"Error executing screenshot: {e}")
            error_response = {
                'type': 'screenshot_error',
                'client_id': self.client_id,
                'command_id': command_id,
                'telegram_user_id': telegram_user_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(error_response))
                logger.info(f"Sent error response to server for command: {command_id}")
    
    async def execute_left_key_command(self, command_id, telegram_user_id=None):
        try:
            from mouse_controller import MouseController
            controller = MouseController()
            mouse_position = controller.press_left_key()
            
            response = {
                'type': 'left_key_completed',
                'client_id': self.client_id,
                'command_id': command_id,
                'telegram_user_id': telegram_user_id,
                'timestamp': datetime.now().isoformat(),
                'result': {
                    'mouse_position': {
                        'x': mouse_position.x,
                        'y': mouse_position.y
                    }
                }
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(response))
                logger.info(f"Sent left key completion response to server for command: {command_id}")
        
        except Exception as e:
            logger.error(f"Error executing left key: {e}")
            error_response = {
                'type': 'left_key_error',
                'client_id': self.client_id,
                'command_id': command_id,
                'telegram_user_id': telegram_user_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(error_response))
                logger.info(f"Sent left key error response to server for command: {command_id}")
    
    async def execute_space_key_command(self, command_id, telegram_user_id=None):
        try:
            from mouse_controller import MouseController
            controller = MouseController()
            mouse_position = controller.press_space_key()
            
            response = {
                'type': 'space_key_completed',
                'client_id': self.client_id,
                'command_id': command_id,
                'telegram_user_id': telegram_user_id,
                'timestamp': datetime.now().isoformat(),
                'result': {
                    'mouse_position': {
                        'x': mouse_position.x,
                        'y': mouse_position.y
                    }
                }
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(response))
                logger.info(f"Sent space key completion response to server for command: {command_id}")
        
        except Exception as e:
            logger.error(f"Error executing space key: {e}")
            error_response = {
                'type': 'space_key_error',
                'client_id': self.client_id,
                'command_id': command_id,
                'telegram_user_id': telegram_user_id,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
            if self.websocket:
                await self.websocket.send(json.dumps(error_response))
                logger.info(f"Sent space key error response to server for command: {command_id}")
    
    async def send_heartbeat(self):
        while self.is_running and self.websocket:
            try:
                heartbeat = {
                    'type': 'heartbeat',
                    'client_id': self.client_id,
                    'timestamp': datetime.now().isoformat()
                }
                await self.websocket.send(json.dumps(heartbeat))
                logger.debug("Sent heartbeat to server")
                await asyncio.sleep(30)
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
                break
    
    async def start(self):
        self.is_running = True
        logger.info(f"Starting screenshot client (ID: {self.client_id})")
        logger.info(f"Connecting to server: {self.server_host}:{self.server_port}")
        
        heartbeat_task = asyncio.create_task(self.send_heartbeat())
        connection_task = asyncio.create_task(self.connect_to_server())
        
        try:
            await asyncio.gather(heartbeat_task, connection_task)
        except asyncio.CancelledError:
            logger.info("Client tasks cancelled")
    
    async def stop(self):
        self.is_running = False
        logger.info("Stopping screenshot client...")
        
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket connection closed")

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Screenshot Client with TTS')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8765, help='Server port')
    parser.add_argument('--vtt-url', help='URL to VTT subtitles file')
    parser.add_argument('--no-tts', action='store_true', help='Disable TTS functionality')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")
    
    client = ScreenshotClient(args.host, args.port, args.vtt_url, enable_tts=not args.no_tts)
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        asyncio.create_task(client.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await client.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main()) 