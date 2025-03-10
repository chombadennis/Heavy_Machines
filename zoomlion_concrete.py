import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# URL and database details
URL = "https://en-product.zoomlion.com/ext/ajax_proList.jsp"
DB_NAME = "equipment_data.db"
TABLE_NAME = "zoomlion_concrete_equipment_specs"

# Headers for request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://en-product.zoomlion.com/product/pro_list.htm?sCat=55",
    "Origin": "https://en-product.zoomlion.com",
}

# Function to fetch data from a specific page
def fetch_page_data(page):
    payload = {
        "flag": "pro",
        "sCat": "55",
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
        theoretical_rated_output = discharge_height = the_capacity_of_aggregate_storage_hopper = max_theorical_output = max_theorical_pressure_on_concrete = rated_power = power = max_vertical_reach = agitator_capacity = max_rotation_speed = power_rating = None
        for spec in specs:
            text = spec.text.strip()
            if "Theoretical Rated Output" in text:
                theoretical_rated_output = spec.find("span", class_="num num01").text.strip()
            elif "Discharge Height" in text:
                discharge_height = spec.find("span", class_="num num01").text.strip()
            elif "The Capacity of Aggregate Storage Hopper" in text:
                the_capacity_of_aggregate_storage_hopper = spec.find("span", class_="num num01").text.strip()
            elif "Maximum theorical output" in text:
                max_rotation_speed = spec.find("span", class_="num num01").text.strip()
            elif "Maximum theorical pressure on concrete" in text:
                max_theorical_pressure_on_concrete = spec.find("span", class_="num num01").text.strip()
            elif "Rated power" in text:
                rated_power = spec.find("span", class_="num num01").text.strip()
            elif "Power" in text:
                power = spec.find("span", class_="num num01").text.strip()
            elif "Maxiumm vertical reach" in text:
                max_vertical_reach = spec.find("span", class_="num num01").text.strip()
            elif "Agitator Capacity" in text:
                agitator_capacity = spec.find("span", class_="num num01").text.strip()
            elif "Max. Rotation Speed" in text:
                max_rotation_speed = spec.find("span", class_="num num01").text.strip()
            elif "Power Rating" in text:
                power_rating = spec.find("span", class_="num num01").text.strip()
                      


        if name and category:
            products.append({
                "Equipment Type": category.text.strip(),
                "Model": name.text.strip(),
                "Theoretical Rated Output": theoretical_rated_output,
                "Discharge Height": discharge_height,
                "The Capacity of Aggregate Storage Hopper": the_capacity_of_aggregate_storage_hopper,
                "Maximum Theorical Output": max_theorical_output,
                "Maximum Theorical Pressure on Concrete": max_theorical_pressure_on_concrete,
                "Rated Power": rated_power,
                "Power": power,
                "Maxiumm Vertical Reach": max_vertical_reach,
                "Agitator Capacity": agitator_capacity,
                "Max. Rotation Speed": max_rotation_speed,
                "Power Rating": power_rating,
            })
    
    return products

# Function to create SQLite table if it doesn't exist
def create_sql_table(cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "Equipment Type" TEXT,
            "Model" TEXT,
            "Theoretical Rated Output" TEXT,
            "Discharge Height" TEXT,
            "The Capacity of Aggregate Storage Hopper" TEXT,
            "Maximum Theorical Output" TEXT,
            "Maximum Theorical Pressure on Concrete" TEXT,
            "Rated Power" TEXT,
            "Power" TEXT,
            "Maxiumm Vertical Reach" TEXT,
            "Agitator Capacity" TEXT,
            "Max. Rotation Speed" TEXT,
            "Power Rating" TEXT
        )
    """)

# Function to save data into SQLite
def save_to_sqlite(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    create_sql_table(cursor)

    for row in data:
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} ("Equipment Type", "Model", "Theoretical Rated Output", "Discharge Height", "The Capacity of Aggregate Storage Hopper", "Maximum Theorical Output", "Maximum Theorical Pressure on Concrete", "Rated Power", "Power", "Maxiumm Vertical Reach", "Agitator Capacity", "Max. Rotation Speed", "Power Rating")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row.values()))

    conn.commit()
    conn.close()
    print(f"Data saved to {DB_NAME}, Table: {TABLE_NAME}")

# Main function to scrape multiple pages and save data
def main():
    all_data = []
    
    for page in range(1, 10):  # Extracts pages 1 to 9
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
