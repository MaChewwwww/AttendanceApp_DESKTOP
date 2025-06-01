import customtkinter as ctk
import tkinter as tk
from app.ui.admin.components.sidebar import DateTimePill  # adjust path if needed
from app.ui.admin.components.modals import CautionModal, DeleteModal, SuccessModal

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
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        self.setup_ui()
    
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
        self.setup_ui()

    def setup_ui(self):
        action = self.action
        # Unpack user data
        name, year, section, program = self.user_data
        if action == "View":
            self.geometry("640x720")
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
                def on_delete():
                    self.destroy()  # Close ActionPopup
                    root = self.winfo_toplevel()  # Get root window
                    SuccessModal(root)  # Show success modal
                DeleteModal(self, on_delete=on_delete)
            else:
                ctk.CTkButton(self, text="Close", fg_color="#2563EB", hover_color="#1D4ED8", text_color="#fff", command=self.destroy).pack(pady=20)

    def show_caution_modal(self):
        def on_continue():
            print('Changes saved!')
            # Place your save logic here
            SuccessModal(self)
        CautionModal(self, on_continue=on_continue)

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
        # Center the window
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 454) // 2
        y = (screen_height - 450) // 2
        self.geometry(f"454x450+{x}+{y}")
        self.update()
        self._create_verification_dialog_content()

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

class UsersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

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

        # Search and filter bar (side by side, both with border, no corner radius, flush)
        search_bar_container = ctk.CTkFrame(self, fg_color="#fff")
        search_bar_container.pack(pady=(0, 10), padx=20, anchor="w")

        # Search entry with icon inside (frame height 36, icon and entry height 28, centered vertically, consistent color)
        search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="", width=160, fg_color="#fff",
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
        table_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Columns (add image column at index 0)
        columns = ["", "Student Name", "Year", "Section", "Program", "Actions"]
        col_widths = [1, 10, 1, 1, 1, 1]  # all integers
        for i, weight in enumerate(col_widths):
            table_frame.grid_columnconfigure(i, weight=weight)

        # Header row (leave image column header blank)
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6B7280",
                anchor="w"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        # Sample data
        sample_data = [
            ("Shadrack Castro", "1st Year", "1-1", "BSIT"),
            ("Jerlee Alipio", "2nd Year", "2-3", "BSCS"),
            ("Steven Masangcay", "3rd Year", "3-2", "BSIT"),
            ("John Mathew Parocha", "4th Year", "4-1", "BSIS"),
        ]

        for idx, (name, year, section, program) in enumerate(sample_data, start=1):
            bg = "#fff"
            # Image placeholder (circle)
            image_canvas = tk.Canvas(table_frame, width=32, height=32, bg=bg, highlightthickness=0)
            image_canvas.grid(row=idx, column=0, sticky="nsew", padx=(32, 0), pady=6)
            image_canvas.create_oval(4, 4, 28, 28, fill="#E5E7EB", outline="#D1D5DB")
            # Name
            ctk.CTkLabel(table_frame, text=name, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color=bg, anchor="w").grid(row=idx, column=1, sticky="nsew", padx=(0, 10), pady=6)
            # Year
            ctk.CTkLabel(table_frame, text=year, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color=bg, anchor="w").grid(row=idx, column=2, sticky="nsew", padx=10, pady=6)
            # Section
            ctk.CTkLabel(table_frame, text=section, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color=bg, anchor="w").grid(row=idx, column=3, sticky="nsew", padx=10, pady=6)
            # Programs
            ctk.CTkLabel(table_frame, text=program, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color=bg, anchor="w").grid(row=idx, column=4, sticky="nsew", padx=10, pady=6)
            # Actions dropdown styled as button
            action_var = tk.StringVar(value="Edit")
            actions = ["Edit", "View", "Delete"]
            action_menu = ctk.CTkOptionMenu(
                table_frame,
                values=actions,
                variable=action_var,
                width=100,
                height=28,
                font=ctk.CTkFont(size=12),
                fg_color="#F3F4F6",
                text_color="#222",
                button_color="#E5E7EB",
                button_hover_color="#D1D5DB",
                dropdown_fg_color="#fff",
                dropdown_hover_color="#E5E7EB",
                dropdown_text_color="#222",
                command=lambda choice, data=(name, year, section, program): self.handle_action(choice, data)
            )
            action_menu.grid(row=idx, column=5, sticky="w", padx=10, pady=6)

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
        if action == "Delete":
            def on_delete():
                root = self.winfo_toplevel()  # Get root window
                SuccessModal(root)  # Show success modal
            DeleteModal(self, on_delete=on_delete)
        else:
            ActionPopup(self, action, data)
