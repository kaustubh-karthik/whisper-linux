#!/bin/bash

echo "==== Setting up Whisper Linux Transcriber ===="

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda not found. Please install Miniconda or Anaconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Source conda.sh to get access to conda command
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    . "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    . "$HOME/anaconda3/etc/profile.d/conda.sh"
else
    echo "Error: Could not find conda.sh in miniconda3 or anaconda3 directories."
    echo "Please run this script again after initializing conda with 'conda init bash'"
    exit 1
fi

# Create and activate conda environment
echo "Creating conda environment 'whisper-linux'..."
conda create -y -n whisper-linux python=3.10
conda activate whisper-linux

# Check if environment activated correctly
if [[ "$CONDA_DEFAULT_ENV" != "whisper-linux" ]]; then
    echo "Error: Failed to activate whisper-linux environment."
    exit 1
else
    echo "Successfully activated whisper-linux environment."
fi

# Install system dependencies
echo "Installing system dependencies (requires sudo)..."
sudo apt-get update
sudo apt-get install -y portaudio19-dev xclip xdotool libasound2-plugins pipewire-audio-client-libraries libspa-0.2-modules

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir openai-whisper
pip install --no-cache-dir pynput pyaudio pyperclip scipy
pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo "Checking installed packages..."
pip list | grep -E "whisper|torch|pynput|pyaudio|pyperclip|scipy"

# Verify installation
echo "Verifying installation..."
python check_gpu.py

echo -e "\n==== Setup Complete ===="
echo "To use the transcriber, run: ./start_whisper.sh"
echo "If you encounter issues, check the README.md file for troubleshooting." 