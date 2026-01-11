# Mega File Manager - Quick Reference Cheat Sheet

## Installation (One-Time Setup)

### Quick Setup
```bash
# Upload and run setup script
scp -i your-key.pem setup_ec2.sh mega_file_manager.py ec2-user@your-ec2-ip:~/
ssh -i your-key.pem ec2-user@your-ec2-ip
chmod +x setup_ec2.sh
./setup_ec2.sh
```

### Manual Setup
```bash
# Install dependencies
pip3 install --user mega.py tqdm colorama

# Or use requirements.txt
pip3 install --user -r requirements.txt
```

## Running the Script

### Standard Run
```bash
python3 mega_file_manager.py
```

### Background Run (Recommended)
```bash
# Using screen
screen -S mega
python3 mega_file_manager.py
# Detach: Ctrl+A then D
# Reattach: screen -r mega

# Using nohup
nohup python3 mega_file_manager.py > output.log 2>&1 &
```

## Menu Navigation

### Account Selection
```
1, 2, 3... - Select saved account
Last option - Add new account
0 - Exit
```

### Confirmation Prompts
```
y - Yes, proceed
n - No, cancel
```

## Workflow

1. **Select/Add Account** → Enter credentials if new
2. **Enter Folder Path** → Path on Mega.nz (e.g., "MyFolder")
3. **Enter Custom Name** → Prefix for renamed files (e.g., "project")
4. **Review Statistics** → Check file counts and types
5. **Dry Run** → Preview changes (recommended)
6. **Confirm Operation** → Apply actual changes

## File Naming Pattern

```
Original: photo.jpg, document.docx, video.mp4
Custom name: "vacation"
Result:
  - vacation_001.jpg
  - vacation_002.docx
  - vacation_003.mp4
```

## Generated Files

| File | Purpose |
|------|---------|
| `mega_sessions.json` | Saved account credentials |
| `mega_operations.log` | Detailed operation logs |
| `backup_YYYYMMDD_HHMMSS.json` | Rename backup (rollback data) |

## Common Commands

### View Logs
```bash
# Live tail
tail -f mega_operations.log

# Last 50 lines
tail -50 mega_operations.log

# Search for errors
grep ERROR mega_operations.log
```

### Check Process Status
```bash
# List processes
ps aux | grep mega_file_manager

# Kill process
kill -9 <PID>
```

### Manage Screen Sessions
```bash
# List sessions
screen -ls

# Create new session
screen -S session_name

# Reattach to session
screen -r session_name

# Kill session
screen -X -S session_name quit
```

### Disk Space
```bash
# Check available space
df -h

# Check directory size
du -sh .
```

## Security

### Protect Credentials
```bash
chmod 600 mega_sessions.json
```

### Clear Credentials
```bash
rm mega_sessions.json
```

### View Saved Accounts (without passwords)
```bash
cat mega_sessions.json | jq 'keys'
# OR
python3 -c "import json; print(json.load(open('mega_sessions.json')).keys())"
```

## Troubleshooting Quick Fixes

### Login Failed
```bash
# Verify credentials
# Check internet connection
ping mega.nz

# Test with curl
curl https://mega.nz
```

### Module Not Found
```bash
# Reinstall dependencies
pip3 install --user --force-reinstall mega.py tqdm colorama
```

### Permission Denied
```bash
# Run from home directory
cd ~
python3 mega_file_manager.py

# Fix permissions
chmod 755 mega_file_manager.py
```

### Script Hangs
```bash
# Check network
ping 8.8.8.8

# Check CPU/Memory
top

# Restart script
# Kill and restart in screen
```

## Performance Tips

### For Large Folders (1000+ files)
- Always use dry-run first
- Run in screen session
- Monitor with `top` or `htop`
- Consider upgrading EC2 instance

### Network Issues
```bash
# Test speed
curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3 -
```

## Examples

### Example 1: Photo Organization
```
Folder: "Vacation2024"
Custom: "trip"
Stats: 150 photos, 5 PDFs
Result: trip_001.jpg ... trip_150.jpg (PDFs deleted)
```

### Example 2: Project Files
```
Folder: "ClientProject/Deliverables"
Custom: "final_delivery"
Stats: 25 files, 3 PDFs
Result: final_delivery_001.docx ... final_delivery_025.xlsx
```

## Automation

### Cron Job (runs daily at 2 AM)
```bash
crontab -e
# Add:
0 2 * * * cd /home/ec2-user && python3 mega_file_manager.py >> cron.log 2>&1
```

### Bash Script Wrapper
```bash
#!/bin/bash
cd /home/ec2-user
python3 mega_file_manager.py
if [ $? -eq 0 ]; then
    echo "Success" | mail -s "Mega Manager Success" you@email.com
else
    echo "Failed" | mail -s "Mega Manager Failed" you@email.com
fi
```

## Emergency Procedures

### Rollback Renames
```bash
# Find latest backup
ls -lt backup_*.json | head -1

# Manual rollback (requires scripting)
# Use file IDs from backup to restore original names
```

### Stop Running Operation
```bash
# Find PID
ps aux | grep mega_file_manager

# Graceful stop
kill <PID>

# Force stop
kill -9 <PID>
```

### Clear All Data
```bash
# Remove all generated files
rm mega_sessions.json mega_operations.log backup_*.json
```

## Support Checklist

Before asking for help, gather:
- [ ] Python version: `python3 --version`
- [ ] mega.py version: `pip3 show mega.py`
- [ ] Error messages from log
- [ ] Last 20 lines of log: `tail -20 mega_operations.log`
- [ ] EC2 instance type
- [ ] OS version: `cat /etc/os-release`

## Useful One-Liners

```bash
# Count files in current directory
ls -1 | wc -l

# Find all backup files
find . -name "backup_*.json"

# Show disk usage by file
ls -lh

# Monitor real-time logs with timestamp
tail -f mega_operations.log | while read line; do echo "$(date): $line"; done

# Check if script is running
pgrep -f mega_file_manager.py && echo "Running" || echo "Not running"
```

---

**Quick Help:**
- Documentation: `cat README.md`
- View script: `cat mega_file_manager.py | less`
- Python help: `python3 mega_file_manager.py --help` (if implemented)

**Emergency Contact:**
For critical issues, check logs first, then review README.md troubleshooting section.
