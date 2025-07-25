import time
import threading
from datetime import datetime

class TaskScheduler:
    def __init__(self, interval_seconds=15):
        self.interval_seconds = interval_seconds
        self.is_running = False
        self.thread = None
    
    def start_scheduled_task(self, task_function):
        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduled_task, args=(task_function,))
        self.thread.daemon = True
        self.thread.start()
    
    def _run_scheduled_task(self, task_function):
        while self.is_running:
            try:
                result = task_function()
            except:
                pass
            
            time.sleep(self.interval_seconds)
    
    def stop_scheduled_task(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
    
    def is_task_running(self):
        return self.is_running 