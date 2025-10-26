
import csv
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# --- USER CONFIGURATION ---
# IMPORTANT: Fill in your InvestorLift credentials here
INVESTORLIFT_EMAIL = "jarvis@keysopendoors.info"
INVESTORLIFT_PASSWORD = "8732Jtja7329$"
# --------------------------

# --- SCRIPT CONFIGURATION ---
LOGIN_URL = "https://investorlift.com/marketplace/?login=true"
MARKETPLACE_URL = "https://investorlift.com/marketplace/"
LOCATIONS_TO_SEARCH = ["District of Columbia", "Maryland", "Virginia"]
OUTPUT_FILE = "listings.csv"
# --------------------------

def parse_property_details(page_content: str) -> dict:
    """
    Parses the HTML of a property detail page to extract structured data.
    """
    soup = BeautifulSoup(page_content, "lxml")
    property_data = {}

    # --- Corrected Selectors based on property_detail.html ---

    # Title: Often in a high-level heading within the main content.
    title_tag = soup.find('h1', class_='deal-page-header__title') # More specific guess
    property_data['title'] = title_tag.get_text(strip=True) if title_tag else "Not Found"

    # Price: Found within a specific div structure
    price_tag = soup.find('div', class_='deal-page-header-price__value')
    property_data['price'] = price_tag.get_text(strip=True) if price_tag else "Not Found"

    # Address Components
    address_line = soup.find('div', class_='deal-page-header-address')
    if address_line:
        full_address = address_line.get_text(strip=True)
        parts = [p.strip() for p in full_address.split(',')]
        # This is a guess, assuming format: Street, City, State Zip
        property_data['address'] = parts[0] if len(parts) > 0 else ""
        property_data['city'] = parts[1] if len(parts) > 1 else ""
        if len(parts) > 2:
            state_zip = parts[2].split()
            property_data['state'] = state_zip[0] if len(state_zip) > 0 else ""
            property_data['zip_code'] = state_zip[1] if len(state_zip) > 1 else ""
        else:
            property_data['state'] = ""
            property_data['zip_code'] = ""
    
    # Description
    description_tag = soup.find('div', class_='deal-page-description__text')
    property_data['description'] = description_tag.get_text(strip=True) if description_tag else "Not Found"

    # Details like Beds, Baths, SqFt
    details_container = soup.find('div', class_='deal-page-details-row')
    if details_container:
        detail_items = details_container.find_all('div', class_='deal-page-details-row__item')
        for item in detail_items:
            text = item.get_text(strip=True).lower()
            if 'bed' in text:
                property_data['bedrooms'] = text.split()[0]
            elif 'bath' in text:
                property_data['bathrooms'] = text.split()[0]
            elif 'sq.ft' in text or 'sq ft' in text:
                property_data['square_feet'] = text.split()[0]
            elif 'lot' in text:
                 property_data['lot_size'] = text
            elif 'built' in text:
                 property_data['year_built'] = text.split()[-1]

    # Property Type is often found in a similar details section
    property_type_tag = soup.find(lambda tag: 'Property Type' in tag.get_text() and tag.name == 'div')
    if property_type_tag:
        property_data['property_type'] = property_type_tag.find_next_sibling().get_text(strip=True)

    # Images
    image_urls = []
    gallery_container = soup.find('div', class_='deal-gallery')
    if gallery_container:
        img_tags = gallery_container.find_all('img')
        for img in img_tags:
            if img.get('src') and 'property-images' in img.get('src'):
                image_urls.append(img.get('src'))
    property_data['image_urls'] = ", ".join(list(set(image_urls))) # Use set to remove duplicates

    return property_data


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
        print("Navigating to login page: {LOGIN_URL}")
        page.goto(LOGIN_URL)
        
        print("Filling in email...")
        page.fill("input[placeholder='Email address']", INVESTORLIFT_EMAIL)

        print("Clicking 'Continue'...")
        page.click("button:has-text('Continue')")

        print("Filling in password...")
        page.locator("input[placeholder='Enter password']").press_sequentially(INVESTORLIFT_PASSWORD, delay=100) # Add 100ms delay between keystrokes
        
        print("Submitting login form...")
        # Click the final continue button, waiting up to 60 seconds for it to become enabled.
        print(" - Waiting for and clicking final 'Continue' button...")
        page.locator("button:has-text('Continue')").last.click(timeout=60000)

        page.wait_for_url(MARKETPLACE_URL, timeout=30000)
        print("Login successful.")

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
                details = parse_property_details(page.content())
                details['url'] = url
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
