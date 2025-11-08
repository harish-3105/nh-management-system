-- Fix report views to calculate length from chainages instead of using non-existent length_km column
-- Run this script to fix the "undefined" length and percentage issues in reports

-- Drop existing views
DROP VIEW IF EXISTS vw_config_statistics;
DROP VIEW IF EXISTS vw_nh_complete_overview;
DROP VIEW IF EXISTS vw_division_nh_summary;
DROP VIEW IF EXISTS vw_nh_config_summary;

-- 1. NH Configuration Summary (fixed to calculate length)
CREATE VIEW vw_nh_config_summary AS
SELECT 
    nm.nh_number,
    nm.nh_name,
    rc.config_name,
    ROUND(SUM(rd.end_chainage - rd.start_chainage), 3) AS total_length,
    COUNT(rd.detail_id) AS number_of_sections
FROM nh_master nm
JOIN nh_segments ns ON nm.nh_id = ns.nh_id
JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
JOIN road_configurations rc ON rd.config_id = rc.config_id
GROUP BY nm.nh_number, nm.nh_name, rc.config_name
ORDER BY nm.nh_number, rc.display_order;

-- 2. Division-wise NH summary (already correct - uses segment chainages)
CREATE VIEW vw_division_nh_summary AS
SELECT 
    d.division_name,
    d.office_name,
    nm.nh_number,
    COUNT(ns.segment_id) AS segment_count,
    COUNT(DISTINCT nm.nh_id) AS nh_count,
    ROUND(SUM(ns.end_chainage - ns.start_chainage), 3) AS total_length
FROM divisions d
JOIN nh_segments ns ON d.division_id = ns.division_office_id
JOIN nh_master nm ON ns.nh_id = nm.nh_id
GROUP BY d.division_name, d.office_name, nm.nh_number
ORDER BY d.division_name, d.office_name, nm.nh_number;

-- 3. Complete NH overview (fixed to calculate length)
CREATE VIEW vw_nh_complete_overview AS
SELECT 
    nm.nh_number,
    nm.nh_name,
    d.division_name,
    d.office_name,
    ns.segment_name,
    ns.start_chainage AS segment_start,
    ns.end_chainage AS segment_end,
    ROUND(ns.end_chainage - ns.start_chainage, 3) AS segment_length_km,
    rc.config_name,
    rd.start_chainage AS config_start,
    rd.end_chainage AS config_end,
    ROUND(rd.end_chainage - rd.start_chainage, 3) AS config_length_km,
    rd.remarks
FROM nh_master nm
JOIN nh_segments ns ON nm.nh_id = ns.nh_id
JOIN divisions d ON ns.division_office_id = d.division_id
LEFT JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
LEFT JOIN road_configurations rc ON rd.config_id = rc.config_id
ORDER BY nm.nh_number, ns.start_chainage, rd.start_chainage;

-- 4. Configuration-wise statistics (fixed to calculate length)
CREATE VIEW vw_config_statistics AS
SELECT 
    rc.config_name,
    rc.config_code,
    rc.display_order,
    COUNT(DISTINCT nm.nh_id) AS num_highways,
    COUNT(rd.detail_id) AS num_sections,
    ROUND(SUM(rd.end_chainage - rd.start_chainage), 3) AS total_length,
    ROUND(AVG(rd.end_chainage - rd.start_chainage), 3) AS avg_section_length,
    ROUND(MIN(rd.end_chainage - rd.start_chainage), 3) AS min_section_length,
    ROUND(MAX(rd.end_chainage - rd.start_chainage), 3) AS max_section_length
FROM road_configurations rc
LEFT JOIN nh_road_details rd ON rc.config_id = rd.config_id
LEFT JOIN nh_segments ns ON rd.segment_id = ns.segment_id
LEFT JOIN nh_master nm ON ns.nh_id = nm.nh_id
GROUP BY rc.config_name, rc.config_code, rc.display_order
ORDER BY rc.display_order;

-- Verify the views are working
SELECT 'vw_nh_config_summary' AS view_name, COUNT(*) AS row_count FROM vw_nh_config_summary
UNION ALL
SELECT 'vw_division_nh_summary', COUNT(*) FROM vw_division_nh_summary
UNION ALL
SELECT 'vw_config_statistics', COUNT(*) FROM vw_config_statistics
UNION ALL
SELECT 'vw_nh_complete_overview', COUNT(*) FROM vw_nh_complete_overview;
