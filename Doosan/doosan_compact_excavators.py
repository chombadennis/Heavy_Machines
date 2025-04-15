import requests
import sqlite3
import time
import re

# SQLite DB and table setup
DB_PATH = "equipment_data.db"
TABLE_NAME = "doosan_compact_excavators_specs"

# API headers
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "origin": "https://www.bobcat.com",
    "referer": "https://www.bobcat.com/",
    "user-agent": "Mozilla/5.0"
}

# Helper to normalize spec keys
def normalize_key(label, unit=None):
    key = label.strip().lower().replace(" ", "_").replace("-", "_")
    if unit:
        unit = unit.lower().replace("/", "_per_").replace("%", "percent")
        key += f"_{unit}"
    return key

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ensure table exists
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    model TEXT,
    series TEXT,
    category TEXT,
    equipment_type TEXT
)
""")
conn.commit()

# Known model codes and their corresponding URLs
model_data = [
    {"model_code": "B4PC", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/0-1t-mini-excavators/e08"},
    {"model_code": "B55N", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-1t-mini-excavators/e10e"},
    {"model_code": "B4PD", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/0-1t-mini-excavators/e10z"},
    {"model_code": "B5NU", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e16-new"},
    {"model_code": "B61", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e17"},
    {"model_code": "B5VD", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e17z"},
    {"model_code": "B5NW", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e17z-new"},
    {"model_code": "B5VF", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e19"},
    {"model_code": "B5NV", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e19-new"},
    {"model_code": "B5VU", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e19e"},
    {"model_code": "B5VH", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e20z"},
    {"model_code": "B5NY", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/1-2t-mini-excavators/e20z-new"},
    {"model_code": "B5W6", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/2-3t-mini-excavators/e26"},
    {"model_code": "B4BA", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/2-3t-mini-excavators/e27"},
    {"model_code": "B5W7", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/2-3t-mini-excavators/e27z-new"},
    {"model_code": "B3Y3", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/3-4t-mini-excavators/e34"},
    {"model_code": "B3Y4", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/3-4t-mini-excavators/e35z"},
    {"model_code": "B4HT", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/4-6t-mini-excavators/e50z"},
    {"model_code": "B4HU", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/4-6t-mini-excavators/e55Z"},   
    {"model_code": "B54A", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/4-6t-mini-excavators/e57W"}, 
    {"model_code": "B4HV", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/4-6t-mini-excavators/e60"},
    {"model_code": "B62N", "url": "https://www.bobcat.com/eu/en/equipment/mini-excavators/6-10t-mini-excavators/e88"},    
    # Add more models as needed
]

# Extract category from URL
def extract_category(url):
    match = re.search(r'/equipment/mini-excavators/([^/]+)/', url)
    if match:
        return match.group(1).replace('-', ' ')
    return "Unknown"

# Fetch and parse specs
def fetch_specs(model_info):
    model_code = model_info["model_code"]
    url = f"https://bobcat.api.bobcat.com/products/bobcat/{model_code}/specs"
    params = {
        "uom": "us",
        "locale": "en-GB",
        "businessUnit": "emea",
        "region": "eu",
        "specLevel": "3",
        "modelType": "product",
        "instance": "public",
        "noerror": "true",
        "lang": "en",
        "productDetailsDataSource": "default"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch specs for model code {model_code}")
        return

    data = response.json()
    if not isinstance(data, dict) or "sections" not in data:
        print(f"Unexpected spec structure for model code {model_code}. Keys: {list(data.keys())}")
        return

    specs = {
        "model": data.get("name", "Unknown"),
        "series": "R2-Series",  # Assuming R2-Series; adjust as needed
        "category": extract_category(model_info["url"]),
        "equipment_type": "Mini Excavator"
    }

    for section in data.get("sections", []):
        for prop in section.get("properties", []):
            label = prop.get("label")
            value = prop.get("value")
            unit = prop.get("unit")
            if label and value is not None:
                col = normalize_key(label, unit)
                specs[col] = str(value).strip()

    save_to_db(specs)

# Insert or update row
def save_to_db(specs):
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    existing_columns = {col[1] for col in cursor.fetchall()}

    # Add any new columns dynamically (properly quoted)
    for key in specs.keys():
        if key not in existing_columns:
            cursor.execute(f'ALTER TABLE {TABLE_NAME} ADD COLUMN "{key}" TEXT')

    # Insert data (columns also quoted)
    columns = ', '.join([f'"{col}"' for col in specs.keys()])
    placeholders = ', '.join(['?'] * len(specs))
    values = list(specs.values())

    cursor.execute(f"""
        INSERT INTO {TABLE_NAME} ({columns})
        VALUES ({placeholders})
    """, values)
    conn.commit()


# Main
if __name__ == "__main__":
    print("Fetching compact excavator models...")
    for model_info in model_data:
        fetch_specs(model_info)
        time.sleep(1)  # avoid rate-limiting

    print("All specs extracted and saved.")
    conn.close()
