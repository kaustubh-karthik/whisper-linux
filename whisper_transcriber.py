import os
import sys
import pyaudio
import numpy as np
import whisper
import pyperclip
import tempfile
import wave
from pynput import keyboard
import subprocess
import threading
import time
import scipy.signal as signal
import torch
import warnings
import logging

# Suppress ALSA error messages
# Redirect stderr for ALSA error messages
os.environ['ALSA_CARD'] = 'Generic'  # Use generic device
logging.getLogger('ALSA').setLevel(logging.ERROR)  # Set ALSA logger to ERROR level
warnings.filterwarnings("ignore", category=UserWarning)  # Ignore user warnings

# Configuration
MODEL_SIZE = "small"  # Options: tiny, base, small, medium, large
USE_GPU = False  # Disabled GPU to use CPU only
CPU_OFFLOAD = False  # Not needed when using CPU only
DEVICE_MAP = None  # Not used in CPU mode
FP16_MODE = False  # Not needed for CPU mode
# RTX 3070 has 8GB VRAM - these settings are optimized for this GPU
MAX_SPLIT_SIZE_MB = 128  # Limit memory split size for better memory management
SAMPLE_RATE_RECORDING = 44100  # Standard sample rate that most hardware supports
SAMPLE_RATE_WHISPER = 16000  # Whisper expects 16kHz audio
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024  # Number of frames per buffer
ACTIVATION_KEYS = {keyboard.Key.ctrl_r, keyboard.Key.shift_r} # Using Right Ctrl + Right Shift
DEBUG = True  # Enable debug mode
DEBUG_SAVE_PATH = os.path.expanduser("~/debug_recording.wav")  # Path to save debug recording
# Set to None to use default device, or set to a specific device index (0, 2, 6, 7, etc.)
# Check the "Available input devices" output to find your microphone
INPUT_DEVICE = 6  # Try Jabra Evolve2 40 headset
# Minimum audio level to consider as speech (0-32767)
MIN_AUDIO_LEVEL = 50

# Global state
current_keys_pressed = set()
is_recording = False
audio_frames = []
recording_thread = None
model = None

def load_model():
    global model
    print(f"Loading Whisper model: {MODEL_SIZE} (CPU mode)...")
    try:
        # Determine if we're running as a packaged app or from source
        if getattr(sys, 'frozen', False):
            # Running as packaged app
            base_path = sys._MEIPASS
            download_root = os.path.join(base_path, 'whisper_models')
            print(f"Running as packaged app, using bundled model from: {download_root}")
        else:
            # Running from source
            download_root = os.path.expanduser("~/.cache/whisper")
            print(f"Running from source, using model from: {download_root}")
        
        # Load the model on CPU
        device = "cpu"
        model = whisper.load_model(MODEL_SIZE, device=device, download_root=download_root)
        print(f"Whisper model loaded successfully on CPU.")
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        print("Please ensure you have a compatible PyTorch version installed and the model files are accessible.")
        exit()

def check_audio_levels(data):
    """Check audio levels to ensure microphone is picking up sound"""
    audio_data = np.frombuffer(data, dtype=np.int16)
    
    # Calculate peak amplitude and RMS
    peak = np.max(np.abs(audio_data))
    rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))
    
    # Calculate peak in dB (relative to max 16-bit value of 32767)
    if peak > 0:
        peak_db = 20 * np.log10(peak / 32767)
    else:
        peak_db = -100
    
    return peak, peak_db, rms

def record_audio():
    global audio_frames, is_recording
    audio_frames = []
    print("Recording started...")
    try:
        p = pyaudio.PyAudio()
        
        # List available input devices
        if DEBUG:
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            print(f"Available input devices:")
            for i in range(0, num_devices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print(f"  - Input Device ID {i}: {p.get_device_info_by_host_api_device_index(0, i).get('name')}")
        
        # Use the specified input device or default if None
        input_device_index = INPUT_DEVICE
        if input_device_index is None:
            input_device_index = p.get_default_input_device_info().get('index') if p.get_default_input_device_info() else None
        
        if DEBUG:
            print(f"Using input device index: {input_device_index}")
            if input_device_index is not None:
                dev_info = p.get_device_info_by_index(input_device_index)
                print(f"  Device: {dev_info['name']}")
        
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=SAMPLE_RATE_RECORDING,
                        input=True,
                        input_device_index=input_device_index,
                        frames_per_buffer=CHUNK)
        
        # For monitoring audio levels
        last_level_print = time.time()
        
        while is_recording:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_frames.append(data)
            
            # Check and print audio levels once per second
            if DEBUG and time.time() - last_level_print > 0.5:  # Check more frequently
                peak, peak_db, rms = check_audio_levels(data)
                print(f"Audio level - Peak: {peak} ({peak_db:.1f} dB), RMS: {rms:.1f}")
                last_level_print = time.time()
            
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Recording stopped.")
    except Exception as e:
        print(f"Error during recording: {e}")
        is_recording = False # Stop recording on error

def enhance_audio(audio_data):
    """Enhance the recorded audio by amplifying it if it's too quiet"""
    # Convert audio data to numpy array
    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
    
    # Check if audio is too quiet
    peak = np.max(np.abs(audio_np))
    if peak < 500:  # Very quiet recording
        print(f"Audio is very quiet (peak: {peak}). Amplifying...")
        # Normalize to use more of the available range, but leave headroom
        gain = min(20000 / (peak + 1e-10), 100)  # Limit maximum gain
        audio_np = audio_np * gain
    
    # Apply light noise gate to remove background hiss
    noise_floor = 50  # Adjust based on your environment
    audio_np[np.abs(audio_np) < noise_floor] = 0
    
    # Convert back to int16
    audio_np = np.clip(audio_np, -32768, 32767).astype(np.int16)
    
    if DEBUG:
        new_peak = np.max(np.abs(audio_np))
        print(f"Audio after enhancement - Peak: {new_peak}")
    
    return audio_np.tobytes()

def resample_audio(audio_data, original_rate, target_rate):
    """Resample audio data from original_rate to target_rate"""
    # Convert audio data to numpy array
    audio_data_np = np.frombuffer(audio_data, dtype=np.int16)
    
    if DEBUG:
        print(f"Original audio shape: {audio_data_np.shape}, Min: {np.min(audio_data_np)}, Max: {np.max(audio_data_np)}")
    
    # Resample
    number_of_samples = round(len(audio_data_np) * float(target_rate) / original_rate)
    resampled_data = signal.resample(audio_data_np, number_of_samples)
    
    # Convert back to int16
    resampled_data = resampled_data.astype(np.int16)
    
    if DEBUG:
        print(f"Resampled audio shape: {resampled_data.shape}, Min: {np.min(resampled_data)}, Max: {np.max(resampled_data)}")
    
    return resampled_data.tobytes()

def stop_record_and_transcribe():
    global is_recording, audio_frames, recording_thread
    if not is_recording:
        return

    is_recording = False
    if recording_thread and recording_thread.is_alive():
        recording_thread.join() # Wait for recording thread to finish
    print("Processing audio...")

    if not audio_frames:
        print("No audio recorded.")
        return
    
    if len(audio_frames) < 10:
        print("Recording too short (less than ~0.2 seconds). Ignoring.")
        return

    # Combine all audio frames
    audio_data = b''.join(audio_frames)
    
    # Check if audio is empty or too quiet
    audio_np = np.frombuffer(audio_data, dtype=np.int16)
    peak = np.max(np.abs(audio_np))
    
    if peak < MIN_AUDIO_LEVEL:
        print(f"Audio too quiet (peak: {peak} < {MIN_AUDIO_LEVEL}). Make sure your microphone is working.")
        print("Skipping transcription.")
        return
    
    # Enhance the audio (amplify and reduce noise)
    audio_data = enhance_audio(audio_data)
    
    # Save a debug copy of the original audio
    if DEBUG:
        with wave.open(DEBUG_SAVE_PATH, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE_RECORDING)
            wf.writeframes(audio_data)
            print(f"Debug recording saved to {DEBUG_SAVE_PATH}")
    
    # Resample if necessary
    if SAMPLE_RATE_RECORDING != SAMPLE_RATE_WHISPER:
        print(f"Resampling audio from {SAMPLE_RATE_RECORDING}Hz to {SAMPLE_RATE_WHISPER}Hz...")
        audio_data = resample_audio(audio_data, SAMPLE_RATE_RECORDING, SAMPLE_RATE_WHISPER)

    # Save to a temporary WAV file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio_file:
        tmp_audio_filename = tmp_audio_file.name
        wf = wave.open(tmp_audio_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2) # 16-bit audio
        wf.setframerate(SAMPLE_RATE_WHISPER)
        wf.writeframes(audio_data)
        wf.close()

    print(f"Audio saved to temporary file: {tmp_audio_filename}")

    if model is None:
        print("Whisper model not loaded. Aborting transcription.")
        return

    try:
        print("Transcribing... (this may take a moment)")
        
        # Start transcription time
        start_time = time.time()
        
        # CPU-only transcription
        result = model.transcribe(
            tmp_audio_filename, 
            fp16=False,  # CPU mode, no FP16
            verbose=DEBUG,
            language="en",  # Explicitly set language to English
            temperature=0.0  # Use lower temperature for more deterministic results
        )
        
        # Calculate transcription time
        transcription_time = time.time() - start_time
        
        transcribed_text = result["text"].strip()
        print(f"Transcription ({transcription_time:.2f}s): '{transcribed_text}'")

        if transcribed_text:
            try:
                pyperclip.copy(transcribed_text)
                print("Copied to clipboard.")
                # Use xdotool to paste
                subprocess.run(["xdotool", "type", "--clearmodifiers", "--file", "-"], input=transcribed_text.encode())
                print("Pasted to active window.")
            except Exception as e:
                print(f"Error copying/pasting text: {e}")
                print("Trying to paste directly with xdotool...")
                subprocess.run(["xdotool", "type", "--clearmodifiers", transcribed_text])
        else:
            print("No text transcribed.")
            
        if DEBUG:
            print(f"Whisper result details: {result}")

    except Exception as e:
        print(f"Error during transcription: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_audio_filename):
            os.remove(tmp_audio_filename)
            print(f"Temporary file {tmp_audio_filename} removed.")

def on_press(key):
    global is_recording, recording_thread, current_keys_pressed
    current_keys_pressed.add(key)
    if not is_recording and all(k in current_keys_pressed for k in ACTIVATION_KEYS):
        is_recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()

def on_release(key):
    global is_recording, current_keys_pressed
    if key in current_keys_pressed:
        current_keys_pressed.remove(key)

    if is_recording and not all(k in current_keys_pressed for k in ACTIVATION_KEYS):
        # Check if any of the activation keys were released while recording
        if any(k in ACTIVATION_KEYS for k in [key] + list(current_keys_pressed)): # Check if *any* activation key is still effectively pressed or was just released
             # If we were recording and an activation key was released or is no longer part of the currently pressed keys
            if not all(k in current_keys_pressed for k in ACTIVATION_KEYS): # and not all activation keys are still pressed
                stop_record_and_transcribe()

# GPU memory stats function removed as we're using CPU only


if __name__ == "__main__":
    # Check for scipy
    try:
        import scipy
    except ImportError:
        print("SciPy is required for audio resampling. Installing...")
        subprocess.run(["pip", "install", "scipy"], check=True)
        print("SciPy installed successfully.")
    
    # Running in CPU-only mode
    print("Running in CPU-only mode - no GPU will be used.")
    
    # Test audio setup
    if DEBUG:
        print("Testing audio setup...")
        p = pyaudio.PyAudio()
        try:
            print("Available input devices:")
            for i in range(p.get_device_count()):
                dev = p.get_device_info_by_index(i)
                if dev['maxInputChannels'] > 0:
                    print(f"  ID {i}: {dev['name']} - {int(dev['defaultSampleRate'])}Hz, {dev['maxInputChannels']} input channels")
                    
            print("\nCurrent INPUT_DEVICE setting:", INPUT_DEVICE)
            if INPUT_DEVICE is not None:
                try:
                    dev_info = p.get_device_info_by_index(INPUT_DEVICE)
                    print(f"  Selected device: {dev_info['name']}")
                except:
                    print("  Warning: Invalid device index! Using default.")
            else:
                try:
                    default_input = p.get_default_input_device_info()
                    print(f"  Using default device: {default_input['name']} (index {default_input['index']})")
                except Exception as e:
                    print(f"  Error getting default input device: {e}")
        except Exception as e:
            print(f"Error testing audio setup: {e}")
        finally:
            p.terminate()
    
    load_model()
    print(f"Whisper Transcriber started. Press and hold {' + '.join(str(k).split('.')[-1].replace('_r','').replace('_l','').capitalize() for k in ACTIVATION_KEYS)} to record.")
    print("Ensure the window you want to type into is active when you release the keys.")
    print("Speak clearly into your microphone when recording.")
    
    # Create a non-daemon listener thread
    listener_thread = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener_thread.start()
    
    try:
        listener_thread.join() # Keep the main thread alive until the listener stops
    except KeyboardInterrupt:
        print("\nExiting...")
        exit(0) 