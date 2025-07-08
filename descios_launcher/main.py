#!/usr/bin/env python3
"""
DeSciOS Launcher - GUI for customizing DeSciOS Docker builds
Allows users to select which applications to install and customize settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import subprocess
import threading
from pathlib import Path
import yaml
import json

# Application templates for common installation patterns
APPLICATION_TEMPLATES = {
    "python_package": {
        "name": "Python Package Template",
        "dockerfile_section": "RUN pip install --no-cache-dir {package}",
        "description": "Install Python package via pip",
        "fields": ["package"]
    },
    "apt_package": {
        "name": "APT Package Template", 
        "dockerfile_section": "RUN apt update && apt install -y {packages}",
        "description": "Install system package via apt",
        "fields": ["packages"]
    },
    "github_release": {
        "name": "GitHub Release Template",
        "dockerfile_section": '''# Install {name}
RUN wget {download_url} && \\
    tar -xzf {archive_name} -C /opt && \\
    rm {archive_name} && \\
    ln -s /opt/{app_dir}/{executable} /usr/local/bin/{app_name} && \\
    echo '[Desktop Entry]\\nName={name}\\nExec={app_name}\\nIcon=applications-science\\nType=Application\\nCategories=Science;' \\
    > /usr/share/applications/{app_id}.desktop''',
        "description": "Install from GitHub release tarball",
        "fields": ["download_url", "archive_name", "app_dir", "executable", "app_name"]
    },
    "web_app": {
        "name": "Web Application Template",
        "dockerfile_section": '''# {name} (via Browser)
RUN echo '[Desktop Entry]\\nName={name}\\nExec=firefox {url}\\nIcon=applications-internet\\nType=Application\\nCategories={categories};' \\
    > /usr/share/applications/{app_id}.desktop''',
        "description": "Create desktop entry for web application",
        "fields": ["url", "categories"]
    },
    "custom": {
        "name": "Custom Dockerfile Section",
        "dockerfile_section": "{custom_commands}",
        "description": "Write custom Dockerfile commands",
        "fields": ["custom_commands"]
    }
}

class DeSciOSLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("DeSciOS Launcher")
        self.root.geometry("1410x1250")  # Increased window size for better layout
        
        # Beautiful color scheme
        self.colors = {
            'primary': '#2563eb',      # Beautiful blue
            'primary_light': '#3b82f6', # Lighter blue
            'secondary': '#10b981',     # Emerald green
            'accent': '#f59e0b',       # Amber
            'success': '#059669',      # Green
            'warning': '#d97706',      # Orange
            'error': '#dc2626',        # Red
            'background': '#f8fafc',   # Light gray
            'surface': '#f8fafc',      # White
            'text': '#1f2937',         # Dark gray
            'text_light': '#6b7280',   # Medium gray
            'border': '#e5e7eb',       # Light border
            'hover': '#f3f4f6'         # Hover state
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Configure styles
        self.setup_styles()
        
        # Initialize custom applications
        self.custom_applications = {}
        self.plugins_dir = Path("descios_plugins")
        
        # Create plugins directory if it doesn't exist
        self.plugins_dir.mkdir(exist_ok=True)
        
        # Application definitions - these will be optional
        self.applications = {
            "jupyterlab": {
                "name": "JupyterLab",
                "description": "Interactive development environment for notebooks",
                "dockerfile_section": 'RUN pip install --no-cache-dir jupyterlab',
                "enabled": True
            },
            "r_rstudio": {
                "name": "R & RStudio",
                "description": "Statistical computing language and IDE",
                "dockerfile_section": '''# Install R for Debian bookworm
RUN apt update -qq && \\
    apt install --no-install-recommends -y dirmngr ca-certificates gnupg wget && \\
    gpg --keyserver keyserver.ubuntu.com --recv-key 95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7 && \\
    gpg --armor --export 95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7 | \\
    tee /etc/apt/trusted.gpg.d/cran_debian_key.asc && \\
    echo "deb http://cloud.r-project.org/bin/linux/debian bookworm-cran40/" > /etc/apt/sources.list.d/cran.list && \\
    apt update -qq && \\
    apt install --no-install-recommends -y r-base

# Install RStudio Desktop (Open Source)
RUN apt update && apt install -y gdebi-core && \\
    wget https://download1.rstudio.org/electron/jammy/amd64/rstudio-2025.05.0-496-amd64.deb && \\
    gdebi -n rstudio-2025.05.0-496-amd64.deb && \\
    rm rstudio-2025.05.0-496-amd64.deb && \\
    echo '[Desktop Entry]\\nName=RStudio\\nExec=rstudio --no-sandbox\\nIcon=rstudio\\nType=Application\\nCategories=Development;' \\
    > /usr/share/applications/rstudio.desktop''',
                "enabled": True
            },
            "spyder": {
                "name": "Spyder",
                "description": "Scientific Python IDE",
                "dockerfile_section": 'RUN pip install --no-cache-dir spyder',
                "enabled": True
            },
            "ugene": {
                "name": "UGENE",
                "description": "Bioinformatics suite",
                "dockerfile_section": '''# Install UGENE (Bioinformatics suite)
RUN wget https://github.com/ugeneunipro/ugene/releases/download/52.1/ugene-52.1-linux-x86-64.tar.gz && \\
    tar -xzf ugene-52.1-linux-x86-64.tar.gz -C /opt && \\
    rm ugene-52.1-linux-x86-64.tar.gz && \\
    ln -s /opt/ugene-52.1/ugene /usr/local/bin/ugene && \\
    echo '[Desktop Entry]\\nName=UGENE\\nExec=ugene -ui\\nIcon=/opt/ugene-52.1/ugene.png\\nType=Application\\nCategories=Science;' \\
    > /usr/share/applications/ugene.desktop''',
                "enabled": True
            },
            "octave": {
                "name": "GNU Octave",
                "description": "MATLAB-compatible scientific computing",
                "dockerfile_section": 'RUN apt update && apt install -y octave',
                "enabled": True
            },
            "fiji": {
                "name": "Fiji (ImageJ)",
                "description": "Image processing and analysis",
                "dockerfile_section": '''# Install Fiji (ImageJ) with bundled JDK
RUN apt update && apt install -y unzip wget && \\
    wget https://downloads.imagej.net/fiji/latest/fiji-latest-linux64-jdk.zip && \\
    unzip fiji-latest-linux64-jdk.zip -d /opt && \\
    rm fiji-latest-linux64-jdk.zip && \\
    chown $USER:$USER -R /opt/Fiji && \\
    chmod +x /opt/Fiji/fiji-linux-x64 && \\
    echo 'alias fiji=/opt/Fiji/fiji-linux-x64' >> /home/$USER/.bashrc && \\
    echo '[Desktop Entry]\\nName=Fiji\\nExec=bash -c "cd /opt/Fiji && ./fiji"\\nIcon=applications-science\\nType=Application\\nCategories=Science;' \\
    > /usr/share/applications/fiji.desktop''',
                "enabled": True
            },
            "nextflow": {
                "name": "Nextflow",
                "description": "Workflow management system",
                "dockerfile_section": '''# Install Nextflow
RUN apt-get update && apt-get install -y openjdk-17-jre-headless && \\
    apt-get clean && rm -rf /var/lib/apt/lists/* && \\
    curl -s https://get.nextflow.io | bash && \\
    mv /nextflow /usr/bin/nextflow && \\
    chmod +x /usr/bin/nextflow && \\
    chown $USER:$USER /usr/bin/nextflow''',
                "enabled": True
            },
            "qgis_grass": {
                "name": "QGIS & GRASS GIS",
                "description": "Geographic Information Systems",
                "dockerfile_section": '''# Install QGIS and GRASS GIS 8
RUN apt update && apt install -y qgis qgis-plugin-grass grass && \\
    sed -i 's|^Exec=grass$|Exec=bash -c "export GRASS_PYTHON=/usr/bin/python3; grass"|' /usr/share/applications/grass82.desktop && \\
    echo 'export GRASS_PYTHON=/usr/bin/python3' >> /home/$USER/.bashrc && \\
    echo 'export GRASS_PYTHON=/usr/bin/python3' >> /root/.bashrc && \\
    update-desktop-database /usr/share/applications''',
                "enabled": True
            },

            "syncthing": {
                "name": "Syncthing",
                "description": "Continuous file synchronization",
                "dockerfile_section": 'RUN apt update && apt install -y syncthing',
                "enabled": True
            },
            "ethercalc": {
                "name": "EtherCalc",
                "description": "Collaborative spreadsheet (browser-based)",
                "dockerfile_section": '''# EtherCalc (via Browser)
RUN echo '[Desktop Entry]\\nName=EtherCalc\\nExec=firefox https://calc.domainepublic.net\\nIcon=applications-office\\nType=Application\\nCategories=Office;' \\
    > /usr/share/applications/ethercalc.desktop''',
                "enabled": True
            },
            "beakerx": {
                "name": "BeakerX",
                "description": "Multi-language kernel extension for JupyterLab",
                "dockerfile_section": '''# BeakerX for JupyterLab (multi-language kernel extension)
RUN pip install --no-cache-dir beakerx && \\
    beakerx install''',
                "enabled": True
            },
            "ngl_viewer": {
                "name": "NGL Viewer",
                "description": "Molecular visualization (browser-based)",
                "dockerfile_section": '''# NGL Viewer (via Browser)
RUN echo '[Desktop Entry]\\nName=NGL Viewer\\nExec=firefox https://nglviewer.org/ngl\\nIcon=applications-science\\nType=Application\\nCategories=Science;' \\
    > /usr/share/applications/nglviewer.desktop''',
                "enabled": True
            },
            "remix_ide": {
                "name": "Remix IDE",
                "description": "Ethereum development environment (browser-based)",
                "dockerfile_section": '''# Remix IDE (via Browser)
RUN echo '[Desktop Entry]\\nName=Remix IDE\\nExec=firefox https://remix.ethereum.org\\nIcon=applications-development\\nType=Application\\nCategories=Development;' \\
    > /usr/share/applications/remix-ide.desktop''',
                "enabled": True
            },
            "nault": {
                "name": "Nault",
                "description": "Nano cryptocurrency wallet (browser-based)",
                "dockerfile_section": '''# Nault (Nano wallet via Browser)
RUN echo '[Desktop Entry]\\nName=Nault\\nExec=firefox https://nault.cc\\nIcon=applications-finance\\nType=Application\\nCategories=Finance;' \\
    > /usr/share/applications/nault.desktop''',
                "enabled": True
            },
            "cellmodeller": {
                "name": "CellModeller",
                "description": "Bacterial cell growth simulation",
                "dockerfile_section": '''# CellModeller
# Install Qt5 and X11 dependencies for CellModeller GUI
RUN apt update && apt install -y \\
    qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools \\
    libqt5widgets5 libqt5gui5 libqt5core5a \\
    libqt5opengl5 libqt5opengl5-dev \\
    libxcb1 libxcb-glx0 libxcb-keysyms1 \\
    libxcb-image0 libxcb-shm0 libxcb-icccm4 \\
    libxcb-sync1 libxcb-xfixes0 libxcb-shape0 \\
    libxcb-randr0 libxcb-render-util0 \\
    libxkbcommon-x11-0 libxkbcommon0 \\
    libxcb-xinerama0 libxcb-cursor0 \\
    mesa-utils x11-apps && apt clean

# Clone and install CellModeller
WORKDIR /opt
RUN git clone https://github.com/cellmodeller/CellModeller.git && \\
    cd /opt/CellModeller && pip install -e . && \\
    mkdir /opt/data && \\
    chown -R $USER:$USER /opt/data && \\
    echo '[Desktop Entry]\\nName=CellModeller\\nExec=bash -c "cd /opt && python CellModeller/Scripts/CellModellerGUI.py"\\nIcon=applications-science\\nType=Application\\nTerminal=true\\nCategories=Science;' \\
    > /usr/share/applications/cellmodeller.desktop && \\
    chmod 644 /usr/share/applications/cellmodeller.desktop && \\
    update-desktop-database /usr/share/applications''',
                "enabled": True
            }
        }
        
        # Load custom applications from plugins
        self.load_custom_applications()
        
        self.setup_ui()

    def load_custom_applications(self):
        """Load custom applications from plugins directory"""
        try:
            for plugin_file in self.plugins_dir.glob("*.yaml"):
                try:
                    with open(plugin_file, 'r') as f:
                        plugin_data = yaml.safe_load(f)
                    
                    if isinstance(plugin_data, dict):
                        for app_id, app_info in plugin_data.items():
                            if self.validate_app_definition(app_info):
                                self.custom_applications[f"custom_{app_id}"] = {
                                    **app_info,
                                    "enabled": app_info.get("enabled", False),
                                    "source": str(plugin_file)
                                }
                                
                except Exception as e:
                    print(f"Error loading plugin {plugin_file}: {e}")
                    
            # Also check for JSON files
            for plugin_file in self.plugins_dir.glob("*.json"):
                try:
                    with open(plugin_file, 'r') as f:
                        plugin_data = json.load(f)
                    
                    if isinstance(plugin_data, dict):
                        for app_id, app_info in plugin_data.items():
                            if self.validate_app_definition(app_info):
                                self.custom_applications[f"custom_{app_id}"] = {
                                    **app_info,
                                    "enabled": app_info.get("enabled", False),
                                    "source": str(plugin_file)
                                }
                                
                except Exception as e:
                    print(f"Error loading plugin {plugin_file}: {e}")
                    
        except Exception as e:
            print(f"Error loading custom applications: {e}")

    def validate_app_definition(self, app_info):
        """Validate that an application definition has required fields"""
        required_fields = ["name", "description", "dockerfile_section"]
        return all(field in app_info for field in required_fields)

    def save_custom_application(self, app_id, app_info):
        """Save a custom application to the plugins directory"""
        try:
            plugin_file = self.plugins_dir / f"{app_id}.yaml"
            with open(plugin_file, 'w') as f:
                yaml.dump({app_id: app_info}, f, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving custom application: {e}")
            return False
        
    def setup_styles(self):
        """Configure beautiful styles for ttk widgets"""
        style = ttk.Style()
        
        # Configure Notebook (tabs)
        style.configure('TNotebook', 
                       background=self.colors['surface'],
                       borderwidth=0)
        style.configure('TNotebook.Tab', 
                       padding=[24, 16],  # Increased padding
                       background=self.colors['hover'],
                       foreground=self.colors['text'],
                       focuscolor='none',
                       font=('TkDefaultFont', 14, 'bold'))  # 12 * 1.2 = 14
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['primary']),
                           ('active', self.colors['primary_light'])],
                 foreground=[('selected', 'white'),
                           ('active', 'white')])
        
        # Configure Frames
        style.configure('TFrame', 
                       background=self.colors['surface'])
        
        # Modern section frame (no gray background)
        style.configure('Section.TFrame',
                       background=self.colors['surface'],
                       relief='flat',
                       borderwidth=0)
        
        # Clean LabelFrame (minimal styling)
        style.configure('Clean.TLabelFrame', 
                       background=self.colors['surface'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'])
        style.configure('Clean.TLabelFrame.Label',
                       background=self.colors['surface'],
                       foreground=self.colors['primary'],
                       font=('TkDefaultFont', 14, 'bold'))  # 12 * 1.2 = 14
        
        # Configure Buttons
        style.configure('TButton',
                       padding=[20, 12],  # Increased padding
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('TkDefaultFont', 13, 'bold'))  # 11 * 1.2 = 13
        style.map('TButton',
                 background=[('active', self.colors['primary_light']),
                           ('pressed', self.colors['primary'])])
        
        # Configure special button styles
        style.configure('Success.TButton',
                       background=self.colors['secondary'],
                       foreground='white')
        style.map('Success.TButton',
                 background=[('active', '#059669')])
        
        style.configure('Warning.TButton',
                       background=self.colors['accent'],
                       foreground='white')
        style.map('Warning.TButton',
                 background=[('active', '#d97706')])
        
        # Configure Labels
        style.configure('TLabel',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       font=('TkDefaultFont', 13))  # 11 * 1.2 = 13
        style.configure('Title.TLabel',
                       font=('TkDefaultFont', 24, 'bold'),  # 20 * 1.2 = 24
                       foreground=self.colors['primary'])
        style.configure('Subtitle.TLabel',
                       font=('TkDefaultFont', 17, 'bold'),  # 14 * 1.2 = 17
                       foreground=self.colors['text'])
        style.configure('SectionHeader.TLabel',
                       font=('TkDefaultFont', 19, 'bold'),  # 16 * 1.2 = 19
                       foreground=self.colors['primary'],
                       background=self.colors['surface'])
        style.configure('Description.TLabel',
                       foreground=self.colors['text_light'],
                       font=('TkDefaultFont', 12))  # 10 * 1.2 = 12
        
        # Configure Checkbuttons
        style.configure('TCheckbutton',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       focuscolor='none',
                       font=('TkDefaultFont', 13))  # 11 * 1.2 = 13
        style.map('TCheckbutton',
                 background=[('active', self.colors['hover'])])
        
        # Configure Entry widgets
        style.configure('TEntry',
                       fieldbackground='white',
                       borderwidth=1,
                       insertcolor=self.colors['primary'],
                       relief='solid',
                       font=('TkDefaultFont', 13))  # 11 * 1.2 = 13
        style.map('TEntry',
                 bordercolor=[('focus', self.colors['primary'])])
        
    def setup_ui(self):
        # Create main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill='both', expand=True)
        
        # Applications tab
        apps_frame = ttk.Frame(notebook)
        notebook.add(apps_frame, text="🔧 Applications")
        self.setup_applications_tab(apps_frame)
        
        # Custom Applications tab
        custom_frame = ttk.Frame(notebook)
        notebook.add(custom_frame, text="🧩 Custom Apps")
        self.setup_custom_applications_tab(custom_frame)
        
        # Settings tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Settings")
        self.setup_settings_tab(settings_frame)
        
        # Build tab
        build_frame = ttk.Frame(notebook)
        notebook.add(build_frame, text="🚀 Build & Deploy")
        self.setup_build_tab(build_frame)

    def setup_custom_applications_tab(self, parent):
        # Title
        title_label = ttk.Label(parent, text="🧩 Custom Applications", 
                               style='Title.TLabel')
        title_label.pack(pady=(20, 30))
        
        # Create main content with proper spacing
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill='both', expand=True, padx=20)
        
        # Existing custom applications section
        if self.custom_applications:
            existing_header = ttk.Label(content_frame, text="📦 Your Custom Applications", 
                                      style='SectionHeader.TLabel')
            existing_header.pack(anchor='w', pady=(0, 15))
            
            existing_frame = ttk.Frame(content_frame, style='Section.TFrame')
            existing_frame.pack(fill='x', pady=(0, 30))
            
            # Create scrollable frame for custom apps
            canvas = tk.Canvas(existing_frame, height=150, bg=self.colors['surface'])
            scrollbar = ttk.Scrollbar(existing_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
            scrollbar.pack(side="right", fill="y")
            
            # Add custom applications to the scrollable frame
            self.custom_app_vars = {}
            for app_id, app_info in self.custom_applications.items():
                self.custom_app_vars[app_id] = tk.BooleanVar(value=app_info.get('enabled', False))
                
                app_frame = ttk.Frame(scrollable_frame)
                app_frame.pack(fill='x', pady=5, padx=10)
                
                cb = ttk.Checkbutton(app_frame, text=app_info['name'], 
                                   variable=self.custom_app_vars[app_id],
                                   command=self.update_config_status)
                cb.pack(anchor='w')
                
                desc_label = ttk.Label(app_frame, text=f"• {app_info['description']}", 
                                     style='Description.TLabel')
                desc_label.pack(anchor='w', padx=(20, 0))
                
                source_label = ttk.Label(app_frame, text=f"Source: {Path(app_info.get('source', 'Unknown')).name}", 
                                       foreground=self.colors['text_light'],
                                       font=('TkDefaultFont', 11))
                source_label.pack(anchor='w', padx=(20, 0))
        
        # Add new application section
        add_header = ttk.Label(content_frame, text="➕ Add New Application", 
                             style='SectionHeader.TLabel')
        add_header.pack(anchor='w', pady=(20, 15))
        
        add_frame = ttk.Frame(content_frame, style='Section.TFrame')
        add_frame.pack(fill='both', expand=True)
        
        # Template selection
        template_frame = ttk.Frame(add_frame)
        template_frame.pack(fill='x', padx=20, pady=15)
        
        ttk.Label(template_frame, text="Choose Template:", font=('TkDefaultFont', 13)).pack(anchor='w', pady=(0, 10))
        
        self.template_var = tk.StringVar(value="python_package")
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var, 
                                    values=list(APPLICATION_TEMPLATES.keys()),
                                    state="readonly", width=30)
        template_combo.pack(anchor='w', pady=(0, 10))
        template_combo.bind('<<ComboboxSelected>>', self.on_template_changed)
        
        # Template description
        self.template_desc_label = ttk.Label(template_frame, text="", 
                                           style='Description.TLabel')
        self.template_desc_label.pack(anchor='w', pady=(0, 15))
        
        # Application details form
        form_frame = ttk.Frame(add_frame)
        form_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Basic info
        row = 0
        ttk.Label(form_frame, text="App ID:", font=('TkDefaultFont', 13)).grid(row=row, column=0, sticky='w', pady=8)
        self.app_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.app_id_var, width=30).grid(row=row, column=1, sticky='ew', padx=(20, 0), pady=8)
        
        row += 1
        ttk.Label(form_frame, text="Name:", font=('TkDefaultFont', 13)).grid(row=row, column=0, sticky='w', pady=8)
        self.app_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.app_name_var, width=30).grid(row=row, column=1, sticky='ew', padx=(20, 0), pady=8)
        
        row += 1
        ttk.Label(form_frame, text="Description:", font=('TkDefaultFont', 13)).grid(row=row, column=0, sticky='w', pady=8)
        self.app_desc_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.app_desc_var, width=30).grid(row=row, column=1, sticky='ew', padx=(20, 0), pady=8)
        
        # Dynamic template fields
        self.template_fields_frame = ttk.Frame(form_frame)
        self.template_fields_frame.grid(row=row+1, column=0, columnspan=2, sticky='ew', pady=15)
        self.template_fields_frame.grid_columnconfigure(1, weight=1)
        
        self.template_field_vars = {}
        
        # Preview section
        preview_frame = ttk.Frame(add_frame)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        ttk.Label(preview_frame, text="Dockerfile Preview:", font=('TkDefaultFont', 13, 'bold')).pack(anchor='w', pady=(0, 10))
        
        self.dockerfile_preview = tk.Text(preview_frame, height=8, width=80,
                                        bg='white', fg=self.colors['text'],
                                        font=('Monaco', 11),
                                        relief='solid', borderwidth=1)
        self.dockerfile_preview.pack(fill='both', expand=True)
        
        # Buttons
        buttons_frame = ttk.Frame(add_frame)
        buttons_frame.pack(fill='x', padx=20, pady=15)
        
        ttk.Button(buttons_frame, text="🔄 Update Preview", 
                  command=self.update_dockerfile_preview).pack(side='left', padx=10)
        ttk.Button(buttons_frame, text="💾 Save Application", 
                  command=self.save_new_application, style='Success.TButton').pack(side='left', padx=10)
        ttk.Button(buttons_frame, text="📁 Load Plugin File", 
                  command=self.load_plugin_file).pack(side='left', padx=10)
        
        # Initialize template fields
        self.on_template_changed()

    def on_template_changed(self, event=None):
        """Update template fields when template selection changes"""
        # Clear existing fields
        for widget in self.template_fields_frame.winfo_children():
            widget.destroy()
        self.template_field_vars.clear()
        
        template_key = self.template_var.get()
        template = APPLICATION_TEMPLATES.get(template_key, {})
        
        # Update description
        self.template_desc_label.config(text=template.get('description', ''))
        
        # Create fields for this template
        fields = template.get('fields', [])
        for i, field in enumerate(fields):
            ttk.Label(self.template_fields_frame, text=f"{field.replace('_', ' ').title()}:", 
                     font=('TkDefaultFont', 13)).grid(row=i, column=0, sticky='w', pady=8)
            
            self.template_field_vars[field] = tk.StringVar()
            
            if field == 'custom_commands':
                # Multi-line text for custom commands
                text_widget = tk.Text(self.template_fields_frame, height=4, width=50,
                                    bg='white', fg=self.colors['text'],
                                    font=('Monaco', 11),
                                    relief='solid', borderwidth=1)
                text_widget.grid(row=i, column=1, sticky='ew', padx=(20, 0), pady=8)
                self.template_field_vars[field].text_widget = text_widget
            else:
                entry = ttk.Entry(self.template_fields_frame, textvariable=self.template_field_vars[field], width=50)
                entry.grid(row=i, column=1, sticky='ew', padx=(20, 0), pady=8)
        
        # Update preview
        self.update_dockerfile_preview()

    def update_dockerfile_preview(self):
        """Update the Dockerfile preview based on current form values"""
        try:
            template_key = self.template_var.get()
            template = APPLICATION_TEMPLATES.get(template_key, {})
            dockerfile_template = template.get('dockerfile_section', '')
            
            # Gather field values
            field_values = {}
            for field, var in self.template_field_vars.items():
                if hasattr(var, 'text_widget'):
                    field_values[field] = var.text_widget.get('1.0', tk.END).strip()
                else:
                    field_values[field] = var.get()
            
            # Add basic info
            field_values['name'] = self.app_name_var.get()
            field_values['app_id'] = self.app_id_var.get()
            
            # Generate Dockerfile section
            try:
                dockerfile_section = dockerfile_template.format(**field_values)
            except KeyError as e:
                dockerfile_section = f"# Missing field: {e}\n{dockerfile_template}"
            
            # Update preview
            self.dockerfile_preview.delete('1.0', tk.END)
            self.dockerfile_preview.insert('1.0', dockerfile_section)
            
        except Exception as e:
            self.dockerfile_preview.delete('1.0', tk.END)
            self.dockerfile_preview.insert('1.0', f"# Error generating preview: {e}")

    def save_new_application(self):
        """Save a new custom application"""
        try:
            app_id = self.app_id_var.get().strip()
            name = self.app_name_var.get().strip()
            description = self.app_desc_var.get().strip()
            
            if not app_id or not name or not description:
                messagebox.showerror("Error", "Please fill in App ID, Name, and Description")
                return
            
            # Check if app_id already exists
            if app_id in self.applications or f"custom_{app_id}" in self.custom_applications:
                messagebox.showerror("Error", f"Application ID '{app_id}' already exists")
                return
            
            # Generate dockerfile section
            template_key = self.template_var.get()
            template = APPLICATION_TEMPLATES.get(template_key, {})
            dockerfile_template = template.get('dockerfile_section', '')
            
            # Gather field values
            field_values = {}
            for field, var in self.template_field_vars.items():
                if hasattr(var, 'text_widget'):
                    field_values[field] = var.text_widget.get('1.0', tk.END).strip()
                else:
                    field_values[field] = var.get()
            
            field_values['name'] = name
            field_values['app_id'] = app_id
            
            try:
                dockerfile_section = dockerfile_template.format(**field_values)
            except KeyError as e:
                messagebox.showerror("Error", f"Missing required field: {e}")
                return
            
            # Create app definition
            app_info = {
                "name": name,
                "description": description,
                "dockerfile_section": dockerfile_section,
                "enabled": False,
                "template": template_key,
                "template_fields": field_values
            }
            
            # Save to file
            if self.save_custom_application(app_id, app_info):
                # Add to current session
                self.custom_applications[f"custom_{app_id}"] = {
                    **app_info,
                    "source": str(self.plugins_dir / f"{app_id}.yaml")
                }
                
                messagebox.showinfo("Success", f"Application '{name}' saved successfully!")
                
                # Clear form
                self.app_id_var.set("")
                self.app_name_var.set("")
                self.app_desc_var.set("")
                for var in self.template_field_vars.values():
                    if hasattr(var, 'text_widget'):
                        var.text_widget.delete('1.0', tk.END)
                    else:
                        var.set("")
                self.update_dockerfile_preview()
                
                # Refresh the custom applications display
                # Note: In a full implementation, you'd want to refresh the UI
                messagebox.showinfo("Note", "Please restart the launcher to see your new application in the list.")
                
            else:
                messagebox.showerror("Error", "Failed to save application")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saving application: {str(e)}")

    def load_plugin_file(self):
        """Load a plugin file and import applications"""
        try:
            filename = filedialog.askopenfilename(
                title="Load Plugin File",
                filetypes=[("YAML files", "*.yaml"), ("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                # Copy file to plugins directory
                import shutil
                dest_file = self.plugins_dir / Path(filename).name
                shutil.copy2(filename, dest_file)
                
                messagebox.showinfo("Success", f"Plugin file loaded: {Path(filename).name}")
                messagebox.showinfo("Note", "Please restart the launcher to see the new applications.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading plugin file: {str(e)}")

    def get_all_applications(self):
        """Get combined dictionary of built-in and custom applications"""
        all_apps = self.applications.copy()
        all_apps.update(self.custom_applications)
        return all_apps
        
    def setup_applications_tab(self, parent):
        # Title with beautiful styling
        title_label = ttk.Label(parent, text="Select Applications to Install", 
                               style='Title.TLabel')
        title_label.pack(pady=(20, 30))
        
        # Main content frame
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill='both', expand=True, padx=20)
        
        # Mandatory section with beautiful styling
        mandatory_label = ttk.Label(content_frame, text="🔒 Mandatory Components", 
                                   style='Subtitle.TLabel')
        mandatory_label.pack(anchor='w', pady=(0, 15))
        
        mandatory_frame = ttk.Frame(content_frame)
        mandatory_frame.pack(fill='x', pady=(0, 30))
        
        # Mandatory items with checkmark emoji and success color
        mandatory_items = [
            "✅ DeSciOS Assistant",
            "✅ Talk to K (Krishnamurti dialogue)",
            "✅ DeSciOS Assistant Font", 
            "✅ Python3-pip (System Python package manager)",
            "✅ IPFS CLI & Desktop (Decentralized file system)"
        ]
        
        for item in mandatory_items:
            item_label = ttk.Label(mandatory_frame, text=item, 
                                 foreground=self.colors['success'],
                                 font=('TkDefaultFont', 14))  # 12 * 1.2 = 14
            item_label.pack(anchor='w', pady=4)
        
        # Optional applications section
        optional_label = ttk.Label(content_frame, text="📦 Optional Applications", 
                                  style='Subtitle.TLabel')
        optional_label.pack(anchor='w', pady=(0, 20))
        
        # Create a frame for applications in columns
        apps_container = ttk.Frame(content_frame)
        apps_container.pack(fill='both', expand=True)
        
        # Configure column weights for responsive layout
        apps_container.grid_columnconfigure(0, weight=1)
        apps_container.grid_columnconfigure(1, weight=1)
        apps_container.grid_columnconfigure(2, weight=1)
        
        # Create checkboxes for each application in 3 columns
        self.app_vars = {}
        all_apps = self.get_all_applications()
        apps_list = list(all_apps.items())
        
        for idx, (app_id, app_info) in enumerate(apps_list):
            self.app_vars[app_id] = tk.BooleanVar(value=app_info['enabled'])
            
            # Determine column (0, 1, or 2)
            col = idx % 3
            row = idx // 3
            
            # Create frame for each application
            app_frame = ttk.Frame(apps_container)
            app_frame.grid(row=row, column=col, sticky='ew', padx=10, pady=8)
            
            # Checkbox and name
            app_name = app_info['name']
            if app_id.startswith('custom_'):
                app_name += " 🧩"  # Add custom app indicator
                
            cb = ttk.Checkbutton(app_frame, text=app_name, 
                               variable=self.app_vars[app_id],
                               command=self.update_config_status)
            cb.pack(anchor='w')
            
            # Description with beautiful styling
            desc_label = ttk.Label(app_frame, text=f"• {app_info['description']}", 
                                 style='Description.TLabel')
            desc_label.pack(anchor='w', padx=(20, 0))
        
        # Buttons frame with beautiful styling
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=20, padx=20)
        
        ttk.Button(buttons_frame, text="✅ Select All", 
                  command=self.select_all, style='Success.TButton').pack(side='left', padx=10)
        ttk.Button(buttons_frame, text="❌ Select None", 
                  command=self.select_none, style='Warning.TButton').pack(side='left', padx=10)
        ttk.Button(buttons_frame, text="🔄 Reset to Defaults", 
                  command=self.reset_defaults).pack(side='left', padx=10)
        
    def select_all(self):
        for var in self.app_vars.values():
            var.set(True)
        self.update_config_status()
            
    def select_none(self):
        for var in self.app_vars.values():
            var.set(False)
        self.update_config_status()
            
    def reset_defaults(self):
        for app_id, var in self.app_vars.items():
            if app_id in self.applications:
                var.set(self.applications[app_id]['enabled'])
            else:
                var.set(False)  # Custom apps default to disabled
        self.update_config_status()
            
    def setup_settings_tab(self, parent):
        # Title
        title_label = ttk.Label(parent, text="🔧 DeSciOS Configuration", 
                               style='Title.TLabel')
        title_label.pack(pady=(20, 30))
        
        # Create main content with proper spacing
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill='both', expand=True, padx=20)
        
        # Ollama models section
        ollama_header = ttk.Label(content_frame, text="🤖 Ollama AI Models", 
                                style='SectionHeader.TLabel')
        ollama_header.pack(anchor='w', pady=(0, 15))
        
        ollama_frame = ttk.Frame(content_frame, style='Section.TFrame')
        ollama_frame.pack(fill='x', pady=(0, 30))
        
        # Clean content area without borders
        ollama_content = ttk.Frame(ollama_frame)
        ollama_content.pack(fill='x', padx=20, pady=15)
        
        ttk.Label(ollama_content, text="Models to install (one per line):", 
                 style='Description.TLabel').pack(anchor='w', padx=15, pady=(15, 10))
        
        self.ollama_models = tk.Text(ollama_content, height=4, width=50,
                                   bg='white', fg=self.colors['text'],
                                   insertbackground=self.colors['primary'],
                                   selectbackground=self.colors['primary'],
                                   selectforeground='white',
                                   relief='solid', borderwidth=1,
                                   font=('TkDefaultFont', 13))  # 11 * 1.2 = 13
        self.ollama_models.pack(fill='x', padx=15, pady=(0, 15))
        self.ollama_models.insert('1.0', 'command-r7b\ngranite3.2-vision')
        self.ollama_models.bind('<KeyRelease>', lambda e: self.update_config_status())
        
        # User settings
        user_header = ttk.Label(content_frame, text="👤 User Configuration", 
                              style='SectionHeader.TLabel')
        user_header.pack(anchor='w', pady=(0, 15))
        
        user_frame = ttk.Frame(content_frame, style='Section.TFrame')
        user_frame.pack(fill='x', pady=(0, 30))
        
        # Clean content area without borders
        user_content = ttk.Frame(user_frame)
        user_content.pack(fill='x', padx=20, pady=15)
        
        user_grid = ttk.Frame(user_content)
        user_grid.pack(fill='x', padx=15, pady=15)
        user_grid.grid_columnconfigure(1, weight=1)
        
        ttk.Label(user_grid, text="Username:", font=('TkDefaultFont', 13)).grid(row=0, column=0, sticky='w', pady=12)  # 11 * 1.2 = 13
        self.username_var = tk.StringVar(value="deScier")
        self.username_var.trace('w', lambda *args: self.update_config_status())
        username_entry = ttk.Entry(user_grid, textvariable=self.username_var, width=25)
        username_entry.grid(row=0, column=1, sticky='ew', padx=(20, 0), pady=12)
        
        ttk.Label(user_grid, text="VNC Password:", font=('TkDefaultFont', 13)).grid(row=1, column=0, sticky='w', pady=12)  # 11 * 1.2 = 13
        self.password_var = tk.StringVar(value="vncpassword")
        self.password_var.trace('w', lambda *args: self.update_config_status())
        password_entry = ttk.Entry(user_grid, textvariable=self.password_var, width=25, show="*")
        password_entry.grid(row=1, column=1, sticky='ew', padx=(20, 0), pady=12)
        
        # GPU settings
        gpu_header = ttk.Label(content_frame, text="🎮 GPU Configuration", 
                             style='SectionHeader.TLabel')
        gpu_header.pack(anchor='w', pady=(0, 15))
        
        gpu_frame = ttk.Frame(content_frame, style='Section.TFrame')
        gpu_frame.pack(fill='x')
        
        # Clean content area without borders
        gpu_content = ttk.Frame(gpu_frame)
        gpu_content.pack(fill='x', padx=20, pady=15)
        
        self.gpu_enabled_var = tk.BooleanVar(value=False)
        gpu_cb = ttk.Checkbutton(gpu_content, text="Enable GPU support (requires NVIDIA GPU with Docker support)", 
                               variable=self.gpu_enabled_var)
        gpu_cb.pack(anchor='w', padx=15, pady=(15, 10))
        
        gpu_info_label = ttk.Label(gpu_content, 
                                 text="💡 Note: GPU support requires NVIDIA Docker runtime and compatible GPU drivers.",
                                 style='Description.TLabel')
        gpu_info_label.pack(anchor='w', padx=15, pady=(0, 15))
        
    def setup_build_tab(self, parent):
        # Title
        title_label = ttk.Label(parent, text="🚀 Build & Deploy DeSciOS", 
                               style='Title.TLabel')
        title_label.pack(pady=(20, 30))
        
        # Create main content with proper spacing
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill='both', expand=True, padx=20)
        
        # Build options
        build_header = ttk.Label(content_frame, text="🔨 Build Options", 
                               style='SectionHeader.TLabel')
        build_header.pack(anchor='w', pady=(0, 15))
        
        options_frame = ttk.Frame(content_frame, style='Section.TFrame')
        options_frame.pack(fill='x', pady=(0, 30))
        
        # Clean content area without borders
        options_content = ttk.Frame(options_frame)
        options_content.pack(fill='x', padx=20, pady=15)
        
        tag_grid = ttk.Frame(options_content)
        tag_grid.pack(fill='x', padx=15, pady=15)
        tag_grid.grid_columnconfigure(1, weight=1)
        
        ttk.Label(tag_grid, text="Docker Image Tag:", font=('TkDefaultFont', 13)).grid(row=0, column=0, sticky='w', pady=12)  # 11 * 1.2 = 13
        self.image_tag_var = tk.StringVar(value="descios:custom")
        tag_entry = ttk.Entry(tag_grid, textvariable=self.image_tag_var, width=35)
        tag_entry.grid(row=0, column=1, sticky='ew', padx=(20, 0), pady=12)
        
        # Buttons with beautiful styling
        buttons_frame = ttk.Frame(options_content)
        buttons_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        ttk.Button(buttons_frame, text="📄 Generate Dockerfile", 
                  command=self.generate_dockerfile).pack(side='left', padx=10)
        ttk.Button(buttons_frame, text="🔨 Build Docker Image", 
                  command=self.build_image, style='Success.TButton').pack(side='left', padx=10)
        ttk.Button(buttons_frame, text="💾 Save Configuration", 
                  command=self.save_config).pack(side='left', padx=10)
        ttk.Button(buttons_frame, text="🚀 Deploy!", 
                  command=self.deploy_image, style='Warning.TButton').pack(side='left', padx=10)
        
        # Configuration status with beautiful styling
        self.config_status_label = ttk.Label(options_content, text="", 
                                           font=('TkDefaultFont', 14, 'bold'))  # 12 * 1.2 = 14
        self.config_status_label.pack(padx=15, pady=(0, 15))
        self.update_config_status()
        
        # Deployment section
        deploy_header = ttk.Label(content_frame, text="🌐 Deployment Commands", 
                                style='SectionHeader.TLabel')
        deploy_header.pack(anchor='w', pady=(0, 15))
        
        deploy_frame = ttk.Frame(content_frame, style='Section.TFrame')
        deploy_frame.pack(fill='x', pady=(0, 30))
        
        # Clean content area without borders
        deploy_content = ttk.Frame(deploy_frame)
        deploy_content.pack(fill='x', padx=20, pady=15)
        
        # Docker run command display
        self.docker_cmd_text = scrolledtext.ScrolledText(deploy_content, height=5, width=80,
                                                       bg='white', fg=self.colors['text'],
                                                       insertbackground=self.colors['primary'],
                                                       selectbackground=self.colors['primary'],
                                                       selectforeground='white',
                                                       relief='solid', borderwidth=1,
                                                       font=('Monaco', 12))  # 10 * 1.2 = 12
        self.docker_cmd_text.pack(fill='x', padx=15, pady=15)
        self.update_docker_command()
        
        # Button to update command
        ttk.Button(deploy_content, text="🔄 Update Docker Run Command", 
                  command=self.update_docker_command).pack(padx=15, pady=(0, 15))
        
        # Output log
        log_header = ttk.Label(content_frame, text="📋 Build Log", 
                             style='SectionHeader.TLabel')
        log_header.pack(anchor='w', pady=(0, 15))
        
        log_frame = ttk.Frame(content_frame, style='Section.TFrame')
        log_frame.pack(fill='both', expand=True)
        
        # Clean content area without borders
        log_content = ttk.Frame(log_frame)
        log_content.pack(fill='both', expand=True, padx=20, pady=15)
        
        self.log_text = scrolledtext.ScrolledText(log_content, height=8,
                                                bg='white', fg='black',
                                                insertbackground=self.colors['primary'],
                                                selectbackground=self.colors['primary'],
                                                selectforeground='white',
                                                relief='solid', borderwidth=1,
                                                font=('Monaco', 12))  # 10 * 1.2 = 12
        self.log_text.pack(fill='both', expand=True, padx=15, pady=15)
        
    def update_docker_command(self):
        """Update the Docker run command based on current settings"""
        image_tag = self.image_tag_var.get()
        gpu_flag = "--gpus all " if self.gpu_enabled_var.get() else ""
        
        basic_cmd = f"docker run -p 6080:6080 {gpu_flag}{image_tag}"
        advanced_cmd = f"docker run -d -p 6080:6080 -p 5901:5901 {gpu_flag}--name descios {image_tag}"
        ipfs_cmd = f"docker run -d -p 6080:6080 -p 5901:5901 -p 4001:4001 -p 4001:4001/udp -p 5001:5001 -p 8080:8080 -p 9090:9090 {gpu_flag}--name descios {image_tag}"
        
        command_text = f"""# MAIN COMMAND (used by Deploy! button):
{ipfs_cmd}

# Basic command (web access via http://localhost:6080):
docker run -p 6080:6080 {image_tag}

# Advanced command (background mode with VNC):
docker run -d -p 6080:6080 -p 5901:5901 {gpu_flag}--name descios {image_tag}

# IPFS Access URLs:
# - IPFS Gateway: http://localhost:8080
# - IPFS API: http://localhost:5001
# - IPFS Web UI: http://localhost:5001/webui

# To stop the container:
docker stop descios

# To restart the container:
docker start descios
"""
        
        self.docker_cmd_text.delete('1.0', tk.END)
        self.docker_cmd_text.insert('1.0', command_text)
            
    def is_default_configuration(self):
        """Check if current configuration matches defaults"""
        # Check if all built-in applications match their default enabled state
        builtin_defaults_match = all(
            var.get() == self.applications[app_id]['enabled'] 
            for app_id, var in self.app_vars.items() 
            if app_id in self.applications
        )
        
        # Check if any custom applications are enabled
        custom_apps_enabled = any(
            var.get() for app_id, var in self.app_vars.items() 
            if app_id.startswith('custom_')
        )
        
        # Check if default models and user settings
        default_models = self.ollama_models.get('1.0', tk.END).strip() == 'command-r7b\ngranite3.2-vision'
        default_user = self.username_var.get() == 'deScier'
        default_password = self.password_var.get() == 'vncpassword'
        
        return builtin_defaults_match and not custom_apps_enabled and default_models and default_user and default_password
            
    def update_config_status(self):
        """Update the configuration status display"""
        if hasattr(self, 'config_status_label'):
            if self.is_default_configuration():
                self.config_status_label.config(
                    text="✨ Default configuration detected - will build from original Dockerfile for speed",
                    foreground=self.colors['success']
                )
            else:
                self.config_status_label.config(
                    text="🔧 Custom configuration - will generate and use Dockerfile.custom",
                    foreground=self.colors['primary']
                )

    def log_message(self, message):
        # Color-coded log messages for white background
        if "✅" in message or "Successfully" in message:
            color = '#059669'  # Success green (darker for white bg)
        elif "❌" in message or "Error" in message or "Failed" in message:
            color = '#dc2626'  # Error red
        elif "🔨" in message or "Building" in message:
            color = '#d97706'  # Warning orange
        elif "🚀" in message or "Deploy" in message:
            color = '#7c3aed'  # Purple
        else:
            color = 'black'  # Default black text
            
        self.log_text.insert(tk.END, f"{message}\n")
        # Apply color to the last line
        line_start = self.log_text.index("end-2c linestart")
        line_end = self.log_text.index("end-2c lineend")
        self.log_text.tag_add("colored", line_start, line_end)
        self.log_text.tag_config("colored", foreground=color)
        self.log_text.see(tk.END)
        self.root.update()

    def get_qt_dependencies(self):
        return '''RUN apt update && apt install -y \\
    qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools \\
    libqt5widgets5 libqt5gui5 libqt5core5a \\
    libqt5opengl5 libqt5opengl5-dev \\
    libxcb1 libxcb-glx0 libxcb-keysyms1 \\
    libxcb-image0 libxcb-shm0 libxcb-icccm4 \\
    libxcb-sync1 libxcb-xfixes0 libxcb-shape0 \\
    libxcb-randr0 libxcb-render-util0 \\
    libxkbcommon-x11-0 libxkbcommon0 \\
    libxcb-xinerama0 libxcb-cursor0 \\
    mesa-utils x11-apps && apt clean'''

    def generate_dockerfile(self):
        try:
            # Check if using default configuration
            if self.is_default_configuration():
                self.log_message("✅ Using original Dockerfile (default configuration)")
                self.log_message("💡 You can build directly without generating a custom Dockerfile!")
                return
            
            # Read the original Dockerfile
            with open('Dockerfile', 'r') as f:
                original_content = f.read()
            
            # Split into sections
            lines = original_content.split('\n')
            
            # Find the section boundaries
            base_section = []
            optional_section_start = None
            mandatory_section_start = None
            end_section = []
            
            in_optional = False
            in_mandatory = False
            
            for i, line in enumerate(lines):
                if 'Install pip for system Python' in line:
                    optional_section_start = i + 2  # Start after the RUN command
                elif 'Install DeSciOS Assistant' in line:
                    mandatory_section_start = i
                    in_optional = False
                    in_mandatory = True
                elif mandatory_section_start and 'Switch to deScier user' in line:
                    in_mandatory = False
                    
                if optional_section_start and not in_mandatory and not mandatory_section_start:
                    in_optional = True
                    
                if not in_optional and not in_mandatory:
                    if mandatory_section_start and i > mandatory_section_start:
                        end_section.append(line)
                    elif not mandatory_section_start:
                        base_section.append(line)
                        
            # Generate new Dockerfile content
            new_content = []
            
            # Add base section (everything before optional apps) but exclude JupyterLab
            base_end = optional_section_start - 2 if optional_section_start else len(base_section)
            for i, line in enumerate(lines[:base_end]):
                # Skip JupyterLab installation line
                if 'pip install --no-cache-dir jupyterlab' in line:
                    continue
                new_content.append(line)
            
            # Add mandatory python3-pip installation
            new_content.append("\n# Install pip for system Python (mandatory)")
            new_content.append("RUN apt update && apt install -y python3-pip")
            
            # Add essential Qt dependencies
            new_content.append("\n# Essential GUI dependencies for Qt/X11 applications")
            new_content.append(self.get_qt_dependencies())
            
            # Add selected applications (both built-in and custom)
            all_apps = self.get_all_applications()
            for app_id, selected in self.app_vars.items():
                if selected.get() and app_id in all_apps:
                    app_info = all_apps[app_id]
                    new_content.append(f"\n# {app_info['name']}")
                    if app_id == "cellmodeller":
                        new_content.append('''# CellModeller
# Install Qt5 and X11 dependencies for CellModeller GUI
''' + self.get_qt_dependencies() + '''

# Clone and install CellModeller
WORKDIR /opt
RUN git clone https://github.com/cellmodeller/CellModeller.git && \\
    cd /opt/CellModeller && pip install -e . && \\
    mkdir /opt/data && \\
    chown -R $USER:$USER /opt/data && \\
    echo '[Desktop Entry]\\nName=CellModeller\\nExec=bash -c "cd /opt && python CellModeller/Scripts/CellModellerGUI.py"\\nIcon=applications-science\\nType=Application\\nTerminal=true\\nCategories=Science;' \\
    > /usr/share/applications/cellmodeller.desktop && \\
    chmod 644 /usr/share/applications/cellmodeller.desktop && \\
    update-desktop-database /usr/share/applications''')
                    else:
                        new_content.append(app_info['dockerfile_section'])
            
            # Add mandatory DeSciOS Assistant section
            new_content.append('''
# Install DeSciOS Assistant
WORKDIR /opt
COPY descios_assistant /opt/descios_assistant
RUN cd /opt/descios_assistant && \\
    /usr/bin/python3 -m pip install --break-system-packages -r requirements.txt && \\
    chmod +x main.py && \\
    cp descios-assistant.desktop /usr/share/applications/ && \\
    chown -R $USER:$USER /opt/descios_assistant

# Install Talk to K Assistant
COPY talk_to_k /opt/talk_to_k
RUN cd /opt/talk_to_k && \\
    /usr/bin/python3 -m pip install --break-system-packages -r requirements.txt && \\
    chmod +x main.py && \\
    cp talk-to-k.desktop /usr/share/applications/ && \\
    chown -R $USER:$USER /opt/talk_to_k

# Install DeSci Assistant font
RUN apt-get update && apt-get install -y wget fontconfig && \\
    mkdir -p /usr/share/fonts/truetype/orbitron && \\
    wget -O /usr/share/fonts/truetype/orbitron/Orbitron.ttf https://github.com/google/fonts/raw/main/ofl/orbitron/Orbitron%5Bwght%5D.ttf && \\
    fc-cache -f -v

# Install IPFS CLI & Desktop (Mandatory)
RUN wget https://dist.ipfs.tech/kubo/v0.24.0/kubo_v0.24.0_linux-amd64.tar.gz && \\
    tar -xzf kubo_v0.24.0_linux-amd64.tar.gz && \\
    cd kubo && \\
    bash install.sh && \\
    cd .. && \\
    rm -rf kubo kubo_v0.24.0_linux-amd64.tar.gz

# Install IPFS Desktop (GUI)
RUN wget https://github.com/ipfs/ipfs-desktop/releases/download/v0.30.2/ipfs-desktop-0.30.2-linux-amd64.deb && \\
    apt install -y ./ipfs-desktop-0.30.2-linux-amd64.deb && \\
    rm ipfs-desktop-0.30.2-linux-amd64.deb

# Configure IPFS for automatic startup
RUN mkdir -p /home/$USER/.ipfs && \\
    chown -R $USER:$USER /home/$USER/.ipfs && \\
    echo 'export IPFS_PATH=/home/deScier/.ipfs' >> /home/$USER/.bashrc && \\
    echo 'export IPFS_PATH=/home/deScier/.ipfs' >> /root/.bashrc

# Copy IPFS status checker script
COPY check_ipfs.sh /usr/local/bin/check_ipfs.sh
RUN chmod +x /usr/local/bin/check_ipfs.sh

# Add IPFS status checker desktop entry
COPY ipfs-status.desktop /usr/share/applications/ipfs-status.desktop''')
            
            # Add the rest of the Dockerfile (OpenCL, user setup, etc.)
            # Find where the end section starts
            for i, line in enumerate(lines):
                if 'OpenCL configuration' in line:
                    new_content.extend(lines[i:])
                    break
            
            # Update Ollama models section
            models = [model.strip() for model in self.ollama_models.get('1.0', tk.END).strip().split('\n') if model.strip()]
            if models:
                # Find and replace Ollama pull commands
                for i, line in enumerate(new_content):
                    if 'ollama pull' in line and 'RUN ollama serve' in line:
                        pull_commands = ' && '.join([f'ollama pull {model}' for model in models])
                        new_content[i] = f'RUN ollama serve & sleep 5 && {pull_commands}'
                        break
            
            # Update user and password
            username = self.username_var.get()
            password = self.password_var.get()
            
            for i, line in enumerate(new_content):
                if line.startswith('ENV USER='):
                    new_content[i] = f'ENV USER={username}'
                elif line.startswith('ARG PASSWORD='):
                    new_content[i] = f'ARG PASSWORD={password}'
            
            # Write new Dockerfile
            output_path = 'Dockerfile.custom'
            with open(output_path, 'w') as f:
                f.write('\n'.join(new_content))
            
            self.log_message(f"✅ Generated custom Dockerfile: {output_path}")
            
            # Count selected applications
            selected_count = sum(var.get() for var in self.app_vars.values())
            custom_count = sum(var.get() for app_id, var in self.app_vars.items() if app_id.startswith('custom_'))
            
            self.log_message(f"Selected {selected_count} applications total")
            if custom_count > 0:
                self.log_message(f"Including {custom_count} custom applications 🧩")
            self.log_message(f"GPU support: {'Enabled' if self.gpu_enabled_var.get() else 'Disabled'}")
            
            # Update the Docker command display
            self.update_docker_command()
            
        except Exception as e:
            self.log_message(f"❌ Error generating Dockerfile: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate Dockerfile: {str(e)}")
            
    def build_image(self):
        def build_thread():
            try:
                self.log_message("🔨 Starting Docker build...")
                image_tag = self.image_tag_var.get()
                
                # Check if user wants default configuration
                if self.is_default_configuration():
                    # Use original Dockerfile for faster build
                    self.log_message("✨ Using default configuration - building from original Dockerfile")
                    dockerfile_path = 'Dockerfile'
                else:
                    # Check if custom Dockerfile exists
                    if not os.path.exists('Dockerfile.custom'):
                        self.log_message("❌ Please generate custom Dockerfile first")
                        return
                    dockerfile_path = 'Dockerfile.custom'
                    self.log_message("🔧 Using custom configuration - building from Dockerfile.custom")
                
                # Run docker build command
                process = subprocess.Popen(
                    ['docker', 'build', '-f', dockerfile_path, '-t', image_tag, '.'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Stream output
                for line in process.stdout:
                    self.log_message(line.strip())
                
                process.wait()
                
                if process.returncode == 0:
                    self.log_message(f"✅ Successfully built image: {image_tag}")
                    self.log_message("🚀 Ready to deploy! Check the deployment commands above.")
                    gpu_status = "with GPU support" if self.gpu_enabled_var.get() else "without GPU support"
                    self.log_message(f"📋 Image built {gpu_status}")
                    if dockerfile_path == 'Dockerfile':
                        self.log_message("⚡ Built using default configuration for maximum speed!")
                    else:
                        # Count custom apps
                        custom_count = sum(var.get() for app_id, var in self.app_vars.items() if app_id.startswith('custom_'))
                        if custom_count > 0:
                            self.log_message(f"🧩 Included {custom_count} custom applications!")
                else:
                    self.log_message(f"❌ Build failed with return code: {process.returncode}")
                    
            except Exception as e:
                self.log_message(f"❌ Build error: {str(e)}")
        
        # Run build in separate thread to avoid blocking UI
        threading.Thread(target=build_thread, daemon=True).start()
        
    def save_config(self):
        try:
            config = {
                'applications': {app_id: var.get() for app_id, var in self.app_vars.items()},
                'ollama_models': self.ollama_models.get('1.0', tk.END).strip(),
                'username': self.username_var.get(),
                'password': self.password_var.get(),
                'image_tag': self.image_tag_var.get(),
                'gpu_enabled': self.gpu_enabled_var.get()
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Configuration"
            )
            
            if filename:
                import json
                with open(filename, 'w') as f:
                    json.dump(config, f, indent=2)
                self.log_message(f"✅ Configuration saved to: {filename}")
                
        except Exception as e:
            self.log_message(f"❌ Error saving configuration: {str(e)}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def deploy_image(self):
        """Deploy the Docker image and open the web interface"""
        try:
            image_tag = self.image_tag_var.get()
            gpu_enabled = self.gpu_enabled_var.get()
            
            # Check if image exists
            check_cmd = ['docker', 'images', '-q', image_tag]
            result = subprocess.run(check_cmd, capture_output=True, text=True)
            
            if not result.stdout.strip():
                self.log_message(f"❌ Docker image '{image_tag}' not found. Please build the image first.")
                messagebox.showerror("Error", f"Docker image '{image_tag}' not found. Please build the image first.")
                return
            
            # Stop any existing container with the same name
            stop_cmd = ['docker', 'stop', 'descios']
            subprocess.run(stop_cmd, capture_output=True)
            
            remove_cmd = ['docker', 'rm', 'descios']
            subprocess.run(remove_cmd, capture_output=True)
            
            # Build the docker run command with IPFS ports
            if gpu_enabled:
                docker_cmd = [
                    'docker', 'run', '-d', '--gpus', 'all', 
                    '-p', '6080:6080', '-p', '5901:5901',
                    '-p', '4001:4001', '-p', '4001:4001/udp',
                    '-p', '5001:5001', '-p', '8080:8080', '-p', '9090:9090',
                    '--name', 'descios', image_tag
                ]
                self.log_message("🚀 Deploying with GPU support and IPFS ports...")
            else:
                docker_cmd = [
                    'docker', 'run', '-d', 
                    '-p', '6080:6080', '-p', '5901:5901',
                    '-p', '4001:4001', '-p', '4001:4001/udp',
                    '-p', '5001:5001', '-p', '8080:8080', '-p', '9090:9090',
                    '--name', 'descios', image_tag
                ]
                self.log_message("🚀 Deploying with IPFS ports...")
            
            # Run the container
            self.log_message(f"\n🚀 [Deploy] Running this command:")
            self.log_message(' '.join(docker_cmd))
            result = subprocess.run(docker_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()[:12]
                self.log_message(f"✅ Container started successfully: {container_id}")
                self.log_message("🌐 Opening web interface...")
                
                # Wait a moment for the container to start, then open browser
                def open_browser():
                    import time
                    time.sleep(3)
                    web_url = "http://localhost:6080/vnc.html"
                    try:
                        subprocess.run(['xdg-open', web_url], check=False)
                    except FileNotFoundError:
                        # Fallback for systems without xdg-open
                        try:
                            subprocess.run(['firefox', web_url], check=False)
                        except FileNotFoundError:
                            try:
                                subprocess.run(['chromium-browser', web_url], check=False)
                            except FileNotFoundError:
                                try:
                                    subprocess.run(['google-chrome', web_url], check=False)
                                except FileNotFoundError:
                                    self.log_message(f"💡 Please open manually: {web_url}")
                
                # Run browser opening in a separate thread
                threading.Thread(target=open_browser, daemon=True).start()
                
                self.log_message(f"🎉 DeSciOS is now running at: http://localhost:6080/vnc.html")
                self.log_message("🌐 IPFS Gateway: http://localhost:8080")
                self.log_message("🔧 IPFS API: http://localhost:5001")
                self.log_message("📁 IPFS Web UI: http://localhost:5001/webui")
                self.log_message("💡 To stop: docker stop descios")
                
                # Show info about custom apps if any
                custom_count = sum(var.get() for app_id, var in self.app_vars.items() if app_id.startswith('custom_'))
                if custom_count > 0:
                    self.log_message(f"🧩 Your {custom_count} custom applications are now available!")
                
            else:
                self.log_message(f"❌ Failed to start container: {result.stderr}")
                messagebox.showerror("Error", f"Failed to start container: {result.stderr}")
                
        except Exception as e:
            self.log_message(f"❌ Deploy error: {str(e)}")
            messagebox.showerror("Error", f"Deploy failed: {str(e)}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="DeSciOS Launcher - GUI for customizing and deploying DeSciOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  descios                    # Launch GUI
  descios --version          # Show version
  descios --help             # Show this help
  
DeSciOS is a containerized scientific computing environment.
Visit: https://github.com/GizmoQuest/DeSciOS
        """
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='DeSciOS Launcher 0.1.0'
    )
    
    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Run in command-line mode (not implemented yet)'
    )
    
    args = parser.parse_args()
    
    if args.no_gui:
        print("Command-line mode not implemented yet. Use GUI mode.")
        return 1
    
    # Check if we're in the right directory
    if not os.path.exists('Dockerfile'):
        print("Error: Dockerfile not found.")
        print("Please run from the DeSciOS directory, or use 'cd' to navigate there first.")
        return 1
        
    root = tk.Tk()
    app = DeSciOSLauncher(root)
    
    try:
        # Try to use the system theme
        root.tk.call('source', '/usr/share/themes/Adwaita/gtk-3.0/gtk.css')
    except:
        pass  # Fallback to default theme
    
    root.mainloop()
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main()) 