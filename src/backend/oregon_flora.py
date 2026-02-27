from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def get_nested_react_data():
    # Setup Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background (optional)
    
    # Initialize the browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        url = "https://oregonflora.org/garden/index.php"
        print(f"Opening {url}...")
        driver.get(url)

        # --- CRITICAL STEP: WAIT FOR THE NESTED CONTENT ---
        # The script will pause here until it actually sees the "search-results" div 
        # appear inside the "react-garden".
        print("Waiting for React to build the nested elements...")
        wait = WebDriverWait(driver, 15)
        
        # We wait until the specific ID 'search-results' (from your screenshot) exists
        search_results_container = wait.until(EC.presence_of_element_located((By.ID, "search-results")))
        
        print("Nested container found! Extracting data...")

        # Now we find the cards inside that container
        cards = search_results_container.find_elements(By.CLASS_NAME, "search-result-link-container")
        
        extracted_data = []

        for card in cards:
            try:
                # 1. Get the link
                link = card.get_attribute('href')
                
                # 2. Get the image
                # We use CSS selectors to find the img tag specifically inside this card
                img_element = card.find_element(By.CSS_SELECTOR, "img.card-img-top")
                img_src = img_element.get_attribute('src')
                
                # 3. Get the text
                card_text_div = card.find_element(By.CLASS_NAME, "card-text")
                
                # The scientific name is in the span with class 'font-italic'
                try:
                    sci_name_el = card_text_div.find_element(By.CLASS_NAME, "font-italic")
                    scientific_name = sci_name_el.text
                except:
                    scientific_name = "N/A"
                
                # The common name is the text that is NOT the scientific name.
                # Usually it's the first line of text in that div.
                all_text = card_text_div.text
                common_name = all_text.split('\n')[0] if all_text else "N/A"
                
                extracted_data.append({
                    "common_name": common_name,
                    "scientific_name": scientific_name,
                    "image": img_src,
                    "link": link
                })
                
            except Exception as e:
                # If a single card fails, just skip it and keep going
                continue

        return extracted_data

    finally:
        # Close the browser window
        driver.quit()

# Run the function
data = get_nested_react_data()

# Print the data
print(f"Found {len(data)} plants.")

with open('oregon_flora_plants.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)