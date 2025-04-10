#!/bin/bash

# Script to automatically commit and push metrics files

# Check if metrics files are modified
if git status --porcelain | grep -q "M.*metrics.*.csv"; then
    # Add the metrics files
    git add *metrics*.csv
    
    # Commit with timestamp
    git commit -m "Update metrics files - $(date '+%Y-%m-%d %H:%M')"
    
    # Push to origin
    git push origin main
    
    echo "Metrics files committed and pushed successfully"
else
    echo "No changes in metrics files to commit"
fi