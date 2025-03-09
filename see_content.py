import sqlite3
import pandas as pd

DB_NAME = "equipment_data.db"

# Connect to the SQLite database
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Loop through each table and display its contents
for table in tables:
    table_name = table[0]
    print(f"\n--- Contents of {table_name} ---")
    
    # Read the entire table
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
    
    if df.empty:
        print("No data in this table.")
    else:
        print(df)

# Close the database connection
conn.close()
