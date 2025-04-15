import sqlite3

# Database and table details
DB_NAME = "equipment_data.db"
TABLE_NAME = "doosan_compact_excavators_specs"

def view_table_contents():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Retrieve all data from the table
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()
    
    # Retrieve column names
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    columns = [col[1] for col in cursor.fetchall()]
    
    conn.close()
    
    # Print column names
    print(" | ".join(columns))
    print("-" * 100)
    
    # Print rows
    for row in rows:
        print(" | ".join(str(item) if item is not None else "NULL" for item in row))

if __name__ == "__main__":
    view_table_contents()