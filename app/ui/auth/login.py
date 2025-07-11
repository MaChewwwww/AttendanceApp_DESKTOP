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
    def __init__(self, master, db_manager=None, on_login_success=None, on_admin_login=None):
        super().__init__(master, fg_color="transparent")
        
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        self.on_admin_login = on_admin_login  # New callback for admin login
        
        # Path for storing remembered credentials
        self.credentials_file = os.path.join(ROOT_DIR, "data", "remembered_credentials.json")
        
        # Initialize variables
        self.email_var = tk.StringVar()
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
        # Create main container frame (single panel, full width)
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(expand=True, fill="both")
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # --- Login card (now full width) ---
        container = ctk.CTkFrame(main_container, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)

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
            font=ctk.CTkFont("Inter", 24, "bold"),
            text_color="#000000"
        ).pack(pady=(0, 2))
        
        # Student label
        ctk.CTkLabel(
            padding_frame,
            text="Admin",
            font=ctk.CTkFont("Inter", 24, "bold"),
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
            font=ctk.CTkFont("Source Sans 3", 12),
            text_color="#707070"
        ).pack(anchor="w", padx=17, pady=(0, 3))
        
        email_entry = ctk.CTkEntry(
            padding_frame,
            textvariable=self.email_var,
            width=420,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Source Sans 3", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000"
        )
        email_entry.pack(padx=17, pady=(0, 10))
        
        # Password
        ctk.CTkLabel(
            padding_frame,
            text="Password",
            font=ctk.CTkFont("Source Sans 3", 12),
            text_color="#707070"
        ).pack(anchor="w", padx=17, pady=(0, 3))
        
        password_entry = ctk.CTkEntry(
            padding_frame,
            textvariable=self.password,
            width=420,
            height=27,
            corner_radius=8,
            font=ctk.CTkFont("Source Sans 3", 12),
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
            font=ctk.CTkFont("Source Sans 3", 12),
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
            font=ctk.CTkFont("Source Sans 3", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#1E3A8A",
            command=self.handle_login
        )
        signin_button.pack(pady=(0, 8))
        
        # Forgot password link
        forgot_password = tk.Label(
            padding_frame,
            text="I forgot password",
            font=("Source Sans 3", 10, "underline"),
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
            # Check if user is admin - admins don't need OTP verification
            user_role = user_data.get('role', '').lower()
            
            if user_role == 'admin':
                # Admin users skip OTP verification and go directly to admin dashboard
                self.handle_successful_login(user_data)
                return
            
            # For students, check OTP requirement
            if self.db_manager:
                # Check if user has recent valid OTP verification
                needs_otp = self.db_manager.check_otp_requirement(user_data['user_id'])
                
                if needs_otp:
                    # Show OTP dialog
                    self.show_otp_dialog(email, user_data)
                else:
                    # OTP still valid, proceed with login
                    self.handle_successful_login(user_data)
            else:
                messagebox.showerror("Error", "Database not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check OTP requirement: {str(e)}")
    
    def handle_successful_login(self, user_data):
        """Handle successful login based on user role"""
        try:
            user_role = user_data.get('role', '').lower()
            
            if user_role == 'admin':
                # Redirect to admin dashboard
                if self.on_admin_login:
                    self.on_admin_login(user_data)
                else:
                    # Fallback: import and show admin dashboard directly
                    try:
                        # Import the admin dashboard
                        import sys
                        import os
                        
                        # Add the admin directory to Python path
                        admin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'admin')
                        if admin_dir not in sys.path:
                            sys.path.insert(0, admin_dir)
                        
                        # Import and create admin dashboard
                        from admindashboard import AdminDashboard
                        
                        # Get reference to main app for logout callback
                        root_window = self.winfo_toplevel()
                        main_app = getattr(root_window, 'main_app', None)
                        
                        # Close current window
                        root_window.withdraw()
                        
                        # Open admin dashboard with logout callback
                        def admin_logout():
                            try:
                                if main_app and hasattr(main_app, 'show_initial_screen'):
                                    main_app.show_initial_screen()
                                    # Show the main window again
                                    root_window.deiconify()
                            except Exception as e:
                                print(f"Error during admin logout: {e}")
                        
                        # Use after_idle to ensure proper cleanup
                        def create_admin_dashboard():
                            try:
                                admin_app = AdminDashboard(root_window, on_logout=admin_logout)
                                admin_app.protocol("WM_DELETE_WINDOW", admin_app.logout)
                                # Do NOT call mainloop on a Toplevel window
                                # admin_app.mainloop()
                                # Clean up - remove from path
                                if admin_dir in sys.path:
                                    sys.path.remove(admin_dir)
                            except Exception as e:
                                print(f"Admin dashboard error: {e}")
                                # If admin dashboard fails, show main window again
                                try:
                                    root_window.deiconify()
                                except:
                                    pass
                                # Clean up - remove from path
                                if admin_dir in sys.path:
                                    sys.path.remove(admin_dir)
                        
                        # Minimal delay, just enough to hide the main window
                        root_window.after(50, create_admin_dashboard)
                        
                    except Exception as e:
                        messagebox.showerror("Error", f"Could not load admin dashboard: {str(e)}")
                        print(f"Admin dashboard error: {e}")
                        
            elif user_role == 'student':
                # Regular student login
                if self.on_login_success:
                    self.on_login_success(user_data)
            else:
                messagebox.showerror("Error", f"Unknown user role: {user_role}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to handle login: {str(e)}")
            print(f"Login handling error: {e}")
    
    def show_otp_dialog(self, email, user_data):
        """Show the OTP verification dialog"""
        try:
            root_window = self.winfo_toplevel()
            dialog = LoginOTPDialog(
                root_window, 
                self.db_manager, 
                email=email,
                user_data=user_data,  # Pass user data to OTP dialog
                on_success=self.handle_successful_login  # Use the new handler
            )
            dialog.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open OTP dialog: {str(e)}")