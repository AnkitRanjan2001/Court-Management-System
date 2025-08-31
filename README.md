# Court Management System

A comprehensive Streamlit-based application for managing court employees, divisions, and administrative tasks for the District and Sessions Court, Jind.

## 🏛️ Features

### Core Functionality
- **Employee Management**: Add, edit, and manage court employees
- **Division Management**: Organize courts by divisions
- **Court Management**: Individual court employee tracking
- **Post Management**: Manage different employee positions
- **Retirement Tracking**: Automatic retirement date calculation
- **Vacancy Analysis**: Track and analyze employee vacancies

### Views Available
- **Individual Court View**: Detailed view for specific courts
- **Division-Wide View**: Overview of all courts in a division
- **System-Wide View**: Complete system overview with statistics

### Authentication & Security
- **User Authentication**: Secure login system
- **Role-Based Access**: Admin and regular user roles
- **Password Management**: Change password functionality
- **User Management**: Admin can manage users

### Data Management
- **CSV Export**: Export employee data in various formats
- **Database Backup**: Export/import database snapshots
- **Filtering & Search**: Advanced filtering options

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd "Jind Sessions Court"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python init_database.py
   ```

5. **Run the application**
   ```bash
   streamlit run main_app.py
   ```

## 🔐 Default Login

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default password immediately after first login!

## 📁 Project Structure

```
Jind Sessions Court/
├── main_app.py                 # Main Streamlit application
├── auth_component.py           # Authentication and user management
├── sidebar_component.py        # Sidebar navigation
├── court_management_component.py # Individual court management
├── division_management_component.py # Division-wide management
├── system_management_component.py # System-wide management
├── database_operations.py      # Database operations
├── init_database.py           # Database initialization
├── insert_dummy_data.py       # Sample data insertion
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🗄️ Database Schema

The application uses SQLite with the following main tables:
- `divisions`: Court divisions
- `courts`: Individual courts
- `posts`: Employee positions
- `employees`: Employee records
- `users`: User accounts

## 🔧 Configuration

### Environment Variables
Create a `.env` file for any environment-specific configurations:
```
DATABASE_PATH=court_management.db
DEBUG_MODE=False
```

### Database Configuration
The database file (`court_management.db`) is automatically created on first run. Make sure to:
- Keep regular backups
- Never commit the database file to version control
- Use the export/import functionality for data migration

## 📊 Usage

### For Administrators
1. **User Management**: Add new users and manage roles
2. **System Management**: Create new courts and posts
3. **Database Management**: Export/import database snapshots
4. **Employee Management**: Full CRUD operations on employees

### For Regular Users
1. **View Employees**: Browse and filter employee data
2. **Export Data**: Generate CSV reports
3. **View Statistics**: Access division and system-wide views

## 🔒 Security Considerations

- **Database Protection**: The `.gitignore` file prevents database files from being committed
- **Password Hashing**: Passwords are hashed using SHA-256
- **Session Management**: Secure session handling
- **Input Validation**: All user inputs are validated

## 🚨 Important Notes

1. **Database Security**: Never commit the `court_management.db` file
2. **Default Credentials**: Change admin password immediately
3. **Backup Regularly**: Use the export functionality for backups
4. **Environment**: Use virtual environment for isolation

## 🛠️ Development

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes
3. Test thoroughly
4. Create pull request

### Code Style
- Follow PEP 8 guidelines
- Add docstrings for functions
- Use meaningful variable names
- Comment complex logic

## 📞 Support

For issues or questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## 📄 License

This project is developed for the District and Sessions Court, Jind.

---

**Note**: This is a production system for court management. Handle all data with appropriate care and security measures.
