-- Triggers for National Highways Management System
-- These triggers help maintain data integrity and audit trail

-- ============================================================================
-- TRIGGERS FOR NH_SEGMENTS
-- ============================================================================

DELIMITER //

-- Trigger to prevent overlapping segments for the same NH
CREATE TRIGGER trg_before_insert_nh_segments
BEFORE INSERT ON nh_segments
FOR EACH ROW
BEGIN
    DECLARE overlap_count INT;
    
    -- Check for overlapping segments
    SELECT COUNT(*) INTO overlap_count
    FROM nh_segments
    WHERE nh_id = NEW.nh_id
      AND segment_id != NEW.segment_id
      AND (
          (NEW.start_chainage < end_chainage AND NEW.end_chainage > start_chainage)
      );
    
    IF overlap_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Segment overlaps with existing segment for this NH';
    END IF;
END //

CREATE TRIGGER trg_before_update_nh_segments
BEFORE UPDATE ON nh_segments
FOR EACH ROW
BEGIN
    DECLARE overlap_count INT;
    
    -- Check for overlapping segments (excluding current segment)
    SELECT COUNT(*) INTO overlap_count
    FROM nh_segments
    WHERE nh_id = NEW.nh_id
      AND segment_id != NEW.segment_id
      AND (
          (NEW.start_chainage < end_chainage AND NEW.end_chainage > start_chainage)
      );
    
    IF overlap_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Segment overlaps with existing segment for this NH';
    END IF;
END //

-- ============================================================================
-- TRIGGERS FOR NH_ROAD_DETAILS
-- ============================================================================

-- Trigger to ensure road details are within segment boundaries
CREATE TRIGGER trg_before_insert_nh_road_details
BEFORE INSERT ON nh_road_details
FOR EACH ROW
BEGIN
    DECLARE seg_start DECIMAL(10, 3);
    DECLARE seg_end DECIMAL(10, 3);
    
    -- Get segment boundaries
    SELECT start_chainage, end_chainage
    INTO seg_start, seg_end
    FROM nh_segments
    WHERE segment_id = NEW.segment_id;
    
    -- Check if road detail is within segment boundaries
    IF NEW.start_chainage < seg_start OR NEW.end_chainage > seg_end THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Road detail chainage must be within segment boundaries';
    END IF;
    
    -- Check for overlapping configurations in the same segment
    IF EXISTS (
        SELECT 1
        FROM nh_road_details
        WHERE segment_id = NEW.segment_id
          AND detail_id != NEW.detail_id
          AND (
              (NEW.start_chainage < end_chainage AND NEW.end_chainage > start_chainage)
          )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Road configuration overlaps with existing configuration in this segment';
    END IF;
END //

CREATE TRIGGER trg_before_update_nh_road_details
BEFORE UPDATE ON nh_road_details
FOR EACH ROW
BEGIN
    DECLARE seg_start DECIMAL(10, 3);
    DECLARE seg_end DECIMAL(10, 3);
    
    -- Get segment boundaries
    SELECT start_chainage, end_chainage
    INTO seg_start, seg_end
    FROM nh_segments
    WHERE segment_id = NEW.segment_id;
    
    -- Check if road detail is within segment boundaries
    IF NEW.start_chainage < seg_start OR NEW.end_chainage > seg_end THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Road detail chainage must be within segment boundaries';
    END IF;
    
    -- Check for overlapping configurations in the same segment
    IF EXISTS (
        SELECT 1
        FROM nh_road_details
        WHERE segment_id = NEW.segment_id
          AND detail_id != NEW.detail_id
          AND (
              (NEW.start_chainage < end_chainage AND NEW.end_chainage > start_chainage)
          )
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Road configuration overlaps with existing configuration in this segment';
    END IF;
END //

-- ============================================================================
-- AUDIT TRIGGERS
-- ============================================================================

-- Audit trigger for NH_SEGMENTS insert
CREATE TRIGGER trg_audit_nh_segments_insert
AFTER INSERT ON nh_segments
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, table_name, record_id, action, new_values)
    VALUES (
        NEW.created_by,
        'nh_segments',
        NEW.segment_id,
        'INSERT',
        JSON_OBJECT(
            'nh_id', NEW.nh_id,
            'division_office_id', NEW.division_office_id,
            'start_chainage', NEW.start_chainage,
            'end_chainage', NEW.end_chainage,
            'segment_name', NEW.segment_name,
            'status', NEW.status
        )
    );
END //

-- Audit trigger for NH_SEGMENTS update
CREATE TRIGGER trg_audit_nh_segments_update
AFTER UPDATE ON nh_segments
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, table_name, record_id, action, old_values, new_values)
    VALUES (
        NEW.created_by,
        'nh_segments',
        NEW.segment_id,
        'UPDATE',
        JSON_OBJECT(
            'nh_id', OLD.nh_id,
            'division_office_id', OLD.division_office_id,
            'start_chainage', OLD.start_chainage,
            'end_chainage', OLD.end_chainage,
            'segment_name', OLD.segment_name,
            'status', OLD.status
        ),
        JSON_OBJECT(
            'nh_id', NEW.nh_id,
            'division_office_id', NEW.division_office_id,
            'start_chainage', NEW.start_chainage,
            'end_chainage', NEW.end_chainage,
            'segment_name', NEW.segment_name,
            'status', NEW.status
        )
    );
END //

-- Audit trigger for NH_SEGMENTS delete
CREATE TRIGGER trg_audit_nh_segments_delete
BEFORE DELETE ON nh_segments
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, table_name, record_id, action, old_values)
    VALUES (
        OLD.created_by,
        'nh_segments',
        OLD.segment_id,
        'DELETE',
        JSON_OBJECT(
            'nh_id', OLD.nh_id,
            'division_office_id', OLD.division_office_id,
            'start_chainage', OLD.start_chainage,
            'end_chainage', OLD.end_chainage,
            'segment_name', OLD.segment_name,
            'status', OLD.status
        )
    );
END //

-- Audit trigger for NH_ROAD_DETAILS insert
CREATE TRIGGER trg_audit_nh_road_details_insert
AFTER INSERT ON nh_road_details
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, table_name, record_id, action, new_values)
    VALUES (
        NEW.created_by,
        'nh_road_details',
        NEW.detail_id,
        'INSERT',
        JSON_OBJECT(
            'segment_id', NEW.segment_id,
            'config_id', NEW.config_id,
            'start_chainage', NEW.start_chainage,
            'end_chainage', NEW.end_chainage,
            'remarks', NEW.remarks
        )
    );
END //

-- Audit trigger for NH_ROAD_DETAILS update
CREATE TRIGGER trg_audit_nh_road_details_update
AFTER UPDATE ON nh_road_details
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, table_name, record_id, action, old_values, new_values)
    VALUES (
        NEW.created_by,
        'nh_road_details',
        NEW.detail_id,
        'UPDATE',
        JSON_OBJECT(
            'segment_id', OLD.segment_id,
            'config_id', OLD.config_id,
            'start_chainage', OLD.start_chainage,
            'end_chainage', OLD.end_chainage,
            'remarks', OLD.remarks
        ),
        JSON_OBJECT(
            'segment_id', NEW.segment_id,
            'config_id', NEW.config_id,
            'start_chainage', NEW.start_chainage,
            'end_chainage', NEW.end_chainage,
            'remarks', NEW.remarks
        )
    );
END //

-- Audit trigger for NH_ROAD_DETAILS delete
CREATE TRIGGER trg_audit_nh_road_details_delete
BEFORE DELETE ON nh_road_details
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (user_id, table_name, record_id, action, old_values)
    VALUES (
        OLD.created_by,
        'nh_road_details',
        OLD.detail_id,
        'DELETE',
        JSON_OBJECT(
            'segment_id', OLD.segment_id,
            'config_id', OLD.config_id,
            'start_chainage', OLD.start_chainage,
            'end_chainage', OLD.end_chainage,
            'remarks', OLD.remarks
        )
    );
END //

-- ============================================================================
-- TRIGGER TO UPDATE LAST LOGIN TIME
-- ============================================================================

CREATE TRIGGER trg_update_last_login
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    -- This would typically be called from application code
    -- When password is verified, set last_login
    IF NEW.last_login != OLD.last_login OR NEW.last_login IS NULL THEN
        SET NEW.last_login = CURRENT_TIMESTAMP;
    END IF;
END //

DELIMITER ;

-- ============================================================================
-- NOTES ON TRIGGERS
-- ============================================================================
-- 1. The overlap prevention triggers ensure data integrity at database level
-- 2. Audit triggers maintain a complete history of all changes
-- 3. The triggers work with the CHECK constraints defined in the schema
-- 4. For production, consider adding more sophisticated overlap detection
-- 5. Consider adding triggers for divisions and nh_master tables if needed
