import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Root directory path (parent of app directory)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "data", "attendance_app.db")

# Make sure parent directory exists
db_dir = os.path.dirname(DB_PATH)
if not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

# App settings
APP_NAME = "Attendance App"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Theme settings
THEME_NAME = "darkly"  # ttkbootstrap theme

# Paths
UPLOAD_DIR = os.path.join(ROOT_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)