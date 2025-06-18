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
import brotli

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
.bubble-user {
    background: #3b82f6;
    color: #fff;
    border-radius: 18px 18px 6px 18px;
    padding: 12px 18px;
    margin: 10px 0 10px 80px;
    box-shadow: 0 2px 8px rgba(59,130,246,0.08);
}
.bubble-assistant {
    background: #23272e;
    color: #e6e6e6;
    border-radius: 18px 18px 18px 6px;
    padding: 12px 18px;
    margin: 10px 80px 10px 0;
    box-shadow: 0 2px 8px rgba(55,65,81,0.08);
}
#inputbox {
    background: #23272e;
    border-radius: 0 0 16px 16px;
    border-top: 1px solid #444;
    padding: 14px 12px 12px 12px;
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

LIGHT_CSS = b'''
window, textview, entry, button, headerbar {
    background: #f7f7fa;
    color: #23272e;
    font-family: "Segoe UI", "Liberation Sans", "Arial", sans-serif;
    font-size: 15px;
}
#headerbar {
    background: linear-gradient(90deg, #a1c4fd 0%, #c2e9fb 100%);
    border-radius: 16px 16px 0 0;
    padding: 14px 28px;
    border-bottom: 1px solid #bbb;
    color: #23272e;
}
.bubble-user {
    background: #3b82f6;
    color: #fff;
    border-radius: 18px 18px 6px 18px;
    padding: 12px 18px;
    margin: 10px 0 10px 80px;
    box-shadow: 0 2px 8px rgba(59,130,246,0.08);
}
.bubble-assistant {
    background: #e6e6e6;
    color: #23272e;
    border-radius: 18px 18px 18px 6px;
    padding: 12px 18px;
    margin: 10px 80px 10px 0;
    box-shadow: 0 2px 8px rgba(55,65,81,0.08);
}
#inputbox {
    background: #f7f7fa;
    border-radius: 0 0 16px 16px;
    border-top: 1px solid #bbb;
    padding: 14px 12px 12px 12px;
}
#togglemode {
    background: transparent;
    border: none;
    color: #23272e;
    font-size: 16px;
    margin-left: 8px;
}
window {
    border-radius: 18px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}
'''

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
        self.current_theme = 'dark'
        self.style_provider = Gtk.CssProvider()
        self.load_theme()

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

        # Welcome message
        self.append_message("assistant", "Hello! I am DeSciOS Assistant. How can I help you today?")

        self.show_all()

    def load_theme(self):
        css = DARK_CSS if self.current_theme == 'dark' else LIGHT_CSS
        screen = Gdk.Screen.get_default()
        # Remove previous provider if present
        Gtk.StyleContext.remove_provider_for_screen(
            screen, self.style_provider
        )
        self.style_provider = Gtk.CssProvider()
        self.style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            self.style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def toggle_theme(self, widget):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.toggle_button.set_label("☾" if self.current_theme == 'dark' else "☀")
        self.load_theme()

    def on_window_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def markdown_to_pango(self, text):
        import re
        # Remove any HTML tags that may have leaked in
        text = re.sub(r'<[^>]+>', '', text)
        # Code blocks (```...```)
        def code_block_repl(match):
            code = match.group(2)
            code = GLib.markup_escape_text(code)
            return f'<span font_family="monospace">{code}</span>'
        text = re.sub(r'```(\w+)?\n([\s\S]+?)```', code_block_repl, text)
        # Headings: use only numeric size values
        text = re.sub(r'^### (.+)$', r'<span size="12000" weight="bold">\1</span>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<span size="15000" weight="bold">\1</span>', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'<span size="20000" weight="bold">\1</span>', text, flags=re.MULTILINE)
        # Inline code (`code`)
        text = re.sub(r'`([^`]+)`', lambda m: f'<span font_family="monospace">{GLib.markup_escape_text(m.group(1))}</span>', text)
        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
        # Italic: *text* or _text_
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
        text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', text)
        # Links: [text](url)
        text = re.sub(r'\[(.+?)\]\((https?://[^\s]+)\)', r'<a href="\2">\1</a>', text)
        # Numbered lists: 1. item
        lines = text.split('\n')
        new_lines = []
        in_list = False
        for line in lines:
            if re.match(r'^\s*\d+\. ', line):
                in_list = True
                new_lines.append('    ' + re.sub(r'^\s*(\d+\.) ', r'<b>\1</b> ', line))
            elif re.match(r'^\s*[-\*] ', line):
                in_list = True
                new_lines.append('    • ' + line.lstrip('-* ').strip())
            else:
                if in_list and line.strip() == '':
                    in_list = False
                new_lines.append(line)
        text = '\n'.join(new_lines)
        # Escape any remaining markup
        text = GLib.markup_escape_text(text)
        # Unescape only the tags we generated
        text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
        text = text.replace('&lt;a href=&quot;', '<a href="').replace('&quot;&gt;', '">').replace('&lt;/a&gt;', '</a>')
        text = text.replace('&lt;span ', '<span ').replace('&lt;/span&gt;', '</span>')
        text = text.replace('&quot;', '"')
        # Strict: only allow <span font_family="monospace"> and <span size="[0-9]+" ...> tags
        text = re.sub(r'<span(?! (font_family="monospace"|size="[0-9]+"))(.*?)>', '', text)
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
