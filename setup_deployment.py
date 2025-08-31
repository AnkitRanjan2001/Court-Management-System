#!/usr/bin/env python3
"""
Setup script for deployment - initializes database with default data
"""

import sqlite3
import os

def setup_deployment():
    """Setup database for deployment"""
    
    db_path = "court_management.db"
    
    # Check if database exists
    if os.path.exists(db_path):
        print("✅ Database already exists")
    else:
        print("🔄 Creating new database...")
        # Initialize database
        from init_database import init_database
        init_database()
    
    # Ensure admin user exists
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                print("❌ Users table not found. Database may not be properly initialized.")
                return False
            
            # Check if admin user exists
            cursor.execute("SELECT username FROM users WHERE username='admin'")
            if not cursor.fetchone():
                print("🔄 Creating admin user...")
                # Create admin user
                import hashlib
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, created_at, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, ("admin", password_hash, "admin"))
                conn.commit()
                print("✅ Admin user created")
            else:
                print("✅ Admin user already exists")
            
            # Check if we have basic data
            cursor.execute("SELECT COUNT(*) FROM divisions")
            div_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM posts")
            post_count = cursor.fetchone()[0]
            
            if div_count == 0 or post_count == 0:
                print("🔄 Adding default data...")
                
                # Add default division if none exists
                if div_count == 0:
                    cursor.execute("""
                        INSERT INTO divisions (division_name, created_at, updated_at)
                        VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, ("Jind Sessions Court",))
                    print("✅ Added default division")
                
                # Add default posts if none exist
                if post_count == 0:
                    default_posts = [
                        ("Judge", "Class I"),
                        ("Clerk", "Class II"),
                        ("Stenographer", "Class II"),
                        ("Peon", "Class IV"),
                        ("Driver", "Class IV"),
                        ("Security Guard", "Class IV")
                    ]
                    
                    for post_name, post_class in default_posts:
                        cursor.execute("""
                            INSERT INTO posts (post_name, post_class, created_at, updated_at)
                            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (post_name, post_class))
                    
                    print(f"✅ Added {len(default_posts)} default posts")
                
                conn.commit()
            else:
                print("✅ Default data already exists")
            
            print("✅ Deployment setup completed successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        return False

if __name__ == "__main__":
    setup_deployment()
