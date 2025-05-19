import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SQLite Database settings - using external database
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "attendance_app.db")
DB_FILE = os.environ.get("DB_FILE", DEFAULT_DB_PATH)

# Make sure parent directory exists
db_dir = os.path.dirname(DB_FILE)
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
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)