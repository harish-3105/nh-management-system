import mysql.connector
from mysql.connector import Error

def fix_report_views():
    """Fix the report views to calculate length from chainages"""
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='WJ28@krhps',
            database='nh_management'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("✅ Connected to database")
            
            # Drop existing views
            print("\n📋 Dropping old views...")
            views_to_drop = [
                'vw_config_statistics',
                'vw_nh_complete_overview', 
                'vw_division_nh_summary',
                'vw_nh_config_summary'
            ]
            
            for view in views_to_drop:
                try:
                    cursor.execute(f"DROP VIEW IF EXISTS {view}")
                    print(f"   ✓ Dropped {view}")
                except Error as e:
                    print(f"   ⚠ Warning dropping {view}: {e}")
            
            connection.commit()
            
            # Create updated views
            print("\n📋 Creating updated views...")
            
            # 1. NH Configuration Summary
            cursor.execute("""
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
                ORDER BY nm.nh_number, rc.config_name
            """)
            print("   ✓ Created vw_nh_config_summary")
            
            # 2. Division Summary
            cursor.execute("""
                CREATE VIEW vw_division_nh_summary AS
                SELECT 
                    d.division_name,
                    d.office_name,
                    nm.nh_number,
                    COUNT(DISTINCT nm.nh_id) AS nh_count,
                    COUNT(ns.segment_id) AS segment_count,
                    ROUND(SUM(ns.end_chainage - ns.start_chainage), 3) AS total_length
                FROM divisions d
                JOIN nh_segments ns ON d.division_id = ns.division_office_id
                JOIN nh_master nm ON ns.nh_id = nm.nh_id
                GROUP BY d.division_name, d.office_name, nm.nh_number
                ORDER BY d.division_name, d.office_name, nm.nh_number
            """)
            print("   ✓ Created vw_division_nh_summary")
            
            # 3. Complete Overview
            cursor.execute("""
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
                ORDER BY nm.nh_number, ns.start_chainage, rd.start_chainage
            """)
            print("   ✓ Created vw_nh_complete_overview")
            
            # 4. Config Statistics
            cursor.execute("""
                CREATE VIEW vw_config_statistics AS
                SELECT 
                    rc.config_name,
                    rc.config_code,
                    COUNT(DISTINCT nm.nh_id) AS num_highways,
                    COUNT(rd.detail_id) AS num_sections,
                    ROUND(COALESCE(SUM(rd.end_chainage - rd.start_chainage), 0), 3) AS total_length,
                    ROUND(COALESCE(AVG(rd.end_chainage - rd.start_chainage), 0), 3) AS avg_section_length,
                    ROUND(COALESCE(MIN(rd.end_chainage - rd.start_chainage), 0), 3) AS min_section_length,
                    ROUND(COALESCE(MAX(rd.end_chainage - rd.start_chainage), 0), 3) AS max_section_length
                FROM road_configurations rc
                LEFT JOIN nh_road_details rd ON rc.config_id = rd.config_id
                LEFT JOIN nh_segments ns ON rd.segment_id = ns.segment_id
                LEFT JOIN nh_master nm ON ns.nh_id = nm.nh_id
                GROUP BY rc.config_name, rc.config_code
                ORDER BY rc.config_name
            """)
            print("   ✓ Created vw_config_statistics")
            
            connection.commit()
            
            # Verify views
            print("\n📊 Verifying views...")
            for view in ['vw_nh_config_summary', 'vw_division_nh_summary', 
                        'vw_config_statistics', 'vw_nh_complete_overview']:
                cursor.execute(f"SELECT COUNT(*) FROM {view}")
                count = cursor.fetchone()[0]
                print(f"   ✓ {view}: {count} rows")
            
            print("\n✅ All views updated successfully!")
            
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Database connection closed")

if __name__ == "__main__":
    fix_report_views()
