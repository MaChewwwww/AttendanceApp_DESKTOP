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
            
            # Get default status for new students (Enrolled)
            cursor.execute("SELECT id FROM statuses WHERE name = 'Enrolled' AND user_type = 'student'")
            status_result = cursor.fetchone()
            default_status_id = status_result[0] if status_result else None
            
            if not default_status_id:
                # Fallback: get any student status if "Enrolled" doesn't exist
                cursor.execute("SELECT id FROM statuses WHERE user_type = 'student' LIMIT 1")
                fallback_result = cursor.fetchone()
                default_status_id = fallback_result[0] if fallback_result else None
            
            # Begin transaction
            conn.execute("BEGIN TRANSACTION")
            
            # Insert user - set as pending for admin verification with default status
            user_query = """
            INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, status_id, face_image, verified, isDeleted, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                default_status_id,  # Assign default status
                face_image,
                0,  # verified = 0 (False) - admin needs to verify
                0,  # isDeleted = 0 (False)
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
            
            print(f"Successfully registered user: {email} (ID: {user_id}) - Pending admin approval with status ID: {default_status_id}")
            
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
                    return False, "Account verification is pending. Please check your email for verification instructions or contact support if you need assistance."
                    
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
                return False, "Account verification is pending. Please contact support for assistance."
            
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

    def create_registration_otp(self, email, first_name):
        """Create and send registration OTP for email verification"""
        try:
            # Generate OTP
            otp_code = self.generate_otp()
            expires_at = datetime.now() + timedelta(minutes=15)  # Registration OTP expires in 15 minutes
            
            # Store OTP temporarily (not tied to user_id since user doesn't exist yet)
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Store in a temporary table or use email as identifier
            cursor.execute("""
                INSERT INTO otp_requests (user_id, otp_code, type, created_at, expires_at, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (0, otp_code, 'registration', datetime.now().isoformat(), expires_at.isoformat(), email))
            
            conn.commit()
            conn.close()
            
            # Send registration OTP email
            success, message = self.email_service.send_registration_otp_email(email, first_name, otp_code)
            
            if success:
                return True, "Registration verification code sent successfully to your email"
            else:
                return False, f"Failed to send verification code: {message}"
            
        except Exception as e:
            print(f"Error creating registration OTP: {e}")
            return False, str(e)
    
    def verify_registration_otp_and_register(self, email, otp_code, registration_data):
        """Verify registration OTP and complete registration if valid"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Find valid registration OTP
            cursor.execute("""
                SELECT id FROM otp_requests
                WHERE email = ? AND otp_code = ? AND type = 'registration' 
                AND expires_at > ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (email, otp_code, datetime.now().isoformat()))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Invalid or expired OTP code"
            
            otp_id = result['id']
            
            # Begin transaction for registration
            conn.execute("BEGIN TRANSACTION")
            
            try:
                # Check if email is already in use
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    conn.rollback()
                    conn.close()
                    return False, "Email is already in use"
                    
                # Check if student number is already in use
                cursor.execute("SELECT id FROM students WHERE student_number = ?", (registration_data['student_number'],))
                if cursor.fetchone():
                    conn.rollback()
                    conn.close()
                    return False, "Student number is already in use"
                    
                # Hash the password
                hashed_pw = bcrypt.hashpw(registration_data['password'].encode('utf-8'), bcrypt.gensalt())
                
                # Convert date_of_birth string to date format if provided
                birthday = None
                if registration_data.get('date_of_birth'):
                    try:
                        # Validate the date format
                        from datetime import datetime as dt
                        dt.strptime(registration_data['date_of_birth'], "%Y-%m-%d")
                        birthday = registration_data['date_of_birth']
                    except ValueError:
                        conn.rollback()
                        conn.close()
                        return False, "Invalid date format"
                
                # Get default status for new students (Enrolled)
                cursor.execute("SELECT id FROM statuses WHERE name = 'Enrolled' AND user_type = 'student'")
                status_result = cursor.fetchone()
                default_status_id = status_result[0] if status_result else None
                
                if not default_status_id:
                    # Fallback: get any student status if "Enrolled" doesn't exist
                    cursor.execute("SELECT id FROM statuses WHERE user_type = 'student' LIMIT 1")
                    fallback_result = cursor.fetchone()
                    default_status_id = fallback_result[0] if fallback_result else None
                
                # Insert user - set as VERIFIED since OTP was successful with default status
                user_query = """
                INSERT INTO users (first_name, last_name, email, birthday, password_hash, contact_number, role, status_id, face_image, verified, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                current_time = datetime.now().isoformat()
                cursor.execute(user_query, (
                    registration_data['first_name'],
                    registration_data['last_name'],
                    registration_data['email'],
                    birthday,
                    hashed_pw.decode('utf-8'),
                    registration_data.get('contact_number'),
                    "Student",
                    default_status_id,  # Assign default status
                    registration_data.get('face_image'),
                    1,  # verified = 1 (True) - OTP verification means account is verified
                    0,  # isDeleted = 0 (False)
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
                    registration_data['student_number']
                ))
                
                # Delete used OTP
                cursor.execute("DELETE FROM otp_requests WHERE id = ?", (otp_id,))
                
                # Commit transaction
                conn.commit()
                conn.close()
                
                print(f"Successfully registered and verified user: {email} (ID: {user_id}) with status ID: {default_status_id}")
                
                # Send welcome email
                try:
                    self.email_service.send_welcome_email(email, registration_data['first_name'])
                except Exception as e:
                    print(f"Warning: Could not send welcome email: {e}")
                
                return True, {
                    "user_id": user_id,
                    "name": f"{registration_data['first_name']} {registration_data['last_name']}",
                    "email": email,
                    "role": "Student",
                    "student_number": registration_data['student_number']
                }
                    
            except Exception as reg_error:
                conn.rollback()
                conn.close()
                return False, f"Registration failed: {str(reg_error)}"
            
        except Exception as e:
            print(f"Error verifying registration OTP: {e}")
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
                INSERT INTO otp_requests (user_id, otp_code, type, created_at, expires_at, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, otp_code, 'password_reset', datetime.now().isoformat(), expires_at.isoformat(), email))
            
            conn.commit()
            conn.close()
            
            # Send password reset OTP email
            success, message = self.email_service.send_password_reset_otp_email(email, first_name, otp_code)
            
            if success:
                return True, "Password reset verification code sent successfully to your email"
            else:
                return False, f"Failed to send verification code: {message}"
            
        except Exception as e:
            print(f"Error creating password reset OTP: {e}")
            return False, str(e)

    def verify_password_reset_otp(self, email, otp_code):
        """Verify password reset OTP"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Find valid password reset OTP
            cursor.execute("""
                SELECT o.user_id, u.first_name
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
            
            # OTP is valid but don't delete it yet - wait for password reset completion
            conn.close()
            return True, "OTP verified successfully"
            
        except Exception as e:
            print(f"Error verifying password reset OTP: {e}")
            return False, str(e)

    def reset_password_with_otp(self, email, otp_code, new_password):
        """Reset password using OTP verification"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Find valid password reset OTP
            cursor.execute("""
                SELECT o.user_id, o.id
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
            
            user_id, otp_id = result
            
            # Hash the new password
            hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Begin transaction
            conn.execute("BEGIN TRANSACTION")
            
            try:
                # Update user password
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = ?, updated_at = ?
                    WHERE id = ?
                """, (hashed_pw.decode('utf-8'), datetime.now().isoformat(), user_id))
                
                # Delete used OTP
                cursor.execute("DELETE FROM otp_requests WHERE id = ?", (otp_id,))
                
                # Commit transaction
                conn.commit()
                conn.close()
                
                print(f"Password reset successfully for user ID: {user_id}")
                return True, "Password reset successfully"
                
            except Exception as e:
                conn.rollback()
                conn.close()
                return False, f"Failed to reset password: {str(e)}"
            
        except Exception as e:
            print(f"Error resetting password with OTP: {e}")
            return False, str(e)

    def _initialize_database(self):
        """Initialize database tables if they don't exist"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if database is empty (no tables exist)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if not tables:
                # Database is empty, run full initialization
                conn.close()
                print("Empty database detected. Running full initialization...")
                self._run_database_seeder()
                return
            
            # Create statuses table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS statuses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    user_type TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
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
                    email TEXT,
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
            
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN status_id INTEGER REFERENCES statuses(id)")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Add email column to otp_requests if it doesn't exist
            try:
                cursor.execute("ALTER TABLE otp_requests ADD COLUMN email TEXT")
            except sqlite3.OperationalError:
                pass
            
            # Insert default statuses if they don't exist
            self._seed_default_statuses(cursor)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing database: {e}")

    def _seed_default_statuses(self, cursor):
        """Seed default status values"""
        try:
            current_time = datetime.now().isoformat()
            
            # Default student statuses
            student_statuses = [
                ('Enrolled', 'Student is currently enrolled', 'student'),
                ('Graduated', 'Student has graduated', 'student'),
                ('Dropout', 'Student has dropped out', 'student'),
                ('On Leave', 'Student is on leave', 'student'),
                ('Suspended', 'Student is suspended', 'student')
            ]
            
            # Default faculty statuses
            faculty_statuses = [
                ('Active', 'Faculty member is active', 'faculty'),
                ('Inactive', 'Faculty member is inactive', 'faculty'),
                ('Retired', 'Faculty member has retired', 'faculty'),
                ('Probationary', 'Faculty member is on probation', 'faculty'),
                ('Tenure Track', 'Faculty member is on tenure track', 'faculty'),
                ('Tenured', 'Faculty member has tenure', 'faculty')
            ]
            
            all_statuses = student_statuses + faculty_statuses
            
            for name, description, user_type in all_statuses:
                # Check if status already exists
                cursor.execute("SELECT id FROM statuses WHERE name = ? AND user_type = ?", (name, user_type))
                if not cursor.fetchone():
                    # Insert new status
                    cursor.execute("""
                        INSERT INTO statuses (name, description, user_type, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (name, description, user_type, current_time, current_time))
                    print(f"Created default status: {name} ({user_type})")
                    
        except Exception as e:
            print(f"Error seeding default statuses: {e}")

    def _run_database_seeder(self):
        """Run the database seeder for full initialization"""
        try:
            import os
            import subprocess
            import sys
            
            # Get the path to the database seeder
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            seeder_path = os.path.join(current_dir, "app", "db_seeder.py")
            
            # Run the seeder script
            result = subprocess.run([sys.executable, seeder_path], check=True)
            
            if result.returncode == 0:
                print("Database seeder ran successfully")
            else:
                print(f"Database seeder exited with code {result.returncode}")
                
        except Exception as e:
            print(f"Error running database seeder: {e}")
    
    def get_all_users_simple(self):
        """Get all users with basic joins - simple query"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Simple query to get all user data with basic joins
            query = """
            SELECT 
                u.*,
                s.name as status_name,
                st.student_number,
                st.section as section_id,
                f.employee_number,
                sec.name as section_name,
                p.name as program_name
            FROM users u
            LEFT JOIN statuses s ON u.status_id = s.id
            LEFT JOIN students st ON u.id = st.user_id
            LEFT JOIN faculties f ON u.id = f.user_id
            LEFT JOIN sections sec ON st.section = sec.id
            LEFT JOIN programs p ON sec.program_id = p.id
            WHERE u.isDeleted = 0
            ORDER BY u.role, u.last_name, u.first_name
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            users = []
            for row in results:
                user_dict = dict(row)
                # Add full_name for convenience
                user_dict['full_name'] = f"{user_dict['first_name']} {user_dict['last_name']}"
                users.append(user_dict)
            
            conn.close()
            return True, users
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return False, str(e)

    def filter_users_python(self, all_users, search_term="", role_filter="", year_filter="", section_filter="", program_filter="", status_filter=""):
        """Filter users using Python instead of SQL"""
        filtered_users = []
        
        for user in all_users:
            # Apply role filter first
            if role_filter and role_filter != "All":
                if user['role'] != role_filter:
                    continue
            
            # Apply status filter
            if status_filter and status_filter != "All":
                if user.get('status_name') != status_filter:
                    continue
            
            # Apply search term (search in multiple fields)
            if search_term:
                search_fields = [
                    user.get('first_name', ''),
                    user.get('last_name', ''),
                    user.get('email', ''),
                    user.get('student_number', ''),
                    user.get('employee_number', ''),
                    user.get('full_name', '')
                ]
                
                # Check if search term exists in any field
                search_found = False
                for field in search_fields:
                    if field and search_term.lower() in str(field).lower():
                        search_found = True
                        break
                
                if not search_found:
                    continue
            
            # Apply year filter (for students only)
            if year_filter and year_filter != "All" and user['role'] == 'Student':
                section_name = user.get('section_name', '')
                if section_name:
                    # Extract year from section name (e.g., "1-1" -> "1")
                    section_year = section_name.split('-')[0] if '-' in section_name else ''
                    year_mapping = {'1': '1st Year', '2': '2nd Year', '3': '3rd Year', '4': '4th Year'}
                    user_year = year_mapping.get(section_year, '')
                    
                    if user_year != year_filter:
                        continue
                else:
                    # If no section, skip this user for year filter
                    continue
            
            # Apply section filter (for students only)
            if section_filter and section_filter != "All" and user['role'] == 'Student':
                if user.get('section_name') != section_filter:
                    continue
            
            # Apply program filter (for students only)
            if program_filter and program_filter != "All" and user['role'] == 'Student':
                program_name = user.get('program_name', '')
                
                # Handle both full names and abbreviations
                program_matches = False
                if program_filter == 'BSIT' and 'Information Technology' in program_name:
                    program_matches = True
                elif program_filter == 'BSCS' and 'Computer Science' in program_name:
                    program_matches = True
                elif program_filter == 'BSIS' and 'Information Systems' in program_name:
                    program_matches = True
                elif program_name == program_filter:
                    program_matches = True
                
                if not program_matches:
                    continue
            
            # If we reach here, user passes all filters
            filtered_users.append(user)
        
        return filtered_users

    def get_students_with_filters(self, search_term="", year_filter="", section_filter="", program_filter="", status_filter=""):
        """Get filtered students using Python filtering"""
        try:
            # Get all users first
            success, all_users = self.get_all_users_simple()
            if not success:
                return False, all_users
            
            # Filter to only students
            students = [user for user in all_users if user['role'] == 'Student']
            
            # Apply filters using Python
            filtered_students = self.filter_users_python(
                students,
                search_term=search_term,
                role_filter="Student",
                year_filter=year_filter,
                section_filter=section_filter,
                program_filter=program_filter,
                status_filter=status_filter
            )
            
            return True, filtered_students
            
        except Exception as e:
            print(f"Error getting filtered students: {e}")
            return False, str(e)

    def get_faculty_with_filters(self, search_term="", status_filter="", role_filter=""):
        """Get filtered faculty using Python filtering"""
        try:
            # Get all users first
            success, all_users = self.get_all_users_simple()
            if not success:
                return False, all_users
            
            # Filter to only faculty and admin
            faculty = [user for user in all_users if user['role'] in ['Faculty', 'Admin']]
            
            # Apply filters using Python
            filtered_faculty = self.filter_users_python(
                faculty,
                search_term=search_term,
                role_filter=role_filter if role_filter and role_filter != "All" else "",
                status_filter=status_filter
            )
            
            return True, filtered_faculty
            
        except Exception as e:
            print(f"Error getting filtered faculty: {e}")
            return False, str(e)

    def get_attendance_logs(self, user_id=None, course_id=None, date_from=None, date_to=None):
        """Get attendance logs with optional filters"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            base_query = """
            SELECT 
                al.id,
                al.user_id,
                al.assigned_course_id,
                al.date,
                al.status,
                al.created_at,
                u.first_name || ' ' || u.last_name as student_name,
                c.name as course_name,
                s.name as section_name,
                p.name as program_name,
                fu.first_name || ' ' || fu.last_name as faculty_name
            FROM attendance_logs al
            JOIN users u ON al.user_id = u.id
            JOIN assigned_courses ac ON al.assigned_course_id = ac.id
            JOIN courses c ON ac.course_id = c.id
            JOIN sections s ON ac.section_id = s.id
            JOIN programs p ON s.course_id = p.id
            JOIN users fu ON ac.user_id = fu.id
            WHERE u.isDeleted = 0
            """
            
            params = []
            conditions = []
            
            if user_id:
                conditions.append("al.user_id = ?")
                params.append(user_id)
            
            if course_id:
                conditions.append("ac.id = ?")
                params.append(course_id)
            
            if date_from:
                conditions.append("al.date >= ?")
                params.append(date_from)
            
            if date_to:
                conditions.append("al.date <= ?")
                params.append(date_to)
            
            if conditions:
                base_query += " AND " + " AND ".join(conditions)
            
            base_query += " ORDER BY al.date DESC, u.last_name, u.first_name"
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            attendance_logs = []
            for row in results:
                log_dict = dict(row)
                attendance_logs.append(log_dict)
            
            conn.close()
            return True, attendance_logs
            
        except Exception as e:
            print(f"Error getting attendance logs: {e}")
            return False, str(e)

    def get_assigned_courses(self, faculty_id=None):
        """Get assigned courses with optional faculty filter"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                ac.id,
                ac.user_id as faculty_id,
                ac.course_id,
                ac.section_id,
                ac.academic_year,
                ac.semester,
                ac.schedule_day,
                ac.schedule_time,
                ac.room,
                c.name as course_name,
                c.description as course_description,
                s.name as section_name,
                p.name as program_name,
                u.first_name || ' ' || u.last_name as faculty_name
            FROM assigned_courses ac
            JOIN courses c ON ac.course_id = c.id
            JOIN sections s ON ac.section_id = s.id
            JOIN programs p ON s.program_id = p.id
            JOIN users u ON ac.user_id = u.id
            WHERE u.isDeleted = 0
            """
            
            params = []
            if faculty_id:
                query += " AND ac.user_id = ?"
                params.append(faculty_id)
            
            query += " ORDER BY c.name, s.name"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            courses = []
            for row in results:
                course_dict = dict(row)
                courses.append(course_dict)
            
            conn.close()
            return True, courses
            
        except Exception as e:
            print(f"Error getting assigned courses: {e}")
            return False, str(e)

    def get_user_by_name(self, first_name, last_name, role=None):
        """Get user details by name"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT u.*, s.student_number, f.employee_number, st.name as status_name
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            LEFT JOIN faculties f ON u.id = f.user_id
            LEFT JOIN statuses st ON u.status_id = st.id
            WHERE u.first_name = ? AND u.last_name = ?
            """
            
            params = [first_name, last_name]
            
            if role:
                query += " AND u.role = ?"
                params.append(role)
            
            query += " AND u.isDeleted = 0 LIMIT 1"
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, dict(result)
            else:
                return False, "User not found"
                
        except Exception as e:
            print(f"Error getting user by name: {e}")
            return False, str(e)

    def get_course_enrollment_count(self, assigned_course_id):
        """Get number of students with attendance records for a course"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as student_count
                FROM attendance_logs
                WHERE assigned_course_id = ?
            """, (assigned_course_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result['student_count'] if result else 0
            
        except Exception as e:
            print(f"Error getting course enrollment count: {e}")
            return 0

    def get_detailed_attendance_logs(self, user_id=None, assigned_course_id=None, date_from=None, date_to=None, limit=None):
        """Get detailed attendance logs with additional information"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
            SELECT 
                al.*,
                u.first_name || ' ' || u.last_name as student_name,
                u.email as student_email,
                s.student_number,
                c.name as course_name,
                sec.name as section_name,
                p.name as program_name,
                fu.first_name || ' ' || fu.last_name as faculty_name,
                ac.schedule_day,
                ac.schedule_time,
                ac.room
            FROM attendance_logs al
            JOIN users u ON al.user_id = u.id
            JOIN students s ON u.id = s.user_id
            JOIN assigned_courses ac ON al.assigned_course_id = ac.id
            JOIN courses c ON ac.course_id = c.id
            JOIN sections sec ON ac.section_id = sec.id
            JOIN programs p ON sec.program_id = p.id
            JOIN users fu ON ac.user_id = fu.id
            WHERE u.isDeleted = 0
            """
            
            params = []
            
            if user_id:
                query += " AND al.user_id = ?"
                params.append(user_id)
            
            if assigned_course_id:
                query += " AND al.assigned_course_id = ?"
                params.append(assigned_course_id)
            
            if date_from:
                query += " AND al.date >= ?"
                params.append(date_from)
            
            if date_to:
                query += " AND al.date <= ?"
                params.append(date_to)
            
            query += " ORDER BY al.date DESC, al.created_at DESC"
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            logs = [dict(row) for row in results]
            conn.close()
            
            return True, logs
            
        except Exception as e:
            print(f"Error getting detailed attendance logs: {e}")
            return False, str(e)

    def get_student_attendance_summary(self, user_id):
        """Get attendance summary for a specific student"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get attendance summary grouped by course
            query = """
            SELECT 
                c.name as course_name,
                s.name as section_name,
                p.name as program_name,
                COUNT(al.id) as total_classes,
                SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as present_count,
                SUM(CASE WHEN al.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                SUM(CASE WHEN al.status = 'late' THEN 1 ELSE 0 END) as late_count,
                ac.id as assigned_course_id,
                ac.schedule_day,
                ac.schedule_time,
                ac.room,
                ac.semester,
                ac.academic_year
            FROM attendance_logs al
            JOIN assigned_courses ac ON al.assigned_course_id = ac.id
            JOIN courses c ON ac.course_id = c.id
            JOIN sections sec ON ac.section_id = sec.id
            JOIN programs p ON sec.program_id = p.id
            LEFT JOIN sections s ON ac.section_id = s.id
            WHERE al.user_id = ?
            GROUP BY ac.id, c.name, s.name, p.name
            ORDER BY c.name, s.name
            """
            
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            
            summary = []
            for row in results:
                summary_dict = dict(row)
                summary.append(summary_dict)
            
            conn.close()
            return True, summary
            
        except Exception as e:
            print(f"Error getting student attendance summary: {e}")
            return False, str(e)

    def get_user_details(self, user_id):
        """Get detailed user information from database for a specific user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Get comprehensive user data with joins - handle null sections/programs
            query = """
            SELECT 
                u.id, u.first_name, u.last_name, u.email, u.birthday, 
                u.contact_number, u.role, u.face_image, u.status_id, 
                u.verified, u.isDeleted, u.created_at, u.updated_at,
                s.name as status_name,
                st.student_number, st.section as section_id,
                f.employee_number,
                COALESCE(sec.name, '') as section_name,
                COALESCE(p.name, '') as program_name
            FROM users u
            LEFT JOIN statuses s ON u.status_id = s.id
            LEFT JOIN students st ON u.id = st.user_id
            LEFT JOIN faculties f ON u.id = f.user_id
            LEFT JOIN sections sec ON st.section = sec.id
            LEFT JOIN programs p ON sec.program_id = p.id
            WHERE u.id = ? AND u.isDeleted = 0
            """
            
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return (False, "User not found")
            
            # Convert row to dictionary - handle null values properly
            user_data = {
                'id': result['id'],
                'first_name': result['first_name'],
                'last_name': result['last_name'],
                'email': result['email'],
                'birthday': result['birthday'],
                'contact_number': result['contact_number'] or '',
                'role': result['role'],
                'face_image': result['face_image'],
                'status_id': result['status_id'],
                'status_name': result['status_name'] or 'No Status',
                'verified': result['verified'],
                'created_at': result['created_at'],
                'updated_at': result['updated_at'],
                'student_number': result['student_number'] if result['student_number'] else '',
                'section_id': result['section_id'],
                'section_name': result['section_name'] if result['section_name'] else '',
                'employee_number': result['employee_number'] if result['employee_number'] else '',
                'program_name': result['program_name'] if result['program_name'] else ''
            }
            
            conn.close()
            return (True, user_data)
            
        except Exception as e:
            print(f"Error getting user details: {e}")
            return (False, f"Database error: {str(e)}")

    def get_programs(self):
        """Get all available programs"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description 
                FROM programs 
                ORDER BY name
            """)
            
            results = cursor.fetchall()
            programs = [dict(row) for row in results]
            
            conn.close()
            return True, programs
            
        except Exception as e:
            print(f"Error getting programs: {e}")
            return False, str(e)

    def get_sections(self, program_id=None):
        """Get all sections, optionally filtered by program"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if program_id:
                cursor.execute("""
                    SELECT id, name, program_id 
                    FROM sections 
                    WHERE program_id = ?
                    ORDER BY name
                """, (program_id,))
            else:
                cursor.execute("""
                    SELECT s.id, s.name, s.program_id, p.name as program_name
                    FROM sections s
                    JOIN programs p ON s.program_id = p.id
                    ORDER BY p.name, s.name
                """)
            
            results = cursor.fetchall()
            sections = [dict(row) for row in results]
            
            conn.close()
            return True, sections
            
        except Exception as e:
            print(f"Error getting sections: {e}")
            return False, str(e)

    def get_sections_by_program(self, program_id):
        """Get sections filtered by program ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, program_id 
                FROM sections 
                WHERE program_id = ?
                ORDER BY name
            """, (program_id,))
            
            results = cursor.fetchall()
            sections = [dict(row) for row in results]
            
            conn.close()
            return True, sections
            
        except Exception as e:
            print(f"Error getting sections by program: {e}")
            return False, str(e)

    def get_statuses(self, user_type=None):
        """Get all statuses, optionally filtered by user type"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if user_type:
                cursor.execute("""
                    SELECT id, name, description, user_type 
                    FROM statuses 
                    WHERE user_type = ?
                    ORDER BY name
                """, (user_type,))
            else:
                cursor.execute("""
                    SELECT id, name, description, user_type 
                    FROM statuses 
                    ORDER BY user_type, name
                """)
            
            results = cursor.fetchall()
            statuses = [dict(row) for row in results]
            
            conn.close()
            return True, statuses
            
        except Exception as e:
            print(f"Error getting statuses: {e}")
            return False, str(e)

    def get_dropdown_options_for_user_type(self, user_type):
        """Get all dropdown options for a specific user type (student/faculty)"""
        try:
            # Get programs
            success_programs, programs = self.get_programs()
            if not success_programs:
                return False, f"Error fetching programs: {programs}"
            
            # Get sections  
            success_sections, sections = self.get_sections()
            if not success_sections:
                return False, f"Error fetching sections: {sections}"
            
            # Get statuses for this user type
            success_statuses, statuses = self.get_statuses(user_type)
            if not success_statuses:
                return False, f"Error fetching statuses: {statuses}"
            
            # Format for dropdown usage
            dropdown_options = {
                'programs': [{'id': p['id'], 'name': p['name'], 'abbreviation': self._get_program_abbreviation(p['name'])} for p in programs],
                'sections': [{'id': s['id'], 'name': s['name'], 'program_id': s.get('program_id')} for s in sections],
                'statuses': [{'id': s['id'], 'name': s['name']} for s in statuses]
            }
            
            return True, dropdown_options
            
        except Exception as e:
            print(f"Error getting dropdown options: {e}")
            return False, str(e)

    def _get_program_abbreviation(self, program_name):
        """Convert program name to abbreviation"""
        if not program_name:
            return "N/A"
        
        if "Information Technology" in program_name:
            return "BSIT"
        elif "Computer Science" in program_name:
            return "BSCS"  
        elif "Information Systems" in program_name:
            return "BSIS"
        else:
            # Extract abbreviation from name if possible, or return first letters
            words = program_name.split()
            if len(words) >= 2:
                return ''.join([word[0].upper() for word in words])
            return program_name[:4].upper()

    def get_user_section_and_program_ids(self, user_id):
        """Get the current section_id and program_id for a user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT st.section as section_id, s.program_id
                FROM students st
                JOIN sections s ON st.section = s.id
                WHERE st.user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return True, {'section_id': result['section_id'], 'program_id': result['program_id']}
            else:
                return False, "User section/program not found"
                
        except Exception as e:
            print(f"Error getting user section/program: {e}")
            return False, str(e)
