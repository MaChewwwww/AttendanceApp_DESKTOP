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
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = ? AND verified = 1", (email,))
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
            
            cursor.execute("SELECT COUNT(*) FROM students s JOIN users u ON s.user_id = u.id WHERE s.student_number = ? AND u.verified = 1", (student_id,))
            count = cursor.fetchone()[0]
            
            conn.close()
            
            if count > 0:
                return True, "Student ID already exists"
            else:
                return False, "Student ID available"
                
        except Exception as e:
            print(f"Database error checking student ID: {str(e)}")
            return False, f"Error checking student ID: {str(e)}"
    
    def register(self, first_name, last_name, email, student_number, password, face_image=None, contact_number=None, date_of_birth=None):
        """Register a new student with face image and additional details"""
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
            
            # Convert date_of_birth string to date format if provided
            birthday = None
            if date_of_birth:
                try:
                    # Keep as string in YYYY-MM-DD format for SQLite
                    from datetime import datetime as dt
                    # Validate the date format
                    dt.strptime(date_of_birth, "%Y-%m-%d")
                    birthday = date_of_birth  # Store as string for SQLite
                except ValueError:
                    return False, "Invalid date format"
            
            # Begin transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Insert user with new schema fields including verified
            user_query = """
            INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, face_image, status, verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            current_time = datetime.now().isoformat()
            cursor.execute(user_query, (
                first_name,
                last_name,
                email,
                birthday,  # Will be stored as TEXT in SQLite
                hashed_pw.decode('utf-8'),
                contact_number,
                "Student",
                face_image,
                "Pending",
                0,  # verified = 0 (False) by default
                current_time,
                current_time
            ))
            
            user_id = cursor.lastrowid
            
            # Insert student record
            student_query = """
            INSERT INTO students (user_id, student_number)
            VALUES (?, ?)
            """
            cursor.execute(student_query, (
                user_id, 
                student_number
            ))
            
            # Commit transaction
            conn.commit()
            
            print(f"Successfully registered user: {email} (ID: {user_id})")
            
            return True, {
                "user_id": user_id,
                "name": f"{first_name} {last_name}",
                "email": email,
                "role": "Student",
                "student_number": student_number,
                "status": "active"
            }
                
        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            print(f"Database error during registration: {e}")
            return False, f"Database error: {str(e)}"
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Unexpected error during registration: {e}")
            return False, f"Registration failed: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if conn:
                print(f"Database connection closed")
                conn.close()
    
    def login(self, email, password):
        """Authenticate user login"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user with student information (updated field names)
            query = """
            SELECT u.*, s.student_number
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.email = ? AND u.role = 'Student'
            """
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if not user:
                return False, "Invalid email or password"
                
            # Check password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return False, "Invalid email or password"
                
            # Check if account is active
            if user['status'] != 'active':
                return False, "Account is not active. Please contact administrator."
                
            # Return user data with updated field names
            user_data = {
                "user_id": user['id'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "email": user['email'],
                "role": user['role'],
                "student_number": user['student_number'],
                "status": user['status'],
                "contact_number": user['contact_number'],
                "birthday": user['birthday']  # Changed from date_of_birth to birthday
            }
            
            print(f"Successful login: {email}")
            return True, user_data
                
        except sqlite3.Error as e:
            print(f"Database error during login: {e}")
            return False, "Database error occurred"
        except Exception as e:
            print(f"Unexpected error during login: {e}")
            return False, "Login failed"
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
