# Mega.nz File Manager - Installation & Usage Guide

## Overview
This script provides automated file management for Mega.nz cloud storage with features including:
- Multi-account session management
- Recursive file renaming with sequential numbering
- Automatic PDF deletion
- Progress tracking and detailed logging
- Dry-run mode for safe testing
- Backup and rollback capabilities

## Prerequisites
- Python 3.7 or higher
- Active Mega.nz account(s)
- AWS EC2 instance (Amazon Linux 2 or Ubuntu recommended)

## Installation on AWS EC2

### Step 1: Connect to Your EC2 Instance
```bash
ssh -i your-key.pem ec2-user@your-ec2-ip
# OR for Ubuntu
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 2: Update System Packages
```bash
# For Amazon Linux 2
sudo yum update -y
sudo yum install python3 python3-pip git -y

# For Ubuntu
sudo apt update
sudo apt install python3 python3-pip git -y
```

### Step 3: Install Required Python Libraries
```bash
pip3 install mega.py tqdm colorama

# If you encounter permission issues, use:
pip3 install --user mega.py tqdm colorama
```

### Step 4: Upload the Script
**Option A: Upload directly**
```bash
# From your local machine
scp -i your-key.pem mega_file_manager.py ec2-user@your-ec2-ip:~/
```

**Option B: Create file on EC2**
```bash
nano mega_file_manager.py
# Paste the script content and save (Ctrl+X, Y, Enter)
```

### Step 5: Make Script Executable
```bash
chmod +x mega_file_manager.py
```

## Usage

### Basic Execution
```bash
python3 mega_file_manager.py
```

### Run in Background (for long operations)
```bash
nohup python3 mega_file_manager.py > output.log 2>&1 &
```

### Using Screen (recommended for long-running tasks)
```bash
# Install screen if not available
sudo yum install screen -y  # Amazon Linux
# OR
sudo apt install screen -y  # Ubuntu

# Start a screen session
screen -S mega_manager

# Run the script
python3 mega_file_manager.py

# Detach from screen: Ctrl+A then D
# Reattach to screen: screen -r mega_manager
```

## Step-by-Step Workflow

### First Run (New Account)
1. Run the script: `python3 mega_file_manager.py`
2. Select "Add new account"
3. Enter your Mega.nz email
4. Enter your Mega.nz password
5. Enter the folder path on Mega (e.g., "MyFolder" or "Documents/Projects")
6. Enter the custom name for files (e.g., "project_file")
7. Review the folder statistics
8. Choose dry-run mode (recommended for first time)
9. Review the dry-run results in the log
10. Confirm to proceed with actual operation

### Subsequent Runs (Existing Account)
1. Run the script: `python3 mega_file_manager.py`
2. Select your saved account from the list
3. Confirm the account selection
4. Continue with steps 5-10 from above

## Configuration Files

The script creates several files in the same directory:

### 1. mega_sessions.json
Stores saved account credentials and last used timestamps
```json
{
    "user@example.com": {
        "password": "your_password",
        "last_used": "2025-01-11 10:30:45"
    }
}
```

### 2. mega_operations.log
Detailed log of all operations
```
2025-01-11 10:30:45 - INFO - Logged in to account: user@example.com
2025-01-11 10:31:02 - INFO - Deleted PDF: document.pdf
2025-01-11 10:31:05 - INFO - Renamed: photo.jpg -> project_file_001.jpg
```

### 3. backup_YYYYMMDD_HHMMSS.json
Backup of original filenames (created for each rename operation)
```json
{
    "timestamp": "2025-01-11T10:30:00",
    "custom_name": "project_file",
    "files": [
        {
            "file_id": "abc123",
            "original_name": "photo.jpg",
            "new_name": "project_file_001.jpg"
        }
    ]
}
```

## Features Explained

### 1. Multi-Account Management
- Store multiple Mega accounts
- Quick switching between accounts
- Session persistence across runs
- Last-used timestamp tracking

### 2. Dry-Run Mode
- Preview all changes before applying
- No actual modifications to files
- Review in log file before confirming
- Recommended for first-time use

### 3. Progress Tracking
- Real-time progress bars for operations
- File count and speed indicators
- Colored console output for clarity
- Detailed logging of every action

### 4. Recursive Processing
- Automatically finds files in subfolders
- Maintains folder structure
- Processes all levels of nesting
- Statistics for entire folder tree

### 5. Sequential Numbering
- Files renamed with zero-padded numbers (001, 002, etc.)
- Maintains original file extensions
- Sorted alphabetically before numbering
- Example: `photo.jpg` → `myproject_001.jpg`

### 6. Backup & Recovery
- Original filenames saved before renaming
- Timestamped backup files
- Can be used for manual rollback if needed
- Includes file IDs for precise restoration

## Example Operations

### Example 1: Organize Photo Collection
```
Folder: "Vacation Photos 2024"
Custom name: "vacation"
Result:
  IMG_1234.jpg → vacation_001.jpg
  IMG_1235.jpg → vacation_002.jpg
  document.pdf → [DELETED]
  video.mp4 → vacation_003.mp4
```

### Example 2: Project Documents
```
Folder: "Project Files"
Custom name: "client_deliverable"
Result:
  report.docx → client_deliverable_001.docx
  presentation.pptx → client_deliverable_002.pptx
  notes.pdf → [DELETED]
  spreadsheet.xlsx → client_deliverable_003.xlsx
```

## Troubleshooting

### Issue: "mega.py library not found"
**Solution:**
```bash
pip3 install --user mega.py
# OR
pip3 install mega.py --break-system-packages
```

### Issue: "Login failed"
**Solutions:**
- Verify email and password are correct
- Check if Mega.nz is accessible from your region
- Try logging in manually at mega.nz to verify credentials
- Check if 2FA is enabled (not supported by mega.py)

### Issue: "Folder not found"
**Solutions:**
- Verify exact folder name (case-sensitive)
- Try entering just the folder name without full path
- Make sure folder exists in your Mega account
- Check if you have permissions to access the folder

### Issue: Script hangs or is slow
**Solutions:**
- Large folders take time - be patient
- Use screen/tmux for long operations
- Check network connection
- Monitor EC2 instance resources

### Issue: Permission denied when creating files
**Solutions:**
```bash
# Make sure you have write permissions
chmod 755 ~/
# OR run from a directory you own
cd ~
python3 mega_file_manager.py
```

## Security Considerations

### For Production Use
1. **Encrypt credentials**: Modify script to use environment variables or AWS Secrets Manager
2. **Use IAM roles**: For EC2, use IAM roles instead of storing credentials
3. **Restrict file permissions**:
   ```bash
   chmod 600 mega_sessions.json
   ```
4. **Use VPC**: Run EC2 in private subnet if processing sensitive data
5. **Enable logging**: Monitor CloudWatch logs for security events

### Best Practices
- Don't share mega_sessions.json file
- Regularly rotate Mega passwords
- Use separate Mega accounts for different projects
- Backup configuration files regularly
- Review logs periodically for unexpected activity

## Performance Tips

### For Large Folders (1000+ files)
1. **Increase EC2 instance size** if needed
2. **Use dry-run mode** to estimate time
3. **Monitor bandwidth** usage
4. **Split large operations** into smaller batches
5. **Use screen/tmux** to keep session alive

### Network Optimization
```bash
# Check network speed
curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3 -

# For better performance, use EC2 in region close to Mega.nz servers
```

## Monitoring

### View Live Logs
```bash
tail -f mega_operations.log
```

### Check Disk Space
```bash
df -h
```

### Monitor Process
```bash
ps aux | grep mega_file_manager
```

### Check Network Usage
```bash
# Install nethogs
sudo yum install nethogs -y  # Amazon Linux
sudo apt install nethogs -y  # Ubuntu

# Monitor network usage
sudo nethogs
```

## Uninstallation

```bash
# Remove script and generated files
rm mega_file_manager.py
rm mega_sessions.json
rm mega_operations.log
rm backup_*.json

# Uninstall Python packages (optional)
pip3 uninstall mega.py tqdm colorama -y
```

## Advanced Usage

### Automate with Cron
```bash
# Edit crontab
crontab -e

# Run daily at 2 AM (requires pre-configured session)
0 2 * * * cd /home/ec2-user && python3 mega_file_manager.py >> cron.log 2>&1
```

### Environment Variables (for automation)
Modify the script to accept environment variables:
```bash
export MEGA_EMAIL="user@example.com"
export MEGA_PASSWORD="password"
export MEGA_FOLDER="MyFolder"
export MEGA_CUSTOM_NAME="files"
python3 mega_file_manager.py
```

## Support & Logs

When reporting issues, include:
1. Python version: `python3 --version`
2. mega.py version: `pip3 show mega.py`
3. Relevant log entries from `mega_operations.log`
4. EC2 instance type and OS
5. Error messages (full stack trace)

## Updates & Maintenance

### Check for Updates
```bash
pip3 install --upgrade mega.py tqdm colorama
```

### Backup Configuration
```bash
# Create backup
cp mega_sessions.json mega_sessions.json.backup
cp mega_operations.log mega_operations.log.backup
```

## License & Disclaimer

This script is provided as-is. Always test with dry-run mode first. The author is not responsible for data loss. Always maintain backups of important files.

---

**Last Updated:** January 2025
**Version:** 1.0
