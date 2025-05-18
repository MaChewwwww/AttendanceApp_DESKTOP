import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import os
import sys

class RegisterScreen(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db_manager = controller.db_manager
        
        # Configure the grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create registration form
        self.create_register_form()
        
    def create_register_form(self):
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
        
        # Right side - registration form
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Create a canvas with scrollbar for the form
        canvas = tk.Canvas(right_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(40, 0), pady=40)
        scrollbar.pack(side="right", fill="y", padx=(0, 40), pady=40)
        
        # Title
        title_label = ttk.Label(
            scrollable_frame, 
            text="Student Registration", 
            font=("TkDefaultFont", 16, "bold")
        )
        title_label.pack(pady=(0, 20), fill="x")
        
        # Form fields
        # First Name
        first_name_frame = ttk.Frame(scrollable_frame)
        first_name_frame.pack(fill="x", pady=5)
        
        first_name_label = ttk.Label(first_name_frame, text="First Name:", width=15, anchor="w")
        first_name_label.pack(side="left")
        
        self.first_name_var = tk.StringVar()
        first_name_entry = ttk.Entry(first_name_frame, textvariable=self.first_name_var)
        first_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Middle Name (optional)
        middle_name_frame = ttk.Frame(scrollable_frame)
        middle_name_frame.pack(fill="x", pady=5)
        
        middle_name_label = ttk.Label(middle_name_frame, text="Middle Name:", width=15, anchor="w")
        middle_name_label.pack(side="left")
        
        self.middle_name_var = tk.StringVar()
        middle_name_entry = ttk.Entry(middle_name_frame, textvariable=self.middle_name_var)
        middle_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Last Name
        last_name_frame = ttk.Frame(scrollable_frame)
        last_name_frame.pack(fill="x", pady=5)
        
        last_name_label = ttk.Label(last_name_frame, text="Last Name:", width=15, anchor="w")
        last_name_label.pack(side="left")
        
        self.last_name_var = tk.StringVar()
        last_name_entry = ttk.Entry(last_name_frame, textvariable=self.last_name_var)
        last_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Email
        email_frame = ttk.Frame(scrollable_frame)
        email_frame.pack(fill="x", pady=5)
        
        email_label = ttk.Label(email_frame, text="Email:", width=15, anchor="w")
        email_label.pack(side="left")
        
        self.email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=self.email_var)
        email_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Student Number
        student_number_frame = ttk.Frame(scrollable_frame)
        student_number_frame.pack(fill="x", pady=5)
        
        student_number_label = ttk.Label(student_number_frame, text="Student Number:", width=15, anchor="w")
        student_number_label.pack(side="left")
        
        self.student_number_var = tk.StringVar()
        student_number_entry = ttk.Entry(student_number_frame, textvariable=self.student_number_var)
        student_number_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Password
        password_frame = ttk.Frame(scrollable_frame)
        password_frame.pack(fill="x", pady=5)
        
        password_label = ttk.Label(password_frame, text="Password:", width=15, anchor="w")
        password_label.pack(side="left")
        
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="•")
        password_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Confirm Password
        confirm_password_frame = ttk.Frame(scrollable_frame)
        confirm_password_frame.pack(fill="x", pady=5)
        
        confirm_password_label = ttk.Label(confirm_password_frame, text="Confirm Password:", width=15, anchor="w")
        confirm_password_label.pack(side="left")
        
        self.confirm_password_var = tk.StringVar()
        confirm_password_entry = ttk.Entry(confirm_password_frame, textvariable=self.confirm_password_var, show="•")
        confirm_password_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Buttons frame
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(pady=20)
        
        # Register button
        register_button = ttk.Button(
            buttons_frame,
            text="Register",
            command=self.handle_register,
            bootstyle="success",
            width=15
        )
        register_button.pack(side="left", padx=5)
        
        # Back button
        back_button = ttk.Button(
            buttons_frame,
            text="Back to Login",
            command=self.handle_back,
            bootstyle="secondary",
            width=15
        )
        back_button.pack(side="left", padx=5)
        
        # Set focus to first name field
        first_name_entry.focus_set()
        
    def handle_register(self):
        """Handle registration form submission"""
        # Get form values
        first_name = self.first_name_var.get().strip()
        middle_name = self.middle_name_var.get().strip()
        last_name = self.last_name_var.get().strip()
        email = self.email_var.get().strip()
        student_number = self.student_number_var.get().strip()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        # Basic validation
        if not first_name or not last_name or not email or not student_number or not password:
            messagebox.showwarning("Registration Failed", "Please fill in all required fields.")
            return
            
        if password != confirm_password:
            messagebox.showwarning("Registration Failed", "Passwords do not match.")
            return
            
        # Display a loading indicator
        self.config(cursor="wait")
        self.update_idletasks()
        
        # Attempt registration (implement this method in db_manager.py)
        success, result = self.db_manager.register(
            first_name=first_name,
            middle_name=middle_name if middle_name else None,
            last_name=last_name,
            email=email,
            student_number=student_number,
            password=password
        )
        
        # Reset cursor
        self.config(cursor="")
        
        if success:
            messagebox.showinfo(
                "Registration Successful",
                "Your account has been created! You can now log in."
            )
            self.controller.show_login()
        else:
            messagebox.showerror("Registration Failed", result)
            
    def handle_back(self):
        """Go back to login screen"""
        self.controller.show_login()