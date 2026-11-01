#!/bin/bash
# Apply Ludora theme and self-destruct
LOGFILE=~/.ludora-theme-apply.log
exec >> $LOGFILE 2>&1

echo "=== Ludora Theme Application Started: $(date) ==="
echo "Running as: $(whoami)"
echo "HOME: $HOME"

# Check if already applied
if [ -f ~/.ludora-theme-applied ]; then
    echo "Already applied (marker exists), exiting"
    exit 0
fi

echo "Applying Ludora theme (org.ludora.desktop) with layout reset..."
plasma-apply-lookandfeel -a org.ludora.desktop --resetLayout
RESULT=$?
echo "Exit code: $RESULT"

if [ $RESULT -eq 0 ]; then
    echo "Success! Marking as applied..."
    touch ~/.ludora-theme-applied

    # First-login race (Plasma 6.8): plasmashell can still be creating its
    # own default layout, and that panel lands after our reset, empty and
    # without a screen, showing as a "+ Add Widgets..." strip. Remove empty
    # panels for a while after the reset; the Ludora panel always has
    # applets, so it is never touched.
    #
    # Also: if plasmashell already loaded the (light) default palette, it
    # does not notice the new colour scheme and the panel stays light
    # (Ludora 45 beta9/beta11). Broadcast KGlobalSettings "palette changed"
    # (type 0) so it repaints; repeat in the loop in case plasmashell was
    # still starting. Restarting plasmashell instead hangs and gets it
    # aborted by systemd (1.1-2).
    notify_palette() {
        dbus-send --session --type=signal /KGlobalSettings \
            org.kde.KGlobalSettings.notifyChange int32:0 int32:0 || true
    }
    notify_palette
    QDBUS=$(command -v qdbus6 || command -v qdbus-qt6 || command -v qdbus)
    if [ -n "$QDBUS" ]; then
        for i in 1 2 3 4 5 6; do
            sleep 5
            notify_palette
            "$QDBUS" org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \
                'panels().forEach(function (p) { if (p.widgets().length == 0) { print("removing empty panel " + p.id); p.remove(); } })'
        done
    fi
    
    echo "Removing autostart file..."
    rm -f ~/.config/autostart/ludora-theme-apply.desktop

    echo "=== Completed Successfully: $(date) ==="
else
    echo "FAILED with exit code: $RESULT"
    echo "=== Failed: $(date) ==="
fi
