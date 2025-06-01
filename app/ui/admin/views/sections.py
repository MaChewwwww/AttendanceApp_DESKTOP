import customtkinter as ctk
from app.ui.admin.components.sidebar import DateTimePill
import tkinter as tk
import io
from PIL import Image, ImageTk

class FilterPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Filter Sections")
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
            text="Filter Sections",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Filter options
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Program filter
        ctk.CTkLabel(filter_frame, text="Program", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
        program_var = tk.StringVar(value="All")
        program_options = ["All", "BSIT", "BSCS", "BSIS"]
        program_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=program_options,
            variable=program_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222"
        )
        program_menu.pack(fill="x", pady=(0, 15))
        
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
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Apply Filters",
            command=self.apply_filters,
            fg_color="#1E3A8A",
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

class SectionsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        # Top bar for the DateTimePill
        topbar = ctk.CTkFrame(self, fg_color="transparent")
        topbar.pack(fill="x", pady=(10, 0), padx=10)
        topbar.grid_columnconfigure(0, weight=1)
        pill = DateTimePill(topbar)
        pill.grid(row=0, column=1, sticky="e")

        # Header with 'Sections' label
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            header_frame,
            text="Sections",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(side="left")

        # Search and filter bar container with full width
        search_bar_container = ctk.CTkFrame(self, fg_color="#f5f5f5")
        search_bar_container.pack(fill="x", pady=(0, 10), padx=20)
        
        # Left side container for search and filter
        left_container = ctk.CTkFrame(search_bar_container, fg_color="transparent")
        left_container.pack(side="left", fill="y")

        # Search entry with icon inside
        search_entry_frame = ctk.CTkFrame(left_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="", width=160, fg_color="#fff",
                                    border_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=15), height=28)
        search_entry.pack(side="left", padx=(2, 8), pady=4)

        # Filter button
        filter_btn = ctk.CTkButton(
            left_container,
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

        # Create button on the rightmost corner
        create_btn = ctk.CTkButton(
            search_bar_container,
            text="Create",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            font=ctk.CTkFont(size=13),
            corner_radius=0,
            width=100,
            height=36,
            command=self.create_section
        )
        create_btn.pack(side="right", padx=(0, 0))

        # Table
        table_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Columns: Section, Program, Year, Actions
        columns = ["Section", "Program", "Year", "Actions"]
        col_widths = [4, 4, 2, 1]
        for i, weight in enumerate(col_widths):
            table_frame.grid_columnconfigure(i, weight=weight)

        # Header row
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6B7280",
                anchor="w"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        # Sample data: (Section, Program, Year)
        sample_data = [
            ("1-1", "BSIT", "1st Year"),
            ("2-3", "BSCS", "2nd Year"),
            ("3-2", "BSIT", "3rd Year"),
            ("4-1", "BSIS", "4th Year"),
        ]

        for idx, (section, program, year) in enumerate(sample_data, start=1):
            # Section
            ctk.CTkLabel(table_frame, text=section, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color="#fff", anchor="w").grid(row=idx, column=0, sticky="nsew", padx=10, pady=6)
            # Program
            ctk.CTkLabel(table_frame, text=program, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color="#fff", anchor="w").grid(row=idx, column=1, sticky="nsew", padx=10, pady=6)
            # Year
            ctk.CTkLabel(table_frame, text=year, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color="#fff", anchor="w").grid(row=idx, column=2, sticky="nsew", padx=10, pady=6)
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
                command=lambda choice, data=(section, program, year): self.handle_action(choice, data)
            )
            action_menu.grid(row=idx, column=3, sticky="w", padx=10, pady=6)

    def show_filter_popup(self):
        FilterPopup(self)

    def handle_action(self, action, data):
        if action == "View":
            SectionViewPopup(self, data)
        else:
            print(f"{action} {data}")

    def create_section(self):
        print("Create section clicked!")

class SectionViewPopup(ctk.CTkToplevel):
    def __init__(self, parent, section_data):
        super().__init__(parent)
        self.title(f"Section View")
        self.geometry("640x720")
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        self.section_data = section_data
        self.setup_ui()

    def setup_ui(self):
        section, program, year = self.section_data
        # Header
        top_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(top_frame, text=f"{program} {section}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#000").pack(anchor="w")
        ctk.CTkLabel(top_frame, text=f"S.Y 2025 - 2026", font=ctk.CTkFont(size=13), text_color="#222").pack(anchor="w")

        # Search and filter bar (copied from users.py ActionPopup)
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

        # Graphs row (placeholders)
        graphs_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        graphs_frame.pack(fill="x", padx=20, pady=(10, 0))
        graphs_frame.grid_columnconfigure(0, weight=1)
        graphs_frame.grid_columnconfigure(1, weight=1)

        # Demographic Pie Chart Placeholder
        pie_card = ctk.CTkFrame(graphs_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        pie_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(pie_card, text="Graph here", font=ctk.CTkFont(size=14, weight="bold"), text_color="#222").pack(expand=True, fill="both", padx=10, pady=10)

        # Absents Bar Chart Placeholder
        bar_card = ctk.CTkFrame(graphs_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        bar_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(bar_card, text="Graph here", font=ctk.CTkFont(size=14, weight="bold"), text_color="#222").pack(expand=True, fill="both", padx=10, pady=10)

        # Table
        table_frame = ctk.CTkFrame(self, fg_color="#fff", border_color="#E5E7EB", border_width=1, corner_radius=8)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ["Course Subject", "Attendance Rate", "Actions"]
        for i in range(3):
            table_frame.grid_columnconfigure(i, weight=1)
        ctk.CTkLabel(table_frame, text="Course Subject", font=ctk.CTkFont(size=13, weight="bold"), text_color="#000", anchor="w").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(table_frame, text="Attendance Rate", font=ctk.CTkFont(size=13, weight="bold"), text_color="#000", anchor="w").grid(row=0, column=1, padx=10, pady=8, sticky="w")
        ctk.CTkLabel(table_frame, text="Actions", font=ctk.CTkFont(size=13, weight="bold"), text_color="#000", anchor="w").grid(row=0, column=2, padx=10, pady=8, sticky="w")
        for idx in range(6):
            ctk.CTkLabel(table_frame, text="Ethics 101", font=ctk.CTkFont(size=13), text_color="#222", fg_color="#fff", anchor="w").grid(row=idx+1, column=0, sticky="nsew", padx=10, pady=6)
            ctk.CTkLabel(table_frame, text="90%", font=ctk.CTkFont(size=13), text_color="#222", fg_color="#fff", anchor="w").grid(row=idx+1, column=1, sticky="nsew", padx=10, pady=6)
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
                command=lambda choice, data=("Ethics 101", "90%"): print(f"{choice} {data}")
            )
            action_menu.grid(row=idx+1, column=2, sticky="w", padx=10, pady=6) 