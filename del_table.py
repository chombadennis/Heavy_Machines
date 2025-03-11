import sqlite3

# Connect to the SQLite database
db_path = "equipment_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the table if it exists
table_name = "cat_skid_steer_loaders_&_compact_track_loaders_specs"
cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Table '{table_name}' has been deleted successfully.")
 