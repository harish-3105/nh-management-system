import mysql.connector
from mysql.connector import Error

def check_nh44_coordinates():
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host='localhost',
            database='nh_management',
            user='root',
            password='1234'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            # Get NH44 segments with GPS coordinates
            query = """
                SELECT 
                    s.segment_id,
                    s.segment_name,
                    s.start_chainage,
                    s.end_chainage,
                    s.start_latitude,
                    s.start_longitude,
                    s.end_latitude,
                    s.end_longitude,
                    n.nh_number
                FROM nh_segments s
                JOIN nh_master n ON s.nh_id = n.nh_id
                WHERE n.nh_number LIKE '%44%'
                ORDER BY s.start_chainage
                LIMIT 10
            """
            
            cursor.execute(query)
            segments = cursor.fetchall()
            
            print(f"\n{'='*100}")
            print(f"Found {len(segments)} NH44 segments:")
            print(f"{'='*100}\n")
            
            if segments:
                for seg in segments:
                    print(f"Segment ID: {seg['segment_id']}")
                    print(f"Name: {seg['segment_name']}")
                    print(f"NH: {seg['nh_number']}")
                    print(f"Chainage: {seg['start_chainage']} - {seg['end_chainage']} km")
                    
                    # Check if GPS coordinates exist
                    if seg['start_latitude'] and seg['start_longitude']:
                        print(f"Start GPS: {seg['start_latitude']}, {seg['start_longitude']}")
                    else:
                        print(f"Start GPS: ❌ NOT SET")
                    
                    if seg['end_latitude'] and seg['end_longitude']:
                        print(f"End GPS: {seg['end_latitude']}, {seg['end_longitude']}")
                    else:
                        print(f"End GPS: ❌ NOT SET")
                    
                    print("-" * 100)
                
                # Count segments with and without coordinates
                with_coords = sum(1 for s in segments if s['start_latitude'] and s['start_longitude'] 
                                 and s['end_latitude'] and s['end_longitude'])
                without_coords = len(segments) - with_coords
                
                print(f"\nSummary:")
                print(f"  ✅ Segments with full GPS coordinates: {with_coords}")
                print(f"  ❌ Segments missing GPS coordinates: {without_coords}")
                
                if without_coords > 0:
                    print(f"\n⚠️  Map will NOT show routes without GPS coordinates!")
                    print(f"   Please add latitude/longitude in the Segments tab.")
            else:
                print("No NH44 segments found in database!")
            
            cursor.close()
            
    except Error as e:
        print(f"Error: {e}")
    
    finally:
        if connection.is_connected():
            connection.close()
            print(f"\n{'='*100}")
            print("Database connection closed.")

if __name__ == "__main__":
    check_nh44_coordinates()
