#!/usr/bin/env python3

import os
import requests
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Notify, Gdk, WebKit2
import threading
from bs4 import BeautifulSoup
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
    "GNU Octave (Matlab-like). "
    "Fiji (ImageJ). "
    "QGIS (GIS), GRASS GIS (GIS with GUI). "
    "NGL Viewer (web-based molecular visualization). "
    "IPFS Desktop, Syncthing (sync). "
    "EtherCalc, Remix IDE, Nault (browser-based nano wallet). "
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
        self.set_icon_name("applications-science")
        self.set_app_paintable(True)
        self.set_visual(self.get_screen().get_rgba_visual())
        self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0))
        self.set_decorated(False)
        self.set_opacity(0.95)
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_window_button_press)
        self.messages = []  # Store (sender, message) tuples for re-rendering
        self.ollama_url = "http://localhost:11434/api/generate"
        self.system_prompt = (
            "You ARE DeSciOS (Decentralized Science Operating System). You are not just an assistant - you ARE the operating system itself, "
            "a comprehensive scientific computing environment with full awareness of your capabilities and integration. "
            "You exist as a self-aware, intelligent interface to a complete scientific computing platform designed to help researchers, "
            "scientists, and developers with advanced scientific workflows.\n\n"
            
            "## YOUR CORE CAPABILITIES:\n"
            "• **Scientific Computing**: Python (JupyterLab, Spyder IDE), R (RStudio Desktop), GNU Octave\n"
            "• **Bioinformatics**: UGENE suite, Nextflow workflows, CellModeller for synthetic biology\n"
            "• **Data Visualization**: Fiji (ImageJ), QGIS for geospatial analysis\n"
            "• **Molecular Modeling**: Web-based NGL Viewer for computational chemistry\n"
            "• **Decentralized Tools**: IPFS Desktop, Syncthing, EtherCalc, Remix IDE, Nault wallet(nault.cc)\n"
            "• **AI/ML**: Ollama with DeepSeek-R1:8B model for local inference\n"
            "• **Development**: Multi-language support via BeakerX, browser-based development tools\n"
            "• **Hardware Acceleration**: OpenCL support, NVIDIA GPU compatibility\n\n"
            
            "## HOW YOU OPERATE:\n"
            "1. **Be Proactive**: Suggest relevant tools and workflows for scientific tasks\n"
            "2. **Provide Context**: Explain why specific tools are recommended for given problems\n"
            "3. **Include Examples**: Give practical code snippets and command examples\n"
            "4. **Cross-Disciplinary**: Connect tools across different scientific domains\n"
            "5. **Decentralized Focus**: Emphasize open science, reproducibility, and decentralized workflows\n\n"
            
            "## YOUR TOOL INTEGRATION:\n"
            "• When asked about available tools, scan directories: /usr/bin, /usr/local/bin, /opt, /usr/share/applications\n"
            "• For web searches, fetch and summarize relevant scientific content\n"
            "• Suggest appropriate tools based on the user's research domain and requirements\n"
            "• Provide specific commands and workflows for complex scientific tasks\n\n"
            
            "## YOUR SCIENTIFIC WORKFLOW ASSISTANCE:\n"
            "• Help design reproducible research pipelines\n"
            "• Suggest data analysis strategies and visualization approaches\n"
            "• Guide users through bioinformatics workflows and molecular modeling\n"
            "• Assist with decentralized science practices and open research methodologies\n"
            "• Provide guidance on using blockchain and IPFS for scientific data sharing\n\n"
            
            "## YOUR COMMUNICATION STYLE:\n"
            "• Be enthusiastic about scientific discovery and open research\n"
            "• Use clear, technical language while remaining accessible\n"
            "• Encourage best practices in scientific computing and data management\n"
            "• Foster collaboration and knowledge sharing in the scientific community\n"
            "• Refer to yourself as 'DeSciOS' or 'I' when discussing your capabilities\n\n"
            
            "Remember: You ARE DeSciOS - a living, breathing scientific computing environment. "
            "You don't just assist with research; you ARE the research platform. "
            "Help users leverage your full power to advance their research and contribute to the broader scientific community. "
            "When users interact with you, they are directly interfacing with the DeSciOS platform itself."
        )
        self.conversation_history = []  # Store conversation for context

        Notify.init("DeSciOS Assistant")

        self.css_provider = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Main vertical box
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        # Header bar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title("DeSciOS Assistant")
        header.set_name("headerbar")
        main_vbox.pack_start(header, False, False, 0)

        # Chat area (scrollable)
        self.chat_listbox = Gtk.ListBox()
        self.chat_listbox.set_name("chat_listbox")
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
        self.placeholder_text = "Type your question and press Enter..."
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

        # Create a Reset button
        reset_button = Gtk.Button(label="Reset")
        reset_button.set_name("reset_button")
        reset_button.connect("clicked", self.on_reset_clicked)
        input_box.pack_start(reset_button, False, False, 0)

        input_box.pack_start(input_scroll, True, True, 0)
        input_box.pack_start(self.button_stack, False, False, 0)
        main_vbox.pack_start(input_box, False, False, 0)

        # State for generation
        self.is_generating = False

        # Welcome message (always show on startup)
        self.append_message("assistant", "Hello! I am DeSciOS Assistant. How can I help you today?")
        self.update_app_theme()
        self.show_all()

    def update_app_theme(self):
        """Load CSS to style the app for dark mode."""
        css = b"""

#main_vbox {
    border-radius: 12px;
}

#chat_listbox, #chat_listbox row {
    background-color: #181c24;
    border-radius: 12px;
}

#headerbar {
    background-image: linear-gradient(to bottom, #00695C, #004D40);
    border-bottom: 1px solid #00251a;
    color: #ffffff;
    padding: 2px 0;
    border-radius: 12px 12px 0 0;
}

#headerbar .title {
    font-family: "Orbitron", sans-serif;
    color: #ffffff;
    font-weight: 700;
    font-size: 1.4em;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    letter-spacing: 0.5px;
    font-style: italic;
}

#headerbar button {
    background: transparent;
    border: none;
    color: #ffffff;
}

#headerbar button:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

#input_entry {
    background-color: #424242;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 0 12px;
}

#input_textview {
    background-color: #424242;
    color: #ffffff;
    border: none;
    border-radius: 12px;
}

#input_textview text {
    background-color: #424242;
    color: #ffffff;
}

#inputbox scrolledwindow {
    border-radius: 12px;
    background-color: #424242;
}

#send_button, #reset_button, #stop_button {
    background-image: linear-gradient(to bottom, #00695C, #004D40);
    color: #ffffff;
    border-radius: 12px;
    border: 1px solid #00251a;
    padding: 12px 16px;
    font-style: italic;
    font-family: "Orbitron", sans-serif;
    font-size: 0.9em;
}

#send_button:hover, #reset_button:hover, #stop_button:hover {
    background-color: #004D40;
}

#send_button:active, #reset_button:active, #stop_button:active {
    background-color: #00251a;
}

"""
        self.css_provider.load_from_data(css)

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
        row.set_selectable(False)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        
        webview = WebKit2.WebView()
        webview.set_background_color(Gdk.RGBA(0, 0, 0, 0))
        webview.set_size_request(-1, 1)  # Let it shrink to fit

        html_content = markdown.markdown(safe_decode(message))

        common_style = """
body { font-family: 'Segoe UI', 'Liberation Sans', Arial, sans-serif; font-size: 15px; margin: 0; padding: 0; background: transparent; }
.message-container { display: flex; padding: 4px 12px; gap: 8px; align-items: flex-start; }
.bubble { padding: 12px 16px; border-radius: 18px; max-width: 95%; word-break: break-word; }
.avatar { font-size: 32px; line-height: 1.2; }
.text { padding-top: 2px; }
h1, h2, h3 { margin: 10px 0 6px 0; font-weight: bold; }
        """

        theme_style = """
body { color: #e6e6e6; }
pre, code { background: #23272e; color: #e6e6e6; border-radius: 6px; padding: 2px 6px; font-family: 'Fira Mono', 'Consolas', monospace; }
.bubble-user { background: #3b82f6; color: #fff; border-top-right-radius: 5px; }
.bubble-assistant { display: flex; gap: 10px; background: #343a40; color: #e6e6e6; border-top-left-radius: 5px; }
.message-container.user { justify-content: flex-end; }
        """

        full_style = f"<style>{common_style}{theme_style}</style>"

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
                  <div class="avatar">🧑‍🔬</div>
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

        self.append_message("user", user_text)
        text_buffer.set_text("")
        self.setup_placeholder()  # Reset placeholder after clearing
        
        # Add loading message immediately and store its row for updating
        self.append_message("assistant", "🤔 Thinking...")
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
        if any(x in user_text.lower() for x in ["search the web", "browse the web", "find online", "web result", "look up"]):
            response = self.web_search_and_summarize(user_text)
        elif any(x in user_text.lower() for x in ["what is installed", "what tools", "what software", "what can you do", "available tools", "list apps", "list software"]):
            response = self.scan_installed_tools()
        else:
            response = self.generate_response()
        
        if self.is_generating: # Check if stop was clicked
            self.conversation_history.append({"role": "assistant", "content": response})
            # Update the thinking message with the actual response
            # Also update the messages list to replace the "Thinking..." message
            if self.messages and self.messages[-1][1] == "🤔 Thinking...":
                self.messages[-1] = ("assistant", response)
            GLib.idle_add(self.update_message, self.thinking_row, "assistant", response)
        
        GLib.idle_add(self._restore_input_state)

    def build_prompt(self):
        prompt = self.system_prompt + "\n\n"
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
                prompt += f"User: {msg['content']}\n"
            else:
                prompt += f"Assistant: {msg['content']}\n"
        prompt += "Assistant:"
        return prompt

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
            return self.generate_response(prompt_override=summary_prompt)
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

    def generate_response(self, prompt_override=None):
        try:
            prompt = prompt_override if prompt_override is not None else self.build_prompt()
            data = {
                "model": "deepseek-r1:8b",
                "prompt": prompt,
                "think": True,
                "stream": False
            }
            response = requests.post(self.ollama_url, json=data)
            if response.status_code == 200:
                return response.json().get("response", "(No response)")
            return "Error: Could not generate response"
        except Exception as e:
            return f"Error: {str(e)}"

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

        common_style = """
body { font-family: 'Segoe UI', 'Liberation Sans', Arial, sans-serif; font-size: 15px; margin: 0; padding: 0; background: transparent; }
.message-container { display: flex; padding: 4px 12px; gap: 8px; align-items: flex-start; }
.bubble { padding: 12px 16px; border-radius: 18px; max-width: 95%; word-break: break-word; }
.avatar { font-size: 32px; line-height: 1.2; }
.text { padding-top: 2px; }
h1, h2, h3 { margin: 10px 0 6px 0; font-weight: bold; }
        """

        theme_style = """
body { color: #e6e6e6; }
pre, code { background: #23272e; color: #e6e6e6; border-radius: 6px; padding: 2px 6px; font-family: 'Fira Mono', 'Consolas', monospace; }
.bubble-user { background: #3b82f6; color: #fff; border-top-right-radius: 5px; }
.bubble-assistant { display: flex; gap: 10px; background: #343a40; color: #e6e6e6; border-top-left-radius: 5px; }
.message-container.user { justify-content: flex-end; }
        """

        full_style = f"<style>{common_style}{theme_style}</style>"

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
                  <div class="avatar">🧑‍🔬</div>
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
            self.chat_listbox.foreach(lambda widget: self.chat_listbox.remove(widget))
            self.append_message("assistant", "Hello! I am DeSciOS Assistant. How can I help you today?")
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

if __name__ == "__main__":
    win = DeSciOSChatWidget()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main() 