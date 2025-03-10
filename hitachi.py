import requests
import sqlite3
import json
from bs4 import BeautifulSoup

# SQLite Database
DB_NAME = "equipment_data.db"

# List of category pages to scrape
CATEGORY_PAGES = [
    {"category": "medium_large_wheel_loaders",
     "url": "https://www.hitachicm.com/us/en/products/wheel-loaders/medium-large/",
     "json_api": "https://www.hitachicm.com/content/hitachicm/us/en/products/wheel-loaders/medium-large/jcr:content/root/containercomponent/productlisting.json"},
    {"category": "compact_wheel_loaders",
     "url": "https://www.hitachicm.com/us/en/products/wheel-loaders/compact/",
     "json_api": "https://www.hitachicm.com/content/hitachicm/us/en/products/wheel-loaders/compact/jcr:content/root/containercomponent/productlisting.json"},
    {"category": "medium_large_excavators",
     "url": "https://www.hitachicm.com/us/en/products/excavators/medium-large/",
     "json_api": "https://www.hitachicm.com/content/hitachicm/us/en/products/excavators/medium-large/jcr:content/root/containercomponent/productlisting.json"},
    {"category": "compact_excavators",
     "url": "https://www.hitachicm.com/us/en/products/excavators/compact/",
     "json_api": "https://www.hitachicm.com/content/hitachicm/us/en/products/excavators/compact/jcr:content/root/containercomponent/productlisting.json"},
    {"category": "mining_excavators",
     "url": "https://www.hitachicm.com/us/en/products/excavators/mining/",
     "json_api": "https://www.hitachicm.com/content/hitachicm/us/en/products/excavators/mining/jcr:content/root/containercomponent/productlisting.json"}, 
    {"category": "super_long_front_excavators",
     "url": "https://www.hitachicm.com/us/en/products/excavators/special-applications/slf/",
     "json_api": "https://www.hitachicm.com/content/hitachicm/us/en/products/excavators/special-applications/slf/jcr:content/root/containercomponent/productlisting.json"},
    {"category": "rigid_dump_trucks",
     "url": "https://www.hitachicm.com/us/en/products/rigid-dump-trucks/",
     "json_api": "https://www.hitachicm.com/content/hitachicm/us/en/products/rigid-dump-trucks/jcr:content/root/containercomponent/productlisting.json"}
]

# Connect to SQLite
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    return conn, conn.cursor()

# Delete table if it exists
def delete_table(cursor, table_name):
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# Ensure the table exists for each category
def create_table(cursor, table_name, columns):
    delete_table(cursor, table_name)  # Ensure table is completely removed before recreating
    columns_sql = ", ".join([f"{col} TEXT" for col in columns])
    cursor.execute(f"""
        CREATE TABLE {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_model_name TEXT,
            product_display_name TEXT,
            image_url TEXT,
            product_page_url TEXT,
            {columns_sql}
        )
    """)

# Fetch JSON Data
def fetch_data(json_api_url):
    response = requests.get(json_api_url)
    if response.status_code != 200:
        print(f"Failed to fetch data from {json_api_url}")
        return []
    return response.json()

# Sanitize column names to be SQLite compatible
def sanitize_column_name(name):
    return name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").replace(".", "")

# Insert Data
def insert_data(cursor, table_name, data):
    for item in data:
        product_model_name = item["productModelName"]
        product_display_name = item["productDisplayName"]
        image_url = item["productListingAsset"]
        product_page_url = "https://www.hitachicm.com" + item["prodPagePath"]
        
        feature_values = {}
        for feature in item.get("prodFeatures", []):
            column_name = sanitize_column_name(feature["featureTitle"])
            feature_values[column_name] = feature["featureFinalValue"]
        
        columns = ["product_model_name", "product_display_name", "image_url", "product_page_url"] + list(feature_values.keys())
        values_placeholders = ", ".join(["?"] * len(columns))
        values = [product_model_name, product_display_name, image_url, product_page_url] + list(feature_values.values())
        
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({values_placeholders})", values)

# Main function
def main():
    conn, cursor = connect_db()
    
    for category in CATEGORY_PAGES:
        table_name = category["category"]
        data = fetch_data(category["json_api"])
        if not data:
            continue
        
        feature_columns = set()
        for item in data:
            for feature in item.get("prodFeatures", []):
                feature_columns.add(sanitize_column_name(feature["featureTitle"]))
        
        create_table(cursor, table_name, feature_columns)
        insert_data(cursor, table_name, data)
        conn.commit()
        print(f"Successfully stored data for category: {table_name}")
    
    conn.close()
    print("All data successfully saved to SQLite!")

if __name__ == "__main__":
    main()
