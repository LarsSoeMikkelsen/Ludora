#!/bin/bash
# Called by Calamares shellprocess after unpackfs.
# Reads /tmp/ludora-selections (written by the ludora_selections Python module)
# and removes any optional package the user deselected in netinstall.
# All packages are present in the squashfs; this just prunes unselected ones.

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
# protect_running_kernel=false is required because the live ISO itself runs
# kernel-ludora, so DNF would otherwise refuse to remove it.
if selected "kernel-ludora"; then
    dnf remove -y --noautoremove kernel kernel-core kernel-modules || true
else
    dnf remove -y --noautoremove --setopt=protect_running_kernel=false \
        kernel-ludora kernel-ludora-core kernel-ludora-modules || true
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

# Ludora Desktop Customization: all-or-nothing — only kde-ludora is listed in
# netinstall so the group is toggled as a unit.
if ! selected "kde-ludora"; then
    dnf remove -y --noautoremove \
        fastfetch fastfetch-settings kde-ludora desktop-defaults-ludora || true
fi
