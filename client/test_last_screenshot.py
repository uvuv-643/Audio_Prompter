#!/usr/bin/env python3

import os
import glob
from PIL import Image
from working_ocr_detector import WorkingOCRDetector

def test_last_screenshot():
    detector = WorkingOCRDetector()
    
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        return False
    
    screenshot_files = glob.glob(os.path.join(screenshots_dir, "*.png"))
    
    if not screenshot_files:
        return False
    
    latest_screenshot = max(screenshot_files, key=os.path.getctime)
    
    try:
        image = Image.open(latest_screenshot)
        timing = detector.extract_timing(image)
        
        if timing:
            if detector.is_valid_timing(timing):
                return True
            else:
                return False
        else:
            return False
            
    except:
        return False

if __name__ == "__main__":
    result = test_last_screenshot()
    
    if result:
        print("🎉 Test PASSED! OCR successfully detected timing!")
    else:
        print("💥 Test FAILED! OCR could not detect timing.") 