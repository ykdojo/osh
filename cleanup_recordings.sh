#!/bin/bash
# Simple script to remove all recording files

# Find all recording files (mp4 for video, wav for audio)
echo "Finding recording files..."
RECORDINGS=$(find . -name "recording_*.mp4" -o -name "recording_*.wav")

# Check if any files were found
if [ -z "$RECORDINGS" ]; then
    echo "No recording files found."
    exit 0
fi

# Display files to be deleted
echo "The following recording files will be deleted:"
echo "$RECORDINGS"

# Ask for confirmation
echo
read -p "Are you sure you want to delete these files? (y/n): " CONFIRM

if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "Y" ]; then
    # Delete the files
    echo "Deleting files..."
    echo "$RECORDINGS" | xargs rm
    echo "Done! Recordings deleted."
else
    echo "Operation cancelled."
fi