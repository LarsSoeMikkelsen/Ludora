#!/bin/bash
set -e
exec >> /var/log/ludora-snapper-setup.log 2>&1
echo "=== Ludora snapper setup: $(date) ==="

# Create snapper root config.
# This also creates the /.snapshots btrfs subvolume (snapper requires this —
# it will fail if .snapshots already exists, so we must NOT pre-create it).
snapper -c root create-config /

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
    btrfs subvolume set-default ${ROOT_SUBVOL_ID} /
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
# Get the UUID of the btrfs root partition from the existing / entry.
BTRFS_UUID=$(awk '$2=="/" && $3=="btrfs" {print $1}' /etc/fstab | sed 's/UUID=//')
BTRFS_OPTS=$(awk '$2=="/" && $3=="btrfs" {print $4}' /etc/fstab | sed 's/subvol=[^,]*,\?//')
echo "UUID=${BTRFS_UUID}  /.snapshots  btrfs  subvol=/@/.snapshots,${BTRFS_OPTS}  0 0" >> /etc/fstab

# Mount /.snapshots now so grub-btrfs.path can start without a reboot
mkdir -p /.snapshots
mount -a

# Reload systemd so it picks up the new .snapshots.mount unit from fstab
systemctl daemon-reload

# Enable snapper timers and grub-btrfs snapshot watcher
systemctl enable --now snapper-timeline.timer
systemctl enable --now snapper-cleanup.timer
systemctl enable --now grub-btrfs.path

# Create initial snapshot so grub-btrfs has something to show immediately
snapper -c root create --description "Initial Ludora installation"

# Populate grub snapshot submenu
grub2-mkconfig -o /boot/grub2/grub.cfg

echo "=== Ludora snapper setup complete: $(date) ==="

# Self-destruct: disable and remove this service
systemctl disable ludora-snapper-setup.service
rm -f /etc/systemd/system/ludora-snapper-setup.service
rm -f /usr/local/bin/ludora-snapper-setup.sh
