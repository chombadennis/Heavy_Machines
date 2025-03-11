import requests
import sqlite3
import time

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

# Retry settings
MAX_RETRIES = 5
SLEEP_TIME = 5  # seconds

# Database path
DB_PATH = "equipment_data.db"


def fetch_cat_data(url):
    """Fetches JSON data from the CAT equipment API with retries."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Attempt {attempt + 1}: Received status code {response.status_code}")
        except requests.exceptions.ReadTimeout:
            print(f"Attempt {attempt + 1}: Request timed out. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1}: Request failed - {e}")
            break
        time.sleep(SLEEP_TIME)
    return None  # Failed after all retries


def save_to_sqlite(data, table_name):
    """Creates a table dynamically and inserts equipment data into SQLite."""
    if not data:
        print(f"No data available for {table_name}. Skipping...")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Extract all possible specification names dynamically
    spec_columns = set()
    for model in data.get("models", []):
        for spec in model.get("specs", []):
            spec_columns.add(spec["spec_name"])

    # Create table dynamically with properly quoted column names
    base_columns = ['"model_name" TEXT', '"product_family" TEXT', '"product_category" TEXT']
    spec_columns_sql = ", ".join([f'"{col}" TEXT' for col in spec_columns])
    
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS "{table_name}" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            {", ".join(base_columns + [spec_columns_sql])}
        )
    ''')

    # Insert data into SQLite
    for model in data.get("models", []):
        model_name = model.get("model_name", "")
        product_family = model.get("productFamily", "")
        product_category = model.get("productCategory", "").split("/")[-1]  # Extract last part

        # Extract specs dynamically
        specs = {spec["spec_name"]: spec["spec_value"][0] for spec in model.get("specs", [])}

        # Prepare data for insertion
        all_columns = ['"model_name"', '"product_family"', '"product_category"'] + [f'"{col}"' for col in specs.keys()]
        values = [model_name, product_family, product_category] + list(specs.values())
        placeholders = ", ".join(["?"] * len(values))

        # Insert into database
        cursor.execute(f'''
            INSERT INTO "{table_name}" ({", ".join(all_columns)}) VALUES ({placeholders})
        ''', values)

    # Commit and close connection
    conn.commit()
    conn.close()

    print(f"Data successfully saved to table '{table_name}' in SQLite database.")


# URLs for different CAT equipment categories
equipment_urls = {
    "cat_articulated_trucks_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/articulated-trucks/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_asphalt_pavers_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/asphalt-pavers/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_backhoe_loaders_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/backhoe-loaders/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_cold_planers_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/cold-planers/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_compactors_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/compactors/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_dozer_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/dozers/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_excavators_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/excavators/jcr:content/root/responsivegrid/productcards.feed.json",	
    "cat_material_handlers_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/material-handlers/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_motor_graders_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/motor-graders/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_off_highway_trucks_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/off-highway-trucks/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_pipelayers_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/pipelayers/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_road_reclaimers_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/road-reclaimers/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_skid_steer_and_compact_track_loaders_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/skid-steer-and-compact-track-loaders/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_telehandlers_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/telehandlers/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_track_loaders_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/track-loaders/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_underground_hard_rock_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/underground-hard-rock/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_wheel_tractor_scrapers_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/wheel-tractor-scrapers/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_wheel_loaders_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/wheel-loaders/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_draglines_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/draglines/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_forest_machines_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/forest-machines/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_hydraulic_mining_shovels_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/hydraulic-mining-shovels/jcr:content/root/responsivegrid/productcards.feed.json",	
    "cat_drills_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/drills/jcr:content/root/responsivegrid/productcards.feed.json",
    "cat_electric_rope_shovels_specs": "https://www.cat.com/content/catdotcom/en_US/products/new/equipment/electric-rope-shovels/jcr:content/root/responsivegrid/productcards.feed.json"
}

# Process each equipment category
for table, url in equipment_urls.items():
    print(f"Fetching data for {table}...")
    data = fetch_cat_data(url)
    save_to_sqlite(data, table)
