import pyautogui
from PIL import Image

class ScreenshotCapture:
    def __init__(self):
        pyautogui.FAILSAFE = True
    
    def capture_full_screen(self):
        screenshot = pyautogui.screenshot()
        return screenshot
    
    def capture_region(self, x, y, width, height):
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        return screenshot 