import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
import sys
from tkinter import messagebox

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import THEME_NAME, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from app.db_manager import DatabaseManager
from app.ui.auth import LoginRegister
from app.ui.student.studentdashboard import StudentDashboard

class AttendanceApp:
    """Main application controller for the Attendance App"""
    
    def __init__(self):
        # Initialize database manager
        self.db_manager = DatabaseManager()
        self.user_data = None
        
        # Create and configure login/registration window
        self.auth_window = LoginRegister(self.db_manager)
        
        # Configure window
        self.auth_window.title(APP_NAME)
        self.auth_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.auth_window.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Center window on screen
        screen_width = self.auth_window.winfo_screenwidth()
        screen_height = self.auth_window.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.auth_window.geometry(f"+{x}+{y}")
        
        # Set up login success callback
        self.auth_window.set_login_success_callback(self.on_login_success)
        
        # Set up close handler
        self.auth_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize student dashboard window reference
        self.dashboard_window = None
        
    def on_login_success(self, user_data):
        """Callback for when login is successful"""
        # Store user data
        self.user_data = user_data
        
        # Show appropriate dashboard based on user role
        self.show_dashboard()
        
    def show_dashboard(self):
        """Show the appropriate dashboard based on user role"""
        # Check if user is logged in
        if not self.user_data:
            return
        
        # Hide the auth window
        self.auth_window.withdraw()
        
        # Determine which dashboard to show based on user role
        role = self.user_data.get('role', '').lower()
        
        if role == 'admin':
            # TODO: Implement admin dashboard later
            pass
        else:
            # Default to student dashboard
            self.show_student_dashboard()
            
    def show_student_dashboard(self):
        """Show the student dashboard in a new window"""
        # Create a new window for the dashboard
        self.dashboard_window = ttk.Window(themename=THEME_NAME)
        self.dashboard_window.title(f"{APP_NAME} - Dashboard")
        self.dashboard_window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.dashboard_window.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Set up close handler
        self.dashboard_window.protocol("WM_DELETE_WINDOW", self.on_dashboard_closing)
        
        # Create container frame
        container = ttk.Frame(self.dashboard_window)
        container.pack(fill="both", expand=True)
        
        # Create dashboard frame
        dashboard = StudentDashboard(container, self)
        dashboard.pack(fill="both", expand=True)
        
        # Center the window
        self.dashboard_window.update_idletasks()
        width = self.dashboard_window.winfo_width()
        height = self.dashboard_window.winfo_height()
        x = (self.dashboard_window.winfo_screenwidth() - width) // 2
        y = (self.dashboard_window.winfo_screenheight() - height) // 2
        self.dashboard_window.geometry(f"+{x}+{y}")
        
        # Show the window
        self.dashboard_window.deiconify()
        
    def logout(self):
        """Handle user logout"""
        # Clear user data
        self.user_data = None
        
        # Close dashboard window if it exists
        if self.dashboard_window:
            self.dashboard_window.destroy()
            self.dashboard_window = None
        
        # Show login screen again
        self.auth_window.deiconify()
        self.auth_window.show_login()
        
    def on_dashboard_closing(self):
        """Handle dashboard window closing"""
        # Ask if user wants to log out or exit
        response = messagebox.askyesnocancel(
            "Close Dashboard", 
            "Do you want to log out?\n\nClick 'Yes' to log out and return to login.\n"
            "Click 'No' to exit the application.\n"
            "Click 'Cancel' to continue using the application."
        )
        
        if response is True:  # Yes - log out
            self.logout()
        elif response is False:  # No - exit app
            self.on_closing()
        # Cancel - do nothing
            
    def on_closing(self):
        """Clean up resources before closing the application"""
        if hasattr(self, 'db_manager') and self.db_manager:
            if hasattr(self.db_manager, 'close'):
                self.db_manager.close()
                
        # Close all windows
        if self.dashboard_window:
            self.dashboard_window.destroy()
            
        # Destroy auth window and exit
        self.auth_window.quit()
        self.auth_window.destroy()
        
    def run(self):
        """Start the application"""
        self.auth_window.mainloop()

if __name__ == "__main__":
    app = AttendanceApp()
    app.run()