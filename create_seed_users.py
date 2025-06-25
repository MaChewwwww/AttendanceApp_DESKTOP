import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to run comprehensive seeding"""
    try:
        from seeders.main_seeder import run_all_seeders
        
        print("=" * 60)
        print("COMPREHENSIVE DATABASE SEEDING")
        print("=" * 60)
        print("This will populate your database with:")
        print("  - Programs, courses, and sections")
        print("  - Faculty and student users")
        print("  - Course assignments and schedules") 
        print("  - Realistic attendance data")
        print("=" * 60)
        
        # Get database path from environment variable
        DB_PATH = os.getenv('DB_PATH')
        if not DB_PATH:
            print("❌ DB_PATH not found in environment variables")
            print("Please check your .env file")
            return False
            
        if not os.path.exists(DB_PATH):
            print(f"❌ Database not found at: {DB_PATH}")
            print("Please run 'python create_db.py' first to create the database")
            return False
        
        success = run_all_seeders()
        
        if success:
            print("\n✅ COMPREHENSIVE SEEDING COMPLETED SUCCESSFULLY!")
            print("Your database is now fully populated and ready to use!")
        else:
            print("\n❌ SEEDING FAILED!")
            print("Check the logs above for error details.")
            
        return success
        
    except ImportError as e:
        print(f"❌ Error importing seeder modules: {e}")
        print("Make sure all seeder files are in the 'seeders' directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Database seeded successfully!")
    else:
        print("\n💥 Failed to seed database!")
        exit(1)
