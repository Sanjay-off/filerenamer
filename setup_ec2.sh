#!/bin/bash

# Mega.nz File Manager - Ubuntu 24.04 EC2 Setup Script
# Optimized for Ubuntu 24.04 LTS on AWS EC2

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}=========================================="
    echo "  $1"
    echo -e "==========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please do not run this script as root (without sudo)"
    echo "Run as normal user: ./setup_ubuntu24.sh"
    exit 1
fi

# Main setup
print_header "Mega.nz File Manager - Ubuntu 24.04 Setup"
echo ""

# Verify Ubuntu version
print_info "Verifying Ubuntu version..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$VERSION_ID" == "24.04" ]]; then
        print_success "Ubuntu 24.04 LTS detected"
    else
        print_warning "Expected Ubuntu 24.04, found: $VERSION_ID"
        read -p "Continue anyway? (y/n): " continue_setup
        if [[ "$continue_setup" != "y" ]]; then
            exit 1
        fi
    fi
else
    print_error "Cannot detect OS version"
    exit 1
fi
echo ""

# Update system packages
print_info "Step 1/6: Updating system packages..."
sudo apt update
sudo apt upgrade -y
print_success "System packages updated"
echo ""

# Install essential packages
print_info "Step 2/6: Installing essential packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    screen \
    tmux \
    htop \
    net-tools \
    vim

print_success "Essential packages installed"
echo ""

# Verify Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_info "Python version: $PYTHON_VERSION"
echo ""

# Create project directory structure
print_info "Step 3/6: Setting up project directory..."
PROJECT_DIR="$HOME/mega-manager"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create virtual environment (recommended for Ubuntu 24.04)
print_info "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

print_success "Virtual environment created at: $PROJECT_DIR/venv"
echo ""

# Install Python dependencies
print_info "Step 4/6: Installing Python dependencies..."

# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install mega.py tqdm colorama

# Verify installation
if python3 -c "import mega; import tqdm; import colorama" 2>/dev/null; then
    print_success "Python dependencies installed successfully"
else
    print_error "Failed to install Python dependencies"
    print_info "Trying alternative installation method..."
    pip install --break-system-packages mega.py tqdm colorama
    
    if python3 -c "import mega; import tqdm; import colorama" 2>/dev/null; then
        print_success "Dependencies installed with alternative method"
    else
        print_error "Installation failed. Please check errors above."
        exit 1
    fi
fi

# Display installed package versions
echo ""
print_info "Installed package versions:"
pip show mega.py | grep Version
pip show tqdm | grep Version
pip show colorama | grep Version
echo ""

# Copy/move script files if they exist
print_info "Step 5/6: Setting up script files..."
SCRIPT_FOUND=false

if [ -f "$HOME/mega_file_manager.py" ]; then
    cp "$HOME/mega_file_manager.py" "$PROJECT_DIR/"
    chmod +x "$PROJECT_DIR/mega_file_manager.py"
    SCRIPT_FOUND=true
    print_success "Script copied from home directory"
fi

if [ -f "$HOME/requirements.txt" ]; then
    cp "$HOME/requirements.txt" "$PROJECT_DIR/"
    print_success "requirements.txt copied"
fi

if [ ! "$SCRIPT_FOUND" = true ]; then
    print_warning "mega_file_manager.py not found"
    print_info "Please upload the script to: $PROJECT_DIR/"
    print_info ""
    print_info "Command from your local machine:"
    PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo "YOUR_EC2_IP")
    echo -e "${YELLOW}  scp -i your-key.pem mega_file_manager.py ubuntu@${PUBLIC_IP}:${PROJECT_DIR}/${NC}"
fi
echo ""

# Create helper scripts
print_info "Step 6/6: Creating helper scripts..."

# Create activation helper
cat > "$PROJECT_DIR/activate.sh" << 'EOF'
#!/bin/bash
# Activate virtual environment
source venv/bin/activate
echo "Virtual environment activated!"
echo "Run: python3 mega_file_manager.py"
EOF
chmod +x "$PROJECT_DIR/activate.sh"

# Create run script
cat > "$PROJECT_DIR/run.sh" << 'EOF'
#!/bin/bash
# Run Mega File Manager
cd "$(dirname "$0")"
source venv/bin/activate
python3 mega_file_manager.py
EOF
chmod +x "$PROJECT_DIR/run.sh"

# Create run in screen script
cat > "$PROJECT_DIR/run_screen.sh" << 'EOF'
#!/bin/bash
# Run Mega File Manager in screen session
cd "$(dirname "$0")"
screen -dmS mega-manager bash -c "source venv/bin/activate && python3 mega_file_manager.py"
echo "Started in screen session 'mega-manager'"
echo "Attach with: screen -r mega-manager"
echo "Detach with: Ctrl+A then D"
EOF
chmod +x "$PROJECT_DIR/run_screen.sh"

# Create systemd service file (optional)
cat > "$PROJECT_DIR/mega-manager.service" << EOF
[Unit]
Description=Mega.nz File Manager
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$PROJECT_DIR/venv/bin/python3 $PROJECT_DIR/mega_file_manager.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Helper scripts created"
echo ""

# Create README for the project directory
cat > "$PROJECT_DIR/UBUNTU_README.md" << 'EOF'
# Mega File Manager - Ubuntu 24.04 Quick Guide

## Directory Structure
```
mega-manager/
├── venv/                    # Python virtual environment
├── mega_file_manager.py     # Main script
├── activate.sh              # Activate venv helper
├── run.sh                   # Quick run script
├── run_screen.sh           # Run in screen session
├── mega-manager.service     # Systemd service file
├── mega_sessions.json       # Generated: saved accounts
├── mega_operations.log      # Generated: operation logs
└── backup_*.json           # Generated: rename backups
```

## Quick Commands

### Activate Virtual Environment
```bash
cd ~/mega-manager
source venv/bin/activate
```

### Run the Script
```bash
# Option 1: Direct run
cd ~/mega-manager
./run.sh

# Option 2: With venv activated
cd ~/mega-manager
source venv/bin/activate
python3 mega_file_manager.py

# Option 3: Background (screen session)
cd ~/mega-manager
./run_screen.sh
screen -r mega-manager  # to attach
```

### Install as System Service (Optional)
```bash
sudo cp ~/mega-manager/mega-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mega-manager.service
sudo systemctl start mega-manager.service
sudo systemctl status mega-manager.service
```

## Troubleshooting

### Import Error
```bash
cd ~/mega-manager
source venv/bin/activate
pip install --upgrade mega.py tqdm colorama
```

### Permission Issues
```bash
chmod 755 ~/mega-manager
chmod +x ~/mega-manager/*.sh
```

### Check Logs
```bash
tail -f ~/mega-manager/mega_operations.log
```

### Network Issues
```bash
# Check connectivity
ping -c 3 mega.nz
curl -I https://mega.nz

# Check DNS
nslookup mega.nz
```

## Maintenance

### Update Dependencies
```bash
cd ~/mega-manager
source venv/bin/activate
pip install --upgrade mega.py tqdm colorama
```

### Backup Configuration
```bash
cd ~/mega-manager
cp mega_sessions.json mega_sessions.json.backup
```

### Clean Up Old Logs
```bash
cd ~/mega-manager
# Keep only last 100 lines of log
tail -100 mega_operations.log > mega_operations.log.tmp
mv mega_operations.log.tmp mega_operations.log
```

## Security

### Secure Credentials File
```bash
chmod 600 ~/mega-manager/mega_sessions.json
```

### Use UFW Firewall (if needed)
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw status
```

## Performance Monitoring

### Check System Resources
```bash
htop
# or
top
```

### Monitor Network Usage
```bash
sudo apt install nethogs
sudo nethogs
```

### Check Disk Space
```bash
df -h
du -sh ~/mega-manager/*
```
EOF

print_success "Project README created"
echo ""

# Display completion summary
print_header "Setup Complete!"
echo ""
echo -e "${GREEN}Installation Summary:${NC}"
echo "  ✓ Ubuntu 24.04 verified"
echo "  ✓ System packages updated"
echo "  ✓ Python $PYTHON_VERSION installed"
echo "  ✓ Virtual environment created"
echo "  ✓ Python dependencies installed"
echo "  ✓ Helper scripts created"
echo ""

echo -e "${BLUE}Project Directory:${NC} $PROJECT_DIR"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo ""

if [ ! "$SCRIPT_FOUND" = true ]; then
    echo "1. Upload the main script:"
    echo -e "   ${BLUE}scp -i your-key.pem mega_file_manager.py ubuntu@$PUBLIC_IP:$PROJECT_DIR/${NC}"
    echo ""
fi

echo "2. To run the script:"
echo -e "   ${BLUE}cd $PROJECT_DIR${NC}"
echo -e "   ${BLUE}./run.sh${NC}"
echo ""
echo "   OR in background:"
echo -e "   ${BLUE}./run_screen.sh${NC}"
echo ""

echo "3. View logs:"
echo -e "   ${BLUE}tail -f $PROJECT_DIR/mega_operations.log${NC}"
echo ""

echo -e "${GREEN}Quick Reference:${NC}"
echo "  Run script:        ./run.sh"
echo "  Run in screen:     ./run_screen.sh"
echo "  Activate venv:     source venv/bin/activate"
echo "  View logs:         tail -f mega_operations.log"
echo "  Attach to screen:  screen -r mega-manager"
echo ""

print_info "For detailed documentation, see: $PROJECT_DIR/UBUNTU_README.md"
print_header "Setup Script Completed Successfully"
