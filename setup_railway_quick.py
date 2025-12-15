"""Quick script to create Railway tables"""
import mysql.connector
from config import DB_CONFIG

print("Connecting to Railway MySQL...")
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor(buffered=True)

print("Reading SQL file...")
with open('railway_setup.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

print("Executing SQL commands...")
# Execute using multi-statement
for result in cursor.execute(sql_content, multi=True):
    try:
        result.fetchall()
    except:
        pass

conn.commit()

# Verify
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"\n✅ Success! Created {len(tables)} tables:")
for table in tables:
    print(f"  - {table[0]}")

cursor.close()
conn.close()
print("\n🎉 Your Railway database is ready!")
