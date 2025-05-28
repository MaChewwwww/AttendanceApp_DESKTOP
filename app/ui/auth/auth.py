import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from customtkinter.windows.widgets.image import CTkImage
import cv2
import threading
import time
import io
import numpy as np
import os
from .login import LoginForm
from .register import RegisterForm

# Set appearance mode and theme
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("dark-blue")  

class LoginRegister(ctk.CTkToplevel):  # Changed from CTk to CTkToplevel
    def __init__(self, db_manager=None):
        super().__init__()
        
        self.db_manager = db_manager
        self.on_login_success = None
        self.initial_screen = None  # Store reference to initial screen
        
        # Configure window
        self.title("Iskoptrix - Face Recognition Attendance System")
        self.geometry("1000x600")
        self.resizable(False, False)
        
        # Create main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)
        
        # Create left panel (branding)
        self.left_panel = ctk.CTkFrame(
            self.main_container,
            width=500,
            fg_color="#1E3A8A",
            corner_radius=0
        )
        self.left_panel.pack(side="left", fill="both")
        self.left_panel.pack_propagate(False)  # Prevent panel from shrinking
        
        # Add back link
        back_link = ctk.CTkLabel(
            self.left_panel,
            text="← Back",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#ffffff",
            cursor="hand2"
        )
        back_link.place(x=20, y=20)
        back_link.bind("<Button-1>", lambda e: self.show_initial_screen())
        
        
        # Create right panel (forms)
        self.right_panel = ctk.CTkFrame(
            self.main_container,
            fg_color="#f5f5f5",
            corner_radius=0
        )
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Initialize forms
        self.login_form = LoginForm(self.right_panel, self.db_manager, on_login_success=self.on_login_success)
        self.register_form = RegisterForm(self.right_panel, self.db_manager)
        
        # Show login form by default
        self.show_login()
        
        # Center window
        self.center_window()
        
    def center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_login(self):
        """Show the login form"""
        self.register_form.pack_forget()
        self.login_form.pack(fill="both", expand=True)
        
    def show_register(self):
        """Show the registration form"""
        self.login_form.pack_forget()
        self.register_form.pack(fill="both", expand=True)
        
    def show_initial_screen(self):
        """Return to the initial screen"""
        # Hide current window
        self.withdraw()
        
        # Show the initial screen that was passed from main.py
        if hasattr(self, 'initial_screen') and self.initial_screen:
            self.initial_screen.deiconify()
        else:
            # If no initial screen exists, destroy this window
            self.destroy()
            
    def show_student_auth(self, show_register=False):
        """Show student authentication window"""
        if hasattr(self, 'initial_screen') and self.initial_screen:
            self.initial_screen.withdraw()
        self.deiconify()  # Show the current window
        if show_register:
            self.show_register()
        else:
            self.show_login()  # Show login form by default
        
    def set_login_success_callback(self, callback):
        """Set a callback function to be called after successful login"""
        self.on_login_success = callback
        # Update the login form's callback
        if hasattr(self, 'login_form'):
            self.login_form.on_login_success = callback

# For testing as standalone
if __name__ == "__main__":
    # For standalone testing, we need a root window first
    root = ctk.CTk()
    root.withdraw()  # Hide the root window
    app = LoginRegister()
    app.mainloop()