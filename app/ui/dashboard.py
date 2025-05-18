import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk
import io
import base64
import os
from datetime import datetime

class Dashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.user_data = controller.user_data
        self.db_manager = controller.db_manager
        
        # Configure the frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)  # Welcome message
        self.rowconfigure(1, weight=0)  # Logout button
        
        # Create a simple dashboard
        self.create_dashboard()
        
    def create_dashboard(self):
        # Welcome area
        welcome_frame = ttk.Frame(self)
        welcome_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # User welcome message
        welcome_label = ttk.Label(
            welcome_frame, 
            text=f"Welcome, {self.user_data['first_name']} {self.user_data['last_name']}!",
            font=("TkDefaultFont", 16, "bold")
        )
        welcome_label.pack(anchor="center", expand=True)
        
        # Show student number
        student_label = ttk.Label(
            welcome_frame,
            text=f"Student ID: {self.user_data['student_number']}",
            font=("TkDefaultFont", 12)
        )
        student_label.pack(anchor="center")
        
        # Show current date and time
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        
        date_label = ttk.Label(
            welcome_frame,
            text=f"{date_str} | {time_str}",
            font=("TkDefaultFont", 10)
        )
        date_label.pack(anchor="center", pady=10)
        
        # Placeholder message
        message_label = ttk.Label(
            welcome_frame,
            text="This is a simple dashboard. More features will be added soon.",
            font=("TkDefaultFont", 12),
            foreground="gray"
        )
        message_label.pack(anchor="center", pady=20)
        
        # Bottom section with logout button
        bottom_frame = ttk.Frame(self)
        bottom_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        
        # Center the logout button
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=0)
        bottom_frame.columnconfigure(2, weight=1)
        
        # Logout button
        logout_btn = ttk.Button(
            bottom_frame, 
            text="Logout",
            command=self.handle_logout,
            bootstyle="danger",
            width=15
        )
        logout_btn.grid(row=0, column=1, pady=10)
        
    def handle_logout(self):
        """Handle logout button click"""
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            # Clear user data
            self.controller.user_data = None
            
            # Navigate back to login screen
            self.controller.show_login()