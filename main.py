import tkinter as tk
import customtkinter as ctk
import os
import sys
from tkinter import messagebox

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import THEME_NAME, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from app.db_manager import DatabaseManager
from app.ui.auth.auth import LoginRegister
from app.ui.student.studentdashboard import StudentDashboard
from app.ui.auth.initial_screen import InitialScreen

class AttendanceApp:
    """Main application controller for the Attendance App"""
    
    def __init__(self):
        # Initialize database manager
        self.db_manager = DatabaseManager()
        self.user_data = None
        
        # Create and configure initial screen
        self.initial_screen = InitialScreen(
            on_student_click=self.show_student_auth
        )
        
        # Configure window
        self.initial_screen.title(APP_NAME)
        self.initial_screen.geometry(f"1000x600")
        self.initial_screen.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Center window on screen
        screen_width = self.initial_screen.winfo_screenwidth()
        screen_height = self.initial_screen.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.initial_screen.geometry(f"+{x}+{y}")
        
        # Set up close handler
        self.initial_screen.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize auth and dashboard windows
        self.auth_window = None
        self.dashboard_window = None
        
    def show_student_auth(self, show_register=False):
        """Show student authentication window"""
        self.initial_screen.withdraw()
        
        # Create and configure login/registration window as CTkToplevel
        self.auth_window = LoginRegister(self.db_manager)
        self.auth_window.initial_screen = self.initial_screen  # Pass the initial screen reference
        
        # Make it a child of the initial screen to maintain proper threading context
        self.auth_window.transient(self.initial_screen)
        
        # Configure window
        self.auth_window.title(f"{APP_NAME} - Student Login")
        self.auth_window.geometry(f"1000x600")
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
        self.auth_window.protocol("WM_DELETE_WINDOW", self.on_auth_closing)
        
        # Show the window
        self.auth_window.deiconify()
        self.auth_window.show_student_auth(show_register)
        
    def show_faculty_auth(self):
        """Show faculty authentication window"""
        # TODO: Implement faculty authentication
        messagebox.showinfo("Coming Soon", "Faculty authentication will be available soon!")
        
    def on_auth_closing(self):
        """Handle auth window closing"""
        if self.auth_window:
            self.auth_window.destroy()
            self.auth_window = None
        self.initial_screen.deiconify()
        
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
        if self.auth_window:
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
        # Create a new CustomTkinter window for the dashboard
        self.dashboard_window = ctk.CTkToplevel()
        self.dashboard_window.title(f"{APP_NAME} - Dashboard")
        self.dashboard_window.geometry(f"1280x720")
        self.dashboard_window.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Configure appearance
        self.dashboard_window.configure(fg_color="#2b2b3b")
        
        # Set up close handler
        self.dashboard_window.protocol("WM_DELETE_WINDOW", self.on_dashboard_closing)
        
        # IMPORTANT: Make sure the dashboard window is properly initialized
        # and becomes the active window for threading operations
        self.dashboard_window.update_idletasks()
        self.dashboard_window.focus_set()
        
        # Create container frame
        container = ctk.CTkFrame(self.dashboard_window, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create dashboard frame - AFTER window is fully initialized
        dashboard = StudentDashboard(container, self)
        dashboard.pack(fill="both", expand=True)
        
        # Center the window
        width = self.dashboard_window.winfo_width()
        height = self.dashboard_window.winfo_height()
        x = (self.dashboard_window.winfo_screenwidth() - width) // 2
        y = (self.dashboard_window.winfo_screenheight() - height) // 2
        self.dashboard_window.geometry(f"+{x}+{y}")
        
        # DON'T make it modal - this can cause threading issues
        # Remove these lines that can interfere with main thread:
        # if self.auth_window:
        #     self.dashboard_window.transient(self.auth_window)
        # self.dashboard_window.grab_set()
        
        # Hide auth window instead of making dashboard modal
        if self.auth_window:
            self.auth_window.withdraw()
        
        # Show the window
        self.dashboard_window.deiconify()
        
        # Ensure window is ready for threading operations
        self.dashboard_window.after(100, lambda: None)  # Small delay to ensure window is ready

    def logout(self):
        """Handle user logout"""
        # Clear user data
        self.user_data = None
        
        # Close dashboard window if it exists
        if self.dashboard_window:
            self.dashboard_window.destroy()
            self.dashboard_window = None
        
        # Show initial screen again
        self.initial_screen.deiconify()
        
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
        if self.auth_window:
            self.auth_window.destroy()
            
        # Destroy initial screen and exit
        self.initial_screen.quit()
        self.initial_screen.destroy()
        
    def run(self):
        """Start the application"""
        self.initial_screen.mainloop()

if __name__ == "__main__":
    app = AttendanceApp()
    app.run()