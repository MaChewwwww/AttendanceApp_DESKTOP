import sqlite3
import bcrypt
import base64
import os
import random
import string
from datetime import datetime, timedelta
from .config import DB_PATH, UPLOAD_DIR
from .email_service import EmailService

class DatabaseManager:
    def __init__(self):
        self.email_service = EmailService()
        # Initialize database tables on first run
        self._initialize_database()
    
    def get_connection(self):
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    
    def close(self):
        """
        Dummy close method to maintain compatibility with application code.
        Since we're using per-operation connections now, this method doesn't need to do anything.
        """
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
            
            # Insert user - set as pending for admin verification
            user_query = """
            INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, face_image, verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                0,  # verified = 0 (False) - admin needs to verify
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
            
            print(f"Successfully registered user: {email} (ID: {user_id}) - Pending admin approval")
            
            # Send registration confirmation email (not welcome email)
            try:
                self.email_service.send_registration_confirmation_email(email, first_name)
            except Exception as e:
                print(f"Warning: Could not send registration confirmation email: {e}")
            
            return True, {
                "user_id": user_id,
                "name": f"{first_name} {last_name}",
                "email": email,
                "role": "Student",
                "student_number": student_number
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
            
            # Get user with student information (for students) or just user info (for admins)
            query = """
            SELECT u.*, s.student_number
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            WHERE u.email = ?
            """
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            
            if not user:
                return False, "Invalid email or password"
                
            # Check password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return False, "Invalid email or password"
            
            # Check role and handle accordingly
            user_role = user['role']
            
            if user_role.lower() == 'admin':
                # Admin login - no verification check needed, always allow
                user_data = {
                    "user_id": user['id'],
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "email": user['email'],
                    "role": user['role'],
                    "student_number": None,  # Admins don't have student numbers
                    "contact_number": user['contact_number'],
                    "birthday": user['birthday']
                }
                
                print(f"Successful admin login: {email}")
                return True, user_data
                
            elif user_role.lower() == 'student':
                # Student login - check verification only
                if user['verified'] == 0:
                    return False, "Account is not verified yet. It will take 1-3 Business days to verify your account. Please contact administrator if you have further concerns."
                    
                # Return user data for student
                user_data = {
                    "user_id": user['id'],
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "email": user['email'],
                    "role": user['role'],
                    "student_number": user['student_number'],
                    "contact_number": user['contact_number'],
                    "birthday": user['birthday']
                }
                
                print(f"Successful student login: {email}")
                return True, user_data
            else:
                return False, "Invalid user role"
                
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
    
    def generate_otp(self, length=6):
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def create_login_otp(self, email):
        """Create and send login OTP for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if user exists and is verified
            cursor.execute("SELECT id, first_name, verified FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "No account found with this email address"
            
            user_id, first_name, verified = user
            
            # Check if account is verified
            if verified == 0:
                conn.close()
                return False, "Account is not verified yet. Please contact administrator."
            
            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = datetime.now() + timedelta(minutes=10)  # OTP expires in 10 minutes
            
            # Store OTP in database
            cursor.execute("""
                INSERT INTO otp_requests (user_id, otp_code, type, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, otp_code, 'login', datetime.now().isoformat(), expires_at.isoformat()))
            
            # Update user's last OTP info
            cursor.execute("""
                UPDATE users SET last_verified_otp_expiry = ? WHERE id = ?
            """, (expires_at.isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            # Send OTP email
            success, message = self.email_service.send_login_otp_email(email, first_name, otp_code)
            
            if success:
                return True, "Login verification code sent successfully to your email"
            else:
                return False, f"Failed to send verification code: {message}"
            
        except Exception as e:
            print(f"Error creating login OTP: {e}")
            return False, str(e)
    
    def check_otp_requirement(self, user_id):
        """Check if user needs OTP verification or if existing verification is still valid"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get user's last OTP verification info
            cursor.execute("""
                SELECT last_verified_otp, last_verified_otp_expiry
                FROM users 
                WHERE id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return True  # User not found, require OTP
            
            last_verified = result['last_verified_otp']
            last_expiry = result['last_verified_otp_expiry']
            
            # If no previous OTP verification, require OTP
            if not last_verified:
                return True
            
            try:
                # Check if last verification is still valid (within 24 hours)
                verified_time = datetime.fromisoformat(last_verified)
                current_time = datetime.now()
                
                # OTP verification is valid for 24 hours
                if current_time - verified_time < timedelta(hours=24):
                    print(f"OTP verification still valid for user {user_id}")
                    return False  # OTP still valid, no need for new verification
                else:
                    print(f"OTP verification expired for user {user_id}")
                    return True  # OTP expired, require new verification
                    
            except ValueError:
                # Invalid datetime format, require OTP
                return True
            
        except Exception as e:
            print(f"Error checking OTP requirement: {e}")
            return True  # On error, require OTP for security

    def update_login_otp_verification(self, user_id):
        """Update user's OTP verification timestamp after successful OTP login"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            current_time = datetime.now()
            expiry_time = current_time + timedelta(hours=24)  # OTP verification valid for 24 hours
            
            cursor.execute("""
                UPDATE users 
                SET last_verified_otp = ?, last_verified_otp_expiry = ?, updated_at = ?
                WHERE id = ?
            """, (current_time.isoformat(), expiry_time.isoformat(), current_time.isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            print(f"Updated OTP verification for user {user_id}")
            return True
            
        except Exception as e:
            print(f"Error updating OTP verification: {e}")
            return False

    def verify_login_otp(self, email, otp_code):
        """Verify login OTP and return user data if valid"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Find valid OTP
            cursor.execute("""
                SELECT o.user_id, u.first_name, u.last_name, u.email, u.role, u.contact_number, u.birthday, s.student_number
                FROM otp_requests o
                JOIN users u ON o.user_id = u.id
                LEFT JOIN students s ON u.id = s.user_id
                WHERE u.email = ? AND o.otp_code = ? AND o.type = 'login' 
                AND o.expires_at > ? 
                ORDER BY o.created_at DESC
                LIMIT 1
            """, (email, otp_code, datetime.now().isoformat()))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Invalid or expired OTP code"
            
            user_id = result['user_id']
            
            # Update user's OTP verification timestamp
            current_time = datetime.now()
            expiry_time = current_time + timedelta(hours=24)  # Valid for 24 hours
            
            cursor.execute("""
                UPDATE users 
                SET last_verified_otp = ?, last_verified_otp_expiry = ?, updated_at = ?
                WHERE id = ?
            """, (current_time.isoformat(), expiry_time.isoformat(), current_time.isoformat(), user_id))
            
            # Delete used OTP
            cursor.execute("""
                DELETE FROM otp_requests WHERE user_id = ? AND otp_code = ? AND type = 'login'
            """, (user_id, otp_code))
            
            conn.commit()
            conn.close()
            
            # Return user data
            user_data = {
                "user_id": result['user_id'],
                "first_name": result['first_name'],
                "last_name": result['last_name'],
                "email": result['email'],
                "role": result['role'],
                "student_number": result['student_number'],
                "contact_number": result['contact_number'],
                "birthday": result['birthday']
            }
            
            print(f"Successful OTP login: {email}")
            return True, user_data
            
        except Exception as e:
            print(f"Error verifying login OTP: {e}")
            return False, str(e)

    def _initialize_database(self):
        """Initialize database tables if they don't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create otp_requests table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS otp_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    otp_code TEXT NOT NULL,
                    type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    used INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)
            
            # Add missing columns to users table if they don't exist
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN last_verified_otp TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN last_verified_otp_expiry TEXT")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing database: {e}")

    def create_password_reset_otp(self, email):
        """Create and send password reset OTP for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT id, first_name FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return False, "No account found with this email address"
            
            user_id, first_name = user
            
            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = datetime.now() + timedelta(minutes=15)  # Password reset OTP expires in 15 minutes
            
            # Store OTP in database
            cursor.execute("""
                INSERT INTO otp_requests (user_id, otp_code, type, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, otp_code, 'password_reset', datetime.now().isoformat(), expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            # Send password reset OTP email
            success, message = self.email_service.send_password_reset_otp_email(email, first_name, otp_code)
            
            if success:
                return True, "Password reset OTP sent successfully to your email"
            else:
                return False, f"Failed to send OTP email: {message}"
            
        except Exception as e:
            print(f"Error creating password reset OTP: {e}")
            return False, str(e)
    
    def verify_password_reset_otp(self, email, otp_code):
        """Verify password reset OTP"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Find valid OTP
            cursor.execute("""
                SELECT o.user_id
                FROM otp_requests o
                JOIN users u ON o.user_id = u.id
                WHERE u.email = ? AND o.otp_code = ? AND o.type = 'password_reset' 
                AND o.expires_at > ?
                ORDER BY o.created_at DESC
                LIMIT 1
            """, (email, otp_code, datetime.now().isoformat()))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Invalid or expired OTP code"
            
            user_id = result['user_id']
            
            # Don't delete the OTP yet - keep it for password reset completion
            # Just mark when it was verified
            cursor.execute("""
                UPDATE users SET last_verified_otp = ? WHERE id = ?
            """, (datetime.now().isoformat(), user_id))
            
            conn.commit()
            conn.close()
            
            return True, {"user_id": user_id, "message": "OTP verified successfully"}
            
        except Exception as e:
            print(f"Error verifying password reset OTP: {e}")
            return False, str(e)
    
    def reset_password_with_otp(self, email, otp_code, new_password):
        """Reset password using verified OTP"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Find valid OTP that was recently verified
            cursor.execute("""
                SELECT o.user_id, u.last_verified_otp
                FROM otp_requests o
                JOIN users u ON o.user_id = u.id
                WHERE u.email = ? AND o.otp_code = ? AND o.type = 'password_reset' 
                AND o.expires_at > ?
                ORDER BY o.created_at DESC
                LIMIT 1
            """, (email, otp_code, datetime.now().isoformat()))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Invalid or expired OTP code"
            
            user_id = result['user_id']
            last_verified = result['last_verified_otp']
            
            # Check if OTP was verified within the last 5 minutes
            if last_verified:
                verified_time = datetime.fromisoformat(last_verified)
                if datetime.now() - verified_time > timedelta(minutes=5):
                    conn.close()
                    return False, "OTP verification expired. Please verify OTP again."
            else:
                conn.close()
                return False, "OTP not verified. Please verify OTP first."
            
            # Hash new password
            hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Update password
            cursor.execute("""
                UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?
            """, (hashed_pw.decode('utf-8'), datetime.now().isoformat(), user_id))
            
            # Delete used OTP
            cursor.execute("""
                DELETE FROM otp_requests WHERE user_id = ? AND otp_code = ? AND type = 'password_reset'
            """, (user_id, otp_code))
            
            # Clear last verified OTP info
            cursor.execute("""
                UPDATE users SET last_verified_otp = NULL, last_verified_otp_expiry = NULL WHERE id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            
            return True, "Password reset successfully"
            
        except Exception as e:
            print(f"Error resetting password: {e}")
            return False, str(e)
    
    def cleanup_expired_otps(self):
        """Clean up expired OTP requests"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Delete expired OTPs
            cursor.execute("""
                DELETE FROM otp_requests WHERE expires_at < ?
            """, (datetime.now().isoformat(),))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                print(f"Cleaned up {deleted_count} expired OTP requests")
            
            return True, f"Cleaned up {deleted_count} expired OTPs"
            
        except Exception as e:
            print(f"Error cleaning up expired OTPs: {e}")
            return False, str(e)
