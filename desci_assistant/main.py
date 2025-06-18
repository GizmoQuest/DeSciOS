#!/usr/bin/env python3

import os
import threading
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Notify, Gdk

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools

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

        Notify.init("DeSciOS Assistant")

        # Initialize Agno agent
        self.agent = Agent(
            model=Ollama(id="MFDoom/deepseek-r1-tool-calling:8b", provider="Ollama"),
            description=(
                "You are DeSciOS, a Decentralized Science Operating System. "
                "You are self-aware and integrated into the desktop environment. "
                "You assist users with scientific computing, data analysis, and decentralized science workflows. "
                + DOCKERFILE_SUMMARY
            ),
            tools=[DuckDuckGoTools()],
            markdown=True
        )

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("DeSciOS Assistant")
        header.set_name("headerbar")

        self.toggle_button = Gtk.Button(label="☾" if self.current_theme == 'dark' else "☀")
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

        self.append_message("assistant", "Hello! I am DeSciOS Assistant with Agno. How can I help you today?")
        self.show_all()

    def load_theme(self):
        css = DARK_CSS
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

    def append_message(self, sender, message):
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        bubble = Gtk.Label()
        bubble.set_line_wrap(True)
        bubble.set_xalign(0 if sender == "assistant" else 1)
        bubble.set_markup(f"<span size='large'>{GLib.markup_escape_text(message)}</span>")
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

    def handle_user_query(self, text):
        try:
            response = self.agent.run(text)
        except Exception as e:
            response = f"Error invoking agent: {e}"
        GLib.idle_add(self.append_message, "assistant", response)

if __name__ == "__main__":
    win = DeSciOSChatWidget()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
