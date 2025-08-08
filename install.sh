#!/bin/bash
# Installation script for ESP32 PLC GUI
# This script sets up the development environment

echo "ESP32 PLC GUI - Installation Script"
echo "==================================="

# Check Python version
python_version=$(python --version 2>&1)
echo "Detected Python version: $python_version"

# Check if Python 3.11+ is available
if python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "✓ Python version is compatible"
else
    echo "✗ Python 3.11 or higher is required"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Linux/macOS
    source .venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo ""
echo "To run the application:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "  1. Activate virtual environment: .venv\\Scripts\\activate"
else
    echo "  1. Activate virtual environment: source .venv/bin/activate"
fi
echo "  2. Run the application: python Main.py"
echo ""
echo "For more information, see README.md"
