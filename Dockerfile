FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV USER=deScier
ARG PASSWORD=vncpassword

# Basic system setup
RUN apt update && apt install -y \
    xfce4 xfce4-goodies tightvncserver \
    novnc websockify python3-websockify \
    xterm curl sudo git wget supervisor \
    dbus-x11 gvfs policykit-1 thunar \
    software-properties-common gnupg2 \
    libgl1-mesa-glx libglib2.0-0 \
    libsm6 libxrender1 libxext6 \
    firefox-esr \
    libglvnd0 \
    libgl1 \
    libglx0 \
    libegl1 \
    mesa-utils \
    ocl-icd-libopencl1 \
    opencl-headers \
    clinfo lshw \
    freeglut3-dev \
    python3-gi \
    gir1.2-gtk-3.0 \
    gir1.2-notify-0.7 \
    x11vnc \
    xvfb \
    gir1.2-webkit2-4.0 \
    cmake \
    pkg-config \
    build-essential \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev \
    libnotify-dev \
    libglib2.0-dev \
    libgtk-3-dev \
    fonts-noto-color-emoji \
    fonts-symbola \
    xdotool \
    x11-xserver-utils \
    xautomation \
    scrot \
    imagemagick \
    gnome-screenshot \
    x11-apps \
    && apt clean

# Set up OS identification
RUN echo 'NAME="DeSciOS"\n\
VERSION="0.1"\n\
ID=descios\n\
ID_LIKE=debian\n\
PRETTY_NAME="DeSciOS"\n\
VERSION_ID="0.1"\n\
HOME_URL="https://descios.desciindia.org"\n\
SUPPORT_URL="https://github.com/GizmoQuest/DeSciOS/issues"\n\
BUG_REPORT_URL="https://github.com/GizmoQuest/DeSciOS/issues"' > /etc/os-release && \
    echo 'DeSciOS' > /etc/hostname && \
    mv /bin/uname /bin/uname.real && \
    echo '#!/bin/sh\nif [ "$1" = "-a" ]; then\n  echo -n "DeSciOS " && /bin/uname.real -a\nelse\n  /bin/uname.real "$@"\nfi' > /bin/uname && \
    chmod +x /bin/uname

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pull the deepseek-r1:8b model
RUN ollama serve & sleep 5 && ollama pull deepseek-r1:8b && ollama pull minicpm-v:8b

# Create user and set password
RUN useradd -ms /bin/bash $USER && echo "$USER:$PASSWORD" | chpasswd && adduser $USER sudo

# Configure bash prompt and hostname for the user
RUN echo 'export PS1="\[\033[01;32m\]$USER@DeSciOS\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ "\n\
# Set hostname in current shell\n\
if [ -z "$HOSTNAME" ] || [[ "$HOSTNAME" =~ ^[0-9a-f]{12}$ ]]; then\n\
    export HOSTNAME=DeSciOS\n\
fi' >> /home/$USER/.bashrc && \
    chown $USER:$USER /home/$USER/.bashrc

# Install JupyterLab and other global Python tools with default pip
RUN pip install --no-cache-dir jupyterlab

# Install pip for system Python
RUN apt update && apt install -y python3-pip

# Install R for Debian bookworm
RUN apt update -qq && \
    apt install --no-install-recommends -y dirmngr ca-certificates gnupg wget && \
    gpg --keyserver keyserver.ubuntu.com --recv-key 95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7 && \
    gpg --armor --export 95C0FAF38DB3CCAD0C080A7BDC78B2DDEABC47B7 | \
    tee /etc/apt/trusted.gpg.d/cran_debian_key.asc && \
    echo "deb http://cloud.r-project.org/bin/linux/debian bookworm-cran40/" > /etc/apt/sources.list.d/cran.list && \
    apt update -qq && \
    apt install --no-install-recommends -y r-base

# Install RStudio Desktop (Open Source)
RUN apt update && apt install -y gdebi-core && \
    wget https://download1.rstudio.org/electron/jammy/amd64/rstudio-2025.05.0-496-amd64.deb && \
    gdebi -n rstudio-2025.05.0-496-amd64.deb && \
    rm rstudio-2025.05.0-496-amd64.deb && \
    echo '[Desktop Entry]\nName=RStudio\nExec=rstudio --no-sandbox\nIcon=rstudio\nType=Application\nCategories=Development;' \
    > /usr/share/applications/rstudio.desktop

# Install Spyder (Scientific Python IDE)
RUN pip install --no-cache-dir spyder

# Install UGENE (Bioinformatics suite)
RUN wget https://github.com/ugeneunipro/ugene/releases/download/52.1/ugene-52.1-linux-x86-64.tar.gz && \
    tar -xzf ugene-52.1-linux-x86-64.tar.gz -C /opt && \
    rm ugene-52.1-linux-x86-64.tar.gz && \
    ln -s /opt/ugene-52.1/ugene /usr/local/bin/ugene && \
    echo '[Desktop Entry]\nName=UGENE\nExec=ugene -ui\nIcon=/opt/ugene-52.1/ugene.png\nType=Application\nCategories=Science;' \
    > /usr/share/applications/ugene.desktop

# Install GNU Octave (Matlab-like)
RUN apt update && apt install -y octave

# Install Fiji (ImageJ) with bundled JDK
RUN apt update && apt install -y unzip wget && \
    wget https://downloads.imagej.net/fiji/latest/fiji-latest-linux64-jdk.zip && \
    unzip fiji-latest-linux64-jdk.zip -d /opt && \
    rm fiji-latest-linux64-jdk.zip && \
    chown $USER:$USER -R /opt/Fiji && \
    chmod +x /opt/Fiji/fiji-linux-x64 && \
    echo 'alias fiji=/opt/Fiji/fiji-linux-x64' >> /home/$USER/.bashrc && \
    echo '[Desktop Entry]\nName=Fiji\nExec=bash -c "cd /opt/Fiji && ./fiji"\nIcon=applications-science\nType=Application\nCategories=Science;' \
    > /usr/share/applications/fiji.desktop

# Install Nextflow
RUN apt-get update && apt-get install -y openjdk-17-jre-headless && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    curl -s https://get.nextflow.io | bash && \
    mv /nextflow /usr/bin/nextflow && \
    chmod +x /usr/bin/nextflow && \
    chown $USER:$USER /usr/bin/nextflow

# Install QGIS and GRASS GIS 8
RUN apt update && apt install -y qgis qgis-plugin-grass grass && \
    sed -i 's|^Exec=grass$|Exec=bash -c "export GRASS_PYTHON=/usr/bin/python3; grass"|' /usr/share/applications/grass82.desktop && \
    echo 'export GRASS_PYTHON=/usr/bin/python3' >> /home/$USER/.bashrc && \
    echo 'export GRASS_PYTHON=/usr/bin/python3' >> /root/.bashrc && \
    update-desktop-database /usr/share/applications

# Install IPFS Desktop (GUI)
RUN wget https://github.com/ipfs/ipfs-desktop/releases/download/v0.30.2/ipfs-desktop-0.30.2-linux-amd64.deb && \
    apt install -y ./ipfs-desktop-0.30.2-linux-amd64.deb && \
    rm ipfs-desktop-0.30.2-linux-amd64.deb

# Syncthing (GUI)
RUN apt update && apt install -y syncthing


# EtherCalc (via Browser)
RUN echo '[Desktop Entry]\nName=EtherCalc\nExec=firefox https://calc.domainepublic.net\nIcon=applications-office\nType=Application\nCategories=Office;' \
    > /usr/share/applications/ethercalc.desktop
# BeakerX for JupyterLab (multi-language kernel extension)
RUN pip install --no-cache-dir beakerx && \
    beakerx install
    
# NGL Viewer (via Browser)
RUN echo '[Desktop Entry]\nName=NGL Viewer\nExec=firefox https://nglviewer.org/ngl\nIcon=applications-science\nType=Application\nCategories=Science;' \
    > /usr/share/applications/nglviewer.desktop

# Remix IDE (via Browser)
RUN echo '[Desktop Entry]\nName=Remix IDE\nExec=firefox https://remix.ethereum.org\nIcon=applications-development\nType=Application\nCategories=Development;' \
    > /usr/share/applications/remix-ide.desktop

# Nault (Nano wallet via Browser)
RUN echo '[Desktop Entry]\nName=Nault\nExec=firefox https://nault.cc\nIcon=applications-finance\nType=Application\nCategories=Finance;' \
    > /usr/share/applications/nault.desktop

# Clone and install CellModeller
WORKDIR /opt
RUN git clone https://github.com/cellmodeller/CellModeller.git && \
    cd /opt/CellModeller && pip install -e . && \
    mkdir /opt/data && \
    chown -R $USER:$USER /opt/data && \
    echo '[Desktop Entry]\nName=CellModeller\nExec=bash -c "cd /opt && python CellModeller/Scripts/CellModellerGUI.py"\nIcon=applications-science\nType=Application\nTerminal=true\nCategories=Science;' \
    > /usr/share/applications/cellmodeller.desktop && \
    chmod 644 /usr/share/applications/cellmodeller.desktop && \
    update-desktop-database /usr/share/applications


# Install DeSciOS Assistant
WORKDIR /opt
COPY descios_assistant /opt/descios_assistant
RUN cd /opt/descios_assistant && \
    /usr/bin/python3 -m pip install --break-system-packages -r requirements.txt && \
    chmod +x main.py && \
    cp descios-assistant.desktop /usr/share/applications/ && \
    chown -R $USER:$USER /opt/descios_assistant

# Install DeSci Assistant font
RUN apt-get update && apt-get install -y wget fontconfig && \
    mkdir -p /usr/share/fonts/truetype/orbitron && \
    wget -O /usr/share/fonts/truetype/orbitron/Orbitron.ttf https://github.com/google/fonts/raw/main/ofl/orbitron/Orbitron%5Bwght%5D.ttf && \
    fc-cache -f -v

# OpenCL configuration
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd
RUN ln -s /usr/lib/x86_64-linux-gnu/libOpenCL.so.1 /usr/lib/libOpenCL.so
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=graphics,utility,compute

# Switch to deScier user
USER $USER
WORKDIR /home/$USER

# Disable session saving to avoid stale session hang
RUN mkdir -p /home/$USER/.config/xfce4/xfconf/xfce-perchannel-xml && \
    echo -e '<channel name="xfce4-session" version="1.0">\n  <property name="General">\n    <property name="SaveOnExit" type="bool" value="false"/>\n  </property>\n</channel>' \
    > /home/$USER/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-session.xml

# Configure VNC
RUN mkdir -p /home/$USER/.vnc && \
    echo -e '#!/bin/bash\nxrdb $HOME/.Xresources\nstartxfce4 &' > /home/$USER/.vnc/xstartup && \
    chmod +x /home/$USER/.vnc/xstartup && \
    echo "$PASSWORD" | vncpasswd -f > /home/$USER/.vnc/passwd && \
    chmod 600 /home/$USER/.vnc/passwd && \
    touch /home/$USER/.Xresources && \
    chown -R $USER:$USER /home/$USER/.vnc /home/$USER/.Xresources /home/$USER/.config

# Switch back to root for final setup
USER root

# Startup and Supervisor
COPY startup.sh /startup.sh
RUN chmod +x /startup.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY os.svg /usr/share/desktop-base/active-theme/wallpaper/contents/images/1920x1080.svg

# Set clean default XFCE panel layout (no power manager plugin)
COPY xfce4-panel.xml /etc/xdg/xfce4/panel/default.xml

# Expose ports for noVNC
EXPOSE 6080

# Apply DeSciOS noVNC Theme
COPY novnc-theme/descios-theme.css /usr/share/novnc/app/styles/
COPY novnc-theme/vnc.html /usr/share/novnc/
COPY novnc-theme/ui.js /usr/share/novnc/app/
COPY novnc-theme/icons/* /usr/share/novnc/app/images/icons/

# Start services
CMD ["/startup.sh"]
