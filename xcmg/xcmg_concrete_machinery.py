import requests
from bs4 import BeautifulSoup
import sqlite3

# Database connection
db_path = "equipment_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Table creation
cursor.execute('''CREATE TABLE IF NOT EXISTS xcmg_concrete_machinery_data_specs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_name TEXT,
    model TEXT,
    spec_name TEXT,
    spec_value TEXT
)''')

# Headers & Payload
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "http://en.xcmg.com",
    "Referer": "http://en.xcmg.com/en-ap/product/Concrete-Machinery/pro-list-1000125.htm"
}

base_url = "http://en.xcmg.com/en-ap/ext/ajax_prolist.jsp"

# Loop through pages
for page in range(1, 5):
    payload = {
        "flag": "1",
        "data1": "",
        "data2": "1000125",
        "data3": "",
        "data4": "",
        "data5": "",
        "data6": "",
        "nowPage": page
    }

    response = requests.post(base_url, headers=headers, data=payload)

    if response.status_code == 200:
        print(f"Page {page} scraped successfully.")  # ✅ Debugging step

        soup = BeautifulSoup(response.text, "html.parser")

        for product in soup.select("li.span-4.midd-6"):  # Fix selector
            img_tag = product.select_one("img")
            equipment_name = img_tag["alt"].strip() if img_tag else "Unknown"

            detail_link = product.select_one(".tit a")
            model = detail_link.text.strip() if detail_link else "Unknown"

            print(f"Found Equipment: {equipment_name} - Model: {model}")  # ✅ Debugging step

            # Find specifications inside <div class="con">
            spec_section = product.select_one(".con ul")
            if spec_section:
                for spec in spec_section.find_all("li", class_="fix"):
                    spec_name = spec.find("div", class_="l").text.strip()
                    spec_value = spec.find("div", class_="r").text.strip()

                    # Insert into database
                    cursor.execute('''INSERT INTO xcmg_concrete_machinery_data_specs 
                                    (equipment_name, model, spec_name, spec_value)
                                    VALUES (?, ?, ?, ?)''', 
                                    (equipment_name, model, spec_name, spec_value))
            else:
                # If no specs found, insert just the equipment name & model
                cursor.execute('''INSERT INTO xcmg_concrete_machinery_data_specs 
                                (equipment_name, model, spec_name, spec_value)
                                VALUES (?, ?, ?, ?)''', 
                                (equipment_name, model, None, None))

    else:
        print(f"Failed to retrieve page {page}")

# Commit changes
conn.commit()
conn.close()

print("XCMG concrete machinery data scraping completed!")
