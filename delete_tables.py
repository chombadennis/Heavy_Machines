import sqlite3

DB_NAME = "equipment_data.db"

# Connect to the SQLite database
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Loop through each table and drop it
for table in tables:
    table_name = table[0]
    print(f"Dropping table: {table_name}")
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")

# Commit changes and close connection
conn.commit()
conn.close()

print("All tables have been deleted.")
