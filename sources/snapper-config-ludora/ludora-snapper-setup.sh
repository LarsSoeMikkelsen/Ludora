#!/bin/bash
# Ludora first-boot snapper + grub-btrfs setup.
# Every step checks whether it is already done, and the completion marker is
# written only at the very end, so a run that fails part-way is simply
# retried on the next boot (the unit is conditioned on the marker).
set -e
exec >> /var/log/ludora-snapper-setup.log 2>&1
echo "=== Ludora snapper setup: $(date) ==="

DONE=/var/lib/ludora/snapper-setup.done
finish() {
    mkdir -p "${DONE%/*}"
    touch "$DONE"
    systemctl disable ludora-snapper-setup.service || true
}

# Snapper and grub-btrfs need a Btrfs root. Manual partitioning allows ext4,
# xfs etc.: nothing to set up then, and no point retrying on every boot.
ROOT_FS=$(findmnt -no FSTYPE /)
if [ "$ROOT_FS" != btrfs ]; then
    echo "Root filesystem is ${ROOT_FS:-unknown}, not btrfs: no snapshots, nothing to do."
    finish
    exit 0
fi

# Create snapper root config.
# This also creates the /.snapshots btrfs subvolume (snapper requires this —
# it will fail if .snapshots already exists, so we must NOT pre-create it).
if [ -e /etc/snapper/configs/root ]; then
    echo "snapper root config exists"
else
    snapper -c root create-config /
fi

# Set /@ as the default Btrfs subvolume so snapper rollback can detect it.
# Without this, snapper rollback fails with "cannot detect ambit since default subvolume is unknown".
# btrfs subvolume list format: ID <n> gen <n> top level <n> path <subvol>
# Anchor @ to end-of-line to avoid matching @home, @log, etc.
ROOT_SUBVOL_ID=$(btrfs subvolume list / | awk '/path @$/{print $2}')
echo "Setting default subvolume to ID ${ROOT_SUBVOL_ID} (@)"
if [ -z "${ROOT_SUBVOL_ID}" ]; then
    echo "ERROR: Could not find @ subvolume ID. Subvolume list output:"
    btrfs subvolume list /
    echo "Skipping set-default — snapper rollback may not work."
else
    btrfs subvolume set-default "${ROOT_SUBVOL_ID}" /
fi

# Tune retention limits (space-conscious for a gaming desktop)
snapper -c root set-config \
    TIMELINE_CREATE=yes \
    TIMELINE_CLEANUP=yes \
    TIMELINE_LIMIT_HOURLY=5 \
    TIMELINE_LIMIT_DAILY=7 \
    TIMELINE_LIMIT_WEEKLY=0 \
    TIMELINE_LIMIT_MONTHLY=3 \
    TIMELINE_LIMIT_YEARLY=0 \
    NUMBER_LIMIT=10 \
    NUMBER_LIMIT_IMPORTANT=5 \
    EMPTY_PRE_POST_CLEANUP=yes \
    EMPTY_PRE_POST_MIN_AGE=3600

# Add /.snapshots to fstab so systemd generates a .snapshots.mount unit,
# which grub-btrfs.path BindsTo= and requires to start.
# Reuse the device field of the existing / entry verbatim: Calamares writes
# UUID=... for plain installs but /dev/mapper/luks-... for encrypted ones.
if awk '$1 !~ /^#/ && $2=="/.snapshots" {f=1} END {exit !f}' /etc/fstab; then
    echo "/.snapshots already in fstab"
else
    ROOT_DEV=$(awk '$1 !~ /^#/ && $2=="/" && $3=="btrfs" {print $1}' /etc/fstab)
    if [ -z "${ROOT_DEV}" ]; then
        echo "ERROR: No btrfs / entry found in /etc/fstab — not adding /.snapshots"
        exit 1
    fi
    BTRFS_OPTS=$(awk '$1 !~ /^#/ && $2=="/" && $3=="btrfs" {print $4}' /etc/fstab | sed 's/subvol=[^,]*,\?//')
    echo "${ROOT_DEV}  /.snapshots  btrfs  subvol=/@/.snapshots,${BTRFS_OPTS}  0 0" >> /etc/fstab
fi

# Reload systemd so it picks up the new .snapshots.mount unit from fstab
systemctl daemon-reload

# Mount /.snapshots now so grub-btrfs.path can start without a reboot
mkdir -p /.snapshots
mountpoint -q /.snapshots || mount /.snapshots

# Enable snapper timers and grub-btrfs snapshot watcher
systemctl enable --now snapper-timeline.timer
systemctl enable --now snapper-cleanup.timer
systemctl enable --now grub-btrfs.path

# Create initial snapshot so grub-btrfs has something to show immediately
# (once: a retried run must not add a second one)
if snapper -c root list --columns description | grep -qF "Initial Ludora installation"; then
    echo "initial snapshot exists"
else
    snapper -c root create --description "Initial Ludora installation"
fi

# Populate grub snapshot submenu. Go through grub-btrfs.service instead of
# running grub2-mkconfig here: the snapshot above already triggered it via
# grub-btrfs.path, and two grub2-mkconfig runs at once corrupt each other's
# output (service failed with "Syntax errors are detected in generated GRUB
# config file"). The unit is Type=oneshot, so this waits for a running
# instance instead of starting a second one.
systemctl start grub-btrfs.service

finish
echo "=== Ludora snapper setup complete: $(date) ==="
