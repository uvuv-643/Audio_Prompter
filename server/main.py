#!/usr/bin/env python3

import asyncio
import signal
import sys
import logging
from server import ScreenshotServer

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('screenshot_server.log')
        ]
    )
    return logging.getLogger(__name__)

async def main():
    logger = setup_logging()
    logger.info("Starting Screenshot Server...")
    
    server = ScreenshotServer(host='0.0.0.0', port=8765, enable_telegram=True)
    shutdown_event = asyncio.Event()
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        shutdown_event.set()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start server in background task
        server_task = asyncio.create_task(server.start())
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        logger.info("Shutdown signal received, stopping server...")
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Cancel server task and stop
        if 'server_task' in locals():
            server_task.cancel()
            try:
                await asyncio.wait_for(server_task, timeout=5.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass
        
        await server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main()) 