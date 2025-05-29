import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

class LoginOTPDialog(ctk.CTkToplevel):
    def __init__(self, parent, db_manager=None, email="", on_success=None):
        super().__init__(parent)
        
        self.db_manager = db_manager
        self.email = email
        self.on_success = on_success
        self.resend_timer_id = None  # Track timer for cleanup
        
        # Configure dialog - INCREASED HEIGHT
        self.title("Login Verification")
        self.geometry("520x500")  # Increased from 500x450
        self.resizable(False, False)
        self.configure(fg_color="#f5f5f5")
        
        # Make dialog modal
        self.grab_set()
        self.transient(parent)
        
        # Center dialog
        self.center_dialog()
        
        # Initialize variables
        self.otp_var = tk.StringVar()
        
        # Create UI
        self.create_dialog_content()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Auto-send OTP on dialog open
        self.after(100, self.send_login_otp)
    
    def center_dialog(self):
        """Center the dialog on screen"""
        try:
            self.update_idletasks()
            x = (self.winfo_screenwidth() - 520) // 2  # Updated for new width
            y = (self.winfo_screenheight() - 500) // 2  # Updated for new height
            self.geometry(f"520x500+{x}+{y}")
        except Exception as e:
            print(f"Error centering dialog: {e}")
            self.geometry("520x500+100+100")
    
    def create_dialog_content(self):
        """Create the dialog content"""
        # Main container with padding
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=15, pady=15)  # Reduced padding
        
        # Main card
        self.card = ctk.CTkFrame(
            main_container,
            corner_radius=12,
            fg_color="#ffffff",
            border_width=1,
            border_color="#d1d1d1"
        )
        self.card.pack(fill="both", expand=True)
        
        # Header - REDUCED HEIGHT
        header_frame = ctk.CTkFrame(self.card, fg_color="transparent", height=60)  # Reduced from 80
        header_frame.pack(fill="x", padx=25, pady=(20, 0))  # Reduced padding
        header_frame.pack_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Login Verification Required",
            font=ctk.CTkFont("Roboto", 18, "bold"),  # Reduced font size
            text_color="#1E3A8A"
        )
        title_label.pack(anchor="w")
        
        # Content frame - ALLOW EXPANSION
        content_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=25, pady=(5, 5))  # Reduced padding
        
        # Instructions
        instruction_label = ctk.CTkLabel(
            content_frame,
            text=f"For security purposes, we've sent a 6-digit verification code to:\n{self.email}",
            font=ctk.CTkFont("Roboto", 11),  # Reduced font size
            text_color="#707070",
            wraplength=400,
            justify="center"
        )
        instruction_label.pack(pady=(0, 15))  # Reduced padding
        
        # OTP label
        otp_label = ctk.CTkLabel(
            content_frame,
            text="Verification Code",
            font=ctk.CTkFont("Roboto", 12, "bold"),
            text_color="#333333"
        )
        otp_label.pack(pady=(0, 5))
        
        # OTP entry
        self.otp_entry = ctk.CTkEntry(
            content_frame,
            textvariable=self.otp_var,
            height=35,  # Reduced height
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 14, "bold"),  # Reduced font size
            fg_color="#ffffff",
            border_color="#d1d1d1",
            text_color="#000000",
            placeholder_text="Enter 6-digit code",
            justify="center",
            width=180  # Reduced width
        )
        self.otp_entry.pack(pady=(0, 10))  # Reduced padding
        
        # Status label for showing messages
        self.status_label = ctk.CTkLabel(
            content_frame,
            text="Sending verification code...",
            font=ctk.CTkFont("Roboto", 10),  # Reduced font size
            text_color="#10B981"
        )
        self.status_label.pack(pady=(0, 8))  # Reduced padding
        
        # Resend frame
        resend_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        resend_frame.pack(fill="x", pady=(0, 15))  # Reduced padding
        
        resend_text = ctk.CTkLabel(
            resend_frame,
            text="Didn't receive the code?",
            font=ctk.CTkFont("Roboto", 10),  # Reduced font size
            text_color="#707070"
        )
        resend_text.pack()
        
        self.resend_btn = ctk.CTkButton(
            resend_frame,
            text="Resend Code",
            font=ctk.CTkFont("Roboto", 10, "bold"),  # Reduced font size
            text_color="#1E3A8A",
            fg_color="transparent",
            hover_color="#f0f0f0",
            width=100,  # Reduced width
            height=22,  # Reduced height
            corner_radius=4,
            command=self.resend_otp,
            state="disabled"
        )
        self.resend_btn.pack(pady=(3, 0))  # Reduced padding
        
        # BUTTON FRAME - FIXED HEIGHT AND VISIBLE
        button_frame = ctk.CTkFrame(self.card, fg_color="#f8f9fa", height=70)  # Added background color to see it
        button_frame.pack(fill="x", padx=25, pady=(0, 20), side="bottom")  # Use side="bottom" to ensure it's at bottom
        button_frame.pack_propagate(False)
        
        # Button container
        button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
        button_container.pack(fill="x", pady=15)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_container,
            text="Cancel",
            width=90,  # Reduced width
            height=35,  # Reduced height
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 11),  # Reduced font size
            fg_color="transparent",
            text_color="#666666",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.on_closing
        )
        cancel_btn.pack(side="right", padx=(8, 0))
        
        # SUBMIT BUTTON - THIS IS THE MAIN SUBMIT BUTTON
        self.submit_btn = ctk.CTkButton(
            button_container,
            text="Verify & Login",
            width=120,  # Reduced width
            height=35,  # Reduced height
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 11, "bold"),  # Reduced font size
            fg_color="#1E3A8A",
            hover_color="#152a63",
            command=self.submit_otp
        )
        self.submit_btn.pack(side="right")
        
        # Focus on OTP entry
        self.otp_entry.focus()
        
        # Bind Enter key to submit
        self.otp_entry.bind("<Return>", lambda e: self.submit_otp())
    
    def send_login_otp(self):
        """Send login OTP to email"""
        try:
            if self.db_manager:
                success, message = self.db_manager.create_login_otp(self.email)
                
                if success:
                    self.status_label.configure(text="Verification code sent successfully!", text_color="#10B981")
                    self.start_resend_cooldown()
                else:
                    self.status_label.configure(text=f"Failed to send code: {message}", text_color="#dc2626")
                    messagebox.showerror("Error", message, parent=self)
                    self.resend_btn.configure(state="normal")  # Re-enable if failed
            else:
                messagebox.showerror("Error", "Database not available.", parent=self)
                self.resend_btn.configure(state="normal")  # Re-enable if failed
        
        except Exception as e:
            error_msg = f"Failed to send verification code: {str(e)}"
            self.status_label.configure(text=error_msg, text_color="#dc2626")
            messagebox.showerror("Error", error_msg, parent=self)
            self.resend_btn.configure(state="normal")  # Re-enable if failed
    
    def start_resend_cooldown(self):
        """Start the resend cooldown timer"""
        # Cancel any existing timer
        if self.resend_timer_id:
            self.after_cancel(self.resend_timer_id)
        
        # Disable resend button
        self.resend_btn.configure(state="disabled")
        
        # Start countdown
        self.update_resend_countdown(30)  # 30 second cooldown
    
    def update_resend_countdown(self, seconds_left):
        """Update the resend button with countdown"""
        if seconds_left > 0:
            self.resend_btn.configure(text=f"Resend Code ({seconds_left}s)")
            self.resend_timer_id = self.after(1000, lambda: self.update_resend_countdown(seconds_left - 1))
        else:
            # Cooldown finished, re-enable button
            try:
                self.resend_btn.configure(state="normal", text="Resend Code")
                self.resend_timer_id = None
            except tk.TclError:
                pass  # Widget was destroyed
    
    def resend_otp(self):
        """Resend OTP"""
        self.resend_btn.configure(state="disabled", text="Sending...")
        self.status_label.configure(text="Resending verification code...", text_color="#10B981")
        
        # Clear the OTP entry when resending
        self.otp_var.set("")
        
        # Send OTP after a short delay to show the status update
        self.after(500, self.send_login_otp)
    
    def submit_otp(self):
        """Submit and verify the OTP code - THIS IS THE SUBMIT FUNCTION"""
        otp = self.otp_var.get().strip()
        
        # Validate OTP
        if not otp:
            messagebox.showerror("Error", "Please enter the verification code.", parent=self)
            self.otp_entry.focus()
            return
        
        if len(otp) != 6 or not otp.isdigit():
            messagebox.showerror("Error", "Please enter a valid 6-digit verification code.", parent=self)
            self.otp_entry.focus()
            return
        
        # Show loading state
        self.submit_btn.configure(state="disabled", text="Verifying...")
        self.configure(cursor="wait")
        self.update_idletasks()
        
        try:
            # Verify OTP via database manager
            if self.db_manager:
                success, result = self.db_manager.verify_login_otp(self.email, otp)
                
                if success:
                    # Success - close dialog first, then call success callback
                    try:
                        self.configure(cursor="")
                    except tk.TclError:
                        pass
                    
                    # Store the callback and result before destroying
                    success_callback = self.on_success
                    user_data = result
                    
                    # Destroy the dialog
                    self.destroy()
                    
                    # Call the success callback after dialog is destroyed
                    if success_callback:
                        success_callback(user_data)
                    
                    return  # Exit the method since dialog is destroyed
                else:
                    messagebox.showerror("Verification Failed", result, parent=self)
                    self.submit_btn.configure(state="normal", text="Verify & Login")
                    self.otp_entry.focus()
            else:
                messagebox.showerror("Error", "Database not available.", parent=self)
                self.submit_btn.configure(state="normal", text="Verify & Login")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to verify code: {str(e)}", parent=self)
            self.submit_btn.configure(state="normal", text="Verify & Login")
        
        finally:
            try:
                self.configure(cursor="")
            except tk.TclError:
                pass  # Window was destroyed
    
    def on_closing(self):
        """Handle dialog closing"""
        # Cancel any active timer
        if self.resend_timer_id:
            self.after_cancel(self.resend_timer_id)
        self.destroy()
