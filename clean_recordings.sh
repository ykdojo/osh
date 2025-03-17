#!/bin/bash
# Script to remove all recording files (MP4 and WAV) from the project directory

echo "Finding recording files in the current directory..."
ALL_FILES=$(find . -maxdepth 1 -name "recording_*.mp4" -o -name "recording_*.wav" | sort)

if [ -z "$ALL_FILES" ]; then
    echo "No recording files found."
    exit 0
fi

echo "Found the following recordings:"
echo "$ALL_FILES" | sed 's/^/  /'
echo 

read -p "Do you want to remove all these recordings? (y/n): " CONFIRM
if [[ $CONFIRM == "y" || $CONFIRM == "Y" ]]; then
    find . -maxdepth 1 -name "recording_*.mp4" -delete
    find . -maxdepth 1 -name "recording_*.wav" -delete
    echo "All recording files have been deleted."
else
    echo "Operation cancelled. No files were deleted."
fi