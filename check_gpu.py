import torch

print("PyTorch version:", torch.__version__ if hasattr(torch, '__version__') else torch.version.__version__)
print("CUDA available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("CUDA device count:", torch.cuda.device_count())
    print("CUDA device name:", torch.cuda.get_device_name(0))
    print("CUDA device capability:", torch.cuda.get_device_capability(0))
    print("CUDA version:", torch.version.cuda)
    
    # Run a small test computation on GPU
    x = torch.rand(5, 3).cuda()
    print("Tensor on GPU:", x)
    print("Tensor device:", x.device)
    
    print("\nGPU is working correctly with PyTorch!")
else:
    print("\nCUDA is not available. Check your PyTorch installation and drivers.") 