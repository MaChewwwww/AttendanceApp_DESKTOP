import sqlite3
import bcrypt
import base64
import os
from datetime import datetime
from .config import DB_PATH, UPLOAD_DIR

class DatabaseManager:
    def get_connection(self):
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        print(f"Database connection opened: {DB_PATH}")
        return conn
    
    def close(self):
        """
        Dummy close method to maintain compatibility with application code.
        Since we're using per-operation connections now, this method doesn't need to do anything.
        """
        print("DatabaseManager.close()")
        return
    
    def check_email_exists(self, email):
        """Check if an email address is already registered
        
        Returns:
            tuple: (success, message) where success is True if email exists
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
            count = cursor.fetchone()[0]
            
            conn.close()
            
            if count > 0:
                return True, "Email already exists"
            else:
                return False, "Email available"
                
        except Exception as e:
            print(f"Database error checking email: {str(e)}")
            return False, f"Error checking email: {str(e)}"
            
    def check_student_id_exists(self, student_id):
        """Check if a student ID is already registered
        
        Returns:
            tuple: (success, message) where success is True if ID exists
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM students WHERE student_number = ?", (student_id,))
            count = cursor.fetchone()[0]
            
            conn.close()
            
            if count > 0:
                return True, "Student ID already exists"
            else:
                return False, "Student ID available"
                
        except Exception as e:
            print(f"Database error checking student ID: {str(e)}")
            return False, f"Error checking student ID: {str(e)}"
    
    def register(self, first_name, middle_name, last_name, email, student_number, password, face_image=None):
        """Register a new student with face image"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if email is already in use
            cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cursor.fetchone():
                return False, "Email is already in use"
                
            # Check if student number is already in use
            cursor.execute("SELECT id FROM students WHERE student_number = ?", (student_number,))
            if cursor.fetchone():
                return False, "Student number is already in use"
                
            # Hash the password
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Begin transaction
            conn.execute("BEGIN TRANSACTION")
            
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
            conn.commit()
            
            return True, {
                "user_id": user_id,
                "name": f"{first_name} {last_name}",
                "email": email,
                "role": "Student",
                "student_number": student_number,
                "status": "pending"
            }
                
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Database error during registration: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                print(f"Database connection closed")
                conn.close()
    
    def login(self, email, password):
        """Authenticate user and get user data"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
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
                return False, "Invalid email or password"
            
            # Convert SQLite row to dictionary
            user = dict(user_row)
                
            # Check password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return False, "Invalid email or password"
                
                
            # Convert face_image to base64 if it exists
            if user.get('face_image'):
                face_image_b64 = base64.b64encode(user['face_image']).decode('utf-8')
                user['face_image_b64'] = face_image_b64
            
            return True, user
            
        except sqlite3.Error as e:
            print(f"Database error during login: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_profile(self, user_id):
        """Get user profile information"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT u.*, s.student_number, s.section
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.id = ?
            """
            cursor.execute(query, (user_id,))
            user_row = cursor.fetchone()
            
            if not user_row:
                return False, "User not found"
            
            # Convert SQLite row to dictionary
            user = dict(user_row)
                
            # Convert face_image to base64 if it exists
            if user.get('face_image'):
                face_image_b64 = base64.b64encode(user['face_image']).decode('utf-8')
                user['face_image_b64'] = face_image_b64
            
            return True, user
            
        except sqlite3.Error as e:
            print(f"Database error getting profile: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def register_face(self, user_id, face_image_data):
        """Register user's face image"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "UPDATE users SET face_image = ? WHERE id = ?"
            cursor.execute(query, (face_image_data, user_id))
            conn.commit()
            
            return True, "Face registered successfully"
            
        except sqlite3.Error as e:
            print(f"Database error registering face: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def log_attendance(self, user_id, course_id, section_id, image_data):
        """Log attendance with face image"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
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
            
            conn.commit()
            attendance_id = cursor.lastrowid
            
            return True, {
                "attendance_id": attendance_id,
                "timestamp": current_time.isoformat()
            }
            
        except sqlite3.Error as e:
            print(f"Database error logging attendance: {e}")
            return False, f"Database error: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    