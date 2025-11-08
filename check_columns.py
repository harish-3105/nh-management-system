import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='WJ28@krhps',
    database='nh_management'
)

cursor = conn.cursor()
cursor.execute('DESCRIBE nh_segments')
cols = cursor.fetchall()
print('nh_segments columns:')
for col in cols:
    print(f'{col[0]} - {col[1]}')

print('\n' + '='*50)
cursor.execute('SELECT segment_id, segment_name, start_latitude, start_longitude, end_latitude, end_longitude FROM nh_segments WHERE segment_id = 15')
result = cursor.fetchone()
print('\nSegment 15 data:')
if result:
    print(f'Segment ID: {result[0]}')
    print(f'Segment Name: {result[1]}')
    print(f'Start Latitude: {result[2]}')
    print(f'Start Longitude: {result[3]}')
    print(f'End Latitude: {result[4]}')
    print(f'End Longitude: {result[5]}')
else:
    print('No data found')

conn.close()
