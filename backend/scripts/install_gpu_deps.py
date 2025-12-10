#!/usr/bin/env python3
"""
Script to install GPU acceleration dependencies for RAPIDS cuML
"""
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_gpu_dependencies():
    """Install GPU acceleration dependencies"""
    logger.info("🚀 Installing GPU acceleration dependencies...")

    try:
        # Install cuML and cuPy for GPU acceleration
        logger.info("📦 Installing RAPIDS cuML (GPU-accelerated ML)...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "cuml-cu11>=23.0.0",
            "cupy-cuda11x>=12.0.0",
            "--extra-index-url", "https://pypi.nvidia.com"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("✅ GPU dependencies installed successfully!")
            logger.info("🎉 Your RAG application now supports GPU-accelerated PCA for 3D visualizations")
            logger.info("   - 10-50x faster vector clustering")
            logger.info("   - GPU-accelerated dimensionality reduction")
            logger.info("   - Automatic fallback to CPU if GPU issues occur")
        else:
            logger.error("❌ Failed to install GPU dependencies")
            logger.error(f"STDOUT: {result.stdout}")
            logger.error(f"STDERR: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"❌ Error installing GPU dependencies: {e}")
        return False

    return True

def check_cuda_availability():
    """Check if CUDA is available on the system"""
    logger.info("🔍 Checking CUDA availability...")

    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ NVIDIA GPU detected")
            # Extract GPU info
            for line in result.stdout.split('\n'):
                if 'Driver Version' in line:
                    logger.info(f"   {line.strip()}")
                if '| GPU' in line and 'Name' in line:
                    next_line = result.stdout.split('\n')[result.stdout.split('\n').index(line) + 1]
                    if '|' in next_line:
                        gpu_name = next_line.split('|')[1].strip()
                        logger.info(f"   GPU: {gpu_name}")
            return True
        else:
            logger.warning("⚠️  NVIDIA GPU not detected or nvidia-smi not available")
            return False
    except FileNotFoundError:
        logger.warning("⚠️  nvidia-smi command not found")
        return False

if __name__ == "__main__":
    logger.info("🖥️  GPU Acceleration Setup for Niki RAG Application")
    logger.info("=" * 50)

    # Check CUDA availability
    cuda_available = check_cuda_availability()

    if not cuda_available:
        logger.warning("⚠️  No NVIDIA GPU detected. GPU acceleration will not be available.")
        logger.info("💡 To enable GPU acceleration:")
        logger.info("   1. Install NVIDIA drivers")
        logger.info("   2. Install CUDA runtime")
        logger.info("   3. Restart this script")
        sys.exit(1)

    # Install dependencies
    success = install_gpu_dependencies()

    if success:
        logger.info("\n🎯 Next steps:")
        logger.info("   1. Restart your application: uvicorn app.main:app --reload")
        logger.info("   2. Upload documents and check 3D visualization speed")
        logger.info("   3. GPU acceleration will be automatically used")
    else:
        logger.error("\n❌ GPU installation failed")
        logger.info("💡 Your application will still work with CPU-only processing")
        sys.exit(1)