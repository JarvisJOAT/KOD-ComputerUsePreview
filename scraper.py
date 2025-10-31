
import csv
import time
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- USER CONFIGURATION ---
# IMPORTANT: Fill in your InvestorLift credentials here
INVESTORLIFT_EMAIL = "Jarvis@keysopendoors.info"
INVESTORLIFT_PASSWORD = "8732Jtja7329$"
# --------------------------

# --- SCRIPT CONFIGURATION ---
LOGIN_URL = "https://investorlift.com/marketplace/?login=true"
MARKETPLACE_URL = "https://investorlift.com/marketplace/"
LOCATIONS_TO_SEARCH = ["District of Columbia", "Maryland", "Virginia"]
OUTPUT_FILE = os.path.abspath("listings.csv")
# --------------------------




def main():
    """
    Main function to run the scraper.
    """
    if INVESTORLIFT_EMAIL == "<YOUR_EMAIL>" or INVESTORLIFT_PASSWORD == "<YOUR_PASSWORD>":
        print("ERROR: Please open scraper.py and fill in your credentials.")
        return

    print("Starting scraper...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500) # headless=False to watch it work
        page = browser.new_page()

        # --- Login ---
        print(f"Navigating to login page: {LOGIN_URL}")
        page.goto(LOGIN_URL, wait_until='networkidle')
        page.wait_for_timeout(3000)  # Give page time to fully load
        
        print("Waiting for email input field...")
        email_input = page.locator("input[placeholder='Email address']")
        email_input.wait_for(state="visible", timeout=15000)
        
        print("Filling in email...")
        email_input.fill(INVESTORLIFT_EMAIL)
        
        print("Clicking 'Continue'...")
        continue_button = page.locator("button:has-text('Continue')").first
        continue_button.click()
        
        # Wait for password field to appear
        print("Waiting for password field...")
        page.wait_for_selector("input[placeholder='Enter password']", timeout=10000)
        page.wait_for_timeout(500)
        
        print("Filling in password...")
        password_input = page.locator("input[placeholder='Enter password']")
        password_input.fill(INVESTORLIFT_PASSWORD)
        page.wait_for_timeout(500)
        
        print("Submitting login form...")
        # The Continue button should become enabled after password is entered
        final_continue = page.locator("button:has-text('Continue')").last
        final_continue.wait_for(state="visible", timeout=5000)
        
        # Wait a bit for form validation
        page.wait_for_timeout(1000)
        
        print(" - Clicking final 'Continue' button...")
        try:
            # Try normal click first
            final_continue.click(timeout=10000)
        except Exception as e:
            print(f" - Normal click failed: {e}")
            print(" - Trying force click...")
            try:
                final_continue.click(force=True, timeout=5000)
            except Exception as e2:
                print(f" - Force click failed: {e2}")
                print(" - Pressing Enter instead...")
                page.keyboard.press("Enter")
        
        # Wait for navigation to marketplace
        print("Waiting for redirect to marketplace...")
        page.wait_for_url(MARKETPLACE_URL, timeout=30000)
        print("Login successful!")

        # --- Filtering ---
        print("Applying filters...")
        try:
            page.click("text='Home Type'")
            page.click("label:has-text('Condo')")
            print("Applied 'No Condos' filter.")
        except Exception as e:
            print(f"Could not apply 'No Condos' filter. It might already be applied or the selector is wrong: {e}")

        for location in LOCATIONS_TO_SEARCH:
            print(f"Searching for location: {location}")
            location_input_selector = "input[placeholder='State, County, City or Zip']"
            page.fill(location_input_selector, location)
            page.press(location_input_selector, "Enter")
            time.sleep(3)

        print("Waiting for search results to appear...")
        page.wait_for_selector('div.map-and-catalog-with-filters_content-and-filters_cards_scroller_inner', timeout=30000)

        # --- Scrape Listing Links ---
        print("Extracting links from the results page...")
        property_links = page.query_selector_all("a.ui-deal-card-link") # Corrected selector
        
        if not property_links:
            print("WARNING: Could not find any property links on the page. The selector might be wrong.")
            # Fallback: try another common selector
            property_links = page.query_selector_all("div.listing-item > a")

        urls_to_scrape = [link.get_attribute('href') for link in property_links]
        # Ensure URLs are absolute
        urls_to_scrape = [f"https://investorlift.com{url}" if url.startswith('/') else url for url in urls_to_scrape]
        
        print(f"Found {len(urls_to_scrape)} property links to scrape.")

        # --- Scrape Each Property ---
        all_properties_data = []
        for i, url in enumerate(urls_to_scrape):
            print(f"Scraping property {i+1}/{len(urls_to_scrape)}: {url}")
            try:
                page.goto(url, wait_until='domcontentloaded')
                page.wait_for_load_state('networkidle')
                
                details = {}
                details['url'] = url
                
                try:
                    details['title'] = page.locator('h1.deal-page-header__title').inner_text()
                except Exception:
                    details['title'] = "Not Found"
                    
                try:
                    details['price'] = page.locator('div.deal-page-header-price__value').inner_text()
                except Exception:
                    details['price'] = "Not Found"
                    
                try:
                    address_line = page.locator('div.deal-page-header-address').inner_text()
                    parts = [p.strip() for p in address_line.split(',')]
                    details['address'] = parts[0] if len(parts) > 0 else ""
                    details['city'] = parts[1] if len(parts) > 1 else ""
                    if len(parts) > 2:
                        state_zip = parts[2].split()
                        details['state'] = state_zip[0] if len(state_zip) > 0 else ""
                        details['zip_code'] = state_zip[1] if len(state_zip) > 1 else ""
                    else:
                        details['state'] = ""
                        details['zip_code'] = ""
                except Exception:
                    details['address'] = ""
                    details['city'] = ""
                    details['state'] = ""
                    details['zip_code'] = ""
                    
                try:
                    details['description'] = page.locator('div.deal-page-description__text').inner_text()
                except Exception:
                    details['description'] = "Not Found"
                    
                try:
                    details_container = page.locator('div.deal-page-details-row')
                    detail_items = details_container.locator('div.deal-page-details-row__item').all()
                    for item in detail_items:
                        text = item.inner_text().lower()
                        if 'bed' in text:
                            details['bedrooms'] = text.split()[0]
                        elif 'bath' in text:
                            details['bathrooms'] = text.split()[0]
                        elif 'sq.ft' in text or 'sq ft' in text:
                            details['square_feet'] = text.split()[0]
                        elif 'lot' in text:
                             details['lot_size'] = text
                        elif 'built' in text:
                             details['year_built'] = text.split()[-1]
                except Exception:
                    details['bedrooms'] = ""
                    details['bathrooms'] = ""
                    details['square_feet'] = ""
                    details['lot_size'] = ""
                    details['year_built'] = ""
                    
                try:
                    property_type_tag = page.locator('div:has-text("Property Type") + div')
                    details['property_type'] = property_type_tag.inner_text()
                except Exception:
                    details['property_type'] = ""
                    
                try:
                    image_urls = []
                    gallery_container = page.locator('div.deal-gallery')
                    img_tags = gallery_container.locator('img').all()
                    for img in img_tags:
                        src = img.get_attribute('src')
                        if src and 'property-images' in src:
                            image_urls.append(src)
                    details['image_urls'] = ", ".join(list(set(image_urls)))
                except Exception:
                    details['image_urls'] = ""
                
                all_properties_data.append(details)
            except Exception as e:
                print(f"  - Failed to scrape {url}: {e}")

        browser.close()

        # --- Save to CSV ---
        if not all_properties_data:
            print("No data was scraped. CSV file will not be created.")
            return
            
        print(f"Scraping complete. Saving {len(all_properties_data)} properties to {OUTPUT_FILE}...")
        
        headers = set()
        for prop in all_properties_data:
            headers.update(prop.keys())
        
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(list(headers)))
            writer.writeheader()
            writer.writerows(all_properties_data)
            
        print("Done.")

if __name__ == "__main__":
    main()
