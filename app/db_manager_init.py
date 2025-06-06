import sqlite3
import os
import subprocess
import sys
from datetime import datetime

class DatabaseInitManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def initialize_database(self):
        """Initialize database if it doesn't exist by running external scripts"""
        try:
            from .config import DB_PATH
            
            # Check if database file exists
            if not os.path.exists(DB_PATH):
                print("Database not found. Creating new database...")
                return self.run_database_creation_scripts()
            
            # Database exists, check if it has basic tables
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Check if we have the essential tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            essential_tables = ['users', 'statuses', 'programs', 'courses', 'sections']
            missing_tables = [table for table in essential_tables if table not in existing_tables]
            
            conn.close()
            
            if missing_tables:
                print(f"Database exists but missing essential tables: {missing_tables}")
                print("Recreating database...")
                return self.run_database_creation_scripts()
            
            print("✓ Database exists and appears to be properly initialized")
            return True
            
        except Exception as e:
            print(f"Error checking database: {e}")
            print("Attempting to recreate database...")
            return self.run_database_creation_scripts()

    def run_database_creation_scripts(self):
        """Run create_db.py and create_seed_users.py"""
        try:
            # Get the root directory (parent of app directory)
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Paths to the scripts
            create_db_script = os.path.join(current_dir, "create_db.py")
            create_seed_script = os.path.join(current_dir, "create_seed_users.py")
            
            # Check if scripts exist
            if not os.path.exists(create_db_script):
                print(f"Error: create_db.py not found at {create_db_script}")
                return False
                
            if not os.path.exists(create_seed_script):
                print(f"Error: create_seed_users.py not found at {create_seed_script}")
                return False
            
            print("Running create_db.py...")
            # Run create_db.py with proper encoding handling
            result = subprocess.run([sys.executable, create_db_script], 
                                  capture_output=True, text=True, cwd=current_dir,
                                  encoding='utf-8', errors='replace')
            
            if result.returncode != 0:
                print(f"create_db.py completed but returned error code: {result.returncode}")
                # Print output even if there's an error code, as the database might still be created
                if result.stdout:
                    print("STDOUT:", result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                # Don't return False immediately, check if database was actually created
            else:
                print("create_db.py completed successfully")
            
            # Check if database was actually created regardless of return code
            from .config import DB_PATH
            if not os.path.exists(DB_PATH):
                print("Database file was not created")
                return False
            
            print("Database structure created successfully")
            print("Running create_seed_users.py...")
            
            # Run create_seed_users.py with proper encoding handling
            result = subprocess.run([sys.executable, create_seed_script], 
                                  capture_output=True, text=True, cwd=current_dir,
                                  encoding='utf-8', errors='replace')
            
            if result.returncode != 0:
                print(f"Error running create_seed_users.py:")
                if result.stdout:
                    print("STDOUT:", result.stdout)
                if result.stderr:
                    print("STDERR:", result.stderr)
                return False
            
            print("Sample data created successfully")
            print("Database initialization completed!")
            return True
            
        except Exception as e:
            print(f"Error running database creation scripts: {e}")
            return False

    def get_database_info(self):
        """Get basic information about the database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get database size (in a simple way)
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'table_count': table_count,
                'tables': tables,
                'initialized': len(tables) > 0
            }
            
        except Exception as e:
            print(f"Error getting database info: {e}")
            return {
                'table_count': 0,
                'tables': [],
                'initialized': False,
                'error': str(e)
            }

    def reset_database(self):
        """Reset the database by running the creation scripts again"""
        try:
            from .config import DB_PATH
            
            # Remove existing database file
            if os.path.exists(DB_PATH):
                os.remove(DB_PATH)
                print("Existing database removed")
            
            # Run creation scripts
            return self.run_database_creation_scripts()
            
        except Exception as e:
            print(f"Error resetting database: {e}")
            return False

    def backup_database(self, backup_path):
        """Create a backup of the database"""
        try:
            import shutil
            from .config import DB_PATH
            
            shutil.copy2(DB_PATH, backup_path)
            print(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error backing up database: {e}")
            return False

    def restore_database(self, backup_path):
        """Restore database from backup"""
        try:
            import shutil
            from .config import DB_PATH
            
            if not os.path.exists(backup_path):
                print(f"Backup file not found: {backup_path}")
                return False
            
            shutil.copy2(backup_path, DB_PATH)
            print(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Error restoring database: {e}")
            return False
