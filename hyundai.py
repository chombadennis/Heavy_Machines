from urllib.request import urlopen
from bs4 import BeautifulSoup as soup
import pandas as pd
import sqlite3
import time

# Base URL
BASE_URL = "https://na.hd-hyundaice.com"

def get_equipment_links():
    """Scrapes and returns a list of equipment page links."""
    try:
        response = urlopen(BASE_URL + "/equipment")
        html = response.read().decode('utf-8')
        bsobj = soup(html, "html.parser")

        links = [
            BASE_URL + a.attrs["href"]
            for a in bsobj.find('div', {'class': 'container-max relative z-10'}).find_all('a', {'class': 'underline hover:text-black'})
            if "href" in a.attrs
        ]
        return links
    except Exception as e:
        print(f"Failed to fetch equipment links: {e}")
        return []

def scrape_equipment_data(link):
    """Scrapes equipment type, model, and specifications from a given link."""
    try:
        page = urlopen(link)
        html = page.read().decode('utf-8')
        equipment_soup = soup(html, "html.parser")

        # Extract Equipment Type and Model
        name_tags = equipment_soup.find_all("span", {
            "class": "flex-1 truncate border-b border-gray-200 py-1 text-xs text-gray-600 transition-all duration-300 group-last:text-black group-last-of-type:border-transparent group-hover/breadcrumb:border-green-600 group-hover/breadcrumb:text-black group-hover/breadcrumb:group-last:border-green-600 group-hover/breadcrumb:group-last-of-type:border-b dark:text-white group-last:dark:text-white group-hover/breadcrumb:dark:text-white"
        })
        
        equipment_type = name_tags[-2].get_text(strip=True) if len(name_tags) >= 2 else "N/A"
        model_name = name_tags[-1].get_text(strip=True) if len(name_tags) >= 2 else "N/A"

        # Extract Specifications
        specs = {}
        spec_table = equipment_soup.find("table", {"class": "w-full table-fixed"})

        if spec_table:
            for row in spec_table.find_all("tr", {"class": "w-full border-b border-gray-200"}):
                cols = row.find_all("td")
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True).replace("\u2013", "–")  # Fix en dash
                    specs[key] = value
        else:
            # Extract Breaker Specifications
            breaker_specs = equipment_soup.find("div", {"class": "flex flex-col gap-5 dark:text-white md:flex-row md:gap-10"})
            if breaker_specs:
                for div in breaker_specs.find_all("div", {"class": "flex flex-col gap-2"}):
                    key_div = div.find("div", {"class": "text-xs text-white sm:text-sm md:text-white"})
                    value_div = div.find("div", {"class": "text-lg font-bold text-white sm:text-xl"})
                    if key_div and value_div:
                        key = key_div.get_text(strip=True)
                        value = value_div.get_text(strip=True).replace("\u2013", "–")  # Fix en dash
                        specs[key] = value

        print(f"Scraped: {equipment_type} - {model_name}")  # Progress update
        return {"Equipment Type": equipment_type, "Model": model_name, "Link": link, **specs}

    except Exception as e:
        print(f"Failed to scrape {link}: {e}")
        return {}

def create_sql_table(cursor, table_name, all_spec_keys):
    """Creates the SQL table dynamically based on extracted specifications."""
    column_definitions = ", ".join([f'"{col}" TEXT' for col in ["Equipment Type", "Model", "Link"] + list(all_spec_keys)])
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {column_definitions})')

def save_to_sqlite(df, db_name="equipment_data.db", table_name="hyundai_equipment_specs"):
    """Saves the DataFrame to SQLite, dynamically handling column names."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the table dynamically based on available columns
    all_spec_keys = set(df.columns) - {"Equipment Type", "Model", "Link"}
    create_sql_table(cursor, table_name, all_spec_keys)

    # Insert data into SQLite
    for _, row in df.iterrows():
        columns = ", ".join(f'"{col}"' for col in row.index)
        placeholders = ", ".join("?" for _ in row.index)
        values = tuple(row.fillna("").values)  # Replace NaN with empty string
        cursor.execute(f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', values)

    conn.commit()
    conn.close()
    print(f"Data saved to SQLite database: {db_name}, Table: {table_name}")

def main():
    """Main function to coordinate the scraping and data storage."""
    equipment_links = get_equipment_links()
    all_data = []

    for link in equipment_links:
        data = scrape_equipment_data(link)
        if data:
            all_data.append(data)
        time.sleep(1)  # Avoid being blocked

    if all_data:
        hyundai_df = pd.DataFrame(all_data)
        save_to_sqlite(hyundai_df)

    print("Scraping complete.")

# Run the script
if __name__ == "__main__":
    main()
