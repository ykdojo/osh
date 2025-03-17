#!/usr/bin/env python3
import curses
import time

def main(stdscr):
    # Initialize curses
    curses.curs_set(0)  # Hide cursor
    stdscr.clear()
    stdscr.refresh()
    
    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, 74, -1)   # Light dusty blue for user messages
    curses.init_pair(2, 173, -1)  # Subtle coral/orange for AI messages
    curses.init_pair(3, 145, -1)  # Light grayish-lavender for info messages
    
    # Base chat history
    base_chat = [
        ("User", "Hello, how are you today?"),
        ("AI", "I'm doing well, thank you! How can I help you?"),
        ("User", "I'm working on a project and need some help with scrollable content."),
        ("AI", "I'd be happy to help with that. What specifically are you trying to implement?"),
        ("User", "I want to create a scrollable chat interface like this one."),
        ("AI", "That's a good project. You'll need to use curses pads for efficient scrolling. They allow you to create content larger than the visible screen."),
        ("User", "How do pads work exactly?"),
        ("AI", "Pads are like windows but can be larger than the physical screen. You create a pad with the total size needed, then use pad.refresh() to display just a portion of it on screen. By changing which portion you display, you create the scrolling effect."),
        ("User", "That makes sense. Any other tips?"),
        ("AI", "Yes, a few important things to keep in mind:\n\n1. Track scroll position carefully\n2. Handle window resizing\n3. Add visual indicators for scrolling\n4. Handle text wrapping for long messages\n5. Use proper error handling for boundary cases"),
        ("User", "Could you explain more about text wrapping?"),
        ("AI", "Sure! Text wrapping is crucial for a good chat UI. When messages are longer than the available width, you need to split them into multiple lines. In curses, you have to handle this manually by:\n\n1. Calculating the available width\n2. Splitting the text into chunks that fit that width\n3. Adding each chunk on a new line\n4. Keeping track of how many lines each message takes\n\nThis affects your scrolling calculations since a long message might take up 5-10 lines of vertical space."),
        ("User", "What about handling emojis and special characters?"),
        ("AI", "Great question! Unicode characters like emojis can be tricky in terminal interfaces:\n\n1. Make sure your terminal supports UTF-8\n2. Use proper encoding when displaying text\n3. Be aware that some emojis and special characters take up double width in terminals\n4. Test with various characters to ensure proper display\n\nSome terminals might not render all emojis correctly, so it's good to have fallbacks."),
        ("User", "How would you implement a scrollbar indicator?"),
        ("AI", "For a scrollbar indicator in a terminal UI, you have a few options:\n\n1. Simple approach: Use arrow characters (↑/↓) at the top and bottom of the viewport when there's more content in that direction\n\n2. Percentage indicator: Show a percentage (e.g., \"50%\") to indicate current position\n\n3. ASCII scrollbar: Create a vertical bar using characters like '█' for the thumb and '│' for the track\n\n4. Position indicator: Show something like \"Lines 10-20 of 50\"\n\nThe method you choose depends on available space and aesthetics."),
        ("User", "Are there any performance considerations?"),
        ("AI", "Yes, several performance considerations for terminal UIs:\n\n1. Minimize screen refreshes - only update when necessary\n\n2. For very large chat histories, consider lazy loading or only keeping a window of messages in memory\n\n3. Use curses' pad selective refresh rather than redrawing everything\n\n4. Batch updates rather than updating character by character\n\n5. When scrolling quickly, consider temporarily reducing rendering quality\n\n6. Profile your code to identify bottlenecks if scrolling feels sluggish"),
        ("User", "What's the best way to handle keyboard shortcuts?"),
        ("AI", "For keyboard shortcuts in a curses application:\n\n1. Define a clear mapping of keys to actions\n\n2. Use familiar shortcuts where possible (arrow keys for navigation, q for quit, etc.)\n\n3. Provide visual indicators of available shortcuts\n\n4. Handle key combinations with curses.getch() and bit manipulation\n\n5. Consider making shortcuts configurable\n\n6. Group related functions under similar keys (h/j/k/l for vim-like navigation)\n\n7. Add a help screen accessible via '?' or 'h' showing all shortcuts")
    ]
    
    # Create a longer chat history by repeating elements with slight modifications
    chat_history = []
    for i in range(3):  # Repeat 3 times
        for sender, message in base_chat:
            if i > 0:
                # Add a slight modification to repeated messages
                message = f"{message} [Copy {i}]"
            chat_history.append((sender, message))
    
    # Set up the pad for scrollable content
    pad_height = len(chat_history) * 10  # Estimate height (will be more than needed)
    
    try:
        while True:
            # Get current dimensions
            height, width = stdscr.getmaxyx()
            
            # Create a pad with plenty of space
            chat_pad = curses.newpad(pad_height, width - 2)
            
            # Fill the pad with content
            y = 0
            for i, (sender, message) in enumerate(chat_history):
                # Choose color based on sender
                color = curses.color_pair(1) if sender == "User" else curses.color_pair(2)
                
                # Print the sender
                prefix = "You: " if sender == "User" else "AI: "
                chat_pad.addstr(y, 0, prefix, color | curses.A_BOLD)
                
                # Print the message with simple wrapping
                available_width = width - 8  # Leave some margin
                
                # Split message by paragraphs
                paragraphs = message.split('\n')
                for paragraph in paragraphs:
                    # Print the first part of the message on the same line as the sender
                    if paragraph == paragraphs[0]:
                        chat_pad.addstr(y, 5, paragraph[:available_width-5], color)
                        text = paragraph[available_width-5:]
                        y += 1
                    else:
                        text = paragraph
                        chat_pad.addstr(y, 0, "", color)  # Start a new paragraph
                        y += 1
                    
                    # Wrap the rest of the text
                    while text:
                        chat_pad.addstr(y, 2, text[:available_width-2], color)
                        text = text[available_width-2:]
                        y += 1
                
                # Add a blank line between messages
                y += 1
            
            # Set up scrolling
            max_scroll = max(0, y - (height - 4))
            scroll_pos = 0
            
            # Display header
            stdscr.clear()
            header = "Scrollable Chat Demo"
            stdscr.addstr(0, (width - len(header)) // 2, header, curses.color_pair(2) | curses.A_BOLD)
            instructions = "Use UP/DOWN to scroll, q to quit"
            stdscr.addstr(1, (width - len(instructions)) // 2, instructions, curses.color_pair(3))
            
            # Main display loop
            while True:
                # Show content from the pad
                try:
                    chat_pad.refresh(scroll_pos, 0, 3, 1, height - 2, width - 2)
                    
                    # Show scroll indicators if needed
                    if scroll_pos > 0:
                        stdscr.addstr(3, width - 3, "↑", curses.color_pair(3))
                    if scroll_pos < max_scroll:
                        stdscr.addstr(height - 2, width - 3, "↓", curses.color_pair(3))
                    
                    # Add a more detailed position indicator
                    if max_scroll > 0:
                        # Calculate percentage and create a progress bar
                        percent = int((scroll_pos / max_scroll) * 100)
                        bar_width = 10
                        filled = int((bar_width * percent) / 100)
                        bar = '█' * filled + '░' * (bar_width - filled)
                        
                        # Create position indicator
                        pos_indicator = f" {percent}% [{bar}]"
                        try:
                            stdscr.addstr(height - 1, width - len(pos_indicator) - 1, pos_indicator, curses.color_pair(3))
                        except curses.error:
                            # If terminal too small for full bar, show just percentage
                            try:
                                stdscr.addstr(height - 1, width - 6, f" {percent}%", curses.color_pair(3))
                            except:
                                pass
                    
                    stdscr.refresh()
                except curses.error:
                    # Handle potential errors during display
                    pass
                
                # Get user input
                try:
                    key = stdscr.getch()
                except:
                    break
                
                # Process input
                if key == ord('q'):
                    return
                elif key == curses.KEY_UP and scroll_pos > 0:
                    scroll_pos -= 1
                elif key == curses.KEY_DOWN and scroll_pos < max_scroll:
                    scroll_pos += 1
                elif key == curses.KEY_NPAGE:  # Page Down
                    scroll_pos = min(max_scroll, scroll_pos + height // 2)
                elif key == curses.KEY_PPAGE:  # Page Up
                    scroll_pos = max(0, scroll_pos - height // 2)
                elif key == curses.KEY_HOME:
                    scroll_pos = 0
                elif key == curses.KEY_END:
                    scroll_pos = max_scroll
                elif key == curses.KEY_RESIZE:
                    # Terminal was resized, restart the inner loop
                    break
    
    except Exception as e:
        # Exit gracefully on error
        curses.endwin()
        print(f"An error occurred: {e}")
        return

if __name__ == "__main__":
    curses.wrapper(main)