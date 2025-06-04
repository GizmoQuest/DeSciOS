FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV USER=jupyter
ARG PASSWORD=1234

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
    clinfo \
    freeglut3-dev \
    && apt clean

# Create user and set password
RUN useradd -ms /bin/bash $USER && echo "$USER:$PASSWORD" | chpasswd && adduser $USER sudo

# Install JupyterLab
RUN pip install --no-cache-dir jupyterlab

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
    rm rstudio-2025.05.0-496-amd64.deb

# Install Spyder (Scientific Python IDE)
RUN pip install --no-cache-dir spyder

# Install UGENE (Bioinformatics suite)
RUN wget https://github.com/ugeneunipro/ugene/releases/download/52.1/ugene-52.1-linux-x86-64.tar.gz && \
    tar -xzf ugene-52.1-linux-x86-64.tar.gz -C /opt && \
    rm ugene-52.1-linux-x86-64.tar.gz && \
    ln -s /opt/ugene-52.1/ugene /usr/local/bin/ugene && \
    echo -e '[Desktop Entry]\nName=UGENE\nExec=ugene\nIcon=/opt/ugene-52.1/ugene.png\nType=Application\nCategories=Science;' \
    > /usr/share/applications/ugene.desktop

# Install ParaView
RUN apt update && apt install -y paraview

# Install GNU Octave (Matlab-like)
RUN apt update && apt install -y octave

# Install Fiji (ImageJ) with bundled JDK
RUN apt update && apt install -y unzip wget && \
    wget https://downloads.imagej.net/fiji/latest/fiji-latest-linux64-jdk.zip && \
    unzip fiji-latest-linux64-jdk.zip -d /opt && \
    rm fiji-latest-linux64-jdk.zip && \
    ln -s /opt/Fiji.app/ImageJ-linux64 /usr/local/bin/fiji

# Install QGIS
RUN apt update && apt install -y qgis qgis-plugin-grass

# Install Avogadro (Molecular modeling)
RUN apt update && apt install -y avogadro

# Install IPFS Desktop (GUI)
RUN wget https://github.com/ipfs/ipfs-desktop/releases/download/v0.30.2/ipfs-desktop-0.30.2-linux-amd64.deb && \
    apt install -y ./ipfs-desktop-0.30.2-linux-amd64.deb && \
    rm ipfs-desktop-0.30.2-linux-amd64.deb

# Syncthing (GUI)
RUN apt update && apt install -y syncthing

# EtherCalc (via Browser)
RUN echo -e '[Desktop Entry]\nName=EtherCalc\nExec=firefox http://ethercalc.org\nType=Application\nCategories=Office;' \
    > /usr/share/applications/ethercalc.desktop

# BeakerX for JupyterLab (multi-language kernel extension)
RUN pip install --no-cache-dir beakerx && \
    beakerx install

# Remix IDE (via Browser)
RUN echo -e '[Desktop Entry]\nName=Remix IDE\nExec=firefox https://remix.ethereum.org\nType=Application\nCategories=Development;' \
    > /usr/share/applications/remix-ide.desktop

# Nault (Nano wallet via Browser)
RUN echo -e '[Desktop Entry]\nName=Nault\nExec=firefox https://nault.cc\nType=Application\nCategories=Finance;' \
    > /usr/share/applications/nault.desktop

# Clone and install CellModeller
WORKDIR /opt
RUN git clone https://github.com/HaseloffLab/CellModeller.git && \
    cd /opt/CellModeller && pip install -e . && \
    mkdir /opt/data && \
    chown -R $USER:$USER /opt/data

# OpenCL configuration
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd
RUN ln -s /usr/lib/x86_64-linux-gnu/libOpenCL.so.1 /usr/lib/libOpenCL.so
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES graphics,utility,compute

# Switch to jupyter user
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

# Start services
CMD ["/startup.sh"]
