#!/usr/bin/env python3
"""
Show contents of multiple files with clear formatting.

Usage:
python show_files.py file1.py file2.py file3.py | pbcopy
"""

import sys
import os

def show_file_content(file_path):
    """Display file path and content with clear formatting"""
    try:
        # Only process if file exists
        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            return False

        # Get absolute path for clarity
        abs_path = os.path.abspath(file_path)
        
        # Print file header
        print(f"\n{'=' * 80}")
        print(f"FILE: {abs_path}")
        print(f"{'=' * 80}\n")
        
        # Print file content
        with open(file_path, 'r') as f:
            print(f.read())
            
        return True
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """Process each filename provided as an argument"""
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} file1 [file2 file3 ...]", file=sys.stderr)
        print(f"Example to copy to clipboard: python {sys.argv[0]} file1.py file2.py | pbcopy", file=sys.stderr)
        sys.exit(1)
    
    # Process each file
    success_count = 0
    for file_path in sys.argv[1:]:
        if show_file_content(file_path):
            success_count += 1
    
    # Report summary to stderr (won't be included in pbcopy)
    print(f"\nProcessed {success_count} of {len(sys.argv) - 1} files successfully", file=sys.stderr)

if __name__ == "__main__":
    main()