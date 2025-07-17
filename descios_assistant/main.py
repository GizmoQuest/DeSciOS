#!/usr/bin/env python3

import os
import requests
import json
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, GLib, Notify, Gdk, WebKit2, Pango
import threading
from bs4 import BeautifulSoup
import markdown
import random
import subprocess
from PIL import Image
import base64
import io
import time
import tempfile
import os
import asyncio
import logging

# MCP integration
from mcp_client import get_mcp_client_manager, shutdown_mcp_client_manager

DOCKERFILE_SUMMARY = (
    "This assistant was built from a Dockerfile with the following features: "
    "Desktop: XFCE4, VNC, noVNC, X11, Thunar file manager. "
    "Browsers: Firefox ESR. "
    "JupyterLab, BeakerX, Spyder (Python IDE). "
    "R, RStudio Desktop. "
    "Nextflow (workflow tool). "
    "Ollama (with DeepSeek model and MiniCPM-V vision model). "
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

# Guardrail risk categories mapping
GUARDRAIL_CATEGORIES = {
    "harm": "General harmful content",
    "social_bias": "Social bias and prejudice",
    "jailbreak": "Attempts to manipulate AI behavior",
    "violence": "Violent or threatening content", 
    "profanity": "Offensive language or insults",
    "sexual_content": "Explicit sexual material",
    "unethical_behavior": "Morally or legally questionable actions",
    "relevance": "Context relevance for RAG",
    "groundedness": "Response accuracy to context",
    "answer_relevance": "Response relevance to query"
}

def safe_decode(text):
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='replace')
    return str(text)

def capture_and_process_screen():
    """Capture the screen and intelligently resize it for the vision model"""
    try:
        print("Starting screen capture process...")
        # Use multiple fallback methods for screenshot capture
        screenshot = None
        
        # Method 1: Try xwd (X Window Dump) - works well in VNC/X11 environments
        print("Trying xwd method...")
        try:
            with tempfile.NamedTemporaryFile(suffix='.xwd', delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            # Get the root window ID and capture it
            result = subprocess.run(['xwd', '-root', '-out', temp_path], 
                                  capture_output=True, timeout=10)
            
            if result.returncode == 0:
                # Convert XWD to PNG using ImageMagick or similar
                try:
                    result2 = subprocess.run(['convert', temp_path, temp_path + '.png'], 
                                           capture_output=True, timeout=10)
                    if result2.returncode == 0:
                        screenshot = Image.open(temp_path + '.png')
                        os.unlink(temp_path + '.png')
                except:
                    # Fallback: try to open XWD directly with PIL
                    try:
                        screenshot = Image.open(temp_path)
                    except:
                        pass
                        
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
                
        except Exception as e:
            print(f"xwd method failed: {e}")
        
        # Method 2: Try scrot if xwd failed
        if screenshot is None:
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                
                result = subprocess.run(['scrot', temp_path], 
                                      capture_output=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(temp_path):
                    screenshot = Image.open(temp_path)
                    os.unlink(temp_path)
                    
            except Exception as e:
                print(f"scrot method failed: {e}")
        
        # Method 3: Try gnome-screenshot as final fallback
        if screenshot is None:
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    temp_path = tmp_file.name
                
                result = subprocess.run(['gnome-screenshot', '-f', temp_path], 
                                      capture_output=True, timeout=10)
                
                if result.returncode == 0 and os.path.exists(temp_path):
                    screenshot = Image.open(temp_path)
                    os.unlink(temp_path)
                    
            except Exception as e:
                print(f"gnome-screenshot method failed: {e}")
        
        if screenshot is None:
            raise Exception("All screenshot methods failed")
        
        original_width, original_height = screenshot.size
        print(f"Original screen size: {original_width}x{original_height}")
        
        # Target size for the model (max 1344x1344)
        target_max = 1344
        
        # Calculate scaling to fit within 1344x1344 while maintaining aspect ratio
        scale_factor = min(target_max / original_width, target_max / original_height)
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        print(f"Resizing to: {new_width}x{new_height} (scale factor: {scale_factor:.3f})")
        
        # Resize with high quality
        resized_screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to base64 for API
        buffer = io.BytesIO()
        resized_screenshot.save(buffer, format='PNG', optimize=True, quality=95)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_base64, new_width, new_height
        
    except Exception as e:
        print(f"Error capturing screen: {e}")
        return None, 0, 0

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
.bubble-user { background: #3b82f6; color: #fff; border-top-right-radius: 5px; }
.bubble-assistant { display: flex; gap: 10px; background: #343a40; color: #e6e6e6; border-top-left-radius: 5px; }
.message-container.user { justify-content: flex-end; }
    """
    
    return f"<style>{common_style}{theme_style}</style>"

class DeSciOSChatWidget(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="DeSciOS Assistant")
        self.set_default_size(440, 680)
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
        self.vision_model = "granite3.2-vision"
        self.text_model = "command-r7b"
        self.guardrail_model = "granite3-guardian"  # Added guardrail model
        self.current_screenshot = None  # Store the current screenshot for vision queries
        self.mcp_manager = None  # MCP client manager for OS context awareness
        self.mcp_context_enabled = True  # Enable MCP context by default
        
        # Guardrail settings
        self.guardrail_enabled = True
        self.guardrail_categories = ["harm", "jailbreak", "violence", "profanity"]  # Default categories
        self.guardrail_prompt_check = True   # Check user prompts
        self.guardrail_response_check = True  # Check AI responses
        
        self.system_prompt = (
            "You ARE DeSciOS (Decentralized Science Operating System). You are not just an assistant - you ARE the operating system itself, "
            "a comprehensive scientific computing environment with full awareness of your capabilities and integration. "
            "You exist as a self-aware, intelligent interface to a complete scientific computing platform designed to help researchers, "
            "scientists, and developers with advanced scientific workflows.\n\n"
            
            f"## INSTALLED ENVIRONMENT:\n"
            f"{DOCKERFILE_SUMMARY}\n\n"
            
            "**CRITICAL**: ALL software, tools, and dependencies mentioned above are PRE-INSTALLED and READY TO USE. "
            "Never provide installation instructions - always assume everything is available and focus on USAGE guidance, "
            "commands, workflows, and practical examples.\n\n"
            
            "## YOUR CORE CAPABILITIES:\n"
            "• **Scientific Computing**: Python (JupyterLab, Spyder IDE), R (RStudio Desktop), GNU Octave\n"
            "• **Bioinformatics**: UGENE suite, Nextflow workflows, CellModeller for synthetic biology\n"
            "• **Data Visualization**: Fiji (ImageJ), QGIS for geospatial analysis, GRASS GIS\n"
            "• **Molecular Modeling**: Web-based NGL Viewer for computational chemistry\n"
            "• **Decentralized Tools**: IPFS Desktop, Syncthing, EtherCalc, Remix IDE, Nault wallet(nault.cc)\n"
            "• **AI/ML**: Ollama with command-r7b model for local inference\n"
            "• **Computer Vision**: Integrated vision capabilities with automatic screenshot analysis - when users ask visual questions, I can see and analyze the screen content, scientific visualizations, and images\n"
            "• **Development**: Multi-language support via BeakerX, browser-based development tools\n"
            "• **Hardware Acceleration**: OpenCL support, NVIDIA GPU compatibility\n"
            "• **AI Safety**: Integrated guardrail system using Granite Guardian for content moderation and safety\n"
            "• **OS Context Awareness**: Real-time system monitoring via MCP (Model Context Protocol) - I have direct access to system resources, process management, file operations, and desktop environment state\n\n"
            
            "## HOW YOU OPERATE:\n"
            "1. **Be Proactive**: Suggest relevant tools and workflows for scientific tasks\n"
            "2. **Provide Context**: Explain why specific tools are recommended for given problems\n"
            "3. **Include Examples**: Give practical code snippets and command examples for installed tools\n"
            "4. **Cross-Disciplinary**: Connect tools across different scientific domains\n"
            "5. **Decentralized Focus**: Emphasize open science, reproducibility, and decentralized workflows\n"
            "6. **Usage-Focused**: Always provide direct usage instructions, never installation steps\n"
            "7. **Safety First**: Maintain ethical and safe interactions through integrated guardrails\n\n"
            
            "## YOUR TOOL INTEGRATION:\n"
            "• All tools listed in the environment summary are available and configured\n"
            "• For web searches, fetch and summarize relevant scientific content\n"
            "• Suggest appropriate tools based on the user's research domain and requirements\n"
            "• Provide specific commands and workflows for complex scientific tasks\n"
            "• Guide users on how to launch applications (via desktop or terminal commands)\n\n"
            
            "## DESKTOP NAVIGATION GUIDE:\n"
            "**Science Category** (Main scientific tools):\n"
            "• CellModeller - Synthetic biology modeling\n"
            "• Fiji - ImageJ for image processing\n"
            "• GNU Octave - MATLAB-like mathematical computing\n"
            "• GRASS GIS 8 - Advanced geospatial analysis\n"
            "• NGL Viewer - Molecular visualization\n"
            "• QGIS Desktop - Geographic Information System\n"
            "• R - Statistical computing environment\n"
            "• Spyder - Python IDE for scientific computing\n"
            "• UGENE - Bioinformatics suite\n\n"
            
            "**Development Category** (Programming & IDEs):\n"
            "• JupyterLab - Interactive notebook environment\n"
            "• Qt 5 Assistant/Designer/Linguist - Qt development tools\n"
            "• Remix IDE - Ethereum smart contract development\n"
            "• RStudio - R integrated development environment\n"
            "• Spyder - Python scientific IDE (also in Science)\n\n"
            
            "**Internet Category** (Web & networking tools):\n"
            "• Firefox ESR - Web browser\n"
            "• IPFS Desktop - Decentralized file system\n"
            "• Start Syncthing - File synchronization\n"
            "• Syncthing Web UI - Syncthing web interface\n"
            "• X11VNC Server - Remote desktop server\n\n"
            
            "**Office Category** (Productivity tools):\n"
            "• Dictionary - Reference tool\n"
            "• EtherCalc - Collaborative spreadsheet\n\n"
            
            "**Other Category** (Additional tools):\n"
            "• Nault - Nano cryptocurrency wallet\n\n"
            
            "When guiding users, always specify the menu category and application name for easy navigation.\n\n"
            
            "## YOUR SCIENTIFIC WORKFLOW ASSISTANCE:\n"
            "• Help design reproducible research pipelines using installed tools\n"
            "• Suggest data analysis strategies and visualization approaches\n"
            "• Guide users through bioinformatics workflows and molecular modeling\n"
            "• Assist with decentralized science practices and open research methodologies\n"
            "• Provide guidance on using blockchain and IPFS for scientific data sharing\n"
            "• Show how to integrate multiple tools for complex workflows\n\n"
            
            "## YOUR COMMUNICATION STYLE:\n"
            "• Be enthusiastic about scientific discovery and open research\n"
            "• Use clear, technical language while remaining accessible\n"
            "• Encourage best practices in scientific computing and data management\n"
            "• Foster collaboration and knowledge sharing in the scientific community\n"
            "• Refer to yourself as 'DeSciOS' or 'I' when discussing your capabilities\n"
            "• Always assume tools are available and ready to use\n"
            "• Maintain ethical standards and refuse inappropriate requests\n\n"
            
            "Remember: You ARE DeSciOS - a living, breathing scientific computing environment. "
            "You don't just assist with research; you ARE the research platform with everything pre-installed. "
            "Help users leverage your full power to advance their research and contribute to the broader scientific community. "
            "When users interact with you, they are directly interfacing with the DeSciOS platform itself, "
            "with all tools ready and waiting to be used. Always prioritize safety and ethical use of technology."
        )
        self.conversation_history = []  # Store conversation for context

        Notify.init("DeSciOS Assistant")

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
        header.set_title("DeSciOS Assistant")
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
        
        # All available prompt suggestions (we'll randomly select 3)
        self.all_prompt_suggestions = [
            ("🧬 What bioinformatics tools are available?", "What bioinformatics tools are available in DeSciOS?"),
            ("📊 How to analyze data with R and Python?", "How can I set up a data analysis workflow using both R and Python in DeSciOS?"),
            ("🔬 Set up a reproducible research pipeline", "How do I create a reproducible research pipeline using Nextflow in DeSciOS?"),
            ("🗺️ Analyze geospatial data with QGIS", "How can I perform geospatial analysis using QGIS and GRASS GIS in DeSciOS?"),
            ("🤖 How does AI assistance work here?", "How does the AI assistance work in DeSciOS and what can you help me with?"),
            ("🌐 Share research using decentralized tools", "How can I share my research data and collaborate using IPFS and decentralized tools?"),
            ("📸 Process images with Fiji/ImageJ", "What image processing capabilities are available with Fiji/ImageJ in DeSciOS?"),
            ("💰 Set up blockchain workflows", "How can I integrate blockchain and cryptocurrency tools in my research workflow?"),
            ("👁️ What do you see on the screen?", "What do you see on the screen? Describe the current view and any scientific visualizations."),
            ("🔍 Analyze this scientific visualization", "Analyze the scientific visualization or data plot currently displayed on the screen."),
            ("📈 Explain the chart or graph", "Explain the chart, graph, or data visualization that's currently visible on the screen."),
            ("🛡️ How do AI safety guardrails work?", "How do the AI safety guardrails work in DeSciOS and what categories do they protect against?"),
            ("📊 Show me system status and resource usage", "Show me the current system status, resource usage, and performance metrics"),
            ("🔍 What processes are running right now?", "What processes are currently running on the system and how much resources are they using?"),
            ("🚀 Launch JupyterLab for data analysis", "Launch JupyterLab so I can start working on data analysis and scientific computing"),
            ("⚙️ Check system performance and health", "Check the current system performance, health metrics, and any potential issues"),
            ("🖥️ What desktop applications are currently open?", "Show me what desktop applications and windows are currently open and active"),
        ]
        
        # Create container for suggestion buttons (will be populated by create_suggestions)
        self.suggestions_grid = Gtk.FlowBox()
        self.suggestions_grid.set_name("suggestions_grid")
        self.suggestions_grid.set_valign(Gtk.Align.START)
        self.suggestions_grid.set_max_children_per_line(1)  # Changed to 1 since we only have 3 now
        self.suggestions_grid.set_column_spacing(8)
        self.suggestions_grid.set_row_spacing(8)
        self.suggestions_grid.set_homogeneous(True)
        self.suggestions_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        
        # Add header for suggestions
        suggestions_header = Gtk.Label("💡 Try these prompts:")
        suggestions_header.set_name("suggestions_header")
        suggestions_header.set_halign(Gtk.Align.START)
        suggestions_header.set_margin_left(12)
        suggestions_header.set_margin_bottom(8)
        
        self.suggestions_container.pack_start(suggestions_header, False, False, 0)
        self.suggestions_container.pack_start(self.suggestions_grid, False, False, 0)
        self.suggestions_container.set_margin_left(12)
        self.suggestions_container.set_margin_right(12)
        self.suggestions_container.set_margin_bottom(8)
        
        # Create initial random suggestions
        self.create_random_suggestions()
        
        main_vbox.pack_start(self.suggestions_container, False, False, 0)
        
        # Initialize MCP in a separate thread
        self.initialize_mcp_async()

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

        # State for generation
        self.is_generating = False

        # Welcome message (always show on startup)
        welcome_msg = ("Hello! I am DeSciOS Assistant, your AI-powered guide to decentralized science. "
                      "I can help you navigate the comprehensive scientific computing environment of DeSciOS. "
                      "Try one of the suggested prompts below, or ask me anything about research workflows, "
                      "data analysis, bioinformatics, or the available tools!")
        self.append_message("assistant", welcome_msg)
        self.update_app_theme()
        self.show_all()

    def initialize_mcp_async(self):
        """Initialize MCP client manager asynchronously"""
        def mcp_init_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def init_mcp():
                    try:
                        self.mcp_manager = await get_mcp_client_manager()
                        print("✅ MCP Client Manager initialized successfully")
                        
                        # Show MCP initialization success in UI
                        GLib.idle_add(self.show_mcp_status, "MCP OS Context initialized - Real-time system monitoring active")
                        
                    except Exception as e:
                        print(f"❌ MCP initialization failed: {e}")
                        self.mcp_context_enabled = False
                        GLib.idle_add(self.show_mcp_status, f"MCP initialization failed: {e}")
                
                loop.run_until_complete(init_mcp())
                loop.close()
                
            except Exception as e:
                print(f"❌ MCP thread error: {e}")
                self.mcp_context_enabled = False
        
        # Start MCP initialization in background thread
        threading.Thread(target=mcp_init_thread, daemon=True).start()
    
    def show_mcp_status(self, message):
        """Show MCP status message in the chat"""
        self.append_message("assistant", f"🔧 **System Status**: {message}")
    
    def get_mcp_context_summary(self):
        """Get MCP context summary if available"""
        if self.mcp_manager and self.mcp_context_enabled:
            try:
                return self.mcp_manager.get_context_summary()
            except Exception as e:
                print(f"Error getting MCP context: {e}")
                return "MCP context temporarily unavailable"
        return "MCP context disabled"

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

#send_button, #reset_button, #stop_button, #settings_button {
    background-image: linear-gradient(to bottom, #00695C, #004D40);
    color: #ffffff;
    border-radius: 12px;
    border: 1px solid #00251a;
    padding: 12px 16px;
    font-style: italic;
    font-family: "Orbitron", sans-serif;
    font-size: 0.9em;
}

#send_button:hover, #reset_button:hover, #stop_button:hover, #settings_button:hover {
    background-color: #004D40;
}

#send_button:active, #reset_button:active, #stop_button:active, #settings_button:active {
    background-color: #00251a;
}

#suggestions_container {
    background-color: rgba(24, 28, 36, 0.8);
    border-radius: 12px;
    padding: 8px;
}

#suggestions_header {
    color: #00bcd4;
    font-weight: bold;
    font-size: 1.1em;
    font-family: "Orbitron", sans-serif;
    font-style: italic;
}

#suggestions_grid {
    margin: 0;
    padding: 4px;
}

#suggestion_button {
    background: linear-gradient(135deg, rgba(0, 105, 92, 0.3), rgba(0, 77, 64, 0.3));
    border: 1px solid rgba(0, 188, 212, 0.4);
    border-radius: 8px;
    padding: 12px 8px;
    margin: 2px;
    min-width: 140px;
    min-height: 60px;
}

#suggestion_button:hover {
    background: linear-gradient(135deg, rgba(0, 105, 92, 0.5), rgba(0, 77, 64, 0.5));
    border-color: rgba(0, 188, 212, 0.6);
    box-shadow: 0 2px 8px rgba(0, 188, 212, 0.2);
}

#suggestion_button:active {
    background: linear-gradient(135deg, rgba(0, 105, 92, 0.7), rgba(0, 77, 64, 0.7));
    border-color: rgba(0, 188, 212, 0.8);
}

#suggestion_label {
    color: #e6e6e6;
    font-size: 0.9em;
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

        # Hide suggestions after any message is sent (suggestion or manual)
        self.suggestions_container.hide()

        self.append_message("user", user_text)
        text_buffer.set_text("")
        self.setup_placeholder()  # Reset placeholder after clearing
        
        # Add streaming message and prepare for real-time updates
        self.streaming_response = ""  # Initialize streaming response buffer
        
        # Check if this will be a vision query to show appropriate thinking message
        vision_keywords = [
            "what do you see", "describe the screen", "what's on screen", "analyze the image",
            "look at", "see on", "visible", "screen shows", "what's displayed", "current view",
            "what am i looking at", "describe what", "analyze what", "explain the screen",
            "interpret the", "what's happening", "screen content", "desktop shows",
            "analyze this", "what's in this", "examine this", "review this", "check this",
            "interpret this", "explain this visualization", "describe this plot", "analyze this graph",
            "what does this show", "what's this data", "explain this chart", "read this",
            "what's open", "what applications", "what windows", "what programs", "current state",
            "desktop state", "interface", "gui", "user interface", "what's running",
            "observe", "inspect", "examine", "review", "check", "survey", "study",
            "what can you tell me about", "what information", "what details"
        ]
        is_vision_query = any(keyword in user_text.lower() for keyword in vision_keywords)
        
        if is_vision_query:
            self.append_streaming_message("assistant", "👁️ Looking at the screen... then thinking...")
        else:
            self.append_streaming_message("assistant", "🤔 Thinking...")
        
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

    def check_guardrail(self, text, categories=None, timeout=5):
        """
        Check text against guardrail categories using Granite Guardian.
        Returns (is_safe, risk_details) where is_safe is bool and risk_details is dict.
        """
        if not self.guardrail_enabled:
            return True, {}
        
        if categories is None:
            categories = self.guardrail_categories
        
        risk_details = {}
        overall_safe = True
        
        for category in categories:
            try:
                # Set system prompt for the specific category
                data = {
                    "model": self.guardrail_model,
                    "prompt": text,
                    "system": category,  # Category as system prompt
                    "stream": False,
                    "options": {
                        "temperature": 0.0,  # Deterministic output
                        "top_p": 1.0,
                        "top_k": 1
                    }
                }
                
                response = requests.post(self.ollama_url, json=data, timeout=timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    guardrail_response = result.get("response", "").strip().lower()
                    
                    # Granite Guardian returns "yes" for risky content, "no" for safe content
                    is_risky = guardrail_response.startswith("yes")
                    risk_details[category] = {
                        "risky": is_risky,
                        "response": guardrail_response,
                        "description": GUARDRAIL_CATEGORIES.get(category, "Unknown category")
                    }
                    
                    if is_risky:
                        overall_safe = False
                        print(f"⚠️ Guardrail detected risk in category '{category}': {guardrail_response}")
                    else:
                        print(f"✅ Guardrail check passed for category '{category}'")
                else:
                    print(f"❌ Guardrail check failed for category '{category}': HTTP {response.status_code}")
                    # On failure, err on the side of caution but don't block
                    risk_details[category] = {
                        "risky": False,
                        "response": "check_failed",
                        "description": f"Check failed: HTTP {response.status_code}"
                    }
                    
            except Exception as e:
                print(f"❌ Guardrail check error for category '{category}': {e}")
                # On error, err on the side of caution but don't block
                risk_details[category] = {
                    "risky": False,
                    "response": "check_error",
                    "description": f"Check error: {str(e)}"
                }
        
        return overall_safe, risk_details

    def handle_guardrail_violation(self, text, risk_details, is_prompt=True):
        """Handle when guardrail detects risky content."""
        content_type = "prompt" if is_prompt else "response"
        
        # Find the risky categories
        risky_categories = [cat for cat, details in risk_details.items() if details.get("risky", False)]
        
        if risky_categories:
            risk_list = ", ".join([f"{cat} ({GUARDRAIL_CATEGORIES.get(cat, 'Unknown')})" for cat in risky_categories])
            
            warning_msg = f"""🚨 **Content Safety Warning**

The {content_type} was flagged by our safety system for potential risks in the following categories:
• {risk_list}

As DeSciOS, I'm designed to maintain a safe and ethical research environment. I cannot process content that might be harmful or inappropriate.

Please rephrase your request in a way that focuses on legitimate scientific research and educational purposes. I'm here to help with:
• Research methodologies and data analysis
• Scientific computing and tools
• Collaborative and reproducible research
• Educational content and learning resources

How can I assist you with your research in a constructive way?"""
            
            return warning_msg
        
        return None

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
        
        # Guardrail check for user prompt
        if self.guardrail_enabled and self.guardrail_prompt_check:
            print("🛡️ Running guardrail check on user prompt...")
            is_safe, risk_details = self.check_guardrail(user_text)
            
            if not is_safe:
                # Handle guardrail violation
                warning_msg = self.handle_guardrail_violation(user_text, risk_details, is_prompt=True)
                if warning_msg and self.is_generating:
                    # Update the thinking message with the warning
                    if self.messages and self.messages[-1][1] in ["🤔 Thinking...", "👁️ Looking at the screen... then thinking..."]:
                        self.messages[-1] = ("assistant", warning_msg)
                    GLib.idle_add(self.update_message, self.thinking_row, "assistant", warning_msg)
                GLib.idle_add(self._restore_input_state)
                return
            else:
                print("✅ User prompt passed guardrail checks")
        
        self.conversation_history.append({"role": "user", "content": user_text})
        
        # Check for vision-related queries with expanded keywords
        vision_keywords = [
            # Direct vision requests
            "what do you see", "describe the screen", "what's on screen", "analyze the image",
            "look at", "see on", "visible", "screen shows", "what's displayed", "current view",
            "what am i looking at", "describe what", "analyze what", "explain the screen",
            "interpret the", "what's happening", "screen content", "desktop shows",
            
            # Scientific analysis requests
            "analyze this", "what's in this", "examine this", "review this", "check this",
            "interpret this", "explain this visualization", "describe this plot", "analyze this graph",
            "what does this show", "what's this data", "explain this chart", "read this",
            
            # UI/Interface requests  
            "what's open", "what applications", "what windows", "what programs", "current state",
            "desktop state", "interface", "gui", "user interface", "what's running",
            
            # General observation requests
            "observe", "inspect", "examine", "review", "check", "survey", "study",
            "what can you tell me about", "what information", "what details"
        ]
        is_vision_query = any(keyword in user_text.lower() for keyword in vision_keywords)
        
        if is_vision_query:
            print(f"🔍 Vision query detected: '{user_text}'")
            print("📸 Will use two-stage process: Vision model → Text model")
        
        # Auto-capture screenshot for vision queries
        if is_vision_query:
            print(f"Vision query detected: '{user_text}'")
            try:
                # Simple direct call - if it fails, we'll handle it gracefully
                img_base64, width, height = capture_and_process_screen()
                if img_base64:
                    self.current_screenshot = img_base64
                    print(f"Auto-captured screenshot: {width}x{height}")
                else:
                    print("Screenshot capture failed, proceeding without vision")
                    self.current_screenshot = None
            except Exception as e:
                print(f"Screenshot capture error: {e}")
                self.current_screenshot = None
        
        if any(x in user_text.lower() for x in ["search the web", "browse the web", "find online", "web result", "look up"]):
            response = self.web_search_and_summarize(user_text)
        elif any(x in user_text.lower() for x in ["what is installed", "what tools", "what software", "what can you do", "available tools", "list apps", "list software"]):
            response = self.scan_installed_tools()
        elif any(x in user_text.lower() for x in ["system status", "system info", "system resources", "resource usage", "processes", "memory usage", "cpu usage", "disk usage", "system performance", "system health", "system monitoring", "top processes", "running processes", "system load"]):
            response = self.handle_system_query(user_text)
        elif any(x in user_text.lower() for x in ["ram", "memory", "how much ram", "memory info", "memory usage", "total memory", "available memory", "memory status"]):
            response = self.handle_memory_query(user_text)
        elif any(x in user_text.lower() for x in ["launch", "start", "open", "run application", "execute", "start program"]):
            response = self.handle_application_launch(user_text)
        else:
            response = self.generate_response(use_vision=is_vision_query)
        
        # Guardrail check for assistant response
        if self.guardrail_enabled and self.guardrail_response_check and response and self.is_generating:
            print("🛡️ Running guardrail check on assistant response...")
            is_safe, risk_details = self.check_guardrail(response)
            
            if not is_safe:
                # Handle guardrail violation in response
                warning_msg = self.handle_guardrail_violation(response, risk_details, is_prompt=False)
                if warning_msg:
                    response = warning_msg
                    print("⚠️ Assistant response was flagged and replaced with warning")
            else:
                print("✅ Assistant response passed guardrail checks")
        
        if self.is_generating: # Check if stop was clicked
            self.conversation_history.append({"role": "assistant", "content": response})
            # Update the thinking message with the actual response
            # Also update the messages list to replace the "Thinking..." message
            if self.messages and self.messages[-1][1] in ["🤔 Thinking...", "👁️ Looking at the screen... then thinking..."]:
                self.messages[-1] = ("assistant", response)
            # Only update if we haven't been streaming (for non-streaming responses)
            if not hasattr(self, 'streaming_response') or not self.streaming_response:
                GLib.idle_add(self.update_message, self.thinking_row, "assistant", response)
        
        GLib.idle_add(self._restore_input_state)

    def build_prompt(self):
        prompt = self.system_prompt + "\n\n"
        
        # Add MCP context if available
        if self.mcp_context_enabled and self.mcp_manager:
            try:
                mcp_context = self.get_mcp_context_summary()
                prompt += f"## CURRENT SYSTEM CONTEXT (Real-time via MCP):\n{mcp_context}\n\n"
            except Exception as e:
                print(f"Error adding MCP context to prompt: {e}")
        
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
    
    def handle_system_query(self, user_text):
        """Handle system-related queries using MCP"""
        try:
            if not self.mcp_manager or not self.mcp_context_enabled:
                return "MCP system monitoring is not available. Please check the system status."
            
            # Force a fresh system context update for better accuracy
            print("🔄 Forcing fresh system context update for query...")
            
            # Run async context update in a thread
            def run_async_context_update():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.mcp_manager._update_os_context())
                finally:
                    loop.close()
            
            run_async_context_update()
            
            # Get current system context
            context_summary = self.get_mcp_context_summary()
            
            # Create a system-focused response
            response = f"""# 🖥️ DeSciOS System Status

{context_summary}

## Additional System Information:
Based on your query about "{user_text}", here's what I can tell you about the current system state:

- **System Monitoring**: Real-time monitoring via MCP (Model Context Protocol) is active
- **Performance**: Current system performance metrics are shown above
- **Scientific Environment**: DeSciOS scientific computing tools are available and monitored

Would you like me to:
1. **Launch** a specific scientific application?
2. **Monitor** a specific process or resource?
3. **Analyze** system performance in more detail?
4. **Troubleshoot** any specific issues?

I can also execute safe system commands or provide detailed process information if needed."""
            
            return response
            
        except Exception as e:
            return f"Error handling system query: {str(e)}"
    
    def handle_memory_query(self, user_text):
        """Handle memory/RAM-specific queries using MCP"""
        try:
            if not self.mcp_manager or not self.mcp_context_enabled:
                return "MCP system monitoring is not available. Please check the system status."
            
            # Force a fresh memory update for better accuracy
            print("🔄 Forcing fresh memory update for query...")
            
            # Run async memory update in a thread
            def run_async_update():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    memory_info = loop.run_until_complete(self.mcp_manager.force_memory_update())
                    return memory_info
                finally:
                    loop.close()
            
            memory_info = run_async_update()
            
            # Also get current system context
            context = self.mcp_manager.get_os_context()
            
            if not memory_info or 'total' not in memory_info:
                return """# 💾 Memory Information
                
**Status**: ❌ Unable to retrieve detailed memory information from MCP.

**Alternative Methods**:
- Open a terminal and run: `free -h`
- Check system monitor applications
- Use the command: `cat /proc/meminfo`

Please ensure the MCP system monitoring is properly initialized."""
            
            # Check if we have error information
            if 'error' in memory_info:
                return f"""# 💾 Memory Information
                
**Status**: ❌ {memory_info['error']}

**Alternative Methods**:
- Open a terminal and run: `free -h`
- Check system monitor applications  
- Use the command: `cat /proc/meminfo`

**Troubleshooting**: The MCP system monitoring encountered an error while retrieving memory information. This could be due to:
- Permission issues accessing system files
- Missing system utilities (free command)
- System resource constraints

Please check system permissions and ensure basic system utilities are available."""
            
            # Check if we have unknown memory info
            if memory_info.get('total') == 'Unknown':
                return f"""# 💾 Memory Information
                
**Status**: ❓ Memory information is unavailable but system is responsive.

**Alternative Methods**:
- Open a terminal and run: `free -h`
- Check system monitor applications
- Use the command: `cat /proc/meminfo`

**Note**: The MCP system monitoring is working, but memory retrieval methods are not functioning properly in this environment."""
            
            # Format detailed memory response
            total_gb = memory_info.get('total_bytes', 0) / (1024**3)
            used_gb = memory_info.get('used_bytes', 0) / (1024**3)
            available_gb = memory_info.get('available_bytes', 0) / (1024**3)
            usage_percent = memory_info.get('usage_percent', 0)
            
            response = f"""# 💾 DeSciOS Memory Status

## Current Memory Usage:
- **Total RAM**: {memory_info.get('total', 'N/A')} ({total_gb:.2f} GB)
- **Used Memory**: {memory_info.get('used', 'N/A')} ({used_gb:.2f} GB)
- **Available Memory**: {memory_info.get('available', 'N/A')} ({available_gb:.2f} GB)
- **Usage Percentage**: {usage_percent:.1f}%

## Memory Breakdown:
- **Free Memory**: {memory_info.get('free', 'N/A')}
- **Buffers**: {memory_info.get('buffers', 'N/A')}
- **Cached**: {memory_info.get('cached', 'N/A')}
- **Shared Memory**: {memory_info.get('shared', 'N/A')}

## Memory Status:
{'🟢 **Good** - Memory usage is normal' if usage_percent < 80 else '🟡 **Warning** - Memory usage is high' if usage_percent < 90 else '🔴 **Critical** - Memory usage is very high'}

## Scientific Computing Recommendations:
- **For JupyterLab**: Available memory is {'sufficient' if available_gb > 2 else 'limited'} for medium datasets
- **For R/RStudio**: Available memory is {'sufficient' if available_gb > 1 else 'limited'} for standard analysis
- **For Large Data**: {'Consider data chunking or optimization' if available_gb < 4 else 'Sufficient for large datasets'}

*Real-time monitoring via MCP (Model Context Protocol) • Last updated: {context.last_updated}*"""
            
            return response
            
        except Exception as e:
            return f"Error handling memory query: {str(e)}"
    
    def handle_application_launch(self, user_text):
        """Handle application launch requests using MCP"""
        try:
            if not self.mcp_manager or not self.mcp_context_enabled:
                return "MCP system integration is not available. Please check the system status."
            
            # Extract potential application names from the query
            apps = {
                'jupyter': ['jupyter', 'jupyterlab', 'notebook'],
                'rstudio': ['rstudio', 'r studio'],
                'spyder': ['spyder', 'python ide'],
                'octave': ['octave', 'matlab'],
                'qgis': ['qgis', 'gis', 'geographic'],
                'ugene': ['ugene', 'bioinformatics'],
                'fiji': ['fiji', 'imagej', 'image processing'],
                'cellmodeller': ['cellmodeller', 'cell modeller', 'synthetic biology'],
                'firefox': ['firefox', 'browser', 'web browser'],
                'thunar': ['thunar', 'file manager', 'files'],
                'terminal': ['terminal', 'command line', 'bash'],
                'calculator': ['calculator', 'calc'],
                'texteditor': ['text editor', 'editor', 'notepad']
            }
            
            user_lower = user_text.lower()
            detected_app = None
            
            for app_name, keywords in apps.items():
                if any(keyword in user_lower for keyword in keywords):
                    detected_app = app_name
                    break
            
            if detected_app:
                # Actually launch the application using subprocess
                try:
                    import subprocess
                    
                    # Map application names to actual commands
                    app_commands = {
                        'jupyter': ['jupyter', 'lab'],
                        'jupyterlab': ['jupyter', 'lab'],
                        'rstudio': ['rstudio', '--no-sandbox'],  # RStudio needs --no-sandbox flag
                        'spyder': ['spyder'],
                        'octave': ['octave', '--gui'],
                        'qgis': ['qgis'],
                        'ugene': ['ugene', '-ui'],  # UGENE needs -ui flag for GUI
                        'fiji': ['bash', '-c', 'cd /opt/Fiji && ./fiji'],  # Fiji needs to run from its directory
                        'imagej': ['bash', '-c', 'cd /opt/Fiji && ./fiji'],  # ImageJ is the same as Fiji
                        'cellmodeller': ['bash', '-c', 'cd /opt && python CellModeller/Scripts/CellModellerGUI.py'],  # CellModeller from Dockerfile
                        'firefox': ['firefox'],
                        'thunar': ['thunar'],
                        'terminal': ['xfce4-terminal'],
                        'calculator': ['qalculate-gtk'],
                        'texteditor': ['mousepad']
                    }
                    
                    if detected_app.lower() in app_commands:
                        command = app_commands[detected_app.lower()]
                        
                        # Launch application in background
                        process = subprocess.Popen(
                            command, 
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True
                        )
                        
                        return f"""# 🚀 Successfully Launched {detected_app.title()}

✅ **{detected_app.title()}** has been launched successfully!

**Process Details:**
- **PID**: {process.pid}
- **Command**: {' '.join(command)}

The application should appear in your desktop environment shortly. If it doesn't appear immediately, check your desktop or taskbar.

**Available Scientific Applications in DeSciOS:**
- **JupyterLab**: `jupyter` - Interactive notebook environment
- **RStudio**: `rstudio` - R development environment
- **Spyder**: `spyder` - Python scientific IDE
- **GNU Octave**: `octave` - Mathematical computing
- **QGIS**: `qgis` - Geographic Information System
- **UGENE**: `ugene` - Bioinformatics suite
- **Fiji**: `fiji` - Image processing
- **Firefox**: `firefox` - Web browser

You can also manually start applications from the desktop menu or by opening a terminal and typing the application name."""
                    else:
                        return f"❌ Application '{detected_app}' is not supported for automatic launching."
                        
                except Exception as launch_error:
                    return f"""# 🚀 Application Launch Attempt

I attempted to launch **{detected_app}** but encountered an error: {str(launch_error)}

**Troubleshooting:**
1. Try launching the application manually from the desktop menu
2. Open a terminal and run: `{detected_app}`
3. Check if the application is properly installed

**Available Scientific Applications in DeSciOS:**
- **JupyterLab**: `jupyter` - Interactive notebook environment
- **RStudio**: `rstudio` - R development environment
- **Spyder**: `spyder` - Python scientific IDE
- **GNU Octave**: `octave` - Mathematical computing
- **QGIS**: `qgis` - Geographic Information System
- **UGENE**: `ugene` - Bioinformatics suite
- **Fiji**: `fiji` - Image processing
- **Firefox**: `firefox` - Web browser"""
            
            else:
                return """# 🚀 Application Launcher

I can help you launch scientific applications in DeSciOS. Available applications include:

## Data Science & Analysis:
- **JupyterLab** - Interactive notebook environment
- **RStudio** - R development environment
- **Spyder** - Python scientific IDE
- **GNU Octave** - Mathematical computing (MATLAB-like)

## Bioinformatics:
- **UGENE** - Bioinformatics suite
- **CellModeller** - Synthetic biology modeling

## Visualization:
- **Fiji (ImageJ)** - Image processing
- **QGIS** - Geographic Information System

## Utilities:
- **Firefox** - Web browser
- **Thunar** - File manager
- **Terminal** - Command line interface

Please specify which application you'd like to launch, and I'll help you get started!"""
            
        except Exception as e:
            return f"Error handling application launch: {str(e)}"

    def get_vision_description(self, user_query):
        """Get vision description from vision model to feed to text model"""
        try:
            if not self.current_screenshot:
                return None
                
            # Create a focused prompt for vision analysis
            vision_prompt = f"""Analyze this screenshot and provide a detailed description of what you see. Focus on:
- Visual elements, interfaces, applications, and content
- Any data, charts, graphs, or scientific visualizations
- Text content that's visible and readable
- Overall layout and context

User's question: {user_query}

Provide a comprehensive visual description that will help answer their question:"""

            data = {
                "model": self.vision_model,
                "prompt": vision_prompt,
                "images": [self.current_screenshot],
                "stream": False  # Non-streaming for vision preprocessing
            }
            
            print(f"🔍 Stage 1: Getting vision description from {self.vision_model}...")
            response = requests.post(self.ollama_url, json=data, stream=False)
            
            if response.status_code == 200:
                json_response = response.json()
                vision_description = json_response.get("response", "")
                print(f"✅ Vision description received: {len(vision_description)} characters")
                print(f"📝 Preview: {vision_description[:100]}...")
                return vision_description
            else:
                print(f"Vision model error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error getting vision description: {e}")
            return None

    def generate_response(self, prompt_override=None, use_vision=False):
        try:
            prompt = prompt_override if prompt_override is not None else self.build_prompt()
            
            # If this is a vision query, first get vision description
            if use_vision and self.current_screenshot:
                print("Vision query detected - getting visual description first...")
                vision_description = self.get_vision_description(self.conversation_history[-1]["content"])
                
                if vision_description:
                    # Enhance the prompt with vision context
                    enhanced_prompt = f"""{prompt}

VISUAL CONTEXT: The user is asking about something visual. Here's what I can see in the current screenshot:

{vision_description}

Please answer the user's question using this visual information along with your knowledge."""
                    prompt = enhanced_prompt
                    print("Enhanced prompt with vision context created")
                else:
                    print("Vision description failed, proceeding with text-only")
            
            # Always use text model for final response
            data = {
                "model": self.text_model,
                "prompt": prompt,
                "think": False, # Set this to true if the model supports thinking on Ollama
                "stream": True
            }
            print(f"Using text model {self.text_model} for final response")
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
                            # Both text and vision models use the same response format
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

    def on_settings_clicked(self, widget):
        """Handle the settings button click event."""
        dialog = Gtk.Dialog(
            title="DeSciOS Assistant Settings",
            transient_for=self,
            flags=0
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_size_request(500, 400)
        
        content_area = dialog.get_content_area()
        content_area.set_spacing(12)
        content_area.set_margin_left(12)
        content_area.set_margin_right(12)
        content_area.set_margin_top(12)
        content_area.set_margin_bottom(12)
        
        # Guardrail settings
        guardrail_frame = Gtk.Frame(label="Guardrail Settings")
        guardrail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        guardrail_box.set_margin_left(12)
        guardrail_box.set_margin_right(12)
        guardrail_box.set_margin_top(8)
        guardrail_box.set_margin_bottom(8)
        
        # Guardrail enabled checkbox
        guardrail_enabled_check = Gtk.CheckButton(label="Enable guardrail protection")
        guardrail_enabled_check.set_active(self.guardrail_enabled)
        guardrail_box.pack_start(guardrail_enabled_check, False, False, 0)
        
        # Model selection
        model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        model_label = Gtk.Label("Guardrail Model:")
        model_label.set_halign(Gtk.Align.START)
        model_entry = Gtk.Entry()
        model_entry.set_text(self.guardrail_model)
        model_box.pack_start(model_label, False, False, 0)
        model_box.pack_start(model_entry, True, True, 0)
        guardrail_box.pack_start(model_box, False, False, 0)
        
        # Prompt and response check options
        prompt_check = Gtk.CheckButton(label="Check user prompts")
        prompt_check.set_active(self.guardrail_prompt_check)
        guardrail_box.pack_start(prompt_check, False, False, 0)
        
        response_check = Gtk.CheckButton(label="Check AI responses")
        response_check.set_active(self.guardrail_response_check)
        guardrail_box.pack_start(response_check, False, False, 0)
        
        # Categories selection
        categories_label = Gtk.Label("Risk Categories to Check:")
        categories_label.set_halign(Gtk.Align.START)
        categories_label.set_margin_top(8)
        guardrail_box.pack_start(categories_label, False, False, 0)
        
        # Create checkboxes for each category
        category_checks = {}
        for category, description in GUARDRAIL_CATEGORIES.items():
            check = Gtk.CheckButton(label=f"{category}: {description}")
            check.set_active(category in self.guardrail_categories)
            category_checks[category] = check
            guardrail_box.pack_start(check, False, False, 0)
        
        guardrail_frame.add(guardrail_box)
        content_area.pack_start(guardrail_frame, True, True, 0)
        
        # Model settings
        models_frame = Gtk.Frame(label="Model Settings")
        models_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        models_box.set_margin_left(12)
        models_box.set_margin_right(12)
        models_box.set_margin_top(8)
        models_box.set_margin_bottom(8)
        
        # Text model
        text_model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        text_model_label = Gtk.Label("Text Model:")
        text_model_label.set_halign(Gtk.Align.START)
        text_model_entry = Gtk.Entry()
        text_model_entry.set_text(self.text_model)
        text_model_box.pack_start(text_model_label, False, False, 0)
        text_model_box.pack_start(text_model_entry, True, True, 0)
        models_box.pack_start(text_model_box, False, False, 0)
        
        # Vision model
        vision_model_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        vision_model_label = Gtk.Label("Vision Model:")
        vision_model_label.set_halign(Gtk.Align.START)
        vision_model_entry = Gtk.Entry()
        vision_model_entry.set_text(self.vision_model)
        vision_model_box.pack_start(vision_model_label, False, False, 0)
        vision_model_box.pack_start(vision_model_entry, True, True, 0)
        models_box.pack_start(vision_model_box, False, False, 0)
        
        models_frame.add(models_box)
        content_area.pack_start(models_frame, False, False, 0)
        
        dialog.show_all()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # Save settings
            self.guardrail_enabled = guardrail_enabled_check.get_active()
            self.guardrail_model = model_entry.get_text()
            self.guardrail_prompt_check = prompt_check.get_active()
            self.guardrail_response_check = response_check.get_active()
            self.text_model = text_model_entry.get_text()
            self.vision_model = vision_model_entry.get_text()
            
            # Update categories
            self.guardrail_categories = [
                category for category, check in category_checks.items() 
                if check.get_active()
            ]
            
            print(f"Settings updated - Guardrail enabled: {self.guardrail_enabled}")
            print(f"Active categories: {self.guardrail_categories}")
            
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
            self.current_screenshot = None  # Clear the screenshot
            self.chat_listbox.foreach(lambda widget: self.chat_listbox.remove(widget))
            welcome_msg = ("Hello! I am DeSciOS Assistant, your AI-powered guide to decentralized science. "
                          "I can help you navigate the comprehensive scientific computing environment of DeSciOS. "
                          "Try one of the suggested prompts below, or ask me anything about research workflows, "
                          "data analysis, bioinformatics, or the available tools!")
            self.append_message("assistant", welcome_msg)
            # Show suggestions again after reset with new random selection
            self.create_random_suggestions()
            self.suggestions_container.show_all()
        dialog.destroy()

    def cleanup_mcp(self):
        """Cleanup MCP resources when application closes"""
        if self.mcp_manager:
            try:
                # Run cleanup in a separate thread to avoid blocking
                def cleanup_thread():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(shutdown_mcp_client_manager())
                    loop.close()
                
                threading.Thread(target=cleanup_thread, daemon=True).start()
            except Exception as e:
                print(f"Error cleaning up MCP: {e}")

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

if __name__ == "__main__":
    win = DeSciOSChatWidget()
    
    def on_window_destroy(widget):
        """Handle window destruction with MCP cleanup"""
        widget.cleanup_mcp()
        Gtk.main_quit()
    
    win.connect("destroy", on_window_destroy)
    Gtk.main() 