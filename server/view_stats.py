#!/usr/bin/env python3
import os
import sys
from collections import defaultdict, Counter

def view_user_stats():
    log_file = "user_requests.log"
    
    if not os.path.exists(log_file):
        print("Файл логов не найден")
        return
    
    user_requests = defaultdict(list)
    all_requests = []
    
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines[1:]:
        parts = line.strip().split('\t')
        if len(parts) >= 2:
            user_id = parts[0]
            request_text = parts[1]
            user_requests[user_id].append(request_text)
            all_requests.append(request_text)
    
    print("=== СТАТИСТИКА ЗАПРОСОВ ===\n")
    
    print(f"Всего запросов: {len(all_requests)}")
    print(f"Уникальных пользователей: {len(user_requests)}")
    print()
    
    print("=== ПОЛЬЗОВАТЕЛИ ===\n")
    for user_id, requests in user_requests.items():
        print(f"Пользователь {user_id}: {len(requests)} запросов")
        for i, req in enumerate(requests[-5:], 1):
            print(f"  {i}. {req}")
        if len(requests) > 5:
            print(f"  ... и еще {len(requests) - 5} запросов")
        print()
    
    print("=== ПОПУЛЯРНЫЕ ЗАПРОСЫ ===\n")
    request_counter = Counter(all_requests)
    for request, count in request_counter.most_common(10):
        print(f"{request}: {count} раз")

if __name__ == "__main__":
    view_user_stats() 