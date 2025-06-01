import customtkinter as ctk
import tkinter as tk
from app.ui.admin.components.sidebar import DateTimePill  # adjust path if needed
from app.db_manager import DatabaseManager

class FilterPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Filter Users")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Set background color to white
        self.configure(fg_color="#fff")
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        # Center the window
        self.update_idletasks()
        self._center_window(400, 500)
        
        self.setup_ui()
    
    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # Header
        ctk.CTkLabel(
            self,
            text="Filter Users",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Filter options
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Year filter
        ctk.CTkLabel(filter_frame, text="Year", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        year_var = tk.StringVar(value="All")
        year_options = ["All", "1st Year", "2nd Year", "3rd Year", "4th Year"]
        year_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=year_options,
            variable=year_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        year_menu.pack(fill="x", pady=(0, 15))
        
        # Section filter
        ctk.CTkLabel(filter_frame, text="Section", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        section_var = tk.StringVar(value="All")
        section_options = ["All", "1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
        section_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=section_options,
            variable=section_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        section_menu.pack(fill="x", pady=(0, 15))
        
        # Programs filter
        ctk.CTkLabel(filter_frame, text="Programs", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        programs_var = tk.StringVar(value="All")
        programs_options = ["All", "BSIT", "BSCS", "BSIS"]
        programs_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=programs_options,
            variable=programs_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        programs_menu.pack(fill="x", pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Apply Filters",
            command=self.apply_filters,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="white"
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Reset",
            command=self.reset_filters,
            fg_color="#F3F4F6",
            text_color="#222",
            hover_color="#E5E7EB"
        ).pack(side="right")
    
    def apply_filters(self):
        # TODO: Implement filter logic
        self.destroy()
    
    def reset_filters(self):
        # TODO: Implement reset logic
        self.destroy()

class ActionPopup(ctk.CTkToplevel):
    def __init__(self, parent, action, user_data):
        super().__init__(parent)
        self.title(f"{action} User")
        self.geometry("350x220")
        self.resizable(False, False)
        self.configure(fg_color="#fff")
        self.transient(parent)
        self.grab_set()
        self.action = action
        self.user_data = user_data
        self.update_idletasks()
        # Center for default, will re-center for other actions in setup_ui
        self._center_window(350, 220)
        self.setup_ui()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        action = self.action
        # Unpack user data
        name, year, section, program = self.user_data
        if action == "View":
            self.geometry("640x720")
            self.update_idletasks()
            self._center_window(640, 720)
            self.configure(fg_color="#F5F5F5")
            # Top frame for image, user info, and export button
            top_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
            top_frame.pack(fill="x", padx=20, pady=(20, 10))
            # Image placeholder
            image_canvas = tk.Canvas(top_frame, width=70, height=70, bg="#fff", highlightthickness=1, highlightbackground="#BDBDBD")
            image_canvas.create_rectangle(2, 2, 68, 68, fill="#E5E7EB", outline="#BDBDBD", width=2)
            image_canvas.pack(side="left", padx=(0, 16))
            # User info
            user_info_frame = ctk.CTkFrame(top_frame, fg_color="#F5F5F5")
            user_info_frame.pack(side="left", fill="y")
            ctk.CTkLabel(user_info_frame, text=name, font=ctk.CTkFont(size=18, weight="bold"), text_color="#000").pack(anchor="w")
            ctk.CTkLabel(user_info_frame, text=f"{program} {section}", font=ctk.CTkFont(size=14), text_color="#000").pack(anchor="w")
            # Export button
            export_btn = ctk.CTkButton(top_frame, text="Export", fg_color="#1E3A8A", hover_color="#1E3A8A", text_color="#fff", width=70, height=32, corner_radius=8)
            export_btn.pack(side="right", padx=(0, 0), pady=(0, 0))

            # --- Search and filter bar (copied from Users tab) ---
            search_bar_container = ctk.CTkFrame(self, fg_color="#F5F5F5")
            search_bar_container.pack(pady=(0, 10), padx=20, anchor="w")
            search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
            search_entry_frame.pack(side="left", pady=0, padx=0)
            search_entry_frame.pack_propagate(False)
            search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
            search_icon.pack(side="left", padx=(8, 0), pady=4)
            search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="", width=160, fg_color="#fff",
                                        border_color="#fff", border_width=0, text_color="#000", font=ctk.CTkFont(size=15), height=28)
            search_entry.pack(side="left", padx=(2, 8), pady=4)
            filter_btn = ctk.CTkButton(
                search_bar_container,
                text="Filters",
                width=80,
                height=36,
                fg_color="#1E3A8A",
                text_color="#fff",
                hover_color="#1E3A8A",
                border_width=1,
                border_color="#BDBDBD",
                corner_radius=0,
                font=ctk.CTkFont(size=13),
                command=lambda: FilterPopup(self)
            )
            filter_btn.pack(side="left", padx=0, pady=0)

            # Table
            table_frame = ctk.CTkFrame(self, fg_color="#fff", border_color="#E5E7EB", border_width=1, corner_radius=8)
            table_frame.pack(fill="both", expand=True, padx=20, pady=10)
            # Table columns
            columns = ["Course Subject", "Attendance", "Absent", "Rating"]
            for i, col in enumerate(columns):
                table_frame.grid_columnconfigure(i, weight=1)
                ctk.CTkLabel(
                    table_frame,
                    text=col,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color="#000",
                    anchor="w"
                ).grid(row=0, column=i, padx=10, pady=8, sticky="w")
            # Sample table data
            table_data = [
                ("Ethics 101", "1", "1", "100%") for _ in range(6)
            ]
            for idx, (subject, attendance, absent, rating) in enumerate(table_data, start=1):
                for col_idx, value in enumerate([subject, attendance, absent, rating]):
                    ctk.CTkLabel(
                        table_frame,
                        text=value,
                        font=ctk.CTkFont(size=13),
                        text_color="#000",
                        fg_color="#fff",
                        anchor="w"
                    ).grid(row=idx, column=col_idx, sticky="nsew", padx=10, pady=6)
        else:
            if action == "Edit":
                self.geometry("640x720")
                self.update_idletasks()
                self._center_window(640, 720)
                # Title
                ctk.CTkLabel(self, text="Edit Student Profile", font=ctk.CTkFont(size=18, weight="bold"), text_color="#000").pack(anchor="w", padx=30, pady=(20, 10))
                # Main form frame
                form_frame = ctk.CTkFrame(self, fg_color="#fff")
                form_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))
                # Two columns for entries
                left_col = ctk.CTkFrame(form_frame, fg_color="#fff")
                left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
                right_col = ctk.CTkFrame(form_frame, fg_color="#fff")
                right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
                form_frame.grid_columnconfigure(0, weight=1)
                form_frame.grid_columnconfigure(1, weight=1)
                # Left column entries
                ctk.CTkLabel(left_col, text="First Name", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
                ctk.CTkEntry(left_col, width=220, fg_color="#fff", text_color="#000").pack(fill="x", pady=(0, 10))
                ctk.CTkLabel(left_col, text="Last Name", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
                ctk.CTkEntry(left_col, width=220, fg_color="#fff", text_color="#000").pack(fill="x", pady=(0, 10))
                ctk.CTkLabel(left_col, text="Email", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
                ctk.CTkEntry(left_col, width=220, fg_color="#fff", text_color="#000").pack(fill="x", pady=(0, 10))
                ctk.CTkLabel(left_col, text="Password", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
                ctk.CTkEntry(left_col, width=220, show="*", fg_color="#fff", text_color="#000").pack(fill="x", pady=(0, 10))
                # Right column entries
                ctk.CTkLabel(right_col, text="Middle Name", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
                ctk.CTkEntry(right_col, width=220, fg_color="#fff", text_color="#000").pack(fill="x", pady=(0, 10))
                ctk.CTkLabel(right_col, text="Suffix Name", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
                ctk.CTkEntry(right_col, width=220, fg_color="#fff", text_color="#000").pack(fill="x", pady=(0, 10))
                ctk.CTkLabel(right_col, text="Section", anchor="w", font=ctk.CTkFont(size=13), text_color="#000").pack(anchor="w", pady=(0, 2))
                ctk.CTkEntry(right_col, width=220, fg_color="#fff", text_color="#000").pack(fill="x", pady=(0, 10))
                # Facial recognition button (no camera emoji)
                fr_btn = ctk.CTkButton(right_col, text="Take Facial Recognition", fg_color="#1E3A8A", hover_color="#1E3A8A", text_color="#fff", width=220, height=32, corner_radius=8, command=lambda: FacialRecognitionPopup(self))
                fr_btn.pack(fill="x", pady=(10, 8))
                # Image/file preview box
                img_frame = ctk.CTkFrame(right_col, fg_color="#222", width=40, height=40, corner_radius=6)
                img_frame.pack(side="left", pady=(0, 0), padx=(0, 8))
                img_frame.pack_propagate(False)
                ctk.CTkLabel(img_frame, text="", fg_color="#222").pack(expand=True, fill="both")
                file_info = ctk.CTkFrame(right_col, fg_color="#fff")
                file_info.pack(fill="x", pady=(0, 10))
                ctk.CTkLabel(file_info, text="img.name", font=ctk.CTkFont(size=13, weight="bold"), text_color="#000").pack(anchor="w")
                ctk.CTkLabel(file_info, text=".jpeg", font=ctk.CTkFont(size=11), text_color="#757575").pack(anchor="w")
                # Bottom buttons
                btns_frame = ctk.CTkFrame(self, fg_color="#fff")
                btns_frame.pack(fill="x", padx=30, pady=(10, 20))
                ctk.CTkButton(btns_frame, text="Cancel", fg_color="#E5E7EB", text_color="#000", hover_color="#D1D5DB", width=600, height=36, corner_radius=8, command=self.destroy).pack(fill="x", pady=(0, 8))
                ctk.CTkButton(btns_frame, text="Save Changes", fg_color="#1E3A8A", hover_color="#1E3A8A", text_color="#fff", width=600, height=36, corner_radius=8, command=self.show_caution_modal).pack(fill="x")
            elif action == "Delete":
                # Responsive Modern Delete Modal
                self.geometry("340x210")
                self.update_idletasks()
                self._center_window(340, 210)
                self.configure(fg_color="#FAFAFA")
                # Card frame for rounded corners, responsive
                card = ctk.CTkFrame(self, fg_color="#fff", corner_radius=16)
                card.pack(expand=True, fill="both", padx=16, pady=16)
                card.pack_propagate(True)
                # Circle + Trash icon (centered)
                import os
                from PIL import Image, ImageTk, ImageOps
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
            else:
                ctk.CTkButton(self, text="Close", fg_color="#2563EB", hover_color="#1D4ED8", text_color="#fff", command=self.destroy).pack(pady=20)

    def show_caution_modal(self):
        def on_continue():
            print('Changes saved!')
            # Place your save logic here
        CautionModal(self, on_continue=on_continue)

    def show_success_modal(self):
        SuccessModal(self)

class FacialRecognitionPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Facial Recognition")
        self.geometry("454x450")
        self.resizable(False, False)
        self.configure(fg_color="#222222")
        self.minsize(454, 450)
        self.maxsize(454, 450)
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        self._center_window(454, 450)
        self.update()
        self._create_verification_dialog_content()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _create_verification_dialog_content(self):
        """Create content for the face verification dialog (as main popup content)"""
        import tkinter.messagebox as messagebox
        # Card Frame with explicit sizing
        card = ctk.CTkFrame(
            self, 
            width=454, 
            height=450, 
            corner_radius=12, 
            fg_color="#ffffff", 
            border_width=0
        )
        card.place(x=0, y=0)
        card.pack_propagate(False)
        card.grid_propagate(False)

        # Info icon (top right)
        info_btn = ctk.CTkButton(
            card, 
            text="i", 
            width=24, 
            height=24, 
            corner_radius=12, 
            fg_color="#f5f5f5", 
            text_color="#222", 
            font=ctk.CTkFont("Roboto", 14, "bold"), 
            hover_color="#e0e0e0", 
            command=lambda: messagebox.showinfo("Info", "Please ensure you're in a well-lit environment before capturing your photo for the best image quality", parent=self)
        )
        info_btn.place(x=420, y=10)

        # Camera Preview Frame with explicit sizing
        self.face_preview_frame = ctk.CTkFrame(
            card, 
            width=410, 
            height=240, 
            fg_color="#fafafa", 
            border_width=1, 
            border_color="#d1d1d1"
        )
        self.face_preview_frame.place(x=22, y=38)
        self.face_preview_frame.pack_propagate(False)
        self.face_preview_frame.grid_propagate(False)

        # Default Preview Label (centered)
        self.preview_label = ctk.CTkLabel(
            self.face_preview_frame,
            text="Camera will appear here\nClick 'Open Camera' to begin",
            font=ctk.CTkFont("Roboto", 12),
            text_color="#a0a0a0"
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Open Camera Button with explicit sizing
        self.camera_button = ctk.CTkButton(
            card,
            text="Open Camera",
            width=410,
            height=32,
            corner_radius=6,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#ffffff",
            text_color="#222",
            border_width=1,
            border_color="#d1d1d1",
            hover_color="#f5f5f5",
            command=self.toggle_camera if hasattr(self, 'toggle_camera') else None
        )
        self.camera_button.place(x=22, y=290)

        # Retake and Capture Buttons with explicit sizing
        self.retake_button = ctk.CTkButton(
            card,
            text="Retake",
            width=200,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#e5e5e5",
            text_color="#707070",
            border_width=0,
            hover_color="#cccccc",
            state="disabled",
            command=self.retake_photo if hasattr(self, 'retake_photo') else None
        )
        self.retake_button.place(x=22, y=335)

        self.capture_button = ctk.CTkButton(
            card,
            text="Capture",
            width=200,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            state="disabled",
            command=self.capture_face if hasattr(self, 'capture_face') else None
        )
        self.capture_button.place(x=232, y=335)

        # Register Button with explicit sizing
        self.register_button = ctk.CTkButton(
            card,
            text="Next",
            width=410,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont("Roboto", 13, "bold"),
            fg_color="#1E3A8A",
            text_color="#fff",
            border_width=0,
            hover_color="#152a63",
            command=self.complete_registration if hasattr(self, 'complete_registration') else None,
            state="disabled"
        )
        self.register_button.place(x=22, y=385)

class CautionModal(ctk.CTkToplevel):
    def __init__(self, parent, on_continue=None):
        super().__init__(parent)
        self.title("Caution")
        self.geometry("340x210")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        self._center_window(340, 210)
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
            command=self.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkButton(
            btns_frame,
            text="Continue",
            fg_color="#FBBF24",
            text_color="#fff",
            hover_color="#f59e1b",
            height=38,
            corner_radius=8,
            command=self.show_success_modal
        ).pack(side="left", expand=True, fill="x", padx=(8, 0))

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def show_success_modal(self):
        SuccessModal(self)

class SuccessModal(ctk.CTkToplevel):
    def __init__(self, parent, on_continue=None):
        super().__init__(parent)
        self.title("Success")
        self.geometry("340x210")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        self._center_window(340, 210)
        self._parent_modal = parent
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
            command=self._close_all        ).pack(expand=True, fill="both", padx=0)

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _close_all(self):
        self.destroy()
        try:
            self._parent_modal.destroy()
        except Exception:
            pass

class UsersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = DatabaseManager()
        self.all_users = []
        self.students_data = []
        self.faculty_data = []
        
        # Pagination settings
        self.students_per_page = 10  # Changed back to 10
        self.faculty_per_page = 10   # Changed back to 10
        self.current_students_page = 1
        self.current_faculty_page = 1
        
        # Setup UI first, then load data
        self.setup_ui()
        self.load_users_data()

    def get_total_students_pages(self):
        """Calculate total pages for students"""
        total_students = len(self.students_data)
        return max(1, (total_students + self.students_per_page - 1) // self.students_per_page)

    def get_total_faculty_pages(self):
        """Calculate total pages for faculty"""
        total_faculty = len(self.faculty_data)
        return max(1, (total_faculty + self.faculty_per_page - 1) // self.faculty_per_page)

    def get_students_for_page(self, page):
        """Get students data for specific page"""
        start_idx = (page - 1) * self.students_per_page
        end_idx = start_idx + self.students_per_page
        return self.students_data[start_idx:end_idx]

    def get_faculty_for_page(self, page):
        """Get faculty data for specific page"""
        start_idx = (page - 1) * self.faculty_per_page
        end_idx = start_idx + self.faculty_per_page
        return self.faculty_data[start_idx:end_idx]

    def change_students_page(self, direction):
        """Change students page"""
        total_pages = self.get_total_students_pages()
        if direction == "prev" and self.current_students_page > 1:
            self.current_students_page -= 1
        elif direction == "next" and self.current_students_page < total_pages:
            self.current_students_page += 1
        self.refresh_students_table()

    def change_faculty_page(self, direction):
        """Change faculty page"""
        total_pages = self.get_total_faculty_pages()
        if direction == "prev" and self.current_faculty_page > 1:
            self.current_faculty_page -= 1
        elif direction == "next" and self.current_faculty_page < total_pages:
            self.current_faculty_page += 1
        self.refresh_faculty_table()

    def load_users_data(self):
        """Load users data from database and filter by role"""
        try:
            success, users = self.db_manager.get_all_users()
            
            if success:
                self.all_users = users
                
                # Filter users by role
                self.students_data = [user for user in users if user['role'].lower() == 'student']
                self.faculty_data = [user for user in users if user['role'].lower() in ['faculty', 'admin']]
                
                # Always refresh the tables since UI is now set up
                self.refresh_students_table()
                self.refresh_faculty_table()
                
            else:
                print(f"Error loading users: {users}")
                
        except Exception as e:
            print(f"Error in load_users_data: {e}")
            import traceback
            traceback.print_exc()

    def refresh_students_table(self):
        """Refresh the students table with current data"""
        try:
            # Clear existing content and rebuild
            for widget in self.students_content.winfo_children():
                widget.destroy()
            self.setup_students_tab(self.students_content)
        except Exception as e:
            print(f"Error refreshing students table: {e}")

    def refresh_faculty_table(self):
        """Refresh the faculty table with current data"""
        try:
            # Clear existing content and rebuild
            for widget in self.faculty_content.winfo_children():
                widget.destroy()
            self.setup_faculty_tab(self.faculty_content)
        except Exception as e:
            print(f"Error refreshing faculty table: {e}")

    def setup_ui(self):
        # Top bar with date pill
        topbar = ctk.CTkFrame(self, fg_color="transparent")
        topbar.pack(fill="x", pady=(10, 0), padx=10)
        topbar.grid_columnconfigure(0, weight=1)
        DateTimePill(topbar).grid(row=0, column=1, sticky="e")

        # Header
        ctk.CTkLabel(
            self,
            text="Users",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w", padx=20, pady=(20, 10))

        # Create tab container
        tab_container = ctk.CTkFrame(self, fg_color="transparent")
        tab_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Tab header frame
        tab_header_frame = ctk.CTkFrame(tab_container, fg_color="#F8FAFC", height=60, border_width=0, corner_radius=12)
        tab_header_frame.pack(fill="x", pady=(0, 8))
        tab_header_frame.pack_propagate(False)

        # Tab buttons container
        tab_buttons_frame = ctk.CTkFrame(tab_header_frame, fg_color="transparent")
        tab_buttons_frame.pack(expand=True, fill="both", padx=0, pady=12)

        # Tab state tracking
        self.active_tab = "students"
        
        # Students tab button
        self.students_tab_btn = ctk.CTkButton(
            tab_buttons_frame,
            text="👥  Students",
            width=140,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#2563EB",
            text_color="#FFFFFF",
            hover_color="#3B82F6",
            border_width=0,
            command=lambda: self.switch_tab("students")
        )
        self.students_tab_btn.pack(side="left", padx=(0, 6))

        # Faculty tab button (renamed from admins)
        self.faculty_tab_btn = ctk.CTkButton(
            tab_buttons_frame,
            text="🎓  Faculty",
            width=140,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(family="Inter", size=13, weight="normal"),
            fg_color="#FFFFFF",
            text_color="#64748B",
            hover_color="#F8FAFC",
            border_width=1,
            border_color="#E2E8F0",
            command=lambda: self.switch_tab("faculty")
        )
        self.faculty_tab_btn.pack(side="left", padx=(6, 0))

        # Content frame
        self.content_frame = ctk.CTkFrame(tab_container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=(8, 0))

        # Create both tab contents
        self.students_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.faculty_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # Setup tab contents
        self.setup_students_tab(self.students_content)
        self.setup_faculty_tab(self.faculty_content)

        # Show initial tab
        self.show_students_tab()

    def switch_tab(self, tab_name):
        """Switch between tabs with smooth animations"""
        if self.active_tab == tab_name:
            return
            
        self.active_tab = tab_name
        
        if tab_name == "students":
            # Animate students tab activation
            self.animate_button_activation(self.students_tab_btn, True)
            self.animate_button_activation(self.faculty_tab_btn, False)
            self.after(80, self.show_students_tab)
        else:
            # Animate faculty tab activation
            self.animate_button_activation(self.faculty_tab_btn, True)
            self.animate_button_activation(self.students_tab_btn, False)
            self.after(80, self.show_faculty_tab)

    def animate_button_activation(self, button, is_active):
        """Smooth animation for tab button state changes"""
        if is_active:
            # Activation animation
            button.configure(fg_color="#3B82F6")
            self.after(20, lambda: button.configure(
                fg_color="#2563EB",
                text_color="#FFFFFF",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                border_width=0,
                hover_color="#3B82F6"
            ))
        else:
            # Deactivation animation
            button.configure(fg_color="#F8FAFC")
            self.after(40, lambda: button.configure(
                fg_color="#FFFFFF",
                text_color="#64748B",
                font=ctk.CTkFont(family="Inter", size=13, weight="normal"),
                border_width=1,
                border_color="#E2E8F0",
                hover_color="#F8FAFC"
            ))

    def show_students_tab(self):
        """Show students tab content"""
        self.faculty_content.pack_forget()
        self.students_content.pack(fill="both", expand=True)

    def show_faculty_tab(self):
        """Show faculty tab content"""
        self.students_content.pack_forget()
        self.faculty_content.pack(fill="both", expand=True)

    def get_status_color(self, status):
        """Get text color for status"""
        status_colors = {
            # Student statuses
            'Enrolled': '#22C55E',      # Green
            'Graduated': '#F59E0B',     # Yellow/Amber
            'Dropout': '#EF4444',       # Red
            'On Leave': '#6B7280',      # Gray
            'Suspended': '#DC2626',     # Dark Red
            
            # Faculty statuses
            'Active': '#10B981',        # Emerald
            'Inactive': '#9CA3AF',      # Light Gray
            'Retired': '#8B5CF6',       # Purple
            'Probationary': '#F97316',  # Orange
            'Tenure Track': '#3B82F6',  # Blue
            'Tenured': '#059669',       # Dark Green
            
            # Default
            'No Status': '#6B7280',     # Light Gray
        }
        
        return status_colors.get(status, status_colors['No Status'])

    def create_status_badge(self, parent, status, row, column):
        """Create a colored status text"""
        color = self.get_status_color(status)
        
        # Create simple label with colored text
        status_label = ctk.CTkLabel(
            parent,
            text=status,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color,
            fg_color="transparent",
            anchor="w"
        )
        status_label.grid(row=row, column=column, sticky="w", padx=10, pady=3)

    def setup_students_tab(self, parent):
        # Search and filter bar (side by side, both with border, no corner radius, flush)
        search_bar_container = ctk.CTkFrame(parent, fg_color="#fff")
        search_bar_container.pack(pady=(0, 10), padx=0, anchor="w")

        # Search entry with icon inside (frame height 36, icon and entry height 28, centered vertically, consistent color)
        search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="Search students...", width=160, fg_color="#fff",
                                    border_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=15), height=28)
        search_entry.pack(side="left", padx=(2, 8), pady=4)

        # Filter button (flush, no corner radius, border on all sides, same height)
        filter_btn = ctk.CTkButton(
            search_bar_container,
            text="Filters",
            width=80,
            height=36,
            fg_color="#fff",
            text_color="#757575",
            hover_color="#F3F4F6",
            border_width=1,
            border_color="#BDBDBD",
            corner_radius=0,
            font=ctk.CTkFont(size=13),
            command=self.show_filter_popup
        )
        filter_btn.pack(side="left", padx=0, pady=0)

        # Table
        table_frame = ctk.CTkFrame(parent, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=0, pady=(10, 5))  # Reduced padding

        # Columns (add status column)
        columns = ["", "Student Name", "Year", "Section", "Program", "Status", "Actions"]
        col_widths = [1, 8, 1, 1, 1, 2, 1]  # increased status column weight
        for i, weight in enumerate(col_widths):
            table_frame.grid_columnconfigure(i, weight=weight)

        # Header row (leave image column header blank) with reduced padding
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6B7280",
                anchor="w"
            ).grid(row=0, column=i, padx=10, pady=6, sticky="w")  # Reduced pady from 8 to 6

        # Use only database data - no sample data fallback
        data_to_display = []
        
        if self.students_data:
            # Get data for current page
            paginated_students = self.get_students_for_page(self.current_students_page)
            
            # Get additional data from database for each student
            for student in paginated_students:
                # Get section and program info
                section_name = "N/A"
                program_name = "N/A"
                year_level = "N/A"
                
                try:
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    
                    # Get section and program info if section ID exists
                    if student.get('section'):
                        cursor.execute("""
                            SELECT s.name as section_name, p.name as program_name
                            FROM sections s
                            JOIN programs p ON s.course_id = p.id
                            WHERE s.id = ?
                        """, (student['section'],))
                        
                        result = cursor.fetchone()
                        if result:
                            section_name = result['section_name']
                            program_name = result['program_name']
                            
                            # Extract year from section name (e.g., "1-1" -> "1st Year")
                            section_year = section_name.split('-')[0]
                            year_mapping = {'1': '1st Year', '2': '2nd Year', '3': '3rd Year', '4': '4th Year'}
                            year_level = year_mapping.get(section_year, f"Year {section_year}")
                            
                            # Shorten program name for display
                            if "Information Technology" in program_name:
                                program_name = "BSIT"
                            elif "Computer Science" in program_name:
                                program_name = "BSCS"
                            elif "Information Systems" in program_name:
                                program_name = "BSIS"
                    
                    conn.close()
                    
                except Exception as e:
                    print(f"Error getting student details: {e}")
                
                # Convert database format to display format
                data_to_display.append((
                    student['full_name'],
                    year_level,
                    section_name,
                    program_name
                ))

        # Display message if no data
        if not data_to_display:
            no_data_label = ctk.CTkLabel(
                table_frame,
                text="No students found. Run the seeder script to add sample data.",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            )
            no_data_label.grid(row=1, column=0, columnspan=7, pady=20)  # Updated columnspan
        else:
            for idx, (name, year, section, program) in enumerate(data_to_display, start=1):
                bg = "#fff"
                # Get status from students_data
                student = self.get_students_for_page(self.current_students_page)[idx-1]
                status = student.get('status_name', 'No Status')
                
                # Image placeholder (circle) - smaller size
                image_canvas = tk.Canvas(table_frame, width=28, height=28, bg=bg, highlightthickness=0)
                image_canvas.grid(row=idx, column=0, sticky="nsew", padx=(32, 0), pady=3)
                image_canvas.create_oval(3, 3, 25, 25, fill="#E5E7EB", outline="#D1D5DB")
                # Name
                ctk.CTkLabel(table_frame, text=name, font=ctk.CTkFont(size=12), text_color="#222",
                            fg_color=bg, anchor="w").grid(row=idx, column=1, sticky="nsew", padx=(0, 10), pady=3)
                # Year
                ctk.CTkLabel(table_frame, text=year, font=ctk.CTkFont(size=12), text_color="#222",
                            fg_color=bg, anchor="w").grid(row=idx, column=2, sticky="nsew", padx=10, pady=3)
                # Section
                ctk.CTkLabel(table_frame, text=section, font=ctk.CTkFont(size=12), text_color="#222",
                            fg_color=bg, anchor="w").grid(row=idx, column=3, sticky="nsew", padx=10, pady=3)
                # Programs
                ctk.CTkLabel(table_frame, text=program, font=ctk.CTkFont(size=12), text_color="#222",
                            fg_color=bg, anchor="w").grid(row=idx, column=4, sticky="nsew", padx=10, pady=3)
                # Status - now with colored badge
                self.create_status_badge(table_frame, status, idx, 5)
                # Actions dropdown styled as button - smaller size
                action_var = tk.StringVar(value="Edit")
                actions = ["Edit", "View", "Delete"]
                action_menu = ctk.CTkOptionMenu(
                    table_frame,
                    values=actions,
                    variable=action_var,
                    width=90,
                    height=24,
                    font=ctk.CTkFont(size=11),
                    fg_color="#F3F4F6",
                    text_color="#222",
                    button_color="#E5E7EB",
                    button_hover_color="#D1D5DB",
                    dropdown_fg_color="#fff",
                    dropdown_hover_color="#E5E7EB",
                    dropdown_text_color="#222",
                    command=lambda choice, data=(name, year, section, program): self.handle_action(choice, data)
                )
                action_menu.grid(row=idx, column=6, sticky="w", padx=10, pady=3)

        # Pagination controls for students - reduced height
        pagination_frame = ctk.CTkFrame(parent, fg_color="#fff", height=40, border_width=1, border_color="#E5E7EB", corner_radius=0)
        pagination_frame.pack(fill="x", padx=0, pady=0)
        pagination_frame.pack_propagate(False)

        # Pagination content
        pagination_content = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        pagination_content.pack(expand=True, fill="both", padx=20, pady=8)

        # Left side - showing X of Y entries
        if self.students_data:
            total_students = len(self.students_data)
            total_pages = self.get_total_students_pages()
            start_entry = (self.current_students_page - 1) * self.students_per_page + 1
            end_entry = min(self.current_students_page * self.students_per_page, total_students)
            entries_text = f"Showing {start_entry} to {end_entry} of {total_students} entries"
        else:
            entries_text = "No entries to display"
            total_pages = 0

        ctk.CTkLabel(
            pagination_content,
            text=entries_text,
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        ).pack(side="left")

        # Right side - navigation buttons (only show if more than 1 page)
        if self.students_data and total_pages > 1:
            nav_frame = ctk.CTkFrame(pagination_content, fg_color="transparent")
            nav_frame.pack(side="right")

            # Previous button
            prev_btn = ctk.CTkButton(
                nav_frame,
                text="← Previous",
                width=80,
                height=30,
                font=ctk.CTkFont(size=12),
                fg_color="#F9FAFB",
                text_color="#374151",
                hover_color="#E5E7EB",
                border_width=1,
                border_color="#D1D5DB",
                corner_radius=6,
                command=lambda: self.change_students_page("prev")
            )
            prev_btn.pack(side="left", padx=(0, 4))

            # Page info
            page_text = f"{self.current_students_page} of {total_pages}"
            ctk.CTkLabel(
                nav_frame,
                text=page_text,
                font=ctk.CTkFont(size=12),
                text_color="#374151",
                width=60
            ).pack(side="left", padx=4)

            # Next button
            next_btn = ctk.CTkButton(
                nav_frame,
                text="Next →",
                width=80,
                height=30,
                font=ctk.CTkFont(size=12),
                fg_color="#F9FAFB",
                text_color="#374151",
                hover_color="#E5E7EB",
                border_width=1,
                border_color="#D1D5DB",
                corner_radius=6,
                command=lambda: self.change_students_page("next")
            )
            next_btn.pack(side="left", padx=(4, 0))

            # Disable buttons when at limits
            if self.current_students_page <= 1:
                prev_btn.configure(state="disabled", fg_color="#F3F4F6", text_color="#9CA3AF")
            if self.current_students_page >= total_pages:
                next_btn.configure(state="disabled", fg_color="#F3F4F6", text_color="#9CA3AF")
        elif self.students_data and total_pages == 1:
            # Show "Page 1 of 1" for single page
            single_page_label = ctk.CTkLabel(
                pagination_content,
                text="Page 1 of 1",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            single_page_label.pack(side="right")

    def setup_faculty_tab(self, parent):
        # Search and filter bar for faculty
        search_bar_container = ctk.CTkFrame(parent, fg_color="#fff")
        search_bar_container.pack(pady=(0, 10), padx=0, anchor="w")

        # Search entry with icon
        search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="Search faculty...", width=160, fg_color="#fff",
                                    border_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=15), height=28)
        search_entry.pack(side="left", padx=(2, 8), pady=4)
        filter_btn = ctk.CTkButton(
            search_bar_container,
            text="Filters",
            width=80,
            height=36,
            fg_color="#fff",
            text_color="#757575",
            hover_color="#F3F4F6",
            border_width=1,
            border_color="#BDBDBD",
            corner_radius=0,
            font=ctk.CTkFont(size=13),
            command=self.show_filter_popup
        )
        filter_btn.pack(side="left", padx=0, pady=0)

        # Faculty table
        table_frame = ctk.CTkFrame(parent, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=0, pady=(10, 5))  # Reduced padding

        # Columns for faculty (add status column)
        columns = ["", "Faculty Name", "Employee Number", "Email", "Role", "Status", "Actions"]
        col_widths = [1, 5, 2, 5, 2, 2, 2]  # adjusted weights
        for i, weight in enumerate(col_widths):
            table_frame.grid_columnconfigure(i, weight=weight)

        # Header row with reduced padding
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6B7280",
                anchor="w"
            ).grid(row=0, column=i, padx=10, pady=6, sticky="w")  # Reduced pady from 8 to 6

        # Use only database data - no sample data fallback
        data_to_display = []
        
        if self.faculty_data:
            # Get data for current page
            paginated_faculty = self.get_faculty_for_page(self.current_faculty_page)
            
            for faculty in paginated_faculty:
                # Convert database format to display format
                data_to_display.append((
                    faculty['full_name'],
                    faculty.get('employee_number', 'N/A'),
                    faculty['email'],
                    faculty['role']
                ))

        # Display message if no data
        if not data_to_display:
            no_data_label = ctk.CTkLabel(
                table_frame,
                text="No faculty found. Run the seeder script to add sample data.",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            )
            no_data_label.grid(row=1, column=0, columnspan=7, pady=20)  # Updated columnspan
        else:
            for idx, (name, emp_num, email, role) in enumerate(data_to_display, start=1):
                bg = "#fff"
                # Get status from faculty_data
                faculty = self.get_faculty_for_page(self.current_faculty_page)[idx-1]
                status = faculty.get('status_name', 'No Status')
                
                # Image placeholder (circle) - smaller size
                image_canvas = tk.Canvas(table_frame, width=28, height=28, bg=bg, highlightthickness=0)
                image_canvas.grid(row=idx, column=0, sticky="nsew", padx=(32, 0), pady=3)
                image_canvas.create_oval(3, 3, 25, 25, fill="#E5E7EB", outline="#D1D5DB")
                # Name
                ctk.CTkLabel(table_frame, text=name, font=ctk.CTkFont(size=12), text_color="#222",
                            fg_color=bg, anchor="w").grid(row=idx, column=1, sticky="nsew", padx=(0, 10), pady=3)
                # Employee Number
                ctk.CTkLabel(table_frame, text=emp_num, font=ctk.CTkFont(size=12), text_color="#222",
                            fg_color=bg, anchor="w").grid(row=idx, column=2, sticky="nsew", padx=10, pady=3)
                # Email
                ctk.CTkLabel(table_frame, text=email, font=ctk.CTkFont(size=12), text_color="#222",
                            fg_color=bg, anchor="w").grid(row=idx, column=3, sticky="nsew", padx=10, pady=3)
                # Role
                ctk.CTkLabel(table_frame, text=role, font=ctk.CTkFont(size=12), text_color="#222",
                            fg_color=bg, anchor="w").grid(row=idx, column=4, sticky="nsew", padx=10, pady=3)
                # Status - now with colored badge
                self.create_status_badge(table_frame, status, idx, 5)
                # Actions dropdown - smaller size
                action_var = tk.StringVar(value="Edit")
                actions = ["Edit", "View", "Delete"]
                action_menu = ctk.CTkOptionMenu(
                    table_frame,
                    values=actions,
                    variable=action_var,
                    width=90,
                    height=24,
                    font=ctk.CTkFont(size=11),
                    fg_color="#F3F4F6",
                    text_color="#222",
                    button_color="#E5E7EB",
                    button_hover_color="#D1D5DB",
                    dropdown_fg_color="#fff",
                    dropdown_hover_color="#E5E7EB",
                    dropdown_text_color="#222",
                    command=lambda choice, data=(name, emp_num, email, role): self.handle_faculty_action(choice, data)
                )
                action_menu.grid(row=idx, column=6, sticky="w", padx=10, pady=3)

        # Pagination controls for faculty - reduced height
        pagination_frame = ctk.CTkFrame(parent, fg_color="#fff", height=40, border_width=1, border_color="#E5E7EB", corner_radius=0)  # Reduced from 50 to 40
        pagination_frame.pack(fill="x", padx=0, pady=0)
        pagination_frame.pack_propagate(False)

        # Pagination content
        pagination_content = ctk.CTkFrame(pagination_frame, fg_color="transparent")
        pagination_content.pack(expand=True, fill="both", padx=20, pady=8)  # Reduced pady from 10 to 8

        # Left side - showing X of Y entries
        if self.faculty_data:
            total_faculty = len(self.faculty_data)
            total_pages = self.get_total_faculty_pages()
            start_entry = (self.current_faculty_page - 1) * self.faculty_per_page + 1
            end_entry = min(self.current_faculty_page * self.faculty_per_page, total_faculty)
            entries_text = f"Showing {start_entry} to {end_entry} of {total_faculty} entries"
        else:
            entries_text = "No entries to display"
            total_pages = 0

        ctk.CTkLabel(
            pagination_content,
            text=entries_text,
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        ).pack(side="left")

        # Right side - navigation buttons (only show if more than 1 page)
        if self.faculty_data and total_pages > 1:
            nav_frame = ctk.CTkFrame(pagination_content, fg_color="transparent")
            nav_frame.pack(side="right")

            # Previous button
            prev_btn = ctk.CTkButton(
                nav_frame,
                text="← Previous",
                width=80,
                height=30,
                font=ctk.CTkFont(size=12),
                fg_color="#F9FAFB",
                text_color="#374151",
                hover_color="#E5E7EB",
                border_width=1,
                border_color="#D1D5DB",
                corner_radius=6,
                command=lambda: self.change_faculty_page("prev")
            )
            prev_btn.pack(side="left", padx=(0, 4))

            # Page info
            page_text = f"{self.current_faculty_page} of {total_pages}"
            ctk.CTkLabel(
                nav_frame,
                text=page_text,
                font=ctk.CTkFont(size=12),
                text_color="#374151",
                width=60
            ).pack(side="left", padx=4)

            # Next button
            next_btn = ctk.CTkButton(
                nav_frame,
                text="Next →",
                width=80,
                height=30,
                font=ctk.CTkFont(size=12),
                fg_color="#F9FAFB",
                text_color="#374151",
                hover_color="#E5E7EB",
                border_width=1,
                border_color="#D1D5DB",
                corner_radius=6,
                command=lambda: self.change_faculty_page("next")
            )
            next_btn.pack(side="left", padx=(4, 0))

            # Disable buttons when at limits
            if self.current_faculty_page <= 1:
                prev_btn.configure(state="disabled", fg_color="#F3F4F6", text_color="#9CA3AF")
            if self.current_faculty_page >= total_pages:
                next_btn.configure(state="disabled", fg_color="#F3F4F6", text_color="#9CA3AF")
        elif self.faculty_data and total_pages == 1:
            # Show "Page 1 of 1" for single page
            single_page_label = ctk.CTkLabel(
                pagination_content,
                text="Page 1 of 1",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            single_page_label.pack(side="right")

    def show_filter_popup(self):
        FilterPopup(self)

    def show_action_menu(self, widget, data):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="View", command=lambda: print(f"Viewing {data[0]}"))
        menu.add_command(label="Edit", command=lambda: print(f"Editing {data[0]}"))
        menu.add_command(label="Delete", command=lambda: print(f"Deleting {data[0]}"))
        x = widget.winfo_rootx()
        y = widget.winfo_rooty() + widget.winfo_height()
        self.after(1, lambda: menu.tk_popup(x, y))

    def handle_action(self, action, data):
        ActionPopup(self, action, data)

    def handle_faculty_action(self, action, data):
        # Reuse existing ActionPopup for faculty
        ActionPopup(self, action, data)
