import os
from datetime import datetime

class FileManager:
    def __init__(self, output_dir="screenshots"):
        self.output_dir = output_dir
        self._ensure_output_directory()
    
    def _ensure_output_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_timestamp_filename(self, extension="png"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"screenshot_{timestamp}.{extension}"
    
    def save_image(self, image, filename=None):
        if filename is None:
            filename = self.generate_timestamp_filename()
        
        filepath = os.path.join(self.output_dir, filename)
        image.save(filepath)
        return filepath
    
    def get_output_directory(self):
        return self.output_dir 