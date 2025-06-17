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
from gi.repository import Gtk, GLib, Notify, Gdk
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

DARK_CSS = b'''
window, textview, entry, button, headerbar {
    background: #23272e;
    color: #e6e6e6;
    font-family: "Segoe UI", "Liberation Sans", "Arial", sans-serif;
    font-size: 13px;
}
#headerbar {
    background: #23272e;
    border-radius: 12px 12px 0 0;
    padding: 8px 16px;
    border-bottom: 1px solid #444;
}
.bubble-user {
    background: #3b82f6;
    color: #fff;
    border-radius: 16px 16px 4px 16px;
    padding: 8px 14px;
    margin: 6px 0 6px 60px;
    align-self: flex-end;
}
.bubble-assistant {
    background: #374151;
    color: #e6e6e6;
    border-radius: 16px 16px 16px 4px;
    padding: 8px 14px;
    margin: 6px 60px 6px 0;
    align-self: flex-start;
}
#inputbox {
    background: #23272e;
    border-radius: 0 0 12px 12px;
    border-top: 1px solid #444;
    padding: 10px 8px 8px 8px;
}
'''

class DeSciOSChatWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="DeSciOS Assistant")
        self.set_default_size(420, 600)
        self.set_keep_above(True)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_border_width(0)
        self.set_icon_name("system-help")
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.14, 0.15, 0.18, 0.98))
        self.set_decorated(False)
        self.set_opacity(0.98)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_window_button_press)

        # CSS styling
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(DARK_CSS)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

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
        icon = Gtk.Image.new_from_icon_name("system-help", Gtk.IconSize.DIALOG)
        header.pack_start(icon)
        main_vbox.pack_start(header, False, False, 0)

        # Chat area (scrollable)
        self.chat_listbox = Gtk.ListBox()
        self.chat_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        chat_scroll = Gtk.ScrolledWindow()
        chat_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        chat_scroll.set_vexpand(True)
        chat_scroll.add(self.chat_listbox)
        main_vbox.pack_start(chat_scroll, True, True, 0)

        # Input area
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        input_box.set_name("inputbox")
        self.input_entry = Gtk.Entry()
        self.input_entry.set_placeholder_text("Type your question and press Enter...")
        self.input_entry.connect("activate", self.on_send_clicked)
        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.on_send_clicked)
        input_box.pack_start(self.input_entry, True, True, 0)
        input_box.pack_start(send_button, False, False, 0)
        main_vbox.pack_start(input_box, False, False, 0)

        # Welcome message
        self.append_message("assistant", "Hello! I am DeSciOS Assistant. How can I help you today?")

        self.show_all()

    def on_window_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def append_message(self, sender, message):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        bubble = Gtk.Label()
        bubble.set_line_wrap(True)
        bubble.set_xalign(0 if sender == "assistant" else 1)
        bubble.set_markup(f"<span size='large'>{Gtk.utils.escape(message)}</span>")
        bubble.set_selectable(True)
        bubble.set_justify(Gtk.Justification.LEFT)
        bubble.set_padding(8, 8)
        bubble.set_margin_top(2)
        bubble.set_margin_bottom(2)
        bubble.set_margin_start(8)
        bubble.set_margin_end(8)
        bubble.set_name(f"bubble-{sender}")
        hbox.pack_end(bubble, True, True, 0) if sender == "user" else hbox.pack_start(bubble, True, True, 0)
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
            search_url = f"https://duckduckgo.com/html/?q={requests.utils.quote(query)}"
            r = requests.get(search_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all('a', class_='result__a', href=True)
            if not links:
                return "No web results found."
            first_url = links[0]['href']
            page = requests.get(first_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
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