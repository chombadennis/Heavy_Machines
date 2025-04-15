import os
import sqlite3
import pandas as pd

# Database file
DB_NAME = "equipment_data.db"
OUTPUT_FOLDER = "equipment_data"

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Connect to the database
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]

# Export each table to a CSV file
for table in tables:
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    csv_filename = os.path.join(OUTPUT_FOLDER, f"{table}.csv")
    df.to_csv(csv_filename, index=False)
    print(f"Saved {table} to {csv_filename}")
    
# Close connection
conn.close()

print("All tables have been exported successfully!")