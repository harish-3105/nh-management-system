import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='WJ28@krhps',
    database='nh_management'
)

cursor = conn.cursor(dictionary=True)

# Check NH44 segments with coordinates
cursor.execute('''
    SELECT s.segment_id, s.segment_name, s.start_chainage, s.end_chainage,
           s.start_latitude, s.start_longitude, s.end_latitude, s.end_longitude,
           n.nh_number
    FROM nh_segments s
    JOIN nh_master n ON s.nh_id = n.nh_id
    WHERE n.nh_number LIKE '%44%'
    ORDER BY s.start_chainage
''')

segments = cursor.fetchall()
print(f'Found {len(segments)} segments for NH44:')
print('='*80)
for seg in segments:
    print(f"\nSegment: {seg['segment_name']}")
    print(f"  Chainage: {seg['start_chainage']} - {seg['end_chainage']} km")
    print(f"  Start: Lat={seg['start_latitude']}, Lng={seg['start_longitude']}")
    print(f"  End: Lat={seg['end_latitude']}, Lng={seg['end_longitude']}")

conn.close()
