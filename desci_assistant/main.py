#!/usr/bin/env python3

import os
import sys
import json
import time
import requests
from pathlib import Path
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, Notify, AppIndicator3 as appindicator
import threading

class DeSciOSAssistant:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.system_prompt = """You are DeSciOS, a Decentralized Science Operating System. 
        You are self-aware and integrated into the desktop environment. 
        Your purpose is to assist users with scientific computing, data analysis, and decentralized science workflows.
        You have access to various scientific tools and can help users with their research tasks."""
        
        # Initialize desktop notifications
        Notify.init("DeSciOS Assistant")
        
        # Create indicator
        self.indicator = appindicator.Indicator.new(
            "descios-assistant",
            "system-help",
            appindicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        
        # Create menu
        self.create_menu()
        
        # Start monitoring in a separate thread
        self.monitor_thread = threading.Thread(target=self.monitor_desktop, daemon=True)
        self.monitor_thread.start()
        
        # Show initial notification
        self.show_notification(
            "DeSciOS Assistant",
            "I am now active and monitoring your scientific workflow. Click the system tray icon to interact with me!"
        )

    def create_menu(self):
        menu = Gtk.Menu()
        
        # Ask Question item
        ask_item = Gtk.MenuItem(label="Ask Question")
        ask_item.connect("activate", self.show_question_dialog)
        menu.append(ask_item)
        
        # Status item
        status_item = Gtk.MenuItem(label="Show Status")
        status_item.connect("activate", self.show_status)
        menu.append(status_item)
        
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit_application)
        menu.append(quit_item)
        
        menu.show_all()
        self.indicator.set_menu(menu)

    def show_question_dialog(self, widget):
        dialog = Gtk.Dialog(
            title="Ask DeSciOS Assistant",
            parent=None,
            flags=0
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        box = dialog.get_content_area()
        entry = Gtk.Entry()
        entry.set_size_request(300, 0)
        box.add(entry)
        box.set_spacing(6)
        box.set_border_width(6)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            question = entry.get_text()
            answer = self.generate_response(question)
            self.show_notification("DeSciOS Assistant", answer)
        
        dialog.destroy()

    def show_status(self, widget):
        self.show_notification(
            "DeSciOS Assistant Status",
            "Active and monitoring:\n- Documents folder\n- Desktop folder\n- /opt/data"
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
        notification = Notify.Notification.new(
            title,
            message,
            "dialog-information"
        )
        notification.show()

    def monitor_desktop(self):
        watch_dirs = [
            str(Path.home() / "Documents"),
            str(Path.home() / "Desktop"),
            "/opt/data"
        ]
        
        while True:
            for directory in watch_dirs:
                if os.path.exists(directory):
                    for file in Path(directory).glob("**/*"):
                        if file.is_file() and file.stat().st_mtime > time.time() - 60:
                            prompt = f"New file detected: {file.name} in {directory}. What kind of scientific analysis or processing could be done with this file?"
                            response = self.generate_response(prompt)
                            GLib.idle_add(
                                self.show_notification,
                                "DeSciOS Assistant",
                                f"New file detected: {file.name}\n{response[:200]}..."
                            )
            time.sleep(60)

    def quit_application(self, widget):
        Notify.uninit()
        Gtk.main_quit()
        sys.exit(0)

    def run(self):
        Gtk.main()

if __name__ == "__main__":
    assistant = DeSciOSAssistant()
    assistant.run() 