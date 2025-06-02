import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
from PIL import Image, ImageTk, ImageOps

class UsersDeleteModal(ctk.CTkToplevel):
    def __init__(self, parent, user_data, user_type="student"):
        super().__init__(parent)
        self.user_data = user_data
        self.user_type = user_type
        self.title(f"Delete User")
        # Responsive Modern Delete Modal
        self.geometry("340x210")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
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
        
        # Circle + Trash icon (centered)
        icon_dir = os.path.join(os.path.dirname(__file__), '../../../assets/icons')
        circle_path = os.path.join(icon_dir, 'circle.png')
        trash_path = os.path.join(icon_dir, 'trash-2.png')
        
        try:
            circle_img = Image.open(circle_path).convert('RGBA').resize((56, 56))
            r, g, b = (248, 113, 113)
            tint = Image.new('RGBA', circle_img.size, (r, g, b, 255))
            circle_img = Image.blend(circle_img, tint, 0.5)
            trash_img = Image.open(trash_path).convert('RGBA').resize((32, 32))
            combined = circle_img.copy()
            combined.paste(trash_img, ((56-32)//2, (56-32)//2), trash_img)
            icon = ImageTk.PhotoImage(combined)
            icon_label = tk.Label(card, image=icon, bg="#fff")
            icon_label.image = icon
            icon_label.pack(pady=(8, 0))
        except Exception:
            icon_label = ctk.CTkLabel(card, text="\U0001F5D1", font=ctk.CTkFont(size=40), text_color="#F87171", fg_color="#fff")
            icon_label.pack(pady=(8, 0))
        
        # Title
        ctk.CTkLabel(card, text="Delete", font=ctk.CTkFont(size=16, weight="bold"), text_color="#222", fg_color="#fff").pack(pady=(4, 0))
        
        # Subtitle
        ctk.CTkLabel(card, text="Are you sure you want to delete?", font=ctk.CTkFont(size=13), text_color="#888", fg_color="#fff").pack(pady=(0, 8))
        
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
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))
        
        ctk.CTkButton(
            btns_frame,
            text="Delete",
            fg_color="#F87171",
            text_color="#fff",
            hover_color="#ef4444",
            height=38,
            corner_radius=8,
            command=self.show_success_modal
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

    def show_success_modal(self):
        """Show success modal after deletion"""
        from .users_modals import SuccessModal
        SuccessModal(self)
