import bcrypt
import random
from .base_seeder import BaseSeeder

class UserSeeder(BaseSeeder):
    """Seeder for users, students, and faculty"""
    
    def seed(self, section_ids):
        """Seed users with their roles"""
        try:
            conn = self.get_connection()
            self.logger.info("Seeding users...")
            
            # Get statuses
            statuses = self._get_statuses(conn)
            
            # Seed faculty (30 faculty members)
            self._seed_faculty(conn, statuses['faculty'])
            
            # Seed students (50 students)
            self._seed_students(conn, statuses['student'], section_ids)
            
            conn.commit()
            
            # Log summary
            self.log_summary(conn, "users", "Total users")
            self.log_summary(conn, "faculties", "Faculty members")
            self.log_summary(conn, "students", "Students")
            
            conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error seeding users: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def _get_statuses(self, conn):
        """Get available statuses for users"""
        cursor = self.execute_query(conn, "SELECT id, name, user_type FROM statuses")
        statuses = cursor.fetchall()
        
        return {
            'student': {s[1]: s[0] for s in statuses if s[2] == 'student'},
            'faculty': {s[1]: s[0] for s in statuses if s[2] == 'faculty'}
        }
    
    def _seed_faculty(self, conn, faculty_statuses):
        """Seed 30 faculty users with diverse backgrounds"""
        faculty_data = [
            # Department Heads and Senior Faculty
            {'first_name': 'Dr. Maria', 'last_name': 'Santos', 'email': 'maria.santos@pup.edu.ph', 'birthday': '1975-03-15', 'password': 'faculty123', 'contact_number': '09123456789', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2015-001', 'status': 'Tenured'},
            {'first_name': 'Prof. John', 'last_name': 'Doe', 'email': 'john.doe@pup.edu.ph', 'birthday': '1978-07-22', 'password': 'faculty123', 'contact_number': '09234567890', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2016-002', 'status': 'Tenured'},
            {'first_name': 'Dr. Jane', 'last_name': 'Smith', 'email': 'jane.smith@pup.edu.ph', 'birthday': '1980-11-30', 'password': 'faculty123', 'contact_number': '09345678901', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2017-003', 'status': 'Tenured'},
            {'first_name': 'Dr. Patricia', 'last_name': 'Reyes', 'email': 'patricia.reyes@pup.edu.ph', 'birthday': '1973-09-12', 'password': 'faculty123', 'contact_number': '09456789012', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2014-004', 'status': 'Tenured'},
            {'first_name': 'Prof. Michael', 'last_name': 'Torres', 'email': 'michael.torres@pup.edu.ph', 'birthday': '1979-01-28', 'password': 'faculty123', 'contact_number': '09567890123', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2018-005', 'status': 'Tenure Track'},
            
            # Associate Professors
            {'first_name': 'Dr. Sarah', 'last_name': 'Villanueva', 'email': 'sarah.villanueva@pup.edu.ph', 'birthday': '1982-12-05', 'password': 'faculty123', 'contact_number': '09678901234', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2019-006', 'status': 'Tenure Track'},
            {'first_name': 'Prof. Robert', 'last_name': 'Garcia', 'email': 'robert.garcia@pup.edu.ph', 'birthday': '1981-04-18', 'password': 'faculty123', 'contact_number': '09789012345', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2020-007', 'status': 'Active'},
            {'first_name': 'Dr. Anna', 'last_name': 'Martinez', 'email': 'anna.martinez@pup.edu.ph', 'birthday': '1984-08-25', 'password': 'faculty123', 'contact_number': '09890123456', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2020-008', 'status': 'Active'},
            {'first_name': 'Prof. David', 'last_name': 'Lopez', 'email': 'david.lopez@pup.edu.ph', 'birthday': '1983-06-14', 'password': 'faculty123', 'contact_number': '09901234567', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2021-009', 'status': 'Active'},
            {'first_name': 'Dr. Elena', 'last_name': 'Cruz', 'email': 'elena.cruz@pup.edu.ph', 'birthday': '1985-10-03', 'password': 'faculty123', 'contact_number': '09012345678', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2021-010', 'status': 'Active'},
            
            # Assistant Professors
            {'first_name': 'Prof. James', 'last_name': 'Rodriguez', 'email': 'james.rodriguez@pup.edu.ph', 'birthday': '1986-02-20', 'password': 'faculty123', 'contact_number': '09123456780', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2022-011', 'status': 'Probationary'},
            {'first_name': 'Dr. Lisa', 'last_name': 'Fernandez', 'email': 'lisa.fernandez@pup.edu.ph', 'birthday': '1987-05-17', 'password': 'faculty123', 'contact_number': '09234567891', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2022-012', 'status': 'Probationary'},
            {'first_name': 'Prof. Carlos', 'last_name': 'Mendoza', 'email': 'carlos.mendoza@pup.edu.ph', 'birthday': '1988-09-11', 'password': 'faculty123', 'contact_number': '09345678902', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2023-013', 'status': 'Probationary'},
            {'first_name': 'Dr. Michelle', 'last_name': 'Perez', 'email': 'michelle.perez@pup.edu.ph', 'birthday': '1989-12-08', 'password': 'faculty123', 'contact_number': '09456789013', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2023-014', 'status': 'Active'},
            {'first_name': 'Prof. Kevin', 'last_name': 'Gonzales', 'email': 'kevin.gonzales@pup.edu.ph', 'birthday': '1990-03-22', 'password': 'faculty123', 'contact_number': '09567890124', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2024-015', 'status': 'Active'},
            
            # Additional Faculty (15 more)
            {'first_name': 'Dr. Rachel', 'last_name': 'Rivera', 'email': 'rachel.rivera@pup.edu.ph', 'birthday': '1981-07-30', 'password': 'faculty123', 'contact_number': '09678901235', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2019-016', 'status': 'Tenure Track'},
            {'first_name': 'Prof. Mark', 'last_name': 'Diaz', 'email': 'mark.diaz@pup.edu.ph', 'birthday': '1985-11-15', 'password': 'faculty123', 'contact_number': '09789012346', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2021-017', 'status': 'Active'},
            {'first_name': 'Dr. Catherine', 'last_name': 'Morales', 'email': 'catherine.morales@pup.edu.ph', 'birthday': '1983-04-12', 'password': 'faculty123', 'contact_number': '09890123457', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2020-018', 'status': 'Active'},
            {'first_name': 'Prof. Steven', 'last_name': 'Castillo', 'email': 'steven.castillo@pup.edu.ph', 'birthday': '1987-08-07', 'password': 'faculty123', 'contact_number': '09901234568', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2022-019', 'status': 'Probationary'},
            {'first_name': 'Dr. Amanda', 'last_name': 'Ramos', 'email': 'amanda.ramos@pup.edu.ph', 'birthday': '1986-01-25', 'password': 'faculty123', 'contact_number': '09012345679', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2022-020', 'status': 'Active'},
            {'first_name': 'Prof. Daniel', 'last_name': 'Herrera', 'email': 'daniel.herrera@pup.edu.ph', 'birthday': '1988-06-18', 'password': 'faculty123', 'contact_number': '09123456781', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2023-021', 'status': 'Active'},
            {'first_name': 'Dr. Nicole', 'last_name': 'Flores', 'email': 'nicole.flores@pup.edu.ph', 'birthday': '1984-09-03', 'password': 'faculty123', 'contact_number': '09234567892', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2021-022', 'status': 'Active'},
            {'first_name': 'Prof. Anthony', 'last_name': 'Valdez', 'email': 'anthony.valdez@pup.edu.ph', 'birthday': '1989-12-14', 'password': 'faculty123', 'contact_number': '09345678903', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2023-023', 'status': 'Probationary'},
            {'first_name': 'Dr. Stephanie', 'last_name': 'Jimenez', 'email': 'stephanie.jimenez@pup.edu.ph', 'birthday': '1987-05-09', 'password': 'faculty123', 'contact_number': '09456789014', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2022-024', 'status': 'Active'},
            {'first_name': 'Prof. Jason', 'last_name': 'Aguilar', 'email': 'jason.aguilar@pup.edu.ph', 'birthday': '1990-02-28', 'password': 'faculty123', 'contact_number': '09567890125', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2024-025', 'status': 'Active'},
            {'first_name': 'Dr. Jennifer', 'last_name': 'Vargas', 'email': 'jennifer.vargas@pup.edu.ph', 'birthday': '1985-10-21', 'password': 'faculty123', 'contact_number': '09678901236', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2021-026', 'status': 'Active'},
            {'first_name': 'Prof. Ryan', 'last_name': 'Ortega', 'email': 'ryan.ortega@pup.edu.ph', 'birthday': '1988-07-16', 'password': 'faculty123', 'contact_number': '09789012347', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2023-027', 'status': 'Probationary'},
            {'first_name': 'Dr. Melissa', 'last_name': 'Gutierrez', 'email': 'melissa.gutierrez@pup.edu.ph', 'birthday': '1986-11-05', 'password': 'faculty123', 'contact_number': '09890123458', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2022-028', 'status': 'Active'},
            {'first_name': 'Prof. Brian', 'last_name': 'Medina', 'email': 'brian.medina@pup.edu.ph', 'birthday': '1991-04-13', 'password': 'faculty123', 'contact_number': '09901234569', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2024-029', 'status': 'Active'},
            {'first_name': 'Dr. Laura', 'last_name': 'Sandoval', 'email': 'laura.sandoval@pup.edu.ph', 'birthday': '1984-08-27', 'password': 'faculty123', 'contact_number': '09012345680', 'role': 'Faculty', 'verified': 1, 'employee_number': 'EMP-2021-030', 'status': 'Active'}
        ]
        
        current_time = self.get_current_time()
        
        for faculty in faculty_data:
            # Check if exists
            existing = self.check_exists(conn, "users", {"email": faculty['email']})
            if existing:
                continue
            
            # Hash password
            hashed_pw = bcrypt.hashpw(faculty['password'].encode('utf-8'), bcrypt.gensalt())
            
            # Get status ID
            status_id = faculty_statuses.get(faculty['status'])
            
            # Insert user
            cursor = self.execute_query(conn, """
                INSERT INTO users (first_name, last_name, email, birthday, password_hash, 
                                 contact_number, role, status_id, verified, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                faculty['first_name'], faculty['last_name'], faculty['email'], faculty['birthday'],
                hashed_pw.decode('utf-8'), faculty['contact_number'], faculty['role'],
                status_id, faculty['verified'], 0, current_time, current_time
            ))
            
            user_id = cursor.lastrowid
            
            # Insert into faculties table
            self.execute_query(conn, """
                INSERT INTO faculties (user_id, employee_number) VALUES (?, ?)
            """, (user_id, faculty['employee_number']))
    
    def _seed_students(self, conn, student_statuses, section_ids):
        """Seed 50 students with realistic Philippine names"""
        # Generate 50 realistic students
        filipino_first_names = [
            # Male names
            'Juan', 'Jose', 'Mark', 'John', 'Miguel', 'Carlo', 'Angelo', 'Paul', 'Christian', 'Rafael',
            'Gabriel', 'Anthony', 'Daniel', 'Joshua', 'Matthew', 'Emmanuel', 'Francis', 'Vincent', 'Leo', 'Adrian',
            'Kenneth', 'Kevin', 'Ryan', 'Jerome', 'Jasper', 'Cedric', 'Ronnie', 'Rodel', 'Arnel', 'Edgar',
            # Female names
            'Maria', 'Ana', 'Rose', 'Grace', 'Joy', 'Angel', 'Princess', 'Christine', 'Michelle', 'Sarah',
            'Angelica', 'Mary', 'Cristina', 'Jennifer', 'Catherine', 'Stephanie', 'Nicole', 'Jessica', 'Patricia', 'Jasmine'
        ]
        
        filipino_last_names = [
            'Santos', 'Reyes', 'Cruz', 'Bautista', 'Ocampo', 'Garcia', 'Mendoza', 'Torres', 'Tomas', 'Andres',
            'Marquez', 'Romualdez', 'Mercado', 'Agbayani', 'Tolentino', 'Castillo', 'Villanueva', 'Soriano', 'Abad', 'Hernandez',
            'Morales', 'Castro', 'Ramos', 'Gutierrez', 'Gonzales', 'Rodriguez', 'Perez', 'Sanchez', 'Ramirez', 'Flores',
            'Rivera', 'Martinez', 'Gomez', 'Lopez', 'Gonzalez', 'Dela Cruz', 'De Leon', 'Del Rosario', 'Fernandez', 'Aguilar',
            'Jimenez', 'Vargas', 'Herrera', 'Medina', 'Ruiz', 'Aquino', 'Diaz', 'Navarro', 'Pascual', 'Salazar'
        ]
        
        student_data = []
        section_list = list(section_ids.keys()) if section_ids else ['default']
        
        # Get programs for proper section assignment
        cursor = self.execute_query(conn, """
            SELECT p.name, s.name as section_name 
            FROM programs p 
            JOIN sections s ON p.id = s.program_id
        """)
        program_sections = cursor.fetchall()
        program_section_map = {f"{section}-{program}": program for program, section in program_sections}
        
        for i in range(1, 51):  # Generate 50 students
            first_name = random.choice(filipino_first_names)
            last_name = random.choice(filipino_last_names)
            
            # Assign to sections with realistic distribution
            section_key = random.choice(section_list)
            program_name = program_section_map.get(section_key, 'Bachelor of Science in Information Technology')
            section_name = section_key.split('-')[0] + '-' + section_key.split('-')[1] if '-' in section_key else '1-1'
            
            # Generate realistic birth years based on year level
            year_level = section_name.split('-')[0] if '-' in section_name else '1'
            if year_level == '1':
                birth_year = random.randint(2003, 2005)  # 19-21 years old
            elif year_level == '2':
                birth_year = random.randint(2002, 2004)  # 20-22 years old  
            elif year_level == '3':
                birth_year = random.randint(2001, 2003)  # 21-23 years old
            else:  # 4th year
                birth_year = random.randint(2000, 2002)  # 22-24 years old
            
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birthday = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
            
            # Generate realistic status distribution
            status_weights = [
                ('Enrolled', 85),     # 85% enrolled
                ('On Leave', 8),      # 8% on leave
                ('Suspended', 3),     # 3% suspended
                ('Graduated', 3),     # 3% graduated (mostly 4th years)
                ('Dropout', 1)        # 1% dropout
            ]
            
            # Adjust status based on year level
            if year_level == '4':
                status_weights = [('Enrolled', 70), ('Graduated', 25), ('On Leave', 3), ('Suspended', 1), ('Dropout', 1)]
            elif year_level == '1':
                status_weights = [('Enrolled', 90), ('On Leave', 5), ('Suspended', 3), ('Graduated', 0), ('Dropout', 2)]
            
            statuses_list, weights = zip(*status_weights)
            status = random.choices(statuses_list, weights=weights)[0]
            
            student_data.append({
                'first_name': first_name,
                'last_name': last_name,
                'email': f"{first_name.lower()}.{last_name.lower().replace(' ', '')}@iskolarngbayan.pup.edu.ph",
                'birthday': birthday,
                'password': 'student123',
                'contact_number': f"09{random.randint(100000000, 999999999)}",
                'role': 'Student',
                'verified': 1,
                'student_number': f"2024-{i:04d}",
                'section': section_key,
                'status': status
            })
        
        # Add key students from the original data
        key_students = [
            {'first_name': 'Shadrack', 'last_name': 'Castro', 'email': 'shadrack.castro@iskolarngbayan.pup.edu.ph', 'birthday': '2002-05-10', 'password': 'student123', 'contact_number': '09456789012', 'role': 'Student', 'verified': 1, 'student_number': '2024-KEY001', 'section': list(section_ids.keys())[0] if section_ids else 'default', 'status': 'Enrolled'},
            {'first_name': 'Jerlee', 'last_name': 'Alipio', 'email': 'jerlee.alipio@iskolarngbayan.pup.edu.ph', 'birthday': '2001-09-18', 'password': 'student123', 'contact_number': '09567890123', 'role': 'Student', 'verified': 1, 'student_number': '2024-KEY002', 'section': list(section_ids.keys())[1] if len(section_ids) > 1 else list(section_ids.keys())[0] if section_ids else 'default', 'status': 'Enrolled'},
            {'first_name': 'Steven', 'last_name': 'Masangcay', 'email': 'steven.masangcay@iskolarngbayan.pup.edu.ph', 'birthday': '2000-12-25', 'password': 'student123', 'contact_number': '09678901234', 'role': 'Student', 'verified': 1, 'student_number': '2024-KEY003', 'section': list(section_ids.keys())[2] if len(section_ids) > 2 else list(section_ids.keys())[0] if section_ids else 'default', 'status': 'Enrolled'},
            {'first_name': 'John Mathew', 'last_name': 'Parocha', 'email': 'john.parocha@iskolarngbayan.pup.edu.ph', 'birthday': '1999-08-14', 'password': 'student123', 'contact_number': '09789012345', 'role': 'Student', 'verified': 1, 'student_number': '2024-KEY004', 'section': list(section_ids.keys())[3] if len(section_ids) > 3 else list(section_ids.keys())[0] if section_ids else 'default', 'status': 'Graduated'}
        ]
        
        all_students = student_data + key_students
        current_time = self.get_current_time()
        
        for student in all_students:
            # Check if exists
            existing = self.check_exists(conn, "users", {"email": student['email']})
            if existing:
                continue
            
            # Hash password
            hashed_pw = bcrypt.hashpw(student['password'].encode('utf-8'), bcrypt.gensalt())
            
            # Get status ID
            status_id = student_statuses.get(student['status'])
            
            # Insert user
            cursor = self.execute_query(conn, """
                INSERT INTO users (first_name, last_name, email, birthday, password_hash,
                                 contact_number, role, status_id, verified, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student['first_name'], student['last_name'], student['email'], student['birthday'],
                hashed_pw.decode('utf-8'), student['contact_number'], student['role'],
                status_id, student['verified'], 0, current_time, current_time
            ))
            
            user_id = cursor.lastrowid
            
            # Insert into students table
            section_id = section_ids.get(student['section'])
            
            self.execute_query(conn, """
                INSERT INTO students (user_id, student_number, section) VALUES (?, ?, ?)
            """, (user_id, student['student_number'], section_id))
