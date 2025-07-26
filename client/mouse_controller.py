import pyautogui
import time

class MouseController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
    
    def click_at_current_position(self):
        current_pos = pyautogui.position()
        pyautogui.click(current_pos.x, current_pos.y)
        return current_pos
    
    def get_current_position(self):
        return pyautogui.position()
    
    def click_at_position(self, x, y):
        pyautogui.click(x, y)
        return pyautogui.Point(x, y) 