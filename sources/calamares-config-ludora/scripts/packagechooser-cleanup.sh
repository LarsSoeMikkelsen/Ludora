#!/bin/bash
# Called by Calamares shellprocess after unpackfs.
# Reads /tmp/ludora-selections (written by the ludora_selections Python module)
# and removes packages from any group the user deselected in netinstall.
# All packages are present in the squashfs; this just prunes unselected ones.

SELECTED=$(cat /tmp/ludora-selections 2>/dev/null || echo "")

selected() {
    echo "$SELECTED" | grep -qF "$1"
}

# If no selection data, keep everything
if [ -z "$SELECTED" ] || [ "$SELECTED" = "null" ]; then
    exit 0
fi

# Codecs (grep check: ffmpeg)
if ! selected "ffmpeg"; then
    dnf remove -y --noautoremove \
        ffmpeg \
        gstreamer1-plugins-base \
        gstreamer1-plugins-good \
        gstreamer1-plugins-bad-free \
        gstreamer1-plugins-ugly-free \
        gstreamer1-plugin-openh264 \
        gstreamer1-libav \
        gstreamer1-plugins-bad-freeworld \
        gstreamer1-plugins-ugly \
        gstreamer1-vaapi || true
fi

# Kernel: remove whichever kernel the user did NOT choose.
# Both kernels are present in the squashfs; this picks one to keep.
if selected "kernel-ludora"; then
    dnf remove -y --noautoremove kernel kernel-core kernel-modules || true
else
    dnf remove -y --noautoremove kernel-ludora kernel-ludora-core kernel-ludora-modules || true
fi

# Gaming stack — mesa-libGL/EGL/dri kept, only mesa-vulkan-drivers is optional (grep check: gamemode)
if ! selected "gamemode"; then
    dnf remove -y --noautoremove \
        mesa-vulkan-drivers \
        gamemode \
        gamescope \
        vkbasalt \
        vulkan-tools || true
fi

# Gaming applications (grep check: steam)
if ! selected "steam"; then
    dnf remove -y --noautoremove \
        steam \
        discord \
        goverlay \
        protonplus \
        lact || true
fi

# Ludora desktop customization (grep check: kde-ludora)
if ! selected "kde-ludora"; then
    dnf remove -y --noautoremove \
        fastfetch \
        fastfetch-settings \
        kde-ludora \
        desktop-defaults-ludora || true
fi
