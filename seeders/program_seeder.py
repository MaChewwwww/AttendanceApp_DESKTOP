import sqlite3
from .base_seeder import BaseSeeder
from .config import PROGRAMS_DATA, COURSES_DATA, SECTION_DISTRIBUTIONS

class ProgramSeeder(BaseSeeder):
    """Seeder for programs, courses, and sections"""
    
    def seed(self):
        """Seed programs, courses, and sections"""
        try:
            conn = self.get_connection()
            self.logger.info("Seeding programs, courses, and sections...")
            
            # Seed programs
            program_ids = self._seed_programs(conn)
            
            # Seed courses
            course_ids = self._seed_courses(conn, program_ids)
            
            # Seed sections
            section_ids = self._seed_sections(conn, program_ids)
            
            conn.commit()
            
            # Log summary
            self.log_summary(conn, "programs", "Programs")
            self.log_summary(conn, "courses", "Courses") 
            self.log_summary(conn, "sections", "Sections")
            
            conn.close()
            return True, program_ids, section_ids, course_ids
            
        except Exception as e:
            self.logger.error(f"Error seeding programs and courses: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False, {}, {}, {}
    
    def _seed_programs(self, conn):
        """Seed programs table"""
        program_ids = {}
        current_time = self.get_current_time()
        
        for program_data in PROGRAMS_DATA:
            # Check if exists
            existing = self.check_exists(conn, "programs", {"name": program_data['name']})
            
            if existing:
                program_ids[program_data['name']] = existing[0]
                continue
                
            try:
                cursor = self.execute_query(conn, """
                    INSERT INTO programs (name, acronym, code, description, color, isDeleted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    program_data['name'], program_data['acronym'], program_data['code'],
                    program_data['description'], program_data['color'], 0, current_time, current_time
                ))
                
                program_id = cursor.lastrowid
                program_ids[program_data['name']] = program_id
                self.logger.info(f"✓ Created program: {program_data['name']} ({program_data['acronym']})")
                
            except sqlite3.IntegrityError as e:
                self.logger.error(f"Failed to create program {program_data['name']}: {e}")
                continue
                
        return program_ids
    
    def _seed_courses(self, conn, program_ids):
        """Seed courses"""
        course_ids = {}
        current_time = self.get_current_time()
        
        for course_data in COURSES_DATA:
            if course_data['program'] not in program_ids:
                continue
                
            program_id = program_ids[course_data['program']]
            
            # Check if exists
            existing = self.check_exists(conn, "courses", {
                "code": course_data['code'],
                "program_id": program_id
            })
            
            if existing:
                course_ids[course_data['name']] = existing[0]
                continue
            
            try:
                cursor = self.execute_query(conn, """
                    INSERT INTO courses (name, code, description, program_id, isDeleted, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    course_data['name'], course_data['code'], course_data['description'],
                    program_id, 0, current_time, current_time
                ))
                
                course_id = cursor.lastrowid
                course_ids[course_data['name']] = course_id
                
            except sqlite3.Error as e:
                self.logger.error(f"Failed to create course {course_data['name']}: {e}")
                continue
        
        return course_ids
    
    def _seed_sections(self, conn, program_ids):
        """Seed sections for each program"""
        section_ids = {}
        current_time = self.get_current_time()
        
        for program_name, sections in SECTION_DISTRIBUTIONS.items():
            if program_name not in program_ids:
                continue
                
            program_id = program_ids[program_name]
            
            for section_name in sections:
                section_key = f"{section_name}-{program_name}"
                
                # Check if exists
                existing = self.check_exists(conn, "sections", {
                    "name": section_name,
                    "program_id": program_id
                })
                
                if existing:
                    section_ids[section_key] = existing[0]
                    continue
                
                try:
                    cursor = self.execute_query(conn, """
                        INSERT INTO sections (name, program_id, isDeleted, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (section_name, program_id, 0, current_time, current_time))
                    
                    section_id = cursor.lastrowid
                    section_ids[section_key] = section_id
                    
                except sqlite3.Error as e:
                    self.logger.error(f"Failed to create section {section_name}: {e}")
                    continue
        
        return section_ids
