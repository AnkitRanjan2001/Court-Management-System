-- Court Employee Management System Database Schema
-- SQLite Database Creation Script

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- 1. DIVISION TABLE
CREATE TABLE IF NOT EXISTS divisions (
    division_id INTEGER PRIMARY KEY AUTOINCREMENT,
    division_name VARCHAR(255) NOT NULL,
    parent_division_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_division_id) REFERENCES divisions(division_id)
);

-- 2. COURT TABLE
CREATE TABLE IF NOT EXISTS courts (
    court_id INTEGER PRIMARY KEY AUTOINCREMENT,
    court_name VARCHAR(255) NOT NULL,
    court_number VARCHAR(50),
    officer_name VARCHAR(255),
    location TEXT,
    parent_division_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_division_id) REFERENCES divisions(division_id)
);

-- 3. POST TABLE
CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_name VARCHAR(255) NOT NULL UNIQUE,
    post_class VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. EMPLOYEE TABLE
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    father_name VARCHAR(255),
    date_of_birth DATE,
    qualifications TEXT,
    caste VARCHAR(100),
    gender VARCHAR(20),
    branch VARCHAR(100),
    post_id INTEGER NOT NULL,
    date_of_joining DATE,
    address TEXT,
    acr TEXT,
    salary DECIMAL(10,2),
    retirement_date DATE,
    court_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(post_id),
    FOREIGN KEY (court_id) REFERENCES courts(court_id)
);

-- 5. POST_COURT TABLE (Junction table for many-to-many relationship)
CREATE TABLE IF NOT EXISTS post_courts (
    court_id INTEGER,
    post_id INTEGER,
    sanctioned_vacancies INTEGER DEFAULT 0,
    active_employees_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (court_id, post_id),
    FOREIGN KEY (court_id) REFERENCES courts(court_id),
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_employees_court_id ON employees(court_id);
CREATE INDEX IF NOT EXISTS idx_employees_post_id ON employees(post_id);
CREATE INDEX IF NOT EXISTS idx_courts_division_id ON courts(parent_division_id);
CREATE INDEX IF NOT EXISTS idx_divisions_parent_id ON divisions(parent_division_id);
CREATE INDEX IF NOT EXISTS idx_post_courts_court_id ON post_courts(court_id);
CREATE INDEX IF NOT EXISTS idx_post_courts_post_id ON post_courts(post_id);

-- Create trigger to update retirement date when date_of_birth is inserted/updated
CREATE TRIGGER IF NOT EXISTS calculate_retirement_date_insert
AFTER INSERT ON employees
BEGIN
    UPDATE employees 
    SET retirement_date = date(date_of_birth, '+58 years', 'last day of month')
    WHERE employee_id = NEW.employee_id;
END;

CREATE TRIGGER IF NOT EXISTS calculate_retirement_date_update
AFTER UPDATE OF date_of_birth ON employees
BEGIN
    UPDATE employees 
    SET retirement_date = date(NEW.date_of_birth, '+58 years', 'last day of month')
    WHERE employee_id = NEW.employee_id;
END;

-- Create trigger to update active_employees_count in post_courts table
CREATE TRIGGER IF NOT EXISTS update_active_employees_count_insert
AFTER INSERT ON employees
BEGIN
    UPDATE post_courts 
    SET active_employees_count = (
        SELECT COUNT(*) 
        FROM employees 
        WHERE employees.court_id = NEW.court_id 
        AND employees.post_id = NEW.post_id
    )
    WHERE court_id = NEW.court_id AND post_id = NEW.post_id;
END;

CREATE TRIGGER IF NOT EXISTS update_active_employees_count_update
AFTER UPDATE OF court_id, post_id ON employees
BEGIN
    -- Update count for old court-post combination
    UPDATE post_courts 
    SET active_employees_count = (
        SELECT COUNT(*) 
        FROM employees 
        WHERE employees.court_id = OLD.court_id 
        AND employees.post_id = OLD.post_id
    )
    WHERE court_id = OLD.court_id AND post_id = OLD.post_id;
    
    -- Update count for new court-post combination
    UPDATE post_courts 
    SET active_employees_count = (
        SELECT COUNT(*) 
        FROM employees 
        WHERE employees.court_id = NEW.court_id 
        AND employees.post_id = NEW.post_id
    )
    WHERE court_id = NEW.court_id AND post_id = NEW.post_id;
END;

CREATE TRIGGER IF NOT EXISTS update_active_employees_count_delete
AFTER DELETE ON employees
BEGIN
    UPDATE post_courts 
    SET active_employees_count = (
        SELECT COUNT(*) 
        FROM employees 
        WHERE employees.court_id = OLD.court_id 
        AND employees.post_id = OLD.post_id
    )
    WHERE court_id = OLD.court_id AND post_id = OLD.post_id;
END;

-- Insert default division (Jind Sessions Court)
INSERT OR IGNORE INTO divisions (division_id, division_name, parent_division_id) 
VALUES (1, 'Jind Sessions Court', NULL);

-- Insert some default posts
INSERT OR IGNORE INTO posts (post_name, post_class) VALUES 
('Judge', 'Class I'),
('Clerk', 'Class II'),
('Stenographer', 'Class II'),
('Peon', 'Class IV'),
('Driver', 'Class IV'),
('Security Guard', 'Class IV');

-- Create view for employee details with related information
CREATE VIEW IF NOT EXISTS employee_details AS
SELECT 
    e.employee_id,
    e.name,
    e.father_name,
    e.date_of_birth,
    e.qualifications,
    e.caste,
    e.gender,
    e.branch,
    e.date_of_joining,
    e.address,
    e.acr,
    e.salary,
    e.retirement_date,
    p.post_name,
    p.post_class,
    c.court_name,
    c.court_number,
    c.location,
    d.division_name
FROM employees e
LEFT JOIN posts p ON e.post_id = p.post_id
LEFT JOIN courts c ON e.court_id = c.court_id
LEFT JOIN divisions d ON c.parent_division_id = d.division_id;

-- Create view for vacancy analysis
CREATE VIEW IF NOT EXISTS vacancy_analysis AS
SELECT 
    c.court_name,
    p.post_name,
    pc.sanctioned_vacancies,
    pc.active_employees_count,
    (pc.sanctioned_vacancies - pc.active_employees_count) as available_vacancies
FROM post_courts pc
JOIN courts c ON pc.court_id = c.court_id
JOIN posts p ON pc.post_id = p.post_id
ORDER BY c.court_name, p.post_name;
