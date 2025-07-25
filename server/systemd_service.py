#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

def create_systemd_service():
    current_dir = Path(__file__).parent.absolute()
    server_path = current_dir / "server.py"
    python_path = sys.executable
    
    service_content = f"""[Unit]
Description=Screenshot Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={current_dir}
ExecStart={python_path} {server_path}
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/etc/systemd/system/screenshot-server.service"
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", "screenshot-server"], check=True)
        
        print(f"Systemd service created: {service_file}")
        print("Service enabled for auto-start")
        print("To start: systemctl start screenshot-server")
        print("To stop: systemctl stop screenshot-server")
        print("To check status: systemctl status screenshot-server")
        
    except subprocess.CalledProcessError as e:
        print(f"Error creating systemd service: {e}")
        print("Run this script with sudo")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_systemd_service() 