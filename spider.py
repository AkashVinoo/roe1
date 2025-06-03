from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
import re

def scrape_tds_content():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the driver with automatic ChromeDriver installation
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Start with the main page
        driver.get("https://tds.s-anand.net/#/2025-01/")
        
        # Wait for the content to load
        time.sleep(5)  # Give time for JavaScript to execute
        
        # Get all links from the sidebar
        sidebar = driver.find_element(By.CLASS_NAME, "sidebar-nav")
        links = sidebar.find_elements(By.TAG_NAME, "a")
        urls = [link.get_attribute("href") for link in links if link.get_attribute("href")]
        
        documents = []
        
        # Process main page first
        main_content = driver.find_element(By.CLASS_NAME, "markdown-section")
        documents.append({
            'url': driver.current_url,
            'title': main_content.find_element(By.TAG_NAME, "h1").text,
            'content': main_content.text
        })
        
        # Visit each link
        for url in urls:
            try:
                driver.get(url)
                time.sleep(3)  # Wait for content to load
                
                # Find the main content
                content = driver.find_element(By.CLASS_NAME, "markdown-section")
                
                # Extract title
                try:
                    title = content.find_element(By.TAG_NAME, "h1").text
                except:
                    title = None
                
                # Create document
                doc = {
                    'url': url,
                    'title': title,
                    'content': content.text
                }
                
                documents.append(doc)
                print(f"Scraped: {url}")
                
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
        
        # Save to JSONL file
        with open('tds_content.jsonl', 'w', encoding='utf-8') as f:
            for doc in documents:
                f.write(json.dumps(doc) + '\n')
        
        print(f"Successfully scraped {len(documents)} pages")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Starting the TDS course content scraper...")
    scrape_tds_content()
    print("Scraping finished. Data saved to tds_content.jsonl") 