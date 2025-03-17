#!/bin/bash
# Script to remove all MP4 recording files from the project directory

echo "Finding MP4 files in the current directory..."
MP4_FILES=$(find . -maxdepth 1 -name "recording_*.mp4" | sort)

if [ -z "$MP4_FILES" ]; then
    echo "No MP4 recording files found."
    exit 0
fi

echo "Found the following MP4 files:"
echo "$MP4_FILES" | sed 's/^/  /'
echo 

read -p "Do you want to remove these files? (y/n): " CONFIRM
if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
    find . -maxdepth 1 -name "recording_*.mp4" -delete
    echo "All recording files have been deleted."
else
    echo "Operation cancelled. No files were deleted."
fi