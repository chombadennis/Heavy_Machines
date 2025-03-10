import sqlite3

def delete_table(db_name, table_name):
    """Deletes the specified table from the SQLite database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.commit()
    conn.close()
    
    print(f"Table '{table_name}' has been deleted successfully.")

# Usage
delete_table("equipment_data.db", "hitachi_equipment_specs")

