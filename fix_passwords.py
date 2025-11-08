"""
Fix user passwords with proper bcrypt hashes
"""
import mysql.connector
import bcrypt

# Connect to database
db = mysql.connector.connect(
    host="localhost",
    database="nh_management",
    user="root",
    password="WJ28@krhps"
)

cursor = db.cursor()

# Generate proper hash for 'admin123'
password = 'admin123'
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print(f"Generated hash: {password_hash}")

# Update all users
cursor.execute("UPDATE users SET password_hash = %s", (password_hash,))
db.commit()

print(f"Updated {cursor.rowcount} users")

# Verify
cursor.execute("SELECT username, password_hash FROM users LIMIT 3")
results = cursor.fetchall()

print("\nVerifying first 3 users:")
for username, hash_value in results:
    print(f"  {username}: {hash_value[:50]}...")
    # Test the hash
    if bcrypt.checkpw(password.encode('utf-8'), hash_value.encode('utf-8')):
        print(f"    ✅ Password verification works!")
    else:
        print(f"    ❌ Password verification failed!")

cursor.close()
db.close()

print("\n✅ Password update complete!")
