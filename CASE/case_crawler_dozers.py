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
    url = "https://www.casece.com/en-zw/africamiddleeast/products/crawler-dozers/1150l"
    driver = setup_driver()
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    time.sleep(5)  # Allow JavaScript to render content
    
    # Extract models
    models = [elem.text.strip() for elem in driver.find_elements(By.CLASS_NAME, "model-detail-specification-table__col-heading__title-spec")]
    if not models:
        print("No models found. Exiting.")
        driver.quit()
        return {}
    
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
        
        spec_entry = {"Category": current_category, "Specification": spec_name}
        for i, model in enumerate(models):
            spec_entry[f"{model}"] = spec_values[i] if i < len(spec_values) else "N/A"
        
        spec_data.append(spec_entry)
    
    driver.quit()
    
    # Extract Engine specifications separately using requests and BeautifulSoup
    engine_data = extract_engine_specs(url, models)
    spec_data.extend(engine_data)  # Merge both datasets
    
    return spec_data

def extract_engine_specs(url, models):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch page for Engine specs.")
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
        
        spec_entry = {"Category": engine_category, "Specification": spec_name}
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
    conn = sqlite3.connect("equipment_data.db")
    df.to_sql("case_crawler_dozer_data_specs", conn, if_exists="replace", index=False)
    conn.close()

if __name__ == "__main__":
    extracted_data = extract_case_excavator_data()
    save_to_db(extracted_data)
    print("CASE crawler dozer data successfully saved.")
