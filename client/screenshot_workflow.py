import time
import threading
from mouse_controller import MouseController
from screenshot_capture import ScreenshotCapture
from image_processor import ImageProcessor
from file_manager import FileManager
from working_ocr_detector import WorkingOCRDetector
from vtt_parser import VTTParser
from tts_engine import TTSEngine

class ScreenshotWorkflow:
    def __init__(self, output_dir="screenshots", vtt_url=None, enable_tts=True):
        self.mouse_controller = MouseController()
        self.screenshot_capture = ScreenshotCapture()
        self.image_processor = ImageProcessor()
        self.file_manager = FileManager(output_dir)
        self.text_detector = WorkingOCRDetector()
        self.vtt_parser = VTTParser()
        self.tts_engine = TTSEngine() if enable_tts else None
        self.vtt_url = vtt_url
        self.enable_tts = enable_tts
        self.last_subtitle = None
        self._load_vtt_subtitles()
    
    def _load_vtt_subtitles(self):
        if self.vtt_url:
            if self.vtt_parser.load_from_url(self.vtt_url):
                print(f"✅ VTT subtitles loaded from: {self.vtt_url}")
            else:
                print(f"❌ Failed to load VTT subtitles from: {self.vtt_url}")
    
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
            
            if self.vtt_parser.subtitles:
                subtitle_info = self.vtt_parser.get_subtitle_info(timing)
                if subtitle_info:
                    timing_str, subtitle_text = subtitle_info
                    print(f"💬 {timing_str} | {subtitle_text}")
                    
                    if self.enable_tts and self.tts_engine and subtitle_text.strip():
                        if self.last_subtitle != subtitle_text:
                            self.last_subtitle = subtitle_text
                            time.sleep(0.1)
                            self._handle_subtitle_speech(subtitle_text, current_pos)
                else:
                    print(f"🔍 {timing} | No subtitle found")
        
        saved_filepath = self.file_manager.save_image(cropped_screenshot)
        
        subtitle_text = ''
        if timing and self.text_detector.is_valid_timing(timing):
            if self.vtt_parser.subtitles:
                subtitle_info = self.vtt_parser.get_subtitle_info(timing)
                if subtitle_info:
                    timing_str, subtitle_text = subtitle_info
        
        return {
            'mouse_position': current_pos,
            'saved_filepath': saved_filepath,
            'crop_size': 100,
            'timing': timing,
            'subtitle_text': subtitle_text
        }
    
    def execute_next_subtitle(self):
        if not self.vtt_url:
            raise ValueError("No VTT URL configured")
        
        import re
        
        old_url = self.vtt_url
        numbers = re.findall(r'\d+', old_url)
        
        if not numbers:
            raise ValueError("No numbers found in URL")
        
        last_number = numbers[-1]
        new_number = str(int(last_number) + 1)
        
        new_url = re.sub(r'\d+(?=[^/]*$)', new_number, old_url)
        new_url = new_url.replace("rus", "eng")
        
        self.vtt_url = new_url
        self._load_vtt_subtitles()
        
        return {
            'old_url': old_url,
            'new_url': new_url,
            'old_number': last_number,
            'new_number': new_number
        }
    
    def _handle_subtitle_speech(self, subtitle_text, mouse_position):
        def speech_and_click():
            try:
                print(f"🎤 Starting speech synthesis for: {subtitle_text}")
                
                if self.tts_engine.speak(subtitle_text, language='ru'):
                    print("⏳ Waiting for speech to complete...")
                    self.tts_engine.wait_for_completion()
                    
                    print("🖱️ Speech completed, performing mouse click...")
                    time.sleep(0.2)
                    
                    self.mouse_controller.click_at_position(mouse_position.x, mouse_position.y)
                    print("✅ Mouse click completed")
                else:
                    print("❌ Failed to start speech synthesis")
                    
            except Exception as e:
                print(f"❌ Error in speech and click workflow: {e}")
        
        speech_thread = threading.Thread(target=speech_and_click)
        speech_thread.daemon = True
        speech_thread.start() 