import streamlit as st
import hashlib
import sqlite3
from typing import Optional, Dict
import os

class AuthComponent:
    def __init__(self):
        self.db_path = "court_management.db"
        self.init_auth_table()
    
    def init_auth_table(self):
        """Initialize the users table if it doesn't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        full_name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1
                    )
                """)
                
                # Insert default admin user if table is empty
                cursor.execute("SELECT COUNT(*) FROM users")
                if cursor.fetchone()[0] == 0:
                    self.create_default_admin()
                
                conn.commit()
        except Exception as e:
            st.error(f"Database initialization error: {e}")
    
    def create_default_admin(self):
        """Create default admin user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                admin_password = "admin123"  # Default password
                password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, role, email)
                    VALUES (?, ?, ?, ?, ?)
                """, ("admin", password_hash, "System Administrator", "admin", "admin@jindcourt.gov.in"))
                
                conn.commit()
                st.success("Default admin user created: username='admin', password='admin123'")
        except Exception as e:
            st.error(f"Error creating default admin: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return self.hash_password(password) == password_hash
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if successful"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, full_name, role, email, is_active
                    FROM users 
                    WHERE username = ? AND is_active = 1
                """, (username,))
                
                user = cursor.fetchone()
                if user:
                    # Get password hash for verification
                    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
                    password_hash = cursor.fetchone()[0]
                    
                    if self.verify_password(password, password_hash):
                        # Update last login
                        cursor.execute("""
                            UPDATE users SET last_login = CURRENT_TIMESTAMP 
                            WHERE username = ?
                        """, (username,))
                        conn.commit()
                        
                        return {
                            'id': user[0],
                            'username': user[1],
                            'full_name': user[2],
                            'role': user[3],
                            'email': user[4],
                            'is_active': user[5]
                        }
        except Exception as e:
            st.error(f"Login error: {e}")
        
        return None
    
    def register_user(self, username: str, password: str, full_name: str, role: str, email: str = None) -> bool:
        """Register a new user (admin only)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                password_hash = self.hash_password(password)
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, full_name, role, email)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, password_hash, full_name, role, email))
                
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            st.error("Username already exists!")
            return False
        except Exception as e:
            st.error(f"Registration error: {e}")
            return False
    
    def get_all_users(self) -> list:
        """Get all users (admin only)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, full_name, role, email, created_at, last_login, is_active
                    FROM users ORDER BY created_at DESC
                """)
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Error fetching users: {e}")
            return []
    
    def render_login_form(self) -> Optional[Dict]:
        """Render login form and return user data if login successful"""
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="
                text-align: center;
                padding: 20px;
                background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
                border-radius: 15px;
                border: 1px solid #4a4a6a;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
                margin: 10px 0;
            ">
                <h1 style="
                    color: #ffffff;
                    font-size: 1.5rem;
                    font-weight: bold;
                    margin-bottom: 5px;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                ">⚖️ Court Management System</h1>
                <p style="
                    color: #a0a0a0;
                    font-size: 0.9rem;
                    margin-bottom: 0;
                ">District and Sessions Court, Jind</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_button = st.form_submit_button("🚪 Login", use_container_width=True)
                with col2:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.stop()
                
                if login_button:
                    if not username or not password:
                        st.error("Please enter both username and password!")
                        return None
                    
                    user = self.login(username, password)
                    if user:
                        st.success(f"Welcome, {user['full_name']}!")
                        return user
                    else:
                        st.error("Invalid username or password!")
                        return None
        
        return None
    
    def render_user_management(self, current_user: Dict):
        """Render user management interface (admin only)"""
        if current_user.get('role') != 'admin':
            st.error("Access denied. Admin privileges required.")
            return
        
        st.subheader("👥 User Management")
        
        # Add new user
        with st.expander("➕ Add New User"):
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("Username *")
                    new_password = st.text_input("Password *", type="password")
                    new_full_name = st.text_input("Full Name *")
                
                with col2:
                    new_role = st.selectbox("Role *", ["admin", "user", "viewer"])
                    new_email = st.text_input("Email")
                
                if st.form_submit_button("➕ Add User"):
                    if new_username and new_password and new_full_name:
                        if self.register_user(new_username, new_password, new_full_name, new_role, new_email):
                            st.success("User added successfully!")
                            st.rerun()
                    else:
                        st.error("Please fill all required fields!")
        
        # View all users
        st.subheader("📋 All Users")
        users = self.get_all_users()
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    'ID': user[0],
                    'Username': user[1],
                    'Full Name': user[2],
                    'Role': user[3],
                    'Email': user[4] or 'N/A',
                    'Created': user[5],
                    'Last Login': user[6] or 'Never',
                    'Status': 'Active' if user[7] else 'Inactive'
                })
            
            df = st.dataframe(user_data, use_container_width=True, hide_index=True)
        else:
            st.info("No users found.")
    
    def render_change_password(self, current_user: Dict):
        """Render change password form"""
        st.subheader("🔐 Change Password")
        
        # Check if current_user is valid
        if not current_user or 'username' not in current_user:
            st.error("User session is invalid. Please log in again.")
            return
        
        # Create form fields
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password", placeholder="Enter your current password")
            new_password = st.text_input("New Password", type="password", placeholder="Enter new password (min 6 characters)")
            confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
            
            submitted = st.form_submit_button("💾 Update Password")
        
        # Handle form submission outside the form
        if submitted:
            # Validate inputs
            if not current_password:
                st.error("Please enter your current password!")
                return
            if not new_password:
                st.error("Please enter a new password!")
                return
            if not confirm_password:
                st.error("Please confirm your new password!")
                return
            
            if new_password != confirm_password:
                st.error("New passwords don't match!")
                return
            
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters long!")
                return
            
            # Verify current password and update
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get current password hash
                    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (current_user['username'],))
                    result = cursor.fetchone()
                    
                    if not result:
                        st.error("User not found in database!")
                        return
                    
                    current_hash = result[0]
                    
                    # Verify current password
                    if not self.verify_password(current_password, current_hash):
                        st.error("Current password is incorrect!")
                        return
                    
                    # Update password
                    new_hash = self.hash_password(new_password)
                    cursor.execute("""
                        UPDATE users SET password_hash = ? WHERE username = ?
                    """, (new_hash, current_user['username']))
                    conn.commit()
                    
                    st.success("✅ Password updated successfully!")
                    st.info("Please log in again with your new password.")
                    
                    # Clear session and redirect to login
                    st.session_state['show_change_password'] = False
                    st.session_state['user'] = None
                    st.session_state['show_login'] = True
                    st.rerun()
                    
            except Exception as e:
                st.error(f"❌ Error updating password: {str(e)}")
                st.error("Please try again or contact administrator.")
    
    def logout(self):
        """Clear session state and logout user"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    def check_auth(self) -> Optional[Dict]:
        """Check if user is authenticated, return user data if yes"""
        return st.session_state.get('user')
    
    def require_auth(self) -> Optional[Dict]:
        """Require authentication, redirect to login if not authenticated"""
        user = self.check_auth()
        if not user:
            st.session_state['show_login'] = True
            return None
        return user
