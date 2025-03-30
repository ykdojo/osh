#!/usr/bin/env python3
"""
Simple typing metrics tracker module.
Records character and word counts from transcriptions.
"""

import os
import csv
from datetime import datetime

def ensure_csv_exists(csv_path):
    """
    Create CSV file with headers if it doesn't exist
    
    Args:
        csv_path (str): Path to CSV file
    """
    if not os.path.exists(csv_path):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'characters', 'words'])

def record_transcription(text):
    """
    Record metrics for a completed transcription
    
    Args:
        text (str): The transcribed text
    """
    # Skip empty transcriptions
    if not text:
        return
        
    # Skip if result contains one of the special messages defined in transcription_prompts.py
    if text == "NO_AUDIO" or text == "NO_AUDIBLE_SPEECH":
        return
        
    # Calculate metrics
    char_count = len(text)
    word_count = len(text.split())
    
    # Get current timestamp
    timestamp = datetime.now().isoformat()
    
    # Define CSV path in the project directory
    csv_path = os.path.join(os.path.dirname(__file__), "typing_metrics.csv")
    
    # Ensure CSV exists
    ensure_csv_exists(csv_path)
    
    # Write to CSV file
    with open(csv_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, char_count, word_count])