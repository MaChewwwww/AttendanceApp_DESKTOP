import customtkinter as ctk
from app.ui.admin.components.sidebar import DateTimePill
import tkinter as tk
from app.ui.admin.components.modals import DeleteModal, SuccessModal

class FilterPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Filter Courses")
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
            text="Filter Courses",
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

class CourseCreatePopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Create Course")
        self.geometry("360x400")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(
            self,
            text="Create Course",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#111",
        ).pack(anchor="w", padx=24, pady=(24, 12))

        # Program
        ctk.CTkLabel(
            self,
            text="Program",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.program_var = ctk.StringVar(value="Choose a program")
        ctk.CTkOptionMenu(
            self,
            variable=self.program_var,
            values=[
                "Bachelor of Science in Information Technology",
                "Bachelor of Science in Computer Science",
                "Bachelor of Science in Information Systems"
            ],
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            width=300,
            height=38,
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Course Subject
        ctk.CTkLabel(
            self,
            text="Course Subject",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.subject_var = ctk.StringVar(value="Choose a course subject")
        ctk.CTkOptionMenu(
            self,
            variable=self.subject_var,
            values=["Ethics 101", "Programming 1", "Data Structures", "Capstone"],
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            width=300,
            height=38,
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Year (entry with calendar icon)
        ctk.CTkLabel(
            self,
            text="Year",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        year_frame = ctk.CTkFrame(self, fg_color="#fff", border_color="#BDBDBD", border_width=1, height=32)
        year_frame.pack(anchor="w", padx=24, pady=(0, 24), fill="x")
        year_frame.pack_propagate(False)
        self.year_var = ctk.StringVar(value="Enter/Select year")
        year_entry = ctk.CTkEntry(year_frame, textvariable=self.year_var, fg_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=10), height=16, width=280)
        year_entry.pack(side="left", padx=(8, 0), pady=0)
        calendar_icon = ctk.CTkLabel(year_frame, text="\U0001F4C5", font=ctk.CTkFont(size=14), text_color="#757575", fg_color="#fff", width=24)
        calendar_icon.pack(side="right", padx=(0, 4), pady=0)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="#FAFAFA")
        button_frame.pack(side="bottom", fill="x", padx=24, pady=(10, 24))
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="#D1D5DB",
            text_color="#222",
            hover_color="#BDBDBD",
            width=140,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 8))
        create_btn = ctk.CTkButton(
            button_frame,
            text="Create",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            width=140,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.create_course
        )
        create_btn.pack(side="right", padx=(8, 0))

    def create_course(self):
        # TODO: Implement creation logic
        self.destroy()

class CourseEditPopup(ctk.CTkToplevel):
    def __init__(self, parent, course_data):
        super().__init__(parent)
        self.title("Update Course")
        self.geometry("360x400")
        self.resizable(False, False)
        self.configure(fg_color="#FAFAFA")
        self.transient(parent)
        self.grab_set()
        self.course_data = course_data
        self.setup_ui()

    def setup_ui(self):
        program, subject, year = self.course_data
        ctk.CTkLabel(
            self,
            text="Update Course",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#111",
        ).pack(anchor="w", padx=24, pady=(24, 12))

        # Program
        ctk.CTkLabel(
            self,
            text="Program",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.program_var = ctk.StringVar(value=program)
        ctk.CTkOptionMenu(
            self,
            variable=self.program_var,
            values=[
                "Bachelor of Science in Information Technology",
                "Bachelor of Science in Computer Science",
                "Bachelor of Science in Information Systems"
            ],
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            width=300,
            height=38,
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Course Subject
        ctk.CTkLabel(
            self,
            text="Course Subject",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        self.subject_var = ctk.StringVar(value=subject)
        ctk.CTkOptionMenu(
            self,
            variable=self.subject_var,
            values=["Ethics 101", "Programming 1", "Data Structures", "Capstone"],
            fg_color="#fff",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            width=300,
            height=38,
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Year (entry with calendar icon)
        ctk.CTkLabel(
            self,
            text="Year",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 4))
        year_frame = ctk.CTkFrame(self, fg_color="#fff", border_color="#BDBDBD", border_width=1, height=32)
        year_frame.pack(anchor="w", padx=24, pady=(0, 24), fill="x")
        year_frame.pack_propagate(False)
        self.year_var = ctk.StringVar(value="Enter/Select year")
        year_entry = ctk.CTkEntry(year_frame, textvariable=self.year_var, fg_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=10), height=16, width=280)
        year_entry.pack(side="left", padx=(8, 0), pady=0)
        calendar_icon = ctk.CTkLabel(year_frame, text="\U0001F4C5", font=ctk.CTkFont(size=14), text_color="#757575", fg_color="#fff", width=24)
        calendar_icon.pack(side="right", padx=(0, 4), pady=0)

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="#FAFAFA")
        button_frame.pack(side="bottom", fill="x", padx=24, pady=(10, 24))
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            fg_color="#D1D5DB",
            text_color="#222",
            hover_color="#BDBDBD",
            width=140,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 8))
        update_btn = ctk.CTkButton(
            button_frame,
            text="Update",
            fg_color="#1E3A8A",
            hover_color="#1D4ED8",
            text_color="#fff",
            width=140,
            height=40,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.update_course
        )
        update_btn.pack(side="right", padx=(8, 0))

    def update_course(self):
        # TODO: Implement update logic
        self.destroy()

class CourseViewPopup(ctk.CTkToplevel):
    def __init__(self, parent, course_data):
        super().__init__(parent)
        self.title(f"{course_data[0]} View")
        self.geometry("640x720")
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        self.setup_ui(course_data)

    def setup_ui(self, course_data):
        subject, program, year_section = course_data
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        header_frame.pack(fill="x", padx=24, pady=(24, 0))
        ctk.CTkLabel(
            header_frame,
            text=subject,
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color="#111"
        ).pack(side="left", anchor="n")
        # Remove duplicate course/section label and only show one
        ctk.CTkLabel(
            self,
            text=f"Current: {subject} - {year_section}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#1E3A8A"
        ).pack(anchor="w", padx=24, pady=(8, 0))
        # Subheader (remove the duplicate course/section info)
        ctk.CTkLabel(
            self,
            text="S.Y 2025 - 2026",
            font=ctk.CTkFont(size=13),
            text_color="#222"
        ).pack(anchor="w", padx=24, pady=(0, 20))
        # Stat cards
        stat_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        stat_frame.pack(fill="x", padx=24, pady=(0, 0))
        card_data = [
            ("99", "Total Absents"),
            ("12%", "Attendance Rate"),
            ("10", "Number of Classes"),
            ("10", "Number of Classes")
        ]
        # First row: 3 cards
        row1 = ctk.CTkFrame(stat_frame, fg_color="#F5F5F5")
        row1.pack(fill="x")
        for value, label in card_data[:3]:
            card = ctk.CTkFrame(row1, fg_color="#fff", width=150, height=92, corner_radius=12)
            card.pack(side="left", padx=8, pady=0)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=13), text_color="#757575").pack(anchor="w", padx=16, pady=(0, 12))
        # Second row: 1 card on the left
        row2 = ctk.CTkFrame(stat_frame, fg_color="#F5F5F5")
        row2.pack(fill="x")
        card = ctk.CTkFrame(row2, fg_color="#fff", width=150, height=92, corner_radius=12)
        card.pack(side="left", padx=8, pady=8)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=card_data[3][0], font=ctk.CTkFont(size=22, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
        ctk.CTkLabel(card, text=card_data[3][1], font=ctk.CTkFont(size=13), text_color="#757575").pack(anchor="w", padx=16, pady=(0, 12))
        # Graph cards row
        graph_row = ctk.CTkFrame(self, fg_color="#F5F5F5")
        graph_row.pack(fill="both", expand=True, padx=24, pady=(24, 0))
        graph_row.grid_columnconfigure(0, weight=1)
        graph_row.grid_columnconfigure(1, weight=1)
        # Course Attendance Rate card
        graph1 = ctk.CTkFrame(graph_row, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        graph1.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        ctk.CTkLabel(graph1, text="Course Attendance Rate", font=ctk.CTkFont(size=15, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
        ctk.CTkLabel(graph1, text="graph here", font=ctk.CTkFont(size=13), text_color="#757575", fg_color="#fff").pack(expand=True, fill="both", padx=16, pady=16)
        # Monthly Attendance card
        graph2 = ctk.CTkFrame(graph_row, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        graph2.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=0)
        ctk.CTkLabel(graph2, text="Monthly Attendance", font=ctk.CTkFont(size=15, weight="bold"), text_color="#222").pack(anchor="w", padx=16, pady=(16, 0))
        ctk.CTkLabel(graph2, text="graph here", font=ctk.CTkFont(size=13), text_color="#757575", fg_color="#fff").pack(expand=True, fill="both", padx=16, pady=16)

class CoursesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.setup_ui()

    def setup_ui(self):
        # Top bar for the DateTimePill
        topbar = ctk.CTkFrame(self, fg_color="transparent")
        topbar.pack(fill="x", pady=(10, 0), padx=10)
        topbar.grid_columnconfigure(0, weight=1)
        DateTimePill(topbar).grid(row=0, column=1, sticky="e")

        # Header with 'Courses' label
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            header_frame,
            text="Courses",
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
            command=self.create_course
        )
        create_btn.pack(side="right", padx=(0, 0))

        # Table
        table_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Columns: Course Subject, Program, Year & Section, Actions
        columns = ["Course Subject", "Program", "Year & Section", "Actions"]
        col_widths = [70, 15, 15, 1]  # Course Subject takes 70%, Program and Year & Section each take 15%, Actions takes minimal space
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

        # Sample data: (Course Subject, Program, Year & Section)
        sample_data = [
            ("Ethics 101", "BSIT", "1st Year - 1-1"),
            ("Programming 1", "BSCS", "2nd Year - 2-3"),
            ("Data Structures", "BSIT", "3rd Year - 3-2"),
            ("Capstone", "BSIS", "4th Year - 4-1"),
        ]

        for idx, (subject, program, year_section) in enumerate(sample_data, start=1):
            # Course Subject
            ctk.CTkLabel(table_frame, text=subject, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color="#fff", anchor="w").grid(row=idx, column=0, sticky="nsew", padx=10, pady=6)
            # Program
            ctk.CTkLabel(table_frame, text=program, font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color="#fff", anchor="w").grid(row=idx, column=1, sticky="nsew", padx=10, pady=6)
            # Year & Section
            ctk.CTkLabel(table_frame, text=year_section, font=ctk.CTkFont(size=13), text_color="#222",
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
                command=lambda choice, data=(subject, program, year_section): self.handle_action(choice, data)
            )
            action_menu.grid(row=idx, column=3, sticky="w", padx=10, pady=6)

    def show_filter_popup(self):
        FilterPopup(self)

    def handle_action(self, action, data):
        if action == "Delete":
            def on_delete():
                root = self.winfo_toplevel()  # Get root window
                SuccessModal(root)  # Show success modal
            DeleteModal(self, on_delete=on_delete)
        elif action == "Edit":
            CourseEditPopup(self, data)
        elif action == "View":
            CourseViewPopup(self, data)
        else:
            print(f"{action} {data}")

    def create_course(self):
        CourseCreatePopup(self) 