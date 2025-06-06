import sqlite3
import bcrypt
import random
import string
from datetime import datetime, timedelta
from .email_service import EmailService

class DatabaseAuthManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.email_service = EmailService()
    
    def check_email_exists(self, email):
        """Check if an email address is already registered
        
        Returns:
            tuple: (success, message) where success is True if email exists
        """
        try:
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM students WHERE student_number = ?", (student_id,))
            count = cursor.fetchone()[0]
            
            conn.close()
            
            if count > 0:
                return True, "Student ID already exists"
            else:
                return False, "Student ID is available"
                
        except Exception as e:
            print(f"Database error checking student ID: {str(e)}")
            return False, f"Error checking student ID: {str(e)}"

    def check_employee_number_exists(self, employee_number):
        """Check if an employee number is already registered
        
        Returns:
            tuple: (success, message) where success is True if employee number exists
        """
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM faculties WHERE employee_number = ?", (employee_number,))
            count = cursor.fetchone()[0]
            
            conn.close()
            
            if count > 0:
                return True, "Employee number already exists"
            else:
                return False, "Employee number is available"
                
        except Exception as e:
            print(f"Database error checking employee number: {str(e)}")
            return False, f"Error checking employee number: {str(e)}"
    
    def login(self, email, password):
        """Authenticate user login"""
        conn = None
        cursor = None
        try:
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
            conn = self.db_manager.get_connection()
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
