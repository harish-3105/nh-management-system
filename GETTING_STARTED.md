# Getting Started with NH Management System

This guide will help you set up and start using the National Highways Management System.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software
- **MySQL 8.0+** or **MariaDB 10.5+**
- **Python 3.8+** (for application layer)
- **Git** (optional, for version control)

### Optional Software
- **MySQL Workbench** (for database management)
- **Postman** (for API testing)
- **VS Code** or your preferred IDE

## Quick Start (5 Minutes)

### Step 1: Install MySQL

**Windows:**
1. Download MySQL Community Server from https://dev.mysql.com/downloads/
2. Run the installer and follow the wizard
3. Remember your root password!

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

**macOS:**
```bash
brew install mysql
brew services start mysql
```

### Step 2: Download the Project Files

If you have all the files in `f:\nh pro\`, you're ready to go!

### Step 3: Run the Setup Script

**Windows (PowerShell or Command Prompt):**
```cmd
cd "f:\nh pro"
setup_database.bat
```

**Linux/Mac (Terminal):**
```bash
cd "/path/to/nh pro"
chmod +x setup_database.sh
./setup_database.sh
```

### Step 4: Configure Environment

Copy the example environment file:
```bash
copy .env.example .env    # Windows
cp .env.example .env      # Linux/Mac
```

Edit `.env` and update the database password:
```
DB_PASSWORD=your_mysql_root_password
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Test the System

```bash
python nh_management.py
```

You should see:
```
Successfully connected to nh_management
Logged in as: Madurai Office Admin (division)

Assigned segments: 3
  - NH44: NH44 Trichy to Madurai
  - NH45: NH45 Trichy to Madurai
  ...
```

🎉 **Congratulations!** Your system is now set up and running!

---

## Detailed Setup Guide

### Manual Database Setup

If you prefer to set up the database manually:

#### 1. Create the Database
```sql
CREATE DATABASE nh_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE nh_management;
```

#### 2. Run SQL Scripts in Order
```bash
# Execute in MySQL command line or MySQL Workbench
SOURCE database_schema.sql;
SOURCE triggers.sql;
SOURCE validation_queries.sql;
SOURCE sample_data.sql;  # Optional
```

#### 3. Verify Installation
```sql
-- Check tables
SHOW TABLES;

-- Should show:
-- audit_log
-- divisions
-- nh_master
-- nh_road_details
-- nh_segments
-- road_configurations
-- users

-- Check sample data
SELECT COUNT(*) FROM divisions;      -- Should be 9
SELECT COUNT(*) FROM nh_master;      -- Should be 16
SELECT COUNT(*) FROM users;          -- Should be 11
```

### Understanding the Database Structure

#### Key Tables:

1. **divisions** - Division offices (9 offices across 3 divisions)
2. **nh_master** - List of 16 National Highways
3. **users** - System users (central authority + division office users)
4. **nh_segments** - Highway segments assigned to divisions
5. **road_configurations** - Types of road configurations (2L, 4L, etc.)
6. **nh_road_details** - Detailed configuration for each segment
7. **audit_log** - Complete audit trail

#### Sample Users:

After loading sample data, you can log in with:

**Central Authority:**
- Username: `central_admin`
- Password: `admin123`
- Role: Can manage everything

**Division Users (Madurai):**
- Username: `madurai_office`
- Password: `admin123`
- Role: Can only manage Madurai office segments

*(Change all passwords in production!)*

---

## Common Tasks

### Task 1: View Your Assigned Segments (Division User)

```sql
-- Login as division user first
-- Then run:
SELECT 
    nm.nh_number,
    ns.segment_name,
    ns.start_chainage,
    ns.end_chainage,
    ROUND(ns.end_chainage - ns.start_chainage, 3) AS length_km
FROM nh_segments ns
JOIN nh_master nm ON ns.nh_id = nm.nh_id
WHERE ns.division_office_id = 2  -- Your division office ID
ORDER BY nm.nh_number, ns.start_chainage;
```

### Task 2: Add Road Configuration Details

```sql
-- Get your segment_id first
SELECT segment_id, segment_name FROM nh_segments 
WHERE division_office_id = 2;

-- Then add details
INSERT INTO nh_road_details 
(segment_id, config_id, start_chainage, end_chainage, remarks, created_by)
VALUES 
(4, 3, 200.000, 220.000, 'Four lanes section', 4);
```

### Task 3: View NH Summary Report

```sql
-- Get summary for NH44
CALL sp_get_nh_summary(3);

-- Or use the view
SELECT * FROM vw_nh_config_summary 
WHERE nh_number = 'NH44';
```

### Task 4: Check for Data Issues

```sql
-- Check for overlapping segments
SELECT * FROM vw_overlapping_segments;

-- Check for overlapping configurations
SELECT * FROM vw_overlapping_configurations;

-- Check for out-of-bounds details
SELECT * FROM vw_out_of_bounds_details;
```

---

## Python Application Usage

### Basic Usage Example

```python
from nh_management import *

# Connect to database
db = NHDatabase(
    host="localhost",
    database="nh_management",
    user="root",
    password="your_password"
)

db.connect()

# Authenticate user
user_mgr = UserManager(db)
user = user_mgr.authenticate("madurai_office", "admin123")

if user:
    print(f"Welcome, {user['full_name']}!")
    
    # Get assigned segments
    segment_mgr = SegmentManager(db)
    segments = segment_mgr.get_segments_by_division(
        user['division_office_id']
    )
    
    print(f"You have {len(segments)} assigned segments")
    
    # Add road detail
    detail_mgr = RoadDetailManager(db)
    success = detail_mgr.add_road_detail(
        segment_id=4,
        config_id=3,
        start_chainage=200.0,
        end_chainage=220.0,
        created_by=user['user_id'],
        remarks="Four lanes section"
    )
    
    if success:
        print("Road detail added successfully!")

db.disconnect()
```

### Creating New Users

```python
user_mgr = UserManager(db)

# Create a central authority user
user_mgr.create_user(
    username="central_user2",
    password="SecurePass123!",
    role="central",
    full_name="John Doe",
    email="john.doe@highways.gov.in",
    division_office_id=None
)

# Create a division user
user_mgr.create_user(
    username="chennai_user1",
    password="SecurePass123!",
    role="division",
    full_name="Jane Smith",
    email="jane.smith@highways.gov.in",
    division_office_id=5  # Chennai office
)
```

---

## Troubleshooting

### Issue: "Access denied for user 'root'@'localhost'"

**Solution:**
- Check your MySQL password
- Update the password in `.env` file
- Try: `mysql -u root -p` to test login

### Issue: "Database 'nh_management' doesn't exist"

**Solution:**
```sql
CREATE DATABASE nh_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

### Issue: "Table already exists"

**Solution:**
Drop and recreate the database:
```sql
DROP DATABASE nh_management;
CREATE DATABASE nh_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
-- Then run setup again
```

### Issue: Python module not found

**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: "Segment overlaps with existing segment"

**Solution:**
This is intentional validation! Check existing segments:
```sql
SELECT * FROM nh_segments WHERE nh_id = YOUR_NH_ID
ORDER BY start_chainage;
```
Adjust your chainage values to avoid overlaps.

---

## Next Steps

### 1. Customize for Your Needs
- Update division offices in `divisions` table
- Update NH list in `nh_master` table
- Modify road configurations as needed

### 2. Create Your Users
```sql
-- Create users for each division office
INSERT INTO users (username, password_hash, role, division_office_id, full_name, email)
VALUES ('your_username', '$2a$10$...', 'division', 1, 'Full Name', 'email@example.com');
```

### 3. Start Entering Data
- Central authority assigns segments to divisions
- Division users enter road configuration details
- Run validation queries regularly

### 4. Generate Reports
```sql
-- NH summary
CALL sp_get_nh_summary(nh_id);

-- Division workload
CALL sp_get_division_workload(division_office_id);

-- Use reporting views
SELECT * FROM vw_division_nh_summary;
SELECT * FROM vw_config_statistics;
```

### 5. Build the Frontend (Optional)
- Choose your framework (React, Vue, Angular)
- Use the Python API as backend
- Create forms for data entry
- Build dashboards and reports

---

## Important Notes

### Security
- **Change all default passwords immediately!**
- Use strong passwords (min 12 characters, mixed case, numbers, symbols)
- Enable SSL/TLS for production
- Set up regular backups
- Limit database access by IP

### Data Entry Guidelines
1. Central authority creates NH segments with proper chainage
2. Ensure no gaps or overlaps between segments
3. Division users add road configurations within their segments
4. Run validation queries before finalizing data
5. Document any issues in the remarks field

### Best Practices
- Back up database daily
- Run validation queries weekly
- Review audit logs regularly
- Update documentation as system evolves
- Train users properly before giving access

---

## Support & Documentation

### Documentation Files
- **README.md** - Complete system documentation
- **PROJECT_STRUCTURE.md** - Project organization
- **quick_start_guide.sql** - SQL testing guide
- **.env.example** - Configuration template

### Getting Help
- Check the README.md for detailed documentation
- Review SQL comments in database files
- Examine Python docstrings in nh_management.py
- Run validation queries to identify issues

### Contributing
If you find issues or want to suggest improvements:
1. Document the issue clearly
2. Provide example data/queries
3. Suggest solutions if possible

---

## License

Copyright © 2025 National Highways Authority
All rights reserved.

---

**Version:** 1.0  
**Last Updated:** November 4, 2025  
**Status:** Production Ready
