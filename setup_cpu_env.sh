#!/bin/bash
set -e

# Configuration
VENV_DIR=".venv"
PYTHON_VERSION="3.10"
PYTORCH_INDEX_URL="https://download.pytorch.org/whl/cpu"

# Clean up existing virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    echo "Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Find Python executable
PYTHON_BIN=$(which python3.10 || which python3)
if [ -z "$PYTHON_BIN" ]; then
    echo "Python 3.10 is required but not found. Please install it first."
    echo "You can install it using: brew install python@3.10"
    exit 1
fi

echo "Creating virtual environment with $PYTHON_BIN..."
"$PYTHON_BIN" -m venv "$VENV_DIR"

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip and setuptools
echo "Upgrading pip and setuptools..."
python -m pip install --upgrade pip setuptools wheel

# Install PyTorch CPU packages
echo "Installing PyTorch CPU packages..."
pip install torch torchvision torchaudio --index-url $PYTORCH_INDEX_URL

# Install remaining dependencies
echo "Installing other dependencies..."
pip install -r requirements-cpu.in

# Create requirements.txt for reproducibility
echo "Creating requirements.txt..."
pip freeze > requirements.txt

echo ""
echo "✅ Environment setup complete!"
echo "To activate the virtual environment, run:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To verify PyTorch is installed correctly, run:"
echo "  python -c 'import torch; print(\"PyTorch version: {}\".format(torch.__version__))'"
echo "  python -c 'import torch; print(\"CUDA available: {}\".format(torch.cuda.is_available()))'"
echo ""
echo "Note: CUDA should be False for CPU-only installation"
