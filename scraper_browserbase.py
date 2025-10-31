"""
InvestorLift Property Scraper using Browserbase
This version uses Browserbase to bypass CloudFront protection.
"""
import csv
import os
from agent import BrowserAgent
from computers.browserbase.browserbase import BrowserbaseComputer

# --- USER CONFIGURATION ---
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
    Main function to run the scraper using Browserbase.
    """
    # Check for Browserbase credentials
    if not os.environ.get("BROWSERBASE_API_KEY"):
        print("ERROR: BROWSERBASE_API_KEY environment variable not set!")
        print("\nTo get started with Browserbase:")
        print("1. Sign up at https://www.browserbase.com")
        print("2. Get your API key and Project ID from the dashboard")
        print("3. Set environment variables:")
        print("   export BROWSERBASE_API_KEY='your-api-key'")
        print("   export BROWSERBASE_PROJECT_ID='your-project-id'")
        return
    
    if not os.environ.get("BROWSERBASE_PROJECT_ID"):
        print("ERROR: BROWSERBASE_PROJECT_ID environment variable not set!")
        print("Please set: export BROWSERBASE_PROJECT_ID='your-project-id'")
        return

    print("Starting Browserbase scraper...")
    print(f"API Key: {os.environ.get('BROWSERBASE_API_KEY')[:10]}...")
    print(f"Project ID: {os.environ.get('BROWSERBASE_PROJECT_ID')}")
    
    # Define the scraping task query
    query = f"""
    You are a web scraping assistant. Please help me scrape property listings from InvestorLift.
    
    Steps to follow:
    1. You are starting at the login page: {LOGIN_URL}
    2. Log in using:
       - Email: {INVESTORLIFT_EMAIL}
       - Password: {INVESTORLIFT_PASSWORD}
       
       The login flow is:
       - Enter email in the input field
       - Click Continue
       - Enter password in the password field  
       - Click Continue again
       
    3. After login, you should be at: {MARKETPLACE_URL}
    4. Apply filters:
       - Click on "Home Type" and uncheck "Condo"
       - Search for these locations one by one: {', '.join(LOCATIONS_TO_SEARCH)}
    5. Wait for search results to load
    6. Extract all property listing links from the results page
    7. For each property listing (limit to first 5 for testing), navigate to it and extract:
       - Title
       - Price
       - Address (street, city, state, zip)
       - Description
       - Bedrooms, Bathrooms, Square Feet
       - Lot Size, Year Built
       - Property Type
       - Image URLs
    8. Report back with the data you've gathered
    
    Please proceed step by step, explaining what you're doing as you go.
    """
    
    # Use Browserbase context manager
    print("\nConnecting to Browserbase...")
    with BrowserbaseComputer(
        screen_size=(1280, 800),
        initial_url=LOGIN_URL
    ) as browser_computer:
        try:
            print("Initializing BrowserAgent...")
            agent = BrowserAgent(
                browser_computer=browser_computer,
                query=query,
                model_name="gemini-2.0-flash-exp"
            )
            
            print("\n" + "="*60)
            print("BrowserAgent is now running with Browserbase!")
            print("="*60)
            print("\nThe AI will:")
            print("1. Connect to a remote Browserbase browser")
            print("2. Navigate and log in to InvestorLift")
            print("3. Apply filters and search locations")
            print("4. Extract property data")
            print("\nMonitor the output below for progress...")
            print("="*60 + "\n")
            
            # Run the agent loop
            agent.agent_loop()
            
            if agent.final_reasoning:
                print(f"\n{'='*60}")
                print("FINAL RESULT:")
                print(f"{'='*60}")
                print(agent.final_reasoning)
                print(f"{'='*60}\n")
            
            # Note: In a production implementation, you would:
            # 1. Parse the agent's final_reasoning and conversation history
            # 2. Extract structured property data
            # 3. Save to CSV
            # For now, the AI will report what it found in final_reasoning
            
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"Error during scraping: {e}")
            print(f"{'='*60}\n")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("""
    ====================================================================
    InvestorLift Scraper - Browserbase + BrowserAgent Version
    ====================================================================
    
    This version uses:
    - Browserbase: Remote browser service to bypass bot detection
    - BrowserAgent: AI-driven automation with Gemini
    
    Benefits:
    - Bypasses CloudFront and anti-bot protections
    - Uses residential IP addresses
    - Professional browser fingerprinting
    - AI figures out the best way to interact with the site
    
    Requirements:
    - BROWSERBASE_API_KEY
    - BROWSERBASE_PROJECT_ID  
    - GEMINI_API_KEY (or Vertex AI credentials)
    
    ====================================================================
    """)
    
    main()
