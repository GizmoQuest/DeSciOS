FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV USER=jupyter
ENV PASSWORD=1234

# Install packages
RUN apt update && apt install -y \
    xfce4 xfce4-goodies tightvncserver \
    novnc websockify python3-websockify \
    xterm curl sudo git wget supervisor \
    dbus-x11 gvfs policykit-1 thunar && \
    apt clean

# Create user and set password
RUN useradd -ms /bin/bash $USER && echo "$USER:$PASSWORD" | chpasswd && adduser $USER sudo

# Install JupyterLab
RUN pip install --no-cache-dir jupyterlab

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
    echo "1234" | vncpasswd -f > /home/$USER/.vnc/passwd && \
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

# Expose ports for Jupyter and noVNC
EXPOSE 8888 6080

# Start services
CMD ["/startup.sh"]

