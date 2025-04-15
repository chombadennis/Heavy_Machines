import requests
import sqlite3

DB_NAME = "equipment_data.db"

categories = [
    {
        "product_id": "0c962e82-7535-4a37-b378-3cc32766409a",  # Dozers
        "equipment_name": "Dozer",
        "table_name": "komatsu_dozer_specs"
    },
    {
        "product_id": "0f7454ca-af3c-4896-be0b-489b38600cb2",  # Excavators
        "equipment_name": "Excavator",
        "table_name": "komatsu_excavator_specs"
    },
    {
        "product_id": "ef074050-dd32-4a26-a4ae-60c94e38f327",  # Motor Graders
        "equipment_name": "Motor Grader",
        "table_name": "komatsu_motor_grader_specs"
    },
    {
        "product_id": "0d514d72-fd67-443c-a3a7-a4ab0289f1bb",  # Wheel Loaders
        "equipment_name": "Wheel Loader",
        "table_name": "komatsu_wheel_loader_specs"
    },
    {
        "product_id": "95503b0a-3166-4ce4-9203-120d88b68f29",  # Trucks
        "equipment_name": "Truck",
        "table_name": "komatsu_trucks_specs"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.komatsu.com/en/products/",
    "Accept-Encoding": "gzip, deflate, br"
}

def fetch_komatsu_data(product_id):
    url = f"https://www.komatsu.com/api/producttiles?product={product_id}&language=en"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def standardize_column_name(name):
    return name.lower().strip().replace(" ", "_").replace(".", "").replace("/", "_").replace("-", "_")

def process_komatsu_data(data, equipment_type):
    results = data.get("results", [])
    records = []
    all_columns = set(["equipment_type", "model", "image_url", "product_url"])  # Always include these

    for item in results:
        record = {
            "equipment_type": equipment_type,
            "model": item.get("name"),
            "image_url": item.get("image"),
            "product_url": f'https://www.komatsu.com{item.get("url", "")}'
        }

        specs = item.get("specifications", [])
        for spec in specs:
            col_name = standardize_column_name(spec.get("name", ""))
            value = spec.get("valueImperial") or spec.get("valueMetric")
            if col_name:
                record[col_name] = value
                all_columns.add(col_name)

        records.append(record)

    return records, all_columns

def save_to_sqlite(db_name, table_name, records, columns):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Drop table if it exists to avoid schema mismatch
    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}"')

    # Create table dynamically
    column_defs = ", ".join([f'"{col}" TEXT' for col in columns])
    create_query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({column_defs})'
    cursor.execute(create_query)

    placeholders = ", ".join(["?" for _ in columns])
    insert_query = f'INSERT INTO "{table_name}" ({",".join(columns)}) VALUES ({placeholders})'

    for record in records:
        row = [record.get(col, None) for col in columns]
        cursor.execute(insert_query, row)

    conn.commit()
    conn.close()

def run_multi_category_komatsu_scraper():
    for cat in categories:
        print(f"🔄 Fetching {cat['equipment_name']}...")
        try:
            data = fetch_komatsu_data(cat["product_id"])
            print(f"✅ Fetched data for {cat['equipment_name']}")

            records, columns = process_komatsu_data(data, cat["equipment_name"])
            save_to_sqlite(DB_NAME, cat["table_name"], records, columns)
            print(f"💾 Saved {len(records)} records to {cat['table_name']} ✅\n")
        except Exception as e:
            print(f"❌ Error fetching {cat['equipment_name']}: {e}")

if __name__ == "__main__":
    run_multi_category_komatsu_scraper()
# This script fetches Komatsu equipment data from the specified API and saves it to a SQLite database.
# It handles multiple categories of equipment, processes the data, and dynamically creates tables in the database.