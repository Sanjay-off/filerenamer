#!/usr/bin/env python3
"""
Mega.nz File Manager
A comprehensive tool for managing files on Mega.nz cloud storage
- Multi-account support with session persistence
- Recursive file renaming with custom naming
- PDF cleanup
- Progress tracking and detailed logging
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import getpass

try:
    from mega import Mega
except ImportError:
    print("ERROR: mega.py library not found!")
    print("Please install it using: pip install mega.py")
    sys.exit(1)

try:
    from tqdm import tqdm
except ImportError:
    print("WARNING: tqdm not found. Installing for progress bars...")
    os.system("pip install tqdm")
    from tqdm import tqdm

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    print("WARNING: colorama not found. Installing for colored output...")
    os.system("pip install colorama")
    from colorama import init, Fore, Style
    init(autoreset=True)


class MegaFileManager:
    """Main class for managing Mega.nz files"""
    
    CONFIG_FILE = "mega_sessions.json"
    LOG_FILE = "mega_operations.log"
    BACKUP_FILE = "rename_backup.json"
    
    def __init__(self):
        self.mega = Mega()
        self.mega_instance = None
        self.current_account = None
        self.setup_logging()
        self.sessions = self.load_sessions()
        
    def setup_logging(self):
        """Configure logging to file and console"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_sessions(self) -> Dict:
        """Load saved sessions from config file"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading sessions: {e}")
                return {}
        return {}
    
    def save_sessions(self):
        """Save sessions to config file"""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(self.sessions, f, indent=4)
            self.logger.info("Sessions saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving sessions: {e}")
    
    def display_banner(self):
        """Display application banner"""
        banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════╗
║         MEGA.NZ FILE MANAGER v1.0                    ║
║         Automated File Organization Tool              ║
╚═══════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)
    
    def select_or_add_account(self) -> Tuple[str, str]:
        """Select existing account or add new one"""
        print(f"\n{Fore.YELLOW}=== ACCOUNT SELECTION ==={Style.RESET_ALL}")
        
        if self.sessions:
            print(f"\n{Fore.GREEN}Saved accounts:{Style.RESET_ALL}")
            accounts = list(self.sessions.keys())
            for idx, email in enumerate(accounts, 1):
                last_used = self.sessions[email].get('last_used', 'Never')
                print(f"  {idx}. {email} (Last used: {last_used})")
            
            print(f"  {len(accounts) + 1}. Add new account")
            print(f"  0. Exit")
            
            while True:
                try:
                    choice = input(f"\n{Fore.CYAN}Select option: {Style.RESET_ALL}").strip()
                    choice = int(choice)
                    
                    if choice == 0:
                        print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                        sys.exit(0)
                    elif 1 <= choice <= len(accounts):
                        email = accounts[choice - 1]
                        confirm = input(f"{Fore.CYAN}Use account '{email}'? (y/n): {Style.RESET_ALL}").lower()
                        if confirm == 'y':
                            password = self.sessions[email]['password']
                            return email, password
                    elif choice == len(accounts) + 1:
                        return self.add_new_account()
                    else:
                        print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Please enter a number!{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No saved accounts found.{Style.RESET_ALL}")
            return self.add_new_account()
    
    def add_new_account(self) -> Tuple[str, str]:
        """Add a new Mega account"""
        print(f"\n{Fore.YELLOW}=== ADD NEW ACCOUNT ==={Style.RESET_ALL}")
        email = input(f"{Fore.CYAN}Enter Mega email: {Style.RESET_ALL}").strip()
        password = getpass.getpass(f"{Fore.CYAN}Enter Mega password: {Style.RESET_ALL}")
        return email, password
    
    def login(self, email: str, password: str) -> bool:
        """Login to Mega account"""
        try:
            print(f"\n{Fore.YELLOW}Logging in to {email}...{Style.RESET_ALL}")
            self.mega_instance = self.mega.login(email, password)
            
            # Save session
            self.sessions[email] = {
                'password': password,
                'last_used': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.save_sessions()
            self.current_account = email
            
            print(f"{Fore.GREEN}✓ Successfully logged in!{Style.RESET_ALL}")
            self.logger.info(f"Logged in to account: {email}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Login failed: {e}{Style.RESET_ALL}")
            self.logger.error(f"Login failed for {email}: {e}")
            return False
    
    def find_folder(self, folder_path: str) -> Optional[dict]:
        """Find folder in Mega by path"""
        try:
            print(f"\n{Fore.YELLOW}Searching for folder: {folder_path}{Style.RESET_ALL}")
            files = self.mega_instance.get_files()
            
            # Search for folder
            for file_id, file_data in files.items():
                if file_data['a'] and 'n' in file_data['a']:
                    if file_data['a']['n'] == folder_path and file_data['t'] == 1:
                        print(f"{Fore.GREEN}✓ Folder found!{Style.RESET_ALL}")
                        return {'id': file_id, 'data': file_data}
            
            # If not found at root, search recursively
            for file_id, file_data in files.items():
                if file_data['a'] and 'n' in file_data['a']:
                    if folder_path in file_data['a']['n'] and file_data['t'] == 1:
                        confirm = input(f"{Fore.CYAN}Found '{file_data['a']['n']}'. Is this correct? (y/n): {Style.RESET_ALL}")
                        if confirm.lower() == 'y':
                            return {'id': file_id, 'data': file_data}
            
            print(f"{Fore.RED}✗ Folder not found!{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            print(f"{Fore.RED}Error finding folder: {e}{Style.RESET_ALL}")
            self.logger.error(f"Error finding folder: {e}")
            return None
    
    def get_all_files_recursive(self, folder_id: str) -> List[dict]:
        """Get all files recursively from folder and subfolders"""
        all_files = []
        files = self.mega_instance.get_files()
        
        def traverse(parent_id):
            for file_id, file_data in files.items():
                if file_data['p'] == parent_id:
                    if file_data['t'] == 0:  # It's a file
                        all_files.append({
                            'id': file_id,
                            'name': file_data['a']['n'] if 'a' in file_data and 'n' in file_data['a'] else 'unknown',
                            'data': file_data
                        })
                    elif file_data['t'] == 1:  # It's a folder
                        traverse(file_id)
        
        traverse(folder_id)
        return all_files
    
    def analyze_folder(self, folder_id: str) -> Dict:
        """Analyze folder contents"""
        print(f"\n{Fore.YELLOW}Analyzing folder contents...{Style.RESET_ALL}")
        
        all_files = self.get_all_files_recursive(folder_id)
        
        stats = {
            'total_files': len(all_files),
            'pdf_files': 0,
            'other_files': 0,
            'file_types': {}
        }
        
        for file_info in all_files:
            name = file_info['name']
            ext = Path(name).suffix.lower()
            
            if ext == '.pdf':
                stats['pdf_files'] += 1
            else:
                stats['other_files'] += 1
            
            stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
        
        return stats
    
    def display_stats(self, stats: Dict):
        """Display folder statistics"""
        print(f"\n{Fore.CYAN}=== FOLDER STATISTICS ==={Style.RESET_ALL}")
        print(f"Total files: {Fore.GREEN}{stats['total_files']}{Style.RESET_ALL}")
        print(f"PDF files: {Fore.RED}{stats['pdf_files']}{Style.RESET_ALL} (will be deleted)")
        print(f"Other files: {Fore.GREEN}{stats['other_files']}{Style.RESET_ALL} (will be renamed)")
        
        print(f"\n{Fore.CYAN}File types breakdown:{Style.RESET_ALL}")
        for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
            ext_display = ext if ext else '(no extension)'
            print(f"  {ext_display}: {count}")
    
    def delete_pdfs(self, folder_id: str, dry_run: bool = False) -> int:
        """Delete all PDF files from folder recursively"""
        all_files = self.get_all_files_recursive(folder_id)
        pdf_files = [f for f in all_files if f['name'].lower().endswith('.pdf')]
        
        if not pdf_files:
            print(f"{Fore.YELLOW}No PDF files found.{Style.RESET_ALL}")
            return 0
        
        print(f"\n{Fore.RED}{'[DRY RUN] ' if dry_run else ''}Deleting {len(pdf_files)} PDF files...{Style.RESET_ALL}")
        
        deleted_count = 0
        
        for pdf_file in tqdm(pdf_files, desc="Deleting PDFs", unit="file"):
            try:
                if not dry_run:
                    self.mega_instance.destroy(pdf_file['id'])
                    self.logger.info(f"Deleted PDF: {pdf_file['name']}")
                else:
                    self.logger.info(f"[DRY RUN] Would delete: {pdf_file['name']}")
                deleted_count += 1
            except Exception as e:
                print(f"\n{Fore.RED}Error deleting {pdf_file['name']}: {e}{Style.RESET_ALL}")
                self.logger.error(f"Error deleting {pdf_file['name']}: {e}")
        
        return deleted_count
    
    def rename_files(self, folder_id: str, custom_name: str, dry_run: bool = False) -> int:
        """Rename all files recursively with custom name and numbering"""
        all_files = self.get_all_files_recursive(folder_id)
        # Exclude PDFs as they'll be deleted
        files_to_rename = [f for f in all_files if not f['name'].lower().endswith('.pdf')]
        
        if not files_to_rename:
            print(f"{Fore.YELLOW}No files to rename.{Style.RESET_ALL}")
            return 0
        
        # Sort files by name for consistent numbering
        files_to_rename.sort(key=lambda x: x['name'])
        
        # Create backup of original names
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'custom_name': custom_name,
            'files': []
        }
        
        print(f"\n{Fore.CYAN}{'[DRY RUN] ' if dry_run else ''}Renaming {len(files_to_rename)} files...{Style.RESET_ALL}")
        
        renamed_count = 0
        
        for idx, file_info in enumerate(tqdm(files_to_rename, desc="Renaming files", unit="file"), 1):
            try:
                original_name = file_info['name']
                extension = Path(original_name).suffix
                new_name = f"{custom_name}_{idx:03d}{extension}"
                
                backup_data['files'].append({
                    'file_id': file_info['id'],
                    'original_name': original_name,
                    'new_name': new_name
                })
                
                if not dry_run:
                    self.mega_instance.rename(file_info['id'], new_name)
                    self.logger.info(f"Renamed: {original_name} -> {new_name}")
                else:
                    self.logger.info(f"[DRY RUN] Would rename: {original_name} -> {new_name}")
                
                renamed_count += 1
                
            except Exception as e:
                print(f"\n{Fore.RED}Error renaming {file_info['name']}: {e}{Style.RESET_ALL}")
                self.logger.error(f"Error renaming {file_info['name']}: {e}")
        
        # Save backup data
        if not dry_run and renamed_count > 0:
            try:
                backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(backup_file, 'w') as f:
                    json.dump(backup_data, f, indent=4)
                print(f"\n{Fore.GREEN}✓ Backup saved to: {backup_file}{Style.RESET_ALL}")
            except Exception as e:
                self.logger.error(f"Error saving backup: {e}")
        
        return renamed_count
    
    def run(self):
        """Main execution flow"""
        self.display_banner()
        
        # Account selection and login
        email, password = self.select_or_add_account()
        
        if not self.login(email, password):
            print(f"{Fore.RED}Cannot proceed without successful login.{Style.RESET_ALL}")
            return
        
        # Get folder path
        print(f"\n{Fore.YELLOW}=== FOLDER SELECTION ==={Style.RESET_ALL}")
        folder_path = input(f"{Fore.CYAN}Enter Mega folder path: {Style.RESET_ALL}").strip()
        
        folder = self.find_folder(folder_path)
        if not folder:
            print(f"{Fore.RED}Folder not found. Exiting.{Style.RESET_ALL}")
            return
        
        # Analyze folder
        stats = self.analyze_folder(folder['id'])
        self.display_stats(stats)
        
        if stats['total_files'] == 0:
            print(f"{Fore.YELLOW}No files found in folder. Exiting.{Style.RESET_ALL}")
            return
        
        # Get custom name
        print(f"\n{Fore.YELLOW}=== FILE NAMING ==={Style.RESET_ALL}")
        custom_name = input(f"{Fore.CYAN}Enter custom name for files: {Style.RESET_ALL}").strip()
        
        if not custom_name:
            print(f"{Fore.RED}Custom name cannot be empty. Exiting.{Style.RESET_ALL}")
            return
        
        # Dry run option
        print(f"\n{Fore.YELLOW}=== OPERATION MODE ==={Style.RESET_ALL}")
        dry_run_choice = input(f"{Fore.CYAN}Perform dry run first? (recommended) (y/n): {Style.RESET_ALL}").lower()
        
        if dry_run_choice == 'y':
            print(f"\n{Fore.MAGENTA}=== DRY RUN MODE ==={Style.RESET_ALL}")
            print("No actual changes will be made. This is a preview only.\n")
            
            # Dry run: Delete PDFs
            if stats['pdf_files'] > 0:
                self.delete_pdfs(folder['id'], dry_run=True)
            
            # Dry run: Rename files
            self.rename_files(folder['id'], custom_name, dry_run=True)
            
            print(f"\n{Fore.CYAN}Dry run complete! Review the log file: {self.LOG_FILE}{Style.RESET_ALL}")
            proceed = input(f"{Fore.YELLOW}Proceed with actual operation? (y/n): {Style.RESET_ALL}").lower()
            
            if proceed != 'y':
                print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                return
        
        # Actual operation
        print(f"\n{Fore.YELLOW}=== STARTING ACTUAL OPERATION ==={Style.RESET_ALL}")
        final_confirm = input(f"{Fore.RED}This will modify your Mega files. Continue? (y/n): {Style.RESET_ALL}").lower()
        
        if final_confirm != 'y':
            print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
            return
        
        start_time = datetime.now()
        
        # Delete PDFs
        if stats['pdf_files'] > 0:
            deleted = self.delete_pdfs(folder['id'], dry_run=False)
            print(f"{Fore.GREEN}✓ Deleted {deleted} PDF files{Style.RESET_ALL}")
        
        # Rename files
        renamed = self.rename_files(folder['id'], custom_name, dry_run=False)
        print(f"{Fore.GREEN}✓ Renamed {renamed} files{Style.RESET_ALL}")
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n{Fore.CYAN}=== OPERATION COMPLETE ==={Style.RESET_ALL}")
        print(f"Files deleted: {Fore.RED}{stats['pdf_files']}{Style.RESET_ALL}")
        print(f"Files renamed: {Fore.GREEN}{renamed}{Style.RESET_ALL}")
        print(f"Duration: {Fore.YELLOW}{duration:.2f} seconds{Style.RESET_ALL}")
        print(f"Log file: {Fore.CYAN}{self.LOG_FILE}{Style.RESET_ALL}")
        
        self.logger.info(f"Operation complete - Deleted: {stats['pdf_files']}, Renamed: {renamed}, Duration: {duration:.2f}s")


def main():
    """Main entry point"""
    try:
        manager = MegaFileManager()
        manager.run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
