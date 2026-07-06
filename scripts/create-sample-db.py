#!/usr/bin/env python3
"""Create a sample SQLite database with employees, departments, companies, and projects."""
import sqlite3, os

DB_PATH = '/opt/hermes-gw/sample_company.db'

# Remove old DB if exists
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Companies
c.execute('''CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT,
    country TEXT,
    employees_total INTEGER,
    revenue_mm REAL
)''')

c.executemany('INSERT INTO companies VALUES (?,?,?,?,?,?)', [
    (1, 'TechNova', 'Technology', 'Spain', 250, 45.2),
    (2, 'GreenEnergy Plus', 'Energy', 'Germany', 1200, 320.8),
    (3, 'FinServ Global', 'Finance', 'UK', 8500, 2100.0),
    (4, 'BioHealth Corp', 'Healthcare', 'France', 430, 89.5),
    (5, 'DataMiners SL', 'Technology', 'Spain', 85, 12.3),
    (6, 'EuroConstruct', 'Construction', 'Italy', 3400, 780.0),
    (7, 'RetailMax Iberia', 'Retail', 'Spain', 5200, 1450.0),
    (8, 'AutoParts Express', 'Automotive', 'Germany', 920, 195.0),
])

# Departments
c.execute('''CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    company_id INTEGER,
    budget REAL,
    FOREIGN KEY (company_id) REFERENCES companies(id)
)''')

c.executemany('INSERT INTO departments VALUES (?,?,?,?)', [
    (1, 'Engineering', 1, 500000),
    (2, 'Sales', 1, 350000),
    (3, 'Engineering', 5, 200000),
    (4, 'Finance', 3, 2000000),
    (5, 'HR', 3, 800000),
    (6, 'R&D', 4, 1200000),
    (7, 'Operations', 2, 3000000),
    (8, 'Marketing', 1, 250000),
    (9, 'IT', 7, 1800000),
    (10, 'Logistics', 7, 2200000),
])

# Employees
c.execute('''CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    department_id INTEGER,
    salary REAL,
    hire_date TEXT,
    seniority_years INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(id)
)''')

c.executemany('INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)', [
    (1, 'Ana', 'García', 'ana.garcia@technova.com', 1, 75000, '2020-03-15', 6),
    (2, 'Carlos', 'Müller', 'carlos.muller@technova.com', 1, 82000, '2019-01-10', 7),
    (3, 'Elena', 'Rossi', 'elena.rossi@technova.com', 2, 65000, '2021-07-01', 5),
    (4, 'Marcus', 'Johnson', 'marcus.johnson@finserv.com', 4, 120000, '2018-11-20', 7),
    (5, 'Sophie', 'Dubois', 'sophie.dubois@finserv.com', 4, 95000, '2020-06-01', 6),
    (6, 'James', 'Smith', 'james.smith@finserv.com', 5, 78000, '2022-01-15', 4),
    (7, 'Laura', 'Fernández', 'laura.fernandez@dataminers.com', 3, 68000, '2023-02-01', 3),
    (8, 'Marco', 'Bianchi', 'marco.bianchi@greenenergy.com', 7, 88000, '2019-09-01', 6),
    (9, 'Isabel', 'Santos', 'isabel.santos@retailmax.com', 9, 72000, '2021-04-01', 5),
    (10, 'David', 'Cohen', 'david.cohen@biohealth.com', 6, 105000, '2017-08-15', 8),
    (11, 'Patricia', 'López', 'patricia.lopez@retailmax.com', 10, 63000, '2022-11-01', 3),
    (12, 'Thomas', 'Weber', 'thomas.weber@autoparts.com', None, 91000, '2018-03-01', 8),
    (13, 'María', 'Gómez', 'maria.gomez@technova.com', 8, 58000, '2023-09-01', 2),
    (14, 'Alex', 'Turner', 'alex.turner@finserv.com', 4, 135000, '2016-05-01', 10),
    (15, 'Sara', 'Nielsen', 'sara.nielsen@greenenergy.com', 7, 79000, '2020-10-01', 5),
])

# Projects
c.execute('''CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    company_id INTEGER,
    department_id INTEGER,
    budget REAL,
    status TEXT,
    start_date TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
)''')

c.executemany('INSERT INTO projects VALUES (?,?,?,?,?,?,?)', [
    (1, 'CloudMigration', 1, 1, 150000, 'active', '2025-01-01'),
    (2, 'AIChatbot', 1, 1, 80000, 'active', '2025-03-01'),
    (3, 'RiskEngine', 3, 4, 500000, 'active', '2024-11-01'),
    (4, 'DrugDiscovery', 4, 6, 300000, 'planning', '2025-06-01'),
    (5, 'SolarFarm', 2, 7, 1200000, 'active', '2024-06-01'),
    (6, 'POS Upgrade', 7, 9, 200000, 'completed', '2024-09-01'),
    (7, 'DataLake', 5, 3, 45000, 'active', '2025-02-01'),
    (8, 'MobileApp v2', 1, 1, 110000, 'planning', '2025-07-01'),
])

conn.commit()
conn.close()
print(f"Database created: {DB_PATH}")
print(f"Size: {os.path.getsize(DB_PATH)} bytes")
print(f"Tables: companies ({c.rowcount} rows), departments, employees, projects")
