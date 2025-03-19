from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    return driver

def extract_case_excavator_data():
    urls = [
        ("https://www.casece.com/en-zw/africamiddleeast/products/compaction/double-drum-rollers/450-dx", "Double Drum Roller"),
        ("https://www.casece.com/en-zw/africamiddleeast/products/compaction/single-drum-rollers/1110ex-d", "Single Drum Roller")
    ]
    
    driver = setup_driver()
    all_spec_data = []
    
    for url, roller_type in urls:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        time.sleep(5)  # Allow JavaScript to render content
        
        # Extract models
        models = [elem.text.strip() for elem in driver.find_elements(By.CLASS_NAME, "model-detail-specification-table__col-heading__title-spec")]
        if not models:
            print(f"No models found for URL: {url}. Skipping.")
            continue
        
        # Expand all sections except Engine (handled separately)
        expandable_sections = driver.find_elements(By.CLASS_NAME, "model-detail-specification-table__spec-category-row__inner-box")
        for section in expandable_sections:
            try:
                if "ENGINE" not in section.text.strip():
                    driver.execute_script("arguments[0].scrollIntoView();", section)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", section)
                    time.sleep(2)
            except Exception as e:
                print(f"Error expanding section: {e}")
        
        # Extract specifications dynamically (excluding Engine)
        spec_data = []
        current_category = ""
        
        for row in driver.find_elements(By.XPATH, "//tr"):
            # Check if the row is a category row
            category_elem = row.find_elements(By.CLASS_NAME, "model-detail-specification-table__spec-category-row__inner-box")
            if category_elem:
                current_category = category_elem[0].text.strip()
                continue  # Move to the next row
            
            # Process specification rows
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 2:
                continue
            
            spec_name = cells[0].text.strip()
            spec_values = [cell.text.strip() for cell in cells[1:]]
            
            # Add the Roller_Type to distinguish the roller type
            spec_entry = {"Category": current_category, "Specification": spec_name, "Roller_Type": roller_type}
            for i, model in enumerate(models):
                spec_entry[f"{model}"] = spec_values[i] if i < len(spec_values) else "N/A"
            
            spec_data.append(spec_entry)
        
        all_spec_data.extend(spec_data)  # Add data from this URL to the overall list
        
        # Extract Engine specifications separately using requests and BeautifulSoup
        engine_data = extract_engine_specs(url, models, roller_type)
        all_spec_data.extend(engine_data)  # Merge engine data
        
    driver.quit()
    
    return all_spec_data

def extract_engine_specs(url, models, roller_type):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page for Engine specs from {url}.")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    engine_category = "ENGINE"
    spec_data = []
    
    engine_section = soup.find("h3", class_="model-detail-specification-table__spec-category-row__inner-box")
    if not engine_section:
        print("No ENGINE section found.")
        return []
    
    # Loop through all `tr` rows following the Engine header
    row = engine_section.find_next_sibling("tr")
    while row and row.find("td"):
        cells = row.find_all("td")
        if len(cells) < 2:
            row = row.find_next_sibling("tr")
            continue
        
        spec_name = cells[0].text.strip()
        spec_values = [cell.text.strip() for cell in cells[1:]]
        
        spec_entry = {"Category": engine_category, "Specification": spec_name, "Roller_Type": roller_type}
        for i, model in enumerate(models):
            spec_entry[f"Bseries_{model}"] = spec_values[i] if i < len(spec_values) else "N/A"
        
        spec_data.append(spec_entry)
        row = row.find_next_sibling("tr")  # Move to the next row
    
    return spec_data

def save_to_db(data):
    if not data:
        print("No data to save.")
        return
    
    df = pd.DataFrame(data)
    
    # Connect to the SQLite database
    conn = sqlite3.connect("equipment_data.db")
    
    # Check if the table exists already
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='case_compactors_data_specs'")
    table_exists = cursor.fetchone()
    
    # If table doesn't exist, create it with the necessary columns
    if not table_exists:
        df.to_sql("case_compactors_data_specs", conn, if_exists="replace", index=False)
    else:
        # Check the columns in the table and DataFrame
        existing_columns = [col[1] for col in cursor.execute("PRAGMA table_info(case_compactors_data_specs)").fetchall()]
        new_columns = [col for col in df.columns if col not in existing_columns]
        
        # If there are new columns, add them to the table
        for column in new_columns:
            try:
                cursor.execute(f"ALTER TABLE case_compactors_data_specs ADD COLUMN `{column}` TEXT")
            except sqlite3.OperationalError:
                # If the column already exists, skip the error
                continue
        
        # Now append the data to the table
        df.to_sql("case_compactors_data_specs", conn, if_exists="append", index=False)
    
    conn.close()

if __name__ == "__main__":
    extracted_data = extract_case_excavator_data()
    save_to_db(extracted_data)
    print("CASE compactors data successfully saved.")
