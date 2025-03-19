import sqlite3

# Connect to the database
db_path = "equipment_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query the table
cursor.execute("SELECT * FROM xcmg_road_machinery_data_specs LIMIT 100;")

# Fetch and display results
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close connection  
conn.close() 

