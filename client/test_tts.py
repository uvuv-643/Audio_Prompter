#!/usr/bin/env python3

from tts_engine import TTSEngine
import time

def test_tts():
    print("🎤 Testing Edge TTS engine...")
    
    tts = TTSEngine()
    
    test_texts = [
        "Привет, как дела?",
        "Время новых сэндвичей",
        "Это тестовая фраза на русском языке"
    ]
    
    for text in test_texts:
        print(f"\n🎤 Testing: {text}")
        if tts.speak(text, language='ru'):
            print("✅ Speech started successfully")
            tts.wait_for_completion()
            print("✅ Speech completed")
        else:
            print("❌ Failed to start speech")
        
        time.sleep(1)

if __name__ == "__main__":
    test_tts() 