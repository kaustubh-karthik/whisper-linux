#!/bin/bash

# Get the absolute path to the whisper-linux directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create autostart directory if it doesn't exist
mkdir -p ~/.config/autostart/

# Create desktop entry file
cat > ~/.config/autostart/whisper-linux.desktop << EOL
[Desktop Entry]
Type=Application
Name=Whisper Linux Transcriber
Comment=Speech-to-text using OpenAI Whisper
Exec=${SCRIPT_DIR}/start_whisper.sh
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOL

echo "Whisper Linux Transcriber has been set up to start automatically on login."
echo "Desktop entry created at: ~/.config/autostart/whisper-linux.desktop" 