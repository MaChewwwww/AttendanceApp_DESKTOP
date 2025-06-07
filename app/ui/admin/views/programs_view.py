import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class ViewProgramPopup(ctk.CTkToplevel):
    def __init__(self, parent, program_data, db_manager=None):
        super().__init__(parent)
        self.program_data = program_data
        self.db_manager = db_manager
        program_name = program_data.get('name', 'Unknown Program')
        self.title(f"{program_name} View")
        self.geometry("900x900")
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
        x = (screen_width - 900) // 2
        y = (screen_height - 900) // 2
        
        # Set window position
        self.geometry(f"900x900+{x}+{y}")

    def setup_ui(self):
        program_name = self.program_data.get('name', 'Unknown Program')
        program_description = self.program_data.get('description', 'No description available')
        
        # Header row with program name, subtitle, and controls
        header_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        header_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        # Program name and subtitle (left)
        name_subtitle = ctk.CTkFrame(header_frame, fg_color="#F5F5F5")
        name_subtitle.pack(side="left", anchor="n")
        
        ctk.CTkLabel(
            name_subtitle,
            text=program_name,
            font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
            text_color="#222"
        ).pack(anchor="w")
        
        # Truncate description if too long
        max_desc_length = 60
        truncated_desc = program_description[:max_desc_length] + "..." if len(program_description) > max_desc_length else program_description
        
        ctk.CTkLabel(
            name_subtitle,
            text=truncated_desc.upper(),
            font=ctk.CTkFont(size=14),
            text_color="#757575",
            anchor="w",
            justify="left"
        ).pack(anchor="w", pady=(2, 0), fill="x")
        
        # Filters (right)
        controls_frame = ctk.CTkFrame(header_frame, fg_color="#F5F5F5")
        controls_frame.pack(side="right", anchor="n")
        
        # Get available options from database
        if self.db_manager:
            success, years = self.db_manager.get_available_academic_years()
            available_years = years if success else []
            
            success, semesters = self.db_manager.get_available_semesters()
            available_semesters = semesters if success else []
        else:
            available_years = ["2024-2025", "2023-2024"]
            available_semesters = ["1st Semester", "2nd Semester"]
        
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
        year_dropdown.grid(row=0, column=0, padx=(0, 10), pady=(0, 5))
        
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
        semester_dropdown.grid(row=0, column=1, pady=(0, 5))
        
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
        """Create the statistics cards section"""
        # Destroy existing stat cards frame if it exists
        if hasattr(self, 'stat_cards_frame') and self.stat_cards_frame:
            self.stat_cards_frame.destroy()
        
        self.stat_cards_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
        self.stat_cards_frame.pack(fill="x", padx=30, pady=(20, 0))
        
        card_data = [
            (str(self.stats['total_students']), "Total Students"),
            (self.stats['attendance_rate'], "Total Attendance Rate"),
            (str(self.stats['total_courses']), "Number of Courses"),
            (str(self.stats['total_absents']), "Total Absents")
        ]
        
        for value, label in card_data:
            card = ctk.CTkFrame(self.stat_cards_frame, fg_color="#fff", width=180, height=100, corner_radius=12)
            card.pack(side="left", padx=15, pady=0)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=22, weight="bold"), text_color="#222").pack(anchor="w", padx=18, pady=(18, 0))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11), text_color="#757575").pack(anchor="w", padx=18, pady=(0, 10))

    def create_charts_section(self):
        """Create the charts section"""
        # Destroy existing charts frame if it exists
        if hasattr(self, 'charts_frame') and self.charts_frame:
            self.charts_frame.destroy()
        
        # Graphs section
        self.charts_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=12)
        self.charts_frame.pack(fill="x", padx=30, pady=25)
        
        # Remove "Data Analytics" title
        
        # Charts container - adjust padding since we removed title
        charts_container = ctk.CTkFrame(self.charts_frame, fg_color="transparent", height=320)
        charts_container.pack(fill="x", padx=25, pady=(20, 20))
        charts_container.pack_propagate(False)
        
        # Left side - Pie Chart (Demographics) - balanced width
        demo_frame = ctk.CTkFrame(charts_container, fg_color="#F8F9FA", corner_radius=8, width=270)
        demo_frame.pack(side="left", fill="y", padx=(0, 15))
        demo_frame.pack_propagate(False)
        
        # Create pie chart
        self.create_pie_chart(demo_frame)
        
        # Right side - Key Metrics Cards - optimal width for 5 cards
        metrics_frame = ctk.CTkFrame(charts_container, fg_color="#F8F9FA", corner_radius=8, width=550)
        metrics_frame.pack(side="right", fill="y", padx=(15, 0))
        metrics_frame.pack_propagate(False)
        
        # Create data cards with improved design
        self.create_data_cards(metrics_frame)

    def create_bar_chart_section(self):
        """Create the bar chart section"""
        # Destroy existing bar chart frame if it exists
        if hasattr(self, 'bar_chart_frame') and self.bar_chart_frame:
            self.bar_chart_frame.destroy()
        
        # Bar Chart section (full width below)
        self.bar_chart_frame = ctk.CTkFrame(self, fg_color="#fff", corner_radius=12)
        self.bar_chart_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        # Remove "Detailed Monthly Analysis" title
        
        # Bar chart container - adjust padding since we removed title
        bar_container = ctk.CTkFrame(self.bar_chart_frame, fg_color="#F8F9FA", corner_radius=8, height=320)
        bar_container.pack(fill="both", expand=True, padx=25, pady=(20, 25))
        bar_container.pack_propagate(False)
        
        # Create bar chart
        self.create_bar_chart(bar_container)

    def create_pie_chart(self, parent):
        # Use real data if available
        if hasattr(self, 'stats'):
            present_count = self.stats.get('total_present', 0)
            late_count = self.stats.get('total_late', 0)
            absent_count = self.stats.get('total_absents', 0)
        else:
            # Fallback data
            present_count = 240
            late_count = 30
            absent_count = 30
        
        # Check if we have any data to display
        total_data = present_count + late_count + absent_count
        if total_data == 0:
            # Display a message when no data is available
            fig, ax = plt.subplots(figsize=(2.8, 2.5))
            fig.patch.set_facecolor('#F8F9FA')
            
            ax.text(0.5, 0.5, 'No attendance\ndata available', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12, color='#666666')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        else:
            fig, ax = plt.subplots(figsize=(2.8, 2.5))
            fig.patch.set_facecolor('#F8F9FA')
            
            labels = ['Present', 'Late', 'Absents']
            sizes = [present_count, late_count, absent_count]
            colors = ['#10B981', '#F59E0B', '#EF4444']  # Green for present, yellow for late, red for absents
            
            # Filter out zero values to avoid division by zero
            filtered_labels = []
            filtered_sizes = []
            filtered_colors = []
            
            for i, size in enumerate(sizes):
                if size > 0:
                    filtered_labels.append(labels[i])
                    filtered_sizes.append(size)
                    filtered_colors.append(colors[i])
            
            if filtered_sizes:  # Only create pie chart if we have data
                ax.pie(filtered_sizes, labels=filtered_labels, colors=filtered_colors, 
                      autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9})
            else:
                ax.text(0.5, 0.5, 'No attendance\ndata available', 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12, color='#666666')
                ax.axis('off')
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=5, padx=10, expand=True)
        
        plt.close(fig)

    def create_data_cards(self, parent):
        # Get real metrics data from database
        if self.db_manager:
            # Get filter values
            academic_year = None if self.year_var.get() == "All Years" else self.year_var.get()
            semester = None if self.semester_var.get() == "All Semesters" else self.semester_var.get()
            
            success, metrics = self.db_manager.get_program_key_metrics(
                self.program_data.get('id'),
                academic_year=academic_year,
                semester=semester
            )
            
            if success:
                card_data = [
                    ("Current Month", metrics.get('current_month', '0%'), "#10B981", "📅"),
                    ("Previous Month", metrics.get('previous_month', '0%'), "#3B82F6", "📊"),
                    ("Best Month", metrics.get('best_month', '0%'), "#059669", "🏆"),
                    ("Lowest Month", metrics.get('lowest_month', '0%'), "#EF4444", "📉"),
                    ("Most Active Day", metrics.get('most_active_day', 'N/A'), "#8B5CF6", "📆")
                ]
            else:
                # Fallback data if database query fails
                card_data = [
                    ("Current Month", "0%", "#10B981", "📅"),
                    ("Previous Month", "0%", "#3B82F6", "📊"),
                    ("Best Month", "0%", "#059669", "🏆"),
                    ("Lowest Month", "0%", "#EF4444", "📉"),
                    ("Most Active Day", "N/A", "#8B5CF6", "📆")
                ]
        else:
            # Default fallback data for testing
            card_data = [
                ("Current Month", "92% (Dec 2024)", "#10B981", "📅"),
                ("Previous Month", "88% (Nov 2024)", "#3B82F6", "📊"),
                ("Best Month", "96% (Sep 2024)", "#059669", "🏆"),
                ("Lowest Month", "78% (Aug 2024)", "#EF4444", "📉"),
                ("Most Active Day", "Monday", "#8B5CF6", "📆")
            ]
        
        # Balanced top spacing
        top_spacer = ctk.CTkFrame(parent, fg_color="transparent", height=25)
        top_spacer.pack(fill="x")
        
        for i, (label, value, color, icon) in enumerate(card_data):
            # Optimized card design with better proportions
            card_frame = ctk.CTkFrame(
                parent, 
                fg_color="#FFFFFF", 
                corner_radius=12, 
                height=48,
                border_width=1,
                border_color="#E5E7EB"
            )
            card_frame.pack(fill="x", padx=22, pady=6)
            card_frame.pack_propagate(False)
            
            # Left section with improved spacing
            left_section = ctk.CTkFrame(card_frame, fg_color="transparent")
            left_section.pack(side="left", fill="y", padx=(18, 0))
            
            # Icon with refined size and design
            icon_frame = ctk.CTkFrame(
                left_section, 
                fg_color=color, 
                width=34, 
                height=34, 
                corner_radius=17
            )
            icon_frame.pack(side="left", pady=7)
            icon_frame.pack_propagate(False)
            
            # Icon with perfect centering
            ctk.CTkLabel(
                icon_frame,
                text=icon,
                font=ctk.CTkFont(size=15),
                text_color="white"
            ).place(relx=0.5, rely=0.5, anchor="center")
            
            # Label with refined typography
            ctk.CTkLabel(
                left_section,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#374151"
            ).pack(side="left", padx=(16, 0), anchor="w")
            
            # Value with optimized text handling
            value_label = ctk.CTkLabel(
                card_frame,
                text=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#111827",
                wraplength=220,  # Generous wrap length for long text
                justify="right"
            )
            value_label.pack(side="right", padx=(8, 22), anchor="e")
        
        # Balanced bottom spacing
        bottom_spacer = ctk.CTkFrame(parent, fg_color="transparent", height=20)
        bottom_spacer.pack(fill="x")

    def create_bar_chart(self, parent):
        # Get real data from database if available
        if self.db_manager:
            # Get filter values
            academic_year = None if self.year_var.get() == "All Years" else self.year_var.get()
            semester = None if self.semester_var.get() == "All Semesters" else self.semester_var.get()
            
            success, chart_data = self.db_manager.get_program_monthly_attendance(
                self.program_data.get('id'),
                academic_year=academic_year,
                semester=semester
            )
            
            if success and chart_data:
                # The database already returns filtered data based on semester selection
                # So we use the data as-is without further filtering
                months = chart_data.get('months', [])
                year_levels = chart_data.get('year_levels', [])
                data = chart_data.get('data', {})
                
                # If no data found for the selected filters, show appropriate message
                if not months or not data:
                    current_semester = self.semester_var.get()
                    if current_semester != "All Semesters":
                        months = [f'No data for {current_semester}']
                    else:
                        months = ['No data available']
                    year_levels = ['No Data']
                    data = {'No Data': [0]}
            else:
                # Fallback to sample data - these are just for demonstration
                current_semester = self.semester_var.get()
                
                if current_semester == "1st Semester":
                    months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan']
                    data = {
                        '1st Year': [89, 91, 88, 86, 85],
                        '2nd Year': [84, 86, 83, 81, 78],
                        '3rd Year': [94, 96, 94, 92, 92],
                        '4th Year': [90, 92, 90, 88, 88]
                    }
                elif current_semester == "2nd Semester":
                    months = ['Feb', 'Mar', 'Apr', 'May', 'Jun']
                    data = {
                        '1st Year': [88, 92, 89, 86, 90],
                        '2nd Year': [82, 85, 88, 84, 87],
                        '3rd Year': [94, 96, 93, 91, 95],
                        '4th Year': [90, 92, 89, 87, 91]
                    }
                elif current_semester == "Summer":
                    months = ['Jul', 'Aug']
                    data = {
                        '1st Year': [87, 85],
                        '2nd Year': [83, 80],
                        '3rd Year': [93, 91],
                        '4th Year': [89, 87]
                    }
                else:  # All Semesters
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    data = {
                        '1st Year': [85, 88, 92, 89, 86, 90, 87, 85, 89, 91, 88, 86],
                        '2nd Year': [78, 82, 85, 88, 84, 87, 83, 80, 84, 86, 83, 81],
                        '3rd Year': [92, 94, 96, 93, 91, 95, 93, 91, 94, 96, 94, 92],
                        '4th Year': [88, 90, 92, 89, 87, 91, 89, 87, 90, 92, 90, 88]
                    }
                
                year_levels = ['1st Year', '2nd Year', '3rd Year', '4th Year']
        else:
            # Fallback data for testing when no database connection
            months = ['Dynamic months based on actual school calendar']
            year_levels = ['Sample Data']
            data = {'Sample Data': [85]}
        
        fig, ax = plt.subplots(figsize=(12, 4.5))
        fig.patch.set_facecolor('#F8F9FA')
        
        x = np.arange(len(months))
        width = 0.2
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
        
        # Only plot data for year levels that exist in the data
        plotted_levels = []
        for i, year_level in enumerate(year_levels):
            if year_level in data and data[year_level]:
                rates = data[year_level]
                ax.bar(x + i * width, rates, width, label=year_level, color=colors[i % len(colors)])
                plotted_levels.append(year_level)
        
        ax.set_xlabel('Month', fontsize=11)
        ax.set_ylabel('Attendance Rate (%)', fontsize=11)
        
        # Dynamic title based on semester
        current_semester = self.semester_var.get()
        if current_semester != "All Semesters":
            title = f'Monthly Attendance by Year Level - {current_semester}'
        else:
            title = 'Monthly Attendance by Year Level'
        
        ax.set_title(title, fontsize=16, pad=25, weight='bold')
        ax.set_xticks(x + width * (len(plotted_levels) - 1) / 2)
        ax.set_xticklabels(months, fontsize=10)
        
        if plotted_levels and not months[0].startswith('No data'):
            ax.legend(fontsize=9, loc='upper right')
        
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)  # Set to 0-100 for percentage data
        
        plt.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20, padx=20, fill="both", expand=True)
        
        plt.close(fig)

    def on_filter_change(self, value=None):
        """Called when year or semester selection changes"""
        self.load_statistics()
        self.refresh_charts()

    def load_statistics(self):
        """Load statistics based on current filter selections"""
        if self.db_manager:
            # Get filter values
            academic_year = None if self.year_var.get() == "All Years" else self.year_var.get()
            semester = None if self.semester_var.get() == "All Semesters" else self.semester_var.get()
            
            success, stats = self.db_manager.get_program_statistics(
                self.program_data.get('id'), 
                academic_year=academic_year, 
                semester=semester
            )
            if success:
                self.stats = stats
            else:
                # Fallback to default stats
                self.stats = {
                    'total_students': 0,
                    'attendance_rate': '0%',
                    'total_courses': 0,
                    'total_absents': 0,
                    'total_present': 0,
                    'total_late': 0
                }
        else:
            # Default stats for testing
            self.stats = {
                'total_students': 300,
                'attendance_rate': '90%',
                'total_courses': 15,
                'total_absents': 0,
                'total_present': 450,
                'total_late': 51
            }

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
        print(f"New stats: Students: {self.stats['total_students']}, Attendance: {self.stats['attendance_rate']}")
