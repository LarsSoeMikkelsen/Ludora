#!/usr/bin/bash
# Remove rescue images copied from the live image build. They carry the
# build's machine-id, so nothing boots them on the installed system (their
# BLS entries are deleted earlier); kernel-install add-all creates a rescue
# image for the installed system's own machine-id.
mid=$(cat /etc/machine-id 2>/dev/null)
[ -n "$mid" ] || exit 0
for f in /boot/vmlinuz-0-rescue-* /boot/initramfs-0-rescue-*.img /boot/.vmlinuz-0-rescue-*.hmac; do
    [ -e "$f" ] || continue
    case "$f" in
        *"$mid"*) ;;
        *) echo "removing stale rescue image $f"; rm -f "$f" ;;
    esac
done
exit 0
