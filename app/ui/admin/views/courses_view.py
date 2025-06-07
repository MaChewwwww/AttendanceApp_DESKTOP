import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ViewCoursePopup(ctk.CTkToplevel):
    def __init__(self, parent, course_data, db_manager=None):
        super().__init__(parent)
        self.course_data = course_data
        self.db_manager = db_manager
        
        course_name = course_data.get('name', 'Unknown Course')
        self.title(f"{course_name} View")
        self.geometry("950x950")  # Slightly larger for better proportions
        self.resizable(False, False)
        self.configure(fg_color="#F5F5F5")
        self.transient(parent)
        self.grab_set()
        
        # Initialize filter variables first
        self.year_var = ctk.StringVar(value="All Years")
        self.semester_var = ctk.StringVar(value="All Semesters")
        
        # Load initial statistics before setting up UI
        self.load_statistics()
        
        # Center the window
        self.center_window()
        self.setup_ui()

    def center_window(self):
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position coordinates
        x = (screen_width - 950) // 2
        y = (screen_height - 950) // 2
        
        # Set window position
        self.geometry(f"950x950+{x}+{y}")

    def setup_ui(self):
        course_name = self.course_data.get('name', 'Unknown Course')
        course_code = self.course_data.get('code', 'N/A')
        course_description = self.course_data.get('description', 'No description available')
        
        # Header row with course name and controls - better spacing
        header_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        header_frame.pack(fill="x", padx=40, pady=(30, 0))
        
        # Course name and subtitle (left)
        name_subtitle = ctk.CTkFrame(header_frame, fg_color="#F5F5F5")
        name_subtitle.pack(side="left", anchor="n")
        
        ctk.CTkLabel(
            name_subtitle,
            text=f"{course_name} ({course_code})",
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color="#222"
        ).pack(anchor="w")
        
        # Course description with better formatting
        if course_description and course_description != "No description available":
            max_desc_length = 80
            display_description = course_description[:max_desc_length] + "..." if len(course_description) > max_desc_length else course_description
            
            ctk.CTkLabel(
                name_subtitle,
                text=display_description,
                font=ctk.CTkFont(size=12),
                text_color="#666666",
                anchor="w",
                justify="left",
                wraplength=450
            ).pack(anchor="w", pady=(8, 0), fill="x")
        
        # Filters (right) - better symmetry
        controls_frame = ctk.CTkFrame(header_frame, fg_color="#F5F5F5")
        controls_frame.pack(side="right", anchor="n")
        
        # Get available years and semesters dynamically from database
        available_years = self.get_available_years()
        available_semesters = self.get_available_semesters()
        
        # Year selection
        year_values = ["All Years"] + available_years
        year_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=year_values,
            variable=self.year_var,
            width=120,
            height=32,
            command=self.on_filter_change
        )
        year_dropdown.grid(row=0, column=0, padx=(0, 10), pady=(0, 6))
        
        # Semester selection
        semester_values = ["All Semesters"] + available_semesters
        semester_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=semester_values,
            variable=self.semester_var,
            width=120,
            height=32,
            command=self.on_filter_change
        )
        semester_dropdown.grid(row=0, column=1, pady=(0, 6))
        
        # Create containers for refreshable content
        self.create_refreshable_content()

    def create_refreshable_content(self):
        """Create the content that can be refreshed (stat cards and charts)"""
        # Store references to refreshable frames
        self.stat_cards_frame = None
        self.charts_frame = None
        self.bar_chart_frame = None
        
        # Create stat cards container
        self.create_stat_cards()
        
        # Create charts section
        self.create_charts_section()
        
        # Create bar chart section
        self.create_bar_chart_section()

    def create_stat_cards(self):
        """Create the statistics cards section with better spacing"""
        if hasattr(self, 'stat_cards_frame') and self.stat_cards_frame:
            self.stat_cards_frame.destroy()
        
        self.stat_cards_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        self.stat_cards_frame.pack(fill="x", padx=40, pady=(28, 0))  # Slightly more top padding
        
        card_data = [
            (str(self.stats['total_students']), "Total Students"),
            (self.stats['attendance_rate'], "Course Attendance Rate"),
            (str(self.stats['total_classes']), "Number of Classes"),
            (str(self.stats['total_absents']), "Total Absents")
        ]
        
        # Create cards with perfect symmetric spacing
        for i, (value, label) in enumerate(card_data):
            card = ctk.CTkFrame(
                self.stat_cards_frame, 
                fg_color="#fff", 
                width=200,  # Slightly wider for better proportion
                height=105, 
                corner_radius=12
            )
            
            # Calculate padding for perfect symmetry
            if i == 0:
                padx = (0, 12)
            elif i == len(card_data) - 1:
                padx = (12, 0)
            else:
                padx = (12, 12)
            
            card.pack(side="left", padx=padx, pady=0, expand=True)
            card.pack_propagate(False)
            
            ctk.CTkLabel(
                card, 
                text=value, 
                font=ctk.CTkFont(size=25, weight="bold"),  # Slightly larger
                text_color="#222"
            ).pack(anchor="w", padx=22, pady=(22, 0))
            
            ctk.CTkLabel(
                card, 
                text=label, 
                font=ctk.CTkFont(size=11), 
                text_color="#757575"
            ).pack(anchor="w", padx=22, pady=(0, 14))

    def create_charts_section(self):
        """Create the charts section with perfect symmetric layout"""
        if hasattr(self, 'charts_frame') and self.charts_frame:
            self.charts_frame.destroy()
        
        # Charts section with symmetric padding
        self.charts_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=12)
        self.charts_frame.pack(fill="x", padx=40, pady=22)  # Better vertical spacing
        
        # Charts container with perfect proportions
        charts_container = ctk.CTkFrame(self.charts_frame, fg_color="transparent", height=165)
        charts_container.pack(fill="x", padx=32, pady=(28, 28))  # Symmetric padding
        charts_container.pack_propagate(False)
        
        # Left side - Bar Chart with exact sizing
        demo_frame = ctk.CTkFrame(
            charts_container, 
            fg_color="#F8F9FA", 
            corner_radius=8, 
            width=355  # Slightly wider
        )
        demo_frame.pack(side="left", fill="y", padx=(0, 18))  # Symmetric gap
        demo_frame.pack_propagate(False)
        
        self.create_pie_chart(demo_frame)
        
        # Right side - Key Metrics with exact sizing
        metrics_frame = ctk.CTkFrame(
            charts_container, 
            fg_color="#F8F9FA", 
            corner_radius=8, 
            width=465  # Complementary width
        )
        metrics_frame.pack(side="right", fill="y", padx=(18, 0))  # Symmetric gap
        metrics_frame.pack_propagate(False)
        
        self.create_data_cards(metrics_frame)

    def load_statistics(self):
        """Load statistics based on current filter selections"""
        if self.db_manager and self.course_data.get('id'):
            try:
                # Get current filter values
                year_filter = self.year_var.get() if self.year_var.get() != "All Years" else None
                semester_filter = self.semester_var.get() if self.semester_var.get() != "All Semesters" else None
                
                # Get course statistics from database using the courses manager
                success, stats = self.db_manager.courses.get_course_statistics(
                    self.course_data['id'], 
                    academic_year=year_filter,
                    semester=semester_filter
                )
                
                if success:
                    self.stats = stats
                    print(f"Loaded course statistics for course {self.course_data['id']}: {stats}")
                else:
                    print(f"Error loading course statistics: {stats}")
                    # Fallback to sample data
                    self.stats = self._get_fallback_stats()
                
                # Load section statistics for bar chart and key metrics
                success_sections, section_stats = self.db_manager.courses.get_course_section_statistics(
                    self.course_data['id'], 
                    academic_year=year_filter,
                    semester=semester_filter
                )
                
                if success_sections:
                    self.section_stats = section_stats
                    print(f"Loaded section statistics: {section_stats}")
                else:
                    print(f"Error loading section statistics: {section_stats}")
                    self.section_stats = self._get_fallback_section_stats()
                
                # Load schedule statistics for key metrics
                success_schedule, schedule_stats = self.db_manager.courses.get_course_schedule_statistics(
                    self.course_data['id'], 
                    academic_year=year_filter,
                    semester=semester_filter
                )
                
                if success_schedule:
                    self.schedule_stats = schedule_stats
                    print(f"Loaded schedule statistics: {schedule_stats}")
                else:
                    print(f"Error loading schedule statistics: {schedule_stats}")
                    self.schedule_stats = self._get_fallback_schedule_stats()
                
                # Load monthly attendance data for line chart
                success_monthly, monthly_stats = self.db_manager.get_course_monthly_attendance(
                    self.course_data['id'], 
                    academic_year=year_filter,
                    semester=semester_filter
                )
                
                if success_monthly:
                    self.monthly_stats = monthly_stats
                    print(f"Loaded monthly attendance statistics: {monthly_stats}")
                else:
                    print(f"Error loading monthly attendance statistics: {monthly_stats}")
                    self.monthly_stats = self._get_fallback_monthly_stats()
                    
            except Exception as e:
                print(f"Exception loading course statistics: {e}")
                # Fallback to sample data
                self.stats = self._get_fallback_stats()
                self.section_stats = self._get_fallback_section_stats()
                self.schedule_stats = self._get_fallback_schedule_stats()
                self.monthly_stats = self._get_fallback_monthly_stats()
        else:
            # Use sample data when no database connection or course ID
            print("Using sample data - no database connection or course ID")
            self.stats = self._get_sample_stats()
            self.section_stats = self._get_sample_section_stats()
            self.schedule_stats = self._get_sample_schedule_stats()
            self.monthly_stats = self._get_sample_monthly_stats()

    def _get_fallback_stats(self):
        """Get fallback statistics when database query fails"""
        return {
            'total_students': 0,
            'attendance_rate': '0%',
            'total_classes': 0,
            'total_absents': 0,
            'total_present': 0,
            'total_late': 0
        }

    def _get_sample_stats(self):
        """Get sample statistics for demonstration"""
        return {
            'total_students': 45,
            'attendance_rate': '87%',
            'total_classes': 24,
            'total_absents': 32,
            'total_present': 180,
            'total_late': 25
        }

    def _get_fallback_section_stats(self):
        """Get fallback section statistics when database query fails"""
        return {
            'section_stats': {},
            'best_section': None,
            'worst_section': None
        }

    def _get_sample_section_stats(self):
        """Get sample section statistics for demonstration"""
        return {
            'section_stats': {
                'Section A': {'attendance_rate': 92.0, 'total_students': 12, 'total_records': 48, 'present_count': 44},
                'Section B': {'attendance_rate': 86.0, 'total_students': 11, 'total_records': 44, 'present_count': 38},
                'Section C': {'attendance_rate': 78.0, 'total_students': 10, 'total_records': 40, 'present_count': 31},
                'Section D': {'attendance_rate': 89.0, 'total_students': 12, 'total_records': 48, 'present_count': 43}
            },
            'best_section': {'name': 'Section A', 'rate': 92.0},
            'worst_section': {'name': 'Section C', 'rate': 78.0}
        }

    def _get_fallback_schedule_stats(self):
        """Get fallback schedule statistics when database query fails"""
        return {
            'best_schedule': None
        }

    def _get_sample_schedule_stats(self):
        """Get sample schedule statistics for demonstration"""
        return {
            'best_schedule': {'time': 'Monday : 9:00 - 10:00', 'rate': 94.5}
        }

    def _get_fallback_monthly_stats(self):
        """Get fallback monthly statistics when database query fails"""
        return {
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'sections_data': {}
        }

    def _get_sample_monthly_stats(self):
        """Get sample monthly statistics for demonstration"""
        return {
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'sections_data': {
                'Section A': [88, 92, 89, 94, 91, 85, 82, 87, 93, 90, 89, 92],
                'Section B': [82, 85, 83, 88, 86, 80, 78, 82, 87, 84, 83, 86],
                'Section C': [75, 78, 76, 81, 79, 72, 70, 75, 80, 77, 76, 78],
                'Section D': [85, 88, 86, 91, 89, 83, 81, 85, 90, 87, 86, 89]
            }
        }

    def on_filter_change(self, value=None):
        """Called when year or semester selection changes"""
        self.load_statistics()
        self.refresh_charts()

    def refresh_charts(self):
        """Refresh all charts with new data"""
        # Update the window to ensure proper layout
        self.update_idletasks()
        
        # Recreate all refreshable content with new data
        self.create_stat_cards()
        self.create_charts_section() 
        self.create_bar_chart_section()
        
        # Force a visual update
        self.update()
        
        print(f"Charts refreshed - Academic Year: {self.year_var.get()}, Semester: {self.semester_var.get()}")
        print(f"Course stats: Students: {self.stats['total_students']}, Attendance: {self.stats['attendance_rate']}")

    def create_data_cards(self, parent):
        """Create compact metric cards with real data from database"""
        # Get data from loaded statistics
        best_section = self.section_stats.get('best_section')
        worst_section = self.section_stats.get('worst_section')
        best_schedule = self.schedule_stats.get('best_schedule')
        
        # Prepare card data with real values or fallbacks
        card_data = []
        
        # Most Active Section
        if best_section and best_section['name']:
            most_active_text = f"{best_section['name']} ({best_section['rate']:.0f}%)"
        else:
            most_active_text = "No data available"
        card_data.append(("Most Active Section", most_active_text, "#10B981", "📈"))
        
        # Least Active Section  
        if worst_section and worst_section['name']:
            least_active_text = f"{worst_section['name']} ({worst_section['rate']:.0f}%)"
        else:
            least_active_text = "No data available"
        card_data.append(("Least Active Section", least_active_text, "#EF4444", "📉"))
        
        # Best Schedule - removed percentage display
        if best_schedule and best_schedule['time']:
            best_schedule_text = best_schedule['time']
        else:
            best_schedule_text = "No schedule data"
        card_data.append(("Best Schedule", best_schedule_text, "#8B5CF6", "📊"))
        
        # Perfect symmetric top spacing
        top_spacer = ctk.CTkFrame(parent, fg_color="transparent", height=20)
        top_spacer.pack(fill="x")
        
        for i, (label, value, color, icon) in enumerate(card_data):
            card_frame = ctk.CTkFrame(
                parent, 
                fg_color="#FFFFFF", 
                corner_radius=8, 
                height=34,  # Slightly taller
                border_width=1,
                border_color="#E5E7EB"
            )
            card_frame.pack(fill="x", padx=32, pady=7)  # Better spacing
            card_frame.pack_propagate(False)
            
            # Left section
            left_section = ctk.CTkFrame(card_frame, fg_color="transparent")
            left_section.pack(side="left", fill="y", padx=(20, 0))  # More padding
            
            # Icon
            icon_frame = ctk.CTkFrame(
                left_section, 
                fg_color=color, 
                width=26, 
                height=26, 
                corner_radius=13
            )
            icon_frame.pack(side="left", pady=4)
            icon_frame.pack_propagate(False)
            
            ctk.CTkLabel(
                icon_frame,
                text=icon,
                font=ctk.CTkFont(size=12),
                text_color="white"
            ).place(relx=0.5, rely=0.5, anchor="center")
            
            # Label
            ctk.CTkLabel(
                left_section,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#374151"
            ).pack(side="left", padx=(16, 0), anchor="w")
            
            # Value
            ctk.CTkLabel(
                card_frame,
                text=value,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#111827",
                wraplength=180,
                justify="right"
            ).pack(side="right", padx=(12, 26), anchor="e")  # More padding
        
        # Perfect symmetric bottom spacing
        bottom_spacer = ctk.CTkFrame(parent, fg_color="transparent", height=20)
        bottom_spacer.pack(fill="x")

    def create_pie_chart(self, parent):
        """Create a bar chart with real section data from database"""
        # Get section data from loaded statistics
        section_stats = self.section_stats.get('section_stats', {})
        
        if not section_stats:
            # Use sample data if no real data available
            sections = ['No Data']
            attendance_rates = [0]
            colors = ['#9CA3AF']
        else:
            # Use real data from database
            sections = list(section_stats.keys())
            attendance_rates = [section_stats[section]['attendance_rate'] for section in sections]
            
            # Generate colors for sections (cycle through predefined colors)
            color_palette = ['#3B82F6', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6', '#06B6D4']
            colors = [color_palette[i % len(color_palette)] for i in range(len(sections))]
        
        fig, ax = plt.subplots(figsize=(3.6, 1.65))  # Perfect proportions
        fig.patch.set_facecolor('#F8F9FA')
        
        # Create bar chart with real data
        bars = ax.bar(sections, attendance_rates, color=colors, alpha=0.88, width=0.68)
        
        # Chart styling with better proportions
        max_rate = max(attendance_rates) if attendance_rates else 100
        ax.set_ylim(0, min(100, max_rate + 10))  # Dynamic y-limit based on data
        ax.set_ylabel('Rate (%)', fontsize=9, color='#374151', weight='bold')
        ax.set_xlabel('Sections', fontsize=9, color='#374151', weight='bold')
        
        # Clean axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E5E7EB')
        ax.spines['bottom'].set_color('#E5E7EB')
        
        # Perfect tick styling
        ax.tick_params(axis='x', colors='#374151', labelsize=8, rotation=0)
        ax.tick_params(axis='y', colors='#6B7280', labelsize=8)
        
        # Value labels with perfect positioning
        for bar, rate in zip(bars, attendance_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{rate:.0f}%' if rate > 0 else 'No Data', 
                   ha='center', va='bottom', fontsize=8, 
                   color='#374151', weight='bold')
        
        # Perfect grid
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=12, padx=18, expand=True)  # Perfect padding
        
        plt.close(fig)

    def create_bar_chart_section(self):
        """Create symmetric monthly chart section without title"""
        if hasattr(self, 'bar_chart_frame') and self.bar_chart_frame:
            self.bar_chart_frame.destroy()
        
        # Monthly Chart section with symmetric padding - no title
        self.bar_chart_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=12)
        self.bar_chart_frame.pack(fill="both", expand=True, padx=40, pady=(10, 35))
        
        # Monthly chart container with symmetric proportions - more space without title
        line_container = ctk.CTkFrame(
            self.bar_chart_frame, 
            fg_color="#F8F9FA", 
            corner_radius=8, 
            height=360  # Increased height since no title
        )
        line_container.pack(fill="both", expand=True, padx=30, pady=25)  # Symmetric padding
        line_container.pack_propagate(False)
        
        self.create_monthly_attendance_line_chart(line_container)

    def create_monthly_attendance_line_chart(self, parent):
        """Create monthly attendance chart with real data from database"""
        # Get real monthly data from loaded statistics
        monthly_data = self.monthly_stats
        months = monthly_data.get('months', ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        sections_data = monthly_data.get('sections_data', {})
        
        # Use sample data if no real data available
        if not sections_data:
            sections_data = {
                'No Data': [0] * 12
            }
        
        fig, ax = plt.subplots(figsize=(11.2, 4.4))
        fig.patch.set_facecolor('#F8F9FA')
        
        x = np.arange(len(months))
        
        # Color palette for different sections
        color_palette = ['#3B82F6', '#F59E0B', '#10B981', '#EF4444', '#8B5CF6', '#06B6D4', '#F97316', '#84CC16']
        marker_styles = ['o', 's', '^', 'D', 'v', 'h', 'p', '*']
        
        # Plot lines for each section with real data
        legend_entries = []
        max_value = 0
        min_value = 100
        
        for i, (section_name, attendance_data) in enumerate(sections_data.items()):
            color = color_palette[i % len(color_palette)]
            marker = marker_styles[i % len(marker_styles)]
            
            # Plot the line
            line = ax.plot(x, attendance_data, 
                          label=section_name, 
                          color=color, 
                          linewidth=3.5 if i == 0 else 3, 
                          marker=marker, 
                          markersize=5 if i == 0 else 4)
            
            legend_entries.append(section_name)
            
            # Track min/max for annotations
            if attendance_data:
                section_max = max(attendance_data)
                section_min = min([val for val in attendance_data if val > 0])  # Exclude 0 values
                if section_max > max_value:
                    max_value = section_max
                if section_min < min_value and section_min > 0:
                    min_value = section_min
        
        # Chart styling
        ax.set_xlabel('Months', fontsize=12, color='#374151', weight='bold')
        ax.set_ylabel('Attendance Rate (%)', fontsize=12, color='#374151', weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(months, fontsize=10, color='#6B7280')
        
        # Dynamic y-axis range based on real data
        if max_value > 0:
            ax.set_ylim(max(0, min_value - 10), min(100, max_value + 10))
        else:
            ax.set_ylim(0, 100)
        
        # Clean axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E5E7EB')
        ax.spines['bottom'].set_color('#E5E7EB')
        
        # Grid
        ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        
        # Tick styling
        ax.tick_params(axis='y', colors='#6B7280', labelsize=10)
        ax.tick_params(axis='x', colors='#6B7280', labelsize=10)
        
        # Legend positioning
        if legend_entries:
            ax.legend(fontsize=11, loc='upper left', frameon=False, bbox_to_anchor=(0.02, 0.98))
        
        # Add annotations for real data peaks and lows
        if sections_data and any(any(data) for data in sections_data.values()):
            # Find section with highest peak
            best_section = None
            best_value = 0
            best_month_idx = 0
            
            worst_section = None
            worst_value = 100
            worst_month_idx = 0
            
            for section_name, attendance_data in sections_data.items():
                if attendance_data:
                    section_max = max(attendance_data)
                    section_min = min([val for val in attendance_data if val > 0])
                    
                    if section_max > best_value:
                        best_value = section_max
                        best_section = section_name
                        best_month_idx = attendance_data.index(section_max)
                    
                    if section_min < worst_value and section_min > 0:
                        worst_value = section_min
                        worst_section = section_name
                        worst_month_idx = attendance_data.index(section_min)
            
            # Add annotations if we have valid data
            if best_section and best_value > 0:
                ax.annotate(f'{best_section} Peak: {best_value:.0f}%', 
                           xy=(best_month_idx, best_value), 
                           xytext=(best_month_idx + 0.5, best_value + 3),
                           fontsize=9, color='#1D4ED8', weight='bold',
                           arrowprops=dict(arrowstyle='->', color='#1D4ED8', alpha=0.7))
            
            if worst_section and worst_value < 100:
                ax.annotate(f'{worst_section} Low: {worst_value:.0f}%', 
                           xy=(worst_month_idx, worst_value), 
                           xytext=(worst_month_idx + 0.5, worst_value - 3),
                           fontsize=9, color='#DC2626', weight='bold',
                           arrowprops=dict(arrowstyle='->', color='#DC2626', alpha=0.7))
        
        plt.tight_layout(pad=2.2)
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=30, padx=30, fill="both", expand=True)
        
        plt.close(fig)

    def get_available_years(self):
        """Get available academic years from database"""
        try:
            if self.db_manager:
                success, years = self.db_manager.get_available_academic_years()
                if success and years:
                    return years
            # Fallback to current and previous years if database query fails
            from datetime import datetime
            current_year = datetime.now().year
            return [f"{current_year}-{current_year + 1}", f"{current_year - 1}-{current_year}"]
        except Exception as e:
            print(f"Error fetching available years: {e}")
            # Fallback years
            from datetime import datetime
            current_year = datetime.now().year
            return [f"{current_year}-{current_year + 1}", f"{current_year - 1}-{current_year}"]

    def get_available_semesters(self):
        """Get available semesters from database"""
        try:
            if self.db_manager:
                success, semesters = self.db_manager.get_available_semesters()
                if success and semesters:
                    return semesters
            # Fallback semesters if database query fails
            return ["1st Semester", "2nd Semester", "Summer"]
        except Exception as e:
            print(f"Error fetching available semesters: {e}")
            # Fallback semesters
            return ["1st Semester", "2nd Semester", "Summer"]
