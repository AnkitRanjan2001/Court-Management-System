import sqlite3
import os

def init_database():
    """Initialize the court employee management database"""
    
    # Database file path
    db_path = "court_management.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Read the schema file
    with open('database_schema.sql', 'r') as file:
        schema_sql = file.read()
    
    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Execute the schema
        cursor.executescript(schema_sql)
        
        # Commit the changes
        conn.commit()
        
        print("✅ Database created successfully!")
        print(f"📁 Database file: {db_path}")
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n📋 Created tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Show some initial data
        print("\n🏛️  Default division:")
        cursor.execute("SELECT * FROM divisions;")
        divisions = cursor.fetchall()
        for div in divisions:
            print(f"   - {div[1]} (ID: {div[0]})")
        
        print("\n👥 Default posts:")
        cursor.execute("SELECT post_name, post_class FROM posts;")
        posts = cursor.fetchall()
        for post in posts:
            print(f"   - {post[0]} ({post[1]})")
        
        print("\n✅ Database initialization completed!")
        
    except sqlite3.Error as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
