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

# Get WPM from config
config = load_config()
WPM = config["typing_metrics"]["wpm"]
CHARS_PER_WORD = config["typing_metrics"]["chars_per_word"]

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
            "time_saved_minutes": round(daily_data[day_key]["characters"] / (WPM * CHARS_PER_WORD) * 60 / 60, 1)
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
            "time_saved_minutes": round(weekly_data[week_key]["characters"] / (WPM * CHARS_PER_WORD) * 60 / 60, 1)
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
            "time_saved_minutes": round(monthly_data[month_key]["characters"] / (WPM * CHARS_PER_WORD) * 60 / 60, 1)
        })
    
    return jsonify({
        "total_chars": total_chars,
        "total_words": total_words,
        "time_saved_minutes": round(total_chars / (WPM * CHARS_PER_WORD) * 60 / 60, 1),
        "wpm_setting": WPM,
        "daily_metrics": daily_metrics,
        "weekly_metrics": weekly_metrics,
        "monthly_metrics": monthly_metrics
    })

def create_templates():
    """Create HTML templates for the dashboard"""
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Typing Time Saved</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f7;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            margin-bottom: 5px;
            color: #2c3e50;
        }
        .stats-container {
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }
        .stat-card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            margin: 10px;
            flex: 1;
            min-width: 200px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        .stat-card h2 {
            margin: 0;
            font-size: 16px;
            font-weight: 500;
            color: #666;
        }
        .stat-card .value {
            font-size: 36px;
            font-weight: 700;
            color: #3498db;
            margin: 10px 0;
        }
        .chart-container {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        }
        .chart-container h2 {
            margin-top: 0;
            color: #2c3e50;
        }
        .time-period-nav {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        .time-period-nav button {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            padding: 8px 16px;
            margin: 0 4px;
            cursor: pointer;
            border-radius: 4px;
            font-weight: 500;
            transition: all 0.2s;
        }
        .time-period-nav button.active {
            background-color: #3498db;
            color: white;
            border-color: #3498db;
        }
        .time-period-nav button:hover:not(.active) {
            background-color: #e9ecef;
        }
        .chart-wrapper {
            height: 300px;
            position: relative;
        }
        .refresh-note {
            text-align: center;
            color: #888;
            font-size: 14px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Typing Time Saved</h1>
            <p>Statistics on time saved using transcription</p>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <h2>Total Estimated Time Saved</h2>
                <div class="value" id="time-saved"></div>
                <div>hours:minutes</div>
            </div>
            <div class="stat-card">
                <h2>Characters Transcribed</h2>
                <div class="value" id="total-chars"></div>
                <div>characters</div>
            </div>
            <div class="stat-card">
                <h2>Words Transcribed</h2>
                <div class="value" id="total-words"></div>
                <div>words</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>Estimated Time Saved Over Time</h2>
            <div class="time-period-nav">
                <button class="period-btn active" data-period="daily">Daily</button>
                <button class="period-btn" data-period="weekly">Weekly</button>
                <button class="period-btn" data-period="monthly">Monthly</button>
            </div>
            <div class="chart-wrapper">
                <canvas id="timeChart"></canvas>
            </div>
        </div>
        
        <div class="refresh-note">
            Data refreshes automatically when you open this page. Close and reopen to see the latest metrics.
        </div>
    </div>
    
    <script>
        // Chart.js initialization
        let timeChart;
        let currentPeriod = 'daily';
        
        // Fetch data and initialize
        fetchDataAndUpdateUI();
        
        // Add event listeners to time period buttons
        document.querySelectorAll('.period-btn').forEach(button => {
            button.addEventListener('click', () => {
                document.querySelectorAll('.period-btn').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                currentPeriod = button.getAttribute('data-period');
                updateChart();
            });
        });
        
        function fetchDataAndUpdateUI() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    // Update summary statistics
                    document.getElementById('time-saved').textContent = formatTime(data.time_saved_minutes);
                    document.getElementById('total-chars').textContent = formatNumber(data.total_chars);
                    document.getElementById('total-words').textContent = formatNumber(data.total_words);
                    
                    // Store data globally for chart updates
                    window.metricsData = data;
                    
                    // Initialize chart
                    updateChart();
                })
                .catch(error => console.error('Error fetching data:', error));
        }
        
        function updateChart() {
            const data = window.metricsData;
            if (!data) return;
            
            let chartData;
            let labels;
            let values;
            
            // Select appropriate data based on current time period
            if (currentPeriod === 'daily') {
                chartData = data.daily_metrics;
                labels = chartData.map(item => formatDate(item.date));
                values = chartData.map(item => item.time_saved_minutes);
            } else if (currentPeriod === 'weekly') {
                chartData = data.weekly_metrics;
                labels = chartData.map(item => formatWeek(item.week));
                values = chartData.map(item => item.time_saved_minutes);
            } else {
                chartData = data.monthly_metrics;
                labels = chartData.map(item => formatMonth(item.month));
                values = chartData.map(item => item.time_saved_minutes);
            }
            
            // Destroy previous chart instance if it exists
            if (timeChart) {
                timeChart.destroy();
            }
            
            // Create new chart
            const ctx = document.getElementById('timeChart').getContext('2d');
            timeChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Time Saved (minutes)',
                        data: values,
                        backgroundColor: 'rgba(52, 152, 219, 0.7)',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Minutes'
                            }
                        }
                    }
                }
            });
        }
        
        // Helper formatting functions
        function formatNumber(num) {
            return num.toLocaleString();
        }
        
        function formatTime(minutes) {
            const hours = Math.floor(minutes / 60);
            const mins = Math.round(minutes % 60);
            return `${hours}:${mins.toString().padStart(2, '0')}`;
        }
        
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
        }
        
        function formatWeek(weekStr) {
            // Extract year and week number from YYYY-WW format
            const [year, weekNum] = weekStr.split('-W');
            return `Week ${weekNum}`;
        }
        
        function formatMonth(monthStr) {
            const date = new Date(monthStr + '-01');
            return date.toLocaleDateString(undefined, { month: 'short', year: 'numeric' });
        }
    </script>
</body>
</html>
"""
    
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    with open(os.path.join(templates_dir, "dashboard.html"), "w") as f:
        f.write(html_template)

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