#!/usr/bin/env python3
"""
Web visualization for typing metrics.
Provides a simple web dashboard to display typing time saved statistics.
"""

import os
import csv
import json
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from collections import defaultdict

app = Flask(__name__)

# Ensure templates directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), "templates"), exist_ok=True)

# Load configuration
def load_config():
    """Load configuration from config.json or use defaults"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    
    defaults = {
        "typing_metrics": {
            "wpm": 40,
            "chars_per_word": 5
        }
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config.json: {e}. Using defaults.")
            return defaults
    else:
        print("No config.json found. Using default settings.")
        return defaults

# Get config values
config = load_config()
WPM = config["typing_metrics"]["wpm"]
CHARS_PER_WORD = config["typing_metrics"]["chars_per_word"]
# Get words per page from reading_metrics if available, or use default
WORDS_PER_PAGE = config.get("reading_metrics", {}).get("words_per_page", 325)

# Create templates for the web dashboard
@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/data')
def get_data():
    """API endpoint to get metrics data"""
    csv_path = os.path.join(os.path.dirname(__file__), "typing_metrics.csv")
    
    # Return empty data if CSV doesn't exist yet
    if not os.path.exists(csv_path):
        return jsonify({
            "total_chars": 0,
            "total_words": 0,
            "total_pages": 0,
            "time_saved_minutes": 0,
            "words_per_page": WORDS_PER_PAGE,
            "daily_metrics": [],
            "weekly_metrics": [],
            "monthly_metrics": []
        })
    
    # Read data from CSV
    data = []
    with open(csv_path, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numeric strings to integers
            row['characters'] = int(row['characters'])
            row['words'] = int(row['words'])
            # Parse timestamp
            row['timestamp'] = datetime.fromisoformat(row['timestamp'])
            data.append(row)
    
    # Calculate totals
    total_chars = sum(row['characters'] for row in data)
    total_words = sum(row['words'] for row in data)
    
    # Group by day
    daily_data = defaultdict(lambda: {"characters": 0, "words": 0})
    for row in data:
        day_key = row['timestamp'].strftime('%Y-%m-%d')
        daily_data[day_key]['characters'] += row['characters']
        daily_data[day_key]['words'] += row['words']
    
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
            "time_saved_minutes": round(daily_data[day_key]["characters"] / (WPM * CHARS_PER_WORD) * 60 / 60, 1),
            "pages": round(daily_data[day_key]["words"] / WORDS_PER_PAGE, 1)
        })
    
    # Group by week
    weekly_data = defaultdict(lambda: {"characters": 0, "words": 0})
    for row in data:
        week_key = row['timestamp'].strftime('%Y-W%W')
        weekly_data[week_key]['characters'] += row['characters']
        weekly_data[week_key]['words'] += row['words']
    
    # Get last 12 weeks
    weekly_metrics = []
    for i in range(12):
        week_date = today - timedelta(weeks=i)
        week_key = week_date.strftime('%Y-W%W')
        weekly_metrics.insert(0, {
            "week": week_key,
            "characters": weekly_data[week_key]["characters"],
            "words": weekly_data[week_key]["words"],
            "time_saved_minutes": round(weekly_data[week_key]["characters"] / (WPM * CHARS_PER_WORD) * 60 / 60, 1),
            "pages": round(weekly_data[week_key]["words"] / WORDS_PER_PAGE, 1)
        })
    
    # Group by month
    monthly_data = defaultdict(lambda: {"characters": 0, "words": 0})
    for row in data:
        month_key = row['timestamp'].strftime('%Y-%m')
        monthly_data[month_key]['characters'] += row['characters']
        monthly_data[month_key]['words'] += row['words']
    
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
            "time_saved_minutes": round(monthly_data[month_key]["characters"] / (WPM * CHARS_PER_WORD) * 60 / 60, 1),
            "pages": round(monthly_data[month_key]["words"] / WORDS_PER_PAGE, 1)
        })
    
    # Calculate total pages
    total_pages = round(total_words / WORDS_PER_PAGE, 1)
    
    return jsonify({
        "total_chars": total_chars,
        "total_words": total_words,
        "total_pages": total_pages,
        "time_saved_minutes": round(total_chars / (WPM * CHARS_PER_WORD) * 60 / 60, 1),
        "wpm_setting": WPM,
        "words_per_page": WORDS_PER_PAGE,
        "daily_metrics": daily_metrics,
        "weekly_metrics": weekly_metrics,
        "monthly_metrics": monthly_metrics
    })

def create_templates():
    """Create HTML templates for the dashboard only if they don't exist"""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    dashboard_path = os.path.join(templates_dir, "dashboard.html")
    
    # Skip template creation if it already exists
    if os.path.exists(dashboard_path):
        print("Dashboard template already exists, skipping creation")
        return

# Function to start the web server
def start_web_server(port=5050, debug=True):
    """Start the Flask web server in a background thread"""
    # Create templates first
    create_templates()
    
    # Start server
    threading.Thread(target=lambda: app.run(host='127.0.0.1', port=port, debug=debug), daemon=True).start()
    print(f"Typing metrics web server started at http://127.0.0.1:{port}/")
    if debug:
        print("Debug mode enabled - templates will automatically reload when modified")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start typing metrics web server")
    parser.add_argument("-p", "--port", type=int, default=5050, help="Port to run web server on")
    parser.add_argument("--no-debug", action="store_true", help="Disable debug mode (disables auto-reloading)")
    
    args = parser.parse_args()
    
    # Make sure templates exist
    create_templates()
    
    debug_mode = not args.no_debug
    
    print(f"Starting typing metrics web server on http://127.0.0.1:{args.port}/")
    if debug_mode:
        print("Debug mode enabled - templates will automatically reload when modified")
    print("Press Ctrl+C to stop the server")
    
    # Start the web server in main thread
    app.run(host='127.0.0.1', port=args.port, debug=debug_mode)