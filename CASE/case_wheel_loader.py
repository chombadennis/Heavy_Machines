from selenium import webdriver
from selenium.webdriver.common.by import By
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

def extract_case_excavator_data(url, model_name):
    driver = setup_driver()
    driver.get(url)
    time.sleep(5)  # Allow JavaScript to render content
    
    models = [elem.text.strip().upper().replace("-", " ") for elem in driver.find_elements(By.CLASS_NAME, "model-detail-specification-table__col-heading__title-spec")]
    model_name = "CX500C ME" if "CX500C" in model_name else model_name.replace("-", " ").upper()
    
    print(f"Extracted models on page: {models}")
    if model_name not in models:
        print(f"Model {model_name} not found on page. Skipping...")
        driver.quit()
        return []
    
    expandable_sections = driver.find_elements(By.CLASS_NAME, "model-detail-specification-table__spec-category-row__inner-box")
    for section in expandable_sections:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", section)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", section)
            time.sleep(2)
        except Exception as e:
            print(f"Error expanding section: {e}")
    
    spec_data = []
    extracted_specs = set()
    current_category = ""
    
    for row in driver.find_elements(By.XPATH, "//tr"):
        category_elem = row.find_elements(By.CLASS_NAME, "model-detail-specification-table__spec-category-row__inner-box")
        if category_elem:
            current_category = category_elem[0].text.strip()
            continue  
        
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) < 2:
            continue
        
        spec_name = cells[0].text.strip()
        spec_values = [cell.text.strip() for cell in cells[1:]]
        
        if model_name in models:
            index = models.index(model_name)
            spec_entry = {"Category": current_category, "Specification": spec_name, f"{model_name}": spec_values[index] if index < len(spec_values) else "N/A"}
            
            spec_tuple = tuple(spec_entry.items())
            if spec_tuple not in extracted_specs:
                extracted_specs.add(spec_tuple)
                spec_data.append(spec_entry)
    
    driver.quit()
    
    engine_data = extract_engine_specs(url, model_name, models)
    if not engine_data:
        print(f"No engine data extracted for model {model_name}")
    spec_data.extend(engine_data)
    
    return spec_data

def extract_engine_specs(url, model_name, models):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    engine_category = "ENGINE"
    spec_data = []
    extracted_specs = set()
    
    # Try different approaches to find the engine section
    engine_section = None
    # Method 1: Direct h3 search
    engine_section = soup.find("h3", string=lambda text: text and "Engine" in text)
    
    # Method 2: Search within the specification table
    if not engine_section:
        spec_table = soup.find("table", class_="model-detail-specification-table")
        if spec_table:
            engine_section = spec_table.find(
                lambda tag: tag.name in ["h3", "td"] and 
                tag.text and 
                "Engine" in tag.text.strip()
            )
    
    if not engine_section:
        print(f"No ENGINE section found for model {model_name}")
        return []
    
    # Find the containing table row and get subsequent rows
    current_tr = engine_section
    while current_tr and not current_tr.name == "tr":
        current_tr = current_tr.find_parent("tr")
    
    if not current_tr:
        return []
    
    # Process subsequent rows until we hit the next category
    current_tr = current_tr.find_next_sibling("tr")
    while current_tr:
        # Check if we've hit the next category
        if current_tr.find("h3") or current_tr.find(class_="model-detail-specification-table__spec-category-row__inner-box"):
            break
            
        # Extract specification name from first cell
        spec_name_cell = current_tr.find("td", class_="model-detail-specification-table__left-most-cell")
        if not spec_name_cell:
            current_tr = current_tr.find_next_sibling("tr")
            continue
            
        spec_name = spec_name_cell.text.strip()
        
        # Extract values from remaining cells
        value_cells = current_tr.find_all("td", class_=lambda x: x and "model-detail-specification-table__table-cell" in x)
        spec_values = [cell.text.strip() for cell in value_cells]
        
        if model_name in models:
            index = models.index(model_name)
            if index < len(spec_values):
                spec_entry = {
                    "Category": engine_category,
                    "Specification": spec_name,
                    f"{model_name}": spec_values[index]
                }
                
                spec_tuple = tuple(spec_entry.items())
                if spec_tuple not in extracted_specs:
                    extracted_specs.add(spec_tuple)
                    spec_data.append(spec_entry)
                    
        current_tr = current_tr.find_next_sibling("tr")
    
    return spec_data

def save_to_db(data):
    if not data:
        return
    
    df = pd.DataFrame(data)
    conn = sqlite3.connect("equipment_data.db")
    df.to_sql("case_wheel_loader_data_specs", conn, if_exists="append", index=False)
    conn.close()

if __name__ == "__main__":
    base_url = "https://www.casece.com/en-zw/africamiddleeast/products/wheel-loaders/"
    
    wheel_loader_models = ["621f", "621xs", "721f", "821f", "921f", "1021f", "1121f"]
    all_data = []
    for model_path in wheel_loader_models:
        model_name = "CX500C ME" if "CX500C" in model_path else model_path.split("/")[-1].replace("-", " ")
        url = f"{base_url}{model_path}"
        print(f"Extracting data for wheel loader {model_name}...")
        extracted_data = extract_case_excavator_data(url, model_name)
        all_data.extend(extracted_data)
    
    save_to_db(all_data)
    print("CASE wheel loader data successfully saved.")
