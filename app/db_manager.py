import sqlite3
import bcrypt
import base64
import os
from datetime import datetime
from .config import DB_FILE, UPLOAD_DIR

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        """Create database connection"""
        try:
            self.connection = sqlite3.connect(DB_FILE)
            # Configure SQLite to return rows as dictionaries
            self.connection.row_factory = sqlite3.Row
            print(f"SQLite connection established: {DB_FILE}")
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite: {e}")
            
    def reconnect_if_needed(self):
        """Check if connection is valid and reconnect if needed"""
        try:
            # Test connection by executing simple query
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
        except sqlite3.Error as e:
            print(f"SQLite connection lost: {e}")
            self.connect()
    
    def register(self, first_name, middle_name, last_name, email, student_number, password, face_image=None):
        """Register a new student with face image"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor()
            
            # Check if email is already in use
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                cursor.close()
                return False, "Email is already in use"
                
            # Check if student number is already in use
            cursor.execute("SELECT id FROM students WHERE student_number = ?", (student_number,))
            if cursor.fetchone():
                cursor.close()
                return False, "Student number is already in use"
                
            # Hash the password
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            try:
                # Begin transaction
                self.connection.execute("BEGIN TRANSACTION")
                
                # Insert user
                user_query = """
                INSERT INTO users (first_name, middle_name, last_name, email, password_hash, face_image, role, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(user_query, (
                    first_name,
                    middle_name,
                    last_name,
                    email,
                    hashed_pw.decode('utf-8'),
                    face_image,  # Binary image data
                    "Student",
                    "pending"
                ))
                
                user_id = cursor.lastrowid
                
                # Insert student
                student_query = """
                INSERT INTO students (user_id, student_number)
                VALUES (?, ?)
                """
                cursor.execute(student_query, (user_id, student_number))
                
                # Commit transaction
                self.connection.commit()
                
                cursor.close()
                
                return True, {
                    "user_id": user_id,
                    "name": f"{first_name} {last_name}",
                    "email": email,
                    "role": "Student",
                    "student_number": student_number,
                    "status": "pending"
                }
                
            except sqlite3.Error as e:
                # Rollback transaction in case of error
                self.connection.rollback()
                print(f"Error during registration: {e}")
                return False, f"Registration error: {str(e)}"
                
        except sqlite3.Error as e:
            print(f"Database error during registration: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
    
    def login(self, email, password):
        """Authenticate user and get user data"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor()
            
            # Query user by email
            query = """
            SELECT u.*, s.student_number 
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.email = ?
            """
            cursor.execute(query, (email,))
            user_row = cursor.fetchone()
            
            if not user_row:
                cursor.close()
                return False, "Invalid email or password"
            
            # Convert SQLite row to dictionary
            user = dict(user_row)
                
            # Check password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                cursor.close()
                return False, "Invalid email or password"
                
            # Check if it's a student
            if not user.get('student_number'):
                cursor.close()
                return False, "Only students can log in to this portal"
                
            # Convert face_image to base64 if it exists
            if user.get('face_image'):
                face_image_b64 = base64.b64encode(user['face_image']).decode('utf-8')
                user['face_image_b64'] = face_image_b64
            
            cursor.close()
            return True, user
            
        except sqlite3.Error as e:
            print(f"Database error during login: {e}")
            return False, f"Database error: {str(e)}"
    
    def get_profile(self, user_id):
        """Get user profile information"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor()
            
            query = """
            SELECT u.*, s.student_number, s.section
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.id = ?
            """
            cursor.execute(query, (user_id,))
            user_row = cursor.fetchone()
            
            if not user_row:
                cursor.close()
                return False, "User not found"
            
            # Convert SQLite row to dictionary
            user = dict(user_row)
                
            # Convert face_image to base64 if it exists
            if user.get('face_image'):
                face_image_b64 = base64.b64encode(user['face_image']).decode('utf-8')
                user['face_image_b64'] = face_image_b64
            
            cursor.close()
            return True, user
            
        except sqlite3.Error as e:
            print(f"Database error getting profile: {e}")
            return False, f"Database error: {str(e)}"
    
    def register_face(self, user_id, face_image_data):
        """Register user's face image"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor()
            
            query = "UPDATE users SET face_image = ? WHERE id = ?"
            cursor.execute(query, (face_image_data, user_id))
            self.connection.commit()
            
            cursor.close()
            return True, "Face registered successfully"
            
        except sqlite3.Error as e:
            print(f"Database error registering face: {e}")
            return False, f"Database error: {str(e)}"
    
    def log_attendance(self, user_id, course_id, section_id, image_data):
        """Log attendance with face image"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO attendance_logs 
            (user_id, course_id, section_id, date, image, status) 
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            current_time = datetime.now()
            cursor.execute(query, (
                user_id, 
                course_id, 
                section_id, 
                current_time.isoformat(),
                image_data,
                "Present"
            ))
            
            self.connection.commit()
            attendance_id = cursor.lastrowid
            
            cursor.close()
            return True, {
                "attendance_id": attendance_id,
                "timestamp": current_time.isoformat()
            }
            
        except sqlite3.Error as e:
            print(f"Database error logging attendance: {e}")
            return False, f"Database error: {str(e)}"
    
    def get_attendance_history(self, user_id):
        """Get attendance history for a user"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor()
            
            query = """
            SELECT al.id, al.date, al.status, 
                   c.name as course_name, s.name as section_name
            FROM attendance_logs al
            JOIN courses c ON al.course_id = c.id
            JOIN sections s ON al.section_id = s.id
            WHERE al.user_id = ?
            ORDER BY al.date DESC
            """
            
            cursor.execute(query, (user_id,))
            logs = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            return True, logs
            
        except sqlite3.Error as e:
            print(f"Database error getting attendance history: {e}")
            return False, f"Database error: {str(e)}"
    
    def get_courses_and_sections(self):
        """Get all courses and their sections"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor()
            
            query = """
            SELECT c.id as course_id, c.name as course_name,
                   s.id as section_id, s.name as section_name
            FROM courses c
            JOIN sections s ON c.id = s.course_id
            ORDER BY c.name, s.name
            """
            
            cursor.execute(query)
            results = [dict(row) for row in cursor.fetchall()]
            
            # Organize data by courses and sections
            courses = {}
            for row in results:
                course_id = row['course_id']
                if course_id not in courses:
                    courses[course_id] = {
                        'id': course_id,
                        'name': row['course_name'],
                        'sections': []
                    }
                courses[course_id]['sections'].append({
                    'id': row['section_id'],
                    'name': row['section_name']
                })
            
            cursor.close()
            return True, list(courses.values())
            
        except sqlite3.Error as e:
            print(f"Database error getting courses and sections: {e}")
            return False, f"Database error: {str(e)}"
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("SQLite connection is closed")