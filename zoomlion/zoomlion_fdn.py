import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# URL and database details
URL = "https://en-product.zoomlion.com/ext/ajax_proList.jsp"
DB_NAME = "equipment_data.db"
TABLE_NAME = "zoomlion_foundation_equipment_specs"

# Headers for request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://en-product.zoomlion.com/product/pro_list.htm?sCat=58",
    "Origin": "https://en-product.zoomlion.com",
}

# Function to fetch data from a specific page
def fetch_page_data(page):
    payload = {
        "flag": "pro",
        "sCat": "58",
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
        max_drilling_diameter = max_drilling_depth = max_output_torque = rotary_speed_range = max_working_radius = max_wall_depth = max_wall_thickness = max_hoisting_force = max_milling_torque = max_slag_discharge_flow = weight_of_milling_device = max_cutting_width = max_pile_pressing_force = min_pile_pressing_speed = max_pile_pressing_speed = max_jacking_force = max_backhauling_force = max_torque = max_rotation_speed_of_rotary_drive = oscillating_diameter = upward_pressure = downward_pressure = oscillating_torque = oscillating_diamete = lifting_force = pushing_stroke = drilling_diameter = rotation_torque = slewing_speed = None
        for spec in specs:
            text = spec.text.strip()
            if "Max. drlling diameter" in text:
                max_drilling_diameter = spec.find("span", class_="num num01").text.strip()
            elif "Max. drlling depth" in text:
                max_drilling_depth = spec.find("span", class_="num num01").text.strip()
            elif "Max. output torque" in text:
                max_output_torque = spec.find("span", class_="num num01").text.strip()
            elif "Rotary speed range" in text:
                rotary_speed_range = spec.find("span", class_="num num01").text.strip()
            elif "Max. working radius" in text:
                max_working_radius = spec.find("span", class_="num num01").text.strip()
            elif "Max. wall depth" in text:
                max_wall_depth = spec.find("span", class_="num num01").text.strip()
            elif "Max. wall thickness" in text:
                max_wall_thickness = spec.find("span", class_="num num01").text.strip()
            elif "Max. hoisting force" in text:
                max_hoisting_force = spec.find("span", class_="num num01").text.strip()
            elif "Max. milling torque" in text:
                max_milling_torque = spec.find("span", class_="num num01").text.strip()
            elif "Max. slag discharge flow" in text:
                max_slag_discharge_flow = spec.find("span", class_="num num01").text.strip()
            elif "Weight of milling device" in text:
                weight_of_milling_device = spec.find("span", class_="num num01").text.strip()
            elif "Max. cutting width" in text:
                max_cutting_width = spec.find("span", class_="num num01").text.strip()
            elif "Max. pile pressing force" in text:
                max_pile_pressing_force = spec.find("span", class_="num num01").text.strip()
            elif "Min. pile pressing speed" in text:
                min_pile_pressing_speed = spec.find("span", class_="num num01").text.strip()
            elif "Max. pile pressing speed" in text:
                max_pile_pressing_speed = spec.find("span", class_="num num01").text.strip()
            elif "Max. jacking force" in text:
                max_jacking_force = spec.find("span", class_="num num01").text.strip()
            elif "Max. backhauling force" in text:
                max_backhauling_force = spec.find("span", class_="num num01").text.strip()
            elif "Max. torque" in text:
                max_torque = spec.find("span", class_="num num01").text.strip()
            elif "Max. rotation speed of rotary drive" in text:
                max_rotation_speed_of_rotary_drive = spec.find("span", class_="num num01").text.strip()
            elif "Oscillating diameter" in text:
                oscillating_diameter = spec.find("span", class_="num num01").text.strip()
            elif "Upward pressure" in text:
                upward_pressure = spec.find("span", class_="num num01").text.strip()
            elif "Downward pressure" in text:
                downward_pressure = spec.find("span", class_="num num01").text.strip()
            elif "Oscillating torque" in text:
                oscillating_torque = spec.find("span", class_="num num01").text.strip() 
            elif "Oscillating diamete" in text:
                oscillating_diamete = spec.find("span", class_="num num01").text.strip()    
            elif "Lifting force" in text:
                lifting_force = spec.find("span", class_="num num01").text.strip()  
            elif "Pushing stroke" in text:
                pushing_stroke = spec.find("span", class_="num num01").text.strip() 
            elif "Drilling diameter" in text:
                drilling_diameter = spec.find("span", class_="num num01").text.strip()
            elif "Rotation torque" in text:
                rotation_torque = spec.find("span", class_="num num01").text.strip()
            elif "Slewing speed" in text:
                slewing_speed = spec.find("span", class_="num num01").text.strip()


        if name and category:
            products.append({
                "Equipment Type": category.text.strip(),
                "Model": name.text.strip(),
                "Max. Drlling Diameter": max_drilling_diameter,
                "Max. Drlling Depth": max_drilling_depth,
                "Max. Output Torque": max_output_torque,
                "Rotary Speed Range": rotary_speed_range,
                "Max. Working Radius": max_working_radius,
                "Max. Wall Depth": max_wall_depth,
                "Max. Wall Thickness": max_wall_thickness,
                "Max. Hoisting Force": max_hoisting_force,
                "Max. Milling Torque": max_milling_torque,
                "Max. Slag Discharge Flow": max_slag_discharge_flow,
                "Weight of Milling Device": weight_of_milling_device,
                "Max. Cutting Width": max_cutting_width,
                "Max. Pile Pressing Force": max_pile_pressing_force,
                "Min. Pile Pressing Speed": min_pile_pressing_speed,
                "Max. Pile Pressing Speed": max_pile_pressing_speed,
                "Max. Jacking Force": max_jacking_force,
                "Max. Backhauling Force": max_backhauling_force,
                "Max. Torque": max_torque,
                "Max. Rotation Speed of Rotary Drive": max_rotation_speed_of_rotary_drive,
                "Oscillating Diameter": oscillating_diameter,
                "Upward Pressure": upward_pressure,
                "Downward Pressure": downward_pressure,
                "Oscillating Torque": oscillating_torque,
                "Oscillating Diamete": oscillating_diamete,
                "Lifting Force": lifting_force,
                "Pushing Stroke": pushing_stroke,
                "Drilling Diameter": drilling_diameter,
                "Rotation Torque": rotation_torque,
                "Slewing Speed": slewing_speed,
            })
    
    return products

# Function to create SQLite table if it doesn't exist
def create_sql_table(cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "Equipment Type" TEXT,
            "Model" TEXT,
            "Max. Drlling Diameter" TEXT,
            "Max. Drlling Depth" TEXT,
            "Max. Output Torque" TEXT,
            "Rotary Speed Range" TEXT,
            "Max. Working Radius" TEXT,
            "Max. Wall Depth" TEXT,
            "Max. Wall Thickness" TEXT,
            "Max. Hoisting Force" TEXT,
            "Max. Milling Torque" TEXT,
            "Max. Slag Discharge Flow" TEXT,
            "Weight of Milling Device" TEXT,
            "Max. Cutting Width" TEXT,
            "Max. Pile Pressing Force" TEXT,
            "Min. Pile Pressing Speed" TEXT,
            "Max. Pile Pressing Speed" TEXT,
            "Max. Jacking Force" TEXT,
            "Max. Backhauling Force" TEXT,
            "Max. Torque" TEXT,
            "Max. Rotation Speed of Rotary Drive" TEXT,
            "Oscillating Diameter" TEXT,
            "Upward Pressure" TEXT,
            "Downward Pressure" TEXT,
            "Oscillating Torque" TEXT,
            "Oscillating Diamete" TEXT,
            "Lifting Force" TEXT,
            "Pushing Stroke" TEXT,
            "Drilling Diameter" TEXT,
            "Rotation Torque" TEXT,
            "Slewing Speed" TEXT
        )
    """)

# Function to save data into SQLite
def save_to_sqlite(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    create_sql_table(cursor)

    for row in data:
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} ("Equipment Type", "Model", "Max. Drlling Diameter", "Max. Drlling Depth", "Max. Output Torque","Rotary Speed Range","Max. Working Radius", "Max. Wall Depth", "Max. Wall Thickness", "Max. Hoisting Force", "Max. Milling Torque", "Max. Slag Discharge Flow","Weight of Milling Device", "Max. Cutting Width", "Max. Pile Pressing Force", "Min. Pile Pressing Speed", "Max. Pile Pressing Speed", "Max. Jacking Force", "Max. Backhauling Force", "Max. Torque", "Max. Rotation Speed of Rotary Drive", "Oscillating Diameter", "Upward Pressure", "Downward Pressure", "Oscillating Torque", "Oscillating Diamete", "Lifting Force", "Pushing Stroke", "Drilling Diameter", "Rotation Torque", "Slewing Speed")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row.values()))

    conn.commit()
    conn.close()
    print(f"Data saved to {DB_NAME}, Table: {TABLE_NAME}")

# Main function to scrape multiple pages and save data
def main():
    all_data = []
    
    for page in range(1, 6):  # Extracts pages 1 to 5
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
