#!/bin/bash

# Path to this script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Starting Whisper Transcriber..."
echo "================================"
echo "Press Ctrl+C to exit"
echo

# Go to script directory
cd "$SCRIPT_DIR"

# Find and source conda.sh
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    . "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    . "$HOME/anaconda3/etc/profile.d/conda.sh"
else
    echo "Error: Could not find conda.sh in miniconda3 or anaconda3 directories."
    echo "Please initialize conda with 'conda init bash' and try again"
    exit 1
fi

# Activate conda environment
conda activate whisper-linux

# Check if environment activated correctly
if [[ "$CONDA_DEFAULT_ENV" != "whisper-linux" ]]; then
    echo "Error: Failed to activate whisper-linux environment."
    echo "Make sure you've run the setup.sh script first to create the environment."
    exit 1
fi

# Check if xclip is installed
if ! command -v xclip &> /dev/null; then
    echo "xclip is not installed. Installing..."
    sudo apt-get install -y xclip
fi

# Run the whisper transcriber
python whisper_transcriber.py 