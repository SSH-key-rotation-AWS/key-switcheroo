#!/bin/bash

USERNAME="$(whoami)"
SUDOERS_FILE="/etc/sudoers.d/$USERNAME"

# Add the user to the sudo group if not already a member
sudo usermod -aG sudo "$USERNAME"

# Overwrite the sudoers configuration
echo "$USERNAME ALL=(ALL) NOPASSWD: /bin/chmod, /bin/chgrp, /usr/bin/chmod, /usr/bin/chgrp, /bin/cp, /usr/bin/cp, /bin/touch, /usr/bin/touch, /bin/mkdir, /usr/bin/mkdir" | sudo tee "$SUDOERS_FILE" >/dev/null

# Validate the sudoers file to avoid syntax errors
sudo visudo -cf "$SUDOERS_FILE" >/dev/null

# Check if the validation succeeded
if [ $? -eq 0 ]; then
    echo "User $USERNAME has been configured to run chmod, chgrp, cp, touch, and mkdir as sudo."
else
    echo "Failed to configure user $USERNAME. Cleaning up..."
    if [ -f "$SUDOERS_FILE" ]; then
        # Remove the file only if it was created or overwritten by the script
        sudo rm "$SUDOERS_FILE"
    fi
fi
