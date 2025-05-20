import torch
import os
import subprocess

print("==== GPU Compatibility Check for Whisper ====")
print("PyTorch version:", torch.__version__ if hasattr(torch, '__version__') else torch.version.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("\n==== GPU Information ====")
    print("CUDA device count:", torch.cuda.device_count())
    print("CUDA device name:", torch.cuda.get_device_name(0))
    print("CUDA device capability:", torch.cuda.get_device_capability(0))
    print("CUDA version:", torch.version.cuda)
    
    # Memory information
    total_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)  # in GB
    reserved_mem = torch.cuda.memory_reserved(0) / (1024**3)  # in GB
    allocated_mem = torch.cuda.memory_allocated(0) / (1024**3)  # in GB
    free_mem = total_mem - reserved_mem
    
    print("\n==== GPU Memory Information ====")
    print(f"Total Memory:     {total_mem:.2f} GB")
    print(f"Reserved Memory:  {reserved_mem:.2f} GB")
    print(f"Allocated Memory: {allocated_mem:.2f} GB")
    print(f"Free Memory:      {free_mem:.2f} GB")
    
    # Run a small test computation on GPU
    print("\n==== Running GPU Test ====")
    x = torch.rand(1000, 1000).cuda()
    y = torch.matmul(x, x.T)
    print(f"Matrix multiplication test: {y.shape}, device: {y.device}")
    
    # Whisper model memory requirements (approximate)
    print("\n==== Whisper Model Memory Requirements ====")
    whisper_sizes = {
        "tiny": 0.5,
        "base": 1.0,
        "small": 2.0,
        "medium": 5.0,
        "large": 10.0
    }
    
    for model_size, memory_req in whisper_sizes.items():
        status = "✅ Compatible" if free_mem >= memory_req else "❌ May have issues"
        if model_size == "medium" and free_mem >= 5.0:
            status += " (Recommended for RTX 3070)"
        print(f"Model '{model_size}': {memory_req:.1f} GB required - {status}")
    
    # Check for half-precision support
    print("\n==== FP16 Support Check ====")
    if torch.cuda.is_available() and torch.cuda.get_device_capability(0) >= (7, 0):
        print("✅ GPU supports FP16 (half precision) - Enabling this will reduce memory usage")
    else:
        print("❌ GPU does not have good FP16 support - This may affect performance")
    
    # Overall assessment
    print("\n==== Overall Assessment ====")
    if free_mem >= 5.0:
        print("✅ Your GPU is compatible with the 'medium' Whisper model!")
    elif free_mem >= 2.0:
        print("⚠️ Your GPU has limited memory. The 'small' model is recommended.")
    else:
        print("⚠️ Your GPU has very limited memory. Use 'tiny' or 'base' model, or enable CPU offloading.")
    
    print("\nGPU is working correctly with PyTorch!")
else:
    print("\n==== No GPU Detected ====")
    print("CUDA is not available. Check your PyTorch installation and drivers.") 
    print("You can still use the Whisper model with CPU, but it will be significantly slower.")
    
    # Check if NVIDIA drivers are installed
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode != 0:
            print("\nNVIDIA drivers may not be properly installed. Try installing them with:")
            print("sudo apt update && sudo apt install nvidia-driver-535")
    except:
        print("\nNVIDIA drivers are not installed or nvidia-smi is not available.")
        print("If you have an NVIDIA GPU, install the drivers with:")
        print("sudo apt update && sudo apt install nvidia-driver-535") 