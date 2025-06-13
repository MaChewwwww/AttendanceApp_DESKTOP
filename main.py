import tkinter as tk
import customtkinter as ctk
import os
import sys
from tkinter import messagebox
from dotenv import load_dotenv

# Load environment variables first, before any other imports
load_dotenv()

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
        self._is_closing = False
        
        # Create main window
        self.main_window = ctk.CTk()
        self.main_window.title(APP_NAME)
        self.main_window.geometry("1000x650")
        self.main_window.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.main_window.resizable(False, False)
        
        # Store reference to main app in window for login form access
        self.main_window.main_app = self
        
        # Center window on screen
        self.center_window()
        
        # Set up close handler
        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main container that will hold all content
        self.main_container = ctk.CTkFrame(self.main_window, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Initialize screens
        self.current_screen = None
        self.initial_screen = None
        self.auth_screen = None
        self.dashboard_screen = None
        
        # Show initial screen
        self.show_initial_screen()
        
    def center_window(self):
        """Center the window on screen"""
        self.main_window.update_idletasks()
        width = self.main_window.winfo_width()
        height = self.main_window.winfo_height()
        x = (self.main_window.winfo_screenwidth() - width) // 2
        y = (self.main_window.winfo_screenheight() - height) // 2
        self.main_window.geometry(f"+{x}+{y}")
        
    def clear_content(self):
        """Clear current content from main container"""
        if self._is_closing:
            return
            
        # Cancel any pending after() calls on widgets being destroyed
        try:
            for widget in self.main_container.winfo_children():
                self._cancel_widget_after_calls(widget)
                widget.destroy()
        except tk.TclError:
            # Widget may already be destroyed
            pass
            
        self.current_screen = None
        
    def _cancel_widget_after_calls(self, widget):
        """Recursively cancel all after() calls for a widget and its children"""
        if self._is_closing:
            return
            
        try:
            # Cancel any pending after calls for this widget
            if hasattr(widget, 'after_cancel'):
                # Get all after IDs if available (this is implementation specific)
                pass
            
            # Recursively handle children
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    self._cancel_widget_after_calls(child)
        except tk.TclError:
            # Widget may already be destroyed
            pass
        
    def show_initial_screen(self):
        """Show the initial screen"""
        if self._is_closing:
            return
            
        self.clear_content()
        
        try:
            self.initial_screen = InitialScreen(
                self.main_container,
                on_student_click=self.show_student_auth
            )
            self.initial_screen.pack(fill="both", expand=True)
            self.current_screen = "initial"
        except tk.TclError:
            # Application may be closing
            pass
        
    def show_student_auth(self, show_register=False):
        """Show student authentication screen"""
        if self._is_closing:
            return
            
        self.clear_content()
        
                on_back_click=self.show_initial_screen,
                on_login_success=self.on_login_success
            )
            self.auth_screen.pack(fill="both", expand=True)
            
            if show_register:
                self.auth_screen.show_register()
            else:
                self.auth_screen.show_login()
                
            self.current_screen = "auth"
        except tk.TclError:
            # Application may be closing
            pass
        
    def on_login_success(self, user_data):
        """Callback for when login is successful"""
        if self._is_closing:
            return
            
        self.user_data = user_data
        self.show_dashboard()
        
    def show_dashboard(self):
        """Show the student dashboard"""
        if not self.user_data or self._is_closing:
            return
            
        self.clear_content()
        
        try:
            self.dashboard_screen = StudentDashboard(
                self.main_container,
                self,
                user_data=self.user_data
            )
            self.dashboard_screen.pack(fill="both", expand=True)
            self.current_screen = "dashboard"
        except tk.TclError:
            # Application may be closing
            pass
        
    def logout(self):
        """Handle user logout"""
        if self._is_closing:
            return
            
        # Clean up current screen before logout
        self._cleanup_current_screen()
        
        self.user_data = None
        
        # Small delay to ensure cleanup completes before showing new screen
        self.main_window.after(10, self._safe_show_initial_screen)
        
    def _cleanup_current_screen(self):
        """Safely cleanup the current screen"""
        try:
            if self.dashboard_screen:
                # Cancel any pending operations in dashboard
                if hasattr(self.dashboard_screen, 'cleanup'):
                    self.dashboard_screen.cleanup()
                self.dashboard_screen = None
                
            if self.auth_screen:
                self.auth_screen = None
                
            if self.initial_screen:
                self.initial_screen = None
        except Exception as e:
            print(f"Error during screen cleanup: {e}")
            
    def _safe_show_initial_screen(self):
        """Safely show initial screen after logout"""
        if not self._is_closing:
            try:
                self.show_initial_screen()
            except tk.TclError:
                # Application may be closing
                pass
        
    def on_closing(self):
        """Clean up resources before closing the application"""
        if self._is_closing:
            return
            
        self._is_closing = True
        
        try:
            # Cancel any pending after calls
            self.main_window.after_cancel("all")
        except:
            pass
            
        try:
            # Clean up current screen
            self._cleanup_current_screen()
            
            # Clean up database manager
            if hasattr(self, 'db_manager') and self.db_manager:
                if hasattr(self.db_manager, 'close'):
                    self.db_manager.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            # Force close the application
            try:
                self.main_window.quit()
            except:
                pass
            try:
                self.main_window.destroy()
            except:
                pass
        
    def run(self):
        """Start the application"""
        try:
            self.main_window.mainloop()
        except KeyboardInterrupt:
            self.on_closing()
        except Exception as e:
            print(f"Application error: {e}")
            self.on_closing()

if __name__ == "__main__":
    app = AttendanceApp()
    app.run()