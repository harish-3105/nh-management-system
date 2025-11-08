import mysql.connector

# Add latitude and longitude columns to nh_segments table

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='WJ28@krhps',
    database='nh_management'
)

cursor = conn.cursor()

try:
    print('Adding latitude and longitude columns to nh_segments table...')
    
    # Add start_latitude column
    cursor.execute('''
        ALTER TABLE nh_segments 
        ADD COLUMN start_latitude DECIMAL(10, 6) NULL AFTER segment_name
    ''')
    print('✓ Added start_latitude column')
    
    # Add start_longitude column
    cursor.execute('''
        ALTER TABLE nh_segments 
        ADD COLUMN start_longitude DECIMAL(10, 6) NULL AFTER start_latitude
    ''')
    print('✓ Added start_longitude column')
    
    # Add end_latitude column
    cursor.execute('''
        ALTER TABLE nh_segments 
        ADD COLUMN end_latitude DECIMAL(10, 6) NULL AFTER start_longitude
    ''')
    print('✓ Added end_latitude column')
    
    # Add end_longitude column
    cursor.execute('''
        ALTER TABLE nh_segments 
        ADD COLUMN end_longitude DECIMAL(10, 6) NULL AFTER end_latitude
    ''')
    print('✓ Added end_longitude column')
    
    conn.commit()
    print('\n✅ Successfully added all latitude/longitude columns!')
    print('\nUpdated table structure:')
    cursor.execute('DESCRIBE nh_segments')
    for col in cursor.fetchall():
        print(f'  {col[0]} - {col[1]}')
    
except mysql.connector.Error as err:
    print(f'❌ Error: {err}')
    conn.rollback()

finally:
    cursor.close()
    conn.close()
