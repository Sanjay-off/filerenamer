#!/bin/bash

# Mega.nz File Manager - EC2 Quick Setup Script
# This script automates the installation process on AWS EC2

set -e  # Exit on error

echo "=========================================="
echo "  Mega.nz File Manager - Quick Setup"
echo "=========================================="
echo ""

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "ERROR: Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

# Update system packages
echo "Step 1/4: Updating system packages..."
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum update -y
    sudo yum install python3 python3-pip git -y
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt update
    sudo apt install python3 python3-pip git -y
else
    echo "Unsupported OS: $OS"
    exit 1
fi
echo "✓ System packages updated"
echo ""

# Install Python dependencies
echo "Step 2/4: Installing Python dependencies..."
pip3 install --user mega.py tqdm colorama

# Try alternative installation if above fails
if [ $? -ne 0 ]; then
    echo "Trying alternative installation method..."
    pip3 install --user --break-system-packages mega.py tqdm colorama
fi
echo "✓ Python dependencies installed"
echo ""

# Verify installation
echo "Step 3/4: Verifying installation..."
python3 -c "import mega; import tqdm; import colorama; print('All modules imported successfully')"
if [ $? -eq 0 ]; then
    echo "✓ Verification successful"
else
    echo "✗ Verification failed. Please check errors above."
    exit 1
fi
echo ""

# Optional: Install screen for background execution
echo "Step 4/4: Installing screen (optional, for background execution)..."
if [ "$OS" = "amzn" ] || [ "$OS" = "rhel" ] || [ "$OS" = "centos" ]; then
    sudo yum install screen -y
elif [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    sudo apt install screen -y
fi
echo "✓ Screen installed"
echo ""

# Check if script file exists
if [ ! -f "mega_file_manager.py" ]; then
    echo "WARNING: mega_file_manager.py not found in current directory"
    echo "Please upload the script file to this directory"
    echo ""
    echo "You can upload it using:"
    echo "  scp -i your-key.pem mega_file_manager.py $(whoami)@$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):~/"
    echo ""
else
    chmod +x mega_file_manager.py
    echo "✓ Script file found and made executable"
    echo ""
fi

# Display completion message
echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Installation Summary:"
echo "  ✓ System packages updated"
echo "  ✓ Python dependencies installed"
echo "  ✓ Installation verified"
echo "  ✓ Screen installed (for background execution)"
echo ""

# Display Python version
echo "Python version: $(python3 --version)"
echo "mega.py version: $(pip3 show mega.py | grep Version | cut -d ' ' -f 2)"
echo ""

if [ -f "mega_file_manager.py" ]; then
    echo "To run the script:"
    echo "  python3 mega_file_manager.py"
    echo ""
    echo "To run in background:"
    echo "  screen -S mega_manager"
    echo "  python3 mega_file_manager.py"
    echo "  (Press Ctrl+A then D to detach)"
    echo ""
    echo "To reattach:"
    echo "  screen -r mega_manager"
else
    echo "Next steps:"
    echo "  1. Upload mega_file_manager.py to this directory"
    echo "  2. Run: python3 mega_file_manager.py"
fi

echo ""
echo "For detailed documentation, see README.md"
echo "=========================================="
