import customtkinter as ctk
import tkinter as tk

class SectionViewPopup(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, section_data):
        super().__init__(parent)
        self.db_manager = db_manager
        self.section_data = section_data
        self.title(f"Section View")
        self.geometry("640x720")
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        
        # Create main scrollable frame
        self.main_frame = ctk.CTkScrollableFrame(self, fg_color="#F5F5F5")
        self.main_frame.pack(fill="both", expand=True)
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        top_frame = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        top_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        section_name = self.section_data.get('name', 'N/A')
        program_acronym = self.section_data.get('program_acronym', 'N/A')
        
        ctk.CTkLabel(
            top_frame, 
            text=f"{program_acronym} {section_name}", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#000"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            top_frame, 
            text=f"S.Y 2025 - 2026", 
            font=ctk.CTkFont(size=13), 
            text_color="#222"
        ).pack(anchor="w")

        # Search and filter bar
        search_bar_container = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        search_bar_container.pack(pady=(0, 10), padx=20, anchor="w")
        
        search_entry_frame = ctk.CTkFrame(
            search_bar_container, 
            fg_color="#fff", 
            border_color="#BDBDBD", 
            border_width=1, 
            corner_radius=0, 
            height=36
        )
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        
        search_icon = ctk.CTkLabel(
            search_entry_frame, 
            text="\U0001F50D", 
            font=ctk.CTkFont(size=16), 
            text_color="#757575", 
            fg_color="#fff", 
            width=28, 
            height=28
        )
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        
        self.search_entry = ctk.CTkEntry(
            search_entry_frame, 
            placeholder_text="Search students...", 
            width=160, 
            fg_color="#fff",
            border_color="#fff", 
            border_width=0, 
            text_color="#000", 
            font=ctk.CTkFont(size=15), 
            height=28
        )
        self.search_entry.pack(side="left", padx=(2, 8), pady=4)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)

        # Statistics cards
        stats_frame = ctk.CTkFrame(self.main_frame, fg_color="#F5F5F5")
        stats_frame.pack(fill="x", padx=20, pady=(10, 0))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        # Get section statistics
        section_id = self.section_data.get('id')
        stats = {}
        if self.db_manager and section_id:
            stats = self.db_manager.get_section_statistics(section_id)
        
        # Total Students Card
        students_card = ctk.CTkFrame(stats_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        students_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        ctk.CTkLabel(students_card, text="Total Students", font=ctk.CTkFont(size=12, weight="bold"), text_color="#666").pack(pady=(10, 0))
        ctk.CTkLabel(students_card, text=str(stats.get('total_students', 0)), font=ctk.CTkFont(size=24, weight="bold"), text_color="#222").pack(pady=(0, 10))

        # Total Courses Card
        courses_card = ctk.CTkFrame(stats_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        courses_card.grid(row=0, column=1, sticky="nsew", padx=2.5, pady=5)
        ctk.CTkLabel(courses_card, text="Total Courses", font=ctk.CTkFont(size=12, weight="bold"), text_color="#666").pack(pady=(10, 0))
        ctk.CTkLabel(courses_card, text=str(stats.get('total_courses', 0)), font=ctk.CTkFont(size=24, weight="bold"), text_color="#222").pack(pady=(0, 10))

        # Average Attendance Card
        attendance_card = ctk.CTkFrame(stats_frame, fg_color="#fff", corner_radius=12, border_width=1, border_color="#E5E7EB")
        attendance_card.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=5)
        ctk.CTkLabel(attendance_card, text="Avg. Attendance", font=ctk.CTkFont(size=12, weight="bold"), text_color="#666").pack(pady=(10, 0))
        ctk.CTkLabel(attendance_card, text=f"{stats.get('average_attendance', 0):.1f}%", font=ctk.CTkFont(size=24, weight="bold"), text_color="#222").pack(pady=(0, 10))

        # Students Table
        self.table_frame = ctk.CTkFrame(self.main_frame, fg_color="#fff", border_color="#E5E7EB", border_width=1, corner_radius=8)
        self.table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Table headers
        columns = ["Student Name", "Student Number", "Status", "Actions"]
        col_widths = [4, 3, 2, 2]
        for i, weight in enumerate(col_widths):
            self.table_frame.grid_columnconfigure(i, weight=weight)
        
        # Header row
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                self.table_frame, 
                text=col, 
                font=ctk.CTkFont(size=13, weight="bold"), 
                text_color="#000", 
                anchor="w"
            ).grid(row=0, column=i, padx=10, pady=8, sticky="w")
        
        # Load and display students
        self.load_students()

    def load_students(self):
        if not self.db_manager:
            return
            
        section_id = self.section_data.get('id')
        if not section_id:
            return
        
        search_term = self.search_entry.get() if hasattr(self, 'search_entry') else ""
        students = self.db_manager.get_section_students(section_id, search_term=search_term)
        
        # Clear existing rows (except header)
        for widget in self.table_frame.winfo_children():
            info = widget.grid_info()
            if info and info['row'] > 0:
                widget.destroy()
        
        # Add student rows
        for idx, student in enumerate(students, start=1):
            # Student Name
            full_name = f"{student['first_name']} {student['last_name']}"
            ctk.CTkLabel(
                self.table_frame, 
                text=full_name, 
                font=ctk.CTkFont(size=13), 
                text_color="#222",
                fg_color="#fff", 
                anchor="w"
            ).grid(row=idx, column=0, sticky="nsew", padx=10, pady=6)
            
            # Student Number
            ctk.CTkLabel(
                self.table_frame, 
                text=student['student_number'], 
                font=ctk.CTkFont(size=13), 
                text_color="#222",
                fg_color="#fff", 
                anchor="w"
            ).grid(row=idx, column=1, sticky="nsew", padx=10, pady=6)
            
            # Status
            ctk.CTkLabel(
                self.table_frame, 
                text=student['status_name'], 
                font=ctk.CTkFont(size=13), 
                text_color="#222",
                fg_color="#fff", 
                anchor="w"
            ).grid(row=idx, column=2, sticky="nsew", padx=10, pady=6)
            
            # Actions dropdown
            action_var = tk.StringVar(value="View")
            actions = ["View", "Edit"]
            action_menu = ctk.CTkOptionMenu(
                self.table_frame,
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
                command=lambda choice, student_data=student: self.handle_student_action(choice, student_data)
            )
            action_menu.grid(row=idx, column=3, sticky="w", padx=10, pady=6)

    def handle_student_action(self, action, student_data):
        if action == "View":
            # TODO: Open student details popup
            print(f"View student: {student_data}")
        elif action == "Edit":
            # TODO: Open student edit popup  
            print(f"Edit student: {student_data}")

    def on_search_change(self, event=None):
        # Reload students with search filter
        self.load_students()
