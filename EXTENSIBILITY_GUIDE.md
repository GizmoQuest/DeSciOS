# DeSciOS Extensibility Guide

## 🧩 Custom Applications & Plugin System

DeSciOS now supports a comprehensive extensibility system that allows researchers to easily add their own applications and tools. This guide covers everything you need to know about extending DeSciOS.

## ✨ What's New

### 1. Custom Applications Tab
- **Template-based Builder**: Create applications using pre-built templates
- **Real-time Preview**: See generated Dockerfile commands as you type
- **Plugin Management**: Load and manage external application definitions
- **Form Validation**: Guided creation with error checking

### 2. Plugin System
- **YAML/JSON Support**: Define applications in standard formats
- **Hot Loading**: Plugins are loaded automatically from the `descios_plugins/` directory
- **Community Sharing**: Easy sharing and distribution of application definitions

### 3. Installation Templates
- **Python Package**: `pip install` for Python libraries
- **APT Package**: `apt install` for system packages
- **GitHub Release**: Download and install from GitHub releases
- **Web Application**: Create desktop shortcuts for web tools
- **Custom Commands**: Write your own Dockerfile instructions

## 🚀 Getting Started

### Prerequisites
```bash
# Install YAML support for plugins
pip install -r descios_launcher/requirements.txt
```

### Launch the Extended Launcher
```bash
python3 descios_launcher/main.py
```

## 📝 Creating Custom Applications

### Method 1: GUI Template Builder (Recommended for Beginners)

1. **Open DeSciOS Launcher**
2. **Go to "🧩 Custom Apps" tab**
3. **Choose a template from the dropdown**
4. **Fill in the form fields**
5. **Preview the generated Dockerfile**
6. **Save your application**

#### Example: Adding a Python Package
1. Select "Python Package" template
2. App ID: `scikit_learn`
3. Name: `Scikit-learn`
4. Description: `Machine learning library for Python`
5. Package: `scikit-learn`
6. Click "💾 Save Application"

### Method 2: Manual Plugin Files (Advanced Users)

Create a YAML file in `descios_plugins/`:

```yaml
# my_tools.yaml
tensorflow:
  name: "TensorFlow"
  description: "Deep learning framework"
  dockerfile_section: "RUN pip install --no-cache-dir tensorflow"
  enabled: false

blast_plus:
  name: "NCBI BLAST+"
  description: "Sequence similarity search tool"
  dockerfile_section: |
    RUN apt update && apt install -y ncbi-blast+ && \
        echo '[Desktop Entry]\nName=BLAST+\nExec=gnome-terminal -- blastn -help\nIcon=applications-science\nType=Application\nCategories=Science;' \
        > /usr/share/applications/blast.desktop
  enabled: false
```

## 🔧 Template Reference

### Python Package Template
```yaml
app_id:
  name: "Package Name"
  description: "Brief description"
  dockerfile_section: "RUN pip install --no-cache-dir {package}"
  enabled: false
```

**Required Fields:**
- `package`: Python package name (e.g., `numpy`, `pandas`)

### APT Package Template
```yaml
app_id:
  name: "Package Name"
  description: "Brief description"
  dockerfile_section: "RUN apt update && apt install -y {packages}"
  enabled: false
```

**Required Fields:**
- `packages`: Space-separated package names (e.g., `git vim curl`)

### GitHub Release Template
```yaml
app_id:
  name: "Tool Name"
  description: "Brief description"
  dockerfile_section: |
    # Install {name}
    RUN wget {download_url} && \
        tar -xzf {archive_name} -C /opt && \
        rm {archive_name} && \
        ln -s /opt/{app_dir}/{executable} /usr/local/bin/{app_name} && \
        echo '[Desktop Entry]\nName={name}\nExec={app_name}\nIcon=applications-science\nType=Application\nCategories=Science;' \
        > /usr/share/applications/{app_id}.desktop
  enabled: false
```

**Required Fields:**
- `download_url`: Direct download URL for the release
- `archive_name`: Name of the downloaded file
- `app_dir`: Directory name after extraction
- `executable`: Path to executable within app_dir
- `app_name`: Command name for /usr/local/bin

### Web Application Template
```yaml
app_id:
  name: "App Name"
  description: "Brief description"
  dockerfile_section: |
    # {name} (via Browser)
    RUN echo '[Desktop Entry]\nName={name}\nExec=firefox {url}\nIcon=applications-internet\nType=Application\nCategories={categories};' \
        > /usr/share/applications/{app_id}.desktop
  enabled: false
```

**Required Fields:**
- `url`: Web application URL
- `categories`: Desktop categories (e.g., `Science`, `Development`)

### Custom Commands Template
```yaml
app_id:
  name: "Custom Tool"
  description: "Brief description"
  dockerfile_section: "{custom_commands}"
  enabled: false
```

**Required Fields:**
- `custom_commands`: Multi-line Dockerfile commands

## 📁 Plugin Directory Structure

```
descios_plugins/
├── README.md                    # Plugin documentation
├── example_python_packages.yaml # Python library examples
├── example_bioinformatics.yaml  # Bioinformatics tools
├── my_research_tools.yaml       # Your custom tools
└── community_contributions.yaml  # Shared community plugins
```

## 🎯 Best Practices

### 1. Application Naming
- Use descriptive `app_id`: `blast_plus`, `my_analysis_tool`
- Clear display names: "NCBI BLAST+", "My Analysis Tool"
- Concise descriptions: Focus on the tool's primary purpose

### 2. Dockerfile Best Practices
- **Clean up after installation**: Remove temporary files and caches
- **Use specific versions**: Pin package versions for reproducibility
- **Create desktop entries**: For GUI applications, add `.desktop` files
- **Set proper permissions**: Use `chown` and `chmod` as needed

### 3. Testing
- **Test locally**: Verify your Dockerfile commands work
- **Check dependencies**: Ensure all required packages are available
- **Validate syntax**: Use YAML validators for plugin files

### 4. Documentation
- **Include examples**: Show how to use your tools
- **Document requirements**: List any special setup needed
- **Provide context**: Explain why the tool is useful

## 🌐 Community Sharing

### Sharing Your Plugins
1. **Create well-documented plugin files**
2. **Test thoroughly with different configurations**
3. **Submit to the DeSciOS community repository**
4. **Include usage examples and documentation**

### Plugin Repositories
- **Official Examples**: Built-in example plugins
- **Community Hub**: Shared community contributions
- **Research-Specific**: Domain-specific plugin collections

## 🔍 Troubleshooting

### Common Issues

**Plugin not loading?**
```bash
# Check YAML syntax
python3 -c "import yaml; yaml.safe_load(open('my_plugin.yaml'))"

# Verify required fields
python3 -c "
import yaml
data = yaml.safe_load(open('my_plugin.yaml'))
for app_id, app in data.items():
    required = ['name', 'description', 'dockerfile_section']
    missing = [f for f in required if f not in app]
    if missing:
        print(f'{app_id} missing: {missing}')
"
```

**Application not installing?**
- Test Dockerfile commands manually in a container
- Check for missing dependencies
- Verify download URLs are accessible
- Ensure proper escape sequences in multi-line strings

**Desktop entry not appearing?**
- Use absolute paths in `Exec` commands
- Include proper `Icon` and `Categories`
- Call `update-desktop-database` if needed

### Debug Mode
```bash
# Enable debug output
PYTHONPATH=. python3 -c "
import descios_launcher.main as launcher
app = launcher.DeSciOSLauncher()
app.load_custom_applications()
print('Custom apps loaded:', len(app.custom_applications))
for app_id, app_info in app.custom_applications.items():
    print(f'  {app_id}: {app_info[\"name\"]}')
"
```

## 📈 Advanced Features

### Conditional Installation
```yaml
gpu_accelerated_tool:
  name: "GPU Accelerated Tool"
  description: "Tool that requires GPU support"
  dockerfile_section: |
    # Only install if GPU support is available
    RUN if [ "$GPU_ENABLED" = "true" ]; then \
        pip install --no-cache-dir gpu-accelerated-package; \
    fi
  enabled: false
```

### Multi-Step Installation
```yaml
complex_tool:
  name: "Complex Research Tool"
  description: "Tool requiring multiple installation steps"
  dockerfile_section: |
    # Step 1: Install dependencies
    RUN apt update && apt install -y build-essential cmake
    
    # Step 2: Download source
    WORKDIR /tmp
    RUN git clone https://github.com/example/tool.git
    
    # Step 3: Build and install
    WORKDIR /tmp/tool
    RUN mkdir build && cd build && \
        cmake .. && make -j$(nproc) && make install
    
    # Step 4: Clean up
    WORKDIR /
    RUN rm -rf /tmp/tool
    
    # Step 5: Create desktop entry
    RUN echo '[Desktop Entry]\nName=Research Tool\nExec=research-tool\nIcon=applications-science\nType=Application\nCategories=Science;' \
        > /usr/share/applications/research-tool.desktop
  enabled: false
```

## 🔮 Future Enhancements

The extensibility system is designed to grow with the community:

1. **Template Marketplace**: Browse and install templates from the community
2. **Dependency Management**: Automatic resolution of application dependencies
3. **Version Management**: Support for multiple versions of the same tool
4. **Build Caching**: Smart caching to speed up builds with many custom apps
5. **Integration Testing**: Automated testing of plugin compatibility

## 🤝 Contributing

We welcome contributions to improve the extensibility system:

1. **Templates**: Submit new installation templates
2. **Plugins**: Share useful application definitions
3. **Documentation**: Improve guides and examples
4. **Features**: Propose and implement new extensibility features

## 📚 Examples Gallery

### Research Domain Plugins

#### Bioinformatics
```yaml
# bioinformatics.yaml
samtools:
  name: "SAMtools"
  description: "Tools for manipulating SAM/BAM files"
  dockerfile_section: "RUN apt update && apt install -y samtools"
  enabled: false

bedtools:
  name: "BEDTools"
  description: "Toolset for genome arithmetic"
  dockerfile_section: "RUN apt update && apt install -y bedtools"
  enabled: false
```

#### Machine Learning
```yaml
# ml_stack.yaml
pytorch:
  name: "PyTorch"
  description: "Deep learning framework"
  dockerfile_section: "RUN pip install --no-cache-dir torch torchvision"
  enabled: false

jupyter_extensions:
  name: "Jupyter Extensions"
  description: "Useful Jupyter notebook extensions"
  dockerfile_section: |
    RUN pip install --no-cache-dir jupyter_contrib_nbextensions && \
        jupyter contrib nbextension install --system
  enabled: false
```

#### Chemistry
```yaml
# chemistry.yaml
openbabel:
  name: "Open Babel"
  description: "Chemical toolbox for format conversion"
  dockerfile_section: "RUN apt update && apt install -y openbabel"
  enabled: false

rdkit:
  name: "RDKit"
  description: "Cheminformatics toolkit"
  dockerfile_section: "RUN pip install --no-cache-dir rdkit"
  enabled: false
```

---

**Ready to extend DeSciOS?** Start with the GUI template builder and gradually explore more advanced plugin creation techniques. The extensibility system grows with your needs and expertise level! 