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
import subprocess
import shlex

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
            "When asked to browse the web, fetch and summarize the relevant web content. "
            "You can execute Linux commands with user consent. Users can request commands in two ways:\n"
            "1. Explicit commands: 'run command: ls -la', 'execute: pwd', or 'run: `whoami`'\n"
            "2. Natural language: 'show me the files', 'what's my current directory', 'check disk usage', 'who am i', 'system info', 'memory usage', 'find files', etc.\n"
            "For natural language requests, you will suggest appropriate commands and explain what they do before asking for user confirmation. "
            "Always ask for user confirmation before executing any command for security reasons."
        )
        self.conversation_history = []  # Store conversation for context

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

    def show_command_confirmation(self, command):
        """Show a dialog asking for user consent to execute a command"""
        dialog = Gtk.Dialog(title="Command Execution Confirmation", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_default_size(400, 200)
        
        content_area = dialog.get_content_area()
        
        # Warning label
        warning_label = Gtk.Label()
        warning_label.set_markup("<span foreground='red'><b>⚠️ Security Warning</b></span>")
        warning_label.set_margin_top(10)
        warning_label.set_margin_bottom(10)
        content_area.pack_start(warning_label, False, False, 0)
        
        # Command display
        command_label = Gtk.Label()
        command_label.set_markup(f"<b>Command to execute:</b>\n<tt>{command}</tt>")
        command_label.set_line_wrap(True)
        command_label.set_margin_bottom(10)
        content_area.pack_start(command_label, False, False, 0)
        
        # Explanation
        explanation_label = Gtk.Label()
        explanation_label.set_markup("This will execute the command in your system. Only proceed if you trust this command.")
        explanation_label.set_line_wrap(True)
        explanation_label.set_margin_bottom(10)
        content_area.pack_start(explanation_label, False, False, 0)
        
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        
        return response == Gtk.ResponseType.OK

    def execute_command(self, command):
        """Execute a command and return the output"""
        try:
            # Use shlex to properly split the command
            args = shlex.split(command)
            result = subprocess.run(args, capture_output=True, text=True, timeout=30)
            
            output = []
            if result.stdout:
                output.append(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                output.append(f"STDERR:\n{result.stderr}")
            if result.returncode != 0:
                output.append(f"Exit code: {result.returncode}")
            
            return "\n".join(output) if output else "Command executed successfully (no output)"
            
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except FileNotFoundError:
            return f"Error: Command '{args[0] if args else command}' not found"
        except Exception as e:
            return f"Error executing command: {str(e)}"

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
.bubble-user {
  background: #3b82f6;
  color: #fff;
  margin-left: auto;
  float: right;
  clear: both;
}
.bubble-assistant {
  background: #23272e;
  color: #e6e6e6;
  margin-right: auto;
  float: left;
  clear: both;
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
.bubble-user {
  background: #3b82f6;
  color: #fff;
  margin-left: auto;
  float: right;
  clear: both;
}
.bubble-assistant {
  background: #e6e6e6;
  color: #23272e;
  margin-right: auto;
  float: left;
  clear: both;
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
        
        # Check if this is a command request first
        if self.is_command_request(user_text):
            # For command requests, don't show "Thinking..." immediately
            threading.Thread(target=self.handle_user_query, args=(user_text,), daemon=True).start()
        else:
            # Add loading message immediately for other requests
            self.append_message("assistant", "Thinking...")
            threading.Thread(target=self.handle_user_query, args=(user_text,), daemon=True).start()

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
        
        # Check if this is a command execution request
        if self.is_command_request(user_text):
            response = self.handle_command_request(user_text)
            # Remove the "Thinking..." message if it exists
            if self.messages and self.messages[-1][1] == "Thinking...":
                self.messages.pop()
                # Remove the last row from the chat listbox
                children = self.chat_listbox.get_children()
                if len(children) > 0:
                    last_row = children[-1]
                    self.chat_listbox.remove(last_row)
        elif any(x in user_text.lower() for x in ["search the web", "browse the web", "find online", "web result", "look up"]):
            response = self.web_search_and_summarize(user_text)
        elif any(x in user_text.lower() for x in ["what is installed", "what tools", "what software", "what can you do", "available tools", "list apps", "list software"]):
            response = self.scan_installed_tools()
        else:
            response = self.generate_response()
        
        # Only append response if it's not a command request (command responses are handled separately)
        if not self.is_command_request(user_text):
            self.conversation_history.append({"role": "assistant", "content": response})
            GLib.idle_add(self.append_message, "assistant", response)

    def is_command_request(self, user_text):
        """Check if the user is requesting to execute a command"""
        command_indicators = [
            "run command", "execute command", "run this command", "execute this command",
            "run the command", "execute the command", "run:", "execute:", "command:",
            "run `", "execute `", "run:", "execute:"
        ]
        
        # Natural language command requests
        natural_indicators = [
            "show me", "display", "list", "check", "find", "search for", "get", "run",
            "what's in", "what files", "show files", "list files", "check if",
            "how much space", "disk usage", "memory usage", "cpu usage",
            "network status", "processes", "running processes", "system info",
            "current directory", "working directory", "where am i", "pwd",
            "who am i", "current user", "logged in as", "user info"
        ]
        
        user_text_lower = user_text.lower()
        
        # Check for explicit command indicators
        if any(indicator in user_text_lower for indicator in command_indicators):
            return True
            
        # Check for natural language requests that likely need command execution
        if any(indicator in user_text_lower for indicator in natural_indicators):
            # But exclude general questions that don't need commands
            exclude_phrases = [
                "what is", "what are", "how to", "explain", "tell me about",
                "what does", "what do", "how do", "why", "when", "where"
            ]
            if not any(exclude in user_text_lower for exclude in exclude_phrases):
                return True
                
        return False

    def extract_command(self, user_text):
        """Extract the actual command from the user's text"""
        # Look for commands in backticks
        if '`' in user_text:
            start = user_text.find('`') + 1
            end = user_text.find('`', start)
            if end != -1:
                return user_text[start:end].strip()
        
        # Look for commands after "run:" or "execute:"
        for prefix in ["run:", "execute:", "command:"]:
            if prefix in user_text.lower():
                parts = user_text.split(prefix, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # If no clear indicator, try to extract after common phrases
        for phrase in ["run command", "execute command", "run this command", "execute this command"]:
            if phrase in user_text.lower():
                parts = user_text.lower().split(phrase, 1)
                if len(parts) > 1:
                    return parts[1].strip()
        
        # If no explicit command found, suggest one based on natural language
        return self.suggest_command_from_natural_language(user_text)

    def suggest_command_from_natural_language(self, user_text):
        """Suggest appropriate commands based on natural language requests"""
        user_text_lower = user_text.lower()
        
        # File and directory operations
        if any(phrase in user_text_lower for phrase in ["show me", "display", "list"]) and any(phrase in user_text_lower for phrase in ["files", "directory", "folder", "what's in"]):
            if "current" in user_text_lower or "here" in user_text_lower:
                return "ls -la"
            else:
                return "ls -la"
        
        if "current directory" in user_text_lower or "working directory" in user_text_lower or "where am i" in user_text_lower or "pwd" in user_text_lower:
            return "pwd"
        
        # System information
        if "system info" in user_text_lower or "system information" in user_text_lower:
            return "uname -a"
        
        if "disk usage" in user_text_lower or "how much space" in user_text_lower or "space" in user_text_lower:
            return "df -h"
        
        if "memory usage" in user_text_lower or "memory" in user_text_lower:
            return "free -h"
        
        if "cpu usage" in user_text_lower or "cpu" in user_text_lower:
            return "top -bn1 | grep 'Cpu(s)'"
        
        if "processes" in user_text_lower or "running processes" in user_text_lower:
            return "ps aux"
        
        if "network status" in user_text_lower or "network" in user_text_lower:
            return "ip addr show"
        
        # User information
        if "who am i" in user_text_lower or "current user" in user_text_lower or "logged in as" in user_text_lower or "user info" in user_text_lower:
            return "whoami"
        
        if "user" in user_text_lower and "info" in user_text_lower:
            return "id"
        
        # File search
        if "find" in user_text_lower or "search for" in user_text_lower:
            if "file" in user_text_lower:
                # Extract filename if mentioned
                words = user_text_lower.split()
                for i, word in enumerate(words):
                    if word in ["file", "files"] and i + 1 < len(words):
                        filename = words[i + 1]
                        if not filename in ["in", "the", "a", "an", "and", "or", "with"]:
                            return f"find . -name '*{filename}*' -type f"
                return "find . -type f | head -20"
        
        # Check if something exists
        if "check if" in user_text_lower:
            words = user_text_lower.split()
            for i, word in enumerate(words):
                if word == "if" and i + 1 < len(words):
                    item = words[i + 1]
                    if not item in ["the", "a", "an", "and", "or", "with", "file", "directory"]:
                        return f"test -e {item} && echo 'Exists' || echo 'Does not exist'"
            return "echo 'Please specify what to check'"
        
        # Date and time
        if "date" in user_text_lower or "time" in user_text_lower:
            return "date"
        
        # Calendar
        if "calendar" in user_text_lower or "cal" in user_text_lower:
            return "cal"
        
        # Weather (if wttr.in is available)
        if "weather" in user_text_lower:
            return "curl -s wttr.in"
        
        # Additional patterns
        if "uptime" in user_text_lower or "how long" in user_text_lower and "running" in user_text_lower:
            return "uptime"
        
        if "load" in user_text_lower and "average" in user_text_lower:
            return "uptime"
        
        if "kernel" in user_text_lower or "version" in user_text_lower:
            return "uname -r"
        
        if "hostname" in user_text_lower or "computer name" in user_text_lower:
            return "hostname"
        
        if "environment" in user_text_lower or "env" in user_text_lower:
            return "env | head -20"
        
        if "history" in user_text_lower and "command" in user_text_lower:
            return "history | tail -10"
        
        if "services" in user_text_lower or "running services" in user_text_lower:
            return "systemctl list-units --type=service --state=running | head -10"
        
        if "ports" in user_text_lower or "listening" in user_text_lower:
            return "netstat -tuln | head -10"
        
        if "connections" in user_text_lower or "network connections" in user_text_lower:
            return "ss -tuln | head -10"
        
        # Default fallback
        return None

    def handle_command_request(self, user_text):
        """Handle a command execution request with user consent"""
        command = self.extract_command(user_text)
        if not command:
            # Check if this was a natural language request that we couldn't interpret
            is_natural_request = not any(indicator in user_text.lower() for indicator in [
                "run command", "execute command", "run:", "execute:", "command:", "run `", "execute `"
            ])
            
            if is_natural_request:
                return self.suggest_helpful_commands(user_text)
            else:
                return "I couldn't identify a command to execute. Please specify the command clearly, for example: 'run command: ls -la' or 'execute: `pwd`'"
        
        # Check if this was a natural language request
        is_natural_request = not any(indicator in user_text.lower() for indicator in [
            "run command", "execute command", "run:", "execute:", "command:", "run `", "execute `"
        ])
        
        if is_natural_request:
            explanation = self.explain_command(command, user_text)
            response = f"I'll help you with that! Based on your request, I suggest running:\n\n**Command:** `{command}`\n\n**What it does:** {explanation}\n\nPlease confirm in the dialog that will appear."
        else:
            response = f"Please confirm the command execution in the dialog that appeared."
        
        # Store the command for the confirmation dialog
        self.pending_command = command
        
        # Show confirmation dialog in the main thread
        GLib.idle_add(self.show_command_confirmation_and_execute)
        return response

    def suggest_helpful_commands(self, user_text):
        """Suggest helpful commands when natural language request is unclear"""
        user_text_lower = user_text.lower()
        
        suggestions = []
        
        if any(word in user_text_lower for word in ["file", "files", "directory", "folder"]):
            suggestions.append("- `ls -la` - List files and directories")
            suggestions.append("- `pwd` - Show current directory")
            suggestions.append("- `find . -name '*.txt' -type f` - Find specific files")
        
        if any(word in user_text_lower for word in ["system", "computer", "machine"]):
            suggestions.append("- `uname -a` - System information")
            suggestions.append("- `hostname` - Computer name")
            suggestions.append("- `uptime` - System uptime and load")
        
        if any(word in user_text_lower for word in ["space", "disk", "storage"]):
            suggestions.append("- `df -h` - Disk space usage")
            suggestions.append("- `du -sh *` - Directory sizes")
        
        if any(word in user_text_lower for word in ["memory", "ram"]):
            suggestions.append("- `free -h` - Memory usage")
            suggestions.append("- `top` - Real-time system monitoring")
        
        if any(word in user_text_lower for word in ["network", "connection", "internet"]):
            suggestions.append("- `ip addr show` - Network interfaces")
            suggestions.append("- `ping google.com` - Test internet connection")
        
        if any(word in user_text_lower for word in ["user", "who", "login"]):
            suggestions.append("- `whoami` - Current user")
            suggestions.append("- `id` - User and group information")
            suggestions.append("- `who` - Currently logged in users")
        
        if not suggestions:
            suggestions = [
                "- `ls -la` - List files and directories",
                "- `pwd` - Show current directory", 
                "- `uname -a` - System information",
                "- `df -h` - Disk space usage",
                "- `free -h` - Memory usage",
                "- `whoami` - Current user"
            ]
        
        return f"I'm not sure what specific command you need. Here are some helpful commands you might want to try:\n\n" + "\n".join(suggestions[:6]) + "\n\nYou can also ask me to run any of these commands directly!"

    def explain_command(self, command, original_request):
        """Explain what a command will do"""
        explanations = {
            "ls -la": "Lists all files and directories in the current location with detailed information (permissions, owner, size, date)",
            "pwd": "Shows the current working directory path",
            "uname -a": "Displays detailed system information including kernel version, architecture, and hostname",
            "uname -r": "Shows the kernel version",
            "df -h": "Shows disk space usage for all mounted filesystems in human-readable format",
            "free -h": "Displays memory usage information (RAM and swap) in human-readable format",
            "top -bn1 | grep 'Cpu(s)'": "Shows current CPU usage percentage",
            "ps aux": "Lists all running processes with detailed information",
            "ip addr show": "Displays network interface information and IP addresses",
            "whoami": "Shows the current username",
            "id": "Displays user and group information for the current user",
            "date": "Shows the current date and time",
            "cal": "Displays a calendar for the current month",
            "curl -s wttr.in": "Fetches current weather information (requires internet connection)",
            "uptime": "Shows how long the system has been running and the current load average",
            "hostname": "Displays the computer's hostname",
            "env | head -20": "Shows the first 20 environment variables",
            "history | tail -10": "Shows the last 10 commands from command history",
            "systemctl list-units --type=service --state=running | head -10": "Lists the first 10 running system services",
            "netstat -tuln | head -10": "Shows the first 10 listening network ports",
            "ss -tuln | head -10": "Shows the first 10 listening network connections (modern alternative to netstat)"
        }
        
        # Check for find commands
        if command.startswith("find . -name"):
            return f"Searches for files matching the pattern '{command.split('*')[1]}' in the current directory and subdirectories"
        
        # Check for test commands
        if command.startswith("test -e"):
            item = command.split()[-1]
            return f"Checks if the file or directory '{item}' exists"
        
        return explanations.get(command, f"Executes the command: {command}")

    def show_command_confirmation_and_execute(self):
        """Show confirmation dialog and execute command if confirmed"""
        if hasattr(self, 'pending_command'):
            command = self.pending_command
            confirmed = self.show_command_confirmation(command)
            
            if confirmed:
                # Execute the command in a separate thread
                threading.Thread(target=self.execute_command_with_result, args=(command,), daemon=True).start()
            else:
                GLib.idle_add(self.append_message, "assistant", "Command execution cancelled by user.")
            
            # Clear the pending command
            delattr(self, 'pending_command')
        
        return False  # Don't call this function again

    def execute_command_with_result(self, command):
        """Execute command and show result in the main thread"""
        result = self.execute_command(command)
        response = f"**Command executed:** `{command}`\n\n**Result:**\n```\n{result}\n```"
        GLib.idle_add(self.append_message, "assistant", response)

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

    def generate_response(self):
        try:
            data = {
                "model": "deepseek-r1:8b",
                "prompt": self.build_prompt(),
                "think": True,
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
