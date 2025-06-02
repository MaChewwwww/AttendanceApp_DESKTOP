import customtkinter as ctk
import tkinter as tk
import traceback
from tkinter import messagebox
from PIL import Image, ImageTk
import io
import base64
from app.ui.admin.components.sidebar import DateTimePill  # adjust path if needed
from app.db_manager import DatabaseManager

# Import separated modal classes
from .users_view import UsersViewModal
from .users_edit import UsersEditModal
from .users_delete import UsersDeleteModal
from .users_add import UsersAddModal
from .users_modals import FacialRecognitionPopup

class FilterPopup(ctk.CTkToplevel):
    def __init__(self, parent, user_type="student"):
        super().__init__(parent)
        self.parent_view = parent
        self.user_type = user_type  # "student" or "faculty"
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
        
        # Initialize filter variables
        self.filters = {}
        
        # Get current filter values from parent
        current_filters = self.parent_view.current_filters.get(self.user_type, {})
        
        if self.user_type == "student":
            # Year filter
            ctk.CTkLabel(filter_frame, text="Year", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
            year_var = tk.StringVar(value=current_filters.get('year', 'All'))
            self.filters['year'] = year_var
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
            section_var = tk.StringVar(value=current_filters.get('section', 'All'))
            self.filters['section'] = section_var
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
            programs_var = tk.StringVar(value=current_filters.get('program', 'All'))
            self.filters['program'] = programs_var
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
            
            # Status filter
            ctk.CTkLabel(filter_frame, text="Status", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
            status_var = tk.StringVar(value=current_filters.get('status', 'All'))
            self.filters['status'] = status_var
            status_options = ["All", "Enrolled", "Graduated", "Dropout", "On Leave", "Suspended"]
            status_menu = ctk.CTkOptionMenu(
                filter_frame,
                values=status_options,
                variable=status_var,
                fg_color="#F3F4F6",
                text_color="#222",
                button_color="#E5E7EB",
                button_hover_color="#D1D5DB",
                dropdown_fg_color="#fff",
                dropdown_hover_color="#E5E7EB",
                dropdown_text_color="#222"
            )
            status_menu.pack(fill="x", pady=(0, 15))
        
        else:
            # Role filter
            ctk.CTkLabel(filter_frame, text="Role", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
            role_var = tk.StringVar(value=current_filters.get('role', 'All'))
            self.filters['role'] = role_var
            role_options = ["All", "Faculty", "Admin"]
            role_menu = ctk.CTkOptionMenu(
                filter_frame,
                values=role_options,
                variable=role_var,
                fg_color="#F3F4F6",
                text_color="#222",
                button_color="#E5E7EB",
                button_hover_color="#D1D5DB",
                dropdown_fg_color="#fff",
                dropdown_hover_color="#E5E7EB",
                dropdown_text_color="#222"
            )
            role_menu.pack(fill="x", pady=(0, 15))
            
            # Status filter
            ctk.CTkLabel(filter_frame, text="Status", font=ctk.CTkFont(weight="bold"), text_color="black").pack(anchor="w", pady=(0, 5))
            status_var = tk.StringVar(value=current_filters.get('status', 'All'))
            self.filters['status'] = status_var
            status_options = ["All", "Active", "Inactive", "Retired", "Probationary", "Tenure Track", "Tenured"]
            status_menu = ctk.CTkOptionMenu(
                filter_frame,
                values=status_options,
                variable=status_var,
                fg_color="#F3F4F6",
                text_color="#222",
                button_color="#E5E7EB",
                button_hover_color="#D1D5DB",
                dropdown_fg_color="#fff",
                dropdown_hover_color="#E5E7EB",
                dropdown_text_color="#222"
            )
            status_menu.pack(fill="x", pady=(0, 15))
        
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
        """Apply filters and update the parent view"""
        filter_values = {}
        for key, var in self.filters.items():
            value = var.get()
            if value != "All":
                filter_values[key] = value
        
        # Apply filters to parent view
        self.parent_view.apply_filters(filter_values, self.user_type)
        self.destroy()
    
    def reset_filters(self):
        """Reset all filters to default values"""
        for var in self.filters.values():
            var.set("All")
        
        # Apply reset filters
        self.parent_view.reset_filters(self.user_type)
        self.destroy()

class UsersView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = DatabaseManager()
        self.all_users = []
        self.students_data = []
        self.faculty_data = []
        
        # Filter state
        self.current_filters = {
            'student': {},
            'faculty': {}
        }
        self.current_search = {
            'student': "",
            'faculty': ""
        }
        
        # Pagination settings
        self.students_per_page = 10
        self.faculty_per_page = 10
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
        """Load initial users data from database"""
        # Load all data initially (no filters)
        self.load_filtered_data()

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
            # Smooth students tab activation with staggered animation
            self.animate_button_activation(self.students_tab_btn, True)
            self.animate_button_activation(self.faculty_tab_btn, False)
            # Delay content switch for smoother transition
            self.after(150, self.show_students_tab)
        else:
            # Smooth faculty tab activation with staggered animation
            self.animate_button_activation(self.faculty_tab_btn, True)
            self.animate_button_activation(self.students_tab_btn, False)
            # Delay content switch for smoother transition
            self.after(150, self.show_faculty_tab)

    def animate_button_activation(self, button, is_active):
        """Smooth animation for tab button state changes with multiple steps"""
        if is_active:
            # Multi-step activation animation
            button.configure(fg_color="#3B82F6")
            self.after(30, lambda: button.configure(fg_color="#2563EB"))
            self.after(60, lambda: button.configure(
                text_color="#FFFFFF",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                border_width=0
            ))
            self.after(90, lambda: button.configure(hover_color="#3B82F6"))
        else:
            # Multi-step deactivation animation
            button.configure(fg_color="#F1F5F9")
            self.after(20, lambda: button.configure(fg_color="#F8FAFC"))
            self.after(40, lambda: button.configure(fg_color="#FFFFFF"))
            self.after(60, lambda: button.configure(
                text_color="#64748B",
                font=ctk.CTkFont(family="Inter", size=13, weight="normal"),
                border_width=1,
                border_color="#E2E8F0"
            ))
            self.after(80, lambda: button.configure(hover_color="#F8FAFC"))

    def show_students_tab(self):
        """Show students tab content with fade-in effect"""
        # Hide faculty content first
        self.faculty_content.pack_forget()
        
        # Add a slight delay and fade-in effect for students content
        self.after(50, lambda: self.students_content.pack(fill="both", expand=True))

    def show_faculty_tab(self):
        """Show faculty tab content with fade-in effect"""
        # Hide students content first
        self.students_content.pack_forget()
        
        # Add a slight delay and fade-in effect for faculty content
        self.after(50, lambda: self.faculty_content.pack(fill="both", expand=True))

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

    def setup_students_tab(self, parent):
        # Search and filter bar
        search_bar_container = ctk.CTkFrame(parent, fg_color="#F0F0F0")
        search_bar_container.pack(pady=(0, 10), padx=0, fill="x")

        # Search entry with icon and clear button
        search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        
        self.student_search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="Search students...", width=160, fg_color="#fff",
                                    border_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=15), height=28)
        self.student_search_entry.pack(side="left", padx=(2, 0), pady=4)
        
        # Clear search button (x icon) - initially hidden
        self.student_clear_search_btn = ctk.CTkButton(
            search_entry_frame,
            text="✕",
            width=20,
            height=20,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color="#757575",
            hover_color="#F3F4F6",
            border_width=0,
            command=lambda: self.clear_search('student')
        )
        
        # Set current search value if it exists and show/hide clear button
        current_search = self.current_search.get('student', "")
        if current_search:
            self.student_search_entry.insert(0, current_search)
            self.student_clear_search_btn.pack(side="right", padx=(0, 8), pady=4)
        
        # Bind search functionality to Enter key and text changes
        self.student_search_entry.bind('<Return>', lambda e: self.on_search_change('student', self.student_search_entry.get()))
        self.student_search_entry.bind('<KeyRelease>', lambda e: self.update_search_clear_button('student'))

        # Filter button container for active state detection
        filter_container = ctk.CTkFrame(search_bar_container, fg_color="transparent")
        filter_container.pack(side="left", padx=0, pady=0)
        
        # Check if filters are active OR if there's a search term
        has_active_filters = any(v != "All" and v != "" for v in self.current_filters.get('student', {}).values())
        has_search = bool(self.current_search.get('student', "").strip())
        is_active = has_active_filters or has_search
        
        # Filter button (flush, no corner radius, border on all sides, same height)
        filter_btn = ctk.CTkButton(
            filter_container,
            text="Filters",
            width=80,
            height=36,
            fg_color="#1E3A8A" if is_active else "#fff",
            text_color="#fff" if is_active else "#757575",
            hover_color="#1D4ED8" if is_active else "#F3F4F6",
            border_width=1,
            border_color="#1E3A8A" if is_active else "#BDBDBD",
            corner_radius=0,
            font=ctk.CTkFont(size=13),
            command=lambda: FilterPopup(self, "student")
        )
        filter_btn.pack(side="left")
        
        # Clear filters button (x icon) - show if filters are active OR search is active
        if is_active:
            clear_filters_btn = ctk.CTkButton(
                filter_container,
                text="✕",
                width=20,
                height=20,
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                text_color="#1E3A8A",
                hover_color="#F3F4F6",
                border_width=0,
                command=lambda: self.reset_filters('student')
            )
            clear_filters_btn.pack(side="left", padx=(5, 0))

        # Actions container (Add and Export buttons) - moved to right
        actions_container = ctk.CTkFrame(search_bar_container, fg_color="transparent")
        actions_container.pack(side="right", padx=(10, 0), pady=0)
        
        # Export button (right)
        export_btn = ctk.CTkButton(
            actions_container,
            text="📊 Export",
            width=100,
            height=36,
            fg_color="#3B82F6",
            text_color="#fff",
            hover_color="#2563EB",
            border_width=0,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.export_students()
        )
        export_btn.pack(side="right")
        
        # Add Student button (left of export)
        add_btn = ctk.CTkButton(
            actions_container,
            text="+ Add Student",
            width=120,
            height=36,
            fg_color="#22C55E",
            text_color="#fff",
            hover_color="#16A34A",
            border_width=0,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: UsersAddModal(self, "student")
        )
        add_btn.pack(side="right", padx=(0, 8))

        # Table
        table_frame = ctk.CTkFrame(parent, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=0, pady=(10, 5))

        # Columns (removed Photo column)
        columns = ["Student Name", "Year", "Section", "Program", "Status", "Actions"]
        col_widths = [5, 2, 2, 3, 2, 2]  # More balanced column widths
        for i, weight in enumerate(col_widths):
            table_frame.grid_columnconfigure(i, weight=weight)

        # Header row with proper alignment
        for i, col in enumerate(columns):
            header_label = ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#374151",
                anchor="w"
            )
            header_label.grid(row=0, column=i, sticky="ew", padx=(15, 5), pady=8)

        # Use simplified data processing
        data_to_display = []
        
        if self.students_data:
            current_page_data = self.get_students_for_page(self.current_students_page)
            
            for i, student in enumerate(current_page_data):
                # Handle program display - show "N/A" only if program is null
                program_display = student.get('program_name', '') or "N/A"
                
                # Handle section display - show actual section or "N/A" independently
                section_display = student.get('section_name', '') or "N/A"
                
                # Handle year display - extract from section if available, otherwise "N/A"
                year_display = "N/A"
                if student.get('section_name'):
                    section_name = student['section_name']
                    if '-' in section_name:
                        year_num = section_name.split('-')[0]
                        year_mapping = {'1': '1st Year', '2': '2nd Year', '3': '3rd Year', '4': '4th Year'}
                        year_display = year_mapping.get(year_num, "N/A")
                
                data_to_display.append({
                    'name': f"{student.get('first_name', '')} {student.get('last_name', '')}",
                    'year': year_display,
                    'section': section_display,
                    'program': program_display,
                    'status': student.get('status_name', 'No Status'),
                    'data': student
                })

        # Display message if no data
        if not data_to_display:
            no_data_label = ctk.CTkLabel(
                table_frame,
                text="No students found matching your criteria",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            )
            no_data_label.grid(row=1, column=0, columnspan=len(columns), pady=40)
        else:
            # Display student data
            for i, student_data in enumerate(data_to_display):
                row = i + 1
                
                # Student Name
                name_label = ctk.CTkLabel(table_frame, text=student_data['name'], anchor="w", font=ctk.CTkFont(size=12), text_color="#111827")
                name_label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=3)
                
                # Year
                year_label = ctk.CTkLabel(table_frame, text=student_data['year'], anchor="w", font=ctk.CTkFont(size=12), text_color="#111827")
                year_label.grid(row=row, column=1, sticky="w", padx=(15, 5), pady=3)
                
                # Section
                section_label = ctk.CTkLabel(table_frame, text=student_data['section'], anchor="w", font=ctk.CTkFont(size=12), text_color="#111827")
                section_label.grid(row=row, column=2, sticky="w", padx=(15, 5), pady=3)
                
                # Program
                program_label = ctk.CTkLabel(table_frame, text=student_data['program'], anchor="w", font=ctk.CTkFont(size=12), text_color="#111827")
                program_label.grid(row=row, column=3, sticky="w", padx=(15, 5), pady=3)
                
                # Status with color
                self.create_status_badge(table_frame, student_data['status'], row, 4)
                
                # Actions dropdown
                action_var = tk.StringVar(value="Actions")
                actions = ["View", "Edit", "Delete"]
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
                    command=lambda choice, data=student_data['data']: self.handle_action(choice, data)
                )
                action_menu.grid(row=row, column=5, sticky="w", padx=(15, 5), pady=6)

        # Add pagination controls
        self.add_students_pagination(parent)

    def setup_faculty_tab(self, parent):
        # Search and filter bar for faculty
        search_bar_container = ctk.CTkFrame(parent, fg_color="#F0F0F0")
        search_bar_container.pack(pady=(0, 10), padx=0, fill="x")

        # Search entry with icon and clear button
        search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        
        self.faculty_search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="Search faculty...", width=160, fg_color="#fff",
                                    border_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=15), height=28)
        self.faculty_search_entry.pack(side="left", padx=(2, 0), pady=4)
        
        # Clear search button (x icon) - initially hidden
        self.faculty_clear_search_btn = ctk.CTkButton(
            search_entry_frame,
            text="✕",
            width=20,
            height=20,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color="#757575",
            hover_color="#F3F4F6",
            border_width=0,
            command=lambda: self.clear_search('faculty')
        )
        
        # Set current search value if it exists and show/hide clear button
        current_search = self.current_search.get('faculty', "")
        if current_search:
            self.faculty_search_entry.insert(0, current_search)
            self.faculty_clear_search_btn.pack(side="right", padx=(0, 8), pady=4)
        
        # Bind search functionality to Enter key and text changes
        self.faculty_search_entry.bind('<Return>', lambda e: self.on_search_change('faculty', self.faculty_search_entry.get()))
        self.faculty_search_entry.bind('<KeyRelease>', lambda e: self.update_search_clear_button('faculty'))
        
        # Filter button container for active state detection
        filter_container = ctk.CTkFrame(search_bar_container, fg_color="transparent")
        filter_container.pack(side="left", padx=0, pady=0)
        
        # Check if filters are active OR if there's a search term
        has_active_filters = any(v != "All" and v != "" for v in self.current_filters.get('faculty', {}).values())
        has_search = bool(self.current_search.get('faculty', "").strip())
        is_active = has_active_filters or has_search
        
        # Filter button (flush, no corner radius, border on all sides, same height)
        filter_btn = ctk.CTkButton(
            filter_container,
            text="Filters",
            width=80,
            height=36,
            fg_color="#1E3A8A" if is_active else "#fff",
            text_color="#fff" if is_active else "#757575",
            hover_color="#1D4ED8" if is_active else "#F3F4F6",
            border_width=1,
            border_color="#1E3A8A" if is_active else "#BDBDBD",
            corner_radius=0,
            font=ctk.CTkFont(size=13),
            command=lambda: FilterPopup(self, "faculty")
        )
        filter_btn.pack(side="left")
        
        # Clear filters button (x icon) - show if filters are active OR search is active
        if is_active:
            clear_filters_btn = ctk.CTkButton(
                filter_container,
                text="✕",
                width=20,
                height=20,
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                text_color="#1E3A8A",
                hover_color="#F3F4F6",
                border_width=0,
                command=lambda: self.reset_filters('faculty')
            )
            clear_filters_btn.pack(side="left", padx=(5, 0))

        # Actions container (Add and Export buttons) - moved to right
        actions_container = ctk.CTkFrame(search_bar_container, fg_color="transparent")
        actions_container.pack(side="right", padx=(10, 0), pady=0)
        
        # Export button (right)
        export_btn = ctk.CTkButton(
            actions_container,
            text="📊 Export",
            width=100,
            height=36,
            fg_color="#3B82F6",
            text_color="#fff",
            hover_color="#2563EB",
            border_width=0,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.export_faculty()
        )
        export_btn.pack(side="right")
        
        # Add Faculty button (left of export)
        add_btn = ctk.CTkButton(
            actions_container,
            text="+ Add Faculty",
            width=120,
            height=36,
            fg_color="#22C55E",
            text_color="#fff",
            hover_color="#16A34A",
            border_width=0,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: UsersAddModal(self, "faculty")
        )
        add_btn.pack(side="right", padx=(0, 8))

        # Faculty table
        table_frame = ctk.CTkFrame(parent, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=0, pady=(10, 5))

        # Columns for faculty (removed Photo column)
        columns = ["Faculty Name", "Employee Number", "Email", "Role", "Status", "Actions"]
        col_widths = [4, 3, 4, 2, 2, 2]  # More balanced column widths
        for i, weight in enumerate(col_widths):
            table_frame.grid_columnconfigure(i, weight=weight)

        # Header row with proper alignment
        for i, col in enumerate(columns):
            header_label = ctk.CTkLabel(
                table_frame,
                text=col,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#374151",
                anchor="w"
            )
            header_label.grid(row=0, column=i, sticky="ew", padx=(15, 5), pady=8)

        # Use simplified data processing
        data_to_display = []
        
        if self.faculty_data:
            current_page_data = self.get_faculty_for_page(self.current_faculty_page)
            
            for i, faculty in enumerate(current_page_data):
                data_to_display.append({
                    'name': f"{faculty.get('first_name', '')} {faculty.get('last_name', '')}",
                    'employee_number': faculty.get('employee_number', 'N/A'),
                    'email': faculty.get('email', ''),
                    'role': faculty.get('role', 'Faculty'),
                    'status': faculty.get('status_name', 'No Status'),
                    'data': faculty
                })

        # Display message if no data
        if not data_to_display:
            no_data_label = ctk.CTkLabel(
                table_frame,
                text="No faculty found matching your criteria",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            )
            no_data_label.grid(row=1, column=0, columnspan=len(columns), pady=40)
        else:
            # Display faculty data
            for i, faculty_data in enumerate(data_to_display):
                row = i + 1
                
                # Faculty Name
                name_label = ctk.CTkLabel(table_frame, text=faculty_data['name'], anchor="w", font=ctk.CTkFont(size=12), text_color="#111827")
                name_label.grid(row=row, column=0, sticky="w", padx=(15, 5), pady=3)
                
                # Employee Number
                emp_label = ctk.CTkLabel(table_frame, text=faculty_data['employee_number'], anchor="w", font=ctk.CTkFont(size=12), text_color="#111827")
                emp_label.grid(row=row, column=1, sticky="w", padx=(15, 5), pady=3)
                
                # Email
                email_label = ctk.CTkLabel(table_frame, text=faculty_data['email'], anchor="w", font=ctk.CTkFont(size=12), text_color="#111827")
                email_label.grid(row=row, column=2, sticky="w", padx=(15, 5), pady=3)
                
                # Role
                role_label = ctk.CTkLabel(table_frame, text=faculty_data['role'], anchor="w", font=ctk.CTkFont(size=12), text_color="#111827")
                role_label.grid(row=row, column=3, sticky="w", padx=(15, 5), pady=3)
                
                # Status with color
                self.create_status_badge(table_frame, faculty_data['status'], row, 4)
                
                # Actions - Check if user is Admin
                if faculty_data['role'].lower() == 'admin':
                    # For admins, show "Not Available" text instead of dropdown
                    not_available_label = ctk.CTkLabel(
                        table_frame,
                        text="Not Available",
                        anchor="w",
                        font=ctk.CTkFont(size=12),
                        text_color="#9CA3AF"
                    )
                    not_available_label.grid(row=row, column=5, sticky="w", padx=(15, 5), pady=3)
                else:
                    # For non-admin users, show actions dropdown
                    action_var = tk.StringVar(value="Actions")
                    actions = ["View", "Edit", "Delete"]
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
                        command=lambda choice, data=faculty_data['data']: self.handle_faculty_action(choice, data)
                    )
                    action_menu.grid(row=row, column=5, sticky="w", padx=(15, 5), pady=6)

        # Add pagination controls
        self.add_faculty_pagination(parent)

    def create_status_badge(self, parent, status, row, column):
        """Create a colored status text with proper alignment"""
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
        status_label.grid(row=row, column=column, sticky="w", padx=(15, 5), pady=3)

    def handle_action(self, action, data):
        """Handle action selection for students"""
        if action == "View":
            UsersViewModal(self, data, "student")
        elif action == "Edit":
            UsersEditModal(self, data, "student")
        elif action == "Delete":
            UsersDeleteModal(self, data, "student")

    def handle_faculty_action(self, action, data):
        """Handle action selection for faculty"""
        if action == "View":
            UsersViewModal(self, data, "faculty")
        elif action == "Edit":
            UsersEditModal(self, data, "faculty")
        elif action == "Delete":
            UsersDeleteModal(self, data, "faculty")

    def apply_filters(self, filter_values, user_type):
        """Apply filters to the specified user type"""
        self.current_filters[user_type] = filter_values
        
        # Reset to first page when applying filters
        if user_type == 'student':
            self.current_students_page = 1
        else:
            self.current_faculty_page = 1
        
        # Reload data with filters
        self.load_filtered_data()

    def reset_filters(self, user_type):
        """Reset filters for the specified user type"""
        self.current_filters[user_type] = {}
        self.current_search[user_type] = ""
        
        # Reset to first page
        if user_type == 'student':
            self.current_students_page = 1
        else:
            self.current_faculty_page = 1
        
        # Clear search entries
        if hasattr(self, 'student_search_entry') and user_type == 'student':
            self.student_search_entry.delete(0, tk.END)
        elif hasattr(self, 'faculty_search_entry') and user_type == 'faculty':
            self.faculty_search_entry.delete(0, tk.END)
        
        # Reload data without filters
        self.load_filtered_data()

    def on_search_change(self, user_type, search_term):
        """Handle search term changes"""
        self.current_search[user_type] = search_term
        
        # Reset to first page when searching
        if user_type == 'student':
            self.current_students_page = 1
        else:
            self.current_faculty_page = 1
        
        # Reload data with search
        self.load_filtered_data()

    def load_filtered_data(self):
        """Load data with current filters and search terms applied"""
        try:
            # Load filtered students using db_manager method
            student_filters = self.current_filters.get('student', {})
            success, students = self.db_manager.get_students_with_filters(
                search_term=self.current_search.get('student', ""),
                year_filter=student_filters.get('year', ""),
                section_filter=student_filters.get('section', ""),
                program_filter=student_filters.get('program', ""),
                status_filter=student_filters.get('status', "")
            )
            
            if success:
                self.students_data = students
            else:
                print(f"Error loading students: {students}")
                self.students_data = []
            
            # Load filtered faculty using db_manager method
            faculty_filters = self.current_filters.get('faculty', {})
            success, faculty = self.db_manager.get_faculty_with_filters(
                search_term=self.current_search.get('faculty', ""),
                status_filter=faculty_filters.get('status', ""),
                role_filter=faculty_filters.get('role', "")
            )
            
            if success:
                self.faculty_data = faculty
            else:
                print(f"Error loading faculty: {faculty}")
                self.faculty_data = []
            
            # Refresh tables
            self.refresh_students_table()
            self.refresh_faculty_table()
            
        except Exception as e:
            print(f"Error in load_filtered_data: {e}")
            traceback.print_exc()

    def update_search_clear_button(self, user_type):
        """Update visibility of clear search button"""
        if user_type == 'student':
            search_entry = getattr(self, 'student_search_entry', None)
            clear_btn = getattr(self, 'student_clear_search_btn', None)
        else:
            search_entry = getattr(self, 'faculty_search_entry', None)
            clear_btn = getattr(self, 'faculty_clear_search_btn', None)
        
        if search_entry and clear_btn:
            current_text = search_entry.get().strip()
            if current_text:
                clear_btn.pack(side="left", padx=(2, 8), pady=4)
            else:
                clear_btn.pack_forget()

    def clear_search(self, user_type):
        """Clear search for specified user type"""
        if user_type == 'student':
            if hasattr(self, 'student_search_entry'):
                self.student_search_entry.delete(0, tk.END)
        else:
            if hasattr(self, 'faculty_search_entry'):
                self.faculty_search_entry.delete(0, tk.END)
        
        # Trigger search change
        self.on_search_change(user_type, "")

    def add_students_pagination(self, parent):
        """Add pagination controls for students"""
        pagination_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pagination_frame.pack(fill="x", pady=(10, 0))
        
        # Previous button
        prev_btn = ctk.CTkButton(
            pagination_frame,
            text="← Previous",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#F3F4F6" if self.current_students_page == 1 else "#1E3A8A",
            text_color="#6B7280" if self.current_students_page == 1 else "#fff",
            hover_color="#E5E7EB" if self.current_students_page == 1 else "#1D4ED8",
            state="disabled" if self.current_students_page == 1 else "normal",
            command=lambda: self.change_students_page("prev")
        )
        prev_btn.pack(side="left")
        
        # Page info
        total_pages = self.get_total_students_pages()
        page_info = ctk.CTkLabel(
            pagination_frame,
            text=f"Page {self.current_students_page} of {total_pages}",
            font=ctk.CTkFont(size=12),
            text_color="#6B7280"
        )
        page_info.pack(side="left", padx=20)
        
        # Next button
        next_btn = ctk.CTkButton(
            pagination_frame,
            text="Next →",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#F3F4F6" if self.current_students_page == total_pages else "#1E3A8A",
            text_color="#6B7280" if self.current_students_page == total_pages else "#fff",
            hover_color="#E5E7EB" if self.current_students_page == total_pages else "#1D4ED8",
            state="disabled" if self.current_students_page == total_pages else "normal",
            command=lambda: self.change_students_page("next")
        )
        next_btn.pack(side="left")

    def add_faculty_pagination(self, parent):
        """Add pagination controls for faculty"""
        pagination_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pagination_frame.pack(fill="x", pady=(10, 0))
        
        # Previous button
        prev_btn = ctk.CTkButton(
            pagination_frame,
            text="← Previous",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#F3F4F6" if self.current_faculty_page == 1 else "#1E3A8A",
            text_color="#6B7280" if self.current_faculty_page == 1 else "#fff",
            hover_color="#E5E7EB" if self.current_faculty_page == 1 else "#1D4ED8",
            state="disabled" if self.current_faculty_page == 1 else "normal",
            command=lambda: self.change_faculty_page("prev")
        )
        prev_btn.pack(side="left")
        
        # Page info
        total_pages = self.get_total_faculty_pages()
        page_info = ctk.CTkLabel(
            pagination_frame,
            text=f"Page {self.current_faculty_page} of {total_pages}",
            font=ctk.CTkFont(size=12),
            text_color="#6B7280"
        )
        page_info.pack(side="left", padx=20)
        
        # Next button
        next_btn = ctk.CTkButton(
            pagination_frame,
            text="Next →",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#F3F4F6" if self.current_faculty_page == total_pages else "#1E3A8A",
            text_color="#6B7280" if self.current_faculty_page == total_pages else "#fff",
            hover_color="#E5E7EB" if self.current_faculty_page == total_pages else "#1D4ED8",
            state="disabled" if self.current_faculty_page == total_pages else "normal",
            command=lambda: self.change_faculty_page("next")
        )
        next_btn.pack(side="left")

    def export_students(self):
        """Export students data to CSV"""
        try:
            import csv
            from tkinter import filedialog
            import os
            from datetime import datetime
            
            # Ask user where to save the file
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            # Export current filtered/searched data
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Student Name', 'Student Number', 'Email', 'Year', 'Section', 'Program', 'Status', 'Contact Number', 'Date of Birth'])
                
                # Write data
                for student in self.students_data:
                    # Handle section display
                    section_display = student.get('section_name', '') or "N/A"
                    
                    # Handle year display
                    year_display = "N/A"
                    if student.get('section_name'):
                        section_name = student['section_name']
                        if '-' in section_name:
                            year_num = section_name.split('-')[0]
                            year_mapping = {'1': '1st Year', '2': '2nd Year', '3': '3rd Year', '4': '4th Year'}
                            year_display = year_mapping.get(year_num, "N/A")
                    
                    writer.writerow([
                        f"{student.get('first_name', '')} {student.get('last_name', '')}",
                        student.get('student_number', ''),
                        student.get('email', ''),
                        year_display,
                        section_display,
                        student.get('program_name', '') or "N/A",
                        student.get('status_name', 'No Status'),
                        student.get('contact_number', ''),
                        student.get('date_of_birth', '')
                    ])
            
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Export Successful", f"Students data exported successfully to:\n{filename}")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"Failed to export students data:\n{str(e)}")

    def export_faculty(self):
        """Export faculty data to CSV"""
        try:
            import csv
            from tkinter import filedialog
            import os
            from datetime import datetime
            
            # Ask user where to save the file
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=f"faculty_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            # Export current filtered/searched data
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Faculty Name', 'Employee Number', 'Email', 'Role', 'Status', 'Contact Number', 'Date of Birth'])
                
                # Write data
                for faculty in self.faculty_data:
                    writer.writerow([
                        f"{faculty.get('first_name', '')} {faculty.get('last_name', '')}",
                        faculty.get('employee_number', 'N/A'),
                        faculty.get('email', ''),
                        faculty.get('role', 'Faculty'),
                        faculty.get('status_name', 'No Status'),
                        faculty.get('contact_number', ''),
                        faculty.get('date_of_birth', '')
                    ])
            
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Export Successful", f"Faculty data exported successfully to:\n{filename}")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"Failed to export faculty data:\n{str(e)}")