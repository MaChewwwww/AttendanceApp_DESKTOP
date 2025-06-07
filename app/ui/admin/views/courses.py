import customtkinter as ctk
from app.ui.admin.components.sidebar import DateTimePill
from app.ui.admin.components.modals import DeleteModal, SuccessModal
from .courses_add import CreateCoursePopup
from .courses_edit import EditCoursePopup
from .courses_view import ViewCoursePopup
from .courses_filter_selection import CoursesFilterSectionFactory
import tkinter as tk

class CoursesFilterPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_view = parent
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
        
        # Get current filter values from parent
        current_filters = self.parent_view.current_filters
        
        # Create filter section using factory
        self.filter_section = CoursesFilterSectionFactory.create_filter_section(
            filter_frame, 
            current_filters
        )
        
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
        filters = self.filter_section.get_filter_values()
        
        for key, var in filters.items():
            value = var.get().strip()
            if value and value != "All":
                filter_values[key] = value
        
        # Apply filters to parent view
        self.parent_view.apply_filters(filter_values)
        self.destroy()
    
    def reset_filters(self):
        """Reset all filters to default values"""
        filters = self.filter_section.get_filter_values()
        for var in filters.values():
            if hasattr(var, 'set'):
                var.set("All" if var.get() in ["All"] + [f for f in filters.values() if hasattr(f, 'get') and f.get() != var.get()] else "")
        
        # Apply reset filters
        self.parent_view.reset_filters()
        self.destroy()

class CoursesView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.db_manager = None
        self.courses_data = []
        self.filtered_courses_data = []
        
        # Filter state
        self.current_filters = {}
        self.current_search = ""
        
        # Pagination settings
        self.courses_per_page = 14  # Changed from 15 to 14
        self.current_page = 1
        
        # Setup UI first, then load data
        self.setup_ui()
        self.load_courses_data()

    def get_total_pages(self):
        """Calculate total pages for courses"""
        # Use filtered data instead of all data
        data_to_use = self.filtered_courses_data if hasattr(self, 'filtered_courses_data') else self.courses_data
        total_courses = len(data_to_use)
        return max(1, (total_courses + self.courses_per_page - 1) // self.courses_per_page)

    def get_courses_for_page(self, page):
        """Get courses data for specific page"""
        # Use filtered data instead of all data
        data_to_use = self.filtered_courses_data if hasattr(self, 'filtered_courses_data') else self.courses_data
        start_idx = (page - 1) * self.courses_per_page
        end_idx = start_idx + self.courses_per_page
        return data_to_use[start_idx:end_idx]

    def change_page(self, direction):
        """Change courses page"""
        total_pages = self.get_total_pages()
        if direction == "prev" and self.current_page > 1:
            self.current_page -= 1
        elif direction == "next" and self.current_page < total_pages:
            self.current_page += 1
        self.refresh_table()

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
                self.courses_data = []
        except Exception as e:
            print(f"Error loading courses data: {e}")
            self.courses_data = []
        
        # Apply current filters and search after loading
        self.apply_filters_and_search()

    def refresh_table(self):
        """Refresh the courses table with current data"""
        try:
            # Clear existing content and rebuild
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.setup_courses_table(self.content_frame)
        except Exception as e:
            print(f"Error refreshing courses table: {e}")

    def setup_ui(self):
        # Top bar with date pill
        topbar = ctk.CTkFrame(self, fg_color="transparent")
        topbar.pack(fill="x", pady=(10, 0), padx=10)
        topbar.grid_columnconfigure(0, weight=1)
        DateTimePill(topbar).grid(row=0, column=1, sticky="e")

        # Header
        ctk.CTkLabel(
            self,
            text="Courses",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="black"
        ).pack(anchor="w", padx=12, pady=(0, 10))

        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Setup courses table
        self.setup_courses_table(self.content_frame)

    def setup_courses_table(self, parent):
        # Search and filter bar
        search_bar_container = ctk.CTkFrame(parent, fg_color="#F0F0F0")
        search_bar_container.pack(pady=(0, 10), padx=0, fill="x")

        # Search entry with icon and clear button
        search_entry_frame = ctk.CTkFrame(search_bar_container, fg_color="#fff", border_color="#BDBDBD", border_width=1, corner_radius=0, height=36)
        search_entry_frame.pack(side="left", pady=0, padx=0)
        search_entry_frame.pack_propagate(False)
        search_icon = ctk.CTkLabel(search_entry_frame, text="\U0001F50D", font=ctk.CTkFont(size=16), text_color="#757575", fg_color="#fff", width=28, height=28)
        search_icon.pack(side="left", padx=(8, 0), pady=4)
        
        self.search_entry = ctk.CTkEntry(search_entry_frame, placeholder_text="Search courses...", width=160, fg_color="#fff",
                                    border_color="#fff", border_width=0, text_color="#222", font=ctk.CTkFont(size=15), height=28)
        self.search_entry.pack(side="left", padx=(2, 0), pady=4)
        
        # Clear search button (x icon) - initially hidden
        self.clear_search_btn = ctk.CTkButton(
            search_entry_frame,
            text="✕",
            width=20,
            height=20,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            text_color="#757575",
            hover_color="#F3F4F6",
            border_width=0,
            command=self.clear_search
        )
        
        # Set current search value if it exists and show/hide clear button
        if self.current_search:
            self.search_entry.insert(0, self.current_search)
            self.clear_search_btn.pack(side="right", padx=(0, 8), pady=2)
        
        # Bind search functionality to Enter key and text changes
        self.search_entry.bind('<Return>', lambda e: self.on_search_change(self.search_entry.get()))
        self.search_entry.bind('<KeyRelease>', lambda e: self.update_search_clear_button())

        # Filter and Sort button container
        filter_sort_container = ctk.CTkFrame(search_bar_container, fg_color="transparent")
        filter_sort_container.pack(side="left", padx=0, pady=0)
        
        # Check if filters are active OR if there's a search term
        has_active_filters = any(v != "All" and v != "" for v in self.current_filters.values())
        has_search = bool(self.current_search.strip())
        is_active = has_active_filters or has_search
        
        # Filter button (second position)
        filter_btn = ctk.CTkButton(
            filter_sort_container,
            text="Filters 🔽",
            width=95,
            height=36,
            fg_color="#1E3A8A" if is_active else "#fff",
            text_color="#fff" if is_active else "#757575",
            hover_color="#1D4ED8" if is_active else "#F3F4F6",
            border_width=1,
            border_color="#1E3A8A" if is_active else "#BDBDBD",
            corner_radius=0,
            font=ctk.CTkFont(size=13),
            command=self.show_filter_popup
        )
        filter_btn.pack(side="left", padx=(0, 0))
        
        # Check if sort is active (not default icon)
        is_sort_active = hasattr(self, 'sort_var') and self.sort_var.get() != "↕"
        
        # Sort dropdown container (third position) - change color based on sort state
        sort_container = ctk.CTkFrame(
            filter_sort_container,
            fg_color="#1E3A8A" if is_sort_active else "#fff",
            border_width=1,
            border_color="#1E3A8A" if is_sort_active else "#BDBDBD",
            corner_radius=0,
            height=36,
            width=40
        )
        sort_container.pack(side="left", padx=(0, 0))
        sort_container.pack_propagate(False)
        
        # Sort dropdown button with better icon
        self.sort_var = tk.StringVar(value="↕")
        sort_options = [
            "None",
            "Sort by Course Name (A-Z)", "Sort by Course Name (Z-A)",
            "Sort by Course Code (A-Z)", "Sort by Course Code (Z-A)",
            "Sort by Program (A-Z)", "Sort by Program (Z-A)"
        ]
        
        sort_btn = ctk.CTkOptionMenu(
            sort_container,
            values=sort_options,
            variable=self.sort_var,
            width=38,
            height=34,
            fg_color="#1E3A8A" if is_sort_active else "#fff",
            text_color="#fff" if is_sort_active else "#757575",
            button_color="#1E3A8A" if is_sort_active else "#fff",
            button_hover_color="#1D4ED8" if is_sort_active else "#F3F4F6",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            corner_radius=0,
            font=ctk.CTkFont(size=14),
            command=self.apply_sort
        )
        sort_btn.pack(padx=0, pady=1, fill="both", expand=True)
        
        # Clear filters button (fourth position) - show if filters are active OR search is active OR sort is active
        if is_active or is_sort_active:
            clear_filters_btn = ctk.CTkButton(
                filter_sort_container,
                text="✕",
                width=20,
                height=20,
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                text_color="#1E3A8A",
                hover_color="#F3F4F6",
                border_width=0,
                command=self.reset_filters
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
            command=self.export_courses
        )
        export_btn.pack(side="right")
        
        # Add Course button (left of export)
        add_btn = ctk.CTkButton(
            actions_container,
            text="+ Add Course",
            width=120,
            height=36,
            fg_color="#22C55E",
            text_color="#fff",
            hover_color="#16A34A",
            border_width=0,
            corner_radius=6,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.create_course
        )
        add_btn.pack(side="right", padx=(0, 8))

        # Table
        table_frame = ctk.CTkFrame(parent, fg_color="#fff", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_frame.pack(fill="both", expand=True, padx=0, pady=(10, 5))

        # Columns
        columns = ["Course Subject", "Course Code", "Program", "Description", "Actions"]
        col_widths = [4, 2, 2, 4, 2]  # Adjusted column widths for better balance
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
        
        if self.courses_data:
            current_page_data = self.get_courses_for_page(self.current_page)
            
            for i, course in enumerate(current_page_data):
                # Description with truncation - reduced for better fit
                description = course.get('description', '')
                truncated_description = description[:40] + "..." if len(description) > 40 else description
                if not truncated_description:
                    truncated_description = "No description"
                
                data_to_display.append({
                    'name': course.get('name', 'Unknown Course'),
                    'code': course.get('code', 'N/A'),
                    'program': course.get('program_acronym', 'N/A'),
                    'description': truncated_description,
                    'data': course
                })

        # Display message if no data
        if not data_to_display:
            no_data_label = ctk.CTkLabel(
                table_frame,
                text="No courses found matching your criteria",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            )
            no_data_label.grid(row=1, column=0, columnspan=len(columns), pady=40)
        else:
            # Display course data with optimized spacing
            for i, course_data in enumerate(data_to_display):
                row = i + 1
                
                # Course Subject
                name_label = ctk.CTkLabel(
                    table_frame, 
                    text=course_data['name'], 
                    anchor="w", 
                    font=ctk.CTkFont(size=12), 
                    text_color="#111827"
                )
                name_label.grid(row=row, column=0, sticky="ew", padx=(15, 5), pady=2)
                
                # Course Code
                code_label = ctk.CTkLabel(
                    table_frame, 
                    text=course_data['code'], 
                    anchor="w", 
                    font=ctk.CTkFont(size=12), 
                    text_color="#111827"
                )
                code_label.grid(row=row, column=1, sticky="ew", padx=(15, 5), pady=2)
                
                # Program
                program_label = ctk.CTkLabel(
                    table_frame, 
                    text=course_data['program'], 
                    anchor="w", 
                    font=ctk.CTkFont(size=12), 
                    text_color="#111827"
                )
                program_label.grid(row=row, column=2, sticky="ew", padx=(15, 5), pady=2)
                
                # Description
                desc_label = ctk.CTkLabel(
                    table_frame, 
                    text=course_data['description'], 
                    anchor="w", 
                    font=ctk.CTkFont(size=12), 
                    text_color="#111827"
                )
                desc_label.grid(row=row, column=3, sticky="ew", padx=(15, 5), pady=2)
                
                # Actions dropdown - compact size
                action_var = tk.StringVar(value="Actions")
                actions = ["View", "Edit", "Delete"]
                action_menu = ctk.CTkOptionMenu(
                    table_frame,
                    values=actions,
                    variable=action_var,
                    width=90,
                    height=26,
                    font=ctk.CTkFont(size=11),
                    fg_color="#F3F4F6",
                    text_color="#222",
                    button_color="#E5E7EB",
                    button_hover_color="#D1D5DB",
                    dropdown_fg_color="#fff",
                    dropdown_hover_color="#E5E7EB",
                    dropdown_text_color="#222",
                    command=lambda choice, data=course_data['data']: self.handle_action(choice, data)
                )
                action_menu.grid(row=row, column=4, sticky="w", padx=(15, 5), pady=3)

        # Add pagination controls
        self.add_pagination(parent)

    def add_pagination(self, parent):
        """Add pagination controls for courses"""
        pagination_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pagination_frame.pack(fill="x", pady=(8, 0))
        
        # Previous button
        prev_btn = ctk.CTkButton(
            pagination_frame,
            text="← Previous",
            width=90,
            height=34,
            font=ctk.CTkFont(size=13),
            fg_color="#F3F4F6" if self.current_page == 1 else "#1E3A8A",
            text_color="#6B7280" if self.current_page == 1 else "#fff",
            hover_color="#E5E7EB" if self.current_page == 1 else "#1D4ED8",
            state="disabled" if self.current_page == 1 else "normal",
            command=lambda: self.change_page("prev")
        )
        prev_btn.pack(side="left")
        
        # Page info
        total_pages = self.get_total_pages()
        page_info = ctk.CTkLabel(
            pagination_frame,
            text=f"Page {self.current_page} of {total_pages}",
            font=ctk.CTkFont(size=13),
            text_color="#6B7280"
        )
        page_info.pack(side="left", padx=18)
        
        # Next button
        next_btn = ctk.CTkButton(
            pagination_frame,
            text="Next →",
            width=90,
            height=34,
            font=ctk.CTkFont(size=13),
            fg_color="#F3F4F6" if self.current_page == total_pages else "#1E3A8A",
            text_color="#6B7280" if self.current_page == total_pages else "#fff",
            hover_color="#E5E7EB" if self.current_page == total_pages else "#1D4ED8",
            state="disabled" if self.current_page == total_pages else "normal",
            command=lambda: self.change_page("next")
        )
        next_btn.pack(side="left")

    def handle_action(self, action, data):
        """Handle action selection for courses"""
        if action == "View":
            # Pass the database manager to the course view popup
            ViewCoursePopup(self, data, db_manager=self.db_manager)
        elif action == "Edit":
            EditCoursePopup(self, data)
        elif action == "Delete":
            self.delete_course(data)

    def delete_course(self, course_data):
        """Handle course deletion"""
        def on_delete():
            try:
                if self.db_manager:
                    success, result = self.db_manager.delete_course(course_data['id'])
                    if success:
                        # Schedule the refresh and success modal to run after the current modal is destroyed
                        self.after(100, lambda: self.refresh_courses())
                        self.after(200, lambda: self._show_delete_success())
                    else:
                        print(f"Error deleting course: {result}")
                        from tkinter import messagebox
                        messagebox.showerror("Delete Error", f"Failed to delete course: {result}")
                else:
                    print("Database manager not available")
                    from tkinter import messagebox
                    messagebox.showerror("Error", "Database manager not available")
            except Exception as e:
                print(f"Error deleting course: {e}")
                from tkinter import messagebox
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        
        DeleteModal(self, on_delete=on_delete)
    
    def _show_delete_success(self):
        """Show success modal for deletion"""
        try:
            SuccessModal(self)
        except Exception as e:
            print(f"Error showing success modal: {e}")

    def show_filter_popup(self):
        """Show filter popup"""
        CoursesFilterPopup(self)

    def on_search_change(self, search_term):
        """Handle search term changes"""
        self.current_search = search_term
        self.current_page = 1  # Reset to first page when searching
        self.apply_filters_and_search()

    def update_search_clear_button(self):
        """Update visibility of clear search button"""
        current_text = self.search_entry.get().strip()
        if current_text:
            self.clear_search_btn.pack(side="right", padx=(0, 8), pady=2)
        else:
            self.clear_search_btn.pack_forget()

    def clear_search(self):
        """Clear search"""
        self.search_entry.delete(0, tk.END)
        self.on_search_change("")

    def reset_filters(self):
        """Reset all filters and search"""
        self.current_filters = {}
        self.current_search = ""
        
        # Reset sort dropdown to default
        if hasattr(self, 'sort_var'):
            self.sort_var.set("↕")
        
        # Reset to first page
        self.current_page = 1
        
        # Clear search entry
        if hasattr(self, 'search_entry'):
            self.search_entry.delete(0, tk.END)
        
        # Reload data without filters
        self.load_courses_data()

    def apply_sort(self, sort_choice):
        """Apply sorting to courses data"""
        if not self.courses_data or sort_choice == "None":
            if sort_choice == "None":
                self.sort_var.set("↕")
                self.load_courses_data()
            return
            
        # Create a copy of the data to sort
        sorted_data = self.courses_data.copy()
        
        if sort_choice == "Sort by Course Name (A-Z)":
            sorted_data.sort(key=lambda x: x.get('name', ''))
        elif sort_choice == "Sort by Course Name (Z-A)":
            sorted_data.sort(key=lambda x: x.get('name', ''), reverse=True)
        elif sort_choice == "Sort by Course Code (A-Z)":
            sorted_data.sort(key=lambda x: x.get('code', '') or 'zzz')
        elif sort_choice == "Sort by Course Code (Z-A)":
            sorted_data.sort(key=lambda x: x.get('code', '') or '', reverse=True)
        elif sort_choice == "Sort by Program (A-Z)":
            sorted_data.sort(key=lambda x: x.get('program_acronym', '') or 'zzz')
        elif sort_choice == "Sort by Program (Z-A)":
            sorted_data.sort(key=lambda x: x.get('program_acronym', '') or '', reverse=True)
        
        # Update the data and refresh the table
        self.courses_data = sorted_data
        self.current_page = 1  # Reset to first page
        self.apply_filters_and_search()

    def apply_filters_and_search(self):
        """Apply current filters and search to the data using Python processing"""
        # Start with all courses data
        filtered_data = self.courses_data.copy()
        
        # Apply search filter using Python string operations
        if self.current_search.strip():
            search_term = self.current_search.lower().strip()
            new_filtered_data = []
            
            for course in filtered_data:
                # Check each field for search term
                course_name = course.get('name', '').lower()
                course_code = course.get('code', '').lower()
                program_name = course.get('program_name', '').lower()
                description = course.get('description', '').lower()
                
                # Use Python 'in' operator for simple string matching
                if (search_term in course_name or 
                    search_term in course_code or 
                    search_term in program_name or 
                    search_term in description):
                    new_filtered_data.append(course)
            
            filtered_data = new_filtered_data
        
        # Apply program filter using Python
        if self.current_filters.get('program') and self.current_filters['program'] != 'All':
            program_filter = self.current_filters['program']
            filtered_data = [
                course for course in filtered_data
                if course.get('program_name', '') == program_filter
            ]
        
        # Apply year filter using Python
        if self.current_filters.get('year') and self.current_filters['year'] != 'All':
            year_filter = self.current_filters['year']
            year_number = self.extract_year_number(year_filter)
            
            if year_number:
                filtered_data = self.filter_courses_by_year(filtered_data, year_number)
        
        # Apply section filter using Python
        if self.current_filters.get('section') and self.current_filters['section'] != 'All':
            section_filter = self.current_filters['section']
            filtered_data = self.filter_courses_by_section(filtered_data, section_filter)
        
        # Update filtered data and refresh table
        self.filtered_courses_data = filtered_data
        self.refresh_table()

    def extract_year_number(self, year_display):
        """Extract year number from display format using simple Python logic"""
        try:
            # Simple mapping using Python dictionary
            year_mappings = {
                '1st Year': 1, '2nd Year': 2, '3rd Year': 3, '4th Year': 4,
                '5th Year': 5, '6th Year': 6, '7th Year': 7, '8th Year': 8
            }
            
            # Use Python dict.get() for safe lookup
            return year_mappings.get(year_display, None)
        except Exception as e:
            print(f"Error extracting year number: {e}")
            return None

    def filter_courses_by_year(self, courses, year_number):
        """Filter courses by year level using simple database query and Python processing"""
        try:
            if not self.db_manager:
                return courses
            
            # Get simple assignment data and process in Python
            success, assigned_courses = self.db_manager.get_courses_by_year(year_number)
            
            if success and assigned_courses:
                # Extract course IDs using Python
                course_ids = []
                for assignment in assigned_courses:
                    course_id = assignment.get('course_id')
                    if course_id and course_id not in course_ids:
                        course_ids.append(course_id)
                
                # Filter courses using Python list comprehension
                filtered_courses = [
                    course for course in courses 
                    if course.get('id') in course_ids
                ]
                return filtered_courses
            else:
                return []
                
        except Exception as e:
            print(f"Error filtering courses by year: {e}")
            return courses

    def filter_courses_by_section(self, courses, section_name):
        """Filter courses by specific section using simple database query and Python processing"""
        try:
            if not self.db_manager:
                return courses
            
            # Get simple assignment data and process in Python
            success, assigned_courses = self.db_manager.get_courses_by_section(section_name)
            
            if success and assigned_courses:
                # Extract course IDs using Python
                course_ids = []
                for assignment in assigned_courses:
                    course_id = assignment.get('course_id')
                    if course_id and course_id not in course_ids:
                        course_ids.append(course_id)
                
                # Filter courses using Python list comprehension
                filtered_courses = [
                    course for course in courses 
                    if course.get('id') in course_ids
                ]
                return filtered_courses
            else:
                return []
                
        except Exception as e:
            print(f"Error filtering courses by section: {e}")
            return courses

    def apply_filters(self, filter_values):
        """Apply filters from filter popup"""
        self.current_filters = filter_values
        self.current_page = 1  # Reset to first page when filtering
        self.apply_filters_and_search()

    def export_courses(self):
        """Export courses data to CSV - uses filtered, searched, and sorted data"""
        try:
            import csv
            from tkinter import filedialog
            from datetime import datetime
            
            # Use filtered data instead of all data
            data_to_export = self.filtered_courses_data if hasattr(self, 'filtered_courses_data') else self.courses_data
            
            if not data_to_export:
                from tkinter import messagebox
                messagebox.showwarning("No Data", "No course data available to export with current filters.")
                return
            
            # Ask user where to save the file
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"courses_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            # Export filtered/searched/sorted data
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Course Name', 'Course Code', 'Program', 'Description', 'Created At'])
                
                # Write filtered data
                for course in data_to_export:
                    row_data = [
                        course.get('name', ''),
                        course.get('code', ''),
                        course.get('program_name', ''),
                        course.get('description', ''),
                        course.get('created_at', '')
                    ]
                    writer.writerow(row_data)
            
            # Show success message with count
            from tkinter import messagebox
            messagebox.showinfo("Export Successful", f"Exported {len(data_to_export)} courses to:\n{filename}")
            
        except Exception as e:
            print(f"Export error: {e}")
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"Failed to export courses data:\n{str(e)}")

    def create_course(self):
        CreateCoursePopup(self)

    def refresh_courses(self):
        """Refresh the courses data and update the UI"""
        self.load_courses_data()
        print("Courses refreshed")