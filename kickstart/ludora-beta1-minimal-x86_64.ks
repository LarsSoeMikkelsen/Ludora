lang en_US.UTF-8
keyboard dk
timezone UTC --utc
rootpw --lock
shutdown
user --name=ludora --gecos="Ludora" --groups=wheel --plaintext --password=ludora

url --url=https://mirrors.dotsrc.org/fedora/linux/releases/43/Everything/x86_64/os/
network --bootproto=dhcp --activate --hostname=ludora

repo --name=fedora-updates --baseurl=https://mirrors.dotsrc.org/fedora/linux/updates/43/Everything/x86_64/
repo --name=ludora --baseurl=https://download.copr.fedorainfracloud.org/results/predze/ludora/fedora-43-x86_64/
repo --name=rpmfusion-free --baseurl=https://mirror.netsite.dk/rpmfusion/free/fedora/releases/43/Everything/x86_64/os/
repo --name=rpmfusion-free-updates --baseurl=https://mirror.netsite.dk/rpmfusion/free/fedora/updates/43/x86_64/
repo --name=rpmfusion-nonfree --baseurl=https://mirror.netsite.dk/rpmfusion/nonfree/fedora/releases/43/Everything/x86_64/os/
repo --name=rpmfusion-nonfree-updates --baseurl=https://mirror.netsite.dk/rpmfusion/nonfree/fedora/updates/43/x86_64/
repo --name=openh264 --baseurl=https://codecs.fedoraproject.org/openh264/43/x86_64/


bootloader --location=none
zerombr
clearpart --all
part / --fstype=ext4 --size=20480 --grow

firewall --enabled --service=ssh
selinux --enforcing

%packages
@core
@base-x
@fonts
@hardware-support
@kde-desktop
@kde-apps
@multimedia

# Bootloader requirements for the ISO builder
grub2-pc
grub2-pc-modules
grub2-tools
grub2-efi-x64
grub2-efi-x64-cdboot
grub2-efi-x64-modules
shim-x64

# Live OS and Installer
livesys-scripts
dracut-live
anaconda
calamares
calamares-libs
calamares-config-ludora
dnf-plugins-core

# Multimedia Codecs
ffmpeg
gstreamer1-plugins-base
gstreamer1-plugins-good
gstreamer1-plugins-bad-free
gstreamer1-plugins-ugly-free
gstreamer1-plugin-openh264
gstreamer1-libav
gstreamer1-plugins-bad-freeworld
gstreamer1-plugins-ugly
gstreamer1-vaapi

# Desktop
sddm
sddm-kcm
firefox

# Btrfs snapshot tooling
snapper
grub-btrfs
libdnf5-plugin-snapper
snapper-config-ludora

%end

%post
# 0. Enable Ludora COPR repo
dnf copr enable predze/ludora -y

# 1. System defaults
systemctl set-default graphical.target
systemctl enable sddm
systemctl enable gamemoded

# 2. KDE Live autologin
mkdir -p /etc/sddm.conf.d
cat >> /etc/sddm.conf.d/autologin.conf << EOF
[Autologin]
User=ludora
Session=plasma
EOF

# 4. Sudoers permissions for Live user
echo "ludora ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/ludora

# 5. Calamares Live launcher wrapper
cat > /usr/local/bin/calamares-launcher << 'EOFLAUNCHER'
#!/bin/bash
# Launch Calamares with proper theming and environment
export QT_STYLE_OVERRIDE=breeze
export QT_QPA_PLATFORMTHEME=qt5ct
export XDG_CURRENT_DESKTOP=KDE
pkexec env DISPLAY=$DISPLAY \
          XAUTHORITY=$XAUTHORITY \
          XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR \
          QT_STYLE_OVERRIDE=breeze \
          QT_QPA_PLATFORMTHEME=qt5ct \
          /usr/bin/calamares
EOFLAUNCHER
chmod +x /usr/local/bin/calamares-launcher

# 6. Live Desktop Launcher for Calamares
mkdir -p /home/ludora/Desktop
cat > /home/ludora/Desktop/install-ludora.desktop << 'EOFDESKTOP'
[Desktop Entry]
Type=Application
Exec=/usr/local/bin/calamares-launcher
Icon=system-software-install
Terminal=false
Name=Install Ludora to Disk
Comment=Launch the Calamares installer
Categories=System;
EOFDESKTOP
chmod +x /home/ludora/Desktop/install-ludora.desktop
chown -R ludora:ludora /home/ludora/Desktop

# 9. Calamares shellprocess module
# All other Calamares module configs are provided by calamares-config-ludora package.
mkdir -p /etc/calamares/modules
cat > /etc/calamares/modules/shellprocess.conf << 'EOFSHELLPROCESS'
---
dontChroot: false
timeout: 300

script:
    # Fix BLS entries to remove /boot/ prefix
    - command: "sed -i 's|^linux /boot/|linux /|g' /boot/loader/entries/*.conf"
      timeout: 30
    - command: "sed -i 's|^initrd /boot/|initrd /|g' /boot/loader/entries/*.conf"
      timeout: 30

    # Remove autologin config (was only for live user)
    - command: "rm -f /etc/sddm.conf.d/autologin.conf"
      timeout: 30

    # Remove live user sudoers
    - command: "rm -f /etc/sudoers.d/ludora"
      timeout: 30

    # Enable RPM Fusion repos on installed system
    - command: "dnf config-manager setopt rpmfusion-free.enabled=1"
      timeout: 30
    - command: "dnf config-manager setopt rpmfusion-free-updates.enabled=1"
      timeout: 30
    - command: "dnf config-manager setopt rpmfusion-nonfree.enabled=1"
      timeout: 30
    - command: "dnf config-manager setopt rpmfusion-nonfree-updates.enabled=1"
      timeout: 30
    # Enable OpenH264 repo on installed system
    - command: "dnf config-manager setopt fedora-cisco-openh264.enabled=1"
      timeout: 30
EOFSHELLPROCESS

# 10. Configure Polkit to allow wheel group to run commands without password
cat > /etc/polkit-1/rules.d/49-nopasswd-wheel.rules << 'EOFPOLKIT'
polkit.addRule(function(action, subject) {
    if (subject.isInGroup("wheel")) {
        return polkit.Result.YES;
    }
});
EOFPOLKIT

# 11. Kernel/Initramfs refresh (includes plymouth changes)
dracut --force --regenerate-all
%end
