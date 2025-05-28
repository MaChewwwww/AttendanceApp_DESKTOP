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
    