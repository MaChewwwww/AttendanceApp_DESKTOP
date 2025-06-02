import customtkinter as ctk
import tkinter as tk

class UsersViewModal(ctk.CTkToplevel):
    def __init__(self, parent, user_data, user_type="student"):
        super().__init__(parent)
        self.user_data = user_data
        self.user_type = user_type
        self.title(f"View User")
        self.geometry("640x720")
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        self._center_window(640, 720)
        self.setup_ui()

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        # Unpack user data
        name = self.user_data[0]
        
        if self.user_type == "student":
            _, year, section, program = self.user_data
            subtitle = f"{program} {section}"
        else:
            _, emp_num, email, role = self.user_data
            subtitle = f"{role} • Employee #{emp_num}"
        
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
        ctk.CTkLabel(user_info_frame, text=subtitle, font=ctk.CTkFont(size=14), text_color="#000").pack(anchor="w")
        
        # Export button
        export_btn = ctk.CTkButton(top_frame, text="Export", fg_color="#1E3A8A", hover_color="#1E3A8A", text_color="#fff", width=70, height=32, corner_radius=8)
        export_btn.pack(side="right", padx=(0, 0), pady=(0, 0))

        # Search and filter bar (copied from Users tab)
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
            command=self.show_filter_popup
        )
        filter_btn.pack(side="left", padx=0, pady=0)

        # Table
        table_frame = ctk.CTkFrame(self, fg_color="#fff", border_color="#E5E7EB", border_width=1, corner_radius=8)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Table columns
        if self.user_type == "student":
            columns = ["Course Subject", "Attendance", "Absent", "Rating"]
            table_data = [
                ("Ethics 101", "1", "1", "100%") for _ in range(6)
            ]
        else:
            columns = ["Course", "Section", "Schedule", "Students"]
            table_data = [
                ("Programming 1", "1-1", "Mon 8:00-10:00", "35"),
                ("Database Systems", "2-1", "Tue 10:00-12:00", "30"),
                ("Web Development", "3-1", "Wed 1:00-3:00", "28"),
                ("Software Engineering", "4-1", "Thu 8:00-10:00", "25"),
                ("Data Structures", "2-2", "Fri 10:00-12:00", "32")
            ]
        
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
        for idx, row_data in enumerate(table_data, start=1):
            for col_idx, value in enumerate(row_data):
                ctk.CTkLabel(
                    table_frame,
                    text=value,
                    font=ctk.CTkFont(size=13),
                    text_color="#000",
                    fg_color="#fff",
                    anchor="w"
                ).grid(row=idx, column=col_idx, sticky="nsew", padx=10, pady=6)

    def show_filter_popup(self):
        """Show filter popup - placeholder for now"""
        from .users_modals import FilterPopup
        FilterPopup(self)

    def edit_user(self):
        """Handle edit user action"""
        from .users_edit import UsersEditModal
        self.destroy()
        UsersEditModal(self.master, self.user_data, self.user_type)
