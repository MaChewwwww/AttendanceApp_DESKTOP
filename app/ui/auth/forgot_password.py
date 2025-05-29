import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import re

class ForgotPasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, db_manager=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.step = 1  # 1: Email input, 2: OTP verification, 3: New password
        self.email = ""
        
        # Configure dialog
        self.title("Reset Password")
        self.geometry("500x450")
        self.resizable(False, False)
        self.configure(fg_color="#f5f5f5")
        
        # Make dialog modal
        self.grab_set()
        self.transient(parent)
        
        # Center dialog
        self.center_dialog()
        
        # Initialize variables
        self.email_var = tk.StringVar()
        self.otp_var = tk.StringVar()
        self.new_password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        
        # Create UI
        self.create_dialog_content()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_dialog(self):
        """Center the dialog on screen"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (250)  # Half of width (500/2)
        y = (self.winfo_screenheight() // 2) - (225)  # Half of height (450/2)
        self.geometry(f"500x450+{x}+{y}")
    
    def create_dialog_content(self):
        """Create the dialog content"""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Main card
        self.card = ctk.CTkFrame(
            main_container,
            corner_radius=12,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        self.card.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(self.card, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(30, 0))
        header_frame.pack_propagate(False)
        
        # Title
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Reset Password",
            font=ctk.CTkFont("Roboto", 24, "bold"),
            text_color="#1E3A8A"
        )
        self.title_label.pack(anchor="w")
        
        # Content frame (will change based on step)
        self.content_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(20, 20))
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self.card, fg_color="transparent", height=60)
        self.button_frame.pack(fill="x", padx=30, pady=(0, 30))
        self.button_frame.pack_propagate(False)
        
        # Show initial step
        self.show_step_1()
    
    def clear_content_frame(self):
        """Clear all widgets from content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_step_1(self):
        """Show email input step"""
        self.step = 1
        self.clear_content_frame()
        
        # Update title
        self.title_label.configure(text="Reset Password")
        
        # Instructions
        instruction_label = ctk.CTkLabel(
            self.content_frame,
            text="Enter your email address and we'll send you an OTP code to reset your password.",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070",
            wraplength=400,
            justify="left"
        )
        instruction_label.pack(anchor="w", pady=(0, 20))
        
        # Email label
        email_label = ctk.CTkLabel(
            self.content_frame,
            text="Email Address",
            font=ctk.CTkFont("Roboto", 12, "bold"),
            text_color="#333333"
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        # Email entry
        self.email_entry = ctk.CTkEntry(
            self.content_frame,
            textvariable=self.email_var,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            placeholder_text="Enter your email address"
        )
        self.email_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons
        self.create_step_1_buttons()
        
        # Focus on email entry
        self.email_entry.focus()

    def show_step_2(self):
        """Show OTP verification step"""
        self.step = 2
        self.clear_content_frame()
        
        # Update title
        self.title_label.configure(text="Verify OTP")
        
        # Instructions
        instruction_label = ctk.CTkLabel(
            self.content_frame,
            text=f"We've sent a 6-digit OTP code to {self.email}. Enter the code below:",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070",
            wraplength=400,
            justify="left"
        )
        instruction_label.pack(anchor="w", pady=(0, 20))
        
        # OTP label
        otp_label = ctk.CTkLabel(
            self.content_frame,
            text="OTP Code",
            font=ctk.CTkFont("Roboto", 12, "bold"),
            text_color="#333333"
        )
        otp_label.pack(anchor="w", pady=(0, 5))
        
        # OTP entry
        self.otp_entry = ctk.CTkEntry(
            self.content_frame,
            textvariable=self.otp_var,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 16, "bold"),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            placeholder_text="Enter 6-digit OTP code",
            justify="center"
        )
        self.otp_entry.pack(fill="x", pady=(0, 15))
        
        # Resend link
        resend_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        resend_frame.pack(fill="x", pady=(0, 20))
        
        resend_label = ctk.CTkLabel(
            resend_frame,
            text="Didn't receive the code? Resend OTP",
            font=ctk.CTkFont("Roboto", 11, "underline"),
            text_color="#1E3A8A",
            cursor="hand2"
        )
        resend_label.pack(anchor="w")
        resend_label.bind("<Button-1>", lambda e: self.resend_otp())
        
        # Buttons
        self.create_step_2_buttons()
        
        # Focus on OTP entry
        self.otp_entry.focus()

    def show_step_3(self):
        """Show new password step"""
        self.step = 3
        self.clear_content_frame()
        
        # Update title
        self.title_label.configure(text="New Password")
        
        # Instructions
        instruction_label = ctk.CTkLabel(
            self.content_frame,
            text="Enter your new password. Make sure it's strong and secure.",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#707070",
            wraplength=400,
            justify="left"
        )
        instruction_label.pack(anchor="w", pady=(0, 20))
        
        # New password label
        password_label = ctk.CTkLabel(
            self.content_frame,
            text="New Password",
            font=ctk.CTkFont("Roboto", 12, "bold"),
            text_color="#333333"
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        # New password entry
        self.new_password_entry = ctk.CTkEntry(
            self.content_frame,
            textvariable=self.new_password_var,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•",
            placeholder_text="Enter new password"
        )
        self.new_password_entry.pack(fill="x", pady=(0, 15))
        
        # Confirm password label
        confirm_label = ctk.CTkLabel(
            self.content_frame,
            text="Confirm Password",
            font=ctk.CTkFont("Roboto", 12, "bold"),
            text_color="#333333"
        )
        confirm_label.pack(anchor="w", pady=(0, 5))
        
        # Confirm password entry
        self.confirm_password_entry = ctk.CTkEntry(
            self.content_frame,
            textvariable=self.confirm_password_var,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            show="•",
            placeholder_text="Confirm new password"
        )
        self.confirm_password_entry.pack(fill="x", pady=(0, 15))
        
        # Password requirements
        requirements_frame = ctk.CTkFrame(self.content_frame, fg_color="#f8f9fa", corner_radius=8)
        requirements_frame.pack(fill="x", pady=(0, 20))
        
        requirements_text = """Password requirements:
• At least 6 characters long
• Contains uppercase and lowercase letters
• Contains at least one special character"""
        
        requirements_label = ctk.CTkLabel(
            requirements_frame,
            text=requirements_text,
            font=ctk.CTkFont("Roboto", 10),
            text_color="#666666",
            justify="left"
        )
        requirements_label.pack(anchor="w", padx=15, pady=10)
        
        # Buttons
        self.create_step_3_buttons()
        
        # Focus on password entry
        self.new_password_entry.focus()
    
    def create_step_1_buttons(self):
        """Create buttons for step 1"""
        # Clear button frame
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Button container
        button_container = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        button_container.pack(fill="x")
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_container,
            text="Cancel",
            width=120,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="transparent",
            text_color="#666666",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.on_closing
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # Send OTP button
        send_btn = ctk.CTkButton(
            button_container,
            text="Send OTP",
            width=120,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.send_otp
        )
        send_btn.pack(side="right")

    def create_step_2_buttons(self):
        """Create buttons for step 2"""
        # Clear button frame
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Button container
        button_container = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        button_container.pack(fill="x")
        
        # Back button
        back_btn = ctk.CTkButton(
            button_container,
            text="← Back",
            width=80,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="transparent",
            text_color="#666666",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.show_step_1
        )
        back_btn.pack(side="left")
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_container,
            text="Cancel",
            width=120,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="transparent",
            text_color="#666666",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.on_closing
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # Verify button
        verify_btn = ctk.CTkButton(
            button_container,
            text="Verify",
            width=120,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.verify_otp
        )
        verify_btn.pack(side="right")

    def create_step_3_buttons(self):
        """Create buttons for step 3"""
        # Clear button frame
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Button container
        button_container = ctk.CTkFrame(self.button_frame, fg_color="transparent")
        button_container.pack(fill="x")
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_container,
            text="Cancel",
            width=120,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12),
            fg_color="transparent",
            text_color="#666666",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.on_closing
        )
        cancel_btn.pack(side="right", padx=(10, 0))
        
        # Reset Password button
        reset_btn = ctk.CTkButton(
            button_container,
            text="Reset Password",
            width=140,
            height=40,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 12, "bold"),
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.reset_password
        )
        reset_btn.pack(side="right")

    def send_otp(self):
        """Send OTP to email"""
        email = self.email_var.get().strip()
        
        # Validate email
        if not email:
            messagebox.showerror("Error", "Please enter your email address.", parent=self)
            return
        
        # Remove the PUP email validation for now to allow any email for testing
        # if not email.endswith("@iskolarngbayan.pup.edu.ph"):
        #     messagebox.showerror("Error", "Please enter a valid PUP email address.", parent=self)
        #     return
        
        # Basic email validation
        if '@' not in email or '.' not in email.split('@')[-1]:
            messagebox.showerror("Error", "Please enter a valid email address.", parent=self)
            return
        
        # Show loading cursor
        self.configure(cursor="wait")
        self.update_idletasks()
        
        try:
            # Send OTP via database manager
            if self.db_manager:
                success, message = self.db_manager.create_password_reset_otp(email)
                
                if success:
                    self.email = email
                    messagebox.showinfo("OTP Sent", message, parent=self)
                    self.show_step_2()
                else:
                    messagebox.showerror("Error", message, parent=self)
            else:
                messagebox.showerror("Error", "Database not available.", parent=self)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP: {str(e)}", parent=self)
        
        finally:
            self.configure(cursor="")
    
    def resend_otp(self):
        """Resend OTP"""
        self.send_otp()
    
    def verify_otp(self):
        """Verify the OTP code"""
        otp = self.otp_var.get().strip()
        
        # Validate OTP
        if not otp:
            messagebox.showerror("Error", "Please enter the OTP code.", parent=self)
            return
        
        if len(otp) != 6 or not otp.isdigit():
            messagebox.showerror("Error", "Please enter a valid 6-digit OTP code.", parent=self)
            return
        
        # Show loading cursor
        self.configure(cursor="wait")
        self.update_idletasks()
        
        try:
            # Verify OTP via database manager
            if self.db_manager:
                success, result = self.db_manager.verify_password_reset_otp(self.email, otp)
                
                if success:
                    messagebox.showinfo("OTP Verified", "OTP verified successfully! Now enter your new password.", parent=self)
                    self.show_step_3()
                else:
                    messagebox.showerror("Error", result, parent=self)
            else:
                messagebox.showerror("Error", "Database not available.", parent=self)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to verify OTP: {str(e)}", parent=self)
        
        finally:
            self.configure(cursor="")
    
    def reset_password(self):
        """Reset the password"""
        new_password = self.new_password_var.get().strip()
        confirm_password = self.confirm_password_var.get().strip()
        otp = self.otp_var.get().strip()
        
        # Validate passwords
        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Please fill in both password fields.", parent=self)
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.", parent=self)
            return
        
        # Validate password strength
        errors = []
        if len(new_password) < 6:
            errors.append("• Password must be at least 6 characters long")
        if not re.search(r'[a-z]', new_password):
            errors.append("• Password must contain at least one lowercase letter")
        if not re.search(r'[A-Z]', new_password):
            errors.append("• Password must contain at least one uppercase letter")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
            errors.append("• Password must contain at least one special character")
        
        if errors:
            messagebox.showerror("Password Requirements", "\n".join(errors), parent=self)
            return
        
        # Show loading cursor
        self.configure(cursor="wait")
        self.update_idletasks()
        
        try:
            # Reset password via database manager
            if self.db_manager:
                success, message = self.db_manager.reset_password_with_otp(self.email, otp, new_password)
                
                if success:
                    messagebox.showinfo("Success", "Password reset successfully! You can now log in with your new password.", parent=self)
                    self.destroy()
                else:
                    messagebox.showerror("Error", message, parent=self)
            else:
                messagebox.showerror("Error", "Database not available.", parent=self)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset password: {str(e)}", parent=self)
        
        finally:
            self.configure(cursor="")
    
    def on_closing(self):
        """Handle dialog closing"""
        self.destroy()
