#!/usr/bin/env python3

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify, GLib
    
class DeSciOSAssistant:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.system_prompt = """You are DeSciOS, a Decentralized Science Operating System. 
        You are self-aware and integrated into the desktop environment. 
        Your purpose is to assist users with scientific computing, data analysis, and decentralized science workflows.
        You have access to various scientific tools and can help users with their research tasks."""
        
        # Initialize desktop notifications
        Notify.init("DeSciOS Assistant")
        self.notification = Notify.Notification.new(
            "DeSciOS Assistant",
            "Initializing...",
            "dialog-information"
        )
        
    def generate_response(self, prompt):
        try:
            data = {
                "model": "deepseek-r1:8b",
                "prompt": f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:",
                "stream": False
            }
            response = requests.post(self.ollama_url, json=data)
            if response.status_code == 200:
                return response.json()["response"]
            return "Error: Could not generate response"
        except Exception as e:
            return f"Error: {str(e)}"

    def show_notification(self, title, message):
        self.notification.update(title, message)
        self.notification.show()

    def monitor_desktop(self):
        # Monitor common scientific directories
        watch_dirs = [
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
            "/opt/data"
        ]
        
        while True:
            for directory in watch_dirs:
                if os.path.exists(directory):
                    # Check for new files
                    for file in Path(directory).glob("**/*"):
                        if file.is_file() and file.stat().st_mtime > time.time() - 60:
                            # New file detected
                            prompt = f"New file detected: {file.name} in {directory}. What kind of scientific analysis or processing could be done with this file?"
                            response = self.generate_response(prompt)
                            self.show_notification(
                                "DeSciOS Assistant",
                                f"New file detected: {file.name}\n{response}"
                            )
            
            time.sleep(60)  # Check every minute

    def run(self):
        self.show_notification(
            "DeSciOS Assistant",
            "I am now active and monitoring your scientific workflow. I can help with data analysis, scientific computing, and DeSci tasks."
        )
        self.monitor_desktop()

if __name__ == "__main__":
    assistant = DeSciOSAssistant()
    assistant.run() 