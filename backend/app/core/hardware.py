"""
Hardware detection utilities for GPU/CPU availability
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def detect_device() -> str:
    """Detect available compute device (GPU preferred, CPU fallback)"""
    try:
        import torch
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0) if device_count > 0 else "Unknown GPU"
            logger.info(f"CUDA GPU detected: {device_name} ({device_count} device(s))")
            return 'cuda'
        else:
            logger.info("CUDA GPU not available, using CPU")
            return 'cpu'
    except ImportError:
        logger.warning("PyTorch not available, falling back to CPU")
        return 'cpu'

def get_hardware_info() -> Dict[str, Any]:
    """Get comprehensive hardware information"""
    info = {
        "cpu_available": True,
        "gpu_available": False,
        "gpu_count": 0,
        "gpu_names": [],
        "preferred_device": "cpu"
    }

    try:
        import torch
        info["gpu_available"] = torch.cuda.is_available()
        info["gpu_count"] = torch.cuda.device_count() if info["gpu_available"] else 0

        if info["gpu_available"]:
            info["gpu_names"] = [torch.cuda.get_device_name(i) for i in range(info["gpu_count"])]
            info["preferred_device"] = "cuda"

        # Check for MPS (Metal Performance Shaders) on macOS
        if hasattr(torch, 'mps') and torch.mps.is_available():
            info["mps_available"] = True
            if info["preferred_device"] == "cpu":
                info["preferred_device"] = "mps"
        else:
            info["mps_available"] = False

    except ImportError:
        logger.warning("PyTorch not available for hardware detection")

    return info

def is_gpu_available() -> bool:
    """Quick check if GPU is available"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False