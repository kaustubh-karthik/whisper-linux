# Whisper Linux Transcriber

A Linux application that transcribes speech to text using OpenAI's Whisper model. This application allows you to transcribe speech by pressing Ctrl+Shift, recording audio while the keys are pressed, and automatically pasting the transcribed text into the active window when the keys are released.

## Features

- Press and hold Right Ctrl + Right Shift to record audio
- Release keys to transcribe speech and paste text into the active window
- GPU acceleration with CUDA for fast transcription
- Memory optimizations for GPUs with limited VRAM (like RTX 3070)
- Audio enhancement for improved transcription quality
- Automatic resampling of audio to Whisper's required format

## Requirements

- Linux operating system
- NVIDIA GPU with CUDA support (recommended, but CPU mode is available)
- Conda environment for dependency management
- xclip and xdotool for clipboard and window management
- PortAudio for audio recording

## Installation

### Automatic Setup (Recommended)

1. Clone this repository
2. Make sure you have [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda installed
3. Run the setup script:

```bash
./setup.sh
```

This script will:
- Create a new Conda environment called 'whisper-linux'
- Install all required system dependencies
- Install Python dependencies with CUDA support
- Verify your GPU configuration

### Manual Installation

If you prefer to install manually:

1. Create and activate the Conda environment:

```bash
conda create -n whisper-linux python=3.10
conda activate whisper-linux
```

2. Install system dependencies:

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev xclip xdotool
```

3. Install Python dependencies:

```bash
pip install openai-whisper pynput pyaudio pyperclip scipy
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

4. Verify GPU support:

```bash
python check_gpu.py
```

## Usage

### Manual Start

1. Run the start script:

```bash
./start_whisper.sh
```

2. Press and hold Right Ctrl + Right Shift to record audio
3. Speak clearly into your microphone
4. Release the keys to transcribe and paste the text into the active window

### Automatic Start (Optional)

To have the application start automatically when you log in:

```bash
./install_autostart.sh
```

This will create a desktop entry that launches the application at login. The application will run silently in the background.

## Configuration

You can modify the following settings in `whisper_transcriber.py`:

- `MODEL_SIZE`: Choose from "tiny", "base", "small", "medium", or "large" (larger models are more accurate but slower)
- `USE_GPU`: Enable/disable GPU acceleration
- `INPUT_DEVICE`: Set a specific audio input device or leave as None for default
- `ACTIVATION_KEYS`: Change the key combination used to activate recording

## GPU Memory Optimization

The application includes several optimizations for GPUs with limited VRAM:

- FP16 precision for reduced memory usage
- CPU offloading to free up GPU memory
- Memory split size restrictions
- CUDA memory allocation optimizations
- TF32 acceleration where available

## Troubleshooting

- If audio recording isn't working, check your microphone settings and try changing the `INPUT_DEVICE` parameter
- If GPU acceleration isn't working, verify your CUDA installation with `python check_gpu.py`
- If you encounter memory errors, try using a smaller model size or enabling CPU_OFFLOAD

## License

This project uses OpenAI's Whisper model which is under the MIT License. 