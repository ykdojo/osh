#!/usr/bin/env python3
"""
Web visualization for reading metrics.
Provides a web dashboard to display text-to-speech conversion statistics.
"""

import os
import csv
import json
import threading
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, redirect, url_for
from collections import defaultdict

app = Flask(__name__)

# Ensure templates directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), "templates"), exist_ok=True)

# Load configuration
def load_config():
    """Load configuration from config.json or use defaults"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    defaults = {
        "reading_metrics": {
            "words_per_page": 325
        }
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Add default reading metrics if not present
            if "reading_metrics" not in config:
                config["reading_metrics"] = defaults["reading_metrics"]
                
            return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config.json: {e}. Using defaults.")
            return defaults
    else:
        print("No config.json found. Using default settings.")
        return defaults

# Get config values
config = load_config()
WORDS_PER_PAGE = config["reading_metrics"]["words_per_page"]

# Define CSV path in the project directory
READING_METRICS_CSV = os.path.join(os.path.dirname(__file__), "reading_metrics.csv")

# Create templates for the web dashboard
@app.route('/')
def index():
    """Redirect to the reading dashboard"""
    return redirect(url_for('reading_dashboard'))

@app.route('/reading')
def reading_dashboard():
    """Render the reading dashboard page"""
    return render_template('reading_dashboard.html')

@app.route('/reading/data')
def get_reading_data():
    """API endpoint to get reading metrics data"""
    # Create mock data if CSV doesn't exist yet
    if not os.path.exists(READING_METRICS_CSV):
        create_mock_data()
        
    # Read data from CSV
    data = []
    with open(READING_METRICS_CSV, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numeric strings to integers
            row['characters'] = int(row['characters'])
            row['words'] = int(row['words'])
            row['paragraphs'] = int(row['paragraphs'])
            # Parse timestamp
            row['timestamp'] = datetime.fromisoformat(row['timestamp'])
            data.append(row)
    
    # Calculate totals
    total_chars = sum(row['characters'] for row in data)
    total_words = sum(row['words'] for row in data)
    total_paragraphs = sum(row['paragraphs'] for row in data)
    
    # Calculate pages read (using industry standard of 250 words per page)
    pages_read = round(total_words / WORDS_PER_PAGE, 1)
    
    # Group by day
    daily_data = defaultdict(lambda: {"characters": 0, "words": 0, "paragraphs": 0})
    for row in data:
        day_key = row['timestamp'].strftime('%Y-%m-%d')
        daily_data[day_key]['characters'] += row['characters']
        daily_data[day_key]['words'] += row['words']
        daily_data[day_key]['paragraphs'] += row['paragraphs']
    
    # Get last 30 days
    today = datetime.now().date()
    daily_metrics = []
    for i in range(30):
        day = today - timedelta(days=i)
        day_key = day.strftime('%Y-%m-%d')
        daily_metrics.insert(0, {
            "date": day_key,
            "characters": daily_data[day_key]["characters"],
            "words": daily_data[day_key]["words"],
            "paragraphs": daily_data[day_key]["paragraphs"]
        })
    
    # Group by week
    weekly_data = defaultdict(lambda: {"characters": 0, "words": 0, "paragraphs": 0})
    for row in data:
        week_key = row['timestamp'].strftime('%Y-W%W')
        weekly_data[week_key]['characters'] += row['characters']
        weekly_data[week_key]['words'] += row['words']
        weekly_data[week_key]['paragraphs'] += row['paragraphs']
    
    # Get last 12 weeks
    weekly_metrics = []
    for i in range(12):
        week_date = today - timedelta(weeks=i)
        week_key = week_date.strftime('%Y-W%W')
        weekly_metrics.insert(0, {
            "week": week_key,
            "characters": weekly_data[week_key]["characters"],
            "words": weekly_data[week_key]["words"],
            "paragraphs": weekly_data[week_key]["paragraphs"]
        })
    
    # Group by month
    monthly_data = defaultdict(lambda: {"characters": 0, "words": 0, "paragraphs": 0})
    for row in data:
        month_key = row['timestamp'].strftime('%Y-%m')
        monthly_data[month_key]['characters'] += row['characters']
        monthly_data[month_key]['words'] += row['words']
        monthly_data[month_key]['paragraphs'] += row['paragraphs']
    
    # Get last 6 months
    monthly_metrics = []
    for i in range(6):
        # Calculate month by subtracting from current month
        month_date = today.replace(day=1)
        for _ in range(i):
            # Move to previous month
            if month_date.month == 1:
                month_date = month_date.replace(year=month_date.year-1, month=12)
            else:
                month_date = month_date.replace(month=month_date.month-1)
        
        month_key = month_date.strftime('%Y-%m')
        monthly_metrics.insert(0, {
            "month": month_key,
            "characters": monthly_data[month_key]["characters"],
            "words": monthly_data[month_key]["words"],
            "paragraphs": monthly_data[month_key]["paragraphs"]
        })
    
    return jsonify({
        "total_chars": total_chars,
        "total_words": total_words,
        "total_paragraphs": total_paragraphs,
        "pages_read": pages_read,
        "words_per_page_setting": WORDS_PER_PAGE,
        "daily_metrics": daily_metrics,
        "weekly_metrics": weekly_metrics,
        "monthly_metrics": monthly_metrics
    })

def create_mock_data():
    """Create mock data to initialize the reading metrics CSV"""
    # Create CSV file with headers if it doesn't exist
    if not os.path.exists(READING_METRICS_CSV):
        os.makedirs(os.path.dirname(READING_METRICS_CSV), exist_ok=True)
        with open(READING_METRICS_CSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'characters', 'words', 'paragraphs'])
    
    # Generate mock data for last 30 days
    today = datetime.now()
    days_with_data = random.sample(range(30), 15)  # Randomly select 15 days out of 30
    
    # Load existing data if any
    existing_data = set()
    try:
        with open(READING_METRICS_CSV, 'r', newline='') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                existing_data.add(row[0])  # Add timestamp to set
    except:
        pass
    
    # Generate and write mock data
    with open(READING_METRICS_CSV, 'a', newline='') as file:
        writer = csv.writer(file)
        
        for day in days_with_data:
            # Generate 1-3 entries per day
            entries_per_day = random.randint(1, 3)
            for _ in range(entries_per_day):
                # Generate random hour and minute
                hour = random.randint(9, 21)
                minute = random.randint(0, 59)
                
                # Create timestamp
                date = today - timedelta(days=day)
                timestamp = date.replace(hour=hour, minute=minute, second=0, microsecond=0).isoformat()
                
                # Skip if this timestamp already exists
                if timestamp in existing_data:
                    continue
                
                # Generate random metrics
                words = random.randint(50, 500)
                chars = words * random.randint(4, 6)  # Average 4-6 chars per word
                paragraphs = random.randint(1, max(1, words // 50))  # Roughly 1 paragraph per 50 words
                
                # Write to CSV
                writer.writerow([timestamp, chars, words, paragraphs])
                existing_data.add(timestamp)

# Reading dashboard template already exists in templates/reading_dashboard.html
# We don't need to recreate it each time since it has been customized

# Function to start the web server
def start_web_server(port=5051, debug=True):
    """Start the Flask web server in a background thread"""
    # Ensure mock data exists
    if not os.path.exists(READING_METRICS_CSV):
        create_mock_data()
    
    # Start server
    threading.Thread(target=lambda: app.run(host='127.0.0.1', port=port, debug=debug), daemon=True).start()
    print(f"Reading metrics web server started at http://127.0.0.1:{port}/")
    if debug:
        print("Debug mode enabled - templates will automatically reload when modified")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start reading metrics web server")
    parser.add_argument("-p", "--port", type=int, default=5051, help="Port to run web server on")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug mode (disables auto-reloading)")
    
    args = parser.parse_args()
    
    # Create mock data if needed
    if not os.path.exists(READING_METRICS_CSV):
        create_mock_data()
    
    debug_mode = not args.no_debug
    
    print(f"Starting reading metrics web server on http://127.0.0.1:{args.port}/")
    print(f"Access the reading dashboard at http://127.0.0.1:{args.port}/reading")
    if debug_mode:
        print("Debug mode enabled - templates will automatically reload when modified")
    print("Press Ctrl+C to stop the server")
    
    # Start the web server in main thread
    app.run(host='127.0.0.1', port=args.port, debug=debug_mode)