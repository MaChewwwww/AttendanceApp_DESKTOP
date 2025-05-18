import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import sys

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import THEME_NAME, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from app.db_manager import DatabaseManager
from app.ui.login import LoginScreen
from app.ui.register import RegisterScreen
from app.ui.dashboard import Dashboard

class AttendanceApp(ttk.Window):
    def __init__(self):
        super().__init__(themename=THEME_NAME)
        
        # Configure window
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Center window on screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        self.user_data = None
        
        # Setup container for frames
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        
        # Show login screen
        self.show_login()
        
    def show_login(self):
        # Remove any existing frames
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Create login frame
        login_frame = LoginScreen(self.container, self)
        login_frame.pack(fill="both", expand=True)
        
    def show_register(self):
        # Remove any existing frames
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Create register frame
        register_frame = RegisterScreen(self.container, self)
        register_frame.pack(fill="both", expand=True)
        
    def show_dashboard(self):
        # Remove any existing frames
        for widget in self.container.winfo_children():
            widget.destroy()
            
        # Create dashboard frame
        dashboard_frame = Dashboard(self.container, self)
        dashboard_frame.pack(fill="both", expand=True)
        
    def on_closing(self):
        """Clean up resources before closing"""
        if self.db_manager:
            self.db_manager.close()
        self.quit()

if __name__ == "__main__":
    app = AttendanceApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()