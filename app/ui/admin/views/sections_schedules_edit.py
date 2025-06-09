import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, time
from app.ui.admin.components.modals import SuccessModal, DeleteModal

class AddScheduleModal(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, assigned_course_data, on_success=None):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = db_manager
        self.assigned_course_data = assigned_course_data
        self.on_success = on_success
        
        self.title("Add Schedule")
        self.geometry("480x500")
        self.resizable(False, False)
        self.configure(fg_color="#F8FAFC")
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
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            main_container,
            text="Add Schedule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            main_container,
            text=f"Create schedule for {self.assigned_course_data.get('course_name', 'Course')}",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        ).pack(pady=(0, 15))
        
        # Form container
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)
        
        # Day of Week
        ctk.CTkLabel(form_frame, text="Day of Week *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.day_var = ctk.StringVar(value="Select day")
        self.day_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.day_var,
            values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.day_menu.pack(fill="x", pady=(0, 10))
        
        # Start Time
        ctk.CTkLabel(form_frame, text="Start Time *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        time_frame1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame1.pack(fill="x", pady=(0, 10))
        
        self.start_hour_var = ctk.StringVar(value="08")
        self.start_minute_var = ctk.StringVar(value="00")
        self.start_period_var = ctk.StringVar(value="AM")
        
        ctk.CTkOptionMenu(
            time_frame1,
            variable=self.start_hour_var,
            values=[f"{i:02d}" for i in range(1, 13)],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(time_frame1, text=":", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        
        ctk.CTkOptionMenu(
            time_frame1,
            variable=self.start_minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 15)],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkOptionMenu(
            time_frame1,
            variable=self.start_period_var,
            values=["AM", "PM"],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left")
        
        # End Time
        ctk.CTkLabel(form_frame, text="End Time *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        time_frame2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame2.pack(fill="x", pady=(0, 20))
        
        self.end_hour_var = ctk.StringVar(value="09")
        self.end_minute_var = ctk.StringVar(value="00")
        self.end_period_var = ctk.StringVar(value="AM")
        
        ctk.CTkOptionMenu(
            time_frame2,
            variable=self.end_hour_var,
            values=[f"{i:02d}" for i in range(1, 13)],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(time_frame2, text=":", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        
        ctk.CTkOptionMenu(
            time_frame2,
            variable=self.end_minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 15)],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkOptionMenu(
            time_frame2,
            variable=self.end_period_var,
            values=["AM", "PM"],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#F3F4F6",
            text_color="#374151",
            hover_color="#E5E7EB",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            button_frame,
            text="Add Schedule",
            width=120,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#059669",
            hover_color="#047857",
            command=self.save_schedule
        ).pack(side="right")

    def save_schedule(self):
        try:
            # Validate inputs
            day = self.day_var.get()
            if day == "Select day":
                messagebox.showerror("Error", "Please select a day of week")
                return
            
            # Convert time to 24-hour format
            start_hour = int(self.start_hour_var.get())
            start_minute = int(self.start_minute_var.get())
            start_period = self.start_period_var.get()
            
            if start_period == "PM" and start_hour != 12:
                start_hour += 12
            elif start_period == "AM" and start_hour == 12:
                start_hour = 0
            
            end_hour = int(self.end_hour_var.get())
            end_minute = int(self.end_minute_var.get())
            end_period = self.end_period_var.get()
            
            if end_period == "PM" and end_hour != 12:
                end_hour += 12
            elif end_period == "AM" and end_hour == 12:
                end_hour = 0
            
            # Create datetime objects for validation
            start_time = datetime.combine(datetime.today(), time(start_hour, start_minute))
            end_time = datetime.combine(datetime.today(), time(end_hour, end_minute))
            
            if start_time >= end_time:
                messagebox.showerror("Error", "End time must be after start time")
                return
            
            # Create schedule
            schedule_data = {
                'assigned_course_id': self.assigned_course_data['assignment_id'],
                'day_of_week': day,
                'start_time': start_time.strftime('%H:%M:%S'),
                'end_time': end_time.strftime('%H:%M:%S')
            }
            
            success, result = self.create_schedule(schedule_data)
            if success:
                self.destroy()
                if self.on_success:
                    self.on_success()
                self.parent_view.after(100, lambda: SuccessModal(self.parent_view))
            else:
                messagebox.showerror("Error", f"Failed to create schedule: {result}")
                
        except Exception as e:
            print(f"Error saving schedule: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def create_schedule(self, schedule_data):
        try:
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.cursor()
                
                # Check for conflicting schedules
                cursor.execute("""
                    SELECT id FROM schedules 
                    WHERE assigned_course_id = ? AND day_of_week = ? 
                    AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
                """, (
                    schedule_data['assigned_course_id'],
                    schedule_data['day_of_week'],
                    schedule_data['start_time'], schedule_data['start_time'],
                    schedule_data['end_time'], schedule_data['end_time']
                ))
                
                if cursor.fetchone():
                    return False, "Schedule conflicts with existing time slot"
                
                # Create datetime objects for ISO format storage
                today = datetime.today().date()
                start_time = datetime.strptime(schedule_data['start_time'], '%H:%M:%S').time()
                end_time = datetime.strptime(schedule_data['end_time'], '%H:%M:%S').time()
                
                start_datetime = datetime.combine(today, start_time).strftime('%Y-%m-%dT%H:%M:%S')
                end_datetime = datetime.combine(today, end_time).strftime('%Y-%m-%dT%H:%M:%S')
                
                # Create new schedule with ISO datetime format
                cursor.execute("""
                    INSERT INTO schedules (assigned_course_id, day_of_week, start_time, end_time, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    schedule_data['assigned_course_id'],
                    schedule_data['day_of_week'],
                    start_datetime,
                    end_datetime,
                    datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                ))
                
                conn.commit()
                return True, "Schedule created successfully"
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            return False, str(e)

class EditScheduleModal(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, schedule_data, on_success=None):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = db_manager
        self.schedule_data = schedule_data
        self.on_success = on_success
        
        self.title("Edit Schedule")
        self.geometry("480x500")
        self.resizable(False, False)
        self.configure(fg_color="#F8FAFC")
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
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=8)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header
        ctk.CTkLabel(
            main_container,
            text="Edit Schedule",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            main_container,
            text="Update schedule details",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        ).pack(pady=(0, 15))
        
        # Form container
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20)
        
        # Day of Week
        ctk.CTkLabel(form_frame, text="Day of Week *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        self.day_var = ctk.StringVar(value=self.schedule_data.get('day_of_week', 'Select day'))
        self.day_menu = ctk.CTkOptionMenu(
            form_frame,
            variable=self.day_var,
            values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            height=28,
            font=ctk.CTkFont(size=11)
        )
        self.day_menu.pack(fill="x", pady=(0, 10))
        
        # Parse existing times - handle both datetime and time formats
        start_time_str = self.schedule_data.get('start_time', '08:00:00')
        end_time_str = self.schedule_data.get('end_time', '09:00:00')
        
        # Try to parse as datetime first, then as time
        try:
            if 'T' in start_time_str:
                # ISO datetime format
                start_time_obj = datetime.fromisoformat(start_time_str).time()
            else:
                # Time only format
                start_time_obj = datetime.strptime(start_time_str, '%H:%M:%S').time()
        except:
            start_time_obj = datetime.strptime('08:00:00', '%H:%M:%S').time()
        
        try:
            if 'T' in end_time_str:
                # ISO datetime format
                end_time_obj = datetime.fromisoformat(end_time_str).time()
            else:
                # Time only format
                end_time_obj = datetime.strptime(end_time_str, '%H:%M:%S').time()
        except:
            end_time_obj = datetime.strptime('09:00:00', '%H:%M:%S').time()
        
        # Convert to 12-hour format
        start_hour_12 = start_time_obj.hour if start_time_obj.hour <= 12 else start_time_obj.hour - 12
        start_hour_12 = 12 if start_hour_12 == 0 else start_hour_12
        start_period = "AM" if start_time_obj.hour < 12 else "PM"
        
        end_hour_12 = end_time_obj.hour if end_time_obj.hour <= 12 else end_time_obj.hour - 12
        end_hour_12 = 12 if end_hour_12 == 0 else end_hour_12
        end_period = "AM" if end_time_obj.hour < 12 else "PM"
        
        # Start Time
        ctk.CTkLabel(form_frame, text="Start Time *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        time_frame1 = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame1.pack(fill="x", pady=(0, 10))
        
        self.start_hour_var = ctk.StringVar(value=f"{start_hour_12:02d}")
        self.start_minute_var = ctk.StringVar(value=f"{start_time_obj.minute:02d}")
        self.start_period_var = ctk.StringVar(value=start_period)
        
        ctk.CTkOptionMenu(
            time_frame1,
            variable=self.start_hour_var,
            values=[f"{i:02d}" for i in range(1, 13)],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(time_frame1, text=":", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        
        ctk.CTkOptionMenu(
            time_frame1,
            variable=self.start_minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 15)],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkOptionMenu(
            time_frame1,
            variable=self.start_period_var,
            values=["AM", "PM"],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left")
        
        # End Time
        ctk.CTkLabel(form_frame, text="End Time *", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 3))
        time_frame2 = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame2.pack(fill="x", pady=(0, 20))
        
        self.end_hour_var = ctk.StringVar(value=f"{end_hour_12:02d}")
        self.end_minute_var = ctk.StringVar(value=f"{end_time_obj.minute:02d}")
        self.end_period_var = ctk.StringVar(value=end_period)
        
        ctk.CTkOptionMenu(
            time_frame2,
            variable=self.end_hour_var,
            values=[f"{i:02d}" for i in range(1, 13)],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(time_frame2, text=":", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        
        ctk.CTkOptionMenu(
            time_frame2,
            variable=self.end_minute_var,
            values=[f"{i:02d}" for i in range(0, 60, 15)],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkOptionMenu(
            time_frame2,
            variable=self.end_period_var,
            values=["AM", "PM"],
            width=60,
            height=28,
            font=ctk.CTkFont(size=11)
        ).pack(side="left")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=80,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#F3F4F6",
            text_color="#374151",
            hover_color="#E5E7EB",
            command=self.destroy
        ).pack(side="left")
        
        ctk.CTkButton(
            button_frame,
            text="Update Schedule",
            width=130,
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self.update_schedule
        ).pack(side="right")

    def update_schedule(self):
        try:
            # Validate inputs
            day = self.day_var.get()
            if day == "Select day":
                messagebox.showerror("Error", "Please select a day of week")
                return
            
            # Convert time to 24-hour format
            start_hour = int(self.start_hour_var.get())
            start_minute = int(self.start_minute_var.get())
            start_period = self.start_period_var.get()
            
            if start_period == "PM" and start_hour != 12:
                start_hour += 12
            elif start_period == "AM" and start_hour == 12:
                start_hour = 0
            
            end_hour = int(self.end_hour_var.get())
            end_minute = int(self.end_minute_var.get())
            end_period = self.end_period_var.get()
            
            if end_period == "PM" and end_hour != 12:
                end_hour += 12
            elif end_period == "AM" and end_hour == 12:
                end_hour = 0
            
            # Create datetime objects for validation
            start_time = datetime.combine(datetime.today(), time(start_hour, start_minute))
            end_time = datetime.combine(datetime.today(), time(end_hour, end_minute))
            
            if start_time >= end_time:
                messagebox.showerror("Error", "End time must be after start time")
                return
            
            # Update schedule
            success, result = self.update_schedule_data(day, start_time.strftime('%H:%M:%S'), end_time.strftime('%H:%M:%S'))
            if success:
                self.destroy()
                if self.on_success:
                    self.on_success()
                self.parent_view.after(100, lambda: SuccessModal(self.parent_view))
            else:
                messagebox.showerror("Error", f"Failed to update schedule: {result}")
                
        except Exception as e:
            print(f"Error updating schedule: {e}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_schedule_data(self, day, start_time, end_time):
        try:
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.cursor()
                
                # Check for conflicting schedules (excluding current schedule)
                cursor.execute("""
                    SELECT id FROM schedules 
                    WHERE assigned_course_id = ? AND day_of_week = ? AND id != ?
                    AND ((start_time <= ? AND end_time > ?) OR (start_time < ? AND end_time >= ?))
                """, (
                    self.schedule_data['assigned_course_id'],
                    day,
                    self.schedule_data['id'],
                    start_time, start_time,
                    end_time, end_time
                ))
                
                if cursor.fetchone():
                    return False, "Schedule conflicts with existing time slot"
                
                # Create datetime objects for ISO format storage
                today = datetime.today().date()
                start_time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
                end_time_obj = datetime.strptime(end_time, '%H:%M:%S').time()
                
                start_datetime = datetime.combine(today, start_time_obj).strftime('%Y-%m-%dT%H:%M:%S')
                end_datetime = datetime.combine(today, end_time_obj).strftime('%Y-%m-%dT%H:%M:%S')
                
                cursor.execute("""
                    UPDATE schedules 
                    SET day_of_week = ?, start_time = ?, end_time = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    day,
                    start_datetime,
                    end_datetime,
                    datetime.now().strftime('%Y-%m-%dT%H:%M:%S'),
                    self.schedule_data['id']
                ))
                
                conn.commit()
                return True, "Schedule updated successfully"
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            return False, str(e)

class ScheduleEditPopup(ctk.CTkToplevel):
    def __init__(self, parent, db_manager, assigned_course_data):
        super().__init__(parent)
        self.parent_view = parent
        self.db_manager = db_manager
        self.assigned_course_data = assigned_course_data
        self.schedules_data = []
        
        self.title(f"Schedules - {assigned_course_data.get('course_name', 'Course')}")
        self.geometry("800x600")
        self.resizable(True, True)
        self.configure(fg_color="#F8FAFC")
        self.transient(parent)
        self.grab_set()
        
        self.load_schedules()
        self.center_window()
        self.setup_ui()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def load_schedules(self):
        """Load schedules for the assigned course"""
        try:
            if self.db_manager:
                success, schedules = self.get_course_schedules(self.assigned_course_data['assignment_id'])
                if success:
                    self.schedules_data = schedules
        except Exception as e:
            print(f"Error loading schedules: {e}")

    def get_course_schedules(self, assigned_course_id):
        """Get schedules for a specific assigned course"""
        try:
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.execute("""
                    SELECT id, assigned_course_id, day_of_week, start_time, end_time, created_at, updated_at
                    FROM schedules
                    WHERE assigned_course_id = ?
                    ORDER BY 
                        CASE day_of_week
                            WHEN 'Monday' THEN 1
                            WHEN 'Tuesday' THEN 2
                            WHEN 'Wednesday' THEN 3
                            WHEN 'Thursday' THEN 4
                            WHEN 'Friday' THEN 5
                            WHEN 'Saturday' THEN 6
                            WHEN 'Sunday' THEN 7
                        END,
                        start_time
                """, (assigned_course_id,))
                
                schedules = cursor.fetchall()
                
                result = []
                for row in schedules:
                    result.append({
                        'id': row['id'],
                        'assigned_course_id': row['assigned_course_id'],
                        'day_of_week': row['day_of_week'],
                        'start_time': row['start_time'],
                        'end_time': row['end_time'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return True, result
                
            finally:
                conn.close()
                
        except Exception as e:
            return False, str(e)

    def setup_ui(self):
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        main_container.pack(fill="both", expand=True)
        
        # Header section
        header_section = ctk.CTkFrame(main_container, fg_color="#FAFAFA", corner_radius=0, height=60)
        header_section.pack(fill="x", padx=0, pady=0)
        header_section.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_section, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Title and Add button
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(fill="x")
        
        ctk.CTkLabel(
            title_frame,
            text="Course Schedules",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#1F2937",
        ).pack(side="left")
        
        # Add button
        ctk.CTkButton(
            title_frame,
            text="Add Schedule",
            width=120,
            height=32,
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="normal"),
            corner_radius=6,
            command=self.add_schedule
        ).pack(side="right")
        
        # Course info
        course_info = f"{self.assigned_course_data.get('course_name', 'Unknown')} ({self.assigned_course_data.get('course_code', '')})"
        ctk.CTkLabel(
            header_content,
            text=course_info,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#6B7280",
        ).pack(anchor="w", pady=(5, 0))

        # Content area
        content_area = ctk.CTkFrame(main_container, fg_color="transparent")
        content_area.pack(fill="both", expand=True, padx=24, pady=16)
        
        # Table container
        table_container = ctk.CTkFrame(content_area, fg_color="#FFFFFF", corner_radius=8, border_width=1, border_color="#E5E7EB")
        table_container.pack(fill="both", expand=True)
        
        # Table setup
        self.setup_table(table_container)

    def setup_table(self, parent):
        # Table header
        table_header = ctk.CTkFrame(parent, fg_color="#F9FAFB", corner_radius=0, height=40)
        table_header.pack(fill="x")
        table_header.pack_propagate(False)
        
        header_frame = ctk.CTkFrame(table_header, fg_color="transparent")
        header_frame.pack(fill="both", expand=True, padx=15, pady=8)
        
        # Header columns
        headers = [
            ("Day", 150),
            ("Start Time", 150),
            ("End Time", 150),
            ("Duration", 120),
            ("Actions", 120)
        ]
        
        for header_text, width in headers:
            ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#374151",
                width=width,
                anchor="w"
            ).pack(side="left", padx=(0, 8))

        # Scrollable content
        self.scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        self.populate_table()

    def populate_table(self):
        # Clear existing content
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        if not self.schedules_data:
            # No schedules message
            no_data_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            no_data_frame.pack(fill="x", pady=40)
            
            ctk.CTkLabel(
                no_data_frame,
                text="No schedules found for this course",
                font=ctk.CTkFont(size=14),
                text_color="#6B7280"
            ).pack()
            return
        
        # Display schedules
        for schedule in self.schedules_data:
            self.create_schedule_row(schedule)

    def create_schedule_row(self, schedule):
        # Row container
        row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#FFFFFF", corner_radius=0, height=40)
        row_frame.pack(fill="x", pady=1, padx=15)
        row_frame.pack_propagate(False)
        
        content_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=8)
        
        # Format times with better error handling
        start_time = schedule.get('start_time', '')
        end_time = schedule.get('end_time', '')
        
        # Convert to 12-hour format for display
        try:
            # Handle both datetime and time formats
            if 'T' in start_time:
                start_time_obj = datetime.fromisoformat(start_time).time()
            else:
                start_time_obj = datetime.strptime(start_time, '%H:%M:%S').time()
            
            if 'T' in end_time:
                end_time_obj = datetime.fromisoformat(end_time).time()
            else:
                end_time_obj = datetime.strptime(end_time, '%H:%M:%S').time()
            
            start_display = start_time_obj.strftime('%I:%M %p')
            end_display = end_time_obj.strftime('%I:%M %p')
            
            # Calculate duration
            start_datetime = datetime.combine(datetime.today(), start_time_obj)
            end_datetime = datetime.combine(datetime.today(), end_time_obj)
            duration = end_datetime - start_datetime
            duration_display = f"{duration.seconds // 3600}h {(duration.seconds // 60) % 60}m"
            
        except Exception as e:
            print(f"Error parsing time: {e}")
            start_display = start_time
            end_display = end_time
            duration_display = "N/A"
        
        # Data columns
        data_columns = [
            (schedule.get('day_of_week', ''), 150),
            (start_display, 150),
            (end_display, 150),
            (duration_display, 120)
        ]
        
        for text, width in data_columns:
            ctk.CTkLabel(
                content_frame,
                text=text,
                font=ctk.CTkFont(size=12),
                text_color="#111827",
                width=width,
                anchor="w"
            ).pack(side="left", padx=(0, 8))
        
        # Actions dropdown
        action_var = tk.StringVar(value="Actions")
        action_menu = ctk.CTkOptionMenu(
            content_frame,
            values=["Edit", "Delete"],
            variable=action_var,
            width=100,
            height=26,
            font=ctk.CTkFont(size=11),
            fg_color="#F3F4F6",
            text_color="#222",
            button_color="#E5E7EB",
            button_hover_color="#D1D5DB",
            dropdown_fg_color="#fff",
            dropdown_hover_color="#E5E7EB",
            dropdown_text_color="#222",
            command=lambda choice, data=schedule: self.handle_action(choice, data)
        )
        action_menu.pack(side="left")

    def handle_action(self, action, schedule_data):
        if action == "Edit":
            self.edit_schedule(schedule_data)
        elif action == "Delete":
            self.delete_schedule(schedule_data)

    def add_schedule(self):
        AddScheduleModal(
            self, 
            self.db_manager, 
            self.assigned_course_data, 
            on_success=self.refresh_schedules
        )

    def edit_schedule(self, schedule_data):
        EditScheduleModal(
            self, 
            self.db_manager, 
            schedule_data, 
            on_success=self.refresh_schedules
        )

    def delete_schedule(self, schedule_data):
        def on_delete():
            try:
                success, message = self.delete_schedule_data(schedule_data['id'])
                if success:
                    self.after(100, self.refresh_schedules)
                    self.after(200, lambda: SuccessModal(self))
                else:
                    messagebox.showerror("Error", f"Failed to delete schedule: {message}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        DeleteModal(self, on_delete=on_delete)

    def delete_schedule_data(self, schedule_id):
        try:
            conn = self.db_manager.get_connection()
            try:
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
                
                conn.commit()
                return True, "Schedule deleted successfully"
                
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
                
        except Exception as e:
            return False, str(e)

    def refresh_schedules(self):
        """Refresh the schedules table"""
        self.load_schedules()
        self.populate_table()
