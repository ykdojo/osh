#!/usr/bin/env python3

class MenuFourFunctions:
    """Functionality for Menu Four options"""
    
    def __init__(self):
        self.results = []
    
    def option_one(self):
        """Functionality for option one"""
        return "Executed Menu Four - Option One"
    
    def option_two(self):
        """Functionality for option two"""
        return "Executed Menu Four - Option Two"
    
    def get_results(self):
        """Return the results of previous operations"""
        if not self.results:
            return ["No operations performed yet"]
        return self.results

# Create a singleton instance
menu_four_functions = MenuFourFunctions()