#!/bin/bash

echo "==== Packaging Whisper Linux Transcriber ===="

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: Conda not found. Please install Miniconda or Anaconda first."
    exit 1
fi

# Source conda.sh to get access to conda command
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    . "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    . "$HOME/anaconda3/etc/profile.d/conda.sh"
else
    echo "Error: Could not find conda.sh in miniconda3 or anaconda3 directories."
    exit 1
fi

# Activate the conda environment
conda activate whisper-linux

# Make sure PyInstaller is installed
if ! pip show pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Create directory for model data
MODEL_DIR="bundled_model"
mkdir -p "$MODEL_DIR"

# Check if model already exists in cache
CACHE_DIR="$HOME/.cache/whisper"
MODEL_NAME="small"
MODEL_FILE="$CACHE_DIR/small.pt"

# Show message
echo "Using '$MODEL_NAME' model for packaging"

if [ -f "$MODEL_FILE" ]; then
    echo "Using existing model from cache: $MODEL_FILE"
    # Make sure target directory exists
    mkdir -p "$MODEL_DIR"
    # Copy model file to bundled_model directory
    cp "$MODEL_FILE" "$MODEL_DIR/"
    echo "Model copied to: $MODEL_DIR/small.pt"
else
    echo "Model not found in cache, downloading..."
    # Load model (which will download it if needed)
    python -c "import whisper; whisper.load_model('$MODEL_NAME', download_root='$MODEL_DIR')"
fi

# Package the application with PyInstaller
echo "Packaging application with PyInstaller..."
pyinstaller --clean \
            --onefile \
            --add-data "$MODEL_DIR:whisper_models" \
            --collect-all torch \
            --collect-all tqdm \
            --collect-all numpy \
            --collect-all whisper \
            --hidden-import=pyaudio \
            --hidden-import=pynput \
            --hidden-import=pyperclip \
            --hidden-import=scipy \
            --hidden-import=scipy.signal \
            --hidden-import=wave \
            --hidden-import=tempfile \
            --name whisper-linux \
            whisper_transcriber.py

# Create a wrapper script for the executable
echo "Creating wrapper script..."
cat > dist/run-whisper-linux.sh << 'EOL'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if xclip is installed
if ! command -v xclip &> /dev/null; then
    echo "xclip is not installed. Installing..."
    sudo apt-get install -y xclip xdotool
fi

# Run the executable
./whisper-linux
EOL

# Make the wrapper script executable
chmod +x dist/run-whisper-linux.sh

echo "==== Packaging Complete ===="
echo "The standalone executable is in the 'dist' directory."
echo "To run, use: ./dist/run-whisper-linux.sh"
echo "You may need to install system dependencies: sudo apt-get install -y portaudio19-dev xclip xdotool" 