import streamlit as st
from database_operations import db_manager
from typing import Optional, Tuple

class SidebarComponent:
    def __init__(self):
        self.selected_division = None
        self.selected_court = None
    
    def render(self, auth=None) -> Tuple[Optional[int], Optional[int]]:
        """Render the sidebar and return selected division_id and court_id"""
        
        with st.sidebar:

            # Main heading - styled text
            st.markdown("""
            <style>
            .main-heading {
                color: white !important;
                font-size: 1.8rem !important;
                font-weight: bold !important;
                text-align: center !important;
                width: 100% !important;
                padding: 15px 0 !important;
                margin-bottom: 15px !important;
                white-space: nowrap !important;
                overflow: hidden !important;
                text-overflow: ellipsis !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display main heading as styled text
            st.markdown('<div class="main-heading">⚖️ District and Sessions Court, Jind</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Overview button
            if st.button("📊 Overview (All Divisions and All Courts)", key="home_button", help="Go to system overview", use_container_width=False):
                # Set session state to home page (All Divisions - All Courts)
                st.session_state.division_select = "All Divisions"
                st.session_state.court_select = "All Courts"
                st.rerun()
            
            # Divisions dropdown (only divisions with parent_id != NULL)
            st.subheader("🏛️ Select Division")
            divisions = db_manager.get_divisions_with_parent()
            
            if not divisions:
                st.warning("No divisions found. Please add divisions first.")
                # Don't return here - continue to show user management
            
            if divisions:
                # Create division options for dropdown with "All divisions" option
                division_options = {"All Divisions": "all"}  # Add "All Divisions" option
                division_options.update({div['division_name']: div['division_id'] for div in divisions})
                
                selected_division_name = st.selectbox(
                    "Choose Division:",
                    options=list(division_options.keys()),
                    key="division_select"
                )
                
                selected_division_id = division_options.get(selected_division_name)
                
                # Courts dropdown (based on selected division)
                st.subheader("⚖️ Select Court")
                
                if selected_division_id == "all":
                    # Show all courts when "All Divisions" is selected
                    courts = db_manager.get_all_courts()
                    court_options = {"All Courts": "all"}  # Add "All Courts" option
                    
                    if courts:
                        # Add individual courts
                        for court in courts:
                            if court['court_number']:
                                court_options[f"{court['court_name']} ({court['court_number']})"] = court['court_id']
                            else:
                                court_options[court['court_name']] = court['court_id']
                        
                        selected_court_name = st.selectbox(
                            "Choose Court:",
                            options=list(court_options.keys()),
                            key="court_select"
                        )
                        selected_court_id = court_options.get(selected_court_name)
                    else:
                        st.info("No courts found. Please add courts first.")
                        selected_division_id = None
                        selected_court_id = None
                        
                else:
                    # Show courts for specific division
                    courts = db_manager.get_courts_by_division(selected_division_id)
                    court_options = {"All Courts": "all"}  # Add "All Courts" option
                    
                    if not courts:
                        st.info(f"No courts found for {selected_division_name}. Please add courts first.")
                        selected_court_id = None
                    else:
                        # Add individual courts for the selected division
                        for court in courts:
                            if court['court_number']:
                                court_options[f"{court['court_name']} ({court['court_number']})"] = court['court_id']
                            else:
                                court_options[court['court_name']] = court['court_id']
                        
                        selected_court_name = st.selectbox(
                            "Choose Court:",
                            options=list(court_options.keys()),
                            key="court_select"
                        )
                        selected_court_id = court_options.get(selected_court_name)
            else:
                selected_division_id = None
                selected_court_id = None
            
            # User info and logout (moved to bottom)
            if auth and auth.check_auth():
                st.markdown("---")
                user = auth.check_auth()
                st.markdown(f"**👤 {user['full_name']}**")
                st.markdown(f"*Role: {user['role'].title()}*")
                
                # User management for admins
                if user['role'] == 'admin':
                    if st.button("👥 User Management", use_container_width=True):
                        st.session_state['show_user_management'] = True
                
                # Change password
                if st.button("🔐 Change Password", use_container_width=True):
                    st.session_state['show_change_password'] = True
                
                # Logout button
                if st.button("🚪 Logout", use_container_width=True):
                    auth.logout()
            
            # Display selected information (removed green confirmation text)
            
            return selected_division_id, selected_court_id
    
    def get_selected_info(self) -> Tuple[str, str]:
        """Get the display names of selected division and court"""
        divisions = db_manager.get_divisions_with_parent()
        division_dict = {div['division_id']: div['division_name'] for div in divisions}
        
        # Get current selection from session state
        selected_division_id = st.session_state.get('division_select')
        selected_court_id = st.session_state.get('court_select')
        
        division_name = division_dict.get(selected_division_id, "Not Selected")
        court_name = "Not Selected"  # Will be updated when court selection is implemented
        
        return division_name, court_name
