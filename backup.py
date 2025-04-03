#!/usr/bin/env python3
"""
Backup script for the steganography application.
This script creates a copy of all important files in a backup directory.
"""
import os
import shutil
import datetime

def create_backup():
    """Create a backup of the steganography application."""
    # Create backup directory with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Files to backup
    files_to_backup = [
        "cli.py",
        "main.py",
        "stegano.py",
        "utils.py",
        "README.md",
        "generated-icon.png",
        "secret.png"
    ]
    
    # Directories to backup
    dirs_to_backup = [
        "templates",
        "uploads",
        "outputs"
    ]
    
    # Copy files
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"Backed up: {file}")
    
    # Copy directories
    for directory in dirs_to_backup:
        if os.path.exists(directory):
            dest_dir = os.path.join(backup_dir, directory)
            shutil.copytree(directory, dest_dir)
            print(f"Backed up directory: {directory}")
    
    print(f"\nBackup completed! All files saved to: {backup_dir}")
    print(f"Total size: {get_directory_size(backup_dir) / (1024*1024):.2f} MB")

def get_directory_size(directory):
    """Calculate the total size of a directory in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if not os.path.islink(filepath):
                total_size += os.path.getsize(filepath)
    return total_size

if __name__ == "__main__":
    create_backup()