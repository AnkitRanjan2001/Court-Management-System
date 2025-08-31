import sqlite3
from typing import List, Dict, Tuple, Optional
from datetime import date, timedelta
import pandas as pd
import io

class DatabaseManager:
    def __init__(self, db_path: str = "court_management.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_divisions_with_parent(self) -> List[Dict]:
        """Get all divisions where parent_id is NOT NULL"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT division_id, division_name, parent_division_id
                FROM divisions 
                WHERE parent_division_id IS NOT NULL
                ORDER BY division_name
                """
                df = pd.read_sql_query(query, conn)
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching divisions: {e}")
            return []
    
    def get_courts_by_division(self, division_id: int) -> List[Dict]:
        """Get all courts under a specific division"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT court_id, court_name, court_number, officer_name, location
                FROM courts 
                WHERE parent_division_id = ?
                ORDER BY court_name
                """
                df = pd.read_sql_query(query, conn, params=(division_id,))
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching courts: {e}")
            return []
    
    def get_all_divisions(self) -> List[Dict]:
        """Get all divisions for reference"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT division_id, division_name, parent_division_id
                FROM divisions 
                ORDER BY division_name
                """
                df = pd.read_sql_query(query, conn)
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching all divisions: {e}")
            return []
    
    def get_all_courts(self) -> List[Dict]:
        """Get all courts across all divisions"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT c.court_id, c.court_name, c.court_number, c.location, c.officer_name,
                       d.division_name
                FROM courts c
                JOIN divisions d ON c.parent_division_id = d.division_id
                ORDER BY d.division_name, c.court_name
                """
                df = pd.read_sql_query(query, conn)
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching all courts: {e}")
            return []
    
    def get_court_details(self, court_id: int) -> Dict:
        """Get detailed information about a specific court"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT c.court_id, c.court_name, c.court_number, c.officer_name, c.location,
                       d.division_name, d.division_id
                FROM courts c
                JOIN divisions d ON c.parent_division_id = d.division_id
                WHERE c.court_id = ?
                """
                df = pd.read_sql_query(query, conn, params=(court_id,))
                return df.to_dict('records')[0] if not df.empty else {}
        except Exception as e:
            print(f"Error fetching court details: {e}")
            return {}
    
    def get_division_details(self, division_id: int) -> Dict:
        """Get detailed information about a specific division"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT division_id, division_name, parent_division_id
                FROM divisions 
                WHERE division_id = ?
                """
                df = pd.read_sql_query(query, conn, params=(division_id,))
                return df.to_dict('records')[0] if not df.empty else {}
        except Exception as e:
            print(f"Error fetching division details: {e}")
            return {}
    
    def get_employee_count_by_division(self, division_id: int) -> int:
        """Get total employee count for a division"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT COUNT(*) as count
                FROM employees e
                JOIN courts c ON e.court_id = c.court_id
                WHERE c.parent_division_id = ?
                """
                df = pd.read_sql_query(query, conn, params=(division_id,))
                return df['count'].iloc[0] if not df.empty else 0
        except Exception as e:
            print(f"Error fetching employee count by division: {e}")
            return 0
    
    def get_vacancy_count_by_division(self, division_id: int) -> int:
        """Get total vacancy count for a division"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT COALESCE(SUM(pc.sanctioned_vacancies - pc.active_employees_count), 0) as total_vacancies
                FROM post_courts pc
                JOIN courts c ON pc.court_id = c.court_id
                WHERE c.parent_division_id = ?
                """
                df = pd.read_sql_query(query, conn, params=(division_id,))
                return df['total_vacancies'].iloc[0] if not df.empty else 0
        except Exception as e:
            print(f"Error fetching vacancy count by division: {e}")
            return 0
    
    def get_vacancy_count_by_court(self, court_id: int) -> int:
        """Get total vacancy count for a court"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT COALESCE(SUM(sanctioned_vacancies - active_employees_count), 0) as total_vacancies
                FROM post_courts
                WHERE court_id = ?
                """
                df = pd.read_sql_query(query, conn, params=(court_id,))
                return df['total_vacancies'].iloc[0] if not df.empty else 0
        except Exception as e:
            print(f"Error fetching vacancy count by court: {e}")
            return 0
    
    def get_division_employees(self, division_id: int) -> List[Dict]:
        """Get all employees for a specific division with their details"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT e.employee_id, e.name, e.father_name, e.date_of_birth, 
                       e.qualifications, e.caste, e.gender, e.branch, e.date_of_joining,
                       e.address, e.acr, e.salary, e.retirement_date,
                       p.post_name, p.post_class, p.post_id, e.court_id
                FROM employees e
                JOIN posts p ON e.post_id = p.post_id
                JOIN courts c ON e.court_id = c.court_id
                WHERE c.parent_division_id = ?
                ORDER BY c.court_name, p.post_class, e.name
                """
                df = pd.read_sql_query(query, conn, params=(division_id,))
                
                # Convert retirement_date strings to date objects
                if 'retirement_date' in df.columns:
                    df['retirement_date'] = pd.to_datetime(df['retirement_date'], errors='coerce').dt.date
                    # Replace NaT with None for better handling
                    df['retirement_date'] = df['retirement_date'].replace({pd.NaT: None})
                
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching division employees: {e}")
            return []
    
    def get_all_employees(self) -> List[Dict]:
        """Get all employees across all divisions with their details"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT e.employee_id, e.name, e.father_name, e.date_of_birth, 
                       e.qualifications, e.caste, e.gender, e.branch, e.date_of_joining,
                       e.address, e.acr, e.salary, e.retirement_date,
                       p.post_name, p.post_class, p.post_id, e.court_id
                FROM employees e
                JOIN posts p ON e.post_id = p.post_id
                ORDER BY e.name
                """
                df = pd.read_sql_query(query, conn)
                
                # Convert retirement_date strings to date objects
                if 'retirement_date' in df.columns:
                    df['retirement_date'] = pd.to_datetime(df['retirement_date'], errors='coerce').dt.date
                    # Replace NaT with None for better handling
                    df['retirement_date'] = df['retirement_date'].replace({pd.NaT: None})
                
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching all employees: {e}")
            return []
    
    def get_system_vacancy_count(self) -> int:
        """Get total vacancy count across the entire system"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT COALESCE(SUM(sanctioned_vacancies - active_employees_count), 0) as total_vacancies
                FROM post_courts
                """
                df = pd.read_sql_query(query, conn)
                return df['total_vacancies'].iloc[0] if not df.empty else 0
        except Exception as e:
            print(f"Error fetching system vacancy count: {e}")
            return 0
    
    def get_employees_retiring_between(self, start_date: date, end_date: date) -> List[Dict]:
        """Get employees retiring between two dates"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT e.employee_id, e.name, e.father_name, e.date_of_birth, 
                       e.qualifications, e.caste, e.gender, e.branch, e.date_of_joining,
                       e.address, e.acr, e.salary, e.retirement_date,
                       p.post_name, p.post_class, p.post_id, e.court_id,
                       c.court_name, c.court_number, d.division_name
                FROM employees e
                JOIN posts p ON e.post_id = p.post_id
                JOIN courts c ON e.court_id = c.court_id
                JOIN divisions d ON c.parent_division_id = d.division_id
                WHERE e.retirement_date BETWEEN ? AND ?
                ORDER BY e.retirement_date, e.name
                """
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
                
                # Convert retirement_date strings to date objects
                if 'retirement_date' in df.columns:
                    df['retirement_date'] = pd.to_datetime(df['retirement_date'], errors='coerce').dt.date
                    # Replace NaT with None for better handling
                    df['retirement_date'] = df['retirement_date'].replace({pd.NaT: None})
                
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching retiring employees: {e}")
            return []
    
    def calculate_retirement_date(self, date_of_birth: date) -> date:
        """Calculate retirement date (last day of month when employee turns 58)"""
        try:
            # Add 58 years to date of birth
            retirement_year = date_of_birth.year + 58
            retirement_month = date_of_birth.month
            
            # Get the last day of the retirement month
            if retirement_month == 12:
                next_month = date(retirement_year + 1, 1, 1)
            else:
                next_month = date(retirement_year, retirement_month + 1, 1)
            
            last_day = next_month - timedelta(days=1)
            return last_day
        except Exception as e:
            print(f"Error calculating retirement date: {e}")
            return None
    
    def update_retirement_date(self, employee_id: int, date_of_birth: date) -> bool:
        """Update retirement date for an employee"""
        try:
            retirement_date = self.calculate_retirement_date(date_of_birth)
            if retirement_date:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE employees 
                        SET retirement_date = ?
                        WHERE employee_id = ?
                    """, (retirement_date, employee_id))
                    conn.commit()
                    return True
            return False
        except Exception as e:
            print(f"Error updating retirement date: {e}")
            return False
    
    def update_court_details(self, court_id: int, court_name: str, court_number: str, officer_name: str, location: str) -> bool:
        """Update court details"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE courts SET
                        court_name = ?, court_number = ?, officer_name = ?, location = ?
                    WHERE court_id = ?
                """, (court_name, court_number, officer_name, location, court_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating court details: {e}")
            return False
    
    def get_court_posts_with_vacancies(self, court_id: int) -> List[Dict]:
        """Get all posts with vacancy information for a specific court"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT p.post_id, p.post_name, p.post_class,
                       pc.sanctioned_vacancies, pc.active_employees_count,
                       (pc.sanctioned_vacancies - pc.active_employees_count) as available_vacancies
                FROM posts p
                LEFT JOIN post_courts pc ON p.post_id = pc.post_id AND pc.court_id = ?
                ORDER BY p.post_class, p.post_name
                """
                df = pd.read_sql_query(query, conn, params=(court_id,))
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching court posts: {e}")
            return []
    
    def get_court_employees(self, court_id: int) -> List[Dict]:
        """Get all employees for a specific court with their details"""
        try:
            with self.get_connection() as conn:
                query = """
                SELECT e.employee_id, e.name, e.father_name, e.date_of_birth, 
                       e.qualifications, e.caste, e.gender, e.branch, e.date_of_joining,
                       e.address, e.acr, e.salary, e.retirement_date,
                       p.post_name, p.post_class, p.post_id
                FROM employees e
                JOIN posts p ON e.post_id = p.post_id
                WHERE e.court_id = ?
                ORDER BY p.post_class, e.name
                """
                df = pd.read_sql_query(query, conn, params=(court_id,))
                
                # Convert retirement_date strings to date objects
                if 'retirement_date' in df.columns:
                    df['retirement_date'] = pd.to_datetime(df['retirement_date'], errors='coerce').dt.date
                    # Replace NaT with None for better handling
                    df['retirement_date'] = df['retirement_date'].replace({pd.NaT: None})
                
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching court employees: {e}")
            return []
    
    def update_post_vacancies(self, court_id: int, post_id: int, sanctioned_vacancies: int) -> bool:
        """Update sanctioned vacancies for a post in a court"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO post_courts (court_id, post_id, sanctioned_vacancies, active_employees_count)
                    VALUES (?, ?, ?, COALESCE((SELECT active_employees_count FROM post_courts WHERE court_id = ? AND post_id = ?), 0))
                """, (court_id, post_id, sanctioned_vacancies, court_id, post_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating post vacancies: {e}")
            return False
    
    def add_employee(self, employee_data: Dict) -> bool:
        """Add a new employee"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO employees (
                        name, father_name, date_of_birth, qualifications, caste, gender,
                        branch, post_id, date_of_joining, address, acr, salary, court_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    employee_data['name'], employee_data['father_name'], 
                    employee_data['date_of_birth'], employee_data['qualifications'],
                    employee_data['caste'], employee_data['gender'], employee_data['branch'],
                    employee_data['post_id'], employee_data['date_of_joining'],
                    employee_data['address'], employee_data['acr'], employee_data['salary'],
                    employee_data['court_id']
                ))
                
                # Get the inserted employee ID
                employee_id = cursor.lastrowid
                
                # Calculate and update retirement date
                if employee_data['date_of_birth']:
                    retirement_date = self.calculate_retirement_date(employee_data['date_of_birth'])
                    if retirement_date:
                        cursor.execute("""
                            UPDATE employees 
                            SET retirement_date = ?
                            WHERE employee_id = ?
                        """, (retirement_date, employee_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding employee: {e}")
            return False
    
    def update_employee(self, employee_id: int, employee_data: Dict) -> bool:
        """Update employee details"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE employees SET
                        name = ?, father_name = ?, date_of_birth = ?, qualifications = ?,
                        caste = ?, gender = ?, branch = ?, post_id = ?, date_of_joining = ?,
                        address = ?, acr = ?, salary = ?, retirement_date = ?
                    WHERE employee_id = ?
                """, (
                    employee_data['name'], employee_data['father_name'], 
                    employee_data['date_of_birth'], employee_data['qualifications'],
                    employee_data['caste'], employee_data['gender'], employee_data['branch'],
                    employee_data['post_id'], employee_data['date_of_joining'],
                    employee_data['address'], employee_data['acr'], employee_data['salary'],
                    employee_data.get('retirement_date'), employee_id
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating employee: {e}")
            return False
    
    def transfer_employee(self, employee_id: int, new_court_id: int, new_post_id: int) -> bool:
        """Transfer employee to a different court and post"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE employees SET court_id = ?, post_id = ?
                    WHERE employee_id = ?
                """, (new_court_id, new_post_id, employee_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error transferring employee: {e}")
            return False
    
    def terminate_employee(self, employee_id: int) -> bool:
        """Terminate employee (delete from database)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error terminating employee: {e}")
            return False
    
    def get_all_posts(self) -> List[Dict]:
        """Get all available posts"""
        try:
            with self.get_connection() as conn:
                query = "SELECT post_id, post_name, post_class FROM posts ORDER BY post_class, post_name"
                df = pd.read_sql_query(query, conn)
                return df.to_dict('records')
        except Exception as e:
            print(f"Error fetching posts: {e}")
            return []
    
    def get_employee_count_by_court(self, court_id: int) -> int:
        """Get employee count for a specific court"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM employees WHERE court_id = ?", (court_id,))
                count = cursor.fetchone()[0]
                return count
        except Exception as e:
            print(f"Error fetching employee count: {e}")
            return 0
    
    def add_court(self, court_name: str, court_number: str, officer_name: str, location: str, division_id: int) -> bool:
        """Add a new court"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO courts (court_name, court_number, officer_name, location, parent_division_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (court_name, court_number, officer_name, location, division_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding court: {e}")
            return False
    
    def add_post(self, post_name: str, post_class: str, description: str) -> bool:
        """Add a new post"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO posts (post_name, post_class, description)
                    VALUES (?, ?, ?)
                """, (post_name, post_class, description))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding post: {e}")
            return False
    
    def export_database_snapshot(self):
        """Export entire database as SQL dump"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get all table names
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # Create SQL dump
                dump = io.StringIO()
                
                # Add header
                dump.write("-- Database Snapshot Export\n")
                dump.write(f"-- Generated on: {date.today()}\n")
                dump.write("-- Jind Sessions Court Management System\n\n")
                
                # Export each table
                for table in tables:
                    table_name = table[0]
                    
                    # Get table schema
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = cursor.fetchall()
                    
                    # Write CREATE TABLE statement
                    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
                    create_statement = cursor.fetchone()[0]
                    dump.write(f"{create_statement};\n\n")
                    
                    # Get all data from table
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    if rows:
                        # Get column names
                        column_names = [col[1] for col in columns]
                        
                        # Write INSERT statements
                        for row in rows:
                            # Handle different data types
                            formatted_values = []
                            for value in row:
                                if value is None:
                                    formatted_values.append("NULL")
                                elif isinstance(value, str):
                                    # Escape single quotes
                                    escaped_value = value.replace("'", "''")
                                    formatted_values.append(f"'{escaped_value}'")
                                elif isinstance(value, date):
                                    formatted_values.append(f"'{value}'")
                                else:
                                    formatted_values.append(str(value))
                            
                            values_str = ", ".join(formatted_values)
                            dump.write(f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({values_str});\n")
                        
                        dump.write("\n")
                
                return dump.getvalue()
                
        except Exception as e:
            print(f"Error exporting database: {e}")
            return None
    
    def import_database_snapshot(self, sql_dump):
        """Import database from SQL dump"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Disable foreign key constraints temporarily
                cursor.execute("PRAGMA foreign_keys = OFF")
                
                # Clear existing data (drop and recreate tables)
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    if table_name != 'sqlite_sequence':  # Don't drop sqlite_sequence
                        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                
                # Split SQL dump into individual statements
                statements = []
                current_statement = ""
                
                for line in sql_dump.split('\n'):
                    line = line.strip()
                    if line.startswith('--') or not line:  # Skip comments and empty lines
                        continue
                    
                    current_statement += line + " "
                    
                    if line.endswith(';'):
                        statements.append(current_statement.strip())
                        current_statement = ""
                
                # Execute each statement
                for statement in statements:
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except Exception as stmt_error:
                            print(f"Error executing statement: {stmt_error}")
                            print(f"Statement: {statement[:100]}...")
                            continue
                
                # Re-enable foreign key constraints
                cursor.execute("PRAGMA foreign_keys = ON")
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error importing database: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager()
