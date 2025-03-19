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

def extract_case_excavator_data(series, url, model_name):
    driver = setup_driver()
    driver.get(url)
    time.sleep(5)  # Allow JavaScript to render content
    
    # Extract models with uppercase names
    models = [elem.text.strip().upper() for elem in driver.find_elements(By.CLASS_NAME, "model-detail-specification-table__col-heading__title-spec")]
    print(f"Extracted models on page: {models}")
    model_name = model_name.upper()
    
    if model_name not in models:
        print(f"Model {model_name} not found on page. Skipping...")
        driver.quit()
        return []
    
    # Expand all sections
    expandable_sections = driver.find_elements(By.CLASS_NAME, "model-detail-specification-table__spec-category-row__inner-box")
    for section in expandable_sections:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", section)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", section)
            time.sleep(2)
        except Exception as e:
            print(f"Error expanding section: {e}")
    
    # Extract specifications for the target model only
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
            spec_entry = {"Category": current_category, "Specification": spec_name, f"{series}_{model_name}": spec_values[index] if index < len(spec_values) else "N/A"}
            
            spec_tuple = tuple(spec_entry.items())
            if spec_tuple not in extracted_specs:
                extracted_specs.add(spec_tuple)
                spec_data.append(spec_entry)
    
    driver.quit()
    
    # Extract Engine specifications separately
    engine_data = extract_engine_specs(series, url, model_name)
    spec_data.extend(engine_data)
    
    return spec_data

def extract_engine_specs(series, url, model_name):
    response = requests.get(url)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    engine_category = "ENGINE"
    spec_data = []
    extracted_specs = set()
    
    engine_section = soup.find("h3", class_="model-detail-specification-table__spec-category-row__inner-box", string=lambda text: text and "Engine" in text)
    if not engine_section:
        print("No ENGINE section found.")
        return []
    
    row = engine_section.find_next("tr")
    while row and row.find("td"):
        cells = row.find_all("td")
        if len(cells) < 2:
            row = row.find_next_sibling("tr")
            continue
        
        spec_name = cells[0].text.strip()
        spec_values = [cell.text.strip() for cell in cells[1:]]
        
        spec_entry = {"Category": engine_category, "Specification": spec_name, f"{series}_{model_name}": spec_values[0] if spec_values else "N/A"}
        
        spec_tuple = tuple(spec_entry.items())
        if spec_tuple not in extracted_specs:
            extracted_specs.add(spec_tuple)
            spec_data.append(spec_entry)
        
        row = row.find_next_sibling("tr")
    
    return spec_data

def save_to_db(data):
    if not data:
        return
    
    df = pd.DataFrame(data)
    conn = sqlite3.connect("equipment_data.db")
    df.to_sql("case_cseries_excavators_data_specs", conn, if_exists="append", index=False)
    conn.close()

if __name__ == "__main__":
    base_url = "https://www.casece.com/en-zw/africamiddleeast/products/excavators/"
    
    c_series_models = ["c-series-crawler-excavators/CX130C", "c-series-crawler-excavators/CX210C", "c-series-crawler-excavators/CX220C", "c-series-crawler-excavators/CX220C-LC-HD", "c-series-crawler-excavators/CX220C-LR", "c-series-crawler-excavators/CX250C", "c-series-crawler-excavators/CX300C", "c-series-crawler-excavators/C350C", "c-series-crawler-excavators/CX370C", "c-series-crawler-excavators/CX490C", "c-series-crawler-excavators/CX500C"]
    
    all_data = []
    for model_path in c_series_models:
        model_name = model_path.split("/")[-1]
        url = f"{base_url}{model_path}"
        print(f"Extracting data for C-series {model_name}...")
        extracted_data = extract_case_excavator_data("Cseries", url, model_name)
        all_data.extend(extracted_data)
    
    save_to_db(all_data)
    print("CASE C-series excavator data successfully saved.")
