import streamlit as st
import pandas as pd
from datetime import date, datetime
from database_operations import db_manager
from typing import Dict, List, Optional

class CourtManagementComponent:
    def __init__(self):
        self.court_id = None
        self.court_details = {}
        self.employees = []
        self.posts = []
    
    def render_court_details(self, court_id: int):
        """Render court information section"""
        self.court_id = court_id
        self.court_details = db_manager.get_court_details(court_id)
        
        if not self.court_details:
            st.error("Court details not found!")
            return
        
        # Check if editing mode is active
        is_editing_court = st.session_state.get('editing_court_details', False)
        
        if is_editing_court:
            # Inline editing form
            with st.form("edit_court_details_form"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    new_court_name = st.text_input("Court Name:", value=self.court_details['court_name'], key="edit_court_name")
                
                with col2:
                    new_court_number = st.text_input("Court Number:", value=self.court_details['court_number'], key="edit_court_number")
                
                with col3:
                    new_officer_name = st.text_input("Officer Name:", value=self.court_details['officer_name'] or '', key="edit_officer_name")
                
                with col4:
                    new_location = st.text_input("Location:", value=self.court_details['location'] or '', key="edit_location")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Changes"):
                        # Update court details in database
                        if db_manager.update_court_details(
                            self.court_id, 
                            new_court_name, 
                            new_court_number, 
                            new_officer_name, 
                            new_location
                        ):
                            st.success("✅ Court details updated successfully!")
                            # Refresh court details
                            self.court_details = db_manager.get_court_details(self.court_id)
                            # Clear editing mode
                            del st.session_state['editing_court_details']
                            st.rerun()
                        else:
                            st.error("❌ Failed to update court details.")
                
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        del st.session_state['editing_court_details']
                        st.rerun()
        else:
            # Display mode - will be handled in the merged layout below
            pass
        
        # Get posts for calculations
        self.posts = db_manager.get_court_posts_with_vacancies(self.court_id)
        
        if self.posts:
            # Calculate totals from database queries
            total_employees = db_manager.get_employee_count_by_court(self.court_id)
            total_vacancies = sum(post['available_vacancies'] for post in self.posts)
            
            # Display court details and totals in a merged layout
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                # Left side - Editable court information
                st.markdown(f"""
                <div style="color: white; margin-bottom: 0.5rem; font-size: 1.1rem;">
                    <strong>Court Number:</strong> {self.court_details['court_number']}
                </div>
                <div style="color: white; margin-bottom: 0.5rem; font-size: 1.1rem;">
                    <strong>Officer Name:</strong> {self.court_details['officer_name'] or 'Not Assigned'}
                </div>
                <div style="color: white; margin-bottom: 0.5rem; font-size: 1.1rem;">
                    <strong>Location:</strong> {self.court_details['location'] or 'Not Specified'}
                </div>
                """, unsafe_allow_html=True)
                
                # Edit button for court details - smaller and simpler
                if st.button("✏️ Edit", key="edit_court_details_btn", use_container_width=False):
                    st.session_state['editing_court_details'] = True
                    st.rerun()
            
            with col2:
                # Right side - Non-editable totals
                st.markdown(f"""
                <div style="
                    font-size: 1.2rem;
                    color: white;
                    text-align: center;
                    margin-bottom: 1rem;
                ">
                    👥 Total Employees: {total_employees}
                </div>
                <div style="
                    font-size: 1.2rem;
                    color: white;
                    text-align: center;
                    margin-bottom: 1rem;
                ">
                    📋 Total Vacancies: {total_vacancies}
                </div>
                """, unsafe_allow_html=True)
    
    def render_post_management(self):
        """Render post management section"""
        st.subheader("👨‍💼 Post Management")
        
        # Get posts with vacancy information (if not already loaded)
        if not hasattr(self, 'posts') or not self.posts:
            self.posts = db_manager.get_court_posts_with_vacancies(self.court_id)
        
        if not self.posts:
            st.warning("No posts found for this court.")
            return
        
        # Show edit dialog if edit posts button was clicked
        if st.session_state.get('show_edit_posts', False):
            self._render_edit_post_dialog()
        
        # Create table with edit buttons
        table_data = []
        for post in self.posts:
            post_id = post['post_id']
            is_editing = st.session_state.get('edit_post_id') == post_id
            
            # Create row data
            row_data = {
                'Post Name': post['post_name'],
                'Post Class': post['post_class'],
                'Sanctioned Vacancies': post['sanctioned_vacancies'],
                'Current Employees': post['active_employees_count'],
                'Available Vacancies': post['available_vacancies'],
                'Actions': f"edit_{post_id}"  # Placeholder for edit button
            }
            table_data.append(row_data)
        
        # Create DataFrame for display
        df_posts_table = pd.DataFrame(table_data)
        
        # Display table
        st.dataframe(df_posts_table[['Post Name', 'Post Class', 'Sanctioned Vacancies', 'Current Employees', 'Available Vacancies']], 
                    width='stretch', use_container_width=True, hide_index=True)
        
        # Single edit button that directly opens edit dialog
        if st.button("✏️ Edit Posts", key="edit_posts_button"):
            st.session_state.show_edit_posts = True
            st.rerun()
    
    def _render_edit_post_dialog(self):
        """Render edit post dialog for sanctioned vacancies"""
        st.markdown("---")
        st.markdown("### ✏️ Edit Sanctioned Vacancies")
        
        # Post selection dropdown
        post_options = {f"{post['post_name']} ({post['post_class']})": post['post_id'] for post in self.posts}
        selected_post_name = st.selectbox("Select Post to Edit:", options=list(post_options.keys()), key="post_selection_dialog")
        selected_post_id = post_options[selected_post_name]
        
        # Get selected post details
        post = next((p for p in self.posts if p['post_id'] == selected_post_id), None)
        
        if post:
            with st.form(f"edit_post_form_{selected_post_id}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Post Name:** {post['post_name']}")
                    st.write(f"**Post Class:** {post['post_class']}")
                    st.write(f"**Current Employees:** {post['active_employees_count']}")
                    st.write(f"**Available Vacancies:** {post['available_vacancies']}")
                
                with col2:
                    st.write(f"**Current Sanctioned Vacancies:** {post['sanctioned_vacancies']}")
                    
                    # Only allow editing sanctioned vacancies
                    # Ensure minimum value is at least current employees, but allow current value if it's lower
                    min_vacancies = max(post['active_employees_count'], post['sanctioned_vacancies'])
                    new_sanctioned_vacancies = st.number_input(
                        "New Sanctioned Vacancies:",
                        min_value=min_vacancies,  # Can't be less than current employees or current value
                        value=post['sanctioned_vacancies'],
                        step=1,
                        key=f"sanctioned_vacancies_{selected_post_id}"
                    )
                    
                    st.info("💡 **Note:** Available vacancies will automatically update based on sanctioned vacancies minus current employees.")
                
                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Save Changes")
                
                with col2:
                    cancel = st.form_submit_button("❌ Cancel")
                
                if submitted:
                    if new_sanctioned_vacancies != post['sanctioned_vacancies']:
                        if db_manager.update_post_vacancies(self.court_id, selected_post_id, new_sanctioned_vacancies):
                            st.success("✅ Sanctioned vacancies updated successfully!")
                            # Clear session state
                            del st.session_state['show_edit_posts']
                            st.rerun()
                        else:
                            st.error("❌ Failed to update sanctioned vacancies.")
                    else:
                        st.info("No changes to save.")
                
                if cancel:
                    # Clear session state
                    del st.session_state['show_edit_posts']
                    st.rerun()
    
    def render_employee_management(self):
        """Render employee management section"""
        # Get employees for this court
        self.employees = db_manager.get_court_employees(self.court_id)
        
        # Show employee management header
        st.subheader("👥 Employee Management")
        
        # Employee management tabs
        tab_names = ["👥 Current Employees", "➕ Add Employee"]
        
        # Create tabs
        tab1, tab2 = st.tabs(tab_names)
        
        with tab1:
            self._render_current_employees()
        
        with tab2:
            # Display success message if employee was added
            if st.session_state.get('employee_added', False):
                st.success("Employee added successfully")
                st.session_state.employee_added = False
            
            self._render_add_employee()
    
    def _render_current_employees(self):
        """Render current employees list"""
        if not self.employees:
            st.info("No employees found for this court.")
            return
        
        # Create DataFrame for display
        df_employees = pd.DataFrame(self.employees)
        
        # Hybrid Search and Filter System
        
        # Check if clear button was pressed in previous run
        if st.session_state.get("clear_filters_clicked", False):
            # Reset all filters to "All" and clear search
            st.session_state["post_filter"] = "All"
            st.session_state["gender_filter"] = "All"
            st.session_state["caste_filter"] = "All"
            # Clear search input by setting it to empty string
            st.session_state["employee_search_main"] = ""
            # Reset the flag
            st.session_state["clear_filters_clicked"] = False
        
        # Primary search box
        search_term = st.text_input("Search", key="employee_search_main", 
                                   placeholder="Search by name, post, qualification, address, etc.",
                                   label_visibility="collapsed")
        
        # Quick filters row
        col1, col2, col3, col4 = st.columns([1, 1, 1, 0.5])
        with col1:
            post_filter = st.selectbox("👨‍💼 Post", 
                                     options=["All"] + list(df_employees['post_name'].unique()),
                                     key="post_filter")
        with col2:
            gender_filter = st.selectbox("👤 Gender", 
                                       options=["All"] + list(df_employees['gender'].unique()),
                                       key="gender_filter")
        with col3:
            caste_filter = st.selectbox("🏷️ Caste", 
                                      options=["All"] + list(df_employees['caste'].unique()),
                                      key="caste_filter")
        with col4:
            st.write("")  # Empty space for alignment
            if st.button("🗑️ Clear", key="clear_filters"):
                # Set flag to clear filters in next run
                st.session_state["clear_filters_clicked"] = True
                st.rerun()
        
        # Apply all filters
        filtered_df = df_employees.copy()
        
        # Primary search filter
        if search_term:
            search_mask = (
                filtered_df['name'].str.contains(search_term, case=False, na=False) |
                filtered_df['post_name'].str.contains(search_term, case=False, na=False) |
                filtered_df['post_class'].str.contains(search_term, case=False, na=False) |
                filtered_df['father_name'].str.contains(search_term, case=False, na=False) |
                filtered_df['qualifications'].str.contains(search_term, case=False, na=False) |
                filtered_df['caste'].str.contains(search_term, case=False, na=False) |
                filtered_df['gender'].str.contains(search_term, case=False, na=False) |
                filtered_df['branch'].str.contains(search_term, case=False, na=False) |
                filtered_df['address'].str.contains(search_term, case=False, na=False) |
                filtered_df['acr'].str.contains(search_term, case=False, na=False) |
                filtered_df['salary'].astype(str).str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[search_mask]
        
        # Quick filters
        if post_filter != "All":
            filtered_df = filtered_df[filtered_df['post_name'] == post_filter]
        
        if gender_filter != "All":
            filtered_df = filtered_df[filtered_df['gender'] == gender_filter]
        
        if caste_filter != "All":
            filtered_df = filtered_df[filtered_df['caste'] == caste_filter]
        

        
        # Show results count
        total_employees = len(df_employees)
        filtered_count = len(filtered_df)
        
        if total_employees != filtered_count:
            st.info(f"📊 Showing {filtered_count} of {total_employees} employees")
        
        # Use filtered dataframe
        df_employees = filtered_df
        
        # Display employees with inline editing and transfer
        for idx, employee in df_employees.iterrows():
            employee_id = employee['employee_id']
            is_editing = st.session_state.get('edit_employee_id') == employee_id
            is_transferring = st.session_state.get('transfer_employee_id') == employee_id
            
            if is_editing:
                # Inline edit mode
                st.markdown(f"### ✏️ Employee ID {employee['employee_id']}")
                
                with st.form(f"inline_edit_form_{employee_id}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Full Name *", value=employee['name'], key=f"name_{employee_id}")
                        date_of_birth = st.date_input("Date of Birth", value=employee['date_of_birth'], key=f"dob_{employee_id}")
                        caste = st.selectbox("Caste", ["General", "OBC", "SC", "ST", "Other"], 
                                           index=["General", "OBC", "SC", "ST", "Other"].index(employee['caste']), key=f"caste_{employee_id}")
                        branch = st.text_input("Court", value=employee['branch'], key=f"branch_{employee_id}")
                        date_of_joining = st.date_input("Date of Joining", value=employee['date_of_joining'], key=f"join_{employee_id}")
                        
                        # Retirement date input (editable)
                        retirement_date = employee.get('retirement_date')
                        # Handle retirement date display - it might be a string from database or NaT
                        if retirement_date and retirement_date != pd.NaT:
                            if isinstance(retirement_date, str):
                                retirement_display = retirement_date
                            else:
                                try:
                                    retirement_display = retirement_date.strftime('%Y-%m-%d')
                                except (ValueError, AttributeError):
                                    retirement_display = 'Invalid date'
                        else:
                            retirement_display = 'Not calculated'
                        
                        # Make retirement date editable
                        retirement_input = st.date_input("Retirement Date", value=retirement_display if retirement_display != 'Not calculated' and retirement_display != 'Invalid date' else None, key=f"retirement_{employee_id}")
                        
                        address = st.text_area("Address", value=employee['address'], key=f"addr_{employee_id}")
                    
                    with col2:
                        father_name = st.text_input("Father's Name", value=employee['father_name'], key=f"father_{employee_id}")
                        gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                            index=["Male", "Female", "Other"].index(employee['gender']), key=f"gender_{employee_id}")
                        
                        # Post selection
                        posts = db_manager.get_all_posts()
                        post_options = {f"{p['post_name']} ({p['post_class']})": p['post_id'] for p in posts}
                        current_post = f"{employee['post_name']} ({employee['post_class']})"
                        selected_post = st.selectbox("Post *", options=list(post_options.keys()), 
                                                   index=list(post_options.keys()).index(current_post), key=f"post_{employee_id}")
                        post_id = post_options[selected_post]
                        
                        # Division field (auto-filled and non-editable)
                        division_name = self.court_details.get('division_name', '')
                        st.text_input("Division", value=division_name, key=f"division_{employee_id}", disabled=True)
                        
                        qualifications = st.text_area("Qualifications", value=employee['qualifications'], key=f"qual_{employee_id}")
                        acr = st.selectbox("ACR Rating", ["Outstanding", "Excellent", "Very Good", "Good", "Average", "Poor"],
                                         index=["Outstanding", "Excellent", "Very Good", "Good", "Average", "Poor"].index(employee['acr']), key=f"acr_{employee_id}")
                        salary = st.number_input("Salary (₹)", min_value=0, value=int(employee['salary']), step=1000, key=f"salary_{employee_id}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("💾 Save Changes")
                    
                    with col2:
                        cancel = st.form_submit_button("❌ Cancel")
                    
                    if submitted:
                        if not name or not post_id:
                            st.error("Name and Post are required fields!")
                        else:
                            employee_data = {
                                'name': name,
                                'father_name': father_name,
                                'date_of_birth': date_of_birth,
                                'qualifications': qualifications,
                                'caste': caste,
                                'gender': gender,
                                'branch': branch,
                                'post_id': post_id,
                                'date_of_joining': date_of_joining,
                                'address': address,
                                'acr': acr,
                                'salary': salary,
                                'retirement_date': retirement_input
                            }
                            
                            if db_manager.update_employee(employee_id, employee_data):
                                st.success("✅ Employee updated successfully!")
                                # Clear session state
                                del st.session_state['edit_employee_id']
                                st.rerun()
                            else:
                                st.error("❌ Failed to update employee.")
                    
                    if cancel:
                        # Clear session state
                        del st.session_state['edit_employee_id']
                        st.rerun()
                
                # Compute retirement date button (outside form)
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🔄 Auto-Calculate Retirement", key=f"compute_retirement_{employee_id}", help="Calculate retirement date based on date of birth"):
                        # Get the current date of birth from the form
                        current_dob = st.session_state.get(f"dob_{employee_id}", employee.get('date_of_birth'))
                        if current_dob:
                            new_retirement_date = db_manager.calculate_retirement_date(current_dob)
                            if new_retirement_date:
                                # Update the retirement date in session state to reflect in the form
                                st.session_state[f"retirement_{employee_id}"] = new_retirement_date
                                st.success("✅ Retirement date auto-calculated! Click 'Save Changes' to update.")
                                st.rerun()
                            else:
                                st.error("❌ Could not calculate retirement date")
                        else:
                            st.error("❌ Please set date of birth first")
                
                st.markdown("---")
            elif is_transferring:
                # Inline transfer mode
                st.markdown(f"### 🔄 Transferring: {employee['name']}")
                
                st.info(f"""
                **Current Position:** {employee['post_name']} ({employee['post_class']})  
                **Current Court:** {self.court_details['court_name']}
                """)
                
                with st.form(f"inline_transfer_form_{employee_id}"):
                    # Target court selection
                    all_courts = db_manager.get_all_courts()
                    court_options = {f"{court['court_name']} ({court['division_name']})": court['court_id'] for court in all_courts}
                    target_court = st.selectbox("Target Court:", options=list(court_options.keys()), key=f"court_{employee_id}")
                    target_court_id = court_options[target_court]
                    
                    # Target post selection
                    posts = db_manager.get_all_posts()
                    post_options = {f"{p['post_name']} ({p['post_class']})": p['post_id'] for p in posts}
                    target_post = st.selectbox("Target Post:", options=list(post_options.keys()), key=f"post_transfer_{employee_id}")
                    target_post_id = post_options[target_post]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        submitted = st.form_submit_button("🔄 Transfer Employee")
                    
                    with col2:
                        cancel = st.form_submit_button("❌ Cancel")
                    
                    if submitted:
                        if db_manager.transfer_employee(employee_id, target_court_id, target_post_id):
                            st.success("✅ Employee transferred successfully!")
                            # Clear session state
                            del st.session_state['transfer_employee_id']
                            st.rerun()
                        else:
                            st.error("❌ Failed to transfer employee.")
                    
                    if cancel:
                        # Clear session state
                        del st.session_state['transfer_employee_id']
                        st.rerun()
                
                st.markdown("---")
            else:
                # Normal display mode
                with st.expander(f"👤 {employee['name']} - {employee['post_name']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Employee ID:** {employee['employee_id']}")
                        st.write(f"**Father's Name:** {employee['father_name']}")
                        st.write(f"**Date of Birth:** {employee['date_of_birth']}")
                        st.write(f"**Gender:** {employee['gender']}")
                        st.write(f"**Caste:** {employee['caste']}")
                        st.write(f"**Qualifications:** {employee['qualifications']}")
                    
                    with col2:
                        st.write(f"**Date of Joining:** {employee['date_of_joining']}")
                        st.write(f"**Salary:** ₹{employee['salary']:,.2f}")
                        # Handle retirement date display - it might be a string from database or NaT
                        retirement_date = employee.get('retirement_date')
                        if retirement_date and retirement_date != pd.NaT:
                            if isinstance(retirement_date, str):
                                retirement_display = retirement_date
                            else:
                                try:
                                    retirement_display = retirement_date.strftime('%Y-%m-%d')
                                except (ValueError, AttributeError):
                                    retirement_display = 'Invalid date'
                        else:
                            retirement_display = 'Not calculated'
                        st.write(f"**Retirement Date:** {retirement_display}")
                        st.write(f"**ACR:** {employee['acr']}")
                        st.write(f"**Address:** {employee['address']}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{employee_id}"):
                            st.session_state.edit_employee_id = employee_id
                            st.rerun()
                    
                    with col2:
                        if st.button("🔄 Transfer", key=f"transfer_{employee_id}"):
                            st.session_state.transfer_employee_id = employee_id
                            st.rerun()
                    
                    with col3:
                        # Use session state to track termination confirmation
                        terminate_key = f"terminate_{employee_id}"
                        confirm_key = f"confirm_terminate_{employee_id}"
                        
                        if st.button("❌ Terminate", key=terminate_key):
                            st.session_state[confirm_key] = True
                            st.rerun()
                        
                        if st.session_state.get(confirm_key, False):
                            # Simple checkbox and submit button
                            confirm_terminate = st.checkbox(
                                "Confirm termination", 
                                key=f"confirm_checkbox_{employee_id}"
                            )
                            
                            # Custom CSS to make only the submit button green when checked
                            if confirm_terminate:
                                st.markdown("""
                                <style>
                                div[data-testid="stButton"] button[kind="primary"] {
                                    background-color: #28a745 !important;
                                    color: white !important;
                                    border-color: #28a745 !important;
                                }
                                </style>
                                """, unsafe_allow_html=True)
                            
                            if st.button(
                                "🗑️ Submit", 
                                key=f"confirm_{employee_id}", 
                                type="primary",
                                disabled=not confirm_terminate
                            ):
                                if db_manager.terminate_employee(employee_id):
                                    st.success("✅ Employee terminated successfully!")
                                    # Clear session state
                                    del st.session_state[confirm_key]
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to terminate employee.")
        

    

    
    def _render_transfer_dialog(self):
        """Render transfer employee dialog"""
        transfer_employee_id = st.session_state.get('transfer_employee_id')
        
        # Get employee details
        employee = next((emp for emp in self.employees if emp['employee_id'] == transfer_employee_id), None)
        
        if employee:
            st.markdown("### 🔄 **Transfer Employee**")
            st.markdown("---")
            
            st.info(f"""
            **Transferring:** {employee['name']}  
            **Current Position:** {employee['post_name']} ({employee['post_class']})  
            **Current Court:** {self.court_details['court_name']}
            """)
            
            with st.form("transfer_employee_form"):
                    # Target court selection
                    all_courts = db_manager.get_all_courts()
                    court_options = {f"{court['court_name']} ({court['division_name']})": court['court_id'] for court in all_courts}
                    target_court = st.selectbox("Target Court:", options=list(court_options.keys()))
                    target_court_id = court_options[target_court]
                    
                    # Target post selection
                    posts = db_manager.get_all_posts()
                    post_options = {f"{p['post_name']} ({p['post_class']})": p['post_id'] for p in posts}
                    target_post = st.selectbox("Target Post:", options=list(post_options.keys()))
                    target_post_id = post_options[target_post]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        submitted = st.form_submit_button("🔄 Transfer Employee")
                    
                    with col2:
                        cancel = st.form_submit_button("❌ Cancel")
                    
                    with col3:
                        if st.form_submit_button("🔄 Transfer & Edit Another"):
                            submitted = True
                            st.session_state.transfer_and_continue = True
                    
                    if submitted:
                        if db_manager.transfer_employee(transfer_employee_id, target_court_id, target_post_id):
                            st.success("✅ Employee transferred successfully!")
                            # Clear session state
                            del st.session_state['transfer_employee_id']
                            if st.session_state.get('transfer_and_continue'):
                                del st.session_state['transfer_and_continue']
                            st.rerun()
                        else:
                            st.error("❌ Failed to transfer employee.")
                    
                    if cancel:
                        # Clear session state
                        del st.session_state['transfer_employee_id']
                        st.rerun()
    

    
    def _render_edit_dialog(self):
        """Render edit employee dialog"""
        edit_employee_id = st.session_state.get('edit_employee_id')
        
        # Get employee details
        employee = next((emp for emp in self.employees if emp['employee_id'] == edit_employee_id), None)
        
        if employee:
            st.markdown("### ✏️ **Edit Employee**")
            st.markdown("---")
            
            st.info(f"**Editing:** {employee['name']} - {employee['post_name']}")
            
            with st.form("edit_employee_dialog_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Full Name *", value=employee['name'])
                    father_name = st.text_input("Father's Name", value=employee['father_name'])
                    date_of_birth = st.date_input("Date of Birth", value=employee['date_of_birth'], min_value=date(1950, 1, 1), max_value=date.today())
                    qualifications = st.text_area("Qualifications", value=employee['qualifications'])
                    caste = st.selectbox("Caste", ["General", "OBC", "SC", "ST", "Other"], 
                                       index=["General", "OBC", "SC", "ST", "Other"].index(employee['caste']))
                    gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                        index=["Male", "Female", "Other"].index(employee['gender']))
                
                with col2:
                    branch = st.text_input("Branch", value=employee['branch'])
                    date_of_joining = st.date_input("Date of Joining", value=employee['date_of_joining'])
                    address = st.text_area("Address", value=employee['address'])
                    acr = st.selectbox("ACR Rating", ["Outstanding", "Excellent", "Very Good", "Good", "Average", "Poor"],
                                     index=["Outstanding", "Excellent", "Very Good", "Good", "Average", "Poor"].index(employee['acr']))
                    salary = st.number_input("Salary (₹)", min_value=0, value=int(employee['salary']), step=1000)
                    
                    # Post selection
                    posts = db_manager.get_all_posts()
                    post_options = {f"{p['post_name']} ({p['post_class']})": p['post_id'] for p in posts}
                    current_post = f"{employee['post_name']} ({employee['post_class']})"
                    selected_post = st.selectbox("Post *", options=list(post_options.keys()), 
                                               index=list(post_options.keys()).index(current_post))
                    post_id = post_options[selected_post]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    submitted = st.form_submit_button("💾 Update Employee")
                
                with col2:
                    cancel = st.form_submit_button("❌ Cancel")
                
                with col3:
                    if st.form_submit_button("🔄 Update & Edit Another"):
                        submitted = True
                        st.session_state.edit_and_continue = True
                
                if submitted:
                    if not name or not post_id:
                        st.error("Name and Post are required fields!")
                    else:
                        employee_data = {
                            'name': name,
                            'father_name': father_name,
                            'date_of_birth': date_of_birth,
                            'qualifications': qualifications,
                            'caste': caste,
                            'gender': gender,
                            'branch': branch,
                            'post_id': post_id,
                            'date_of_joining': date_of_joining,
                            'address': address,
                            'acr': acr,
                            'salary': salary
                        }
                        
                        if db_manager.update_employee(edit_employee_id, employee_data):
                            st.success("✅ Employee updated successfully!")
                            # Clear session state
                            del st.session_state['edit_employee_id']
                            if st.session_state.get('edit_and_continue'):
                                del st.session_state['edit_and_continue']
                            st.rerun()
                        else:
                            st.error("❌ Failed to update employee.")
                    
                    if cancel:
                        # Clear session state
                        del st.session_state['edit_employee_id']
                        st.rerun()
    
    def _render_add_employee(self):
        """Render add employee form"""
        st.write("**Add New Employee:**")
        
        # Clear form if requested
        if st.session_state.get('clear_add_form', False):
            st.session_state.clear_add_form = False
            # Reset form by not providing default values
        
        with st.form("add_employee_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name *")
                date_of_birth = st.date_input("Date of Birth", min_value=date(1950, 1, 1), max_value=date.today())
                caste = st.selectbox("Caste", ["General", "OBC", "SC", "ST", "Other"])
                # Auto-fill court name and make it non-editable
                court_name = self.court_details.get('court_name', '')
                st.text_input("Court", value=court_name, disabled=True)
                date_of_joining = st.date_input("Date of Joining", min_value=date(1990, 1, 1), max_value=date.today())
                address = st.text_area("Address")
                salary = st.number_input("Salary (₹)", min_value=0, value=30000, step=1000)
            
            with col2:
                father_name = st.text_input("Father's Name")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                # Post selection
                posts = db_manager.get_all_posts()
                post_options = {f"{p['post_name']} ({p['post_class']})": p['post_id'] for p in posts}
                selected_post = st.selectbox("Post *", options=list(post_options.keys()))
                post_id = post_options[selected_post]
                # Auto-fill division name and make it non-editable
                division_name = self.court_details.get('division_name', '')
                st.text_input("Division", value=division_name, disabled=True)
                qualifications = st.text_area("Qualifications")
                acr = st.selectbox("ACR Rating", ["Outstanding", "Excellent", "Very Good", "Good", "Average", "Poor"])
            
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                if not name or not post_id:
                    st.error("Name and Post are required fields!")
                else:
                    employee_data = {
                        'name': name,
                        'father_name': father_name,
                        'date_of_birth': date_of_birth,
                        'qualifications': qualifications,
                        'caste': caste,
                        'gender': gender,
                        'branch': court_name,  # Use court name instead of branch
                        'post_id': post_id,
                        'date_of_joining': date_of_joining,
                        'address': address,
                        'acr': acr,
                        'salary': salary,
                        'court_id': self.court_id
                    }
                    
                    if db_manager.add_employee(employee_data):
                        st.success("Employee added successfully")
                        st.session_state.employee_added = True
                        st.rerun()
                    else:
                        st.error("❌ Failed to add employee.")
    

    

    
    def render_court_operations(self):
        """Render export employee list button"""
        st.subheader("📥 Export Employee List")
        if self.employees:
            df = pd.DataFrame(self.employees)
            
            # Add missing columns from court details
            df['division_name'] = self.court_details.get('division_name', '')
            df['court_number'] = self.court_details.get('court_number', '')
            df['court_name'] = self.court_details.get('court_name', '')
            df['officer_name'] = self.court_details.get('officer_name', '')
            
            # Add sanctioned vacancies and available vacancies from posts data
            post_vacancies = {}
            post_available_vacancies = {}
            if hasattr(self, 'posts') and self.posts:
                for post in self.posts:
                    post_vacancies[post['post_name']] = post['sanctioned_vacancies']
                    post_available_vacancies[post['post_name']] = post['available_vacancies']
            
            df['sanctioned_vacancies'] = df['post_name'].map(post_vacancies).fillna(0)
            df['available_vacancies'] = df['post_name'].map(post_available_vacancies).fillna(0)
            
            # Reorder and rename columns for export
            column_mapping = {
                'employee_id': 'Employee ID',
                'division_name': 'Division',
                'court_number': 'Court Number', 
                'court_name': 'Court Name',
                'officer_name': 'Officer Name',
                'post_name': 'Post',
                'post_class': 'Class',
                'sanctioned_vacancies': 'Sanctioned Vacancies',
                'available_vacancies': 'Vacancies',
                'name': 'Employee Name',
                'gender': 'Gender',
                'father_name': "Father's Name",
                'date_of_birth': 'Date of Birth',
                'qualifications': 'Qualification',
                'retirement_date': 'Retirement Date'
            }
            
            # Select and rename columns in the desired order
            export_columns = [
                'employee_id', 'division_name', 'court_number', 'court_name', 
                'officer_name', 'post_name', 'post_class', 'sanctioned_vacancies',
                'available_vacancies', 'name', 'gender', 'father_name', 'date_of_birth', 
                'qualifications', 'retirement_date'
            ]
            
            # Filter dataframe to only include available columns
            available_columns = [col for col in export_columns if col in df.columns]
            df_export = df[available_columns].copy()
            
            # Rename columns
            df_export = df_export.rename(columns=column_mapping)
            
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"employees_{self.court_details['court_name'].replace(' ', '_')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No employees to export.")
