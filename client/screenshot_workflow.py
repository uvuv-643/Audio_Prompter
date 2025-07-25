import time
from mouse_controller import MouseController
from screenshot_capture import ScreenshotCapture
from image_processor import ImageProcessor
from file_manager import FileManager
from working_ocr_detector import WorkingOCRDetector

class ScreenshotWorkflow:
    def __init__(self, output_dir="screenshots"):
        self.mouse_controller = MouseController()
        self.screenshot_capture = ScreenshotCapture()
        self.image_processor = ImageProcessor()
        self.file_manager = FileManager(output_dir)
        self.text_detector = WorkingOCRDetector()
    
    def execute_screenshot_workflow(self):
        current_pos = self.mouse_controller.click_at_current_position()
        
        time.sleep(0.3)
        
        left = max(0, current_pos.x - 100)
        top = max(0, current_pos.y - 100)
        width = 100
        height = 40
        
        cropped_screenshot = self.screenshot_capture.capture_region(left, top, width, height)
        
        timing = self.text_detector.extract_timing(cropped_screenshot)
        
        if timing and self.text_detector.is_valid_timing(timing):
            print(f"🎬 {timing}")
        
        saved_filepath = self.file_manager.save_image(cropped_screenshot)
        
        return {
            'mouse_position': current_pos,
            'saved_filepath': saved_filepath,
            'crop_size': 100,
            'timing': timing
        } 