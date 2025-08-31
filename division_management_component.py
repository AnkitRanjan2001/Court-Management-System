import streamlit as st
import pandas as pd
from datetime import date, datetime
from database_operations import db_manager
from typing import Dict, List, Optional

class DivisionManagementComponent:
    def __init__(self):
        self.division_id = None
        self.division_details = {}
        self.courts = []
        self.employees = []
    
    def render_division_details(self, division_id: int):
        """Render division information section"""
        self.division_id = division_id
        self.division_details = db_manager.get_division_details(division_id)
        
        if not self.division_details:
            st.error("Division details not found!")
            return
        
        # Get courts for this division
        self.courts = db_manager.get_courts_by_division(division_id)
        
        if self.courts:
            # Calculate division statistics
            total_courts = len(self.courts)
            total_employees = db_manager.get_employee_count_by_division(division_id)
            total_vacancies = db_manager.get_vacancy_count_by_division(division_id)
            
            # Display division header
            st.markdown(f"""
            <h1 style="
                font-size: 2.5rem;
                font-weight: bold;
                color: #1f77b4;
                text-align: center;
                margin-bottom: 2rem;
            ">
                🏛️ {self.division_details['division_name']}
            </h1>
            """, unsafe_allow_html=True)
            
            # Division Statistics
            st.subheader("📊 Division Statistics")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Courts in Division", total_courts)
            with col2:
                st.metric("Total Employees", total_employees)
            with col3:
                st.metric("Total Vacancies", total_vacancies)
            
            st.markdown("---")
            
            # Court-wise Breakdown
            st.subheader("⚖️ Court-wise Breakdown")
            self._render_court_breakdown()
            
            st.markdown("---")
            
            # Division Actions
            st.subheader("📥 Division Actions")
            self._render_division_actions()
    
    def _render_court_breakdown(self):
        """Render court-wise breakdown with employee count and vacancies"""
        if not self.courts:
            st.info("No courts found in this division.")
            return
        
        # Create table data for court breakdown
        court_data = []
        for court in self.courts:
            court_id = court['court_id']
            employee_count = db_manager.get_employee_count_by_court(court_id)
            vacancy_count = db_manager.get_vacancy_count_by_court(court_id)
            
            court_data.append({
                'Court Name': court['court_name'],
                'Court Number': court['court_number'] or 'N/A',
                'Officer Name': court['officer_name'] or 'Not Assigned',
                'Employees': employee_count,
                'Vacancies': vacancy_count
            })
        
        # Create DataFrame and display
        df_courts = pd.DataFrame(court_data)
        st.dataframe(df_courts, use_container_width=True, hide_index=True)
    
    def _render_division_actions(self):
        """Render division action buttons"""
        if self.courts:
            # Get all employees in the division
            self.employees = db_manager.get_division_employees(self.division_id)
            
            if self.employees:
                df = pd.DataFrame(self.employees)
                
                # Add missing columns from court details
                df['division_name'] = self.division_details.get('division_name', '')
                
                # Add court information for each employee
                court_info = {}
                for court in self.courts:
                    court_info[court['court_id']] = {
                        'court_number': court['court_number'],
                        'court_name': court['court_name'],
                        'officer_name': court['officer_name']
                    }
                
                df['court_number'] = df['court_id'].map(lambda x: court_info.get(x, {}).get('court_number', ''))
                df['court_name'] = df['court_id'].map(lambda x: court_info.get(x, {}).get('court_name', ''))
                df['officer_name'] = df['court_id'].map(lambda x: court_info.get(x, {}).get('officer_name', ''))
                
                # Add sanctioned vacancies and available vacancies from posts data
                post_vacancies = {}
                post_available_vacancies = {}
                for court in self.courts:
                    court_posts = db_manager.get_court_posts_with_vacancies(court['court_id'])
                    for post in court_posts:
                        key = f"{post['post_name']}_{court['court_id']}"
                        post_vacancies[key] = post['sanctioned_vacancies']
                        post_available_vacancies[key] = post['available_vacancies']
                
                df['post_court_key'] = df['post_name'] + '_' + df['court_id'].astype(str)
                df['sanctioned_vacancies'] = df['post_court_key'].map(post_vacancies).fillna(0)
                df['available_vacancies'] = df['post_court_key'].map(post_available_vacancies).fillna(0)
                
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
                    file_name=f"division_{self.division_details['division_name'].replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No employees found in this division.")
        else:
            st.info("No courts found in this division.")
    

