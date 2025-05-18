import mysql.connector
from mysql.connector import Error
import bcrypt
import base64
import os
from datetime import datetime
from .config import DB_HOST, DB_USER, DB_PASS, DB_NAME, UPLOAD_DIR

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME
            )
            print("MySQL connection is established")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            
    def reconnect_if_needed(self):
        """Reconnect to database if connection was lost"""
        try:
            if self.connection and not self.connection.is_connected():
                self.connection.reconnect()
                print("Reconnected to MySQL")
        except Error as e:
            print(f"Error reconnecting to MySQL: {e}")
            self.connect()
            
    def login(self, email, password):
        """Authenticate user and get user data"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor(dictionary=True)
            
            # Query user by email
            query = """
            SELECT u.*, s.student_number 
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.email = %s
            """
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                return False, "Invalid email or password"
                
            # Check password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return False, "Invalid email or password"
                
            # Check if it's a student
            if not user.get('student_number'):
                return False, "Only students can log in to this portal"
                
            # Convert face_image to base64 if it exists
            if user.get('face_image'):
                face_image_b64 = base64.b64encode(user['face_image']).decode('utf-8')
                user['face_image_b64'] = face_image_b64
                
            return True, user
            
        except Error as e:
            print(f"Database error during login: {e}")
            return False, f"Database error: {str(e)}"
            
    def get_profile(self, user_id):
        """Get user profile information"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT u.*, s.student_number, s.section
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.id = %s
            """
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            cursor.close()
            
            if not user:
                return False, "User not found"
                
            # Convert face_image to base64 if it exists
            if user.get('face_image'):
                face_image_b64 = base64.b64encode(user['face_image']).decode('utf-8')
                user['face_image_b64'] = face_image_b64
                
            return True, user
            
        except Error as e:
            print(f"Database error getting profile: {e}")
            return False, f"Database error: {str(e)}"
            
    def register_face(self, user_id, face_image_data):
        """Register user's face image"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor()
            
            query = "UPDATE users SET face_image = %s WHERE id = %s"
            cursor.execute(query, (face_image_data, user_id))
            self.connection.commit()
            cursor.close()
            
            return True, "Face registered successfully"
            
        except Error as e:
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
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            current_time = datetime.now()
            cursor.execute(query, (
                user_id, 
                course_id, 
                section_id, 
                current_time,
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
            
        except Error as e:
            print(f"Database error logging attendance: {e}")
            return False, f"Database error: {str(e)}"
            
    def get_attendance_history(self, user_id):
        """Get attendance history for a user"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT al.id, al.date, al.status, 
                   c.name as course_name, s.name as section_name
            FROM attendance_logs al
            JOIN courses c ON al.course_id = c.id
            JOIN sections s ON al.section_id = s.id
            WHERE al.user_id = %s
            ORDER BY al.date DESC
            """
            
            cursor.execute(query, (user_id,))
            logs = cursor.fetchall()
            cursor.close()
            
            return True, logs
            
        except Error as e:
            print(f"Database error getting attendance history: {e}")
            return False, f"Database error: {str(e)}"
            
    def get_courses_and_sections(self):
        """Get all courses and their sections"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT c.id as course_id, c.name as course_name,
                   s.id as section_id, s.name as section_name
            FROM courses c
            JOIN sections s ON c.id = s.course_id
            ORDER BY c.name, s.name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
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
            
            return True, list(courses.values())
            
        except Error as e:
            print(f"Database error getting courses and sections: {e}")
            return False, f"Database error: {str(e)}"
    
    def register(self, first_name, middle_name, last_name, email, student_number, password):
        """Register a new student"""
        try:
            self.reconnect_if_needed()
            cursor = self.connection.cursor(dictionary=True)
            
            # Check if email is already in use
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                return False, "Email is already in use"
                
            # Check if student number is already in use
            cursor.execute("SELECT id FROM students WHERE student_number = %s", (student_number,))
            if cursor.fetchone():
                cursor.close()
                return False, "Student number is already in use"
                
            # Hash the password
            import bcrypt
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Insert user
            user_query = """
            INSERT INTO users (first_name, middle_name, last_name, email, password_hash, role, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(user_query, (
                first_name,
                middle_name,
                last_name,
                email,
                hashed_pw.decode('utf-8'),
                "Student",
                "pending"
            ))
            
            user_id = cursor.lastrowid
            
            # Insert student
            student_query = """
            INSERT INTO students (user_id, student_number)
            VALUES (%s, %s)
            """
            cursor.execute(student_query, (user_id, student_number))
            
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
            
        except Exception as e:
            self.connection.rollback()
            print(f"Registration error: {str(e)}")
            return False, f"Registration error: {str(e)}"
            
    def close(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection is closed")

    