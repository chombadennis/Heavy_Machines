import sqlite3

# Connect to the SQLite database
db_path = "equipment_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Drop the table if it exists
table_name = "doosan_compact_excavators_specs"
cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Table '{table_name}' has been deleted successfully.")
