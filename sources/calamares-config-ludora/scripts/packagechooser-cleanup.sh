#!/bin/bash
# Called by Calamares shellprocess after unpackfs.
# Reads /tmp/ludora-selections (written by the ludora_selections Python module)
# and removes any optional package the user deselected in netinstall.
# All packages are present in the squashfs; this just prunes unselected ones.

SELECTED=$(cat /tmp/ludora-selections 2>/dev/null || echo "")

# Exact whole-line match against the package list
selected() {
    echo "$SELECTED" | grep -qxF "$1"
}

# If no selection data, keep everything
if [ -z "$SELECTED" ] || [ "$SELECTED" = "null" ]; then
    exit 0
fi

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
remove_if_missing \
    ffmpeg \
    gstreamer1-plugins-base \
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
if selected "kernel-ludora"; then
    dnf remove -y --noautoremove kernel kernel-core kernel-modules || true
else
    dnf remove -y --noautoremove kernel-ludora kernel-ludora-core kernel-ludora-modules || true
fi

# Gaming Stack (mesa-libGL/EGL/dri kept — desktop needs them)
remove_if_missing \
    mesa-vulkan-drivers \
    gamemode \
    gamescope \
    vkbasalt \
    vulkan-tools

# Gaming Applications
remove_if_missing \
    steam \
    discord \
    goverlay \
    protonplus \
    lact

# Ludora Desktop Customization
remove_if_missing \
    fastfetch \
    fastfetch-settings \
    kde-ludora \
    desktop-defaults-ludora
