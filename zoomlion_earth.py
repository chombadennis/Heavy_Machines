import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# URL and database details
URL = "https://en-product.zoomlion.com/ext/ajax_proList.jsp"
DB_NAME = "equipment_data.db"
TABLE_NAME = "zoomlion_earthmoving_equipment_specs"

# Headers for request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://en-product.zoomlion.com/product/pro_list.htm?sCat=57",
    "Origin": "https://en-product.zoomlion.com",
}

# Function to fetch data from a specific page
def fetch_page_data(page):
    payload = {
        "flag": "pro",
        "sCat": "57",
        "tCat": "",
        "htzParam": "[]",
        "key": "",
        "chanelld": "22482",
        "nowPage": str(page),
        "page_size": "6"
    }
    
    response = requests.post(URL, data=payload, headers=HEADERS)
    return response.text if response.status_code == 200 else ""

# Function to parse equipment details
def parse_equipment_data(html):
    soup = BeautifulSoup(html, "html.parser")
    products = []
    
    for item in soup.find_all("li"):
        name = item.find("div", class_="tit tit22")
        category = item.find("div", class_="con con16")
        specs = item.find_all("div", class_="line line01 con16")

        # Extract specifications
        weight = power = capacity = None
        for spec in specs:
            text = spec.text.strip()
            if "Operating weight" in text:
                weight = spec.find("span", class_="num num01").text.strip()
            elif "Rated power" in text:
                power = spec.find("span", class_="num num01").text.strip()
            elif "Standard capacity" in text:
                capacity = spec.find("span", class_="num num01").text.strip()

        if name and category:
            products.append({
                "Equipment Type": category.text.strip(),
                "Model": name.text.strip(),
                "Operating Weight": weight,
                "Rated Power": power,
                "Standard Capacity": capacity,
            })
    
    return products

# Function to create SQLite table if it doesn't exist
def create_sql_table(cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "Equipment Type" TEXT,
            "Model" TEXT,
            "Operating Weight" TEXT,
            "Rated Power" TEXT,
            "Standard Capacity" TEXT
        )
    """)

# Function to save data into SQLite
def save_to_sqlite(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    create_sql_table(cursor)

    for row in data:
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} ("Equipment Type", "Model", "Operating Weight", "Rated Power", "Standard Capacity")
            VALUES (?, ?, ?, ?, ?)
        """, tuple(row.values()))

    conn.commit()
    conn.close()
    print(f"Data saved to {DB_NAME}, Table: {TABLE_NAME}")

# Main function to scrape multiple pages and save data
def main():
    all_data = []
    
    for page in range(1, 7):  # Extracts pages 1 to 6
        print(f"Fetching page {page}...")
        html = fetch_page_data(page)
        if html:
            all_data.extend(parse_equipment_data(html))
        time.sleep(1)  # Pause to prevent overwhelming the server

    if all_data:
        save_to_sqlite(all_data)

    print("Scraping complete.")

# Run script
if __name__ == "__main__":
    main()
