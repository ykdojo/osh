#!/usr/bin/env python3
"""
Test script for typing metrics functionality.
Generates sample data and starts the web server.
"""

import os
import time
import random
from datetime import datetime, timedelta
from typing_metrics import record_transcription
from typing_metrics_web import start_web_server

def generate_sample_data(num_entries=30):
    """
    Generate sample transcription data for testing
    
    Args:
        num_entries (int): Number of sample entries to generate
    """
    # Remove existing CSV if it exists
    csv_path = os.path.join(os.path.dirname(__file__), "typing_metrics.csv")
    if os.path.exists(csv_path):
        os.remove(csv_path)
    
    # Generate random transcription data for the past 30 days
    today = datetime.now()
    
    for i in range(num_entries):
        # Random date within the past 30 days
        days_ago = random.randint(0, 29)
        entry_date = today - timedelta(days=days_ago)
        
        # Create a random transcription
        # Between 50 and 500 words with avg 5 chars per word
        word_count = random.randint(50, 500)
        char_count = word_count * random.randint(4, 7)
        
        # Generate a fake transcription
        transcription = 'x' * char_count
        
        # Record it
        record_transcription(transcription)
        
        # Add some time variation
        time.sleep(0.1)
        
    print(f"Generated {num_entries} sample transcription entries")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test typing metrics functionality")
    parser.add_argument("--generate", action="store_true", help="Generate sample data")
    parser.add_argument("--port", type=int, default=5050, help="Port for web server")
    
    args = parser.parse_args()
    
    # Generate sample data if requested
    if args.generate:
        generate_sample_data()
    
    # Start the web server
    print(f"Starting web server at http://127.0.0.1:{args.port}/")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Import Flask app and run it directly (non-daemon) to keep script running
        from typing_metrics_web import app
        app.run(host='127.0.0.1', port=args.port, debug=False)
    except KeyboardInterrupt:
        print("\nServer stopped")