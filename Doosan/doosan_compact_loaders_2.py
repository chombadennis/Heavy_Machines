import requests
import sqlite3
import re
import sys

# Configuration
DB_PATH = "equipment_data.db"  
TABLE_NAME = "doosan_compact_loader_specs"

# Endpoints for each loader type
LOADERS = {
    "Skid Steer Loader": {
        "url": "https://bobcat.api.bobcat.com/search/product",
        "params": {
            "region": "eu",
            "category": "Loaders",
            "subcategory": "Skid Steer loaders",  # spaces will be URL encoded
            "hideSelectedVariants": "false",
            "facetCategory": "/bobcat/eu/products/Skid-Steer-Loaders",
            "lang": "en",
            "from": "0",
            "size": "12",
            "sort": "name.keyword:asc"
        }
    },
    "Small Articulated Loader": {
        "url": "https://bobcat.api.bobcat.com/search/product",
        "params": {
            "region": "eu",
            "category": "Loaders",
            "subcategory": "Small Articulated Loader",
            "hideSelectedVariants": "false",
            "facetCategory": "/bobcat/eu/products/Small-Articulated-Loader",
            "lang": "en",
            "from": "0",
            "size": "100",
            "sort": "name.keyword:asc"
        }
    },
    "Compact Wheel loader": {
        "url": "https://bobcat.api.bobcat.com/search/product",
        "params": {
            "region": "eu",
            "category": "Loaders",
            "subcategory": "Compact Wheel Loaders",
            "hideSelectedVariants": "false",
            "facetCategory": "/bobcat/eu/products/Compact-wheel-loaders",
            "lang": "en",
            "from": "0",
            "size": "100",
            "sort": "name.keyword:asc"
        }
    },
    "Compact Track Loader": {
        "url": "https://bobcat.api.bobcat.com/search/product",
        "params": {
            "region": "eu",
            "category": "Loaders",
            "subcategory": "Compact Track Loaders",
            "hideSelectedVariants": "false",
            "facetCategory": "/bobcat/eu/products/Compact-tracked-loaders",
            "lang": "en",
            "from": "0",
            "size": "100",
            "sort": "name.keyword:asc"
        }
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*"
}

def normalize_column_name(name):
    """Convert key names to lower-case snake_case strings for columns."""
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name.lower()

def fetch_loader_data(loader_type, endpoint_info):
    """Fetch JSON data from the API endpoint and extract product records."""
    try:
        response = requests.get(endpoint_info["url"], headers=HEADERS, params=endpoint_info["params"])
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to fetch data for {loader_type}: {e}")
        return []
    
    try:
        data = response.json()
    except Exception as e:
        print(f"[ERROR] JSON decode error for {loader_type}: {e}")
        print(f"Response (first 500 chars): {response.text[:500]}")
        return []
    
    # Check for known keys:
    products = []
    if isinstance(data, dict):
        if "items" in data:
            products = data["items"]
        elif "results" in data:
            products = data["results"]
        else:
            print(f"[WARNING] Unexpected JSON structure for {loader_type}. Keys found: {list(data.keys())}")
            products = []
    elif isinstance(data, list):
        products = data
    else:
        print(f"[WARNING] Unexpected JSON type for {loader_type}.")
    
    if not products:
        print(f"[WARNING] No records found for {loader_type}.")
    
    records = []
    for product in products:
        record = {}
        record["equipment_name"] = product.get("name")
        record["model"] = product.get("id")
        record["loader_type"] = loader_type
        # Process keyProperties, if present
        key_props = product.get("keyProperties", [])
        for prop in key_props:
            key = prop.get("key")
            if key:
                col_name = normalize_column_name(key)
                value = prop.get("value")
                unit = prop.get("unit", "")
                record[col_name] = f"{value} {unit}".strip() if unit else value
        records.append(record)
    return records

def create_or_update_table(conn, record):
    """Create the table if missing and add any new dynamic columns based on the record."""
    cursor = conn.cursor()
    base_columns = {"loader_type": "TEXT", "equipment_name": "TEXT", "model": "TEXT"}
    dynamic_cols = {k: "TEXT" for k in record.keys() if k not in base_columns}
    
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}';")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        all_cols = {**base_columns, **dynamic_cols}
        col_defs = ", ".join([f'"{col}" {ctype}' for col, ctype in all_cols.items()])
        create_sql = f"CREATE TABLE {TABLE_NAME} (id INTEGER PRIMARY KEY AUTOINCREMENT, {col_defs});"
        try:
            cursor.execute(create_sql)
            conn.commit()
        except Exception as e:
            print(f"[ERROR] Creating table failed: {e}")
    else:
        cursor.execute(f"PRAGMA table_info({TABLE_NAME});")
        existing_cols = {row[1] for row in cursor.fetchall()}
        for col, col_type in dynamic_cols.items():
            if col not in existing_cols:
                alter_sql = f'ALTER TABLE {TABLE_NAME} ADD COLUMN "{col}" {col_type};'
                try:
                    cursor.execute(alter_sql)
                except Exception as e:
                    print(f"[WARNING] Could not add column {col}: {e}")
        conn.commit()

def insert_record(conn, record):
    """Insert a record dictionary into the table."""
    cursor = conn.cursor()
    keys = list(record.keys())
    columns = ", ".join([f'"{k}"' for k in keys])
    placeholders = ", ".join(["?"] * len(keys))
    sql = f'INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})'
    values = [record[k] for k in keys]
    try:
        cursor.execute(sql, values)
        conn.commit()
    except Exception as e:
        print(f"[ERROR] Inserting record {record} failed: {e}")
        conn.rollback()

def main():
    try:
        conn = sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"[ERROR] Unable to connect to database {DB_PATH}: {e}")
        sys.exit(1)
    
    total_records = 0
    for loader_type, endpoint_info in LOADERS.items():
        print(f"Fetching data for: {loader_type}")
        records = fetch_loader_data(loader_type, endpoint_info)
        for rec in records:
            create_or_update_table(conn, rec)
            insert_record(conn, rec)
            total_records += 1
    conn.close()
    print(f"✅ Data extraction complete! Total records inserted: {total_records}")

if __name__ == "__main__":
    main()
# This script fetches data from the Bobcat API for Doosan compact loaders,
# processes the data, and stores it in an SQLite database.