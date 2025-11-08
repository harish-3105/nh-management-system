"""
National Highways Management System - Python Application Layer
This module provides a Python interface to interact with the NH database
"""

import mysql.connector
from mysql.connector import Error
from mysql.connector.pooling import MySQLConnectionPool
import bcrypt
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import json


class NHDatabase:
    """Database connection and operations handler with connection pooling"""
    
    def __init__(self, host: str, database: str, user: str, password: str, port: int = 3306):
        """
        Initialize database connection pool
        
        Args:
            host: Database host address
            database: Database name
            user: Database username
            password: Database password
            port: Database port (default: 3306)
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.pool = None
        self.last_error = None  # Store last error for retrieval
        
    def connect(self):
        """Create database connection pool"""
        try:
            self.pool = MySQLConnectionPool(
                pool_name="nh_pool",
                pool_size=10,
                pool_reset_session=True,
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print(f"Successfully connected to {self.database}")
            return True
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection pool"""
        # Connection pool doesn't need explicit closing
        pass
    
    def execute_query(self, query: str, params: Optional[tuple] = None, 
                     fetch: bool = True, raise_on_error: bool = False) -> Optional[List[tuple]]:
        """
        Execute a SQL query using connection from pool
        
        Args:
            query: SQL query string
            params: Query parameters (for prepared statements)
            fetch: Whether to fetch results
            raise_on_error: If True, raise exceptions; if False, return None on error
            
        Returns:
            Query results if fetch=True, True for successful non-fetch, None on error (if not raising)
        
        Raises:
            Error: Database errors (only if raise_on_error=True)
        """
        connection = None
        cursor = None
        try:
            self.last_error = None
            
            # Get connection from pool
            connection = self.pool.get_connection()
            
            # Use buffered cursor to fetch all results immediately
            cursor = connection.cursor(dictionary=True, buffered=True)
            cursor.execute(query, params or ())
            
            if fetch:
                results = cursor.fetchall()
            else:
                connection.commit()
                results = True
                
            cursor.close()
            connection.close()  # Return connection to pool
            return results
            
        except Error as e:
            self.last_error = str(e)
            print(f"Error executing query: {e}")
            
            # Clean up
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if connection:
                try:
                    connection.close()
                except:
                    pass
            
            # Either raise the error or return None based on flag
            if raise_on_error:
                raise
            else:
                return None


class UserManager:
    """Manage user authentication and authorization"""
    
    def __init__(self, db: NHDatabase):
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user
        
        Args:
            username: User's username
            password: User's password
            
        Returns:
            User data dict if successful, None otherwise
        """
        query = """
            SELECT u.user_id, u.username, u.password_hash, u.role, 
                   u.division_office_id, u.full_name, u.email,
                   d.division_name, d.office_name
            FROM users u
            LEFT JOIN divisions d ON u.division_office_id = d.division_id
            WHERE u.username = %s AND u.is_active = TRUE
        """
        
        results = self.db.execute_query(query, (username,))
        
        if results and len(results) > 0:
            user = results[0]
            if self.verify_password(password, user['password_hash']):
                # Update last login
                update_query = "UPDATE users SET last_login = NOW() WHERE user_id = %s"
                self.db.execute_query(update_query, (user['user_id'],), fetch=False)
                
                # Remove password hash from returned data
                del user['password_hash']
                return user
        
        return None
    
    def create_user(self, username: str, password: str, role: str,
                   full_name: str, email: str, 
                   division_office_id: Optional[int] = None) -> bool:
        """
        Create a new user
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            role: 'central' or 'division'
            full_name: User's full name
            email: User's email
            division_office_id: Division office ID (required for division users)
            
        Returns:
            True if successful, False otherwise
        """
        # Validate role and division_office_id combination
        if role == 'division' and division_office_id is None:
            print("Division users must have a division_office_id")
            return False
        if role == 'central' and division_office_id is not None:
            print("Central users must not have a division_office_id")
            return False
        
        password_hash = self.hash_password(password)
        
        query = """
            INSERT INTO users (username, password_hash, role, division_office_id, 
                             full_name, email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        result = self.db.execute_query(
            query, 
            (username, password_hash, role, division_office_id, full_name, email),
            fetch=False
        )
        
        return result is not None


class NHManager:
    """Manage National Highway data"""
    
    def __init__(self, db: NHDatabase):
        self.db = db
    
    def get_all_nhs(self) -> List[Dict]:
        """Get all National Highways"""
        query = "SELECT * FROM nh_master ORDER BY nh_number"
        return self.db.execute_query(query) or []
    
    def get_nh_summary(self, nh_id: int) -> Dict:
        """Get summary for a specific NH"""
        query = "CALL sp_get_nh_summary(%s)"
        return self.db.execute_query(query, (nh_id,)) or {}
    
    def get_nh_segments(self, nh_id: int) -> List[Dict]:
        """Get all segments for a specific NH"""
        query = """
            SELECT ns.*, d.division_name, d.office_name
            FROM nh_segments ns
            JOIN divisions d ON ns.division_office_id = d.division_id
            WHERE ns.nh_id = %s
            ORDER BY ns.start_chainage
        """
        return self.db.execute_query(query, (nh_id,)) or []


class SegmentManager:
    """Manage NH segments"""
    
    def __init__(self, db: NHDatabase):
        self.db = db
    
    def get_segments_by_division(self, division_office_id: int) -> List[Dict]:
        """Get all segments assigned to a division office"""
        query = """
            SELECT ns.*, nm.nh_number, nm.nh_name
            FROM nh_segments ns
            JOIN nh_master nm ON ns.nh_id = nm.nh_id
            WHERE ns.division_office_id = %s
            ORDER BY nm.nh_number, ns.start_chainage
        """
        return self.db.execute_query(query, (division_office_id,)) or []
    
    def create_segment(self, nh_id: int, division_office_id: int,
                      start_chainage: float, end_chainage: float,
                      segment_name: str, created_by: int,
                      remarks: Optional[str] = None) -> bool:
        """Create a new NH segment"""
        query = """
            INSERT INTO nh_segments 
            (nh_id, division_office_id, start_chainage, end_chainage, 
             segment_name, remarks, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        result = self.db.execute_query(
            query,
            (nh_id, division_office_id, start_chainage, end_chainage,
             segment_name, remarks, created_by),
            fetch=False
        )
        
        return result is not None
    
    def get_segment_details(self, segment_id: int) -> Optional[Dict]:
        """Get details for a specific segment"""
        query = """
            SELECT ns.*, nm.nh_number, nm.nh_name, 
                   d.division_name, d.office_name
            FROM nh_segments ns
            JOIN nh_master nm ON ns.nh_id = nm.nh_id
            JOIN divisions d ON ns.division_office_id = d.division_id
            WHERE ns.segment_id = %s
        """
        results = self.db.execute_query(query, (segment_id,))
        return results[0] if results else None


class RoadDetailManager:
    """Manage road configuration details"""
    
    def __init__(self, db: NHDatabase):
        self.db = db
    
    def get_configurations(self) -> List[Dict]:
        """Get all road configuration types"""
        query = """
            SELECT * FROM road_configurations 
            WHERE is_active = TRUE 
            ORDER BY display_order
        """
        return self.db.execute_query(query) or []
    
    def get_segment_details(self, segment_id: int) -> List[Dict]:
        """Get all road details for a segment"""
        query = """
            SELECT rd.*, rc.config_name, rc.config_code
            FROM nh_road_details rd
            JOIN road_configurations rc ON rd.config_id = rc.config_id
            WHERE rd.segment_id = %s
            ORDER BY rd.start_chainage
        """
        return self.db.execute_query(query, (segment_id,)) or []
    
    def add_road_detail(self, segment_id: int, config_id: int,
                       start_chainage: float, end_chainage: float,
                       created_by: int, remarks: Optional[str] = None) -> bool:
        """Add road configuration detail to a segment
        
        Raises:
            Error: Database constraint violations (overlap, out of bounds, etc.)
        """
        query = """
            INSERT INTO nh_road_details 
            (segment_id, config_id, start_chainage, end_chainage, 
             remarks, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        result = self.db.execute_query(
            query,
            (segment_id, config_id, start_chainage, end_chainage, 
             remarks, created_by),
            fetch=False,
            raise_on_error=True  # Raise errors so server can handle them
        )
        
        return result is not None and result is not False
    
    def update_road_detail(self, detail_id: int, start_chainage: float,
                          end_chainage: float, 
                          remarks: Optional[str] = None) -> bool:
        """Update a road configuration detail"""
        query = """
            UPDATE nh_road_details 
            SET start_chainage = %s, end_chainage = %s, remarks = %s
            WHERE detail_id = %s
        """
        
        result = self.db.execute_query(
            query,
            (start_chainage, end_chainage, remarks, detail_id),
            fetch=False,
            raise_on_error=True
        )
        
        return result is not None and result is not False
    
    def delete_road_detail(self, detail_id: int) -> bool:
        """Delete a road configuration detail"""
        query = "DELETE FROM nh_road_details WHERE detail_id = %s"
        result = self.db.execute_query(query, (detail_id,), fetch=False, raise_on_error=True)
        return result is not None and result is not False


class ValidationManager:
    """Manage data validation and integrity checks"""
    
    def __init__(self, db: NHDatabase):
        self.db = db
    
    def check_overlapping_segments(self) -> List[Dict]:
        """Check for overlapping segments"""
        query = "SELECT * FROM vw_overlapping_segments"
        return self.db.execute_query(query) or []
    
    def check_overlapping_configurations(self) -> List[Dict]:
        """Check for overlapping road configurations"""
        query = "SELECT * FROM vw_overlapping_configurations"
        return self.db.execute_query(query) or []
    
    def check_out_of_bounds_details(self) -> List[Dict]:
        """Check for road details outside segment boundaries"""
        query = "SELECT * FROM vw_out_of_bounds_details"
        return self.db.execute_query(query) or []
    
    def validate_nh_continuity(self, nh_id: int) -> List[Dict]:
        """Validate continuity for a specific NH"""
        query = "CALL sp_validate_nh_continuity(%s)"
        return self.db.execute_query(query, (nh_id,)) or []


class ReportManager:
    """Generate reports and analytics"""
    
    def __init__(self, db: NHDatabase):
        self.db = db
    
    def get_nh_config_summary(self, nh_number: Optional[str] = None) -> List[Dict]:
        """Get NH configuration summary"""
        if nh_number:
            query = """
                SELECT * FROM vw_nh_config_summary 
                WHERE nh_number = %s
                ORDER BY nh_number, config_name
            """
            return self.db.execute_query(query, (nh_number,)) or []
        else:
            query = "SELECT * FROM vw_nh_config_summary ORDER BY nh_number, config_name"
            return self.db.execute_query(query) or []
    
    def get_division_summary(self, division_name: Optional[str] = None) -> List[Dict]:
        """Get division-wise summary"""
        if division_name:
            query = """
                SELECT * FROM vw_division_nh_summary 
                WHERE division_name = %s
                ORDER BY division_name, office_name, nh_number
            """
            return self.db.execute_query(query, (division_name,)) or []
        else:
            query = """
                SELECT * FROM vw_division_nh_summary 
                ORDER BY division_name, office_name, nh_number
            """
            return self.db.execute_query(query) or []
    
    def get_config_statistics(self) -> List[Dict]:
        """Get configuration-wise statistics"""
        query = "SELECT * FROM vw_config_statistics ORDER BY config_name"
        return self.db.execute_query(query) or []
    
    def get_config_details(self, config_id: int) -> List[Dict]:
        """Get detailed chainage report for a specific configuration"""
        query = """
            SELECT 
                nm.nh_number,
                ns.segment_name,
                rd.start_chainage,
                rd.end_chainage,
                ROUND(rd.end_chainage - rd.start_chainage, 3) AS length_km,
                rd.remarks,
                d.division_name,
                d.office_name
            FROM nh_road_details rd
            JOIN nh_segments ns ON rd.segment_id = ns.segment_id
            JOIN nh_master nm ON ns.nh_id = nm.nh_id
            JOIN divisions d ON ns.division_office_id = d.division_id
            WHERE rd.config_id = %s
            ORDER BY nm.nh_number, ns.start_chainage, rd.start_chainage
        """
        return self.db.execute_query(query, (config_id,)) or []
    
    def get_division_wise_details(self, nh_number: Optional[str] = None, config_id: Optional[int] = None) -> List[Dict]:
        """Get division-wise detailed report with optional NH and config filters"""
        query = """
            SELECT 
                d.division_name,
                d.office_name,
                nm.nh_number,
                nm.nh_name,
                ns.segment_name,
                ns.start_chainage AS segment_start,
                ns.end_chainage AS segment_end,
                ROUND(ns.end_chainage - ns.start_chainage, 3) AS segment_length,
                rc.config_name,
                rd.start_chainage AS config_start,
                rd.end_chainage AS config_end,
                ROUND(rd.end_chainage - rd.start_chainage, 3) AS config_length,
                rd.remarks
            FROM divisions d
            JOIN nh_segments ns ON d.division_id = ns.division_office_id
            JOIN nh_master nm ON ns.nh_id = nm.nh_id
            LEFT JOIN nh_road_details rd ON ns.segment_id = rd.segment_id
            LEFT JOIN road_configurations rc ON rd.config_id = rc.config_id
            WHERE 1=1
        """
        params = []
        
        if nh_number and nh_number != 'ALL':
            query += " AND nm.nh_number = %s"
            params.append(nh_number)
        
        if config_id:
            query += " AND rd.config_id = %s"
            params.append(config_id)
        
        query += " ORDER BY d.division_name, d.office_name, nm.nh_number, ns.start_chainage, rd.start_chainage"
        
        return self.db.execute_query(query, tuple(params)) if params else self.db.execute_query(query) or []
    
    def get_user_activity(self) -> List[Dict]:
        """Get user activity summary"""
        query = "SELECT * FROM vw_user_activity ORDER BY role, division_name"
        return self.db.execute_query(query) or []


# Example usage
if __name__ == "__main__":
    # Initialize database connection
    db = NHDatabase(
        host="localhost",
        database="nh_management",
        user="root",
        password="your_password"
    )
    
    if db.connect():
        # Initialize managers
        user_mgr = UserManager(db)
        nh_mgr = NHManager(db)
        segment_mgr = SegmentManager(db)
        detail_mgr = RoadDetailManager(db)
        validation_mgr = ValidationManager(db)
        report_mgr = ReportManager(db)
        
        # Example: Authenticate user
        user = user_mgr.authenticate("madurai_office", "admin123")
        if user:
            print(f"Logged in as: {user['full_name']} ({user['role']})")
            
            # Example: Get user's assigned segments
            if user['role'] == 'division':
                segments = segment_mgr.get_segments_by_division(
                    user['division_office_id']
                )
                print(f"\nAssigned segments: {len(segments)}")
                for seg in segments:
                    print(f"  - {seg['nh_number']}: {seg['segment_name']}")
            
            # Example: Get all NHs
            nhs = nh_mgr.get_all_nhs()
            print(f"\nTotal NHs: {len(nhs)}")
            
            # Example: Run validation checks
            overlaps = validation_mgr.check_overlapping_segments()
            print(f"\nOverlapping segments: {len(overlaps)}")
            
            # Example: Get reports
            stats = report_mgr.get_config_statistics()
            print("\nConfiguration Statistics:")
            for stat in stats:
                print(f"  {stat['config_name']}: {stat['total_length_km']} km")
        
        db.disconnect()
