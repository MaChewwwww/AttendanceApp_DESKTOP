import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime, timedelta
from app.ui.admin.components.sidebar import DateTimePill

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        # Get database manager from parent or create new one
        self.db_manager = getattr(parent, 'db_manager', None)
        if not self.db_manager:
            try:
                from app.db_manager import DatabaseManager
                self.db_manager = DatabaseManager()
            except Exception as e:
                print(f"Error creating database manager: {e}")
                self.db_manager = None
        
        self.dashboard_data = {}
        
        self.setup_ui()
        # Load data after UI is set up
        self.after(100, self.load_dashboard_data)

    def load_dashboard_data(self):
        """Load all dashboard data from database"""
        try:
            if not self.db_manager:
                print("No database manager available")
                # Set default values
                self.dashboard_data = {
                    'total_students': 0,
                    'total_faculty': 0,
                    'total_courses': 0,
                    'total_programs': 0,
                    'total_sections': 0,
                    'attendance_overview': {},
                    'monthly_attendance': {'months': [], 'rates': []},
                    'program_enrollment': {'programs': [], 'counts': [], 'colors': []},
                    'section_performance': {'sections': [], 'rates': []},
                    'recent_activity': {'new_users_week': 0, 'today_attendance': 0}
                }
                self.update_metric_cards()
                self.update_charts()
                return
            
            # Get key metrics
            self.dashboard_data = {
                'total_students': self.get_total_students(),
                'total_faculty': self.get_total_faculty(),
                'total_courses': self.get_total_courses(),
                'total_programs': self.get_total_programs(),
                'total_sections': self.get_total_sections(),
                'attendance_overview': self.get_attendance_overview(),
                'monthly_attendance': self.get_monthly_attendance_data(),
                'program_enrollment': self.get_program_enrollment_data(),
                'section_performance': self.get_section_performance_data(),
                'recent_activity': self.get_recent_activity()
            }
            
            print(f"Loaded dashboard data: {self.dashboard_data}")
            
            # Update UI with loaded data
            self.update_metric_cards()
            self.update_charts()
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            # Set default values on error
            self.dashboard_data = {
                'total_students': 0,
                'total_faculty': 0,
                'total_courses': 0,
                'total_programs': 0,
                'total_sections': 0,
                'attendance_overview': {},
                'monthly_attendance': {'months': [], 'rates': []},
                'program_enrollment': {'programs': [], 'counts': [], 'colors': []},
                'section_performance': {'sections': [], 'rates': []},
                'recent_activity': {'new_users_week': 0, 'today_attendance': 0}
            }
            self.update_metric_cards()
            self.update_charts()

    def get_total_students(self):
        """Get total number of active students"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM users u
                JOIN students s ON u.id = s.user_id
                WHERE u.role = 'Student' AND (u.isDeleted = 0 OR u.isDeleted IS NULL)
            """)
            result = cursor.fetchone()
            conn.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting total students: {e}")
            return 0

    def get_total_faculty(self):
        """Get total number of active faculty"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM users u
                JOIN faculties f ON u.id = f.user_id
                WHERE u.role = 'Faculty' AND (u.isDeleted = 0 OR u.isDeleted IS NULL)
            """)
            result = cursor.fetchone()
            conn.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting total faculty: {e}")
            return 0

    def get_total_courses(self):
        """Get total number of active courses"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM courses 
                WHERE isDeleted = 0 OR isDeleted IS NULL
            """)
            result = cursor.fetchone()
            conn.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting total courses: {e}")
            return 0

    def get_total_programs(self):
        """Get total number of active programs"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM programs 
                WHERE isDeleted = 0 OR isDeleted IS NULL
            """)
            result = cursor.fetchone()
            conn.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting total programs: {e}")
            return 0

    def get_total_sections(self):
        """Get total number of active sections"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM sections s
                WHERE s.isDeleted = 0 OR s.isDeleted IS NULL
            """)
            result = cursor.fetchone()
            conn.close()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error getting total sections: {e}")
            return 0

    def get_attendance_overview(self):
        """Get overall attendance statistics"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_logs,
                    SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count,
                    SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                    SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) as late_count
                FROM attendance_logs
                WHERE date >= datetime('now', '-30 days')
            """)
            result = cursor.fetchone()
            conn.close()
            
            if result and result['total_logs'] > 0:
                total = result['total_logs']
                present = result['present_count']
                absent = result['absent_count']
                late = result['late_count']
                
                return {
                    'total_logs': total,
                    'present_rate': round((present / total) * 100, 1),
                    'absent_rate': round((absent / total) * 100, 1),
                    'late_rate': round((late / total) * 100, 1),
                    'present_count': present,
                    'absent_count': absent,
                    'late_count': late
                }
            else:
                return {
                    'total_logs': 0,
                    'present_rate': 0,
                    'absent_rate': 0,
                    'late_rate': 0,
                    'present_count': 0,
                    'absent_count': 0,
                    'late_count': 0
                }
        except Exception as e:
            print(f"Error getting attendance overview: {e}")
            return {
                'total_logs': 0,
                'present_rate': 0,
                'absent_rate': 0,
                'late_rate': 0,
                'present_count': 0,
                'absent_count': 0,
                'late_count': 0
            }

    def get_monthly_attendance_data(self):
        """Get monthly attendance data for the last 6 months"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT 
                    strftime('%Y-%m', date) as month,
                    COUNT(*) as total_logs,
                    SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present_count
                FROM attendance_logs
                WHERE date >= datetime('now', '-6 months')
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month
            """)
            results = cursor.fetchall()
            conn.close()
            
            months = []
            attendance_rates = []
            
            for row in results:
                month_str = row['month']
                total = row['total_logs']
                present = row['present_count']
                
                # Convert month to readable format
                try:
                    month_obj = datetime.strptime(month_str, '%Y-%m')
                    month_name = month_obj.strftime('%b %Y')
                    months.append(month_name)
                    
                    if total > 0:
                        rate = (present / total) * 100
                        attendance_rates.append(round(rate, 1))
                    else:
                        attendance_rates.append(0)
                except:
                    continue
            
            return {'months': months, 'rates': attendance_rates}
            
        except Exception as e:
            print(f"Error getting monthly attendance data: {e}")
            return {'months': [], 'rates': []}

    def get_program_enrollment_data(self):
        """Get student enrollment data by program"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT 
                    p.name as program_name,
                    p.acronym,
                    COUNT(u.id) as student_count
                FROM programs p
                LEFT JOIN sections s ON p.id = s.program_id
                LEFT JOIN students st ON s.id = st.section
                LEFT JOIN users u ON st.user_id = u.id AND (u.isDeleted = 0 OR u.isDeleted IS NULL)
                WHERE p.isDeleted = 0 OR p.isDeleted IS NULL
                GROUP BY p.id, p.name, p.acronym
                HAVING COUNT(u.id) > 0
                ORDER BY student_count DESC
            """)
            results = cursor.fetchall()
            conn.close()
            
            programs = []
            counts = []
            colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899']
            
            for i, row in enumerate(results):
                program_name = row['acronym'] or row['program_name']
                programs.append(program_name)
                counts.append(row['student_count'])
            
            return {'programs': programs, 'counts': counts, 'colors': colors[:len(programs)]}
            
        except Exception as e:
            print(f"Error getting program enrollment data: {e}")
            return {'programs': [], 'counts': [], 'colors': []}

    def get_section_performance_data(self):
        """Get top performing sections by attendance rate"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.execute("""
                SELECT 
                    s.name as section_name,
                    p.acronym as program_acronym,
                    COUNT(al.id) as total_logs,
                    SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as present_count
                FROM sections s
                JOIN programs p ON s.program_id = p.id
                JOIN assigned_courses ac ON s.id = ac.section_id
                JOIN attendance_logs al ON ac.id = al.assigned_course_id
                WHERE (ac.isDeleted = 0 OR ac.isDeleted IS NULL) 
                  AND (s.isDeleted = 0 OR s.isDeleted IS NULL)
                GROUP BY s.id, s.name, p.acronym
                HAVING COUNT(al.id) >= 5
                ORDER BY (CAST(SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(al.id)) DESC
                LIMIT 10
            """)
            results = cursor.fetchall()
            conn.close()
            
            sections = []
            rates = []
            
            for row in results:
                section_name = f"{row['program_acronym']} {row['section_name']}"
                sections.append(section_name)
                
                total = row['total_logs']
                present = row['present_count']
                if total > 0:
                    rate = (present / total) * 100
                    rates.append(round(rate, 1))
                else:
                    rates.append(0)
            
            return {'sections': sections, 'rates': rates}
            
        except Exception as e:
            print(f"Error getting section performance data: {e}")
            return {'sections': [], 'rates': []}

    def get_recent_activity(self):
        """Get recent activity summary"""
        try:
            conn = self.db_manager.get_connection()
            
            # Get recent registrations
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM users 
                WHERE created_at >= datetime('now', '-7 days') 
                  AND (isDeleted = 0 OR isDeleted IS NULL)
            """)
            new_users = cursor.fetchone()['count'] or 0
            
            # Get today's attendance logs
            cursor = conn.execute("""
                SELECT COUNT(*) as count 
                FROM attendance_logs 
                WHERE date(date) = date('now')
            """)
            today_attendance = cursor.fetchone()['count'] or 0
            
            conn.close()
            
            return {
                'new_users_week': new_users,
                'today_attendance': today_attendance
            }
            
        except Exception as e:
            print(f"Error getting recent activity: {e}")
            return {'new_users_week': 0, 'today_attendance': 0}

    def setup_ui(self):
        # Top bar for the DateTimePill with reduced spacing
        topbar = ctk.CTkFrame(self, fg_color="transparent")
        topbar.pack(fill="x", pady=(5, 0), padx=5)  # Reduced padding
        topbar.grid_columnconfigure(0, weight=1)
        pill = DateTimePill(topbar)
        pill.grid(row=0, column=1, sticky="e")

        # Header with reduced spacing
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=5, pady=(5, 15))  # Reduced padding
        
        ctk.CTkLabel(
            header_frame,
            text="Admin Dashboard",
            font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
            text_color="#1F2937",
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Comprehensive overview of key metrics and system performance",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#6B7280",
            anchor="w"
        ).pack(anchor="w", pady=(3, 0))

        # Create scrollable frame with minimal padding since parent handles margins
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color="#E5E7EB",
            scrollbar_button_hover_color="#D1D5DB"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))  # Minimal padding

        # Metrics cards section with reduced spacing
        self.create_metrics_section()
        
        # Charts section with optimized layout
        self.create_charts_section()

    def create_metrics_section(self):
        """Create the metrics cards section with optimized spacing"""
        # Metrics container with reduced spacing
        metrics_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        metrics_container.pack(fill="x", pady=(0, 25))
        
        # Card grid with perfect symmetry - minimal padding since parent handles margins
        card_grid = ctk.CTkFrame(metrics_container, fg_color="transparent")
        card_grid.pack(fill="x", padx=0)  # No additional padding
        
        # Configure grid with equal weights for perfect symmetry
        for c in range(4):
            card_grid.grid_columnconfigure(c, weight=1, uniform="cards")
        
        # Create metric cards with optimized dimensions
        self.metric_cards = {}
        metrics_info = [
            ("students", "Total Students", "#3B82F6", "👥"),
            ("faculty", "Total Faculty", "#10B981", "👨‍🏫"),
            ("courses", "Active Courses", "#F59E0B", "📚"),
            ("programs", "Programs", "#8B5CF6", "🎓")
        ]
        
        for idx, (key, label, color, icon) in enumerate(metrics_info):
            card = self.create_metric_card(card_grid, "0", label, color, icon)
            card.grid(row=0, column=idx, padx=8, pady=8, sticky="nsew")
            self.metric_cards[key] = card

    def create_metric_card(self, parent, value, label, color, icon):
        """Create an optimized metric card"""
        card = ctk.CTkFrame(
            parent, 
            fg_color="#FFFFFF", 
            corner_radius=12, 
            border_width=1, 
            border_color="#E5E7EB",
            height=120  # Reduced from 140
        )
        card.grid_propagate(False)
        
        # Main content frame with optimized padding
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=16)
        
        # Top section with icon and indicator
        top_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_section.pack(fill="x", pady=(0, 12))
        
        # Icon container - slightly smaller
        icon_container = ctk.CTkFrame(
            top_section,
            fg_color=color,
            width=40,
            height=40,
            corner_radius=20
        )
        icon_container.pack(side="left")
        icon_container.pack_propagate(False)
        
        # Icon
        ctk.CTkLabel(
            icon_container,
            text=icon,
            font=ctk.CTkFont(size=20),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Colored indicator line
        indicator = ctk.CTkFrame(
            top_section, 
            fg_color=color, 
            height=3, 
            corner_radius=2
        )
        indicator.pack(side="right", fill="x", expand=True, padx=(12, 0))
        
        # Value section
        value_label = ctk.CTkLabel(
            content_frame,
            text=value,
            font=ctk.CTkFont(family="Inter", size=28, weight="bold"),  # Reduced from 36
            text_color="#1F2937"
        )
        value_label.pack(anchor="w")
        
        # Label section
        label_widget = ctk.CTkLabel(
            content_frame,
            text=label,
            font=ctk.CTkFont(family="Inter", size=12, weight="normal"),  # Reduced from 14
            text_color="#6B7280"
        )
        label_widget.pack(anchor="w", pady=(6, 0))
        
        # Store references for updating
        card.value_label = value_label
        card.label_widget = label_widget
        
        return card

    def create_charts_section(self):
        """Create the charts section with optimized 2x2 grid layout"""
        charts_container = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        charts_container.pack(fill="x", pady=(0, 20))
        
        # Charts grid with perfect 2x2 symmetry - minimal padding since parent handles margins
        charts_grid = ctk.CTkFrame(charts_container, fg_color="transparent")
        charts_grid.pack(fill="x", padx=0)  # No additional padding
        
        # Configure grid for perfect symmetry
        for i in range(2):
            charts_grid.grid_columnconfigure(i, weight=1, uniform="charts")
            charts_grid.grid_rowconfigure(i, weight=1, uniform="charts")
        
        # Create chart containers with optimized sizing
        self.create_attendance_overview_chart(charts_grid)
        self.create_monthly_attendance_chart(charts_grid)
        self.create_program_enrollment_chart(charts_grid)
        self.create_section_performance_chart(charts_grid)

    def create_attendance_overview_chart(self, parent):
        """Create attendance overview pie chart with optimized design"""
        chart_frame = ctk.CTkFrame(
            parent, 
            fg_color="#FFFFFF", 
            corner_radius=12, 
            border_width=1, 
            border_color="#E5E7EB",
            height=280  # Reduced from 320
        )
        chart_frame.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        chart_frame.grid_propagate(False)
        
        # Chart title - more compact
        title_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Attendance Overview",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),  # Reduced from 16
            text_color="#1F2937"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Last 30 days distribution",
            font=ctk.CTkFont(family="Inter", size=11),  # Reduced from 12
            text_color="#6B7280"
        ).pack(anchor="w", pady=(1, 0))
        
        # Chart canvas container
        self.attendance_chart_container = ctk.CTkFrame(chart_frame, fg_color="transparent")
        self.attendance_chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_monthly_attendance_chart(self, parent):
        """Create monthly attendance trend line chart with optimized design"""
        chart_frame = ctk.CTkFrame(
            parent, 
            fg_color="#FFFFFF", 
            corner_radius=12, 
            border_width=1, 
            border_color="#E5E7EB",
            height=280  # Reduced from 320
        )
        chart_frame.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        chart_frame.grid_propagate(False)
        
        # Chart title - more compact
        title_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Attendance Trends",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1F2937"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Monthly performance tracking",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(1, 0))
        
        # Chart canvas container
        self.monthly_chart_container = ctk.CTkFrame(chart_frame, fg_color="transparent")
        self.monthly_chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_program_enrollment_chart(self, parent):
        """Create program enrollment bar chart with optimized design"""
        chart_frame = ctk.CTkFrame(
            parent, 
            fg_color="#FFFFFF", 
            corner_radius=12, 
            border_width=1, 
            border_color="#E5E7EB",
            height=280  # Reduced from 320
        )
        chart_frame.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        chart_frame.grid_propagate(False)
        
        # Chart title - more compact
        title_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Program Enrollment",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1F2937"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Student distribution by program",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(1, 0))
        
        # Chart canvas container
        self.enrollment_chart_container = ctk.CTkFrame(chart_frame, fg_color="transparent")
        self.enrollment_chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def create_section_performance_chart(self, parent):
        """Create section performance horizontal bar chart with optimized design"""
        chart_frame = ctk.CTkFrame(
            parent, 
            fg_color="#FFFFFF", 
            corner_radius=12, 
            border_width=1, 
            border_color="#E5E7EB",
            height=280  # Reduced from 320
        )
        chart_frame.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")
        chart_frame.grid_propagate(False)
        
        # Chart title - more compact
        title_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            title_frame,
            text="Top Performers",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1F2937"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Highest attendance rates by section",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#6B7280"
        ).pack(anchor="w", pady=(1, 0))
        
        # Chart canvas container
        self.performance_chart_container = ctk.CTkFrame(chart_frame, fg_color="transparent")
        self.performance_chart_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def update_metric_cards(self):
        """Update metric cards with loaded data"""
        try:
            # Update student count
            if 'students' in self.metric_cards:
                self.metric_cards['students'].value_label.configure(text=str(self.dashboard_data.get('total_students', 0)))
            
            # Update faculty count
            if 'faculty' in self.metric_cards:
                self.metric_cards['faculty'].value_label.configure(text=str(self.dashboard_data.get('total_faculty', 0)))
            
            # Update courses count
            if 'courses' in self.metric_cards:
                self.metric_cards['courses'].value_label.configure(text=str(self.dashboard_data.get('total_courses', 0)))
            
            # Update programs count
            if 'programs' in self.metric_cards:
                self.metric_cards['programs'].value_label.configure(text=str(self.dashboard_data.get('total_programs', 0)))
                
            print("Metric cards updated successfully")
                
        except Exception as e:
            print(f"Error updating metric cards: {e}")

    def update_charts(self):
        """Update all charts with loaded data"""
        try:
            self.update_attendance_overview_chart()
            self.update_monthly_attendance_chart()
            self.update_program_enrollment_chart()
            self.update_section_performance_chart()
        except Exception as e:
            print(f"Error updating charts: {e}")

    def update_attendance_overview_chart(self):
        """Update attendance overview pie chart with optimized styling"""
        try:
            # Clear existing chart
            for widget in self.attendance_chart_container.winfo_children():
                widget.destroy()
            
            attendance_data = self.dashboard_data.get('attendance_overview', {})
            
            if not attendance_data or attendance_data.get('total_logs', 0) == 0:
                # Enhanced no data message
                no_data_frame = ctk.CTkFrame(self.attendance_chart_container, fg_color="transparent")
                no_data_frame.pack(expand=True)
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="📊",
                    font=ctk.CTkFont(size=28),  # Reduced from 32
                    text_color="#D1D5DB"
                ).pack(pady=(15, 8))
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="No attendance data available",
                    font=ctk.CTkFont(family="Inter", size=12, weight="normal"),  # Reduced from 14
                    text_color="#6B7280"
                ).pack()
                return
            
            # Create optimized pie chart
            fig, ax = plt.subplots(figsize=(4.5, 3))  # Reduced from (5, 3.5)
            fig.patch.set_facecolor('#ffffff')
            
            labels = ['Present', 'Absent', 'Late']
            sizes = [
                attendance_data.get('present_count', 0),
                attendance_data.get('absent_count', 0),
                attendance_data.get('late_count', 0)
            ]
            colors = ['#22C55E', '#EF4444', '#F59E0B']
            
            # Filter out zero values
            filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
            
            if filtered_data:
                labels, sizes, colors = zip(*filtered_data)
                
                # Enhanced pie chart styling
                wedges, texts, autotexts = ax.pie(
                    sizes, 
                    labels=labels, 
                    colors=colors, 
                    autopct='%1.1f%%', 
                    startangle=90,
                    textprops={'fontsize': 9, 'fontweight': 'normal'},  # Reduced from 10
                    wedgeprops=dict(width=0.8, edgecolor='white', linewidth=2)
                )
                
                # Enhanced text styling
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(10)
                
                for text in texts:
                    text.set_fontsize(9)
                    text.set_fontweight('normal')
                    text.set_color('#374151')
            
            plt.tight_layout()
            
            # Embed chart
            canvas = FigureCanvasTkAgg(fig, self.attendance_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
            
        except Exception as e:
            print(f"Error updating attendance overview chart: {e}")

    def update_monthly_attendance_chart(self):
        """Update monthly attendance trend chart with optimized styling"""
        try:
            # Clear existing chart
            for widget in self.monthly_chart_container.winfo_children():
                widget.destroy()
            
            monthly_data = self.dashboard_data.get('monthly_attendance', {})
            months = monthly_data.get('months', [])
            rates = monthly_data.get('rates', [])
            
            if not months or not rates:
                # Enhanced no data message
                no_data_frame = ctk.CTkFrame(self.monthly_chart_container, fg_color="transparent")
                no_data_frame.pack(expand=True)
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="📈",
                    font=ctk.CTkFont(size=28),
                    text_color="#D1D5DB"
                ).pack(pady=(15, 8))
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="No monthly data available",
                    font=ctk.CTkFont(family="Inter", size=12, weight="normal"),
                    text_color="#6B7280"
                ).pack()
                return
            
            # Create optimized line chart
            fig, ax = plt.subplots(figsize=(4.5, 3))  # Reduced from (5, 3.5)
            fig.patch.set_facecolor('#ffffff')
            
            # Enhanced line styling
            ax.plot(months, rates, marker='o', linewidth=3, markersize=6,  # Reduced markersize from 8
                   color='#3B82F6', markerfacecolor='#3B82F6', 
                   markeredgecolor='white', markeredgewidth=2)
            ax.fill_between(months, rates, alpha=0.2, color='#3B82F6')
            
            # Enhanced styling
            ax.set_ylabel('Attendance Rate (%)', fontsize=10, fontweight='normal', color='#374151')  # Reduced from 11
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, color='#E5E7EB', linewidth=1)
            ax.set_facecolor('#FAFAFA')
            
            # Style axes
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#E5E7EB')
            ax.spines['bottom'].set_color('#E5E7EB')
            
            # Rotate x-axis labels if too many
            if len(months) > 4:
                plt.xticks(rotation=45, fontsize=8, color='#6B7280')  # Reduced from 9
            else:
                plt.xticks(fontsize=9, color='#6B7280')  # Reduced from 10
            
            plt.yticks(fontsize=8, color='#6B7280')  # Reduced from 9
            plt.tight_layout()
            
            # Embed chart
            canvas = FigureCanvasTkAgg(fig, self.monthly_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
            
        except Exception as e:
            print(f"Error updating monthly attendance chart: {e}")

    def update_program_enrollment_chart(self):
        """Update program enrollment bar chart with optimized styling"""
        try:
            # Clear existing chart
            for widget in self.enrollment_chart_container.winfo_children():
                widget.destroy()
            
            enrollment_data = self.dashboard_data.get('program_enrollment', {})
            programs = enrollment_data.get('programs', [])
            counts = enrollment_data.get('counts', [])
            colors = enrollment_data.get('colors', [])
            
            if not programs or not counts:
                # Enhanced no data message
                no_data_frame = ctk.CTkFrame(self.enrollment_chart_container, fg_color="transparent")
                no_data_frame.pack(expand=True)
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="🎓",
                    font=ctk.CTkFont(size=28),
                    text_color="#D1D5DB"
                ).pack(pady=(15, 8))
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="No enrollment data available",
                    font=ctk.CTkFont(family="Inter", size=12, weight="normal"),
                    text_color="#6B7280"
                ).pack()
                return
            
            # Create optimized bar chart
            fig, ax = plt.subplots(figsize=(4.5, 3))  # Reduced from (5, 3.5)
            fig.patch.set_facecolor('#ffffff')
            
            # Enhanced bar styling
            bars = ax.bar(programs, counts, color=colors[:len(programs)], 
                         alpha=0.8, edgecolor='white', linewidth=1.5)
            
            # Add value labels on bars with enhanced styling
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{int(height)}',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),
                           textcoords="offset points",
                           ha='center', va='bottom', 
                           fontweight='bold', fontsize=9, color='#374151')  # Reduced from 10
            
            # Enhanced styling
            ax.set_ylabel('Number of Students', fontsize=10, fontweight='normal', color='#374151')  # Reduced from 11
            ax.grid(True, alpha=0.3, axis='y', color='#E5E7EB', linewidth=1)
            ax.set_facecolor('#FAFAFA')
            
            # Style axes
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#E5E7EB')
            ax.spines['bottom'].set_color('#E5E7EB')
            
            plt.xticks(fontsize=9, color='#6B7280', fontweight='normal')  # Reduced from 10
            plt.yticks(fontsize=8, color='#6B7280')  # Reduced from 9
            plt.tight_layout()
            
            # Embed chart
            canvas = FigureCanvasTkAgg(fig, self.enrollment_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
            
        except Exception as e:
            print(f"Error updating program enrollment chart: {e}")

    def update_section_performance_chart(self):
        """Update section performance horizontal bar chart with optimized styling"""
        try:
            # Clear existing chart
            for widget in self.performance_chart_container.winfo_children():
                widget.destroy()
            
            performance_data = self.dashboard_data.get('section_performance', {})
            sections = performance_data.get('sections', [])
            rates = performance_data.get('rates', [])
            
            if not sections or not rates:
                # Enhanced no data message
                no_data_frame = ctk.CTkFrame(self.performance_chart_container, fg_color="transparent")
                no_data_frame.pack(expand=True)
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="🏆",
                    font=ctk.CTkFont(size=24),
                    text_color="#D1D5DB"
                ).pack(pady=(10, 5))
                
                ctk.CTkLabel(
                    no_data_frame,
                    text="No performance data available",
                    font=ctk.CTkFont(family="Inter", size=11, weight="normal"),
                    text_color="#6B7280"
                ).pack()
                return
            
            # Limit to top 4 sections for better visibility in smaller space
            sections = sections[:4]
            rates = rates[:4]
            
            # Create optimized horizontal bar chart with smaller figure size
            fig, ax = plt.subplots(figsize=(3.6, 2.4))
            fig.patch.set_facecolor('#ffffff')
            
            # Enhanced color mapping based on performance
            colors = []
            for rate in rates:
                if rate >= 95:
                    colors.append('#059669')  # Excellent - dark green
                elif rate >= 90:
                    colors.append('#22C55E')  # Good - green
                elif rate >= 80:
                    colors.append('#F59E0B')  # Average - yellow
                else:
                    colors.append('#EF4444')  # Poor - red
            
            # Create horizontal bars with reduced height and proper alignment
            bars = ax.barh(sections, rates, color=colors, alpha=0.8, 
                          edgecolor='white', linewidth=1, height=0.6, 
                          align='center')  # Added align='center' for proper alignment
            
            # Add value labels on bars with enhanced styling
            for i, (bar, rate) in enumerate(zip(bars, rates)):
                width = bar.get_width()
                ax.annotate(f'{rate:.1f}%',
                           xy=(width + 1, bar.get_y() + bar.get_height() / 2),
                           xytext=(0, 0),
                           textcoords="offset points",
                           ha='left', va='center', 
                           fontweight='bold', fontsize=7, color='#374151')
            
            # Enhanced styling with proper x-axis starting from 0
            ax.set_xlabel('Attendance Rate (%)', fontsize=9, fontweight='normal', color='#374151')
            ax.set_xlim(0, 105)  # Start from 0 to show full bar lengths
            ax.grid(True, alpha=0.3, axis='x', color='#E5E7EB', linewidth=1)
            ax.set_facecolor('#FAFAFA')
            
            # Style axes
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#E5E7EB')
            ax.spines['bottom'].set_color('#E5E7EB')
            
            plt.yticks(fontsize=7, color='#6B7280', fontweight='normal')
            plt.xticks(fontsize=7, color='#6B7280')
            
            # Adjust layout for section names with tighter margins
            plt.subplots_adjust(left=0.35, right=0.92, top=0.95, bottom=0.15)
            
            # Force x-axis to start at 0
            ax.set_xlim(left=0)
            
            # Embed chart
            canvas = FigureCanvasTkAgg(fig, self.performance_chart_container)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
            
        except Exception as e:
            print(f"Error updating section performance chart: {e}")