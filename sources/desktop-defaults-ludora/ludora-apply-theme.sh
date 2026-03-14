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

    echo "Configuring panel favorites..."
    # Configure panel favorites: Konsole, Files, Firefox, Discord, Lutris, Steam
    kwriteconfig5 --file ~/.config/kickoffrc --group Favorites --key FavoriteApps "preferred://browser,org.kde.konsole.desktop,org.kde.dolphin.desktop,firefox.desktop,steam.desktop"

    echo "Removing autostart file..."
    rm -f ~/.config/autostart/ludora-theme-apply.desktop

    echo "=== Completed Successfully: $(date) ==="
else
    echo "FAILED with exit code: $RESULT"
    echo "=== Failed: $(date) ==="
fi
