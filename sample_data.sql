-- Sample Data for National Highways Management System
-- This file contains initial setup data

-- ============================================================================
-- 1. INSERT DIVISIONS AND OFFICES
-- ============================================================================
INSERT INTO divisions (division_name, office_name) VALUES
-- Madurai Division
('Madurai', 'Tirunelveli'),
('Madurai', 'Madurai'),
('Madurai', 'Trichy'),

-- Chennai Division
('Chennai', 'Villupuram'),
('Chennai', 'Chennai'),
('Chennai', 'Vellore'),

-- Salem Division
('Salem', 'Gobi'),
('Salem', 'Salem'),
('Salem', 'Coimbatore');

-- ============================================================================
-- 2. INSERT NATIONAL HIGHWAYS
-- ============================================================================
INSERT INTO nh_master (nh_number, nh_name, description) VALUES
('NH7', 'National Highway 7', 'Connects Varanasi to Kanyakumari'),
('NH8', 'National Highway 8', 'Delhi to Mumbai'),
('NH44', 'National Highway 44', 'Srinagar to Kanyakumari'),
('NH45', 'National Highway 45', 'Chennai to Theni'),
('NH47', 'National Highway 47', 'Salem to Kochi'),
('NH48', 'National Highway 48', 'Delhi to Chennai'),
('NH67', 'National Highway 67', 'Nagapattinam to Coimbatore'),
('NH79', 'National Highway 79', 'Pulgaon to Madurai'),
('NH81', 'National Highway 81', 'Rameshwaram to Mizoram'),
('NH83', 'National Highway 83', 'Trichy to Thanjavur'),
('NH138', 'National Highway 138', 'Salem to Namakkal'),
('NH209', 'National Highway 209', 'Madurai to Ramanathapuram'),
('NH381', 'National Highway 381', 'Vellore to Krishnagiri'),
('NH544', 'National Highway 544', 'Salem to Coimbatore'),
('NH716', 'National Highway 716', 'Madurai to Dindigul'),
('NH948', 'National Highway 948', 'Chennai to Tiruvallur');

-- ============================================================================
-- 3. INSERT ROAD CONFIGURATIONS
-- ============================================================================
INSERT INTO road_configurations (config_name, config_code, description, display_order) VALUES
('Two Lanes', '2L', 'Standard two-lane road', 1),
('Two Lanes with Paved Shoulder', '2L-PS', 'Two lanes with paved shoulders for additional safety', 2),
('Four Lanes', '4L', 'Four-lane divided highway', 3),
('Four Lanes with Paved Shoulder', '4L-PS', 'Four lanes with paved shoulders', 4),
('Six Lanes', '6L', 'Six-lane expressway', 5),
('Single Lane', '1L', 'Single lane road', 6);

-- ============================================================================
-- 4. INSERT USERS
-- ============================================================================
-- Password: 'admin123' (hashed - in production use bcrypt or similar)
INSERT INTO users (username, password_hash, role, division_office_id, full_name, email) VALUES
-- Central Authority Users
('central_admin', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'central', NULL, 'Central Administrator', 'central@highways.gov.in'),
('central_viewer', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'central', NULL, 'Central Viewer', 'viewer@highways.gov.in'),

-- Madurai Division Users
('madurai_tirunelveli', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 1, 'Tirunelveli Office Admin', 'tirunelveli@highways.gov.in'),
('madurai_office', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 2, 'Madurai Office Admin', 'madurai@highways.gov.in'),
('madurai_trichy', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 3, 'Trichy Office Admin', 'trichy@highways.gov.in'),

-- Chennai Division Users
('chennai_villupuram', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 4, 'Villupuram Office Admin', 'villupuram@highways.gov.in'),
('chennai_office', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 5, 'Chennai Office Admin', 'chennai@highways.gov.in'),
('chennai_vellore', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 6, 'Vellore Office Admin', 'vellore@highways.gov.in'),

-- Salem Division Users
('salem_gobi', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 7, 'Gobi Office Admin', 'gobi@highways.gov.in'),
('salem_office', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 8, 'Salem Office Admin', 'salem@highways.gov.in'),
('salem_coimbatore', '$2a$10$XqjKWdLsxXcRRJFY/B3zY.t1vV1YXf3b0N8Y.YxYvZY0x1QYzY', 'division', 9, 'Coimbatore Office Admin', 'coimbatore@highways.gov.in');

-- ============================================================================
-- 5. INSERT SAMPLE NH SEGMENTS
-- ============================================================================
-- NH44 segments (distributed across divisions)
INSERT INTO nh_segments (nh_id, division_office_id, start_chainage, end_chainage, segment_name, created_by) VALUES
-- Chennai Division - NH44
(3, 5, 0.000, 85.500, 'NH44 Chennai to Chengalpattu', 7),
(3, 4, 85.500, 142.300, 'NH44 Chengalpattu to Villupuram', 6),

-- Madurai Division - NH44
(3, 3, 142.300, 198.750, 'NH44 Villupuram to Trichy', 5),
(3, 2, 198.750, 267.800, 'NH44 Trichy to Madurai', 4),
(3, 1, 267.800, 321.400, 'NH44 Madurai to Tirunelveli', 3);

-- NH45 segments
INSERT INTO nh_segments (nh_id, division_office_id, start_chainage, end_chainage, segment_name, created_by) VALUES
(4, 5, 0.000, 45.200, 'NH45 Chennai to Chengalpattu', 7),
(4, 3, 45.200, 105.600, 'NH45 Chengalpattu to Trichy', 5),
(4, 2, 105.600, 142.800, 'NH45 Trichy to Madurai', 4);

-- NH47 segments (Salem Division)
INSERT INTO nh_segments (nh_id, division_office_id, start_chainage, end_chainage, segment_name, created_by) VALUES
(5, 8, 0.000, 52.300, 'NH47 Salem to Namakkal', 10),
(5, 9, 52.300, 118.700, 'NH47 Namakkal to Coimbatore', 11),
(5, 9, 118.700, 156.200, 'NH47 Coimbatore to Kerala Border', 11);

-- ============================================================================
-- 6. INSERT SAMPLE ROAD CONFIGURATIONS FOR SEGMENTS
-- ============================================================================
-- NH44 Chennai to Chengalpattu (segment_id = 1)
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by) VALUES
(1, 3, 0.000, 25.000, 'Four lanes from Chennai city', 7),
(1, 4, 25.000, 65.500, 'Four lanes with PS - highway section', 7),
(1, 3, 65.500, 85.500, 'Four lanes approaching Chengalpattu', 7);

-- NH44 Chengalpattu to Villupuram (segment_id = 2)
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by) VALUES
(2, 2, 85.500, 120.300, 'Two lanes with PS', 6),
(2, 1, 120.300, 142.300, 'Two lanes standard', 6);

-- NH44 Villupuram to Trichy (segment_id = 3)
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by) VALUES
(3, 2, 142.300, 165.000, 'Two lanes with PS', 5),
(3, 3, 165.000, 198.750, 'Four lanes - upgraded section', 5);

-- NH44 Trichy to Madurai (segment_id = 4)
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by) VALUES
(4, 4, 198.750, 235.000, 'Four lanes with PS - major highway', 4),
(4, 3, 235.000, 267.800, 'Four lanes', 4);

-- NH44 Madurai to Tirunelveli (segment_id = 5)
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by) VALUES
(5, 2, 267.800, 295.600, 'Two lanes with PS', 3),
(5, 1, 295.600, 321.400, 'Two lanes', 3);

-- NH45 segments road details
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by) VALUES
(6, 4, 0.000, 35.200, 'Four lanes with PS from Chennai', 7),
(6, 2, 35.200, 45.200, 'Two lanes with PS', 7),
(7, 2, 45.200, 85.400, 'Two lanes with PS', 5),
(7, 1, 85.400, 105.600, 'Two lanes', 5),
(8, 1, 105.600, 142.800, 'Two lanes', 4);

-- NH47 segments road details
INSERT INTO nh_road_details (segment_id, config_id, start_chainage, end_chainage, remarks, created_by) VALUES
(9, 3, 0.000, 42.300, 'Four lanes from Salem', 10),
(9, 2, 42.300, 52.300, 'Two lanes with PS', 10),
(10, 3, 52.300, 98.700, 'Four lanes - major route', 11),
(10, 2, 98.700, 118.700, 'Two lanes with PS', 11),
(11, 2, 118.700, 156.200, 'Two lanes with PS to border', 11);
