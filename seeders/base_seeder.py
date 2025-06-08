import sqlite3
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from .config import DB_PATH

class BaseSeeder(ABC):
    """Base class for all seeders providing common database operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(DB_PATH)
    
    def get_current_time(self):
        """Get current timestamp for database records"""
        return datetime.now().isoformat()
        
    def execute_query(self, conn, query, params=None):
        """Execute a query with proper error handling"""
        try:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except sqlite3.Error as e:
            self.logger.error(f"Database error: {e}")
            raise
    
    def check_exists(self, conn, table, conditions):
        """Check if record exists based on conditions"""
        where_clause = " AND ".join([f"{k} = ?" for k in conditions.keys()])
        query = f"SELECT id FROM {table} WHERE {where_clause}"
        cursor = self.execute_query(conn, query, list(conditions.values()))
        return cursor.fetchone()
    
    @abstractmethod
    def seed(self):
        """Main seeding method to be implemented by subclasses"""
        pass
    
    def log_summary(self, conn, table_name, description=""):
        """Log summary statistics for a table"""
        cursor = self.execute_query(conn, f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        self.logger.info(f"✓ {description or table_name.title()}: {count} records")
        return count
