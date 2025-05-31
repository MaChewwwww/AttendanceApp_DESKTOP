from sqlalchemy import create_engine
from models import Base, User, Student, Faculty  # Import all model classes
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Use relative path from the current script location
SCRIPT_DIR = Path(__file__).parent  # Directory where create_db.py is located
DATA_DIR = SCRIPT_DIR / "data"  # data folder relative to script
DEFAULT_DB_PATH = DATA_DIR / "attendance_app.db"

# Get database path from environment variable or use default
DB_PATH = os.getenv("DB_PATH", str(DEFAULT_DB_PATH))

# Delete the database file if it exists
if os.path.exists(DB_PATH):
    try:
        logger.info(f"Removing existing database at: {DB_PATH}")
        os.remove(DB_PATH)
        logger.info("Existing database removed successfully")
    except Exception as e:
        logger.error(f"Failed to remove existing database: {str(e)}")
        exit(1)  # Exit if we can't remove the existing database

# Ensure directory exists
DATA_DIR.mkdir(exist_ok=True)  # Create data directory if it doesn't exist

logger.info(f"Creating new database at: {DB_PATH}")

# Create SQLite engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Create all tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    logger.info(f"Tables in database: {tables}")
    
    if 'users' not in tables:
        logger.error("Users table not found after creation!")
        exit(1)  # Exit if users table wasn't created
    else:
        logger.info("Users table successfully created")
except Exception as e:
    logger.exception(f"Error creating database tables: {str(e)}")
    exit(1)  # Exit if table creation failed

print(f"Database successfully created at: {DB_PATH}")
print(f"Tables created: {', '.join(tables)}")

# Automatically run the seeder
print("\nRunning database seeder...")
try:
    import subprocess
    import sys
    
    # Run the seeder
    result = subprocess.run([sys.executable, "seed_db.py"], 
                          capture_output=True, text=True, check=True)
    print(result.stdout)
    
except subprocess.CalledProcessError as e:
    print(f"Error running seeder: {e}")
    print(f"Stderr: {e.stderr}")
except Exception as e:
    print(f"Error running seeder: {e}")
    print("You can manually run 'python seed_db.py' to seed the database.")