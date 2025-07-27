#!/usr/bin/env python3
import os

def test_log_file():
    log_file = "user_requests.log"
    
    if os.path.exists(log_file):
        print(f"Файл {log_file} существует")
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Содержимое файла:\n{content}")
    else:
        print(f"Файл {log_file} не существует")

if __name__ == "__main__":
    test_log_file() 