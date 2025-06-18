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
from gi.repository import Gtk, GLib, Notify, Gdk, WebKit2
import threading
from bs4 import BeautifulSoup
import re
import brotli
import markdown

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

def safe_decode(text):
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='replace')
    return str(text)

class DeSciOSChatWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="DeSciOS Assistant")
        self.set_default_size(440, 640)
        self.set_keep_above(True)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_border_width(0)
        self.set_icon_name("system-help")
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.set_decorated(False)
        self.set_opacity(0.98)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_window_button_press)
        self.current_theme = 'light'
        self.messages = []  # Store (sender, message) tuples for re-rendering

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
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("DeSciOS Assistant")
        header.set_name("headerbar")
        # Light/dark mode toggle button
        self.toggle_button = Gtk.Button(label="☾" if self.current_theme == 'dark' else "☀")
        self.toggle_button.set_name("togglemode")
        self.toggle_button.connect("clicked", self.toggle_theme)
        header.pack_end(self.toggle_button)
        main_vbox.pack_start(header, False, False, 0)

        # Chat area (scrollable)
        self.chat_listbox = Gtk.ListBox()
        self.chat_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        chat_scroll = Gtk.ScrolledWindow()
        chat_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        chat_scroll.set_vexpand(True)
        chat_scroll.set_hexpand(True)
        chat_scroll.add(self.chat_listbox)
        main_vbox.pack_start(chat_scroll, True, True, 0)

        # Input area
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        input_box.set_name("inputbox")
        self.input_entry = Gtk.Entry()
        self.input_entry.set_placeholder_text("Type your question and press Enter...")
        self.input_entry.set_size_request(0, 36)
        self.input_entry.set_hexpand(True)
        self.input_entry.connect("activate", self.on_send_clicked)
        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.on_send_clicked)
        input_box.pack_start(self.input_entry, True, True, 0)
        input_box.pack_start(send_button, False, False, 0)
        main_vbox.pack_start(input_box, False, False, 0)

        # Welcome message (always show on startup)
        self.append_message("assistant", "Hello! I am DeSciOS Assistant. How can I help you today?")
        self.show_all()

    def toggle_theme(self, widget):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.toggle_button.set_label("☾" if self.current_theme == 'dark' else "☀")
        # Re-render all messages with the new theme
        self.chat_listbox.foreach(lambda row: self.chat_listbox.remove(row))
        for sender, message in self.messages:
            self._append_message_no_store(sender, message)

    def on_window_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def append_message(self, sender, message):
        print(f"append_message called with sender={sender}, message={message}")
        self.messages.append((sender, message))
        self._append_message_no_store(sender, message)

    def _append_message_no_store(self, sender, message):
        print(f"_append_message_no_store called with sender={sender}, message={message}")
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        webview = WebKit2.WebView()
        webview.set_size_request(-1, 1)  # Let it shrink to fit

        html = markdown.markdown(safe_decode(message))
        bubble_class = "bubble-user" if sender == "user" else "bubble-assistant"
        if self.current_theme == 'dark':
            style = '''<style>
body {
  font-family: 'Segoe UI', 'Liberation Sans', Arial, sans-serif;
  font-size: 15px;
  margin: 0;
  padding: 0;
  background: #181c24;
  color: #e6e6e6;
}
.bubble {
  margin: 12px 24px;
  padding: 14px 18px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(59,130,246,0.08);
  max-width: 90%;
  word-break: break-word;
  display: inline-block;
}
.bubble-user {
  background: #3b82f6;
  color: #fff;
  margin-left: auto;
}
.bubble-assistant {
  background: #23272e;
  color: #e6e6e6;
  margin-right: auto;
}
h1, h2, h3 {
  margin: 10px 0 6px 0;
  font-weight: bold;
}
pre, code {
  background: #23272e;
  color: #e6e6e6;
  border-radius: 6px;
  padding: 2px 6px;
  font-family: 'Fira Mono', 'Consolas', monospace;
}
</style>'''
        else:
            style = '''<style>
body {
  font-family: 'Segoe UI', 'Liberation Sans', Arial, sans-serif;
  font-size: 15px;
  margin: 0;
  padding: 0;
  background: #f7f7fa;
  color: #23272e;
}
.bubble {
  margin: 12px 24px;
  padding: 14px 18px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(59,130,246,0.08);
  max-width: 90%;
  word-break: break-word;
  display: inline-block;
}
.bubble-user {
  background: #3b82f6;
  color: #fff;
  margin-left: auto;
}
.bubble-assistant {
  background: #e6e6e6;
  color: #23272e;
  margin-right: auto;
}
h1, h2, h3 {
  margin: 10px 0 6px 0;
  font-weight: bold;
}
pre, code {
  background: #e6e6e6;
  color: #23272e;
  border-radius: 6px;
  padding: 2px 6px;
  font-family: 'Fira Mono', 'Consolas', monospace;
}
</style>'''
        html = f"""
<html>
<head>{style}</head>
<body><div class='bubble {bubble_class}'>{html}</div></body>
</html>
"""
        print("HTML being loaded into WebView:")
        print(html)
        webview.load_html(html, "file:///")
        webview.set_hexpand(True)
        webview.set_vexpand(False)

        def on_load_changed(webview, load_event):
            if load_event == WebKit2.LoadEvent.FINISHED:
                # This JS returns the height of the body content
                webview.run_javascript(
                    "document.body.scrollHeight;",
                    None,
                    lambda webview, result, user_data: set_webview_height(webview, result),
                    None
                )

        def set_webview_height(webview, result):
            value = webview.run_javascript_finish(result)
            js_result = value.get_js_value()
            height = js_result.to_int32()
            print(f"Setting WebView height to: {height}")
            webview.set_size_request(-1, height)

        webview.connect("load-changed", on_load_changed)

        hbox.pack_end(webview, True, True, 0) if sender == "user" else hbox.pack_start(webview, True, True, 0)
        row.add(hbox)
        self.chat_listbox.add(row)
        self.chat_listbox.show_all()
        adj = self.chat_listbox.get_parent().get_vadjustment()
        GLib.idle_add(adj.set_value, adj.get_upper())

    def on_send_clicked(self, widget):
        user_text = self.input_entry.get_text().strip()
        if not user_text:
            return
        self.append_message("user", user_text)
        self.input_entry.set_text("")
        threading.Thread(target=self.handle_user_query, args=(user_text,), daemon=True).start()

    def handle_user_query(self, user_text):
        if any(x in user_text.lower() for x in ["search the web", "browse the web", "find online", "web result", "look up"]):
            response = self.web_search_and_summarize(user_text)
        elif any(x in user_text.lower() for x in ["what is installed", "what tools", "what software", "what can you do", "available tools", "list apps", "list software"]):
            response = self.scan_installed_tools()
        else:
            response = self.generate_response(user_text)
        GLib.idle_add(self.append_message, "assistant", response)

    def web_search_and_summarize(self, query):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept-Encoding": "gzip, deflate"
            }
            search_url = f"https://search.brave.com/search?q={requests.utils.quote(query)}"
            r = requests.get(search_url, timeout=10, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all('a', href=True)
            result_links = [a for a in links if a['href'].startswith('http') and 'brave.com' not in a['href']]
            if not result_links:
                return "No web results found."
            first_url = result_links[0]['href']
            page = requests.get(first_url, timeout=10, headers=headers)
            page_soup = BeautifulSoup(page.text, "html.parser")
            texts = page_soup.stripped_strings
            content = ' '.join(list(texts)[:1000])[:2000]
            summary_prompt = f"Summarize the following web page for a scientist:\n\n{content}"
            return self.generate_response(summary_prompt)
        except Exception as e:
            return f"Error during web search: {str(e)}"

    def scan_installed_tools(self):
        try:
            bins = set()
            for d in ["/usr/bin", "/usr/local/bin", "/opt"]:
                if os.path.exists(d):
                    for f in os.listdir(d):
                        if os.access(os.path.join(d, f), os.X_OK) and not os.path.isdir(os.path.join(d, f)):
                            bins.add(f)
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
