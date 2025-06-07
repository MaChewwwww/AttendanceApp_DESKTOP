import customtkinter as ctk
import tkinter as tk
import winsound  # For Windows system sounds

class CautionModal(ctk.CTkToplevel):
    def __init__(self, parent, on_continue=None):
        super().__init__(parent)
        self.title("Caution")
        self.geometry("340x210")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.on_continue = on_continue
        self._is_destroyed = False
        
        # Use simple centering like other modals
        self._center_window(340, 210)
        self.setup_ui()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # Card frame for rounded corners, responsive
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=16)
        card.pack(expand=True, fill="both", padx=16, pady=16)
        card.pack_propagate(True)
        
        # Draw yellow circle with exclamation mark
        canvas = tk.Canvas(card, width=56, height=56, bg="#fff", highlightthickness=0)
        canvas.create_oval(4, 4, 52, 52, outline="#FBBF24", width=3)
        canvas.create_text(28, 28, text="!", font=("Segoe UI", 28, "bold"), fill="#FBBF24")
        canvas.pack(pady=(8, 0))
        
        # Title
        ctk.CTkLabel(card, text="Caution", font=ctk.CTkFont(size=16, weight="bold"), text_color="#222", fg_color="#fff").pack(pady=(4, 0))
        
        # Subtitle
        ctk.CTkLabel(card, text="Do you want to make changes to this?", font=ctk.CTkFont(size=13), text_color="#888", fg_color="#fff").pack(pady=(0, 8))
        
        # Buttons
        btns_frame = ctk.CTkFrame(card, fg_color="#fff")
        btns_frame.pack(side="bottom", fill="x", pady=(0, 16), padx=0)
        
        ctk.CTkButton(
            btns_frame,
            text="Cancel",
            fg_color="#D1D5DB",
            text_color="#444",
            hover_color="#BDBDBD",
            height=38,
            corner_radius=8,
            command=self._on_close
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))
        
        ctk.CTkButton(
            btns_frame,
            text="Continue",
            fg_color="#FBBF24",
            text_color="#fff",
            hover_color="#f59e1b",
            height=38,
            corner_radius=8,
            command=self._handle_continue
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

    def _handle_continue(self):
        if not self._is_destroyed:
            try:
                if self.on_continue:
                    self.on_continue()
            except Exception as e:
                print(f"Error in continue handler: {e}")
            finally:
                self._on_close()

    def _on_close(self):
        if not self._is_destroyed:
            self._is_destroyed = True
            try:
                self.grab_release()
            except:
                pass
            try:
                self.destroy()
            except:
                pass

class DeleteModal(ctk.CTkToplevel):
    def __init__(self, parent, on_delete=None):
        super().__init__(parent)
        self.on_delete_callback = on_delete
        self.title("Delete Confirmation")
        self.geometry("340x210")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self._center_window(340, 210)
        self.setup_ui()

    def _center_window(self, width, height):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # Card frame for rounded corners
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=16)
        card.pack(expand=True, fill="both", padx=16, pady=16)
        
        # Draw red circle with X mark
        canvas = tk.Canvas(card, width=56, height=56, bg="#fff", highlightthickness=0)
        canvas.create_oval(4, 4, 52, 52, outline="#EF4444", width=3)
        canvas.create_line(18, 18, 38, 38, fill="#EF4444", width=4)
        canvas.create_line(38, 18, 18, 38, fill="#EF4444", width=4)
        canvas.pack(pady=(8, 0))
        
        # Title
        ctk.CTkLabel(card, text="Delete Item", font=ctk.CTkFont(size=16, weight="bold"), text_color="#222").pack(pady=(4, 0))
        
        # Subtitle
        ctk.CTkLabel(card, text="Are you sure you want to delete this item?", font=ctk.CTkFont(size=13), text_color="#888").pack(pady=(0, 8))
        
        # Buttons
        btns_frame = ctk.CTkFrame(card, fg_color="#fff")
        btns_frame.pack(side="bottom", fill="x", pady=(0, 16))
        
        ctk.CTkButton(
            btns_frame,
            text="Cancel",
            fg_color="#D1D5DB",
            text_color="#444",
            hover_color="#BDBDBD",
            height=38,
            corner_radius=8,
            command=self.safe_destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))
        
        ctk.CTkButton(
            btns_frame,
            text="Delete",
            fg_color="#EF4444",
            text_color="#fff",
            hover_color="#DC2626",
            height=38,
            corner_radius=8,
            command=self.confirm_delete
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

    def safe_destroy(self):
        """Safely destroy the modal"""
        try:
            self.grab_release()
            self.destroy()
        except Exception as e:
            print(f"Error destroying delete modal: {e}")

    def confirm_delete(self):
        """Confirm deletion and execute callback"""
        try:
            # Release grab and destroy modal first
            self.grab_release()
            
            # Execute the delete callback if provided
            if self.on_delete_callback:
                self.on_delete_callback()
            
            # Destroy the modal
            self.destroy()
            
        except Exception as e:
            print(f"Error in confirm_delete: {e}")
            # Ensure modal is destroyed even if callback fails
            try:
                self.destroy()
            except:
                pass

class SuccessModal(ctk.CTkToplevel):
    def __init__(self, parent, on_continue=None):
        super().__init__(parent)
        self.title("Success")
        self.geometry("340x210")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.on_continue = on_continue
        self._is_destroyed = False
        
        # Play success sound
        self.play_success_sound()
        
        # Bind close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Use the same centering approach as other modals
        self._center_window(340, 210)
        
        self.setup_ui()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def play_success_sound(self):
        """Play a success sound notification"""
        try:
            # Use Windows system sound for success/information
            winsound.MessageBeep(winsound.MB_OK)
        except Exception as e:
            print(f"Could not play sound: {e}")
            # Fallback: try system bell
            try:
                self.bell()
            except:
                pass  # Silent fallback if no sound is available

    def setup_ui(self):
        # Card frame for rounded corners, responsive and matching other modals
        card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=16)
        card.pack(expand=True, fill="both", padx=16, pady=16)
        card.pack_propagate(True)
        
        # Draw green circle with checkmark
        canvas = tk.Canvas(card, width=56, height=56, bg="#fff", highlightthickness=0)
        canvas.create_oval(4, 4, 52, 52, outline="#22C55E", width=3)
        # Draw checkmark
        canvas.create_line(18, 32, 27, 42, 40, 18, fill="#22C55E", width=4, capstyle=tk.ROUND, joinstyle=tk.ROUND)
        canvas.pack(pady=(8, 0))
        
        # Title
        ctk.CTkLabel(card, text="Success!", font=ctk.CTkFont(size=16, weight="bold"), text_color="#222", fg_color="#fff").pack(pady=(4, 0))
        # Subtitle
        ctk.CTkLabel(card, text="Action is done successfully.", font=ctk.CTkFont(size=13), text_color="#888", fg_color="#fff").pack(pady=(0, 8))
        # Responsive Continue button (full width, bottom, fixed height)
        btns_frame = ctk.CTkFrame(card, fg_color="#fff", height=38)
        btns_frame.pack(side="bottom", fill="x", pady=(0, 16), padx=0)
        btns_frame.pack_propagate(False)
        ctk.CTkButton(
            btns_frame,
            text="Continue",
            fg_color="#22C55E",
            text_color="#fff",
            hover_color="#16a34a",
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8,
            command=self._handle_continue
        ).pack(expand=True, fill="both", padx=0)

    def _on_close(self):
        if not self._is_destroyed:
            self._is_destroyed = True
            try:
                self.grab_release()
            except:
                pass
            try:
                self.destroy()
            except:
                pass

    def _handle_continue(self):
        if not self._is_destroyed:
            try:
                if self.on_continue:
                    self.on_continue()
            except Exception as e:
                print(f"Error in continue handler: {e}")
            finally:
                self._on_close()