#!/usr/bin/env python3

import signal
import sys
import argparse
from screenshot_workflow import ScreenshotWorkflow
from scheduler import TaskScheduler

def signal_handler(sig, frame):
    if scheduler:
        scheduler.stop_scheduled_task()
    sys.exit(0)

def main():
    global scheduler
    
    parser = argparse.ArgumentParser(description='Screenshot Workflow with VTT Subtitles and TTS')
    parser.add_argument('--vtt-url', help='URL to VTT subtitles file')
    parser.add_argument('--interval', type=int, default=15, help='Screenshot interval in seconds')
    parser.add_argument('--no-tts', action='store_true', help='Disable TTS functionality')
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    workflow = ScreenshotWorkflow(vtt_url=args.vtt_url, enable_tts=not args.no_tts)
    scheduler = TaskScheduler(interval_seconds=args.interval)
    
    scheduler.start_scheduled_task(workflow.execute_screenshot_workflow)
    
    try:
        while scheduler.is_task_running():
            signal.pause()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    scheduler = None
    main() 