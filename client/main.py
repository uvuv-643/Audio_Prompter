#!/usr/bin/env python3

import signal
import sys
from screenshot_workflow import ScreenshotWorkflow
from scheduler import TaskScheduler

def signal_handler(sig, frame):
    if scheduler:
        scheduler.stop_scheduled_task()
    sys.exit(0)

def main():
    global scheduler
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    workflow = ScreenshotWorkflow()
    scheduler = TaskScheduler(interval_seconds=15)
    
    scheduler.start_scheduled_task(workflow.execute_screenshot_workflow)
    
    try:
        while scheduler.is_task_running():
            signal.pause()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    scheduler = None
    main() 