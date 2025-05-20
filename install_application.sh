#!/bin/bash

echo "==== Installing Whisper Linux as an Application ===="

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create necessary directories
sudo mkdir -p /usr/local/bin
sudo mkdir -p /usr/local/share/whisper-linux
sudo mkdir -p /usr/local/share/icons
sudo mkdir -p /usr/local/share/applications

# Check if the distribution exists
if [ ! -d "$SCRIPT_DIR/dist" ]; then
    echo "Error: Distribution not found. Please run package.sh first."
    exit 1
fi

# Copy the executable
sudo cp "$SCRIPT_DIR/dist/whisper-linux" /usr/local/share/whisper-linux/

# Copy and fix the run script
sudo cp "$SCRIPT_DIR/dist/run-whisper-linux.sh" /usr/local/bin/
sudo sed -i 's|./whisper-linux|/usr/local/share/whisper-linux/whisper-linux|g' /usr/local/bin/run-whisper-linux.sh
sudo chmod +x /usr/local/bin/run-whisper-linux.sh

# Copy the whisper_models directory if it exists
if [ -d "$SCRIPT_DIR/dist/whisper_models" ]; then
    sudo cp -r "$SCRIPT_DIR/dist/whisper_models" /usr/local/share/whisper-linux/
fi

# Install the icon - prioritize the packaged icon
if [ -f "$SCRIPT_DIR/dist/whisper-linux-icon.png" ]; then
    echo "Using packaged icon..."
    sudo cp "$SCRIPT_DIR/dist/whisper-linux-icon.png" /usr/local/share/icons/whisper-linux.png
elif [ -f "$HOME/Downloads/whisper_icon.png" ]; then
    echo "Using whisper_icon from Downloads folder..."
    sudo cp "$HOME/Downloads/whisper_icon.png" /usr/local/share/icons/whisper-linux.png
else
    echo "No icon found. Using system icon..."
    # Use a system icon as a placeholder (microphone icon)
    if [ -f "/usr/share/icons/hicolor/256x256/apps/audio-input-microphone.png" ]; then
        sudo cp "/usr/share/icons/hicolor/256x256/apps/audio-input-microphone.png" /usr/local/share/icons/whisper-linux.png
    else
        # If no system icon is found, create a text-based icon
        convert -size 256x256 -background "#0077cc" -fill white -gravity center label:"W" /tmp/whisper-linux-temp.png
        sudo mv /tmp/whisper-linux-temp.png /usr/local/share/icons/whisper-linux.png
    fi
fi

# Install the desktop file
sudo cp "$SCRIPT_DIR/whisper-linux.desktop" /usr/local/share/applications/
sudo update-desktop-database /usr/local/share/applications/

# Update model path in run script
sudo sed -i 's|MODEL_DIR="$SCRIPT_DIR/whisper_models"|MODEL_DIR="/usr/local/share/whisper-linux/whisper_models"|g' /usr/local/bin/run-whisper-linux.sh

echo "==== Installation Complete ===="
echo "Whisper Linux has been installed as an application."
echo "You can now launch it from your application menu or by running 'run-whisper-linux.sh'" 