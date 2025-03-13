import sqlite3
import pandas as pd

DB_NAME = "equipment_data.db"

def list_table_columns(db_name):
    """Connects to the SQLite database and prints column names for each table."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Loop through each table and display its column names
    for table in tables:
        table_name = table[0]
        print(f"\n--- Columns in {table_name} ---")

        # Fetch column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]  # Extract column names
        print(column_names)

    # Close the database connection
    conn.close()


def list_table_contents(db_name):
    """Connects to the SQLite database and prints contents of each table."""
    conn = sqlite3.connect(db_name)
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


# Run the functions
if __name__ == "__main__":
    list_table_contents(DB_NAME)
    list_table_columns(DB_NAME)
    