import requests
from bs4 import BeautifulSoup
import re
import sqlite3
from urllib.parse import urljoin
from collections import defaultdict

BASE_URLS = {
    "excavators": "https://www.volvoce.com/africa/en-za/products/excavators/",
    "wheel_loaders": "https://www.volvoce.com/africa/en-za/products/wheel-loaders/",
    "articulated haulers": "https://www.volvoce.com/africa/en-za/products/articulated-haulers/",
    "rigid haulers": "https://www.volvoce.com/africa/en-za/products/rigid-haulers/",
    "pipelayers": "https://www.volvoce.com/africa/en-za/products/pipelayers/",
}

MODEL_SUFFIXES = {
    "excavators": [
        "ec750d", "ec950e", "ec550e", "ec480d", "ec380d", "ec360", "ec350d", "ec300d",
        "ec250d", "ec230", "ec220d", "ec220", "ec210d", "ec210", "ec200d", "ec140d",
        "ew205d", "ew145b-prime", "ec75d", "ec55d", "ec27d"
    ],
    "wheel_loaders": [
        "L350H", "L260H", "L220H", "l200h-high-lift", "L180H", "L150H",
        "L120H", "L110H", "l90h", "l70h", "L60H"
    ],
    "articulated haulers": [
        "A60H", "A50", "A45", "A40", "A35", "A30G", "A25G"
    ],
    "rigid haulers": [
        "R100E", "R70D", "R60D"
    ],
    "pipelayers": [
        "PL4809D", "PL3005E"
    ]
}

DB_NAME = "equipment_data.db"
TABLE_NAME = "volvo_equipment_specs"

def extract_specifications(soup):
    specs = {}
    rows = soup.select("table tbody tr")
    for row in rows:
        header = row.find("th")
        value_td = row.find("td")
        if header and value_td:
            key = header.get_text(strip=True)
            val = " ".join(span.get_text(strip=True) for span in value_td.find_all(['span', 'td']) if span.get_text(strip=True))
            if not val:
                val = value_td.get_text(strip=True)
            specs[key] = val
    return specs

def extract_equipment_name_and_model(soup):
    name = None
    model = None
    candidates = soup.find_all(["vcdk-typography", "h1", "h2", "span", "div"])
    for tag in candidates:
        if not name and tag.get("variant") == "caption1":
            name = tag.get_text(strip=True)
        elif not model and tag.get("variant") == "heading2":
            model = tag.get_text(strip=True)
        if not model and tag.name in ["h1", "h2"] and "model" in tag.text.lower():
            model = tag.get_text(strip=True)
        if name and model:
            break
    return name, model

def extract_brochure_link(soup, base_url):
    pdf_links = soup.find_all("a", href=True)
    for link in pdf_links:
        href = link["href"]
        if href.endswith(".pdf"):
            return urljoin(base_url, href)
    return None

def make_unique_column_names(keys):
    seen = {}
    unique_keys = []
    for key in keys:
        original_key = key
        count = seen.get(key, 0)
        while key in seen:
            count += 1
            key = f"{original_key}_{count}"
        seen[key] = 1
        unique_keys.append(key)
    return unique_keys



def save_to_sqlite_dynamic(data, db_name, table_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 1. Collect all columns for deduplication (Normalize case)
    key_counter = defaultdict(int)
    original_to_safe = {}

    for row in data:
        for key in row.keys():
            base_key = re.sub(r"[^\w]+", "_", key.strip()).lower()  # Normalize to lowercase
            safe_key = base_key
            while safe_key in original_to_safe.values():
                key_counter[base_key] += 1
                safe_key = f"{base_key}_{key_counter[base_key]}"
            if key not in original_to_safe:
                original_to_safe[key] = safe_key

    # 2. Prepare CREATE TABLE statement with unique columns
    final_cols = list(original_to_safe.values())
    col_defs = ", ".join([f'"{col}" TEXT' for col in final_cols])

    # Log the final column names to ensure no duplicates
    print(f"Final columns for table {table_name}: {final_cols}")

    # Check if table exists
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    table_exists = cursor.fetchone() is not None

    if not table_exists:
        # Create table with full schema
        cursor.execute(f'CREATE TABLE "{table_name}" ({col_defs})')
    else:
        # Get existing columns
        cursor.execute(f'PRAGMA table_info("{table_name}")')
        existing_cols = [row[1] for row in cursor.fetchall()]

        # Add any new columns
        for col in final_cols:
            if col not in existing_cols:
                cursor.execute(f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" TEXT')

    # 3. Insert data using mapped column names
    for row in data:
        row_data = {original_to_safe[k]: v for k, v in row.items() if k in original_to_safe}
        columns = ", ".join([f'"{col}"' for col in final_cols])
        placeholders = ", ".join(["?" for _ in final_cols])
        values = [row_data.get(col, None) for col in final_cols]
        cursor.execute(f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})', values)

    conn.commit()
    conn.close()

def scrape_volvo_equipment():
    all_data = []

    for category, base_url in BASE_URLS.items():
        for suffix in MODEL_SUFFIXES.get(category, []):
            url = f"{base_url}{suffix}/"
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                name, model = extract_equipment_name_and_model(soup)
                specs = extract_specifications(soup)
                brochure_link = extract_brochure_link(soup, url)

                row = {
                    "equipment_name": name,
                    "model": model,
                }
                row.update(specs)
                row["brochure_link"] = brochure_link
                all_data.append(row)

                print(f"[✓] Scraped {name or 'UNKNOWN'} ({model or 'UNKNOWN'})")

            except Exception as e:
                print(f"[!] Failed to scrape {url}: {e}")

    if all_data:
        save_to_sqlite_dynamic(all_data, DB_NAME, TABLE_NAME)
        print(f"\n✅ Saved {len(all_data)} records to '{TABLE_NAME}' in '{DB_NAME}'.")

if __name__ == "__main__":
    scrape_volvo_equipment()
