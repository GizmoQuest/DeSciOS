#!/usr/bin/env python3
"""
GuruCool - Decentralized Academic Collaboration Platform
A CoCalc-like environment for teachers and students using IPFS for communication
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import json
import os
import time
import hashlib
from pathlib import Path
import webbrowser
from datetime import datetime
# Remove ipfshttpclient import
# import ipfshttpclient  # REMOVE THIS LINE
import requests

class GuruCoolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GuruCool - Decentralized Academic Collaboration")
        self.root.geometry("1400x900")
        
        # Color scheme
        self.colors = {
            'primary': '#2563eb',
            'secondary': '#10b981', 
            'accent': '#f59e0b',
            'success': '#059669',
            'warning': '#d97706',
            'error': '#dc2626',
            'background': '#f8fafc',
            'surface': '#ffffff',
            'text': '#1f2937',
            'text_light': '#6b7280',
            'border': '#e5e7eb'
        }
        
        # Configure root
        self.root.configure(bg=self.colors['background'])
        
        # IPFS client
        self.ipfs_client = None
        self.ipfs_connected = False
        self.ipfs_api_url = None  # Will be set from settings
        
        # Current session data
        self.current_session = {
            'course_id': None,
            'user_role': None,  # 'teacher' or 'student'
            'user_id': None,
            'collaborators': []
        }
        
        # Course data
        self.courses = {}
        self.load_courses()
        
        self.setup_ui()
        self.connect_ipfs()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="🎓 GuruCool", 
                              font=('Arial', 24, 'bold'),
                              fg=self.colors['primary'],
                              bg=self.colors['background'])
        title_label.pack(side='left')
        
        subtitle_label = tk.Label(title_frame, text="Decentralized Academic Collaboration Platform",
                                 font=('Arial', 12),
                                 fg=self.colors['text_light'],
                                 bg=self.colors['background'])
        subtitle_label.pack(side='left', padx=(10, 0))
        
        # Status indicator
        self.status_label = tk.Label(title_frame, text="🔴 IPFS Disconnected",
                                    font=('Arial', 10),
                                    fg=self.colors['error'],
                                    bg=self.colors['background'])
        self.status_label.pack(side='right')
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Setup tabs
        self.setup_courses_tab()
        self.setup_collaboration_tab()
        self.setup_resources_tab()
        self.setup_settings_tab()

    def setup_courses_tab(self):
        courses_frame = ttk.Frame(self.notebook)
        self.notebook.add(courses_frame, text="📚 Courses")
        
        # Course management section
        course_mgmt_frame = ttk.LabelFrame(courses_frame, text="Course Management", padding=20)
        course_mgmt_frame.pack(fill='x', padx=20, pady=20)
        
        # Create/Join course section
        create_frame = ttk.Frame(course_mgmt_frame)
        create_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(create_frame, text="Course ID:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.course_id_var = tk.StringVar()
        ttk.Entry(create_frame, textvariable=self.course_id_var, width=30).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(create_frame, text="Role:").grid(row=0, column=2, sticky='w', padx=(0, 10))
        self.role_var = tk.StringVar(value="student")
        role_combo = ttk.Combobox(create_frame, textvariable=self.role_var, 
                                 values=["student", "teacher"], state="readonly", width=10)
        role_combo.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Button(create_frame, text="Join Course", 
                  command=self.join_course).grid(row=0, column=4, padx=(0, 10))
        ttk.Button(create_frame, text="Create Course", 
                  command=self.create_course).grid(row=0, column=5)
        
        # Current course info
        self.course_info_frame = ttk.LabelFrame(courses_frame, text="Current Course", padding=20)
        self.course_info_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.course_info_text = scrolledtext.ScrolledText(self.course_info_frame, height=8,
                                                         bg='white', fg=self.colors['text'])
        self.course_info_text.pack(fill='both', expand=True)
        
        # Course list
        courses_list_frame = ttk.LabelFrame(courses_frame, text="Available Courses", padding=20)
        courses_list_frame.pack(fill='both', expand=True, padx=20)
        
        # Treeview for courses
        columns = ('Course ID', 'Name', 'Teacher', 'Students', 'Last Activity')
        self.courses_tree = ttk.Treeview(courses_list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.courses_tree.heading(col, text=col)
            self.courses_tree.column(col, width=150)
        
        self.courses_tree.pack(fill='both', expand=True)
        self.courses_tree.bind('<Double-1>', self.on_course_select)
        
        # Refresh button
        ttk.Button(courses_list_frame, text="🔄 Refresh Courses", 
                  command=self.refresh_courses).pack(pady=(10, 0))

    def setup_collaboration_tab(self):
        collab_frame = ttk.Frame(self.notebook)
        self.notebook.add(collab_frame, text="👥 Collaboration")
        
        # Chat section
        chat_frame = ttk.LabelFrame(collab_frame, text="Real-time Chat", padding=20)
        chat_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(chat_frame, height=15,
                                                    bg='white', fg=self.colors['text'])
        self.chat_display.pack(fill='both', expand=True, pady=(0, 10))
        
        # Message input
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill='x')
        
        self.message_var = tk.StringVar()
        message_entry = ttk.Entry(input_frame, textvariable=self.message_var, width=60)
        message_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        message_entry.bind('<Return>', self.send_message)
        
        ttk.Button(input_frame, text="Send", command=self.send_message).pack(side='right')
        
        # File sharing section
        files_frame = ttk.LabelFrame(collab_frame, text="File Sharing", padding=20)
        files_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        file_buttons_frame = ttk.Frame(files_frame)
        file_buttons_frame.pack(fill='x')
        
        ttk.Button(file_buttons_frame, text="📁 Share File", 
                  command=self.share_file).pack(side='left', padx=(0, 10))
        ttk.Button(file_buttons_frame, text="📥 Download File", 
                  command=self.download_file).pack(side='left', padx=(0, 10))
        ttk.Button(file_buttons_frame, text="📋 View Shared Files", 
                  command=self.view_shared_files).pack(side='left')
        
        # Shared files list
        self.files_tree = ttk.Treeview(files_frame, columns=('File', 'Size', 'Uploader', 'Date'), 
                                      show='headings', height=6)
        for col in ('File', 'Size', 'Uploader', 'Date'):
            self.files_tree.heading(col, text=col)
            self.files_tree.column(col, width=150)
        self.files_tree.pack(fill='x', pady=(10, 0))

    def setup_resources_tab(self):
        resources_frame = ttk.Frame(self.notebook)
        self.notebook.add(resources_frame, text="📖 Resources")
        
        # Jupyter integration
        jupyter_frame = ttk.LabelFrame(resources_frame, text="Jupyter Integration", padding=20)
        jupyter_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(jupyter_frame, text="Launch collaborative Jupyter notebooks:").pack(anchor='w')
        
        jupyter_buttons = ttk.Frame(jupyter_frame)
        jupyter_buttons.pack(fill='x', pady=10)
        
        ttk.Button(jupyter_buttons, text="🚀 Launch JupyterLab", 
                  command=self.launch_jupyterlab).pack(side='left', padx=(0, 10))
        ttk.Button(jupyter_buttons, text="📊 Launch Jupyter Notebook", 
                  command=self.launch_jupyter_notebook).pack(side='left')
        
        # Educational tools
        tools_frame = ttk.LabelFrame(resources_frame, text="Educational Tools", padding=20)
        tools_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        tools_buttons = ttk.Frame(tools_frame)
        tools_buttons.pack(fill='x')
        
        ttk.Button(tools_buttons, text="📝 LaTeX Editor", 
                  command=self.launch_latex_editor).pack(side='left', padx=(0, 10))
        ttk.Button(tools_buttons, text="📈 R Studio", 
                  command=self.launch_rstudio).pack(side='left', padx=(0, 10))
        ttk.Button(tools_buttons, text="🐍 Spyder IDE", 
                  command=self.launch_spyder).pack(side='left')
        
        # Course materials
        materials_frame = ttk.LabelFrame(resources_frame, text="Course Materials", padding=20)
        materials_frame.pack(fill='both', expand=True, padx=20)
        
        materials_buttons = ttk.Frame(materials_frame)
        materials_buttons.pack(fill='x', pady=(0, 10))
        
        ttk.Button(materials_buttons, text="📚 Upload Material", 
                  command=self.upload_material).pack(side='left', padx=(0, 10))
        ttk.Button(materials_buttons, text="📖 View Materials", 
                  command=self.view_materials).pack(side='left')
        
        # Materials list
        self.materials_tree = ttk.Treeview(materials_frame, 
                                          columns=('Material', 'Type', 'Uploader', 'Date'),
                                          show='headings', height=8)
        for col in ('Material', 'Type', 'Uploader', 'Date'):
            self.materials_tree.heading(col, text=col)
            self.materials_tree.column(col, width=150)
        self.materials_tree.pack(fill='both', expand=True)

    def setup_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # User settings
        user_frame = ttk.LabelFrame(settings_frame, text="User Settings", padding=20)
        user_frame.pack(fill='x', padx=20, pady=20)
        
        user_grid = ttk.Frame(user_frame)
        user_grid.pack(fill='x')
        user_grid.grid_columnconfigure(1, weight=1)
        
        ttk.Label(user_grid, text="User ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.user_id_var = tk.StringVar(value=f"user_{int(time.time())}")
        ttk.Entry(user_grid, textvariable=self.user_id_var).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Label(user_grid, text="Display Name:").grid(row=1, column=0, sticky='w', pady=5)
        self.display_name_var = tk.StringVar(value="Anonymous")
        ttk.Entry(user_grid, textvariable=self.display_name_var).grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        # IPFS settings
        ipfs_frame = ttk.LabelFrame(settings_frame, text="IPFS Configuration", padding=20)
        ipfs_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        ipfs_grid = ttk.Frame(ipfs_frame)
        ipfs_grid.pack(fill='x')
        ipfs_grid.grid_columnconfigure(1, weight=1)
        
        ttk.Label(ipfs_grid, text="IPFS API URL:").grid(row=0, column=0, sticky='w', pady=5)
        self.ipfs_url_var = tk.StringVar(value="/ip4/127.0.0.1/tcp/5001")
        ttk.Entry(ipfs_grid, textvariable=self.ipfs_url_var).grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        ttk.Button(ipfs_grid, text="🔗 Connect", 
                  command=self.connect_ipfs).grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Course directory
        ttk.Label(ipfs_grid, text="Course Directory:").grid(row=1, column=0, sticky='w', pady=5)
        self.course_dir_var = tk.StringVar(value=str(Path.home() / "gurucool_courses"))
        ttk.Entry(ipfs_grid, textvariable=self.course_dir_var).grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=5)
        ttk.Button(ipfs_grid, text="📁 Browse", 
                  command=self.browse_course_dir).grid(row=1, column=2, padx=(10, 0), pady=5)
        
        # System info
        info_frame = ttk.LabelFrame(settings_frame, text="System Information", padding=20)
        info_frame.pack(fill='both', expand=True, padx=20)
        
        self.system_info_text = scrolledtext.ScrolledText(info_frame, height=10,
                                                        bg='white', fg=self.colors['text'])
        self.system_info_text.pack(fill='both', expand=True)
        
        # Update system info
        self.update_system_info()

    def call_ipfs_api(self, endpoint, method='get', params=None, files=None, data=None, stream=False):
        """Helper to call IPFS HTTP API"""
        url = self.ipfs_api_url.rstrip('/') + endpoint
        try:
            if method == 'get':
                resp = requests.get(url, params=params, stream=stream)
            elif method == 'post':
                resp = requests.post(url, params=params, files=files, data=data, stream=stream)
            else:
                raise ValueError('Unsupported HTTP method')
            resp.raise_for_status()
            return resp
        except Exception as e:
            self.log_message(f"❌ IPFS API error: {e}")
            return None

    def connect_ipfs(self):
        """Connect to IPFS daemon via HTTP API"""
        self.ipfs_api_url = self.ipfs_url_var.get()
        if self.ipfs_api_url.startswith('/ip4/'):
            # Convert multiaddr to HTTP URL
            # e.g. /ip4/127.0.0.1/tcp/5001 -> http://127.0.0.1:5001
            parts = self.ipfs_api_url.split('/')
            try:
                ip = parts[2]
                port = parts[4]
                self.ipfs_api_url = f"http://{ip}:{port}"
            except Exception:
                self.ipfs_api_url = "http://127.0.0.1:5001"
        try:
            resp = self.call_ipfs_api('/api/v0/version', method='post')
            if resp and resp.ok:
                self.ipfs_connected = True
                self.status_label.config(text="🟢 IPFS Connected", fg=self.colors['success'])
                self.log_message(f"✅ Connected to IPFS daemon: {resp.json().get('Version','?')}")
            else:
                raise Exception('No response from IPFS API')
        except Exception as e:
            self.ipfs_connected = False
            self.status_label.config(text="🔴 IPFS Disconnected", fg=self.colors['error'])
            self.log_message(f"❌ Failed to connect to IPFS: {str(e)}")

    def join_course(self):
        """Join an existing course"""
        course_id = self.course_id_var.get().strip()
        role = self.role_var.get()
        
        if not course_id:
            messagebox.showerror("Error", "Please enter a course ID")
            return
        
        if not self.ipfs_connected:
            messagebox.showerror("Error", "Please connect to IPFS first")
            return
        
        try:
            # Create course directory
            course_dir = Path(self.course_dir_var.get()) / course_id
            course_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize course data
            self.current_session['course_id'] = course_id
            self.current_session['user_role'] = role
            self.current_session['user_id'] = self.user_id_var.get()
            
            # Create or load course data
            course_file = course_dir / "course_data.json"
            if course_file.exists():
                with open(course_file, 'r') as f:
                    course_data = json.load(f)
            else:
                course_data = {
                    'course_id': course_id,
                    'created_by': self.current_session['user_id'],
                    'created_at': datetime.now().isoformat(),
                    'students': [],
                    'teachers': [],
                    'materials': [],
                    'chat_history': [],
                    'shared_files': []
                }
            
            # Add user to course
            if role == 'teacher':
                if self.current_session['user_id'] not in course_data['teachers']:
                    course_data['teachers'].append(self.current_session['user_id'])
            else:
                if self.current_session['user_id'] not in course_data['students']:
                    course_data['students'].append(self.current_session['user_id'])
            
            # Save course data
            with open(course_file, 'w') as f:
                json.dump(course_data, f, indent=2)
            
            # Upload to IPFS
            self.upload_course_data(course_dir)
            
            self.log_message(f"✅ Joined course: {course_id} as {role}")
            self.update_course_info()
            self.refresh_courses()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to join course: {str(e)}")

    def create_course(self):
        """Create a new course"""
        course_id = self.course_id_var.get().strip()
        
        if not course_id:
            messagebox.showerror("Error", "Please enter a course ID")
            return
        
        if not self.ipfs_connected:
            messagebox.showerror("Error", "Please connect to IPFS first")
            return
        
        try:
            # Create course directory
            course_dir = Path(self.course_dir_var.get()) / course_id
            if course_dir.exists():
                messagebox.showerror("Error", "Course already exists")
                return
            
            course_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize course data
            course_data = {
                'course_id': course_id,
                'name': f"Course {course_id}",
                'created_by': self.user_id_var.get(),
                'created_at': datetime.now().isoformat(),
                'students': [],
                'teachers': [self.user_id_var.get()],
                'materials': [],
                'chat_history': [],
                'shared_files': []
            }
            
            # Save course data
            course_file = course_dir / "course_data.json"
            with open(course_file, 'w') as f:
                json.dump(course_data, f, indent=2)
            
            # Upload to IPFS
            self.upload_course_data(course_dir)
            
            self.current_session['course_id'] = course_id
            self.current_session['user_role'] = 'teacher'
            self.current_session['user_id'] = self.user_id_var.get()
            
            self.log_message(f"✅ Created course: {course_id}")
            self.update_course_info()
            self.refresh_courses()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create course: {str(e)}")

    def upload_course_data(self, course_dir):
        """Upload course data to IPFS using HTTP API"""
        if not self.ipfs_connected:
            return None
        try:
            # Tar the directory for upload
            import tarfile, io
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode='w'):
                for root, dirs, files in os.walk(course_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, start=course_dir)
                        tar_stream.seek(0, io.SEEK_END)
                        tar_stream.write(b'')
                        tar_stream.flush()
                        tar_stream.seek(0, io.SEEK_END)
                        tar_stream.truncate()
                        tar_stream.seek(0)
                        with open(full_path, 'rb') as f:
                            info = tarfile.TarInfo(name=arcname)
                            f_bytes = f.read()
                            info.size = len(f_bytes)
                            tar_stream.write(tarfile.TarInfo(name=arcname).tobuf())
                            tar_stream.write(f_bytes)
            tar_stream.seek(0)
            files = {'file': ('course_data.tar', tar_stream.getvalue())}
            resp = self.call_ipfs_api('/api/v0/add', method='post', params={'recursive': 'true', 'wrap-with-directory': 'true'}, files=files)
            if resp and resp.ok:
                # The last line is the directory hash
                results = [json.loads(line) for line in resp.text.strip().split('\n') if line.strip()]
                course_hash = results[-1]['Hash']
                # Optionally publish to IPNS
                self.call_ipfs_api('/api/v0/name/publish', method='post', params={'arg': f'/ipfs/{course_hash}'})
                self.log_message(f"📤 Course data uploaded to IPFS: {course_hash}")
                return course_hash
            else:
                raise Exception('Failed to upload to IPFS')
        except Exception as e:
            self.log_message(f"❌ Failed to upload course data: {str(e)}")
            return None

    def send_message(self, event=None):
        """Send a message to the course chat"""
        message = self.message_var.get().strip()
        if not message:
            return
        
        if not self.current_session['course_id']:
            messagebox.showerror("Error", "Please join a course first")
            return
        
        try:
            # Create message data
            message_data = {
                'user_id': self.current_session['user_id'],
                'display_name': self.display_name_var.get(),
                'role': self.current_session['user_role'],
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add to chat display
            timestamp = datetime.now().strftime("%H:%M")
            role_emoji = "👨‍🏫" if self.current_session['user_role'] == 'teacher' else "👨‍🎓"
            self.chat_display.insert(tk.END, f"[{timestamp}] {role_emoji} {self.display_name_var.get()}: {message}\n")
            self.chat_display.see(tk.END)
            
            # Save to course data
            course_dir = Path(self.course_dir_var.get()) / self.current_session['course_id']
            course_file = course_dir / "course_data.json"
            
            if course_file.exists():
                with open(course_file, 'r') as f:
                    course_data = json.load(f)
                
                course_data['chat_history'].append(message_data)
                
                with open(course_file, 'w') as f:
                    json.dump(course_data, f, indent=2)
                
                # Upload to IPFS
                self.upload_course_data(course_dir)
            
            # Clear input
            self.message_var.set("")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")

    def share_file(self):
        """Share a file with the course using IPFS HTTP API"""
        if not self.current_session['course_id']:
            messagebox.showerror("Error", "Please join a course first")
            return
        filename = filedialog.askopenfilename(title="Select file to share")
        if not filename:
            return
        try:
            file_path = Path(filename)
            # Copy file to course directory
            course_dir = Path(self.course_dir_var.get()) / self.current_session['course_id']
            shared_dir = course_dir / "shared_files"
            shared_dir.mkdir(exist_ok=True)
            dest_path = shared_dir / file_path.name
            import shutil
            shutil.copy2(file_path, dest_path)
            # Upload to IPFS
            if self.ipfs_connected:
                with open(dest_path, 'rb') as f:
                    files = {'file': (file_path.name, f)}
                    resp = self.call_ipfs_api('/api/v0/add', method='post', files=files)
                    if resp and resp.ok:
                        file_hash = resp.json()['Hash']
                        # Add to course data
                        course_file = course_dir / "course_data.json"
                        if course_file.exists():
                            with open(course_file, 'r') as f:
                                course_data = json.load(f)
                            file_info = {
                                'name': file_path.name,
                                'size': file_path.stat().st_size,
                                'uploader': self.current_session['user_id'],
                                'date': datetime.now().isoformat(),
                                'ipfs_hash': file_hash
                            }
                            course_data['shared_files'].append(file_info)
                            with open(course_file, 'w') as f:
                                json.dump(course_data, f, indent=2)
                            # Upload updated course data
                            self.upload_course_data(course_dir)
                            self.log_message(f"📁 File shared: {file_path.name} (IPFS: {file_hash})")
                            self.refresh_shared_files()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to share file: {str(e)}")

    def download_file(self):
        """Download a shared file from IPFS using HTTP API"""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file to download")
            return
        item = self.files_tree.item(selection[0])
        file_info = item['values']
        try:
            # Download from IPFS
            if self.ipfs_connected and len(file_info) > 4:
                file_hash = file_info[4]  # IPFS hash
                resp = self.call_ipfs_api('/api/v0/cat', params={'arg': file_hash}, stream=True)
                if resp and resp.ok:
                    downloads_dir = Path.home() / "Downloads" / "gurucool"
                    downloads_dir.mkdir(parents=True, exist_ok=True)
                    out_path = downloads_dir / file_info[0]
                    with open(out_path, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    self.log_message(f"📥 File downloaded: {file_info[0]}")
                    messagebox.showinfo("Success", f"File downloaded to: {downloads_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download file: {str(e)}")

    def view_shared_files(self):
        """Refresh the shared files list"""
        if not self.current_session['course_id']:
            return
        
        try:
            # Clear existing items
            for item in self.files_tree.get_children():
                self.files_tree.delete(item)
            
            # Load course data
            course_dir = Path(self.course_dir_var.get()) / self.current_session['course_id']
            course_file = course_dir / "course_data.json"
            
            if course_file.exists():
                with open(course_file, 'r') as f:
                    course_data = json.load(f)
                
                # Add files to tree
                for file_info in course_data.get('shared_files', []):
                    size_mb = file_info.get('size', 0) / (1024 * 1024)
                    self.files_tree.insert('', 'end', values=(
                        file_info.get('name', 'Unknown'),
                        f"{size_mb:.2f} MB",
                        file_info.get('uploader', 'Unknown'),
                        file_info.get('date', 'Unknown')[:10],
                        file_info.get('ipfs_hash', '')
                    ))
        
        except Exception as e:
            self.log_message(f"❌ Failed to load shared files: {str(e)}")

    def refresh_shared_files(self):
        """Refresh shared files display"""
        self.view_shared_files()

    def launch_jupyterlab(self):
        """Launch JupyterLab"""
        try:
            subprocess.Popen(['jupyter', 'lab', '--no-browser', '--port=8888'])
            webbrowser.open('http://localhost:8888')
            self.log_message("🚀 JupyterLab launched")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch JupyterLab: {str(e)}")

    def launch_jupyter_notebook(self):
        """Launch Jupyter Notebook"""
        try:
            subprocess.Popen(['jupyter', 'notebook', '--no-browser', '--port=8889'])
            webbrowser.open('http://localhost:8889')
            self.log_message("📊 Jupyter Notebook launched")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Jupyter Notebook: {str(e)}")

    def launch_latex_editor(self):
        """Launch LaTeX editor"""
        try:
            subprocess.Popen(['texstudio'])
            self.log_message("📝 LaTeX editor launched")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch LaTeX editor: {str(e)}")

    def launch_rstudio(self):
        """Launch RStudio"""
        try:
            subprocess.Popen(['rstudio'])
            self.log_message("📈 RStudio launched")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch RStudio: {str(e)}")

    def launch_spyder(self):
        """Launch Spyder IDE"""
        try:
            subprocess.Popen(['spyder'])
            self.log_message("🐍 Spyder IDE launched")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Spyder IDE: {str(e)}")

    def upload_material(self):
        """Upload course material"""
        if not self.current_session['course_id']:
            messagebox.showerror("Error", "Please join a course first")
            return
        
        filename = filedialog.askopenfilename(title="Select material to upload")
        if not filename:
            return
        
        try:
            file_path = Path(filename)
            
            # Copy to course materials
            course_dir = Path(self.course_dir_var.get()) / self.current_session['course_id']
            materials_dir = course_dir / "materials"
            materials_dir.mkdir(exist_ok=True)
            
            dest_path = materials_dir / file_path.name
            import shutil
            shutil.copy2(file_path, dest_path)
            
            # Add to course data
            course_file = course_dir / "course_data.json"
            if course_file.exists():
                with open(course_file, 'r') as f:
                    course_data = json.load(f)
                
                material_info = {
                    'name': file_path.name,
                    'type': file_path.suffix[1:] if file_path.suffix else 'unknown',
                    'uploader': self.current_session['user_id'],
                    'date': datetime.now().isoformat(),
                    'size': file_path.stat().st_size
                }
                
                course_data['materials'].append(material_info)
                
                with open(course_file, 'w') as f:
                    json.dump(course_data, f, indent=2)
                
                # Upload to IPFS
                self.upload_course_data(course_dir)
                
                self.log_message(f"📚 Material uploaded: {file_path.name}")
                self.view_materials()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload material: {str(e)}")

    def view_materials(self):
        """View course materials"""
        if not self.current_session['course_id']:
            return
        
        try:
            # Clear existing items
            for item in self.materials_tree.get_children():
                self.materials_tree.delete(item)
            
            # Load course data
            course_dir = Path(self.course_dir_var.get()) / self.current_session['course_id']
            course_file = course_dir / "course_data.json"
            
            if course_file.exists():
                with open(course_file, 'r') as f:
                    course_data = json.load(f)
                
                # Add materials to tree
                for material in course_data.get('materials', []):
                    size_mb = material.get('size', 0) / (1024 * 1024)
                    self.materials_tree.insert('', 'end', values=(
                        material.get('name', 'Unknown'),
                        material.get('type', 'Unknown').upper(),
                        material.get('uploader', 'Unknown'),
                        material.get('date', 'Unknown')[:10]
                    ))
        
        except Exception as e:
            self.log_message(f"❌ Failed to load materials: {str(e)}")

    def browse_course_dir(self):
        """Browse for course directory"""
        directory = filedialog.askdirectory(title="Select Course Directory")
        if directory:
            self.course_dir_var.set(directory)

    def update_course_info(self):
        """Update the course information display"""
        if not self.current_session['course_id']:
            self.course_info_text.delete('1.0', tk.END)
            self.course_info_text.insert('1.0', "No active course")
            return
        
        try:
            course_dir = Path(self.course_dir_var.get()) / self.current_session['course_id']
            course_file = course_dir / "course_data.json"
            
            if course_file.exists():
                with open(course_file, 'r') as f:
                    course_data = json.load(f)
                
                info_text = f"""Course ID: {course_data.get('course_id', 'Unknown')}
Name: {course_data.get('name', 'Unnamed Course')}
Created by: {course_data.get('created_by', 'Unknown')}
Created: {course_data.get('created_at', 'Unknown')[:10]}

Teachers: {', '.join(course_data.get('teachers', []))}
Students: {', '.join(course_data.get('students', []))}

Materials: {len(course_data.get('materials', []))} files
Shared Files: {len(course_data.get('shared_files', []))} files
Chat Messages: {len(course_data.get('chat_history', []))} messages

Your Role: {self.current_session['user_role']}
Your ID: {self.current_session['user_id']}"""
                
                self.course_info_text.delete('1.0', tk.END)
                self.course_info_text.insert('1.0', info_text)
            
        except Exception as e:
            self.course_info_text.delete('1.0', tk.END)
            self.course_info_text.insert('1.0', f"Error loading course info: {str(e)}")

    def refresh_courses(self):
        """Refresh the courses list"""
        try:
            # Clear existing items
            for item in self.courses_tree.get_children():
                self.courses_tree.delete(item)
            
            # Scan for courses
            course_base_dir = Path(self.course_dir_var.get())
            if course_base_dir.exists():
                for course_dir in course_base_dir.iterdir():
                    if course_dir.is_dir():
                        course_file = course_dir / "course_data.json"
                        if course_file.exists():
                            with open(course_file, 'r') as f:
                                course_data = json.load(f)
                            
                            # Get last activity
                            chat_history = course_data.get('chat_history', [])
                            last_activity = "Never"
                            if chat_history:
                                last_msg = chat_history[-1]
                                last_activity = last_msg.get('timestamp', 'Unknown')[:10]
                            
                            self.courses_tree.insert('', 'end', values=(
                                course_data.get('course_id', 'Unknown'),
                                course_data.get('name', 'Unnamed Course'),
                                course_data.get('created_by', 'Unknown'),
                                len(course_data.get('students', [])),
                                last_activity
                            ))
        
        except Exception as e:
            self.log_message(f"❌ Failed to refresh courses: {str(e)}")

    def on_course_select(self, event):
        """Handle course selection"""
        selection = self.courses_tree.selection()
        if selection:
            item = self.courses_tree.item(selection[0])
            course_id = item['values'][0]
            self.course_id_var.set(course_id)

    def update_system_info(self):
        """Update system information display"""
        try:
            info_text = f"""GuruCool Version: 1.0.0
Python Version: {subprocess.check_output(['python3', '--version']).decode().strip()}
IPFS Status: {'Connected' if self.ipfs_connected else 'Disconnected'}
IPFS API: {self.ipfs_url_var.get()}
Course Directory: {self.course_dir_var.get()}

Available Tools:
• JupyterLab - Interactive notebooks
• Jupyter Notebook - Classic notebook interface
• LaTeX Editor - Document preparation
• RStudio - Statistical computing
• Spyder IDE - Python development

IPFS Features:
• Decentralized file sharing
• Course data persistence
• Collaborative document editing
• Real-time chat synchronization

For help, visit: https://github.com/GizmoQuest/DeSciOS"""
            
            self.system_info_text.delete('1.0', tk.END)
            self.system_info_text.insert('1.0', info_text)
            
        except Exception as e:
            self.system_info_text.delete('1.0', tk.END)
            self.system_info_text.insert('1.0', f"Error loading system info: {str(e)}")

    def load_courses(self):
        """Load existing courses"""
        try:
            course_base_dir = Path(self.course_dir_var.get() if hasattr(self, 'course_dir_var') else str(Path.home() / "gurucool_courses"))
            if course_base_dir.exists():
                for course_dir in course_base_dir.iterdir():
                    if course_dir.is_dir():
                        course_file = course_dir / "course_data.json"
                        if course_file.exists():
                            with open(course_file, 'r') as f:
                                course_data = json.load(f)
                                self.courses[course_data['course_id']] = course_data
        except Exception as e:
            self.log_message(f"❌ Failed to load courses: {str(e)}")

    def log_message(self, message):
        """Log a message to the system"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

def main():
    root = tk.Tk()
    app = GuruCoolApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 