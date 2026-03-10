#!/bin/bash
# Apply Ludora theme to all non-live users via autostart
LOGFILE="/var/log/ludora-theme-setup.log"

echo "=== Ludora Theme Setup Started: $(date) ===" >> $LOGFILE
echo "Running as: $(whoami)" >> $LOGFILE
echo "PWD: $(pwd)" >> $LOGFILE
echo "Checking /home/ contents:" >> $LOGFILE
ls -la /home/ >> $LOGFILE 2>&1

for homedir in /home/*; do
  echo "Processing: $homedir" >> $LOGFILE

  if [ -d "$homedir" ]; then
    echo "  Is directory: YES" >> $LOGFILE
    username=$(basename "$homedir")
    echo "  Username: $username" >> $LOGFILE

    if [ "$username" != "ludora" ]; then
      echo "  Not ludora user, proceeding..." >> $LOGFILE

      # Create autostart directory
      echo "  Creating autostart directory..." >> $LOGFILE
      mkdir -p "$homedir/.config/autostart" >> $LOGFILE 2>&1

      # Create autostart desktop file that applies theme on first login
      echo "  Creating autostart desktop file..." >> $LOGFILE
      cat > "$homedir/.config/autostart/ludora-theme-apply.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=Apply Ludora Theme
Exec=/usr/bin/ludora-apply-theme.sh
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
X-KDE-StartupNotify=false
EOF

      # Apply proper ownership
      echo "  Setting ownership to $username:$username..." >> $LOGFILE
      chown -R "$username:$username" "$homedir/.config" >> $LOGFILE 2>&1

      echo "  Verifying:" >> $LOGFILE
      ls -la "$homedir/.config/autostart/" >> $LOGFILE 2>&1
      echo "  SUCCESS for $username" >> $LOGFILE
    else
      echo "  Skipping ludora user" >> $LOGFILE
    fi
  else
    echo "  Not a directory, skipping" >> $LOGFILE
  fi
done

echo "=== Ludora Theme Setup Completed: $(date) ===" >> $LOGFILE
