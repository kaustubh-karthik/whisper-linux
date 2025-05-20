# Whisper Linux

A Linux desktop application for real-time speech-to-text transcription using OpenAI's Whisper model.

## Features

- Trigger transcription with keyboard shortcut (Ctrl+Shift)
- Record audio and automatically transcribe speech
- Paste transcribed text into the active application window
- Works across all applications and text fields
- Audio enhancement for quieter recordings
- CPU-only mode for systems without dedicated GPUs

## Installation

### Option 1: Build from source

1. Ensure you have the prerequisites:
   ```bash
   sudo apt-get install python3-pip python3-dev portaudio19-dev xclip xdotool
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/whisper-linux.git
   cd whisper-linux
   ```

3. Package the application:
   ```bash
   ./package.sh
   ```

4. Install as a desktop application:
   ```bash
   ./install_application.sh
   ```

### Option 2: Download prebuilt package

*Coming soon*

## Usage

Once installed, you can use Whisper Linux in two ways:

1. **From the application menu**: Search for "Whisper Linux" in your application launcher
2. **Using keyboard shortcuts**: Press `Ctrl+Shift` to start recording, release to transcribe

When you press and hold `Ctrl+Shift`, the application will record audio from your microphone. When you release the keys, it will transcribe the recorded audio and paste the text where your cursor is located.

## Set up autostart

To make Whisper Linux start automatically when you log in:

```bash
./install_autostart.sh
```

## Troubleshooting

- **Missing dependencies**: Make sure you have all required system packages
  ```bash
  sudo apt-get install portaudio19-dev xclip xdotool
  ```

- **Audio input issues**: Check your microphone settings in the system sound settings

- **Model download issues**: If the model doesn't download automatically, you can manually download it from [OpenAI's Whisper models](https://github.com/openai/whisper/blob/main/model-card.md) and place it in the appropriate directory

## Uninstallation

To uninstall the application from your system:

```bash
sudo rm -rf /usr/local/share/whisper-linux
sudo rm /usr/local/bin/run-whisper-linux.sh
sudo rm /usr/local/share/icons/whisper-linux.png
sudo rm /usr/local/share/applications/whisper-linux.desktop
sudo update-desktop-database /usr/local/share/applications/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for the speech recognition model
- The Python community for the excellent libraries that made this possible 