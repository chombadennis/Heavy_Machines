import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# URL and database details
URL = "https://en-product.zoomlion.com/ext/ajax_proList.jsp"
DB_NAME = "equipment_data.db"
TABLE_NAME = "zoomlion_towercrane_equipment_specs"

# Headers for request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://en-product.zoomlion.com/product/pro_list.htm?sCat=56",
    "Origin": "https://en-product.zoomlion.com",
}

# Function to fetch data from a specific page
def fetch_page_data(page):
    payload = {
        "flag": "pro",
        "sCat": "56",
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
        working_radius = max_hoisting_capacity = max_Free_Standing_Height = max_jib_length = max_tip_load = tip_load = max_FSH_L69 = max_FSH_RB = max_working_radius = max_FSH_L68 = max_FSH_RA = max_free_standing_height_2 = max_boom_length = max_hoisting_capacity_at_jib_end = capacity = speed = cage_size =  None
        for spec in specs:
            text = spec.text.strip()
            if "Working Radius" in text:
                working_radius = spec.find("span", class_="num num01").text.strip()
            elif "Max. Hoisting Capacity" in text:
                max_hoisting_capacity = spec.find("span", class_="num num01").text.strip()
            elif "Max. Free Standing Height" in text:
                max_Free_Standing_Height = spec.find("span", class_="num num01").text.strip()
            elif "Max. Jib Length" in text:
                max_jib_length = spec.find("span", class_="num num01").text.strip()
            elif "Max. Tip Load" in text:
                max_tip_load = spec.find("span", class_="num num01").text.strip()
            elif "Tip Load" in text:
                tip_load = spec.find("span", class_="num num01").text.strip()
            elif "Maximum FSH [L69]" in text:
                max_FSH_L69 = spec.find("span", class_="num num01").text.strip()
            elif "Maximum FSH [RB]" in text:
                max_FSH_RB = spec.find("span", class_="num num01").text.strip()
            elif "Maximum Working Radius" in text:
                max_working_radius = spec.find("span", class_="num num01").text.strip()
            elif "Maximum FSH [L68]" in text:
                max_FSH_L68 = spec.find("span", class_="num num01").text.strip()
            elif "Maximum FSH [RA]" in text:
                max_FSH_RA = spec.find("span", class_="num num01").text.strip()
            elif "Max. free standing height" in text:
                max_free_standing_height_2 = spec.find("span", class_="num num01").text.strip()
            elif "Max. boom length" in text:
                max_boom_length = spec.find("span", class_="num num01").text.strip()
            elif "Max. hoisting capacity at jib end" in text:
                max_hoisting_capacity_at_jib_end = spec.find("span", class_="num num01").text.strip()
            elif "Capacity" in text:
                capacity = spec.find("span", class_="num num01").text.strip()
            elif "Speed" in text:
                speed = spec.find("span", class_="num num01").text.strip()
            elif "Cage Size" in text:
                cage_size = spec.find("span", class_="num num01").text.strip()
                 


        if name and category:
            products.append({
                "Equipment Type": category.text.strip(),
                "Model": name.text.strip(),
                "Working Radius": working_radius,
                "Max. Hoisting Capacity": max_hoisting_capacity,
                "Max. Free Standing Height": max_Free_Standing_Height,
                "Max. Jib Length": max_jib_length,
                "Max. Tip Load": max_tip_load,
                "Tip Load": tip_load,
                "Maximum FSH [L69]": max_FSH_L69,
                "Maximum FSH [RB]": max_FSH_RB,
                "Maximum Working Radius": max_working_radius,
                "Maximum FSH [L68]": max_FSH_L68,
                "Maximum FSH [RA]": max_FSH_RA,
                "Max. free standing height_2": max_free_standing_height_2,
                "Max. boom length": max_boom_length,
                "Max. hoisting capacity at jib end": max_hoisting_capacity_at_jib_end,
                "Capacity": capacity,
                "Speed": speed,
                "Cage Size": cage_size,
            })
    
    return products

# Function to create SQLite table if it doesn't exist
def create_sql_table(cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "Equipment Type" TEXT,
            "Model" TEXT,
            "Working Radius" TEXT,
            "Max. Hoisting Capacity" TEXT,
            "Max. Free Standing Height" TEXT,
            "Max. Jib Length" TEXT,
            "Max. Tip Load" TEXT,
            "Tip Load" TEXT,
            "Maximum FSH [L69]" TEXT,
            "Maximum FSH [RB]" TEXT,
            "Maximum Working Radius" TEXT,
            "Maximum FSH [L68]" TEXT,
            "Maximum FSH [RA]" TEXT,
            "Max. free standing height_2" TEXT,
            "Max. boom length" TEXT,
            "Max. hoisting capacity at jib end" TEXT,
            "Capacity" TEXT,
            "Speed" TEXT,
            "Cage Size" TEXT
        )
    """)

# Function to save data into SQLite
def save_to_sqlite(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    create_sql_table(cursor)

    for row in data:
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} ("Equipment Type", "Model", "Working Radius", "Max. Hoisting Capacity", "Max. Free Standing Height", "Max. Jib Length", "Max. Tip Load", "Tip Load", "Maximum FSH [L69]", "Maximum FSH [RB]", "Maximum Working Radius", "Maximum FSH [L68]", "Maximum FSH [RA]", "Max. free standing height_2", "Max. boom length", "Max. hoisting capacity at jib end", "Capacity", "Speed", "Cage Size")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row.values()))

    conn.commit()
    conn.close()
    print(f"Data saved to {DB_NAME}, Table: {TABLE_NAME}")

# Main function to scrape multiple pages and save data
def main():
    all_data = []
    
    for page in range(1, 14):  # Extracts pages 1 to 13
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
