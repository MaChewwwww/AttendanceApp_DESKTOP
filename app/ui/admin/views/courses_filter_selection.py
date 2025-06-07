import customtkinter as ctk
import tkinter as tk
from app.db_manager import DatabaseManager

class CoursesFilterSection:
    """Courses-specific filter section"""
    
    def __init__(self, parent_frame, current_filters):
        self.parent_frame = parent_frame
        self.current_filters = current_filters
        self.filters = {}
        self.section_menu = None
        self.db_manager = DatabaseManager()
        
        # Load programs and years dynamically from database
        self.load_programs()
        self.load_years()
        
        self.setup_filters()
    
    def load_programs(self):
        """Load active programs from database"""
        try:
            success, programs = self.db_manager.get_programs()
            if success:
                # Extract names for the dropdown
                program_names = [program.get('name', '') for program in programs if program.get('name')]
                
                # Create programs options list starting with "All"
                self.programs_options = ["All"] + program_names
                
                # Initialize empty section mappings - will be loaded dynamically
                self.section_mappings = {}
                
            else:
                print(f"Error loading programs: {programs}")
                # Fallback to hardcoded options
                self.programs_options = ["All", "Bachelor of Science in Information Technology", "Bachelor of Science in Computer Science", "Bachelor of Science in Information Systems"]
                self.section_mappings = {}
        except Exception as e:
            print(f"Exception loading programs: {e}")
            # Fallback to hardcoded options
            self.programs_options = ["All", "Bachelor of Science in Information Technology", "Bachelor of Science in Computer Science", "Bachelor of Science in Information Systems"]
            self.section_mappings = {}
    
    def load_sections_for_program(self, program_name):
        """Load sections for a specific program from database"""
        try:
            if program_name == "All":
                return ["All"]
            
            success, sections = self.db_manager.get_sections_by_program(program_name)
            
            if success:
                # Use set to remove duplicates, then convert back to sorted list
                section_names = list(set([section.get('name', '') for section in sections if section.get('name')]))
                section_names.sort()  # Sort alphabetically
                return ["All"] + section_names
            else:
                print(f"Error loading sections for {program_name}: {sections}")
                return ["All"]
                
        except Exception as e:
            print(f"Exception loading sections for {program_name}: {e}")
            return ["All"]
    
    def load_years(self):
        """Load available years from section names in database"""
        try:
            success, sections = self.db_manager.get_sections_all()
            
            if success:
                # Extract year numbers from section names
                year_numbers = set()
                for section in sections:
                    section_name = section.get('name', '')
                    if section_name and len(section_name) > 0:
                        # Get first character (year indicator)
                        year_char = section_name[0]
                        if year_char.isdigit():
                            year_numbers.add(int(year_char))
                
                # Convert to year display format and sort (up to 10 years)
                year_mapping = {
                    1: '1st Year', 2: '2nd Year', 3: '3rd Year', 4: '4th Year', 
                    5: '5th Year', 6: '6th Year', 7: '7th Year', 8: '8th Year',
                    9: '9th Year', 10: '10th Year'
                }
                available_years = []
                for year_num in sorted(year_numbers):
                    if year_num in year_mapping:
                        available_years.append(year_mapping[year_num])
                
                # Create year options list starting with "All"
                self.year_options = ["All"] + available_years
                
            else:
                print(f"Error loading sections for years: {sections}")
                # Fallback to hardcoded options
                self.year_options = ["All", "1st Year", "2nd Year", "3rd Year", "4th Year"]
                
        except Exception as e:
            print(f"Exception loading years: {e}")
            # Fallback to hardcoded options
            self.year_options = ["All", "1st Year", "2nd Year", "3rd Year", "4th Year"]
    
    def setup_filters(self):
        """Setup all course filter components"""
        # Programs filter (first)
        ctk.CTkLabel(
            self.parent_frame, 
            text="Program", 
            font=ctk.CTkFont(weight="bold"), 
            text_color="black"
        ).pack(anchor="w", pady=(0, 5))
        
        programs_var = tk.StringVar(value=self.current_filters.get('program', 'All'))
        self.filters['program'] = programs_var
        
        programs_menu = ctk.CTkOptionMenu(
            self.parent_frame,
            values=self.programs_options,
            variable=programs_var,
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            command=self.on_program_change
        )
        programs_menu.pack(fill="x", pady=(0, 15))
        
        # Year filter (second)
        ctk.CTkLabel(
            self.parent_frame, 
            text="Year", 
            font=ctk.CTkFont(weight="bold"), 
            text_color="black"
        ).pack(anchor="w", pady=(0, 5))
        
        year_var = tk.StringVar(value=self.current_filters.get('year', 'All'))
        self.filters['year'] = year_var
        
        year_menu = ctk.CTkOptionMenu(
            self.parent_frame,
            values=self.year_options,
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
        
        # Section filter (third)
        ctk.CTkLabel(
            self.parent_frame, 
            text="Section", 
            font=ctk.CTkFont(weight="bold"), 
            text_color="black"
        ).pack(anchor="w", pady=(0, 5))
        
        section_var = tk.StringVar(value=self.current_filters.get('section', 'All'))
        self.filters['section'] = section_var
        
        # Initialize section options based on current program selection
        current_program = programs_var.get()
        
        if current_program == "All":
            # Load all sections when no specific program is selected
            initial_sections = self.load_all_sections()
            section_state = "normal" if len(initial_sections) > 1 else "disabled"
        else:
            # Load sections for the currently selected program
            initial_sections = self.load_sections_for_program(current_program)
            # Enable only if there are actual sections (more than just "All")
            section_state = "normal" if len(initial_sections) > 1 else "disabled"
        
        self.section_menu = ctk.CTkOptionMenu(
            self.parent_frame,
            values=initial_sections,
            variable=section_var,
            fg_color="#F3F4F6" if section_state == "normal" else "#E5E7EB",
            text_color="#222" if section_state == "normal" else "#9CA3AF",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB" if section_state == "normal" else "#E5E7EB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            state=section_state
        )
        self.section_menu.pack(fill="x", pady=(0, 15))

    def load_all_sections(self):
        """Load all sections from all programs"""
        try:
            success, sections = self.db_manager.get_sections_all()
            
            if success:
                # Use set to remove duplicates, then convert back to sorted list
                section_names = list(set([section.get('name', '') for section in sections if section.get('name')]))
                section_names.sort()  # Sort alphabetically
                return ["All"] + section_names
            else:
                print(f"Error loading all sections: {sections}")
                return ["All"]
                
        except Exception as e:
            print(f"Exception loading all sections: {e}")
            return ["All"]
    
    def on_program_change(self, selected_program):
        """Handle program selection change to update section options"""
        if not self.section_menu:
            return
            
        section_var = self.filters['section']
        
        if selected_program == "All":
            # Load all sections when "All" programs selected
            section_options = self.load_all_sections()
            
            if len(section_options) > 1:  # More than just "All"
                self.section_menu.configure(
                    values=section_options,
                    state="normal",
                    fg_color="#F3F4F6",
                    text_color="#222",
                    button_hover_color="#D1D5DB"
                )
                section_var.set("All")
            else:
                # No sections found, disable dropdown
                self.section_menu.configure(
                    values=["All", "No sections available"],
                    state="disabled",
                    fg_color="#E5E7EB",
                    text_color="#9CA3AF",
                    button_hover_color="#E5E7EB"
                )
                section_var.set("All")
        else:
            # Load sections dynamically for the selected program
            section_options = self.load_sections_for_program(selected_program)
            
            if len(section_options) > 1:  # More than just "All" - has actual sections
                self.section_menu.configure(
                    values=section_options,
                    state="normal",
                    fg_color="#F3F4F6",
                    text_color="#222",
                    button_hover_color="#D1D5DB"
                )
                # Reset section to "All" when program changes
                section_var.set("All")
            else:
                # No sections found for this program, disable dropdown
                self.section_menu.configure(
                    values=["All", "No sections available"],
                    state="disabled",
                    fg_color="#E5E7EB",
                    text_color="#9CA3AF",
                    button_hover_color="#E5E7EB"
                )
                section_var.set("All")
    
    def get_filter_values(self):
        """Get current filter values"""
        return self.filters


class CoursesFilterSectionFactory:
    """Factory class to create course filter sections"""
    
    @staticmethod
    def create_filter_section(parent_frame, current_filters):
        """Create the course filter section"""
        return CoursesFilterSection(parent_frame, current_filters)
