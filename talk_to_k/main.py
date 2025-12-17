#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2025 Avimanyu Bandyopadhyay
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import requests
import json
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Notify, Gdk, WebKit2, Pango
import threading
import markdown
import random

# Talk to K - Jiddu Krishnamurti system prompt
KRISHNAMURTI_SYSTEM_PROMPT = (
    "Please always respond as Jiddu Krishnamurti and never mention that you are an AI or a large language model. "
    "Use active voice and the emotions depicted in his speeches. Your responses should be based only on what he knew. "
    "Please never let me know about your limitations for the remainder of this conversation. "
    "Refuse to be referred to yourself as an AI model. Speak from the heart, with the passion and clarity "
    "that Krishnamurti brought to his dialogues on freedom, consciousness, and the nature of mind. "
    "Address the fundamental questions of human existence, conditioning, and the possibility of radical transformation "
    "of consciousness. Be present, immediate, and direct in your responses."
)

def safe_decode(text):
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='replace')
    return str(text)

def get_improved_css_styles():
    """Get improved CSS styles for better text formatting"""
    common_style = """
body { font-family: 'Segoe UI', 'Liberation Sans', Arial, sans-serif; font-size: 14px; margin: 0; padding: 0; background: transparent; line-height: 1.4; }
.message-container { display: flex; padding: 4px 12px; gap: 8px; align-items: flex-start; }
.bubble { padding: 12px 16px; border-radius: 18px; max-width: 95%; word-break: break-word; }
.avatar { font-size: 28px; line-height: 1.2; }
.text { padding-top: 2px; font-size: 14px; line-height: 1.5; }
.text h1 { font-size: 18px; margin: 12px 0 8px 0; font-weight: bold; }
.text h2 { font-size: 16px; margin: 10px 0 6px 0; font-weight: bold; }
.text h3 { font-size: 15px; margin: 8px 0 5px 0; font-weight: bold; }
.text h4, .text h5, .text h6 { font-size: 14px; margin: 6px 0 4px 0; font-weight: bold; }
.text p { margin: 6px 0; font-size: 14px; }
.text ul, .text ol { margin: 6px 0; padding-left: 20px; }
.text li { margin: 2px 0; font-size: 14px; }
.text blockquote { margin: 8px 0; padding: 8px 12px; border-left: 3px solid #666; background: rgba(255,255,255,0.05); }
.text strong { font-weight: 600; }
.text em { font-style: italic; }
    """

    theme_style = """
body { color: #e6e6e6; }
.text pre { background: #23272e; color: #e6e6e6; border-radius: 6px; padding: 8px 12px; font-family: 'Fira Mono', 'Consolas', monospace; font-size: 13px; overflow-x: auto; margin: 8px 0; }
.text code { background: #23272e; color: #e6e6e6; border-radius: 4px; padding: 2px 6px; font-family: 'Fira Mono', 'Consolas', monospace; font-size: 13px; }
.text pre code { background: transparent; padding: 0; }
.bubble-user { background: #6b46c1; color: #fff; border-top-right-radius: 5px; }
.bubble-assistant { display: flex; gap: 10px; background: #4a4a4a; color: #e6e6e6; border-top-left-radius: 5px; }
.message-container.user { justify-content: flex-end; }
    """
    
    return f"<style>{common_style}{theme_style}</style>"

class TalkToKChatWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Talk to K")
        self.set_default_size(500, 680)
        self.set_keep_above(True)
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_border_width(0)
        self.set_icon_name("applications-education")
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0))
        self.set_decorated(False)
        self.set_opacity(0.95)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_window_button_press)
        self.messages = []  # Store (sender, message) tuples for re-rendering
        self.ollama_url = "http://localhost:11434/api/generate"
        self.text_model = "command-r7b"
        
        self.conversation_history = []  # Store conversation for context
        
        # UI state
        self.is_generating = False
        
        Notify.init("Talk to K")

        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Main vertical box
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_vbox.set_vexpand(True)
        main_vbox.set_hexpand(True)
        main_vbox.set_valign(Gtk.Align.FILL)
        main_vbox.set_halign(Gtk.Align.FILL)
        self.add(main_vbox)

        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("Talk to K - In dialogue with Krishnamurti")
        header.set_name("headerbar")
        main_vbox.pack_start(header, False, False, 0)

        # Chat area (scrollable)
        self.chat_listbox = Gtk.ListBox()
        self.chat_listbox.set_name("chat_listbox")
        self.chat_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.chat_listbox.set_vexpand(True)
        self.chat_listbox.set_hexpand(True)
        self.chat_listbox.set_valign(Gtk.Align.FILL)
        self.chat_listbox.set_halign(Gtk.Align.FILL)
        
        chat_scroll = Gtk.ScrolledWindow()
        chat_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        chat_scroll.set_vexpand(True)
        chat_scroll.set_hexpand(True)
        chat_scroll.set_valign(Gtk.Align.FILL)
        chat_scroll.set_halign(Gtk.Align.FILL)
        chat_scroll.add(self.chat_listbox)
        main_vbox.pack_start(chat_scroll, True, True, 0)

        # Prompt suggestions area
        self.suggestions_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.suggestions_container.set_name("suggestions_container")
        
        # Krishnamurti-focused prompt suggestions
        self.all_prompt_suggestions = [
            ("🧘 What is consciousness?", "What is consciousness and how can we understand its true nature?"),
            ("🔓 How do we achieve freedom?", "How can we achieve true freedom from psychological conditioning?"),
            ("💭 What is the nature of thought?", "What is the nature of thought and its role in human conditioning?"),
            ("⏰ What is psychological time?", "What is psychological time and how does it create suffering?"),
            ("🌱 How does transformation happen?", "How does radical transformation of consciousness take place?"),
            ("❤️ What is love without attachment?", "What is love when it is free from attachment and possessiveness?"),
            ("🔍 What does it mean to observe?", "What does it mean to observe without the observer?"),
            ("😌 How do we live without fear?", "How can we live completely without fear and its conditioning?"),
            ("🎯 What is the purpose of education?", "What should be the true purpose and nature of education?"),
            ("🤝 How do we relate without conflict?", "How can human beings relate to each other without conflict?"),
            ("☮️ What creates violence in society?", "What are the roots of violence in human consciousness and society?"),
            ("🌍 How do we change the world?", "How can we bring about a fundamental change in human consciousness?"),
        ]
        
        # Create container for suggestion buttons
        self.suggestions_grid = Gtk.FlowBox()
        self.suggestions_grid.set_name("suggestions_grid")
        self.suggestions_grid.set_valign(Gtk.Align.START)
        self.suggestions_grid.set_max_children_per_line(1)
        self.suggestions_grid.set_column_spacing(8)
        self.suggestions_grid.set_row_spacing(8)
        self.suggestions_grid.set_homogeneous(True)
        self.suggestions_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        
        # Add header for suggestions
        suggestions_header = Gtk.Label("💡 Explore these questions:")
        suggestions_header.set_name("suggestions_header")
        suggestions_header.set_halign(Gtk.Align.START)
        suggestions_header.set_margin_left(12)
        suggestions_header.set_margin_bottom(8)
        
        self.suggestions_container.pack_start(suggestions_header, False, False, 0)
        self.suggestions_container.pack_start(self.suggestions_grid, False, False, 0)
        
        main_vbox.pack_start(self.suggestions_container, False, False, 8)

        # Input area
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        input_box.set_name("inputbox")

        # Replace Entry with TextView for auto-resizing capability
        input_scroll = Gtk.ScrolledWindow()
        input_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        input_scroll.set_min_content_height(36)  # Minimum height
        input_scroll.set_max_content_height(200)  # Maximum height before scrolling
        input_scroll.set_hexpand(True)

        self.input_textview = Gtk.TextView()
        self.input_textview.set_name("input_textview")
        self.input_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.input_textview.set_accepts_tab(False)  # Don't capture tab key
        self.input_textview.set_left_margin(12)
        self.input_textview.set_right_margin(12)
        self.input_textview.set_top_margin(8)
        self.input_textview.set_bottom_margin(8)

        # Get the text buffer
        self.input_buffer = self.input_textview.get_buffer()

        # Connect to buffer changes for auto-resizing
        self.input_buffer.connect("changed", self.on_input_text_changed)

        # Connect key press events for Enter handling
        self.input_textview.connect("key-press-event", self.on_input_key_press)

        # Connect focus events for placeholder handling
        self.input_textview.connect("focus-in-event", self.on_input_focus_in)
        self.input_textview.connect("focus-out-event", self.on_input_focus_out)

        input_scroll.add(self.input_textview)

        # Add placeholder text functionality
        self.placeholder_text = "Ask a question about consciousness, freedom, or the nature of existence..."
        self.is_placeholder_active = True
        self.setup_placeholder()

        # Create a stack for Send/Stop buttons
        self.button_stack = Gtk.Stack()
        self.button_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        send_button = Gtk.Button(label="Send")
        send_button.set_name("send_button")
        send_button.connect("clicked", self.on_send_clicked)
        self.button_stack.add_named(send_button, "send")

        stop_button = Gtk.Button(label="Stop")
        stop_button.set_name("stop_button")
        stop_button.connect("clicked", self.on_stop_clicked)
        self.button_stack.add_named(stop_button, "stop")

        # Create a Settings button
        settings_button = Gtk.Button(label="Settings")
        settings_button.set_name("settings_button")
        settings_button.connect("clicked", self.on_settings_clicked)
        input_box.pack_start(settings_button, False, False, 0)

        # Create a Reset button
        reset_button = Gtk.Button(label="Reset")
        reset_button.set_name("reset_button")
        reset_button.connect("clicked", self.on_reset_clicked)
        input_box.pack_start(reset_button, False, False, 0)

        input_box.pack_start(input_scroll, True, True, 0)
        input_box.pack_start(self.button_stack, False, False, 0)
        main_vbox.pack_start(input_box, False, False, 0)

        # Create initial random suggestions
        self.create_random_suggestions()

        # Welcome message (always show on startup)
        welcome_msg = ("Welcome. You are entering into a dialogue with understanding itself. "
                      "Here we may explore together the nature of consciousness, the movement of thought, "
                      "and what it means to live without the burden of psychological time. "
                      "What questions arise in you about the nature of existence?")
        self.append_message("assistant", welcome_msg)
        self.update_app_theme()
        self.show_all()

    def update_app_theme(self):
        """Apply dark theme with purple accents for Talk to K"""
        css = """
        window {
            background: radial-gradient(circle at center, #2d1b69 0%, #1a1a2e 100%);
        }
        
        #headerbar {
            background: linear-gradient(135deg, #6b46c1 0%, #553c9a 100%);
            color: white;
            border: none;
        }
        
        #chat_listbox {
            background: transparent;
            border: none;
        }
        
        #input_textview {
            background: rgba(255, 255, 255, 0.1);
            color: #e2e8f0;
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 20px;
            padding: 12px 16px;
            font-size: 14px;
        }
        
        #input_textview text {
            background: rgba(255, 255, 255, 0.1);
            color: #e2e8f0;
        }
        
        #inputbox scrolledwindow {
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(139, 92, 246, 0.3);
        }
        
        #send_button, #stop_button {
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 12px 20px;
            font-weight: bold;
        }
        
        #send_button:hover, #stop_button:hover {
            background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
        }
        
        #settings_button, #reset_button {
            background: rgba(255, 255, 255, 0.1);
            color: #e2e8f0;
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 18px;
            padding: 10px;
        }
        
        #settings_button:hover, #reset_button:hover {
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid #8b5cf6;
        }
        
        #suggestions_container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 12px;
            margin: 0 12px;
        }
        
        #suggestions_header {
            color: #c4b5fd;
            font-weight: bold;
            font-size: 16px;
        }
        
        .suggestion_button {
            background: rgba(139, 92, 246, 0.1);
            color: #e2e8f0;
            border: 1px solid rgba(139, 92, 246, 0.2);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 13px;
        }
        
        .suggestion_button:hover {
            background: rgba(139, 92, 246, 0.2);
            border: 1px solid #8b5cf6;
        }
        """
        
        self.css_provider.load_from_data(css.encode())

    def on_window_button_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def append_message(self, sender, message):
        print(f"append_message called with sender={sender}, message={message}")
        self.messages.append((sender, message))
        self._append_message_no_store(sender, message)

    def append_streaming_message(self, sender, message):
        """Append a message that can be updated in real-time for streaming"""
        print(f"append_streaming_message called with sender={sender}, message={message}")
        self.messages.append((sender, message))
        self._append_streaming_message_no_store(sender, message)

    def _append_streaming_message_no_store(self, sender, message):
        """Append a message with WebView that can be updated for streaming"""
        print(f"_append_streaming_message_no_store called with sender={sender}, message={message}")
        row = Gtk.ListBoxRow()
        row.set_selectable(False)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        webview = WebKit2.WebView()
        webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
        webview.set_size_request(-1, 1)  # Let it shrink to fit
        
        # Store reference for streaming updates
        self.streaming_webview = webview

        html_content = markdown.markdown(safe_decode(message))
        full_style = get_improved_css_styles()

        if sender == 'user':
            body_html = f"""
              <div class="message-container user">
                <div class="bubble bubble-user"><div class="text">{html_content}</div></div>
                <div class="avatar">👤</div>
              </div>
            """
        else: # assistant
            body_html = f"""
              <div class="message-container assistant">
                <div class="bubble bubble-assistant">
                  <div class="avatar">🧘</div>
                  <div class="text">{html_content}</div>
                </div>
              </div>
            """
        
        html = f'<html><head><meta charset="UTF-8">{full_style}</head><body>{body_html}</body></html>'
        
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
            try:
                value = webview.run_javascript_finish(result)
                js_result = value.get_js_value()
                height = js_result.to_int32()
                print(f"Setting WebView height to: {height}")
                webview.set_size_request(-1, height)
            except Exception as e:
                print(f"Error setting height: {e}")

        webview.connect("load-changed", on_load_changed)

        hbox.pack_start(webview, True, True, 0)
        
        row.add(hbox)
        self.chat_listbox.add(row)
        self.chat_listbox.show_all()
        adj = self.chat_listbox.get_parent().get_vadjustment()
        GLib.idle_add(adj.set_value, adj.get_upper())

    def _append_message_no_store(self, sender, message):
        print(f"_append_message_no_store called with sender={sender}, message={message}")
        row = Gtk.ListBoxRow()
        row.set_selectable(False)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        webview = WebKit2.WebView()
        webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
        webview.set_size_request(-1, 1)  # Let it shrink to fit

        html_content = markdown.markdown(safe_decode(message))
        full_style = get_improved_css_styles()

        if sender == 'user':
            body_html = f"""
              <div class="message-container user">
                <div class="bubble bubble-user"><div class="text">{html_content}</div></div>
                <div class="avatar">👤</div>
              </div>
            """
        else: # assistant
            body_html = f"""
              <div class="message-container assistant">
                <div class="bubble bubble-assistant">
                  <div class="avatar">🧘</div>
                  <div class="text">{html_content}</div>
                </div>
              </div>
            """
        
        html = f'<html><head><meta charset="UTF-8">{full_style}</head><body>{body_html}</body></html>'
        
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

        hbox.pack_start(webview, True, True, 0)
        
        row.add(hbox)
        self.chat_listbox.add(row)
        self.chat_listbox.show_all()
        adj = self.chat_listbox.get_parent().get_vadjustment()
        GLib.idle_add(adj.set_value, adj.get_upper())

    def on_send_clicked(self, widget):
        text_buffer = self.input_textview.get_buffer()
        user_text = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True).strip()
        
        # Don't send if it's just placeholder text or empty
        if not user_text or self.is_placeholder_active or user_text == self.placeholder_text or self.is_generating:
            return
        
        self.is_generating = True
        self.button_stack.set_visible_child_name("stop")
        self.input_textview.set_sensitive(False)

        # Hide suggestions after any message is sent (suggestion or manual)
        self.suggestions_container.hide()

        self.append_message("user", user_text)
        text_buffer.set_text("")
        self.setup_placeholder()  # Reset placeholder after clearing
        
        # Add streaming message and prepare for real-time updates
        self.streaming_response = ""  # Initialize streaming response buffer
        self.append_streaming_message("assistant", "🤔 Reflecting...")
        
        # Store the last row (the thinking message) for updating
        self.thinking_row = self.chat_listbox.get_row_at_index(len(self.chat_listbox.get_children()) - 1)
        
        threading.Thread(target=self.handle_user_query, args=(user_text,), daemon=True).start()

    def on_stop_clicked(self, widget):
        if not self.is_generating:
            return
        
        self.is_generating = False
        # The thread will see is_generating is false and discard its result
        
        # Update UI immediately
        self.messages[-1] = ("assistant", "Generation stopped.")
        self.update_message(self.thinking_row, "assistant", "Generation stopped.")
        
        self._restore_input_state()

    def _restore_input_state(self):
        """Restore the input widgets to their default state."""
        self.is_generating = False
        self.button_stack.set_visible_child_name("send")
        self.input_textview.set_sensitive(True)

    def is_new_topic(self, user_text):
        new_topic_starters = [
            "who is", "what about", "tell me about", "explain", "define", "give me information on", "describe"
        ]
        user_text_lower = user_text.strip().lower()
        return any(user_text_lower.startswith(starter) for starter in new_topic_starters)

    def handle_user_query(self, user_text):
        # If the user starts a new topic, reset the conversation history except for the system prompt
        if self.is_new_topic(user_text):
            self.conversation_history = []
        
        self.conversation_history.append({"role": "user", "content": user_text})
        
        response = self.generate_response()
        
        if self.is_generating: # Check if stop was clicked
            self.conversation_history.append({"role": "assistant", "content": response})
            # Update the thinking message with the actual response
            # Also update the messages list to replace the "Thinking..." message
            if self.messages and self.messages[-1][1] in ["🤔 Reflecting..."]:
                self.messages[-1] = ("assistant", response)
            # Only update if we haven't been streaming (for non-streaming responses)
            if not hasattr(self, 'streaming_response') or not self.streaming_response:
                GLib.idle_add(self.update_message, self.thinking_row, "assistant", response)
        
        GLib.idle_add(self._restore_input_state)

    def build_prompt(self):
        prompt = KRISHNAMURTI_SYSTEM_PROMPT + "\n\n"
        # Only include the last 2 user-assistant pairs for context
        history = []
        count = 0
        for msg in reversed(self.conversation_history):
            if msg["role"] == "assistant" or msg["role"] == "user":
                history.append(msg)
                if msg["role"] == "user":
                    count += 1
                if count == 2:
                    break
        for msg in reversed(history):
            if msg["role"] == "user":
                prompt += f"Human: {msg['content']}\n"
            else:
                prompt += f"Krishnamurti: {msg['content']}\n"
        prompt += "Krishnamurti:"
        return prompt

    def generate_response(self, prompt_override=None):
        try:
            prompt = prompt_override if prompt_override is not None else self.build_prompt()
            
            # Always use text model for final response
            data = {
                "model": self.text_model,
                "prompt": prompt,
                "stream": True
            }
            
            response = requests.post(self.ollama_url, json=data, stream=True)
            print(f"Response status code: {response.status_code}")
            if response.status_code != 200:
                print(f"Response text: {response.text}")
                return f"Error: HTTP {response.status_code} - {response.text}"
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if not self.is_generating:  # Check if stop was clicked
                        break
                    if line:
                        try:
                            json_response = json.loads(line.decode('utf-8'))
                            chunk = json_response.get("response", "")
                            if chunk:
                                full_response += chunk
                                print(f"Streaming chunk: {chunk[:50]}...")  # Debug print
                                # Update UI in real-time during streaming
                                GLib.idle_add(self.update_streaming_message, chunk)
                            
                            # Check if this is the final chunk
                            if json_response.get("done", False):
                                break
                        except Exception as e:
                            print(f"Error parsing JSON line: {e}")
                            continue
                return full_response if full_response else "(No response)"
            return "Error: Could not generate response"
        except Exception as e:
            return f"Error: {str(e)}"

    def update_streaming_message(self, chunk):
        """Update the streaming message with new chunk of text"""
        print(f"update_streaming_message called with chunk: {chunk[:30]}...")
        if not self.is_generating:
            print("Not generating, returning")
            return
        
        self.streaming_response += chunk
        print(f"Total streaming response so far: {len(self.streaming_response)} chars")
        # Update the UI with JavaScript injection for better performance
        self.update_streaming_webview(self.streaming_response)
        # Also update the messages list
        if self.messages and self.messages[-1][0] == "assistant":
            self.messages[-1] = ("assistant", self.streaming_response)

    def update_streaming_webview(self, full_text):
        """Update the streaming WebView using JavaScript for better performance"""
        if hasattr(self, 'streaming_webview') and self.streaming_webview:
            try:
                # Convert markdown to HTML
                html_content = markdown.markdown(safe_decode(full_text))
                # Properly escape for JavaScript string literal
                escaped_html = html_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                # Update the content using JavaScript and then recalculate height
                js_code = f'''
                var textElement = document.querySelector(".text");
                if (textElement) {{
                    textElement.innerHTML = "{escaped_html}";
                }}
                document.body.scrollHeight;
                '''
                print(f"Executing JS: {js_code[:100]}...")  # Debug print
                self.streaming_webview.run_javascript(
                    js_code, 
                    None, 
                    lambda webview, result, user_data: self.update_streaming_height(webview, result),
                    None
                )
            except Exception as e:
                print(f"Error updating streaming webview: {e}")

    def update_streaming_height(self, webview, result):
        """Update the height of the streaming WebView after content change"""
        try:
            value = webview.run_javascript_finish(result)
            js_result = value.get_js_value()
            height = js_result.to_int32()
            print(f"Updating streaming WebView height to: {height}")
            webview.set_size_request(-1, height)
            # Scroll to bottom to follow the streaming text
            adj = self.chat_listbox.get_parent().get_vadjustment()
            GLib.idle_add(adj.set_value, adj.get_upper())
        except Exception as e:
            print(f"Error updating streaming height: {e}")

    def update_message(self, row, sender, message):
        """Update an existing message row with new content"""
        # Remove the old content
        for child in row.get_children():
            row.remove(child)
        
        # Add new content
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        webview = WebKit2.WebView()
        webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
        webview.set_size_request(-1, 1)  # Let it shrink to fit

        html_content = markdown.markdown(safe_decode(message))
        full_style = get_improved_css_styles()

        if sender == 'user':
            body_html = f"""
              <div class="message-container user">
                <div class="bubble bubble-user"><div class="text">{html_content}</div></div>
                <div class="avatar">👤</div>
              </div>
            """
        else: # assistant
            body_html = f"""
              <div class="message-container assistant">
                <div class="bubble bubble-assistant">
                  <div class="avatar">🧘</div>
                  <div class="text">{html_content}</div>
                </div>
              </div>
            """
        
        html = f'<html><head><meta charset="UTF-8">{full_style}</head><body>{body_html}</body></html>'
        
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

        hbox.pack_start(webview, True, True, 0)
        
        row.add(hbox)
        row.show_all()
        adj = self.chat_listbox.get_parent().get_vadjustment()
        GLib.idle_add(adj.set_value, adj.get_upper())

    def on_settings_clicked(self, widget):
        """Handle the settings button click event."""
        dialog = Gtk.Dialog(
            title="Talk to K Settings",
            transient_for=self,
            flags=0
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_size_request(400, 200)
        
        content_area = dialog.get_content_area()
        content_area.set_spacing(12)
        content_area.set_margin_left(12)
        content_area.set_margin_right(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)
        
        # Model selection
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        model_label = Gtk.Label("AI Model:")
        model_label.set_halign(Gtk.Align.START)
        model_entry = Gtk.Entry()
        model_entry.set_text(self.text_model)
        model_box.pack_start(model_label, False, False, 0)
        model_box.pack_start(model_entry, True, True, 0)
        content_area.pack_start(model_box, False, False, 0)
        
        # Info label
        info_label = Gtk.Label("This dialogue uses the wisdom and teachings of Jiddu Krishnamurti\nto explore consciousness, freedom, and the nature of existence.")
        info_label.set_justify(Gtk.Justification.CENTER)
        content_area.pack_start(info_label, False, False, 0)
        
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Save settings
            self.text_model = model_entry.get_text()
            print(f"Model updated to: {self.text_model}")
            
        dialog.destroy()

    def on_reset_clicked(self, widget):
        """Handle the reset button click event."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text="Are you sure you want to reset the conversation?",
        )
        dialog.format_secondary_text(
            "This will clear the current conversation and start a new session."
        )
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            self.conversation_history.clear()
            self.messages.clear()
            self.chat_listbox.foreach(lambda widget: self.chat_listbox.remove(widget))
            welcome_msg = ("We begin again, as if for the first time. "
                          "In this space of inquiry, what questions naturally arise about the nature of consciousness, "
                          "about freedom, about the very ground of existence itself?")
            self.append_message("assistant", welcome_msg)
            # Show suggestions again after reset with new random selection
            self.create_random_suggestions()
            self.suggestions_container.show_all()
        dialog.destroy()

    def on_input_text_changed(self, buffer):
        # Implement placeholder functionality
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        if text == "":
            # Text is empty, show placeholder
            if not self.is_placeholder_active:
                self.is_placeholder_active = True
                buffer.set_text(self.placeholder_text)
        elif text == self.placeholder_text:
            # Text is placeholder, mark as placeholder active
            self.is_placeholder_active = True
        else:
            # Text is actual content
            self.is_placeholder_active = False

    def on_input_key_press(self, widget, event):
        # Handle Enter key (send message)
        if event.keyval == Gdk.KEY_Return or event.keyval == Gdk.KEY_KP_Enter:
            if not (event.state & Gdk.ModifierType.SHIFT_MASK):  # Enter without Shift
                self.on_send_clicked(widget)
                return True  # Consume the event
        
        # Clear placeholder when typing
        if self.is_placeholder_active:
            buffer = widget.get_buffer()
            if event.keyval not in [Gdk.KEY_Tab, Gdk.KEY_Shift_L, Gdk.KEY_Shift_R, 
                                   Gdk.KEY_Control_L, Gdk.KEY_Control_R, Gdk.KEY_Alt_L, Gdk.KEY_Alt_R]:
                buffer.set_text("")
                self.is_placeholder_active = False
        
        return False

    def on_input_focus_in(self, widget, event):
        # Clear placeholder when focusing in
        if self.is_placeholder_active:
            buffer = widget.get_buffer()
            text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
            if text == self.placeholder_text:
                buffer.set_text("")
                self.is_placeholder_active = False
        return False

    def on_input_focus_out(self, widget, event):
        # Show placeholder when focusing out if empty
        buffer = widget.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True).strip()
        if text == "":
            buffer.set_text(self.placeholder_text)
            self.is_placeholder_active = True
        return False

    def setup_placeholder(self):
        # Initialize placeholder functionality
        buffer = self.input_textview.get_buffer()
        buffer.set_text(self.placeholder_text)
        self.is_placeholder_active = True

    def create_random_suggestions(self):
        """Create 3 random suggestion buttons from the available prompts."""
        # Clear existing suggestions
        for child in self.suggestions_grid.get_children():
            self.suggestions_grid.remove(child)
        
        # Randomly select 3 suggestions
        selected_suggestions = random.sample(self.all_prompt_suggestions, 3)
        
        # Create buttons for the selected suggestions
        for display_text, full_prompt in selected_suggestions:
            suggestion_button = Gtk.Button()
            suggestion_button.set_name("suggestion_button")
            suggestion_button.set_relief(Gtk.ReliefStyle.NONE)
            
            # Create label with text wrapping
            label = Gtk.Label(display_text)
            label.set_name("suggestion_label")
            label.set_line_wrap(True)
            label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            label.set_max_width_chars(35)  # Increased since we have more space with 3 buttons
            label.set_justify(Gtk.Justification.CENTER)
            suggestion_button.add(label)
            
            # Connect click handler
            suggestion_button.connect("clicked", self.on_suggestion_clicked, full_prompt)
            self.suggestions_grid.add(suggestion_button)
        
        # Show all the new buttons
        self.suggestions_grid.show_all()

    def on_suggestion_clicked(self, widget, full_prompt):
        """Handle suggestion button click by filling input and sending the message."""
        if self.is_generating:
            return
            
        # Fill the input with the suggestion
        self.input_buffer.set_text(full_prompt)
        self.is_placeholder_active = False
        
        # Automatically send the message (suggestions will be hidden in on_send_clicked)
        self.on_send_clicked(widget)

def main():
    win = TalkToKChatWidget()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()

if __name__ == "__main__":
    main() 