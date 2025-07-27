import asyncio
import threading
import time
import re
import tempfile
import os
import subprocess
import platform
from edge_tts import Communicate

class TTSEngine:
    def __init__(self):
        self.is_playing = False
        self.current_thread = None
        self.current_process = None
        self.voice = "ru-RU-SvetlanaNeural"
        self._initialize_tts()
    
    def _initialize_tts(self):
        try:
            print("🎤 Initializing Edge TTS engine...")
            print(f"✅ Using voice: {self.voice}")
            print("🎤 TTS engine ready (Microsoft Edge TTS)!")
        except Exception as e:
            print(f"❌ Failed to initialize TTS: {e}")
    
    def _clean_text(self, text):
        if not text or not text.strip():
            return ""
        
        text = text.strip()
        text = re.sub(r'[^\w\s\-\.\,\!\?\(\)\:\;]', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def _play_audio_file(self, file_path):
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                self.current_process = subprocess.Popen(["afplay", file_path])
                self.current_process.wait()
            elif system == "Windows":
                self.current_process = subprocess.Popen(["start", file_path], shell=True)
                self.current_process.wait()
            else:  # Linux
                self.current_process = subprocess.Popen(["aplay", file_path])
                self.current_process.wait()
        except Exception as e:
            print(f"❌ Audio playback error: {e}")
    
    async def _generate_speech(self, text):
        try:
            communicate = Communicate(text, self.voice, rate="+30%")
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_path = temp_file.name
            
            await communicate.save(temp_path)
            return temp_path
        except Exception as e:
            print(f"❌ Speech generation error: {e}")
            return None
    
    def speak(self, text, language='ru'):
        if not text:
            return False
        
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            return False
        
        try:
            if self.is_playing:
                print("🔇 Stopping previous speech...")
                self.stop_speaking()
                time.sleep(0.1)
            
            print(f"🎤 Speaking: {cleaned_text}")
            
            self.is_playing = True
            
            def speak_thread():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    temp_path = loop.run_until_complete(self._generate_speech(cleaned_text))
                    
                    if temp_path and os.path.exists(temp_path):
                        self._play_audio_file(temp_path)
                        
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    
                    loop.close()
                    
                except Exception as e:
                    print(f"❌ TTS error: {e}")
                finally:
                    self.is_playing = False
            
            self.current_thread = threading.Thread(target=speak_thread)
            self.current_thread.daemon = True
            self.current_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start TTS: {e}")
            self.is_playing = False
            return False
    
    def is_speaking(self):
        return self.is_playing
    
    def stop_speaking(self):
        if self.is_playing:
            try:
                if self.current_process:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=1)
            except Exception as e:
                print(f"⚠️ Error stopping speech: {e}")
            finally:
                self.is_playing = False
                print("🔇 Audio stopped")
    
    def wait_for_completion(self):
        if self.current_thread and self.current_thread.is_alive():
            self.current_thread.join() 