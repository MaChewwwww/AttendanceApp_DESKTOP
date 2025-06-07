from .config import DB_PATH
import sqlite3

class DatabaseProgramManager:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def get_connection(self):
        """Create and return a new database connection."""
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def create_program(self, program_data):
        """
        Create a new program
        
        Args:
            program_data (dict): Dictionary containing program information
                - name (str): Program name
                - acronym (str): Program acronym
                - code (str): Program code
                - description (str): Program description (optional)
                - color (str): Hex color code (optional)
        
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if acronym already exists
            cursor.execute("""
                SELECT id FROM programs 
                WHERE acronym = ? AND isDeleted = 0
            """, (program_data['acronym'],))
            
            if cursor.fetchone():
                return False, "A program with this acronym already exists."
            
            # Check if code already exists
            cursor.execute("""
                SELECT id FROM programs 
                WHERE code = ? AND isDeleted = 0
            """, (program_data['code'],))
            
            if cursor.fetchone():
                return False, "A program with this code already exists."
            
            # Create new program
            cursor.execute("""
                INSERT INTO programs (name, acronym, code, description, color, isDeleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, datetime('now'), datetime('now'))
            """, (
                program_data['name'],
                program_data['acronym'],
                program_data['code'],
                program_data.get('description', ''),
                program_data.get('color', '#3B82F6')
            ))
            
            program_id = cursor.lastrowid
            conn.commit()
            
            # Return the created program data
            cursor.execute("""
                SELECT id, name, acronym, code, description, color, created_at, updated_at
                FROM programs WHERE id = ?
            """, (program_id,))
            
            program = cursor.fetchone()
            if program:
                program_dict = {
                    'id': program['id'],
                    'name': program['name'],
                    'acronym': program['acronym'],
                    'code': program['code'],
                    'description': program['description'],
                    'color': program['color'],
                    'created_at': program['created_at'],
                    'updated_at': program['updated_at']
                }
                return True, program_dict
            else:
                return False, "Failed to retrieve created program."
            
        except Exception as e:
            conn.rollback()
            print(f"Error creating program: {e}")
            return False, f"Failed to create program: {str(e)}"
        finally:
            conn.close()

    def update_program(self, program_id, program_data):
        """
        Update an existing program
        
        Args:
            program_id (int): Program ID
            program_data (dict): Dictionary containing updated program information
        
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if program exists
            cursor.execute("""
                SELECT id FROM programs 
                WHERE id = ? AND isDeleted = 0
            """, (program_id,))
            
            if not cursor.fetchone():
                return False, "Program not found."
            
            # Check for duplicate acronym (excluding current program)
            if 'acronym' in program_data:
                cursor.execute("""
                    SELECT id FROM programs 
                    WHERE acronym = ? AND id != ? AND isDeleted = 0
                """, (program_data['acronym'], program_id))
                
                if cursor.fetchone():
                    return False, "A program with this acronym already exists."
            
            # Check for duplicate code (excluding current program)
            if 'code' in program_data:
                cursor.execute("""
                    SELECT id FROM programs 
                    WHERE code = ? AND id != ? AND isDeleted = 0
                """, (program_data['code'], program_id))
                
                if cursor.fetchone():
                    return False, "A program with this code already exists."
            
            # Build update query dynamically
            update_fields = []
            update_values = []
            
            for key, value in program_data.items():
                if key in ['name', 'acronym', 'code', 'description', 'color']:
                    update_fields.append(f"{key} = ?")
                    update_values.append(value)
            
            if update_fields:
                update_fields.append("updated_at = datetime('now')")
                update_values.append(program_id)
                
                query = f"UPDATE programs SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
            
            conn.commit()
            
            # Return updated program data
            cursor.execute("""
                SELECT id, name, acronym, code, description, color, created_at, updated_at
                FROM programs WHERE id = ?
            """, (program_id,))
            
            program = cursor.fetchone()
            if program:
                program_dict = {
                    'id': program['id'],
                    'name': program['name'],
                    'acronym': program['acronym'],
                    'code': program['code'],
                    'description': program['description'],
                    'color': program['color'],
                    'created_at': program['created_at'],
                    'updated_at': program['updated_at']
                }
                return True, program_dict
            else:
                return False, "Failed to retrieve updated program."
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating program: {e}")
            return False, f"Failed to update program: {str(e)}"
        finally:
            conn.close()

    def delete_program(self, program_id):
        """
        Soft delete a program (set isDeleted = 1)
        
        Args:
            program_id (int): Program ID
        
        Returns:
            tuple: (success: bool, result: str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if program exists
            cursor.execute("""
                SELECT id FROM programs 
                WHERE id = ? AND isDeleted = 0
            """, (program_id,))
            
            if not cursor.fetchone():
                return False, "Program not found."
            
            # Soft delete by setting isDeleted flag
            cursor.execute("""
                UPDATE programs 
                SET isDeleted = 1, updated_at = datetime('now')
                WHERE id = ?
            """, (program_id,))
            
            conn.commit()
            return True, "Program deleted successfully."
            
        except Exception as e:
            conn.rollback()
            print(f"Error deleting program: {e}")
            return False, f"Failed to delete program: {str(e)}"
        finally:
            conn.close()

    def check_program_in_use(self, program_id):
        """
        Check if a program is being used by students or sections
        
        Args:
            program_id (int): Program ID
        
        Returns:
            tuple: (success: bool, result: dict/str)
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Check if any students are enrolled in this program
            cursor.execute("""
                SELECT COUNT(*) as student_count FROM users 
                WHERE program_id = ? AND isDeleted = 0 AND role = 'student'
            """, (program_id,))
            
            student_count = cursor.fetchone()['student_count']
            
            # Check if any sections belong to this program
            cursor.execute("""
                SELECT COUNT(*) as section_count FROM sections 
                WHERE program_id = ? AND isDeleted = 0
            """, (program_id,))
            
            section_count = cursor.fetchone()['section_count']
            
            usage_info = {
                'in_use': student_count > 0 or section_count > 0,
                'student_count': student_count,
                'section_count': section_count
            }
            
            return True, usage_info
            
        except Exception as e:
            print(f"Error checking program usage: {e}")
            return False, f"Failed to check program usage: {str(e)}"
        finally:
            conn.close()
