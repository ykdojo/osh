#!/usr/bin/env python3
import curses

class MenuItem:
    def __init__(self, name):
        self.name = name

class Menu:
    def __init__(self, title, items=None):
        self.title = title
        self.items = items or []
        self.selected_index = 0

    def add_item(self, item):
        self.items.append(item)

class MenuSystem:
    def __init__(self):
        self.menus = {}
        self.current_menu = None
    
    def add_menu(self, name, menu):
        self.menus[name] = menu
        if not self.current_menu:
            self.current_menu = name
    
    def draw_menu(self, stdscr):
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        menu = self.menus[self.current_menu]
        
        # Draw title
        title = f"=== {menu.title} ==="
        stdscr.addstr(1, (w - len(title)) // 2, title)
        
        # Draw menu items
        for i, item in enumerate(menu.items):
            y = 3 + i
            x = (w - len(item.name)) // 2
            
            if i == menu.selected_index:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, x - 2, f"> {item.name} <")
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, x, item.name)
                
        # Draw footer
        footer = "Use arrow keys to navigate, Enter to select, 'q' to quit"
        stdscr.addstr(h-2, (w - len(footer)) // 2, footer)
        
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
            # For submenus, always go back to main menu
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
    main_menu.add_item(MenuItem("Menu One"))
    main_menu.add_item(MenuItem("Menu Two"))
    main_menu.add_item(MenuItem("Menu Three"))
    main_menu.add_item(MenuItem("Exit"))
    menu_system.add_menu("main_menu", main_menu)
    
    # Create submenus
    menu_one = Menu("MENU ONE")
    menu_one.add_item(MenuItem("This is the content for Menu One"))
    menu_one.add_item(MenuItem(""))
    menu_one.add_item(MenuItem("Back to Main Menu"))
    menu_system.add_menu("menu_one", menu_one)
    
    menu_two = Menu("MENU TWO")
    menu_two.add_item(MenuItem("This is the content for Menu Two"))
    menu_two.add_item(MenuItem(""))
    menu_two.add_item(MenuItem("Back to Main Menu"))
    menu_system.add_menu("menu_two", menu_two)
    
    menu_three = Menu("MENU THREE")
    menu_three.add_item(MenuItem("This is the content for Menu Three"))
    menu_three.add_item(MenuItem(""))
    menu_three.add_item(MenuItem("Back to Main Menu"))
    menu_system.add_menu("menu_three", menu_three)
    
    # Main loop
    running = True
    while running:
        menu_system.draw_menu(stdscr)
        key = stdscr.getch()
        running = menu_system.handle_input(key)

if __name__ == "__main__":
    curses.wrapper(main)