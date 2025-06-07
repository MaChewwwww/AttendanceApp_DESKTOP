import customtkinter as ctk
from app.ui.admin.components.sidebar import DateTimePill
from app.ui.admin.components.modals import DeleteModal, SuccessModal
from .courses_add import CreateCoursePopup
from .courses_edit import EditCoursePopup
from .courses_view import ViewCoursePopup
import tkinter as tk

class FilterPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Filter Courses")
        self.geometry("400x500")
        self.resizable(False, False)
        self.configure(fg_color="#fff")
        self.transient(parent)
        self.grab_set()
        self.center_window()
        self.setup_ui()
    
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
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
        self.program_var = tk.StringVar(value="All")
        program_options = ["All", "BSIT", "BSCS", "BSIS"]
        program_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=program_options,
            variable=self.program_var,
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
        self.year_var = tk.StringVar(value="All")
        year_options = ["All", "1st Year", "2nd Year", "3rd Year", "4th Year"]
        year_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=year_options,
            variable=self.year_var,
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
        self.section_var = tk.StringVar(value="All")
        section_options = ["All", "1-1", "1-2", "2-1", "2-2", "3-1", "3-2", "4-1", "4-2"]
        section_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=section_options,
            variable=self.section_var,
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

class CoursesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = None
        self.courses_data = []
        self.load_courses_data()
        self.setup_ui()

    def load_courses_data(self):
        """Load courses data from database"""
        try:
            from app.db_manager import DatabaseManager
            self.db_manager = DatabaseManager()
            success, courses = self.db_manager.get_courses()
            
            if success:
                self.courses_data = courses
            else:
                print(f"Error loading courses: {courses}")
                # Fallback to sample data
                self.courses_data = [
                    {"id": 1, "name": "Ethics 101", "program_name": "BSIT", "program_acronym": "BSIT"},
                    {"id": 2, "name": "Programming 1", "program_name": "BSCS", "program_acronym": "BSCS"},
                    {"id": 3, "name": "Data Structures", "program_name": "BSIT", "program_acronym": "BSIT"},
                    {"id": 4, "name": "Capstone", "program_name": "BSIS", "program_acronym": "BSIS"},
                ]
        except Exception as e:
            print(f"Error loading courses data: {e}")
            # Fallback to sample data
            self.courses_data = [
                {"id": 1, "name": "Ethics 101", "program_name": "BSIT", "program_acronym": "BSIT"},
                {"id": 2, "name": "Programming 1", "program_name": "BSCS", "program_acronym": "BSCS"},
                {"id": 3, "name": "Data Structures", "program_name": "BSIT", "program_acronym": "BSIT"},
                {"id": 4, "name": "Capstone", "program_name": "BSIS", "program_acronym": "BSIS"},
            ]

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

        # Display courses data
        for idx, course in enumerate(self.courses_data, start=1):
            # Course Subject
            ctk.CTkLabel(table_frame, text=course['name'], font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color="#fff", anchor="w").grid(row=idx, column=0, sticky="nsew", padx=10, pady=6)
            # Program
            ctk.CTkLabel(table_frame, text=course['program_acronym'], font=ctk.CTkFont(size=13), text_color="#222",
                         fg_color="#fff", anchor="w").grid(row=idx, column=1, sticky="nsew", padx=10, pady=6)
            # Year & Section (placeholder)
            ctk.CTkLabel(table_frame, text="Multiple", font=ctk.CTkFont(size=13), text_color="#222",
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
                command=lambda choice, data=course: self.handle_action(choice, data)
            )
            action_menu.grid(row=idx, column=3, sticky="w", padx=10, pady=6)

    def show_filter_popup(self):
        FilterPopup(self)

    def handle_action(self, action, data):
        if action == "Delete":
            def on_delete():
                try:
                    if self.db_manager:
                        success, result = self.db_manager.delete_course(data['id'])
                        if success:
                            self.refresh_courses()
                            root = self.winfo_toplevel()
                            SuccessModal(root)
                        else:
                            print(f"Error deleting course: {result}")
                    else:
                        print("Database manager not available")
                except Exception as e:
                    print(f"Error deleting course: {e}")
            
            DeleteModal(self, on_delete=on_delete)
        elif action == "Edit":
            EditCoursePopup(self, data)
        elif action == "View":
            ViewCoursePopup(self, data)
        else:
            print(f"{action} {data}")

    def create_course(self):
        CreateCoursePopup(self)

    def refresh_courses(self):
        """Refresh the courses data and update the UI"""
        self.load_courses_data()
        # TODO: Refresh the table display
        print("Courses refreshed")