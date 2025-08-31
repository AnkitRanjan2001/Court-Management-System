import streamlit as st
from sidebar_component import SidebarComponent
from court_management_component import CourtManagementComponent
from division_management_component import DivisionManagementComponent
from system_management_component import SystemManagementComponent
from database_operations import db_manager
from auth_component import AuthComponent

def main():
    # Page configuration
    st.set_page_config(
        page_title="Court Employee Management System",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'show_login' not in st.session_state:
        st.session_state['show_login'] = True
    if 'show_user_management' not in st.session_state:
        st.session_state['show_user_management'] = False
    if 'show_change_password' not in st.session_state:
        st.session_state['show_change_password'] = False
    
    # Initialize authentication
    auth = AuthComponent()
    
    # Check if user is logged in
    if st.session_state.get('show_login', False) or not auth.check_auth():
        # Show login form
        user = auth.render_login_form()
        if user:
            st.session_state['user'] = user
            st.session_state['show_login'] = False
            st.rerun()
        return
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    /* Remove red borders from input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: none !important;
        border-radius: 4px !important;
        background-color: #262730 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stDateInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        background-color: #262730 !important;
    }
    
    /* Remove red borders from Streamlit widgets */
    .stTextInput > div,
    .stSelectbox > div,
    .stDateInput > div,
    .stNumberInput > div,
    .stTextArea > div {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove borders from sidebar selectboxes specifically */
    .css-1d391kg .stSelectbox > div > div > div {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove all borders from form fields */
    .stForm .stTextInput > div > div > input,
    .stForm .stSelectbox > div > div > select,
    .stForm .stDateInput > div > div > input,
    .stForm .stNumberInput > div > div > input,
    .stForm .stTextArea > div > div > textarea {
        border: none !important;
        background-color: #262730 !important;
    }
    
    /* Remove focus borders from all elements */
    *:focus {
        outline: none !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove red borders from dropdown selection states */
    .stSelectbox > div > div > div[data-baseweb="select"] {
        border: none !important;
        box-shadow: none !important;
    }
    
    .stSelectbox > div > div > div[data-baseweb="select"]:focus {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Remove red borders from dropdown options */
    .stSelectbox > div > div > div[data-baseweb="select"] > div {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove red borders from dropdown when open */
    .stSelectbox > div > div > div[data-baseweb="select"][aria-expanded="true"] {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove red borders from all select elements */
    select:focus,
    select:active,
    select:hover {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Remove red borders from dropdown containers */
    .stSelectbox > div > div > div[data-baseweb="select"] > div[role="listbox"] {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove red borders from dropdown option items */
    .stSelectbox > div > div > div[data-baseweb="select"] > div[role="listbox"] > div {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove red borders from dropdown when selecting */
    .stSelectbox > div > div > div[data-baseweb="select"][aria-expanded="true"] > div {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Aggressive removal of all red borders from dropdowns */
    .stSelectbox * {
        border-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Remove red borders from all dropdown states */
    .stSelectbox > div,
    .stSelectbox > div > div,
    .stSelectbox > div > div > div,
    .stSelectbox > div > div > div > div,
    .stSelectbox > div > div > div > div > div {
        border: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Remove red borders from dropdown input */
    .stSelectbox input,
    .stSelectbox select {
        border: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Remove red borders from dropdown when focused */
    .stSelectbox:focus,
    .stSelectbox:focus-within,
    .stSelectbox:focus-visible {
        border: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Remove red borders from all form elements */
    .stForm *,
    .stForm *:focus,
    .stForm *:active,
    .stForm *:hover {
        border: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Remove red borders from sidebar specifically */
    .css-1d391kg *,
    .css-1d391kg *:focus,
    .css-1d391kg *:active,
    .css-1d391kg *:hover {
        border: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    
    /* Add white line to separate current selection from dropdown options */
    .stSelectbox > div > div > div[data-baseweb="select"] {
        border-bottom: 2px solid white !important;
        border-radius: 4px 4px 0 0 !important;
    }
    
    /* Style the dropdown options container */
    .stSelectbox > div > div > div[data-baseweb="select"] > div[role="listbox"] {
        border-top: 2px solid white !important;
        border-radius: 0 0 4px 4px !important;
        margin-top: -2px !important;
    }
    
    /* Add subtle white border to dropdown when open */
    .stSelectbox > div > div > div[data-baseweb="select"][aria-expanded="true"] {
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 4px !important;
    }
    
    /* Style individual dropdown options */
    .stSelectbox > div > div > div[data-baseweb="select"] > div[role="listbox"] > div {
        border-bottom: 2px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Remove bottom border from last option */
    .stSelectbox > div > div > div[data-baseweb="select"] > div[role="listbox"] > div:last-child {
        border-bottom: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize sidebar component
    sidebar = SidebarComponent()
    
    # Render sidebar and get selections
    selected_division_id, selected_court_id = sidebar.render(auth)
    
    # Handle user management and change password
    if st.session_state.get('show_user_management', False):
        auth.render_user_management(auth.check_auth())
        if st.button("← Back to Main"):
            st.session_state['show_user_management'] = False
            st.rerun()
        return
    
    if st.session_state.get('show_change_password', False):
        auth.render_change_password(auth.check_auth())
        if st.button("← Back to Main"):
            st.session_state['show_change_password'] = False
            st.rerun()
        return
    
    # Main content area
    if selected_court_id and selected_court_id != "all":
        # Single court view
        court_manager = CourtManagementComponent()
        
        # Get court details for header
        court_details = db_manager.get_court_details(selected_court_id)
        if court_details:
            # Dynamic header with court name and division
            header_text = f"⚖️ {court_details['court_name']} ({court_details['division_name']})"
            st.markdown(f'<h1 class="main-header">{header_text}</h1>', unsafe_allow_html=True)
        
        # Render court management sections
        court_manager.render_court_details(selected_court_id)
        st.markdown("---")
        
        # Employee Management (moved above post management)
        court_manager.render_employee_management()
        st.markdown("---")
        
        # Post Management
        court_manager.render_post_management()
        st.markdown("---")
        
        # Court Operations
        court_manager.render_court_operations()
        
    elif selected_division_id and selected_division_id != "all":
        # Division-wide view (specific division + all courts)
        division_manager = DivisionManagementComponent()
        division_manager.render_division_details(selected_division_id)
        
    elif selected_division_id == "all":
        # System-wide view (all divisions + all courts)
        system_manager = SystemManagementComponent()
        system_manager.render_system_overview()
        
    else:
        st.info("📋 Please select a division and court from the sidebar to begin.")
    


if __name__ == "__main__":
    main()
