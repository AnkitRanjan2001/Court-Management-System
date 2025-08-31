import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from database_operations import db_manager
from typing import Dict, List, Optional

class SystemManagementComponent:
    def __init__(self):
        self.divisions = []
        self.courts = []
        self.employees = []
    
    def render_system_overview(self):
        """Render system-wide overview"""
        # Get all divisions and courts
        self.divisions = db_manager.get_divisions_with_parent()
        self.courts = db_manager.get_all_courts()
        self.employees = db_manager.get_all_employees()
        
        # Display main heading
        st.markdown(f"""
        <h1 style="
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        ">
            🏛️ Jind Sessions Court
        </h1>
        """, unsafe_allow_html=True)
        
        # System Summary
        st.subheader("📊 System Summary")
        self._render_system_summary()
        
        st.markdown("---")
        
        # System Management
        st.subheader("🏗️ System Management")
        self._render_system_management()
        
        st.markdown("---")
        
        # Division-wise Breakdown
        st.subheader("🏛️ Division-wise Breakdown")
        self._render_division_breakdown()
        
        st.markdown("---")
        
        # Upcoming Retirements
        st.subheader("👥 Upcoming Retirements (Next 2 Months)")
        self._render_upcoming_retirements()
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("🔧 Quick Actions")
        self._render_quick_actions()
        
        # Database Management (always show for admin)
        st.markdown("---")
        st.subheader("💾 Database Management")
        self._render_database_management()
    
    def _render_system_summary(self):
        """Render system summary statistics"""
        # Calculate system-wide statistics
        total_divisions = len(self.divisions)
        total_courts = len(self.courts)
        total_employees = len(self.employees)
        total_posts = len(db_manager.get_all_posts())
        total_vacancies = db_manager.get_system_vacancy_count()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Divisions", total_divisions)
        with col2:
            st.metric("Total Courts", total_courts)
        with col3:
            st.metric("Total Employees", total_employees)
        with col4:
            st.metric("Total Posts", total_posts)
        with col5:
            st.metric("Total Vacancies", total_vacancies)
    
    def _render_division_breakdown(self):
        """Render division-wise breakdown with courts"""
        if not self.divisions:
            st.info("No divisions found.")
            return
        
        for division in self.divisions:
            division_id = division['division_id']
            division_name = division['division_name']
            
            # Get division statistics
            division_employee_count = db_manager.get_employee_count_by_division(division_id)
            division_vacancy_count = db_manager.get_vacancy_count_by_division(division_id)
            
            # Get courts in this division
            division_courts = db_manager.get_courts_by_division(division_id)
            
            # Create expandable section for each division
            with st.expander(f"🏛️ {division_name} ({division_employee_count} employees, {division_vacancy_count} vacancies)"):
                # Division summary
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Total Employees:** {division_employee_count}")
                with col2:
                    st.write(f"**Total Vacancies:** {division_vacancy_count}")
                
                # Courts list
                if division_courts:
                    st.write("**Courts:**")
                    court_data = []
                    for court in division_courts:
                        court_id = court['court_id']
                        court_employee_count = db_manager.get_employee_count_by_court(court_id)
                        court_vacancy_count = db_manager.get_vacancy_count_by_court(court_id)
                        
                        court_data.append({
                            'Court Name': court['court_name'],
                            'Court Number': court['court_number'] or 'N/A',
                            'Employees': court_employee_count,
                            'Vacancies': court_vacancy_count
                        })
                    
                    df_courts = pd.DataFrame(court_data)
                    st.dataframe(df_courts, use_container_width=True, hide_index=True)
                else:
                    st.info("No courts found in this division.")
    
    def _render_upcoming_retirements(self):
        """Render upcoming retirements in next 2 months"""
        # Calculate date range for next 2 months
        today = date.today()
        two_months_later = today + timedelta(days=60)
        
        # Get employees retiring in next 2 months
        retiring_employees = db_manager.get_employees_retiring_between(today, two_months_later)
        
        if retiring_employees:
            # Create DataFrame for display
            retirement_data = []
            for emp in retiring_employees:
                retirement_data.append({
                    'Employee ID': emp['employee_id'],
                    'Division': emp['division_name'],
                    'Court Number': emp['court_number'] or 'N/A',
                    'Court Name': emp['court_name'],
                    'Employee Name': emp['name'],
                    'Post': emp['post_name'],
                    'Retirement Date': emp['retirement_date']
                })
            
            df_retirements = pd.DataFrame(retirement_data)
            st.dataframe(df_retirements, use_container_width=True, hide_index=True)
        else:
            st.info("No employees retiring in the next 2 months.")
    
    def _render_quick_actions(self):
        """Render quick action buttons"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Vacancy Summary"):
                self._show_vacancy_summary()
        
        with col2:
            if st.button("⚠️ Retirement Alerts (6 months)"):
                self._show_retirement_alerts()
        
        with col3:
            if st.button("📥 Export All Data"):
                self._export_all_data()
        
        # Database backup and restore (admin only)
        # Check if current user is admin
        current_user = st.session_state.get('user')
        if current_user and current_user.get('role') == 'admin':
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📤 Export Database Snapshot"):
                    self._export_database_snapshot()
            
            with col2:
                if st.button("📥 Restore Database"):
                    self._show_restore_database()
        else:
            st.info("🔒 Database management features are only available to administrators.")
    
    def _render_database_management(self):
        """Render database management section"""
        # Check if current user is admin
        current_user = st.session_state.get('user')
        if current_user and current_user.get('role') == 'admin':
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📤 Export Database Snapshot", key="export_db"):
                    self._export_database_snapshot()
            
            with col2:
                if st.button("📥 Restore Database", key="restore_db"):
                    self._show_restore_database()
        else:
            st.info("🔒 Database management features are only available to administrators.")
    
    def _render_system_management(self):
        """Render system management options"""
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🏛️ Create Court"):
                self._show_create_court_form()
        
        with col2:
            if st.button("📋 Create Post"):
                self._show_create_post_form()
    
    def _show_vacancy_summary(self):
        """Show vacancy summary table"""
        st.write("### 📋 Vacancy Summary")
        
        # Get vacancy data for all courts
        vacancy_data = []
        for court in self.courts:
            court_id = court['court_id']
            court_posts = db_manager.get_court_posts_with_vacancies(court_id)
            
            for post in court_posts:
                if post['available_vacancies'] > 0:  # Only show posts with vacancies
                    vacancy_data.append({
                        'Division': court['division_name'],
                        'Court Name': court['court_name'],
                        'Court Number': court['court_number'] or 'N/A',
                        'Post': post['post_name'],
                        'Class': post['post_class'],
                        'Sanctioned': post['sanctioned_vacancies'],
                        'Current': post['active_employees_count'],
                        'Vacancies': post['available_vacancies']
                    })
        
        if vacancy_data:
            df_vacancies = pd.DataFrame(vacancy_data)
            st.dataframe(df_vacancies, use_container_width=True, hide_index=True)
        else:
            st.info("No vacancies found across the system.")
    
    def _show_retirement_alerts(self):
        """Show retirement alerts for next 6 months"""
        st.write("### ⚠️ Retirement Alerts (Next 6 Months)")
        
        # Calculate date range for next 6 months
        today = date.today()
        six_months_later = today + timedelta(days=180)
        
        # Get employees retiring in next 6 months
        retiring_employees = db_manager.get_employees_retiring_between(today, six_months_later)
        
        if retiring_employees:
            # Group by month
            retirement_by_month = {}
            for emp in retiring_employees:
                retirement_date = emp['retirement_date']
                # Handle retirement date - it might be a string from database or NaT
                if retirement_date and retirement_date != pd.NaT:
                    if isinstance(retirement_date, str):
                        # Convert string to date object for formatting
                        try:
                            retirement_date_obj = datetime.strptime(retirement_date, '%Y-%m-%d').date()
                            month_key = retirement_date_obj.strftime('%B %Y')
                        except:
                            month_key = 'Unknown'
                    else:
                        try:
                            month_key = retirement_date.strftime('%B %Y')
                        except (ValueError, AttributeError):
                            month_key = 'Unknown'
                else:
                    month_key = 'Unknown'
                
                if month_key not in retirement_by_month:
                    retirement_by_month[month_key] = []
                retirement_by_month[month_key].append(emp)
            
            # Display by month
            for month, employees in retirement_by_month.items():
                st.write(f"**{month} ({len(employees)} employees):**")
                
                month_data = []
                for emp in employees:
                    month_data.append({
                        'Employee ID': emp['employee_id'],
                        'Division': emp['division_name'],
                        'Court': emp['court_name'],
                        'Employee Name': emp['name'],
                        'Post': emp['post_name'],
                        'Retirement Date': emp['retirement_date']
                    })
                
                df_month = pd.DataFrame(month_data)
                st.dataframe(df_month, use_container_width=True, hide_index=True)
                st.markdown("---")
        else:
            st.info("No employees retiring in the next 6 months.")
    
    def _export_all_data(self):
        """Export all employees data to CSV"""
        if self.employees:
            df = pd.DataFrame(self.employees)
            
            # Add missing columns from court and division details
            df['division_name'] = df['court_id'].map(lambda x: self._get_division_name_by_court(x))
            
            # Add court information for each employee
            court_info = {}
            for court in self.courts:
                court_info[court['court_id']] = {
                    'court_number': court['court_number'],
                    'court_name': court['court_name'],
                    'officer_name': court.get('officer_name', '')
                }
            
            df['court_number'] = df['court_id'].map(lambda x: court_info.get(x, {}).get('court_number', ''))
            df['court_name'] = df['court_id'].map(lambda x: court_info.get(x, {}).get('court_name', ''))
            df['officer_name'] = df['court_id'].map(lambda x: court_info.get(x, {}).get('officer_name', ''))
            
            # Add sanctioned vacancies from posts data
            post_vacancies = {}
            for court in self.courts:
                court_posts = db_manager.get_court_posts_with_vacancies(court['court_id'])
                for post in court_posts:
                    key = f"{post['post_name']}_{court['court_id']}"
                    post_vacancies[key] = post['sanctioned_vacancies']
            
            df['post_court_key'] = df['post_name'] + '_' + df['court_id'].astype(str)
            df['sanctioned_vacancies'] = df['post_court_key'].map(post_vacancies).fillna(0)
            
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
                'name', 'gender', 'father_name', 'date_of_birth', 
                'qualifications', 'retirement_date'
            ]
            
            # Filter dataframe to only include available columns
            available_columns = [col for col in export_columns if col in df.columns]
            df_export = df[available_columns].copy()
            
            # Rename columns
            df_export = df_export.rename(columns=column_mapping)
            
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="📥 Download All Data (CSV)",
                data=csv,
                file_name=f"all_employees_{date.today().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No employees found in the system.")
    
    def _get_division_name_by_court(self, court_id):
        """Helper method to get division name by court ID"""
        for court in self.courts:
            if court['court_id'] == court_id:
                return court['division_name']
        return ''
    
    def _show_create_court_form(self):
        """Show create court form"""
        with st.form("create_court_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                court_name = st.text_input("Court Name *")
                court_number = st.text_input("Court Number")
                officer_name = st.text_input("Officer Name")
            
            with col2:
                # Division selection
                divisions = db_manager.get_divisions_with_parent()
                division_options = {div['division_name']: div['division_id'] for div in divisions}
                selected_division = st.selectbox("Division *", options=list(division_options.keys()))
                division_id = division_options[selected_division]
                
                location = st.text_input("Location")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Submit")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submitted:
                if not court_name or not division_id:
                    st.error("Court Name and Division are required fields!")
                else:
                    if db_manager.add_court(court_name, court_number, officer_name, location, division_id):
                        st.success("Court created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create court.")
            
            if cancel:
                st.rerun()
    
    def _show_create_post_form(self):
        """Show create post form"""
        with st.form("create_post_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                post_name = st.text_input("Post Name *")
                post_class = st.selectbox("Post Class *", ["Class I", "Class II", "Class III", "Class IV"])
            
            with col2:
                description = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Submit")
            with col2:
                cancel = st.form_submit_button("Cancel")
            
            if submitted:
                if not post_name or not post_class:
                    st.error("Post Name and Post Class are required fields!")
                else:
                    if db_manager.add_post(post_name, post_class, description):
                        st.success("Post created successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create post.")
            
            if cancel:
                st.rerun()
    
    def _export_database_snapshot(self):
        """Export database as SQL snapshot"""
        try:
            sql_dump = db_manager.export_database_snapshot()
            if sql_dump:
                # Create filename with timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"jind_court_database_snapshot_{timestamp}.sql"
                
                st.download_button(
                    label="📥 Download Database Snapshot",
                    data=sql_dump,
                    file_name=filename,
                    mime="text/plain",
                    help="Download complete database backup as SQL file"
                )
                st.success("Database snapshot ready for download!")
            else:
                st.error("Failed to export database snapshot.")
        except Exception as e:
            st.error(f"Error exporting database: {e}")
    
    def _show_restore_database(self):
        """Show database restore interface"""
        st.warning("⚠️ **Warning:** This will replace all current data!")
        
        uploaded_file = st.file_uploader(
            "Choose SQL database snapshot file",
            type=['sql'],
            help="Upload a previously exported database snapshot"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                sql_content = uploaded_file.read().decode('utf-8')
                
                if st.button("🔄 Restore Database", type="primary"):
                    if db_manager.import_database_snapshot(sql_content):
                        st.success("✅ Database restored successfully!")
                        st.info("Please refresh the page to see the restored data.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to restore database.")
                        
            except Exception as e:
                st.error(f"Error reading file: {e}")
