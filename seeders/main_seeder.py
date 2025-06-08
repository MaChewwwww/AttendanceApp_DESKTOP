import logging
import os
from .config import DB_PATH
from .program_seeder import ProgramSeeder
from .user_seeder import UserSeeder
from .course_assignment_seeder import CourseAssignmentSeeder
from .attendance_seeder import AttendanceSeeder

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_all_seeders():
    """Run all seeders in the correct order"""
    
    if not os.path.exists(DB_PATH):
        logger.error(f"Database not found at: {DB_PATH}")
        logger.error("Please run create_db.py first to create the database")
        return False
    
    try:
        logger.info("Starting comprehensive database seeding...")
        
        # 1. Seed programs, courses, and sections
        logger.info("STEP 1: Seeding programs, courses, and sections...")
        program_seeder = ProgramSeeder()
        success, program_ids, section_ids, course_ids = program_seeder.seed()
        if not success:
            logger.error("Failed to seed programs")
            return False
        logger.info(f"✓ Created {len(program_ids)} programs, {len(section_ids)} sections, {len(course_ids)} courses")
        
        # 2. Seed users (faculty and students)
        logger.info("STEP 2: Seeding users (faculty and students)...")
        user_seeder = UserSeeder()
        success = user_seeder.seed(section_ids)
        if not success:
            logger.error("Failed to seed users")
            return False
        logger.info("✓ Successfully created users")
        
        # 3. Seed course assignments
        logger.info("STEP 3: Seeding course assignments and schedules...")
        assignment_seeder = CourseAssignmentSeeder()
        success, assigned_course_ids = assignment_seeder.seed()
        if not success:
            logger.error("Failed to seed course assignments")
            return False
        logger.info(f"✓ Created {len(assigned_course_ids)} course assignments")
        
        # 4. Seed attendance logs
        logger.info("STEP 4: Seeding attendance logs...")
        attendance_seeder = AttendanceSeeder()
        success = attendance_seeder.seed(assigned_course_ids)
        if not success:
            logger.error("Failed to seed attendance logs")
            return False
        logger.info("✓ Successfully created attendance logs")
        
        logger.info("✅ All seeders completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during seeding process: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running comprehensive database seeding...")
    success = run_all_seeders()
    if success:
        print("\n✅ Database seeded successfully!")
    else:
        print("\n❌ Failed to seed database!")
        exit(1)
