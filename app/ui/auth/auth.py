import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from .login import LoginForm
from .register import RegisterForm

class LoginRegister(ctk.CTkFrame):
    def __init__(self, parent, db_manager=None, on_back_click=None, on_login_success=None):
        super().__init__(parent, fg_color="transparent")
        
        self.db_manager = db_manager
        self.on_back_click = on_back_click
        self.on_login_success = on_login_success

        # Main container with blue background
        self.main_container = ctk.CTkFrame(self, fg_color="#1E3A8A")
        self.main_container.pack(fill="both", expand=True)

        # Right panel with blue background
        self.right_panel = ctk.CTkFrame(
            self.main_container,
            fg_color="#1E3A8A",
            corner_radius=0
        )
        self.right_panel.pack(fill="both", expand=True)

        # --- Back button in transparent container, top left ---
        self.back_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.back_container.place(relx=0.0, rely=0.0, anchor="nw", x=20, y=20)  # 20px padding from top/left

        self.back_button = ctk.CTkButton(
            self.back_container,
            text="← Back",
            command=self.handle_back,
            fg_color="transparent",
            hover_color="#2563eb",
            text_color="#fff",
            width=80,
            height=32,
            corner_radius=8,
            border_width=1,
            border_color="#fff"
        )
        self.back_button.pack()

        # Central container for forms (centered vertically and horizontally)
        self.form_container = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.form_container.place(relx=0.5, rely=0.5, anchor="center")

        # Initialize forms
        self.login_form = LoginForm(self.form_container, self.db_manager, on_login_success=self.on_login_success)
        self.register_form = RegisterForm(self.form_container, self.db_manager, on_success=self.on_registration_success)

        # Show login form by default
        self.show_login()

    def handle_back(self):
        if self.on_back_click:
            self.on_back_click()

    def show_login(self):
        """Show the login form"""
        self.register_form.pack_forget()
        self.login_form.pack(fill="both", expand=True)

    def show_register(self):
        """Show the registration form"""
        self.login_form.pack_forget()
        self.register_form.pack(fill="both", expand=True)

    def on_registration_success(self, email):
        """Handle successful registration - auto-login flow"""
        self.show_login()
        if hasattr(self.login_form, 'email_var'):
            self.login_form.email_var.set(email)