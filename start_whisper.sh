#!/bin/bash

# Path to this script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting Whisper Transcriber..."
echo "================================"
echo "Press Ctrl+C to exit"
echo

# Activate conda environment and run whisper transcriber
cd "$SCRIPT_DIR"
source ~/miniconda3/etc/profile.d/conda.sh
conda activate whisper-linux

# Check if xclip is installed
if ! command -v xclip &> /dev/null; then
    echo "xclip is not installed. Installing..."
    sudo apt-get install -y xclip
fi

# Run the whisper transcriber
python whisper_transcriber.py 