#!/usr/bin/env python3
import curses
import os
from voice_transcription import voice_transcription_functions

# Define color pair constants
PAIR_SELECTED = 1  # For selected menu items
PAIR_TITLE = 2     # For menu titles
PAIR_FOOTER = 3    # For footer text

class Menu:
    def __init__(self, title, items=None):
        self.title = title
        self.items = items or []
        self.selected_index = 0

class MenuSystem:
    def __init__(self):
        self.menus = {}
        self.current_menu = None
        self._stdscr = None
    
    def add_menu(self, name, menu):
        self.menus[name] = menu
        if not self.current_menu:
            self.current_menu = name
    
    def draw_menu(self, stdscr):
        # Store stdscr for use in other methods
        self._stdscr = stdscr
        
        # Special case for recording screen
        if self.current_menu == "recording_screen" and voice_transcription_functions.is_recording:
            # Draw the recording screen with microphone interface
            # We use a variable in the class rather than a static variable to avoid conflicting draws
            voice_transcription_functions.show_recording_screen(stdscr)
            return  # Skip regular menu drawing
        
        # Clear screen
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        # Account for borders
        max_y = h - 1
        max_x = w - 1
        
        menu = self.menus[self.current_menu]
        
        # Draw box (avoid drawing at the very edge to prevent errors)
        for i in range(1, max_y):
            stdscr.addstr(i, 0, "│")
            stdscr.addstr(i, max_x-1, "│")
        for i in range(1, max_x-1):
            stdscr.addstr(0, i, "─")
            stdscr.addstr(max_y-1, i, "─")
        
        # Draw corners
        stdscr.addstr(0, 0, "┌")
        stdscr.addstr(0, max_x-1, "┐")
        stdscr.addstr(max_y-1, 0, "└")
        stdscr.addstr(max_y-1, max_x-1, "┘")
        
        # Draw title
        title = f" {menu.title} "
        x_pos = (w - len(title)) // 2
        if x_pos > 0 and x_pos + len(title) < max_x:
            if curses.has_colors():
                stdscr.addstr(0, x_pos, title, curses.color_pair(PAIR_TITLE) | curses.A_BOLD)
            else:
                stdscr.addstr(0, x_pos, title, curses.A_BOLD)
        
        # Draw menu items
        for i, item in enumerate(menu.items):
            y = 3 + i
            
            # Skip rendering if we're out of screen space
            if y >= max_y - 2:
                continue
                
            # Ensure we don't try to write beyond the window
            display_text = f"→ {item}" if i == menu.selected_index else f"  {item}"
            if len(display_text) > max_x - 6:
                display_text = display_text[:max_x - 9] + "..."
                
            # Item display
            try:
                if i == menu.selected_index and curses.has_colors():
                    # Draw a subtle highlight for the selected item
                    stdscr.addstr(y, 2, " " * (max_x - 4), curses.color_pair(PAIR_SELECTED))
                    stdscr.addstr(y, 4, display_text, curses.color_pair(PAIR_SELECTED) | curses.A_BOLD)
                elif i == menu.selected_index:
                    # Fallback for terminals without color
                    stdscr.addstr(y, 4, display_text, curses.A_REVERSE)
                else:
                    # Regular item
                    stdscr.addstr(y, 4, display_text)
            except curses.error:
                # Ignore any curses errors from drawing
                pass
                
        # Draw footer
        footer = "↑/↓: Navigate | Enter: Select | q: Quit"
        x_pos = (w - len(footer)) // 2
        if x_pos > 0 and x_pos + len(footer) < max_x:
            try:
                if curses.has_colors():
                    stdscr.addstr(max_y-1, x_pos, footer, curses.color_pair(PAIR_FOOTER))
                else:
                    stdscr.addstr(max_y-1, x_pos, footer)
            except curses.error:
                pass
        
        stdscr.refresh()
    
    def handle_input(self, key):
        current_menu = self.menus[self.current_menu]
        
        if key == curses.KEY_UP:
            current_menu.selected_index = max(0, current_menu.selected_index - 1)
            return True
        elif key == curses.KEY_DOWN:
            current_menu.selected_index = min(len(current_menu.items) - 1, current_menu.selected_index + 1)
            return True
        elif key == 10:  # Enter key
            return self.select_item()
        elif key == ord('q'):
            return False
        
        return True
    
    def select_item(self):
        current_menu = self.menus[self.current_menu]
        selected_index = current_menu.selected_index
        
        if self.current_menu == "main_menu":
            if selected_index == 0:
                self.current_menu = "menu_voice"  # Voice Transcription menu is now first
            elif selected_index == 1:
                self.current_menu = "menu_two"
            elif selected_index == 2:
                self.current_menu = "menu_three"
            elif selected_index == 3:
                return False  # Exit
        elif self.current_menu == "menu_voice":
            # Handle voice transcription functionality
            if selected_index == 0:
                # Start transcription - it will handle the state change to recording_screen
                voice_transcription_functions.transcribe(self._stdscr)
                # Continue the event loop
                return True
            elif selected_index == 1:
                # Go to test screen
                voice_transcription_functions.show_test_screen()
                return True
            elif selected_index == 2:
                self.current_menu = "main_menu"
                return True
        elif self.current_menu == "recording_screen":
            # Any key (except shortcuts handled by listener) stops recording and returns to voice menu
            if voice_transcription_functions.is_recording:
                # Stop recording and return to voice menu
                voice_transcription_functions.stop_recording()
            
            # Return to voice menu
            self.current_menu = "menu_voice"
            return True
        elif self.current_menu == "test_screen":
            # Any key returns to the voice transcription menu
            self.current_menu = "menu_voice"
            return True
        else:
            # For other submenus, go back to main menu when selecting "Back"
            if selected_index == len(current_menu.items) - 1:
                self.current_menu = "main_menu"
        
        return True

def main(stdscr):
    # Set up curses
    curses.curs_set(0)  # Hide cursor
    # Use timeout mode instead of nodelay for better CPU usage
    stdscr.timeout(50)  # 50ms timeout
    
    # Initialize colors if terminal supports them
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()  # Use terminal's default colors
        
        # Init color pairs with subtle designer-friendly colors
        # Light blue background for selected items (not too vibrant)
        curses.init_pair(PAIR_SELECTED, 0, 74)   # Dark text on light dusty blue
        # Subtle orangish color for title that complements the blue
        curses.init_pair(PAIR_TITLE, 173, -1)    # Soft coral/orange on default background
        # Brighter footer text that's more visible
        curses.init_pair(PAIR_FOOTER, 145, -1)   # Lighter grayish-lavender for footer
    
    # Create menu system
    menu_system = MenuSystem()
    
    # Set up keyboard shortcut listener for voice transcription
    print("Setting up voice transcription keyboard shortcut")
    voice_transcription_functions.set_menu_system(menu_system)
    voice_transcription_functions.stdscr = stdscr
    try:
        voice_transcription_functions.start_keyboard_listener()
    except Exception as e:
        print(f"Error starting keyboard listener: {e}")
    
    # Create main menu
    main_menu = Menu("MAIN MENU")
    main_menu.items = [
        "Voice Transcription",
        "Menu Two",
        "Menu Three",
        "Exit"
    ]
    menu_system.add_menu("main_menu", main_menu)
    
    # Create submenus
    
    # Voice Transcription menu (former menu_four, now first)
    voice_menu = Menu("VOICE TRANSCRIPTION")
    voice_menu.items = [
        "Start Transcribing (⇧⌘Z)",
        "Test Screen (Alt)",
        "Back to Main Menu"
    ]
    menu_system.add_menu("menu_voice", voice_menu)
    
    menu_two = Menu("MENU TWO")
    menu_two.items = [
        "Item 2-1",
        "Item 2-2",
        "Back to Main Menu"
    ]
    menu_system.add_menu("menu_two", menu_two)
    
    menu_three = Menu("MENU THREE")
    menu_three.items = [
        "Item 3-1",
        "Item 3-2",
        "Back to Main Menu"
    ]
    menu_system.add_menu("menu_three", menu_three)
    
    # Create recording screen menu (empty, just for state tracking)
    recording_menu = Menu("RECORDING")
    recording_menu.items = []
    menu_system.add_menu("recording_screen", recording_menu)
    
    # Create test screen menu (empty, just for state tracking)
    test_menu = Menu("TEST SCREEN")
    test_menu.items = []
    menu_system.add_menu("test_screen", test_menu)
    
    # Main loop
    running = True
    while running:
        try:
            menu_system.draw_menu(stdscr)
            key = stdscr.getch()
            if key != -1:  # -1 means no key was pressed during timeout
                running = menu_system.handle_input(key)
        except curses.error:
            # Redraw on terminal resize
            stdscr.clear()
            stdscr.refresh()

if __name__ == "__main__":
    # Make sure terminal is in a good state after exiting
    os.environ.setdefault('ESCDELAY', '25')  # Reduce delay after pressing ESC
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass  # Handle Ctrl+C gracefully