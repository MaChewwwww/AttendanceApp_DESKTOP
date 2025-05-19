import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import os
import sys

from ..db_manager import DatabaseManager

class LoginScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_manager = controller.db_manager
        
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create login form
        self.create_login_form()
        
    def create_login_form(self):
        # Left side - image or logo
        left_frame = ttk.Frame(self, bootstyle="light")
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        # Try to load and display a logo
        try:
            # Get the absolute path to the assets directory
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(base_dir, "assets", "images", "attendance_logo.png")
            
            # Check if the file exists, use a placeholder if not
            if not os.path.exists(image_path):
                # Create a solid color placeholder
                logo_img = Image.new('RGB', (300, 300), color=(32, 32, 96))
                logo_photo = ImageTk.PhotoImage(logo_img)
            else:
                # Load the actual logo
                logo_img = Image.open(image_path)
                logo_img = logo_img.resize((300, 300))
                logo_photo = ImageTk.PhotoImage(logo_img)
                
            logo_label = ttk.Label(left_frame, image=logo_photo)
            logo_label.image = logo_photo  # Keep a reference to prevent garbage collection
            logo_label.pack(expand=True, fill="both", padx=20, pady=20)
            
        except Exception as e:
            print(f"Error loading logo: {e}")
            # If logo fails, just show app name
            app_name = ttk.Label(
                left_frame, 
                text="Attendance App", 
                font=("TkDefaultFont", 24, "bold"),
                bootstyle="light"
            )
            app_name.pack(expand=True)
        
        # Right side - login form
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        form_frame = ttk.Frame(right_frame, width=300)
        form_frame.pack(expand=True, fill="y", padx=40, pady=40)
        
        # Title
        title_label = ttk.Label(
            form_frame, 
            text="Login", 
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Email field
        email_frame = ttk.Frame(form_frame)
        email_frame.pack(fill="x", pady=10)
        
        email_label = ttk.Label(email_frame, text="Email:", width=10, anchor="w")
        email_label.pack(side="left")
        
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.email_var, width=30)
        email_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Password field
        password_frame = ttk.Frame(form_frame)
        password_frame.pack(fill="x", pady=10)
        
        password_label = ttk.Label(password_frame, text="Password:", width=10, anchor="w")
        password_label.pack(side="left")
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="•", width=30)
        password_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Buttons frame
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(pady=20)
        
        # Login button
        login_button = ttk.Button(
            buttons_frame, 
            text="Login", 
            command=self.handle_login, 
            bootstyle="primary",
            width=15
        )
        login_button.pack(side="left", padx=5)
        
        # Register button
        register_button = ttk.Button(
            buttons_frame, 
            text="Register", 
            command=self.handle_register, 
            bootstyle="secondary",
            width=15
        )
        register_button.pack(side="left", padx=5)
        
        # Set focus to email field
        email_entry.focus_set()
        
        # Bind Enter key to login
        self.bind_all("<Return>", lambda event: self.handle_login())
        
    def handle_login(self):
        email = self.email_var.get()
        password = self.password_var.get()
        
        if not email or not password:
            messagebox.showwarning("Login Failed", "Please enter both email and password.")
            return
            
        # Display a loading indicator
        self.config(cursor="wait")
        self.update_idletasks()
        
        # Attempt login
        success, result = self.db_manager.login(email, password)
        
        # Reset cursor
        self.config(cursor="")
        
        if success:
            # Store user data in controller
            self.controller.user_data = result
            
            # Show welcome message
            messagebox.showinfo(
                "Login Successful",
                f"Welcome {result['first_name']} {result['last_name']}!"
            )
            
            # Navigate based on role
            if result.get('role') == "Student":
                self.controller.show_student_dashboard()
            elif result.get('role') == "Admin":
                # Will be implemented later
                messagebox.showinfo("Not Implemented", "Admin dashboard will be available soon.")
            else:
                # Default to student dashboard for now
                self.controller.show_student_dashboard()
        else:
            messagebox.showerror("Login Failed", result)
            
    def handle_register(self):
        """Navigate to registration screen"""
        self.controller.show_register()