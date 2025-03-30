# Typing Time Saved Tracker: Implementation Plan

## Overview
Create a system to track and visualize how much typing time is saved through transcription services.

## Data Storage
- **Format**: CSV file with simple structure
- **Columns**: timestamp, characters, words
- **Location**: Store in user data directory
- **Sample**: `2025-03-29T14:30:45,1245,215`

## Metrics Calculation
- Calculate typing time saved at runtime using formula:
  - `characters / (WPM * 5) * 60` seconds
  - Default WPM: 40 (configurable)
- This approach keeps raw data clean and calculation flexible

## Integration Points
1. **Hook into transcription completion**:
   - After successful transcription, capture character/word count
   - Add new row to CSV with current timestamp and counts
   - Minimal impact on existing transcription flow

## Web Dashboard
- **Technology**: Flask (lightweight web server)
- **Implementation**: Background thread that doesn't block main app
- **Port**: Use configurable port (default: 5050)

### Dashboard Features
- **Summary Statistics**:
  - Total time saved (hours:minutes:seconds)
  - Total characters/words transcribed
  
- **Visualizations** (Chart.js):
  - **Time Period Views**:
    - Daily (last 7 days)
    - Weekly (last 4 weeks)
    - Monthly (last 6 months)
    - All time (cumulative)
  
  - **Chart Types**:
    - Line chart: Cumulative time saved over time
    - Bar chart: Time saved per period (day/week/month)
    - Pie chart: Distribution by time of day

- **User Experience**:
  - Clean, minimal interface with professional styling
  - Responsive design for desktop/mobile
  - Filter controls to adjust time periods
  - Auto-refresh option for real-time updates

## Implementation Steps
1. Create CSV data storage module
2. Implement metrics calculation functions
3. Hook into transcription completion flow
4. Develop Flask web server with background thread
5. Create HTML/CSS/JS for dashboard
6. Implement Chart.js visualizations
7. Add configuration options for typing speed
8. Test with real transcription data

## Future Enhancements
- Export feature for data
- Custom date range selection
- Typing speed calibration tool
- Session vs. lifetime statistics