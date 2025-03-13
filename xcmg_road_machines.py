import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# URL and database details
URL = "http://en.xcmg.com/en-ap/ext/ajax_prolist.jsp"
DB_NAME = "equipment_data.db"
TABLE_NAME = "xcmg_road_machinery_data_specs"

# Headers for request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "http://en.xcmg.com/en-ap/product/Road-Machinery/pro-list-1000121.htm",
    "Origin": "http://en.xcmg.com",
}

# Function to fetch data from a specific page
def fetch_page_data(page):
    payload = {
        "flag": "1",
        "data1": "",
        "data2": "1000121",
        "data3": "",
        "data4": "",
        "data5": "",
        "data6": "",
        "nowPage": str(page)
    }
    
    response = requests.post(URL, data=payload, headers=HEADERS)
    return response.text if response.status_code == 200 else ""

# Function to parse equipment details and specifications
def parse_equipment_data(html):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    
    for item in soup.find_all("li", class_="span-4 midd-6"):  # Updated class
        model_tag = item.find("div", class_="tit").find("a")
        checkbox = item.find("input", class_="plp-item-constrast-chk")
        image_tag = item.find("img", class_="_full")
        
        if model_tag and checkbox:
            product_data = {
                "Equipment_Type": checkbox["data-title"].strip(),
                "Model": checkbox["data-name"].strip(),
                "Image_URL": f"http://en.xcmg.com{image_tag['src']}" if image_tag and image_tag.has_attr('src') else None
            }
            
            # Extract specifications from <li class="fix">
            specs = item.find_all("li", class_="fix")
            for spec in specs:
                spec_name = spec.find("div", class_="l").get_text(strip=True)  # Get spec name
                spec_value = spec.find("div", class_="r").get_text(strip=True)  # Get spec value

                # Normalize spec names (replace spaces and special characters)
                normalized_spec_name = spec_name.lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
                product_data[normalized_spec_name] = spec_value  # Add to dictionary
            
            products.append(product_data)
    
    return products

# Function to create SQLite table dynamically if it doesn't exist
def create_sql_table(cursor, columns):
    column_defs = ", ".join([f'"{col}" TEXT' for col in columns])  # Use double quotes for safety
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {column_defs}
        )
    """)

# Function to save data into SQLite
def save_to_sqlite(data):
    if not data:
        print("No data to save.")
        return
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Get all unique columns from extracted data
    all_columns = set()
    for row in data:
        all_columns.update(row.keys())

    all_columns = sorted(all_columns)  # Ensure consistent order
    create_sql_table(cursor, all_columns)  # Ensure table exists with correct schema

    placeholders = ", ".join(["?" for _ in all_columns])
    column_names = ", ".join([f'"{col}"' for col in all_columns])  # Enclose column names in quotes
    insert_query = f'INSERT INTO {TABLE_NAME} ({column_names}) VALUES ({placeholders})'

    for row in data:
        row_values = [row.get(col, None) for col in all_columns]  # Ensure all columns are present
        cursor.execute(insert_query, row_values)
    
    conn.commit()
    conn.close()
    print(f"Data saved to {DB_NAME}, Table: {TABLE_NAME}")

# Main function to scrape multiple pages and save data
def main():
    all_data = []
    
    for page in range(1, 30):  # Extracts pages 1 to 29
        print(f"Fetching page {page}...")
        html = fetch_page_data(page)
        if html:
            page_data = parse_equipment_data(html)
            print(f"Extracted {len(page_data)} records from page {page}")
            all_data.extend(page_data)
        time.sleep(1)  # Pause to prevent overwhelming the server
    
    if not all_data:
        print("No data was extracted. Check the scraper.")
        return

    print(f"Total extracted records: {len(all_data)}")
    print("Sample record:", all_data[0] if all_data else "No records")

    save_to_sqlite(all_data)
    
    print("Scraping complete.")

if __name__ == "__main__":
    main()
