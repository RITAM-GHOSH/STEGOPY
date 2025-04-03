#!/usr/bin/env python3
"""
Export script for the steganography application.
This script creates a single text file with all the source code and file names.
"""
import os
import datetime

def export_code():
    """Export all source code to a single file."""
    # Create export file with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = f"steganography_app_export_{timestamp}.txt"
    
    # Files to export
    files_to_export = [
        "cli.py",
        "main.py",
        "stegano.py",
        "utils.py",
        "README.md",
        "backup.py"
    ]
    
    # Templates to export
    template_files = []
    if os.path.exists("templates"):
        for file in os.listdir("templates"):
            if file.endswith(".html"):
                template_files.append(os.path.join("templates", file))
    
    # Combine all files to export
    all_files = files_to_export + template_files
    
    # Write all code to the export file
    with open(export_file, 'w', encoding='utf-8') as f:
        f.write("# Steganography Application Export\n")
        f.write(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for file_path in all_files:
            if os.path.exists(file_path):
                f.write(f"\n\n{'=' * 80}\n")
                f.write(f"# FILE: {file_path}\n")
                f.write(f"{'=' * 80}\n\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as source_file:
                        content = source_file.read()
                        f.write(content)
                except Exception as e:
                    f.write(f"# Error reading file: {str(e)}\n")
    
    print(f"Code export completed! All code saved to: {export_file}")
    print(f"Total size: {os.path.getsize(export_file) / 1024:.2f} KB")
    print(f"Number of files exported: {len(all_files)}")

if __name__ == "__main__":
    export_code()