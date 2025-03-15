#!/usr/bin/env python3
import curses
import os

class Menu:
    def __init__(self, title, items=None):
        self.title = title
        self.items = items or []
        self.selected_index = 0

class MenuSystem:
    def __init__(self):
        self.menus = {}
        self.current_menu = None
    
    def add_menu(self, name, menu):
        self.menus[name] = menu
        if not self.current_menu:
            self.current_menu = name
    
    def draw_menu(self, stdscr):
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
            stdscr.addstr(0, x_pos, title)
        
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
                if i == menu.selected_index:
                    stdscr.addstr(y, 4, display_text)
                else:
                    stdscr.addstr(y, 4, display_text)
            except curses.error:
                # Ignore any curses errors from drawing
                pass
                
        # Draw footer
        footer = "↑/↓: Navigate | Enter: Select | q: Quit"
        x_pos = (w - len(footer)) // 2
        if x_pos > 0 and x_pos + len(footer) < max_x:
            try:
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
                self.current_menu = "menu_one"
            elif selected_index == 1:
                self.current_menu = "menu_two"
            elif selected_index == 2:
                self.current_menu = "menu_three"
            elif selected_index == 3:
                return False  # Exit
        else:
            # For submenus, go back to main menu when selecting "Back"
            if selected_index == len(current_menu.items) - 1:
                self.current_menu = "main_menu"
        
        return True

def main(stdscr):
    # Set up curses
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking input
    
    # Create menu system
    menu_system = MenuSystem()
    
    # Create main menu
    main_menu = Menu("MAIN MENU")
    main_menu.items = [
        "Menu One",
        "Menu Two",
        "Menu Three",
        "Exit"
    ]
    menu_system.add_menu("main_menu", main_menu)
    
    # Create submenus
    menu_one = Menu("MENU ONE")
    menu_one.items = [
        "Item 1-1",
        "Item 1-2",
        "Back to Main Menu"
    ]
    menu_system.add_menu("menu_one", menu_one)
    
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
    
    # Main loop
    running = True
    while running:
        try:
            menu_system.draw_menu(stdscr)
            key = stdscr.getch()
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