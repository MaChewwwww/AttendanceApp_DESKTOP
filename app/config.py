import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
ROOT_DIR = os.getenv('ROOT_DIR', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.getenv('DB_PATH', os.path.join(ROOT_DIR, 'data', 'attendance.db'))

# Make sure parent directory exists
db_dir = os.path.dirname(DB_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

# App settings
APP_NAME = os.getenv('APP_NAME', 'Attendance App')
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Theme settings
THEME_NAME = "darkly"  # ttkbootstrap theme

# Paths - use environment variable or default
UPLOAD_DIR = os.getenv('UPLOAD_DIR', os.path.join(ROOT_DIR, "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Email settings
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Google App Password
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'

# Email templates
EMAIL_VERIFICATION_SUBJECT = os.getenv('EMAIL_VERIFICATION_SUBJECT', 'Verify Your Email - AttendanceApp')
EMAIL_PASSWORD_RESET_SUBJECT = os.getenv('EMAIL_PASSWORD_RESET_SUBJECT', 'Password Reset - AttendanceApp')
EMAIL_LOGIN_OTP_SUBJECT = os.getenv('EMAIL_LOGIN_OTP_SUBJECT', 'Your AttendanceApp login code')