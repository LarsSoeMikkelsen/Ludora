#!/bin/bash
# ludora-snapshot-notify.sh - Notify user when booted into a snapshot
#
# This script runs at KDE session startup and checks if the user is booted
# into a read-only snapshot. If so, it shows a notification with options to
# either make the snapshot permanent or ignore it.
#
# Installed to: /usr/local/bin/ludora-snapshot-notify.sh
# Autostart via: /etc/xdg/autostart/ludora-snapshot-notify.desktop

# Wait for KDE session to fully initialize
sleep 5

# Detect current subvolume
CURRENT_SUBVOL=$(findmnt -no SOURCE / | sed 's/.*\[//' | sed 's/\]//')

# Check if we're in a snapshot
if [[ "$CURRENT_SUBVOL" =~ \.snapshots/[0-9]+/snapshot ]]; then
    # Extract snapshot number
    SNAPSHOT_NUM=$(echo "$CURRENT_SUBVOL" | sed 's/.*\.snapshots\/\([0-9]*\).*/\1/')
    
    # Get snapshot description if available
    SNAPSHOT_DESC=$(snapper list --columns number,description 2>/dev/null | grep "^$SNAPSHOT_NUM " | sed "s/^$SNAPSHOT_NUM *//" || echo "")
    
    # Build notification message
    if [[ -n "$SNAPSHOT_DESC" ]]; then
        MESSAGE="You are currently booted into snapshot #$SNAPSHOT_NUM:\n<i>$SNAPSHOT_DESC</i>\n\nWould you like to make this snapshot your permanent system state?"
    else
        MESSAGE="You are currently booted into snapshot #$SNAPSHOT_NUM.\n\nWould you like to make this snapshot your permanent system state?"
    fi
    
    # Show KDE notification with actions
    # Use kdialog for better action button support
    if command -v kdialog &> /dev/null; then
        kdialog --title "Snapshot Boot Detected" \
                --icon system-upgrade \
                --yesno "$MESSAGE" \
                --yes-label "Make Permanent" \
                --no-label "Keep Testing"
        
        RESPONSE=$?
        
        if [[ $RESPONSE -eq 0 ]]; then
            # User clicked "Make Permanent"
            konsole --hold -e pkexec /usr/local/bin/snapper-commit
        fi
    else
        # Fallback to notify-send if kdialog not available
        notify-send -i system-upgrade -u critical \
                    "Snapshot Boot Detected" \
                    "You are booted into snapshot #$SNAPSHOT_NUM. Run 'sudo snapper-commit' to make it permanent, or reboot normally to return to your main system."
    fi
fi
