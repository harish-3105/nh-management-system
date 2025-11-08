-- National Highways Management System - Database Schema
-- Created: November 4, 2025

-- ============================================================================
-- 1. DIVISIONS TABLE
-- Stores the main divisions and their offices
-- ============================================================================
CREATE TABLE divisions (
    division_id INT PRIMARY KEY AUTO_INCREMENT,
    division_name VARCHAR(50) NOT NULL,
    office_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_division_office (division_name, office_name)
);

-- ============================================================================
-- 2. NH_MASTER TABLE
-- Master list of National Highways
-- ============================================================================
CREATE TABLE nh_master (
    nh_id INT PRIMARY KEY AUTO_INCREMENT,
    nh_number VARCHAR(20) NOT NULL UNIQUE,
    nh_name VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================================
-- 3. USERS TABLE
-- Stores user credentials and their roles
-- ============================================================================
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('central', 'division') NOT NULL DEFAULT 'division',
    division_office_id INT NULL,
    full_name VARCHAR(100),
    email VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (division_office_id) REFERENCES divisions(division_id) ON DELETE SET NULL
);

-- ============================================================================
-- 4. NH_SEGMENTS TABLE
-- Stores segments of NHs maintained by each division office
-- ============================================================================
CREATE TABLE nh_segments (
    segment_id INT PRIMARY KEY AUTO_INCREMENT,
    nh_id INT NOT NULL,
    division_office_id INT NOT NULL,
    start_chainage DECIMAL(10, 3) NOT NULL,
    end_chainage DECIMAL(10, 3) NOT NULL,
    segment_name VARCHAR(100),
    status ENUM('draft', 'active', 'archived') DEFAULT 'active',
    remarks TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (nh_id) REFERENCES nh_master(nh_id) ON DELETE CASCADE,
    FOREIGN KEY (division_office_id) REFERENCES divisions(division_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CHECK (end_chainage > start_chainage),
    UNIQUE KEY unique_nh_segment (nh_id, start_chainage, end_chainage)
);

-- ============================================================================
-- 5. ROAD_CONFIGURATIONS TABLE
-- Master list of road configuration types
-- ============================================================================
CREATE TABLE road_configurations (
    config_id INT PRIMARY KEY AUTO_INCREMENT,
    config_name VARCHAR(100) NOT NULL UNIQUE,
    config_code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    display_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================================================
-- 6. NH_ROAD_DETAILS TABLE
-- Stores road configuration details for each segment
-- ============================================================================
CREATE TABLE nh_road_details (
    detail_id INT PRIMARY KEY AUTO_INCREMENT,
    segment_id INT NOT NULL,
    config_id INT NOT NULL,
    start_chainage DECIMAL(10, 3) NOT NULL,
    end_chainage DECIMAL(10, 3) NOT NULL,
    length_km DECIMAL(10, 3) GENERATED ALWAYS AS (end_chainage - start_chainage) STORED,
    remarks TEXT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (segment_id) REFERENCES nh_segments(segment_id) ON DELETE CASCADE,
    FOREIGN KEY (config_id) REFERENCES road_configurations(config_id) ON DELETE RESTRICT,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CHECK (end_chainage > start_chainage)
);

-- ============================================================================
-- 7. AUDIT_LOG TABLE (Optional but recommended)
-- Tracks all changes for auditing purposes
-- ============================================================================
CREATE TABLE audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    table_name VARCHAR(50) NOT NULL,
    record_id INT NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_values JSON,
    new_values JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users table indexes
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_division ON users(division_office_id);

-- NH Segments indexes
CREATE INDEX idx_segments_nh ON nh_segments(nh_id);
CREATE INDEX idx_segments_division ON nh_segments(division_office_id);
CREATE INDEX idx_segments_chainage ON nh_segments(start_chainage, end_chainage);

-- NH Road Details indexes
CREATE INDEX idx_details_segment ON nh_road_details(segment_id);
CREATE INDEX idx_details_config ON nh_road_details(config_id);
CREATE INDEX idx_details_chainage ON nh_road_details(start_chainage, end_chainage);

-- Audit log indexes
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_table ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_created ON audit_log(created_at);
