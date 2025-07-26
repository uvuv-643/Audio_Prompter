import re
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

class VTTSubtitle:
    def __init__(self, start_time: str, end_time: str, text: str = ""):
        self.start_time = start_time
        self.end_time = end_time
        self.text = text.strip()
    
    def __str__(self):
        return f"{self.start_time} --> {self.end_time}\n{self.text}"

class VTTParser:
    def __init__(self):
        self.subtitles: List[VTTSubtitle] = []
        self.time_pattern = re.compile(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})')
    
    def load_from_url(self, url: str) -> bool:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            return self.parse_content(response.text)
        except Exception as e:
            print(f"Error loading VTT from URL: {e}")
            return False
    
    def load_from_file(self, file_path: str) -> bool:
        try:
            encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'windows-1251', 'iso-8859-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                print(f"Error: Could not decode file with any encoding")
                return False
                
            return self.parse_content(content)
        except Exception as e:
            print(f"Error loading VTT from file: {e}")
            return False
    
    def parse_content(self, content: str) -> bool:
        self.subtitles.clear()
        
        content = content.strip()
        if content.startswith('\ufeff'):
            content = content[1:]
        
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line == 'WEBVTT' or not line:
                i += 1
                continue
            
            time_match = self.time_pattern.search(line)
            if time_match:
                start_time = time_match.group(0)
                
                end_match = self.time_pattern.search(line, time_match.end())
                if end_match:
                    end_time = end_match.group(0)
                    
                    text_lines = []
                    i += 1
                    while i < len(lines) and lines[i].strip():
                        text_lines.append(lines[i].strip())
                        i += 1
                    
                    text = '\n'.join(text_lines)
                    subtitle = VTTSubtitle(start_time, end_time, text)
                    self.subtitles.append(subtitle)
            
            i += 1
        
        return len(self.subtitles) > 0
    
    def time_to_seconds(self, time_str: str) -> float:
        if '.' in time_str:
            match = self.time_pattern.match(time_str)
            if not match:
                return 0.0
            
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3))
            milliseconds = int(match.group(4))
            
            return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
        else:
            simple_pattern = re.compile(r'(\d{1,2}):(\d{2}):(\d{2})')
            match = simple_pattern.match(time_str)
            if not match:
                return 0.0
            
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3))
            
            return hours * 3600 + minutes * 60 + seconds
    
    def seconds_to_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"
    
    def find_subtitle_at_time(self, timing: str) -> Optional[VTTSubtitle]:
        if not self.subtitles:
            return None
        
        target_seconds = self.time_to_seconds(timing)
        
        for subtitle in self.subtitles:
            start_seconds = self.time_to_seconds(subtitle.start_time)
            end_seconds = self.time_to_seconds(subtitle.end_time)
            
            if start_seconds <= target_seconds <= end_seconds:
                return subtitle
        
        return None
    
    def find_closest_subtitle(self, timing: str) -> Optional[VTTSubtitle]:
        if not self.subtitles:
            return None
        
        target_seconds = self.time_to_seconds(timing)
        closest_subtitle = None
        min_distance = float('inf')
        
        for subtitle in self.subtitles:
            start_seconds = self.time_to_seconds(subtitle.start_time)
            end_seconds = self.time_to_seconds(subtitle.end_time)
            
            if start_seconds <= target_seconds <= end_seconds:
                return subtitle
            
            distance_to_start = abs(target_seconds - start_seconds)
            distance_to_end = abs(target_seconds - end_seconds)
            min_subtitle_distance = min(distance_to_start, distance_to_end)
            
            if min_subtitle_distance < min_distance:
                min_distance = min_subtitle_distance
                closest_subtitle = subtitle
        
        return closest_subtitle if min_distance <= 5.0 else None
    
    def get_subtitle_info(self, timing: str) -> Optional[Tuple[str, str]]:
        subtitle = self.find_subtitle_at_time(timing)
        if not subtitle:
            subtitle = self.find_closest_subtitle(timing)
        
        if subtitle:
            return (timing, subtitle.text)
        return None 