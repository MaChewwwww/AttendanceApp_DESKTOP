import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os
import base64
from datetime import datetime
from ...config import ROOT_DIR
from .forgot_password import ForgotPasswordDialog
from .login_otp import LoginOTPDialog

class LoginForm(ctk.CTkFrame):
    def __init__(self, master, db_manager=None, on_login_success=None):
        super().__init__(master, fg_color="transparent")
        
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        
        # Path for storing remembered credentials
        self.credentials_file = os.path.join(ROOT_DIR, "data", "remembered_credentials.json")
        
        # Initialize variables
        self.email_var = tk.StringVar()  # Changed from student_number to email
        self.password = tk.StringVar()
        self.remember_me = tk.BooleanVar()
        
        # Load remembered credentials if they exist
        self._load_remembered_credentials()
        
        # Create the login form
        self._create_login_form()
        
    def _encode_password(self, password):
        """Simple encoding for password storage (not encryption, just obfuscation)"""
        return base64.b64encode(password.encode()).decode()
    
    def _decode_password(self, encoded_password):
        """Decode the stored password"""
        try:
            return base64.b64decode(encoded_password.encode()).decode()
        except:
            return ""
        
    def _load_remembered_credentials(self):
        """Load saved credentials if remember me was checked"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    data = json.load(f)
                    
                if data.get('remember_me', False):
                    self.email_var.set(data.get('email', ''))
                    # Load and decode password
                    encoded_password = data.get('password', '')
                    if encoded_password:
                        self.password.set(self._decode_password(encoded_password))
                    self.remember_me.set(True)
                    
        except Exception as e:
            print(f"Error loading remembered credentials: {e}")
    
    def _save_remembered_credentials(self):
        """Save credentials if remember me is checked"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
            
            data = {
                'remember_me': self.remember_me.get(),
                'email': self.email_var.get() if self.remember_me.get() else '',
                'password': self._encode_password(self.password.get()) if self.remember_me.get() else '',
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving remembered credentials: {e}")
    
    def _clear_remembered_credentials(self):
        """Clear saved credentials"""
        try:
            if os.path.exists(self.credentials_file):
                os.remove(self.credentials_file)
        except Exception as e:
            print(f"Error clearing remembered credentials: {e}")

    def _create_login_form(self):
        # Create container frame
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create card frame
        card = ctk.CTkFrame(
            container,
            fg_color="#ffffff",
            corner_radius=15,
            width=454,
            height=353,
            border_width=1,
            border_color="#d1d1d1"
        )
        card.pack(padx=20, pady=20)
        card.pack_propagate(False)
        
        # Create padding frame
        padding_frame = ctk.CTkFrame(card, fg_color="transparent")
        padding_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        ctk.CTkLabel(
            padding_frame,
            text="Sign in as",
            font=ctk.CTkFont("Roboto", 24, "bold"),
            text_color="#000000"
        ).pack(pady=(0, 2))
        
        # Student label
        ctk.CTkLabel(
            padding_frame,
            text="Student",
            font=ctk.CTkFont("Roboto", 24, "bold"),
            text_color="#1E3A8A"
        ).pack(pady=(0, 5))
        
        # Divider
        divider_container = ctk.CTkFrame(padding_frame, fg_color="transparent", height=2)
        divider_container.pack(fill="x", pady=(0, 15))
        divider_container.pack_propagate(False)
        
        divider = ctk.CTkFrame(
            divider_container,
            fg_color="#1E3A8A",
            width=50,
            height=2
        )
        divider.place(relx=0.5, rely=0.5, anchor="center")
        
        # Email (changed from Student Number)
        ctk.CTkLabel(
            padding_frame,
            text="Email Address",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w", padx=17, pady=(0, 3))
        
        email_entry = ctk.CTkEntry(
            padding_frame,
            textvariable=self.email_var,
            width=420,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000"
        )
        email_entry.pack(padx=17, pady=(0, 10))
        
        # Password
        ctk.CTkLabel(
            padding_frame,
            text="Password",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070"
        ).pack(anchor="w", padx=17, pady=(0, 3))
        
        password_entry = ctk.CTkEntry(
            padding_frame,
            textvariable=self.password,
            width=420,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•"
        )
        password_entry.pack(padx=17, pady=(0, 10))
        
        # Remember me checkbox
        checkbox_frame = ctk.CTkFrame(padding_frame, fg_color="transparent")
        checkbox_frame.pack(fill="x", padx=17, pady=(0, 15))
        
        remember_checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Remember me",
            variable=self.remember_me,
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070",
            checkbox_width=15,
            checkbox_height=15,
            corner_radius=4,
            border_width=1,
            fg_color="#1E3A8A",
            hover_color="#1E3A8A"
        )
        remember_checkbox.pack(side="left")
        
        # Sign in button
        signin_button = ctk.CTkButton(
            padding_frame,
            text="Sign in",
            width=120,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#1E3A8A",
            command=self.handle_login
        )
        signin_button.pack(pady=(0, 8))
        
        # Forgot password link
        forgot_password = tk.Label(
            padding_frame,
            text="I forgot password",
            font=("Roboto", 10, "underline"),
            fg="#F87171",
            cursor="hand2",
            bg="#ffffff"
        )
        forgot_password.pack()
        forgot_password.bind("<Button-1>", lambda e: self.open_forgot_password_dialog())
    
    def open_forgot_password_dialog(self):
        """Open the forgot password dialog"""
        try:
            root_window = self.winfo_toplevel()
            dialog = ForgotPasswordDialog(root_window, self.db_manager)
            dialog.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open forgot password dialog: {str(e)}")

    def handle_login(self):
        """Handle login button click"""
        email = self.email_var.get().strip()
        password = self.password.get().strip()
        
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        # PUP email validation
        if not email.endswith("@iskolarngbayan.pup.edu.ph"):
            messagebox.showerror("Error", "Please enter a valid PUP email address ending with @iskolarngbayan.pup.edu.ph")
            return
        
        # Save or clear remembered credentials based on checkbox
        if self.remember_me.get():
            self._save_remembered_credentials()
        else:
            self._clear_remembered_credentials()
            
        # Implement actual login logic with database
        if self.db_manager:
            success, result = self.db_manager.login(email, password)
            if success:
                # Check if OTP verification is needed
                self.check_otp_requirement(email, result)
            else:
                messagebox.showerror("Login Failed", result)
        else:
            messagebox.showerror("Error", "Database not available")
    
    def check_otp_requirement(self, email, user_data):
        """Check if OTP verification is required or still valid"""
        try:
            if self.db_manager:
                # Check if user has recent valid OTP verification
                needs_otp = self.db_manager.check_otp_requirement(user_data['user_id'])
                
                if needs_otp:
                    # Show OTP dialog
                    self.show_otp_dialog(email, user_data)
                else:
                    # OTP still valid, proceed with login
                    if self.on_login_success:
                        self.on_login_success(user_data)
            else:
                messagebox.showerror("Error", "Database not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check OTP requirement: {str(e)}")
    
    def show_otp_dialog(self, email, user_data):
        """Show the OTP verification dialog"""
        try:
            root_window = self.winfo_toplevel()
            dialog = LoginOTPDialog(
                root_window, 
                self.db_manager, 
                email=email,
                on_success=self.on_login_success
            )
            dialog.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open OTP dialog: {str(e)}")