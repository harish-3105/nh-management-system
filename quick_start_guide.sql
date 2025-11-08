-- Quick Start Guide - National Highways Management System
-- Execute these queries in sequence to set up and test the system

-- ============================================================================
-- STEP 1: CREATE DATABASE
-- ============================================================================
CREATE DATABASE IF NOT EXISTS nh_management 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE nh_management;

-- ============================================================================
-- STEP 2: VERIFY INSTALLATION
-- ============================================================================

-- Check all tables are created
SHOW TABLES;
-- Expected: 7 tables (divisions, nh_master, users, nh_segments, 
--                     road_configurations, nh_road_details, audit_log)

-- Check triggers
SHOW TRIGGERS;
-- Expected: 12+ triggers for validation and auditing

-- Check views
SHOW FULL TABLES WHERE table_type = 'VIEW';
-- Expected: Multiple views for reporting

-- Check stored procedures
SHOW PROCEDURE STATUS WHERE db = 'nh_management';

-- ============================================================================
-- STEP 3: VERIFY SAMPLE DATA
-- ============================================================================

-- Count records in each table
SELECT 'Divisions' AS table_name, COUNT(*) AS count FROM divisions
UNION ALL
SELECT 'NH Master', COUNT(*) FROM nh_master
UNION ALL
SELECT 'Users', COUNT(*) FROM users
UNION ALL
SELECT 'Road Configurations', COUNT(*) FROM road_configurations
UNION ALL
SELECT 'NH Segments', COUNT(*) FROM nh_segments
UNION ALL
SELECT 'NH Road Details', COUNT(*) FROM nh_road_details;

-- ============================================================================
-- STEP 4: TEST QUERIES - BASIC DATA RETRIEVAL
-- ============================================================================

-- Q1: List all divisions and their offices
SELECT division_name, office_name 
FROM divisions 
ORDER BY division_name, office_name;

-- Q2: List all National Highways
SELECT nh_number, nh_name 
FROM nh_master 
ORDER BY nh_number;

-- Q3: List all road configuration types
SELECT config_code, config_name, description 
FROM road_configurations 
ORDER BY display_order;

-- Q4: List all users by division
SELECT 
    u.username,
    u.full_name,
    u.role,
    d.division_name,
    d.office_name,
    u.is_active
FROM users u
LEFT JOIN divisions d ON u.division_office_id = d.division_id
ORDER BY u.role, d.division_name, d.office_name;

-- ============================================================================
-- STEP 5: TEST QUERIES - SEGMENTS AND CONFIGURATIONS
-- ============================================================================

-- Q5: View all segments for a specific NH (e.g., NH44)
SELECT 
    nm.nh_number,
    ns.segment_name,
    d.division_name,
    d.office_name,
    ns.start_chainage,
    ns.end_chainage,
    ROUND(ns.end_chainage - ns.start_chainage, 3) AS length_km,
    ns.status
FROM nh_segments ns
JOIN nh_master nm ON ns.nh_id = nm.nh_id
JOIN divisions d ON ns.division_office_id = d.division_id
WHERE nm.nh_number = 'NH44'
ORDER BY ns.start_chainage;

-- Q6: View complete road configuration for NH44
SELECT 
    nm.nh_number,
    d.division_name,
    d.office_name,
    ns.segment_name,
    ns.start_chainage AS seg_start,
    ns.end_chainage AS seg_end,
    rc.config_name,
    rd.start_chainage AS config_start,
    rd.end_chainage AS config_end,
    rd.length_km,
    rd.remarks
FROM nh_master nm
JOIN nh_segments ns ON nm.nh_id = ns.nh_id
JOIN divisions d ON ns.division_office_id = d.division_id
LEFT JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
LEFT JOIN road_configurations rc ON rd.config_id = rc.config_id
WHERE nm.nh_number = 'NH44'
ORDER BY ns.start_chainage, rd.start_chainage;

-- ============================================================================
-- STEP 6: TEST VALIDATION VIEWS
-- ============================================================================

-- V1: Check for overlapping segments (should be empty if data is valid)
SELECT * FROM vw_overlapping_segments;

-- V2: Check for overlapping configurations (should be empty if data is valid)
SELECT * FROM vw_overlapping_configurations;

-- V3: Check for out-of-bounds details (should be empty if data is valid)
SELECT * FROM vw_out_of_bounds_details;

-- ============================================================================
-- STEP 7: TEST REPORTING VIEWS
-- ============================================================================

-- R1: NH and Configuration Summary
SELECT * FROM vw_nh_config_summary 
WHERE nh_number = 'NH44'
ORDER BY nh_number, config_name;

-- R2: Division-wise NH Summary
SELECT * FROM vw_division_nh_summary 
WHERE division_name = 'Madurai'
ORDER BY division_name, office_name, nh_number;

-- R3: Configuration Statistics
SELECT * FROM vw_config_statistics
ORDER BY display_order;

-- R4: User Activity
SELECT * FROM vw_user_activity
ORDER BY role, division_name, office_name;

-- ============================================================================
-- STEP 8: TEST STORED PROCEDURES
-- ============================================================================

-- P1: Get NH Summary for NH44
CALL sp_get_nh_summary(3);  -- nh_id for NH44

-- P2: Validate NH Continuity for NH44
CALL sp_validate_nh_continuity(3);  -- Should show no issues

-- P3: Get Division Workload for Madurai office
CALL sp_get_division_workload(2);  -- division_id for Madurai

-- ============================================================================
-- STEP 9: TEST DATA INSERTION (Division User Perspective)
-- ============================================================================

-- Scenario: Madurai office adds a new segment detail
-- First, check assigned segments
SELECT 
    ns.segment_id,
    nm.nh_number,
    ns.segment_name,
    ns.start_chainage,
    ns.end_chainage
FROM nh_segments ns
JOIN nh_master nm ON ns.nh_id = nm.nh_id
WHERE ns.division_office_id = 2  -- Madurai office
ORDER BY nm.nh_number, ns.start_chainage;

-- Add a new road configuration detail (example)
-- Uncomment to test:
/*
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by)
VALUES (
    4,  -- segment_id (adjust based on your data)
    3,  -- config_id (Four Lanes)
    250.000,
    260.000,
    'Test configuration - urban bypass',
    4   -- user_id (madurai_office user)
);
*/

-- ============================================================================
-- STEP 10: TEST VALIDATION TRIGGERS
-- ============================================================================

-- Test 1: Try to insert overlapping segment (should fail)
-- Uncomment to test:
/*
INSERT INTO nh_segments (nh_id, division_office_id, start_chainage, end_chainage, segment_name, created_by)
VALUES (
    3,  -- NH44
    2,  -- Madurai office
    200.000,  -- Overlaps with existing segment
    250.000,
    'Test Overlap Segment',
    4
);
-- Expected: Error - "Segment overlaps with existing segment for this NH"
*/

-- Test 2: Try to insert road detail outside segment boundaries (should fail)
-- Uncomment to test:
/*
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by)
VALUES (
    4,  -- segment_id
    3,  -- config_id
    100.000,  -- Outside segment boundaries
    110.000,
    'Test Out of Bounds',
    4
);
-- Expected: Error - "Road detail chainage must be within segment boundaries"
*/

-- ============================================================================
-- STEP 11: USEFUL ANALYTICAL QUERIES
-- ============================================================================

-- A1: Total length by configuration type across all NHs
SELECT 
    rc.config_name,
    COUNT(DISTINCT nm.nh_id) AS num_highways,
    ROUND(SUM(rd.length_km), 3) AS total_length_km,
    ROUND(AVG(rd.length_km), 3) AS avg_section_length
FROM road_configurations rc
LEFT JOIN nh_road_details rd ON rc.config_id = rd.config_id
LEFT JOIN nh_segments ns ON rd.segment_id = ns.segment_id
LEFT JOIN nh_master nm ON ns.nh_id = nm.nh_id
GROUP BY rc.config_name
ORDER BY total_length_km DESC;

-- A2: Division workload comparison
SELECT 
    d.division_name,
    d.office_name,
    COUNT(DISTINCT ns.nh_id) AS num_highways,
    COUNT(ns.segment_id) AS num_segments,
    ROUND(SUM(ns.end_chainage - ns.start_chainage), 3) AS total_length_km,
    COUNT(rd.detail_id) AS num_configurations
FROM divisions d
LEFT JOIN nh_segments ns ON d.division_id = ns.division_office_id
LEFT JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
GROUP BY d.division_name, d.office_name
ORDER BY total_length_km DESC;

-- A3: NH completeness check
WITH nh_coverage AS (
    SELECT 
        nm.nh_id,
        nm.nh_number,
        COUNT(ns.segment_id) AS num_segments,
        ROUND(SUM(ns.end_chainage - ns.start_chainage), 3) AS total_covered_length,
        ROUND(SUM(rd.length_km), 3) AS total_configured_length,
        COUNT(rd.detail_id) AS num_configurations
    FROM nh_master nm
    LEFT JOIN nh_segments ns ON nm.nh_id = ns.nh_id
    LEFT JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
    GROUP BY nm.nh_id, nm.nh_number
)
SELECT 
    nh_number,
    num_segments,
    total_covered_length,
    total_configured_length,
    num_configurations,
    CASE 
        WHEN total_configured_length IS NULL THEN 'No Data'
        WHEN total_configured_length < total_covered_length THEN 'Partial Coverage'
        WHEN total_configured_length = total_covered_length THEN 'Complete Coverage'
        ELSE 'Over Coverage (Check for overlaps)'
    END AS coverage_status
FROM nh_coverage
ORDER BY nh_number;

-- ============================================================================
-- STEP 12: AUDIT LOG REVIEW
-- ============================================================================

-- Recent audit entries
SELECT 
    al.log_id,
    u.username,
    al.table_name,
    al.action,
    al.record_id,
    al.created_at
FROM audit_log al
LEFT JOIN users u ON al.user_id = u.user_id
ORDER BY al.created_at DESC
LIMIT 20;

-- Audit summary by user
SELECT 
    u.username,
    u.full_name,
    al.table_name,
    al.action,
    COUNT(*) AS count
FROM audit_log al
JOIN users u ON al.user_id = u.user_id
GROUP BY u.username, u.full_name, al.table_name, al.action
ORDER BY u.username, al.table_name, al.action;

-- ============================================================================
-- STEP 13: PERFORMANCE MONITORING
-- ============================================================================

-- Table sizes
SELECT 
    table_name,
    table_rows,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
FROM information_schema.TABLES
WHERE table_schema = 'nh_management'
ORDER BY (data_length + index_length) DESC;

-- Index usage (requires performance schema)
-- This helps identify unused indexes
SELECT 
    table_schema,
    table_name,
    index_name,
    rows_read
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE table_schema = 'nh_management'
ORDER BY rows_read DESC;

-- ============================================================================
-- SUMMARY
-- ============================================================================
/*
This quick start guide covers:
1. Database setup verification
2. Sample data validation
3. Basic queries for common use cases
4. Validation and integrity checks
5. Reporting views and procedures
6. Testing data insertion and triggers
7. Analytical queries for insights
8. Audit trail review
9. Performance monitoring

Next steps:
- Develop application layer (web/mobile)
- Implement authentication and authorization
- Create user-friendly forms for data entry
- Build dashboards and reports
- Set up automated backups
- Configure monitoring and alerts
*/
