import sqlite3
import os
from datetime import date, datetime

def insert_dummy_data():
    """Insert dummy data into all tables for testing"""
    
    db_path = "court_management.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found. Please run init_database.py first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🚀 Inserting dummy data...")
        
        # 1. Insert divisions (with parent_id = 1 for Jind Sessions Court)
        print("📋 Inserting divisions...")
        divisions_data = [
            ("Civil Division", 1),
            ("Criminal Division", 1),
            ("Family Court Division", 1),
            ("Commercial Court Division", 1),
            ("Motor Accident Claims Division", 1)
        ]
        
        for div_name, parent_id in divisions_data:
            cursor.execute("""
                INSERT INTO divisions (division_name, parent_division_id)
                VALUES (?, ?)
            """, (div_name, parent_id))
        
        print(f"✅ Inserted {len(divisions_data)} divisions")
        
        # 2. Insert courts under each division
        print("⚖️ Inserting courts...")
        courts_data = [
            # Civil Division Courts
            ("Civil Court 1", "CC-001", "Judge Sharma", "Ground Floor, Block A", 2),
            ("Civil Court 2", "CC-002", "Judge Verma", "First Floor, Block A", 2),
            ("Small Causes Court", "SCC-001", "Judge Gupta", "Ground Floor, Block B", 2),
            
            # Criminal Division Courts
            ("Sessions Court 1", "SC-001", "Judge Singh", "Second Floor, Block A", 3),
            ("Sessions Court 2", "SC-002", "Judge Kumar", "Second Floor, Block A", 3),
            ("Fast Track Court", "FTC-001", "Judge Patel", "Third Floor, Block A", 3),
            
            # Family Court Division
            ("Family Court 1", "FC-001", "Judge Reddy", "First Floor, Block B", 4),
            ("Family Court 2", "FC-002", "Judge Iyer", "First Floor, Block B", 4),
            
            # Commercial Court Division
            ("Commercial Court 1", "COC-001", "Judge Malhotra", "Third Floor, Block B", 5),
            ("Commercial Court 2", "COC-002", "Judge Kapoor", "Third Floor, Block B", 5),
            
            # Motor Accident Claims Division
            ("MACT Court 1", "MACT-001", "Judge Joshi", "Ground Floor, Block C", 6),
            ("MACT Court 2", "MACT-002", "Judge Desai", "Ground Floor, Block C", 6)
        ]
        
        for court_name, court_number, officer_name, location, division_id in courts_data:
            cursor.execute("""
                INSERT INTO courts (court_name, court_number, officer_name, location, parent_division_id)
                VALUES (?, ?, ?, ?, ?)
            """, (court_name, court_number, officer_name, location, division_id))
        
        print(f"✅ Inserted {len(courts_data)} courts")
        
        # 3. Insert more posts
        print("👥 Inserting additional posts...")
        additional_posts = [
            ("Senior Judge", "Class I"),
            ("Additional Judge", "Class I"),
            ("Senior Clerk", "Class II"),
            ("Junior Clerk", "Class II"),
            ("Senior Stenographer", "Class II"),
            ("Junior Stenographer", "Class II"),
            ("Court Manager", "Class II"),
            ("Office Superintendent", "Class II"),
            ("Senior Peon", "Class IV"),
            ("Junior Peon", "Class IV"),
            ("Senior Driver", "Class IV"),
            ("Junior Driver", "Class IV"),
            ("Senior Security Guard", "Class IV"),
            ("Junior Security Guard", "Class IV")
        ]
        
        for post_name, post_class in additional_posts:
            cursor.execute("""
                INSERT INTO posts (post_name, post_class)
                VALUES (?, ?)
            """, (post_name, post_class))
        
        print(f"✅ Inserted {len(additional_posts)} additional posts")
        
        # 4. Insert employees
        print("👤 Inserting employees...")
        employees_data = [
            # Civil Division Employees
            ("Rajesh Kumar", "Mohan Lal", date(1985, 6, 15), "LLB, LLM", "General", "Male", "Civil", 2, date(2010, 7, 1), "123 Civil Colony, Jind", "Excellent", 45000, None, 1),
            ("Priya Sharma", "Rajesh Sharma", date(1990, 3, 22), "LLB", "General", "Female", "Civil", 3, date(2012, 4, 15), "456 Civil Colony, Jind", "Good", 38000, None, 1),
            ("Amit Verma", "Suresh Verma", date(1988, 11, 8), "LLB, MBA", "OBC", "Male", "Civil", 4, date(2011, 9, 1), "789 Civil Colony, Jind", "Very Good", 42000, None, 2),
            
            # Criminal Division Employees
            ("Deepak Singh", "Harbhajan Singh", date(1983, 4, 12), "LLB, LLM", "General", "Male", "Criminal", 5, date(2008, 6, 1), "321 Criminal Colony, Jind", "Outstanding", 52000, None, 4),
            ("Neha Gupta", "Ramesh Gupta", date(1992, 8, 25), "LLB", "General", "Female", "Criminal", 6, date(2013, 3, 1), "654 Criminal Colony, Jind", "Good", 35000, None, 4),
            ("Vikram Patel", "Rajesh Patel", date(1987, 12, 3), "LLB, LLM", "OBC", "Male", "Criminal", 7, date(2010, 8, 1), "987 Criminal Colony, Jind", "Very Good", 45000, None, 5),
            
            # Family Court Division Employees
            ("Sunita Reddy", "Krishna Reddy", date(1986, 7, 18), "LLB, LLM", "General", "Female", "Family", 8, date(2009, 5, 1), "147 Family Colony, Jind", "Excellent", 48000, None, 7),
            ("Rahul Iyer", "Suresh Iyer", date(1991, 1, 30), "LLB", "General", "Male", "Family", 9, date(2012, 7, 1), "258 Family Colony, Jind", "Good", 38000, None, 7),
            
            # Commercial Court Division Employees
            ("Arun Malhotra", "Rajesh Malhotra", date(1984, 9, 14), "LLB, LLM, MBA", "General", "Male", "Commercial", 10, date(2007, 4, 1), "369 Commercial Colony, Jind", "Outstanding", 55000, None, 9),
            ("Kavita Kapoor", "Amit Kapoor", date(1989, 5, 20), "LLB, LLM", "General", "Female", "Commercial", 11, date(2011, 2, 1), "741 Commercial Colony, Jind", "Very Good", 45000, None, 9),
            
            # MACT Division Employees
            ("Sanjay Joshi", "Mohan Joshi", date(1982, 2, 28), "LLB, LLM", "General", "Male", "MACT", 12, date(2006, 8, 1), "852 MACT Colony, Jind", "Outstanding", 58000, None, 11),
            ("Meera Desai", "Rajesh Desai", date(1988, 10, 10), "LLB, LLM", "General", "Female", "MACT", 13, date(2010, 1, 1), "963 MACT Colony, Jind", "Excellent", 48000, None, 11)
        ]
        
        for emp_data in employees_data:
            cursor.execute("""
                INSERT INTO employees (
                    name, father_name, date_of_birth, qualifications, caste, gender, 
                    branch, post_id, date_of_joining, address, acr, salary, 
                    retirement_date, court_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, emp_data)
        
        print(f"✅ Inserted {len(employees_data)} employees")
        
        # 5. Insert post_court allocations with sanctioned vacancies
        print("🔗 Inserting post-court allocations...")
        
        # Get all courts and posts for allocation
        cursor.execute("SELECT court_id FROM courts")
        court_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT post_id FROM posts")
        post_ids = [row[0] for row in cursor.fetchall()]
        
        # Create post-court combinations with vacancies
        post_court_data = []
        for court_id in court_ids:
            for post_id in post_ids:
                # Set different vacancy numbers based on post class
                if post_id in [1, 2, 3]:  # Judge posts
                    sanctioned_vacancies = 1
                elif post_id in [4, 5, 6, 7, 8]:  # Clerk and Stenographer posts
                    sanctioned_vacancies = 2
                else:  # Other posts
                    sanctioned_vacancies = 3
                
                post_court_data.append((court_id, post_id, sanctioned_vacancies, 0))
        
        for court_id, post_id, sanctioned_vacancies, active_count in post_court_data:
            cursor.execute("""
                INSERT INTO post_courts (court_id, post_id, sanctioned_vacancies, active_employees_count)
                VALUES (?, ?, ?, ?)
            """, (court_id, post_id, sanctioned_vacancies, active_count))
        
        print(f"✅ Inserted {len(post_court_data)} post-court allocations")
        
        # Commit all changes
        conn.commit()
        
        print("\n🎉 All dummy data inserted successfully!")
        
        # Show summary
        print("\n📊 Data Summary:")
        cursor.execute("SELECT COUNT(*) FROM divisions")
        print(f"   Divisions: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM courts")
        print(f"   Courts: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM posts")
        print(f"   Posts: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM employees")
        print(f"   Employees: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM post_courts")
        print(f"   Post-Court Allocations: {cursor.fetchone()[0]}")
        
    except sqlite3.Error as e:
        print(f"❌ Error inserting data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    insert_dummy_data()
