# National Highways Management System
## Database Design & System Documentation

### Version 1.0 | November 4, 2025

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Database Architecture](#database-architecture)
3. [Table Descriptions](#table-descriptions)
4. [Data Flow](#data-flow)
5. [Security & Access Control](#security--access-control)
6. [Data Integrity & Validation](#data-integrity--validation)
7. [Installation Guide](#installation-guide)
8. [Usage Examples](#usage-examples)
9. [API Endpoints (Suggested)](#api-endpoints-suggested)
10. [Maintenance & Monitoring](#maintenance--monitoring)

---

## System Overview

### Purpose
This system manages National Highway (NH) data across three main divisions (Madurai, Chennai, Salem) with multiple division offices. It maintains comprehensive information about highway segments, road configurations, and ensures continuity of chainage across divisions.

### Key Features
- **Centralized Database**: Single source of truth for all NH data
- **Multi-Division Support**: 3 main divisions with 9 division offices
- **16 National Highways**: Complete coverage of all NHs
- **Role-Based Access**: Central authority and division office users
- **Chainage Continuity**: Automatic validation to prevent gaps and overlaps
- **Configuration Tracking**: Four main road types (2L, 2L-PS, 4L, 4L-PS)
- **Audit Trail**: Complete history of all changes
- **Real-time Validation**: Database triggers prevent invalid data entry

### Divisions & Offices
| Division | Offices |
|----------|---------|
| **Madurai** | Tirunelveli, Madurai, Trichy |
| **Chennai** | Villupuram, Chennai, Vellore |
| **Salem** | Gobi, Salem, Coimbatore |

### Road Configuration Types
1. **Two Lanes (2L)**: Standard two-lane road
2. **Two Lanes with Paved Shoulder (2L-PS)**: Enhanced two-lane with safety shoulders
3. **Four Lanes (4L)**: Divided four-lane highway
4. **Four Lanes with Paved Shoulder (4L-PS)**: Premium four-lane configuration
5. **Six Lanes (6L)**: Expressway standard
6. **Single Lane (1L)**: Rural road standard

---

## Database Architecture

### Entity Relationship Diagram (ERD)

```
┌─────────────┐
│  divisions  │
└──────┬──────┘
       │
       │ 1:N
       │
┌──────▼────────┐         ┌──────────────┐
│     users     │         │  nh_master   │
└───────────────┘         └──────┬───────┘
                                 │
                                 │ 1:N
                                 │
                          ┌──────▼──────────┐
                          │  nh_segments    │◄────┐
                          └──────┬──────────┘     │
                                 │                 │ FK
                                 │ 1:N             │
                                 │                 │
                    ┌────────────▼──────────┐     │
                    │  nh_road_details      │─────┘
                    └───────┬───────────────┘
                            │
                            │ N:1
                            │
                 ┌──────────▼────────────┐
                 │ road_configurations   │
                 └───────────────────────┘

                    ┌──────────────┐
                    │  audit_log   │
                    └──────────────┘
```

### Database Schema Summary

| Table | Primary Key | Foreign Keys | Purpose |
|-------|-------------|--------------|---------|
| **divisions** | division_id | - | Stores division and office information |
| **nh_master** | nh_id | - | Master list of all National Highways |
| **users** | user_id | division_office_id | User authentication and authorization |
| **nh_segments** | segment_id | nh_id, division_office_id | Highway segments by division |
| **road_configurations** | config_id | - | Types of road configurations |
| **nh_road_details** | detail_id | segment_id, config_id | Configuration details for segments |
| **audit_log** | log_id | user_id | Complete audit trail |

---

## Table Descriptions

### 1. divisions
Stores information about divisions and their offices.

**Columns:**
- `division_id` (PK): Unique identifier
- `division_name`: Name of the division (Madurai, Chennai, Salem)
- `office_name`: Name of the division office
- `created_at`, `updated_at`: Timestamps

**Constraints:**
- Unique combination of (division_name, office_name)

### 2. nh_master
Master table for all National Highways.

**Columns:**
- `nh_id` (PK): Unique identifier
- `nh_number`: NH designation (e.g., 'NH44', 'NH45')
- `nh_name`: Full name of the highway
- `description`: Additional details
- `created_at`, `updated_at`: Timestamps

**Constraints:**
- Unique nh_number

### 3. users
User authentication and role management.

**Columns:**
- `user_id` (PK): Unique identifier
- `username`: Login username (unique)
- `password_hash`: Encrypted password (bcrypt recommended)
- `role`: 'central' or 'division'
- `division_office_id` (FK): Links to divisions (NULL for central users)
- `full_name`, `email`: User details
- `is_active`: Account status
- `last_login`: Last login timestamp
- `created_at`, `updated_at`: Timestamps

**Constraints:**
- Central users must have NULL division_office_id
- Division users must have valid division_office_id

### 4. nh_segments
Highway segments assigned to division offices.

**Columns:**
- `segment_id` (PK): Unique identifier
- `nh_id` (FK): Reference to nh_master
- `division_office_id` (FK): Responsible division office
- `start_chainage`: Starting chainage (km)
- `end_chainage`: Ending chainage (km)
- `segment_name`: Descriptive name
- `status`: 'draft', 'active', or 'archived'
- `remarks`: Additional notes
- `created_by` (FK): User who created the segment
- `created_at`, `updated_at`: Timestamps

**Constraints:**
- end_chainage > start_chainage
- Unique combination of (nh_id, start_chainage, end_chainage)
- No overlapping segments for the same NH (enforced by trigger)

### 5. road_configurations
Master list of road configuration types.

**Columns:**
- `config_id` (PK): Unique identifier
- `config_name`: Full name (e.g., 'Four Lanes with Paved Shoulder')
- `config_code`: Short code (e.g., '4L-PS')
- `description`: Additional details
- `display_order`: Ordering for UI display
- `is_active`: Configuration status
- `created_at`, `updated_at`: Timestamps

**Constraints:**
- Unique config_name and config_code

### 6. nh_road_details
Detailed road configuration for each segment.

**Columns:**
- `detail_id` (PK): Unique identifier
- `segment_id` (FK): Reference to nh_segments
- `config_id` (FK): Reference to road_configurations
- `start_chainage`: Starting chainage within segment
- `end_chainage`: Ending chainage within segment
- `length_km`: Auto-calculated (end - start)
- `remarks`: Additional notes
- `created_by` (FK): User who created the detail
- `created_at`, `updated_at`: Timestamps

**Constraints:**
- end_chainage > start_chainage
- Chainage must be within parent segment boundaries (enforced by trigger)
- No overlapping configurations within same segment (enforced by trigger)

### 7. audit_log
Complete audit trail of all changes.

**Columns:**
- `log_id` (PK): Unique identifier
- `user_id` (FK): User who made the change
- `table_name`: Name of affected table
- `record_id`: ID of affected record
- `action`: 'INSERT', 'UPDATE', or 'DELETE'
- `old_values`: JSON of old values
- `new_values`: JSON of new values
- `ip_address`: Client IP (optional)
- `created_at`: Timestamp

---

## Data Flow

### 1. Initial Setup (Central Authority)
```
1. Create Divisions → divisions table
2. Create NH Master → nh_master table
3. Create Road Configurations → road_configurations table
4. Create Users → users table
5. Assign Segments to Divisions → nh_segments table
```

### 2. Division Office Data Entry
```
1. User Login → Authenticate against users table
2. View Assigned Segments → Filter by division_office_id
3. Enter Road Configurations → nh_road_details table
   - Select segment
   - Choose configuration type
   - Enter start/end chainage
   - Validate against segment boundaries
   - Check for overlaps
4. Save → Trigger validation → Audit log
```

### 3. Reporting & Analysis (Central Authority)
```
1. Query all segments → Join tables
2. Check continuity → Run validation queries
3. Generate reports → Use views and stored procedures
4. Export data → Standard SQL queries
```

---

## Security & Access Control

### Authentication
- Password hashing using bcrypt (or similar)
- Session management (implement in application layer)
- Multi-factor authentication (recommended for production)

### Authorization

#### Central Authority Users
**Permissions:**
- Create, read, update, delete all records
- Manage divisions and offices
- Create and manage all NH segments
- View all data across divisions
- Run validation and integrity checks
- Access audit logs
- Manage user accounts

#### Division Office Users
**Permissions:**
- Read all NH master data
- Read their assigned segments only
- Create, update, delete road configurations for assigned segments
- View their division's data only
- Cannot modify segment boundaries (assigned by central authority)
- Cannot access other divisions' data

### Implementation Example (SQL)
```sql
-- For division users, filter queries by their division office
SELECT * FROM nh_segments 
WHERE division_office_id = @current_user_division_id;

-- For central users, no filter needed
SELECT * FROM nh_segments;
```

---

## Data Integrity & Validation

### Database-Level Validation

#### 1. CHECK Constraints
- `end_chainage > start_chainage` (segments and details)
- Role-based division_office_id validation
- Valid status enums

#### 2. UNIQUE Constraints
- No duplicate usernames
- No duplicate nh_numbers
- No duplicate segment boundaries for same NH
- No duplicate configuration names/codes

#### 3. FOREIGN KEY Constraints
- Cascading deletes where appropriate
- Prevent orphaned records

#### 4. Database Triggers
- **Overlap Prevention**: Prevents overlapping segments for same NH
- **Boundary Validation**: Ensures road details stay within segment boundaries
- **Configuration Overlap**: Prevents overlapping configurations in same segment
- **Audit Logging**: Automatic tracking of all changes

### Application-Level Validation

#### 1. Continuity Checks
```sql
-- Run this query to check for gaps in NH coverage
CALL sp_validate_nh_continuity(@nh_id);
```

#### 2. Coverage Analysis
```sql
-- Check segment coverage by configurations
SELECT * FROM vw_overlapping_configurations;
```

#### 3. Data Quality Reports
- Use validation views to identify issues
- Schedule regular integrity checks
- Alert system for data anomalies

---

## Installation Guide

### Prerequisites
- MySQL 8.0+ or MariaDB 10.5+
- Database administration access
- Backup capabilities

### Step-by-Step Installation

#### Step 1: Create Database
```sql
CREATE DATABASE nh_management CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nh_management;
```

#### Step 2: Create Schema
```bash
mysql -u root -p nh_management < database_schema.sql
```

#### Step 3: Create Triggers
```bash
mysql -u root -p nh_management < triggers.sql
```

#### Step 4: Create Views and Procedures
```bash
mysql -u root -p nh_management < validation_queries.sql
```

#### Step 5: Load Sample Data (Optional)
```bash
mysql -u root -p nh_management < sample_data.sql
```

#### Step 6: Verify Installation
```sql
-- Check all tables created
SHOW TABLES;

-- Check all triggers
SHOW TRIGGERS;

-- Check all views
SHOW FULL TABLES WHERE table_type = 'VIEW';

-- Check all procedures
SHOW PROCEDURE STATUS WHERE db = 'nh_management';
```

### Configuration
Update the following in your application config:
```properties
db.host=localhost
db.port=3306
db.name=nh_management
db.username=nh_user
db.password=<secure_password>
db.pool.size=10
```

---

## Usage Examples

### Example 1: Create a New Division Office User
```sql
INSERT INTO users (username, password_hash, role, division_office_id, full_name, email)
VALUES (
    'madurai_user1',
    '$2a$10$...',  -- bcrypt hash of password
    'division',
    2,  -- Madurai office
    'Rajesh Kumar',
    'rajesh.kumar@highways.gov.in'
);
```

### Example 2: Assign a Segment to Division Office
```sql
INSERT INTO nh_segments (nh_id, division_office_id, start_chainage, end_chainage, segment_name, created_by)
VALUES (
    3,  -- NH44
    2,  -- Madurai office
    150.000,
    225.500,
    'NH44 Trichy to Madurai Section',
    4  -- user_id of creator
);
```

### Example 3: Add Road Configuration Details
```sql
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by)
VALUES 
    (10, 4, 150.000, 180.000, 'Four lanes with PS - urban section', 4),
    (10, 3, 180.000, 210.500, 'Four lanes - highway section', 4),
    (10, 2, 210.500, 225.500, 'Two lanes with PS - rural section', 4);
```

### Example 4: Query Division's Workload
```sql
CALL sp_get_division_workload(2);  -- Madurai office
```

### Example 5: Get NH Summary Report
```sql
CALL sp_get_nh_summary(3);  -- NH44
```

### Example 6: Check for Data Issues
```sql
-- Check for overlapping segments
SELECT * FROM vw_overlapping_segments;

-- Check for gaps in coverage
SELECT * FROM vw_overlapping_configurations;

-- Check segment coverage
SELECT * FROM vw_out_of_bounds_details;
```

---

## API Endpoints (Suggested)

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/session` - Get current session

### Divisions
- `GET /api/divisions` - List all divisions and offices
- `GET /api/divisions/{id}` - Get division details

### National Highways
- `GET /api/nh` - List all NHs
- `GET /api/nh/{id}` - Get NH details
- `GET /api/nh/{id}/segments` - Get all segments for NH
- `GET /api/nh/{id}/summary` - Get NH summary report

### Segments (Division Users)
- `GET /api/segments` - List assigned segments (filtered by user)
- `GET /api/segments/{id}` - Get segment details
- `POST /api/segments` - Create segment (central only)
- `PUT /api/segments/{id}` - Update segment (central only)
- `DELETE /api/segments/{id}` - Delete segment (central only)

### Road Details (Division Users)
- `GET /api/segments/{id}/details` - Get road configurations for segment
- `POST /api/segments/{id}/details` - Add road configuration
- `PUT /api/details/{id}` - Update road configuration
- `DELETE /api/details/{id}` - Delete road configuration

### Reports (Central Authority)
- `GET /api/reports/division-summary` - Division-wise summary
- `GET /api/reports/config-statistics` - Configuration statistics
- `GET /api/reports/validation` - Data validation report
- `GET /api/reports/audit-log` - Audit trail

### Validation
- `POST /api/validate/continuity/{nh_id}` - Check NH continuity
- `GET /api/validate/overlaps` - Find overlapping segments
- `GET /api/validate/gaps` - Find gaps in coverage

---

## Maintenance & Monitoring

### Regular Maintenance Tasks

#### Daily
- Monitor database connections and performance
- Check for failed validation triggers
- Review audit log for suspicious activity

#### Weekly
- Run validation queries to check data integrity
- Check for gaps and overlaps in NH coverage
- Review user activity and access patterns

#### Monthly
- Database backup and verification
- Archive old audit logs
- Performance tuning and index optimization
- User account review and cleanup

### Backup Strategy
```bash
# Full backup
mysqldump -u root -p nh_management > backup_$(date +%Y%m%d).sql

# Backup with compression
mysqldump -u root -p nh_management | gzip > backup_$(date +%Y%m%d).sql.gz

# Automated daily backup (cron job)
0 2 * * * /path/to/backup_script.sh
```

### Monitoring Queries
```sql
-- Check database size
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables
WHERE table_schema = 'nh_management';

-- Check table row counts
SELECT 
    table_name,
    table_rows
FROM information_schema.tables
WHERE table_schema = 'nh_management'
ORDER BY table_rows DESC;

-- Recent audit activity
SELECT 
    DATE(created_at) AS date,
    action,
    COUNT(*) AS count
FROM audit_log
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(created_at), action
ORDER BY date DESC, action;
```

### Performance Optimization
```sql
-- Analyze and optimize tables
ANALYZE TABLE nh_segments, nh_road_details;
OPTIMIZE TABLE audit_log;

-- Check slow queries (enable slow query log)
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Overlapping Segments Error
**Error Message:** "Segment overlaps with existing segment for this NH"
**Solution:** 
- Check existing segments for the NH
- Adjust chainage values to avoid overlap
- Run validation query: `SELECT * FROM vw_overlapping_segments;`

#### Issue 2: Chainage Out of Bounds
**Error Message:** "Road detail chainage must be within segment boundaries"
**Solution:**
- Verify segment boundaries
- Ensure road detail chainage is within segment range
- Check: `SELECT * FROM vw_out_of_bounds_details;`

#### Issue 3: Login Issues
**Solution:**
- Verify user exists and is active
- Check password hash
- Verify division_office_id for division users

### Contact & Support
- Technical Support: support@highways.gov.in
- Database Admin: dba@highways.gov.in
- Documentation: https://docs.highways.gov.in

---

## Appendix

### A. Chainage System
Chainage represents the distance in kilometers along the highway from a reference point (usually the start of the highway). It's measured as a decimal value (e.g., 125.750 km).

### B. Glossary
- **NH**: National Highway
- **Chainage**: Distance measurement along highway
- **PS**: Paved Shoulder
- **Segment**: Continuous stretch of highway under one division office
- **Configuration**: Type of road construction (lanes, shoulders, etc.)

### C. References
- Indian Roads Congress (IRC) Standards
- Ministry of Road Transport and Highways Guidelines
- National Highways Authority of India (NHAI) Documentation

---

**Document Version:** 1.0  
**Last Updated:** November 4, 2025  
**Authors:** Database Design Team  
**Review Date:** February 4, 2026
