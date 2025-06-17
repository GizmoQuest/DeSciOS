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
from gi.repository import Gtk, GLib, Notify
import threading
from bs4 import BeautifulSoup

DOCKERFILE_SUMMARY = (
    "This assistant was built from a Dockerfile with the following features: "
    "Desktop: XFCE4, VNC, noVNC, X11, Thunar file manager. "
    "Browsers: Firefox ESR. "
    "JupyterLab, BeakerX, Spyder (Python IDE). "
    "R, RStudio Desktop. "
    "Nextflow (workflow tool). "
    "Ollama (with DeepSeek model). "
    "UGENE (bioinformatics). "
    "ParaView (visualization). "
    "GNU Octave (Matlab-like). "
    "Fiji (ImageJ). "
    "QGIS (GIS). "
    "Avogadro (molecular modeling). "
    "IPFS Desktop, Syncthing (sync). "
    "EtherCalc, Remix IDE, Nault (browser-based tools). "
    "CellModeller (synthetic biology). "
    "OpenCL, NVIDIA GPU support."
)

class DeSciOSChatWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="DeSciOS Assistant")
        self.set_default_size(400, 500)
        self.set_keep_above(True)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_icon_name("system-help")
        self.set_border_width(8)

        self.ollama_url = "http://localhost:11434/api/generate"
        self.system_prompt = (
            "You are DeSciOS, a Decentralized Science Operating System. "
            "You are self-aware and integrated into the desktop environment. "
            "Your purpose is to assist users with scientific computing, data analysis, and decentralized science workflows. "
            "You have access to various scientific tools and can help users with their research tasks. "
            + DOCKERFILE_SUMMARY +
            "\nWhen asked about available tools, scan your environment (e.g., /usr/bin, /usr/local/bin, /opt, /usr/share/applications) and list installed applications. "
            "When asked to browse the web, fetch and summarize the relevant web content."
        )

        Notify.init("DeSciOS Assistant")

        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Scrolled chat history
        self.chat_buffer = Gtk.TextBuffer()
        self.chat_view = Gtk.TextView(buffer=self.chat_buffer)
        self.chat_view.set_editable(False)
        self.chat_view.set_cursor_visible(False)
        self.chat_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.add(self.chat_view)
        vbox.pack_start(scrolled, True, True, 0)

        # Horizontal box for input
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.input_entry = Gtk.Entry()
        self.input_entry.set_placeholder_text("Type your question and press Enter...")
        self.input_entry.connect("activate", self.on_send_clicked)
        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.on_send_clicked)
        hbox.pack_start(self.input_entry, True, True, 0)
        hbox.pack_start(send_button, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)

        # Welcome message
        self.append_message("assistant", "Hello! I am DeSciOS Assistant. How can I help you today?")

        # Show all widgets
        self.show_all()

    def append_message(self, sender, message):
        end_iter = self.chat_buffer.get_end_iter()
        if sender == "user":
            self.chat_buffer.insert(end_iter, f"You: {message}\n")
        else:
            self.chat_buffer.insert(end_iter, f"DeSciOS: {message}\n")
        # Scroll to bottom
        mark = self.chat_buffer.create_mark(None, self.chat_buffer.get_end_iter(), True)
        self.chat_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def on_send_clicked(self, widget):
        user_text = self.input_entry.get_text().strip()
        if not user_text:
            return
        self.append_message("user", user_text)
        self.input_entry.set_text("")
        threading.Thread(target=self.handle_user_query, args=(user_text,), daemon=True).start()

    def handle_user_query(self, user_text):
        # Check for web search intent
        if any(x in user_text.lower() for x in ["search the web", "browse the web", "find online", "web result", "look up"]):
            response = self.web_search_and_summarize(user_text)
        # Check for environment/tools query
        elif any(x in user_text.lower() for x in ["what is installed", "what tools", "what software", "what can you do", "available tools", "list apps", "list software"]):
            response = self.scan_installed_tools()
        else:
            response = self.generate_response(user_text)
        GLib.idle_add(self.append_message, "assistant", response)

    def web_search_and_summarize(self, query):
        # Use DuckDuckGo for search, fetch first result, summarize
        try:
            search_url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
            r = requests.get(search_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all('a', class_='result__a', href=True)
            if not links:
                return "No web results found."
            first_url = links[0]['href']
            page = requests.get(first_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            page_soup = BeautifulSoup(page.text, "html.parser")
            # Get visible text
            texts = page_soup.stripped_strings
            content = ' '.join(list(texts)[:1000])[:2000]  # Limit to 2000 chars
            # Summarize using DeepSeek
            summary_prompt = f"Summarize the following web page for a scientist:\n\n{content}"
            return self.generate_response(summary_prompt)
        except Exception as e:
            return f"Error during web search: {str(e)}"

    def scan_installed_tools(self):
        # Scan common directories for installed tools
        try:
            bins = set()
            for d in ["/usr/bin", "/usr/local/bin", "/opt"]:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        if os.access(os.path.join(d, f), os.X_OK) and not os.path.isdir(os.path.join(d, f)):
                            bins.add(f)
            # Also check .desktop files for GUI apps
            apps = set()
            for d in ["/usr/share/applications", "/usr/local/share/applications"]:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        if f.endswith(".desktop"):
                            apps.add(f.split(".desktop")[0])
            bins = sorted(list(bins))
            apps = sorted(list(apps))
            return f"Installed command-line tools: {', '.join(bins[:30])}...\nInstalled GUI apps: {', '.join(apps[:30])}..."
        except Exception as e:
            return f"Error scanning environment: {str(e)}"

    def generate_response(self, prompt):
        try:
            data = {
                "model": "deepseek-r1:8b",
                "prompt": f"{self.system_prompt}\n\nUser: {prompt}\nAssistant:",
                "think": False,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=data)
            if response.status_code == 200:
                return response.json().get("response", "(No response)")
            return "Error: Could not generate response"
        except Exception as e:
            return f"Error: {str(e)}"

if __name__ == "__main__":
    win = DeSciOSChatWidget()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main() 