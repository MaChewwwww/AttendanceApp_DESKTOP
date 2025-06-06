from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


Base = declarative_base()
class Status(Base):
    __tablename__ = "statuses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    user_type = Column(String(20), nullable=False)  # 'student' or 'faculty'
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=False)
    birthday = Column(Date, nullable=False)
    password_hash = Column(String(255), nullable=False)
    contact_number = Column(String(20), nullable=False)
    role = Column(String(50), nullable=False, default="Student")
    status_id = Column(Integer, ForeignKey("statuses.id"), nullable=True)  # Added status reference
    face_image = Column(LargeBinary, nullable=True)  # LargeBinary (LBLOB)
    verified = Column(Integer, nullable=False, default=0)  # 0 for False, 1 for True
    isDeleted = Column(Integer, nullable=False, default=0)  # 0 for False, 1 for True
    last_verified_otp = Column(DateTime, nullable=True)  # Last OTP verification time
    last_verified_otp_expiry = Column(DateTime, nullable=True)  # Last OTP expiry time
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_number = Column(String(50), unique=True, nullable=False)  
    section = Column(Integer, ForeignKey("sections.id"), nullable=True)

class Faculty(Base):
    __tablename__ = "faculties"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_number = Column(String(50), unique=True, nullable=False)

class OTP_Request(Base):
    __tablename__ = "otp_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp_code = Column(String(6), nullable=False)  # Assuming OTP is a 6-digit code
    type = Column(String(50), nullable=False)  # e.g., "login", "registration", "password_reset"
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)  # When the OTP expires

class Program(Base):
    __tablename__ = "programs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    acronym = Column(String(50), nullable=False, unique=True) 
    code = Column(String(50), nullable=False, unique=True) 
    description = Column(String(255), nullable=True)
    color = Column(String(7), nullable=True)  # Hex color code like #FF5733
    isDeleted = Column(Integer, nullable=False, default=0)  # 0 for False, 1 for True
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class Section(Base):
    __tablename__ = "sections"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class Assigned_Course(Base):
    __tablename__ = "assigned_courses"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    semester = Column(String(50), nullable=False)
    school_year = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, index=True)
    assigned_course_id = Column(Integer, ForeignKey("assigned_courses.id"), nullable=False)
    day_of_week = Column(String(50), nullable=False)  # e.g., "Monday", "Tuesday"
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())


class AttendanceLog(Base):
    __tablename__ = "attendance_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_course_id = Column(Integer, ForeignKey("assigned_courses.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    image = Column(LargeBinary, nullable=True)  # Changed from LONGBLOB to LargeBinary
    status = Column(String(50), nullable=False)  # e.g., "present", "absent", "late"
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())



    
class LoginRequest(BaseModel):
    email: str
    password: str