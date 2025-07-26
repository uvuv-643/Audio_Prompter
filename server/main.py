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
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        asyncio.create_task(server.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        await server.stop()
        logger.info("Server stopped")

if __name__ == "__main__":
    asyncio.run(main()) 