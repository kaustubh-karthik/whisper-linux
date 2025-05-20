#!/bin/bash

echo "==== Setting up Whisper Linux to start automatically on login ===="

# Create autostart directory if it doesn't exist
mkdir -p ~/.config/autostart/

# Check if application is installed system-wide
if [ -f "/usr/local/bin/run-whisper-linux.sh" ]; then
    # Create desktop entry file for the installed application
    cat > ~/.config/autostart/whisper-linux.desktop << EOL
[Desktop Entry]
Type=Application
Name=Whisper Linux Transcriber
Comment=Speech-to-text using OpenAI Whisper
Exec=/usr/local/bin/run-whisper-linux.sh
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
EOL
    echo "Application found in system path."
else
    # Get the absolute path to the whisper-linux directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Create desktop entry file for the local directory
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
    echo "Using local application path: ${SCRIPT_DIR}"
fi

echo "Whisper Linux Transcriber has been set up to start automatically on login."
echo "Desktop entry created at: ~/.config/autostart/whisper-linux.desktop" 