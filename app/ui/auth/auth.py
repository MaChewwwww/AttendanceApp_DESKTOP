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
        self.left_panel.pack_propagate(False)
        
        # Add back link
        back_link = ctk.CTkLabel(
            self.left_panel,
            text="← Back",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#ffffff",
            cursor="hand2"
        )
        back_link.place(x=20, y=20)
        back_link.bind("<Button-1>", lambda e: self.on_back_click() if self.on_back_click else None)
        
        # Create right panel (forms)
        self.right_panel = ctk.CTkFrame(
            self.main_container,
            fg_color="#f5f5f5",
            corner_radius=0
        )
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Initialize forms
        self.login_form = LoginForm(self.right_panel, self.db_manager, on_login_success=self.on_login_success)
        self.register_form = RegisterForm(self.right_panel, self.db_manager, on_success=self.on_registration_success)
        
        # Show login form by default
        self.show_login()
        
    def show_login(self):
        """Show the login form"""
        self.register_form.pack_forget()
        self.login_form.pack(fill="both", expand=True)
        
    def show_register(self):
        """Show the registration form"""
        self.login_form.pack_forget()
        self.register_form.pack(fill="both", expand=True)
        
    def on_registration_success(self, email):
        """Handle successful registration"""
        self.show_login()
        # Pre-fill email if needed
        if hasattr(self.login_form, 'email_var'):
            self.login_form.email_var.set(email)
        
        # Show success message
        messagebox.showinfo(
            "Registration Successful", 
            f"Account registered successfully!\n\n" +
            f"Your account is now pending admin approval. You will be notified via email when your account is activated.\n\n" +
            f"This process typically takes 1-3 business days.\n\n" +
            f"Email: {email}",
            parent=self
        )