#!/bin/bash
# Called by Calamares shellprocess after unpackfs.
# Reads /tmp/ludora-selections (written by the ludora_selections Python module)
# and removes any optional package the user deselected in netinstall.
# All packages are present in the squashfs; this just prunes unselected ones.

# Protect packages that must never be autoremoved, regardless of user selections.
# gstreamer1-plugins-base: qt6-qtmultimedia (used across Plasma and KDE apps)
# depends on it; if it gets orphaned (install_reason=dep, all codec parents removed),
# DNF5 may clean it even with --noautoremove, cascading through qt6-qtmultimedia.
# plasma-login-manager: the login manager since F44 (sddm is no longer installed).
# vulkan-tools: kinfocenter hard-depends on it; removing it forces kinfocenter out.
# Mark these before any removal so they are treated as user-installed.
dnf mark install gstreamer1-plugins-base plasma-login-manager plasma-workspace vulkan-tools || true

# If the file doesn't exist the module never ran — keep everything as-is
if [ ! -f /tmp/ludora-selections ]; then
    exit 0
fi

SELECTED=$(cat /tmp/ludora-selections)

# Guard against unexpected null output from the Python module
if [ "$SELECTED" = "null" ]; then
    exit 0
fi

# Exact whole-line match against the package list
selected() {
    echo "$SELECTED" | grep -qxF "$1"
}

remove_if_missing() {
    local REMOVE=()
    for pkg in "$@"; do
        selected "$pkg" || REMOVE+=("$pkg")
    done
    if [ ${#REMOVE[@]} -gt 0 ]; then
        dnf remove -y --noautoremove "${REMOVE[@]}" || true
    fi
}

# Codecs
# gstreamer1-plugins-base is intentionally excluded: qt6-qtmultimedia depends
# on it, so removing it would force Qt Multimedia and its users out.
remove_if_missing \
    ffmpeg \
    gstreamer1-plugins-good \
    gstreamer1-plugins-bad-free \
    gstreamer1-plugins-ugly-free \
    gstreamer1-plugin-openh264 \
    gstreamer1-libav \
    gstreamer1-plugins-bad-freeworld \
    gstreamer1-plugins-ugly \
    gstreamer1-vaapi

# Kernel: all-or-nothing — only kernel-ludora is listed in netinstall so the
# group is toggled as a unit; removing it also removes -core and -modules.
# Fedora's kernel is always kept: it is signed by Fedora, so it is the boot
# fallback whenever kernel-ludora is refused under Secure Boot (MOK
# enrollment missed, signing failed).
# protect_running_kernel=false: the live ISO runs Fedora's kernel, but DNF in
# the chroot may resolve uname -r to either kernel.
if selected "kernel-ludora"; then
    # Keep kernel-ludora the GRUB default. 20-grub.install takes the default
    # kernel type from DEFAULTKERNEL via grub2-get-kernel-settings (setting
    # GRUB_DEFAULT_KERNEL_TYPE in /etc/default/grub does not work: it is
    # overridden) and then moves saved_entry only to new kernels whose
    # version contains "ludora", so Fedora kernel updates do not take over
    # the default. kernel-install add-all (later in shellprocess) sets the
    # initial default the same way.
    sed -i 's/^DEFAULTKERNEL=.*/DEFAULTKERNEL=kernel-ludora-core/' /etc/sysconfig/kernel
    grep -q '^DEFAULTKERNEL=' /etc/sysconfig/kernel \
        || echo 'DEFAULTKERNEL=kernel-ludora-core' >> /etc/sysconfig/kernel
else
    dnf remove -y --noautoremove --setopt=protect_running_kernel=false \
        kernel-ludora kernel-ludora-core kernel-ludora-modules || true
fi

# Gaming Stack (mesa-libGL/EGL/dri kept — desktop needs them)
# vulkan-tools is intentionally excluded: kinfocenter hard-depends on it,
# so removing it forces kinfocenter out as a reverse dependency.
remove_if_missing \
    mesa-vulkan-drivers \
    gamemode \
    gamescope \
    vkbasalt

# Gaming Applications
remove_if_missing \
    steam \
    discord \
    goverlay \
    protonplus \
    lact

# Ludora Desktop Customization: all-or-nothing — only kde-ludora is listed in
# netinstall so the group is toggled as a unit.
# Mark plasma-login-manager and plasma-workspace as explicitly installed first
# so they are never removed as orphaned dependencies of kde-ludora.
if ! selected "kde-ludora"; then
    dnf mark install plasma-login-manager plasma-workspace || true
    dnf remove -y --noautoremove \
        fastfetch fastfetch-settings kde-ludora desktop-defaults-ludora || true
fi
