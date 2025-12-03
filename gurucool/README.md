# GuruCool - Decentralized Academic Collaboration Platform

GuruCool is a CoCalc-like collaborative platform built for DeSciOS that enables teachers and students to communicate and collaborate in an academic environment using IPFS (InterPlanetary File System) for decentralized data storage and sharing.

## 🎓 Features

### Core Collaboration Features
- **Real-time Chat**: Instant messaging between teachers and students
- **File Sharing**: Decentralized file sharing using IPFS
- **Course Management**: Create and join academic courses
- **Role-based Access**: Separate interfaces for teachers and students
- **Course Materials**: Upload and share educational resources

### Educational Tools Integration
- **JupyterLab**: Launch collaborative Jupyter notebooks
- **Jupyter Notebook**: Classic notebook interface
- **LaTeX Editor**: Document preparation and typesetting
- **RStudio**: Statistical computing environment
- **Spyder IDE**: Python development environment

### Decentralized Features
- **IPFS Integration**: All course data stored on IPFS
- **Decentralized Storage**: No central server required
- **Data Persistence**: Course data persists across sessions
- **Peer-to-Peer**: Direct communication between participants

## 🚀 Getting Started

### Prerequisites
- DeSciOS environment with IPFS installed
- IPFS daemon running locally
- Python 3.8+ with required dependencies

### Installation
GuruCool is automatically installed as part of DeSciOS. To launch:

1. **From Desktop**: Navigate to Education category and click "GuruCool"
2. **From Terminal**: Run `/usr/bin/python3 /opt/gurucool/main.py`

### First Time Setup
1. **Connect to IPFS**: Click "Connect" in the Settings tab
2. **Configure User**: Set your User ID and Display Name
3. **Set Course Directory**: Choose where course data will be stored locally

## 📚 Using GuruCool

### Creating a Course
1. Go to the "Courses" tab
2. Enter a unique Course ID
3. Select "teacher" role
4. Click "Create Course"

### Joining a Course
1. Go to the "Courses" tab
2. Enter the Course ID
3. Select your role (student/teacher)
4. Click "Join Course"

### Real-time Collaboration
- **Chat**: Use the chat interface in the "Collaboration" tab
- **File Sharing**: Upload files that are automatically shared via IPFS
- **Materials**: Share course materials in the "Resources" tab

### Educational Tools
- **JupyterLab**: Click "Launch JupyterLab" for interactive notebooks
- **RStudio**: Click "Launch R Studio" for statistical computing
- **LaTeX**: Click "LaTeX Editor" for document preparation

## 🔧 Configuration

### IPFS Settings
- **API URL**: Default is `/ip4/127.0.0.1/tcp/5001`
- **Connection**: Click "Connect" to establish IPFS connection
- **Status**: Green indicator shows successful connection

### User Settings
- **User ID**: Unique identifier for your account
- **Display Name**: Name shown in chat and course lists
- **Course Directory**: Local storage location for course data

## 📁 File Structure

```
/opt/gurucool/
├── main.py              # Main application
├── requirements.txt     # Python dependencies
├── gurucool.desktop    # Desktop entry
└── README.md           # This file

~/.local/share/gurucool/
└── courses/            # Local course data
    └── {course_id}/
        ├── course_data.json
        ├── materials/
        └── shared_files/
```

## 🔗 IPFS Integration

### How IPFS is Used
1. **Course Data**: All course information stored on IPFS
2. **File Sharing**: Files uploaded to IPFS with hash-based addressing
3. **Chat History**: Messages synchronized via IPFS
4. **Materials**: Educational resources distributed via IPFS

### IPFS Commands Used
- `ipfs add`: Upload files and directories
- `ipfs get`: Download files by hash
- `ipfs name publish`: Publish course data for discovery
- `ipfs cat`: Retrieve file contents

## 🎯 Use Cases

### For Teachers
- Create and manage academic courses
- Share lecture materials and assignments
- Monitor student participation
- Provide real-time feedback
- Collaborate with other educators

### For Students
- Join courses and participate in discussions
- Access shared educational resources
- Submit assignments via file sharing
- Collaborate with peers on projects
- Use integrated educational tools

### Academic Scenarios
- **Remote Learning**: Decentralized education without central servers
- **Research Collaboration**: Share data and findings via IPFS
- **Open Education**: Public course materials accessible to all
- **Academic Publishing**: Decentralized publication of educational content

## 🔒 Security & Privacy

### Data Privacy
- **Local Storage**: Course data stored locally by default
- **IPFS Encryption**: Optional encryption for sensitive data
- **User Control**: Users control what data is shared
- **No Central Database**: No central authority collecting data

### Access Control
- **Role-based Permissions**: Different capabilities for teachers/students
- **Course Isolation**: Data separated by course ID
- **User Authentication**: Basic user identification system

## 🛠️ Technical Details

### Dependencies
- `ipfshttpclient`: IPFS API client
- `requests`: HTTP requests for web integration
- `pathlib2`: Path manipulation utilities
- `tkinter`: GUI framework (built-in)

### Architecture
- **Frontend**: Tkinter-based GUI
- **Backend**: Python with IPFS integration
- **Storage**: Local filesystem + IPFS
- **Communication**: IPFS pubsub (future enhancement)

### Performance
- **Local Caching**: Course data cached locally
- **Incremental Sync**: Only changed data uploaded to IPFS
- **Efficient Storage**: Compressed data storage
- **Fast Startup**: Minimal initialization time

## 🚧 Future Enhancements

### Planned Features
- **Real-time Collaboration**: Live document editing
- **Video Conferencing**: Integrated video calls
- **Blockchain Integration**: Course certificates on blockchain
- **AI Assistance**: Intelligent tutoring system
- **Mobile Support**: Mobile app for on-the-go access

### Technical Improvements
- **IPFS Pubsub**: Real-time messaging via IPFS
- **WebRTC**: Peer-to-peer video/audio
- **End-to-End Encryption**: Enhanced security
- **Distributed Identity**: Decentralized user identity

## 🤝 Contributing

GuruCool is part of the DeSciOS ecosystem. To contribute:

1. Fork the DeSciOS repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

GuruCool is licensed under the same license as DeSciOS. See the main LICENSE file for details.

## 🆘 Support

For support and questions:
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check the DeSciOS documentation
- **Community**: Join the DeSciOS community discussions

## 🔗 Related Projects

- **DeSciOS**: Main scientific computing environment
- **IPFS**: Decentralized file system
- **Jupyter**: Interactive computing platform
- **CoCalc**: Commercial collaborative platform (inspiration)

---

*GuruCool - Empowering decentralized academic collaboration through IPFS technology.* 