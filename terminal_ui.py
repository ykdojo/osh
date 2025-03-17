#!/usr/bin/env python3
"""
Terminal UI module for curses-based interfaces.
Provides reusable UI components and display functions.
"""

import curses

def init_curses(stdscr):
    """Initialize curses environment"""
    curses.noecho()  # Don't echo keypresses
    curses.cbreak()  # React to keys instantly
    stdscr.keypad(True)  # Enable keypad mode
    
    # Try to enable colors if terminal supports it
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()  # Use terminal's default colors for better visibility
        
        # Slightly more vibrant but still subtle colors
        curses.init_pair(1, 209, -1)  # Title - slightly brighter coral/orange
        curses.init_pair(2, 68, -1)   # Highlight - slightly brighter blue
        curses.init_pair(3, 147, -1)  # Footer - slightly brighter grayish-lavender
    
    return stdscr

def cleanup_curses(stdscr):
    """Clean up curses on exit"""
    if stdscr:
        stdscr.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()

def display_screen_template(stdscr, title, content, status_message="", footer_text=None):
    """Common screen display template to reduce code duplication"""
    if not stdscr:
        return
        
    # Clear screen
    stdscr.clear()
    
    # Get terminal dimensions
    height, width = stdscr.getmaxyx()
    
    # Display border and title
    stdscr.addstr(0, 0, "=" * (width-1))
    
    # Title with color if available
    if curses.has_colors():
        stdscr.addstr(1, 0, title.center(width-1), curses.color_pair(1))
    else:
        stdscr.addstr(1, 0, title.center(width-1))
        
    stdscr.addstr(2, 0, "=" * (width-1))
    
    # Display content
    line_num = 4
    for line in content:
        stdscr.addstr(line_num, 0, line)
        line_num += 1
    
    # Display footer
    footer_line = height - 3
    
    # Footer with color if available
    if curses.has_colors():
        color = curses.color_pair(3)
    else:
        color = curses.A_NORMAL
        
    if footer_text:
        stdscr.addstr(footer_line, 0, footer_text, color)
    else:
        stdscr.addstr(footer_line, 0, "Press ⇧⌥Z (Shift+Alt+Z) to start/stop recording", color)
        stdscr.addstr(footer_line + 1, 0, "Press Ctrl+C to exit", color)
    
    # Bottom border
    stdscr.addstr(height-1, 0, "=" * (width-1))
    
    # Display status message if any
    if status_message:
        msg_y = height - 5
        stdscr.addstr(msg_y, 0, status_message, curses.A_DIM)
    
    # Update the screen
    stdscr.refresh()