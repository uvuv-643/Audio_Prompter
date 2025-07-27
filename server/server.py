import asyncio
import websockets
import json
import signal
import sys
from datetime import datetime
from typing import Set, Dict, Any
import logging
import time
import os

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
        self.requests_log_file = "user_requests.log"
        
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
            telegram_user_id = data.get('telegram_user_id')
            result = data.get('result', {})
            subtitle_text = data.get('subtitle_text')
            russian_text = data.get('russian_text', '')
            timing = data.get('timing', '')
            self.logger.info(f"Screenshot completed by client {client_id}: {result.get('timing', 'N/A')}")
            if telegram_user_id and subtitle_text:
                await self.handle_subtitle_response(telegram_user_id, subtitle_text, russian_text, timing)
        
        elif message_type == 'left_key_completed':
            client_id = data.get('client_id', 'unknown')
            telegram_user_id = data.get('telegram_user_id')
            result = data.get('result', {})
            self.logger.info(f"Left key completed by client {client_id}")
            if telegram_user_id:
                await self.handle_key_response(telegram_user_id, 'left')
        
        elif message_type == 'space_key_completed':
            client_id = data.get('client_id', 'unknown')
            telegram_user_id = data.get('telegram_user_id')
            result = data.get('result', {})
            self.logger.info(f"Space key completed by client {client_id}")
            if telegram_user_id:
                await self.handle_key_response(telegram_user_id, 'space')
        
        elif message_type == 'next_subtitle_completed':
            client_id = data.get('client_id', 'unknown')
            telegram_user_id = data.get('telegram_user_id')
            result = data.get('result', {})
            self.logger.info(f"Next subtitle completed by client {client_id}")
            if telegram_user_id:
                await self.handle_next_subtitle_response(telegram_user_id, result)
        
        elif message_type == 'heartbeat':
            await websocket.send(json.dumps({
                'type': 'heartbeat_ack',
                'timestamp': datetime.now().isoformat()
            }))
    
    async def broadcast_screenshot_command(self, telegram_user_id=None):
        if not self.clients:
            self.logger.warning("No connected clients to send screenshot command to")
            return
        
        message = {
            'type': 'execute_screenshot',
            'timestamp': datetime.now().isoformat(),
            'command_id': f"cmd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'telegram_user_id': telegram_user_id
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
    
    async def broadcast_left_key_command(self, telegram_user_id=None):
        if not self.clients:
            self.logger.warning("No connected clients to send left key command to")
            return
        
        message = {
            'type': 'execute_left_key',
            'timestamp': datetime.now().isoformat(),
            'command_id': f"left_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'telegram_user_id': telegram_user_id
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
        
        self.logger.info(f"Left key command sent to {sent_count} clients")
        return sent_count
    
    async def broadcast_space_key_command(self, telegram_user_id=None):
        if not self.clients:
            self.logger.warning("No connected clients to send space key command to")
            return
        
        message = {
            'type': 'execute_space_key',
            'timestamp': datetime.now().isoformat(),
            'command_id': f"space_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'telegram_user_id': telegram_user_id
        }
    
    async def broadcast_next_subtitle_command(self, telegram_user_id=None):
        if not self.clients:
            self.logger.warning("No connected clients to send next subtitle command to")
            return
        
        message = {
            'type': 'execute_next_subtitle',
            'timestamp': datetime.now().isoformat(),
            'command_id': f"next_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'telegram_user_id': telegram_user_id
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
        
        self.logger.info(f"Space key command sent to {sent_count} clients")
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
    
    async def handle_subtitle_response(self, telegram_user_id, subtitle_text, russian_text="", timing=""):
        self.log_user_request(telegram_user_id, subtitle_text.replace("\n", " "), russian_text.replace("\n", " "), timing)
        if self.telegram_bot:
            await self.telegram_bot.send_subtitle_response(telegram_user_id, subtitle_text)
    
    async def handle_key_response(self, telegram_user_id, key_type):
        if self.telegram_bot:
            await self.telegram_bot.send_key_response(telegram_user_id, key_type)
    
    async def handle_next_subtitle_response(self, telegram_user_id, result):
        new_url = result.get('new_url', '')
        old_url = result.get('old_url', '')
        eng_url = result.get('eng_url', '')
        if self.telegram_bot:
            await self.telegram_bot.send_next_subtitle_response(telegram_user_id, result)
    
    def log_user_request(self, telegram_user_id, request_text, russian_text="", timing=""):
        try:
            if not telegram_user_id or not request_text:
                self.logger.warning(f"Skipping log entry - missing data: user_id={telegram_user_id}, text={request_text}")
                return
            
            if not os.path.exists(self.requests_log_file):
                with open(self.requests_log_file, 'w', encoding='utf-8') as f:
                    f.write("Telegram_ID\tRequest_Text\tRussian_Text\tTiming\n")
            
            log_entry = f"{telegram_user_id}\t{request_text}\t{russian_text}\t{timing}\n"
            
            with open(self.requests_log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            self.logger.info(f"Logged request: User {telegram_user_id} - {request_text}")
        except Exception as e:
            self.logger.error(f"Error logging user request: {e}")

 