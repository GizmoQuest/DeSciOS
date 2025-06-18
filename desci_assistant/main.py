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
import re

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
* {
    transition: background 0.3s, color 0.3s;
}
window, textview, entry, button, headerbar {
    background: #181c24;
    color: #e6e6e6;
    font-family: "Segoe UI", "Liberation Sans", "Arial", sans-serif;
    font-size: 15px;
}
#headerbar {
    background: linear-gradient(90deg, #3b82f6 0%, #6366f1 100%);
    border-radius: 16px 16px 0 0;
    padding: 14px 28px;
    border-bottom: 1px solid #444;
    color: #fff;
}
.bubble-user, .bubble-assistant {
    border-radius: 20px;
    padding: 14px 20px;
    margin: 12px 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.bubble-user {
    background: #3b82f6;
    color: #fff;
    margin-left: 80px;
}
.bubble-assistant {
    background: #23272e;
    color: #e6e6e6;
    margin-right: 80px;
}
#inputbox {
    background: #23272e;
    border-radius: 0 0 16px 16px;
    border-top: 1px solid #444;
    margin: 8px;
    padding: 14px 12px 12px 12px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}
#togglemode {
    background: transparent;
    border: none;
    color: #fff;
    font-size: 16px;
    margin-left: 8px;
}
window {
    border-radius: 18px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
}
'''

LIGHT_CSS = DARK_CSS.replace(b'#181c24', b'#f7f7fa').replace(
    b'#23272e', b'#ffffff').replace(b'#e6e6e6', b'#23272e').replace(
    b'#bbb', b'#ccc')

class DeSciOSChatWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="DeSciOS Assistant")
        self.set_default_size(440, 640)
        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.set_opacity(0.98)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_window_button_press)
        self.current_theme = 'dark'
        self.style_provider = Gtk.CssProvider()
        self.load_theme()

        self.ollama_url = "http://localhost:11434/api/generate"
        self.system_prompt = (
            "You are DeSciOS, a Decentralized Science Operating System. "
            "You are self-aware and integrated into the desktop environment. "
            "You help users with scientific computing, data analysis, and decentralized science workflows. "
            + DOCKERFILE_SUMMARY
        )

        Notify.init("DeSciOS Assistant")

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("DeSciOS Assistant")
        header.set_name("headerbar")
        header.connect("button-press-event", self.on_header_double_click)

        self.toggle_button = Gtk.Button(label="☾")
        self.toggle_button.set_name("togglemode")
        self.toggle_button.connect("clicked", self.toggle_theme)
        header.pack_end(self.toggle_button)
        main_vbox.pack_start(header, False, False, 0)

        self.chat_listbox = Gtk.ListBox()
        self.chat_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        chat_scroll = Gtk.ScrolledWindow()
        chat_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        chat_scroll.set_vexpand(True)
        chat_scroll.add(self.chat_listbox)
        main_vbox.pack_start(chat_scroll, True, True, 0)

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

        self.append_message("assistant", "Hello! I am DeSciOS Assistant. How can I help you today?")
        self.show_all()

    def load_theme(self):
        css = DARK_CSS if self.current_theme == 'dark' else LIGHT_CSS
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.remove_provider_for_screen(screen, self.style_provider)
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(screen, self.style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def toggle_theme(self, widget):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.toggle_button.set_label("☾" if self.current_theme == 'dark' else "☀")
        self.load_theme()

    def on_window_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def on_header_double_click(self, widget, event):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            for row in self.chat_listbox.get_children():
                self.chat_listbox.remove(row)

    def markdown_to_pango(self, text):
        import re
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'```(\w+)?\n([\s\S]+?)```', lambda m: f'<span font_family="monospace">{GLib.markup_escape_text(m.group(2))}</span>', text)
        text = re.sub(r'^### (.+)$', r'<span size="12000" weight="bold">\1</span>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<span size="15000" weight="bold">\1</span>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<span size="20000" weight="bold">\1</span>', text, flags=re.MULTILINE)
        text = re.sub(r'`([^`]+)`', lambda m: f'<span font_family="monospace">{GLib.markup_escape_text(m.group(1))}</span>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
        text = re.sub(r'\[(.+?)\]\((https?://[^\s]+)\)', r'<a href="\2">\1</a>', text)
        return text

    def append_message(self, sender, message):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        bubble = Gtk.Label()
        bubble.set_line_wrap(True)
        bubble.set_xalign(0 if sender == "assistant" else 1)
        markup = self.markdown_to_pango(message)
        bubble.set_markup(f"<span size='large'>{markup}</span>")
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
        self.input_entry.grab_focus()
        threading.Thread(target=self.handle_user_query, args=(user_text,), daemon=True).start()

    def handle_user_query(self, user_text):
        GLib.idle_add(self.append_message, "assistant", "Typing...")
        time.sleep(0.4)
        children = self.chat_listbox.get_children()
        if children:
            GLib.idle_add(self.chat_listbox.remove, children[-1])

        if any(x in user_text.lower() for x in ["search the web", "browse the web", "find online", "web result", "look up"]):
            response = self.web_search_and_summarize(user_text)
        elif any(x in user_text.lower() for x in ["what is installed", "what tools", "what software", "what can you do", "available tools", "list apps", "list software"]):
            response = self.scan_installed_tools()
        else:
            response = self.generate_response(user_text)
        GLib.idle_add(self.append_message, "assistant", response)

    def web_search_and_summarize(self, query):
        try:
            headers = {"User-Agent": "Mozilla/5.0", "Accept-Encoding": "gzip, deflate"}
            r = requests.get(f"https://search.brave.com/search?q={requests.utils.quote(query)}", timeout=10, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all('a', href=True)
            result_links = [a for a in links if a['href'].startswith('http') and 'brave.com' not in a['href']]
            if not result_links:
                return "No web results found."
            first_url = result_links[0]['href']
            page = requests.get(first_url, timeout=10, headers=headers)
            content = ' '.join(list(BeautifulSoup(page.text, "html.parser").stripped_strings)[:1000])[:2000]
            return self.generate_response(f"Summarize this for a scientist:\n\n{content}")
        except Exception as e:
            return f"Error during web search: {str(e)}"

    def scan_installed_tools(self):
        try:
            bins = {f for d in ["/usr/bin", "/usr/local/bin", "/opt"] if os.path.exists(d) for f in os.listdir(d) if os.access(os.path.join(d, f), os.X_OK)}
            apps = {f.split(".desktop")[0] for d in ["/usr/share/applications", "/usr/local/share/applications"] if os.path.exists(d) for f in os.listdir(d) if f.endswith(".desktop")}
            return f"Installed CLI tools: {', '.join(sorted(bins)[:30])}...\nGUI apps: {', '.join(sorted(apps)[:30])}..."
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
