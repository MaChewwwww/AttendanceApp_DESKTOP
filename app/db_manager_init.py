import sqlite3
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

class DatabaseInitManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def initialize_database(self):
        """Check if database exists and is properly initialized"""
        try:
            # Get DB_PATH directly from environment variable
            DB_PATH = os.getenv('DB_PATH')
            if not DB_PATH:
                print("❌ Error: DB_PATH not found in environment variables")
                print("Please check your .env file")
                return False
            
            # Check if database file exists
            if not os.path.exists(DB_PATH):
                print("❌ Database not found!")
                print(f"Expected location: {DB_PATH}")
                print("\nTo create the database, run:")
                print("  python create_db.py")
                return False
            
            # Database exists, check if it has basic tables
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                # Check if we have the essential tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                essential_tables = ['users', 'statuses', 'programs', 'courses', 'sections']
                missing_tables = [table for table in essential_tables if table not in existing_tables]
                
                conn.close()
                
                if missing_tables:
                    print(f"❌ Database exists but missing essential tables: {missing_tables}")
                    print("Please recreate the database by running:")
                    print("  python create_db.py")
                    return False
                
                print("✓ Database found and properly initialized")
                return True
                
            except Exception as e:
                print(f"❌ Error checking database structure: {e}")
                print("Database may be corrupted. Please recreate it by running:")
                print("  python create_db.py")
                return False
            
        except Exception as e:
            print(f"❌ Error during database initialization: {e}")
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
