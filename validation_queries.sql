-- Validation and Utility Queries for NH Management System

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- 1. Check for overlapping segments within the same NH
-- This identifies if two division offices have overlapping chainages for the same NH
CREATE VIEW vw_overlapping_segments AS
SELECT 
    s1.nh_id,
    nm.nh_number,
    s1.segment_id AS segment1_id,
    s2.segment_id AS segment2_id,
    s1.division_office_id AS division1,
    s2.division_office_id AS division2,
    s1.start_chainage AS s1_start,
    s1.end_chainage AS s1_end,
    s2.start_chainage AS s2_start,
    s2.end_chainage AS s2_end
FROM nh_segments s1
JOIN nh_segments s2 ON s1.nh_id = s2.nh_id AND s1.segment_id < s2.segment_id
JOIN nh_master nm ON s1.nh_id = nm.nh_id
WHERE s1.start_chainage < s2.end_chainage 
  AND s1.end_chainage > s2.start_chainage;

-- 2. Check for gaps in NH coverage
-- Identifies gaps in chainage coverage for each NH
WITH segment_boundaries AS (
    SELECT 
        nh_id,
        segment_id,
        start_chainage,
        end_chainage,
        LAG(end_chainage) OVER (PARTITION BY nh_id ORDER BY start_chainage) AS prev_end
    FROM nh_segments
)
SELECT 
    sb.nh_id,
    nm.nh_number,
    sb.prev_end AS gap_start,
    sb.start_chainage AS gap_end,
    (sb.start_chainage - sb.prev_end) AS gap_length_km
FROM segment_boundaries sb
JOIN nh_master nm ON sb.nh_id = nm.nh_id
WHERE sb.prev_end IS NOT NULL 
  AND sb.start_chainage > sb.prev_end
ORDER BY sb.nh_id, gap_start;

-- 3. Check for overlapping road configurations within segments
CREATE VIEW vw_overlapping_configurations AS
SELECT 
    r1.segment_id,
    ns.nh_id,
    nm.nh_number,
    r1.detail_id AS detail1_id,
    r2.detail_id AS detail2_id,
    r1.config_id AS config1,
    r2.config_id AS config2,
    r1.start_chainage AS r1_start,
    r1.end_chainage AS r1_end,
    r2.start_chainage AS r2_start,
    r2.end_chainage AS r2_end
FROM nh_road_details r1
JOIN nh_road_details r2 ON r1.segment_id = r2.segment_id AND r1.detail_id < r2.detail_id
JOIN nh_segments ns ON r1.segment_id = ns.segment_id
JOIN nh_master nm ON ns.nh_id = nm.nh_id
WHERE r1.start_chainage < r2.end_chainage 
  AND r1.end_chainage > r2.start_chainage;

-- 4. Check if road detail chainages are within segment boundaries
CREATE VIEW vw_out_of_bounds_details AS
SELECT 
    rd.detail_id,
    rd.segment_id,
    nm.nh_number,
    ns.start_chainage AS segment_start,
    ns.end_chainage AS segment_end,
    rd.start_chainage AS detail_start,
    rd.end_chainage AS detail_end,
    CASE 
        WHEN rd.start_chainage < ns.start_chainage THEN 'Start out of bounds'
        WHEN rd.end_chainage > ns.end_chainage THEN 'End out of bounds'
        ELSE 'Both out of bounds'
    END AS error_type
FROM nh_road_details rd
JOIN nh_segments ns ON rd.segment_id = ns.segment_id
JOIN nh_master nm ON ns.nh_id = nm.nh_id
WHERE rd.start_chainage < ns.start_chainage 
   OR rd.end_chainage > ns.end_chainage;

-- 5. Check segment coverage by road configurations
-- Shows which parts of segments are not covered by any configuration
WITH segment_coverage AS (
    SELECT 
        ns.segment_id,
        ns.nh_id,
        nm.nh_number,
        ns.start_chainage,
        ns.end_chainage,
        ns.end_chainage - ns.start_chainage AS segment_length,
        COALESCE(SUM(rd.end_chainage - rd.start_chainage), 0) AS covered_length
    FROM nh_segments ns
    JOIN nh_master nm ON ns.nh_id = nm.nh_id
    LEFT JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
    GROUP BY ns.segment_id, ns.nh_id, nm.nh_number, ns.start_chainage, ns.end_chainage
)
SELECT 
    *,
    segment_length - covered_length AS uncovered_length,
    ROUND((covered_length / segment_length * 100), 2) AS coverage_percentage
FROM segment_coverage
WHERE ROUND((covered_length / segment_length * 100), 2) < 100
ORDER BY nh_id, segment_id;

-- ============================================================================
-- REPORTING QUERIES
-- ============================================================================

-- 6. Total length by NH and configuration type
CREATE VIEW vw_nh_config_summary AS
SELECT 
    nm.nh_number,
    nm.nh_name,
    rc.config_name,
    ROUND(SUM(rd.length_km), 3) AS total_length_km,
    COUNT(rd.detail_id) AS number_of_sections
FROM nh_master nm
JOIN nh_segments ns ON nm.nh_id = ns.nh_id
JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
JOIN road_configurations rc ON rd.config_id = rc.config_id
GROUP BY nm.nh_number, nm.nh_name, rc.config_name
ORDER BY nm.nh_number, rc.display_order;

-- 7. Division-wise NH summary
CREATE VIEW vw_division_nh_summary AS
SELECT 
    d.division_name,
    d.office_name,
    nm.nh_number,
    COUNT(ns.segment_id) AS num_segments,
    ROUND(SUM(ns.end_chainage - ns.start_chainage), 3) AS total_length_km,
    MIN(ns.start_chainage) AS min_chainage,
    MAX(ns.end_chainage) AS max_chainage
FROM divisions d
JOIN nh_segments ns ON d.division_id = ns.division_office_id
JOIN nh_master nm ON ns.nh_id = nm.nh_id
GROUP BY d.division_name, d.office_name, nm.nh_number
ORDER BY d.division_name, d.office_name, nm.nh_number;

-- 8. Complete NH overview with all configurations
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
    rd.length_km AS config_length_km,
    rd.remarks
FROM nh_master nm
JOIN nh_segments ns ON nm.nh_id = ns.nh_id
JOIN divisions d ON ns.division_office_id = d.division_id
LEFT JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
LEFT JOIN road_configurations rc ON rd.config_id = rc.config_id
ORDER BY nm.nh_number, ns.start_chainage, rd.start_chainage;

-- 9. Configuration-wise statistics across all NHs
CREATE VIEW vw_config_statistics AS
SELECT 
    rc.config_name,
    rc.config_code,
    COUNT(DISTINCT nm.nh_id) AS num_highways,
    COUNT(rd.detail_id) AS num_sections,
    ROUND(SUM(rd.length_km), 3) AS total_length_km,
    ROUND(AVG(rd.length_km), 3) AS avg_section_length_km,
    ROUND(MIN(rd.length_km), 3) AS min_section_length_km,
    ROUND(MAX(rd.length_km), 3) AS max_section_length_km
FROM road_configurations rc
LEFT JOIN nh_road_details rd ON rc.config_id = rd.config_id
LEFT JOIN nh_segments ns ON rd.segment_id = ns.segment_id
LEFT JOIN nh_master nm ON ns.nh_id = nm.nh_id
GROUP BY rc.config_name, rc.config_code
ORDER BY rc.display_order;

-- 10. User activity summary
CREATE VIEW vw_user_activity AS
SELECT 
    u.username,
    u.full_name,
    u.role,
    d.division_name,
    d.office_name,
    COUNT(DISTINCT ns.segment_id) AS segments_created,
    COUNT(DISTINCT rd.detail_id) AS details_created,
    u.last_login,
    u.is_active
FROM users u
LEFT JOIN divisions d ON u.division_office_id = d.division_id
LEFT JOIN nh_segments ns ON u.user_id = ns.created_by
LEFT JOIN nh_road_details rd ON u.user_id = rd.created_by
GROUP BY u.user_id, u.username, u.full_name, u.role, d.division_name, d.office_name, u.last_login, u.is_active
ORDER BY u.role, d.division_name, d.office_name;

-- ============================================================================
-- STORED PROCEDURES FOR COMMON OPERATIONS
-- ============================================================================

-- Procedure to validate segment continuity for an NH
DELIMITER //

CREATE PROCEDURE sp_validate_nh_continuity(IN p_nh_id INT)
BEGIN
    -- Check for overlaps
    SELECT 'OVERLAPS' AS issue_type, 
           s1.segment_id, s2.segment_id,
           s1.start_chainage, s1.end_chainage,
           s2.start_chainage, s2.end_chainage
    FROM nh_segments s1
    JOIN nh_segments s2 ON s1.nh_id = s2.nh_id AND s1.segment_id < s2.segment_id
    WHERE s1.nh_id = p_nh_id
      AND s1.start_chainage < s2.end_chainage 
      AND s1.end_chainage > s2.start_chainage
    
    UNION ALL
    
    -- Check for gaps
    SELECT 'GAPS' AS issue_type,
           segment_id, NULL,
           prev_end, start_chainage,
           NULL, NULL
    FROM (
        SELECT 
            segment_id,
            start_chainage,
            LAG(end_chainage) OVER (ORDER BY start_chainage) AS prev_end
        FROM nh_segments
        WHERE nh_id = p_nh_id
    ) AS gaps
    WHERE prev_end IS NOT NULL 
      AND start_chainage > prev_end;
END //

-- Procedure to get NH summary
CREATE PROCEDURE sp_get_nh_summary(IN p_nh_id INT)
BEGIN
    SELECT 
        nm.nh_number,
        nm.nh_name,
        COUNT(DISTINCT ns.segment_id) AS total_segments,
        COUNT(DISTINCT ns.division_office_id) AS divisions_involved,
        ROUND(SUM(ns.end_chainage - ns.start_chainage), 3) AS total_length_km,
        MIN(ns.start_chainage) AS min_chainage,
        MAX(ns.end_chainage) AS max_chainage
    FROM nh_master nm
    LEFT JOIN nh_segments ns ON nm.nh_id = ns.nh_id
    WHERE nm.nh_id = p_nh_id
    GROUP BY nm.nh_id, nm.nh_number, nm.nh_name;
    
    -- Configuration breakdown
    SELECT 
        rc.config_name,
        ROUND(SUM(rd.length_km), 3) AS length_km,
        COUNT(rd.detail_id) AS num_sections
    FROM nh_segments ns
    JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
    JOIN road_configurations rc ON rd.config_id = rc.config_id
    WHERE ns.nh_id = p_nh_id
    GROUP BY rc.config_name
    ORDER BY rc.display_order;
END //

-- Procedure to get division office workload
CREATE PROCEDURE sp_get_division_workload(IN p_division_office_id INT)
BEGIN
    SELECT 
        nm.nh_number,
        ns.segment_name,
        ROUND(ns.end_chainage - ns.start_chainage, 3) AS segment_length_km,
        COUNT(rd.detail_id) AS num_configurations,
        ROUND(SUM(rd.length_km), 3) AS configured_length_km,
        ns.status
    FROM nh_segments ns
    JOIN nh_master nm ON ns.nh_id = nm.nh_id
    LEFT JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
    WHERE ns.division_office_id = p_division_office_id
    GROUP BY ns.segment_id, nm.nh_number, ns.segment_name, ns.start_chainage, ns.end_chainage, ns.status
    ORDER BY nm.nh_number, ns.start_chainage;
END //

DELIMITER ;
