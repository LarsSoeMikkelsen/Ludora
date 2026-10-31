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

    # First-login race (seen with Plasma 6.8 in Ludora 45 beta8): plasmashell
    # can still be creating its own default layout when this runs, and that
    # panel lands after our reset, empty and without a screen, showing as a
    # "+ Add Widgets..." strip. Remove empty panels for a while after the
    # reset; the Ludora panel always has applets, so it is never touched.
    QDBUS=$(command -v qdbus6 || command -v qdbus-qt6 || command -v qdbus)
    if [ -n "$QDBUS" ]; then
        for i in 1 2 3 4 5 6; do
            sleep 5
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
