import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='WJ28@krhps',
    database='nh_management'
)

cursor = conn.cursor()

# Update NH44 segment with Chennai to Chengalpattu coordinates
# Chennai coordinates: 13.0827, 80.2707
# Chengalpattu coordinates: 12.6916, 79.9759

cursor.execute('''
    UPDATE nh_segments 
    SET start_latitude = 13.0827,
        start_longitude = 80.2707,
        end_latitude = 12.6916,
        end_longitude = 79.9759
    WHERE segment_name = 'NH44 Chennai to Chengalpattu'
''')

conn.commit()
print('✅ Updated NH44 segment with GPS coordinates')
print('   Start: Chennai (13.0827, 80.2707)')
print('   End: Chengalpattu (12.6916, 79.9759)')

conn.close()
