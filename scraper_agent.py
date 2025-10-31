"""
InvestorLift Property Scraper using Computer Use Preview Framework
This version uses the BrowserAgent class for AI-driven browser automation.
"""
import csv
import os
from agent import BrowserAgent
from computers.playwright.playwright import PlaywrightComputer

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
    Main function to run the scraper using BrowserAgent.
    """
    if INVESTORLIFT_EMAIL == "<YOUR_EMAIL>" or INVESTORLIFT_PASSWORD == "<YOUR_PASSWORD>":
        print("ERROR: Please fill in your credentials.")
        return

    print("Starting AI-powered scraper using BrowserAgent...")
    
    # Initialize the BrowserAgent with the task query
    query = f"""
    You are a web scraping assistant. Please help me scrape property listings from InvestorLift.
    
    Steps to follow:
    1. Navigate to the login page: {LOGIN_URL}
    2. Log in using:
       - Email: {INVESTORLIFT_EMAIL}
       - Password: {INVESTORLIFT_PASSWORD}
    3. After login, you should be at: {MARKETPLACE_URL}
    4. Apply filters:
       - Click on "Home Type" and uncheck "Condo"
       - Search for these locations one by one: {', '.join(LOCATIONS_TO_SEARCH)}
    5. Wait for search results to load
    6. Extract all property listing links from the results page
    7. For each property listing, navigate to it and extract:
       - Title
       - Price
       - Address (street, city, state, zip)
       - Description
       - Bedrooms, Bathrooms, Square Feet
       - Lot Size, Year Built
       - Property Type
       - Image URLs
    8. Save all the data
    
    Please proceed with these steps and let me know when you've gathered all the property data.
    """
    
    # Use context manager for proper browser cleanup
    with PlaywrightComputer(
        screen_size=(1280, 800),
        initial_url=LOGIN_URL
    ) as browser_computer:
        try:
            agent = BrowserAgent(
                browser_computer=browser_computer,
                query=query,
                model_name="gemini-2.0-flash-exp"
            )
            
            print("Agent initialized. Starting automation...")
            
            print("""
            ============================================================
            BrowserAgent is now running. The AI model will attempt to:
            1. Log in to InvestorLift
            2. Apply filters
            3. Extract property listings
            
            The agent will use AI to determine the best actions to take.
            Monitor the browser window to see the automation in progress.
            ============================================================
            """)
            
            # Run the agent loop
            agent.agent_loop()
            
            if agent.final_reasoning:
                print(f"\n{'='*60}")
                print(f"Final Result: {agent.final_reasoning}")
                print(f"{'='*60}")
            
            # For a production implementation, you would need to:
            # - Add a mechanism to extract structured data from the agent's context
            # - Implement callbacks to save data as it's collected
            # - Parse the agent's reasoning and screenshots to extract property data
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            import traceback
            traceback.print_exc()


def scrape_with_framework_actions():
    """
    Alternative approach: Use BrowserAgent's action methods directly.
    This provides more control over the scraping process.
    """
    print("Starting scraper with direct action control...")
    
    with PlaywrightComputer(
        screen_size=(1280, 800),
        initial_url=LOGIN_URL
    ) as browser_computer:
        agent = BrowserAgent(
            browser_computer=browser_computer,
            query="Scrape InvestorLift properties",
            model_name="gemini-2.0-flash-exp"
        )
        
        # Example of using agent actions:
        # 1. Navigate to login page (already done via initial_url)
        
        # 2. Click on email input field (coordinates would need to be determined)
        # state = agent.handle_action(types.FunctionCall(
        #     name="click_at",
        #     args={"x": 500, "y": 300}
        # ))
        
        # 3. Type email
        # state = agent.handle_action(types.FunctionCall(
        #     name="type_text_at",
        #     args={
        #         "x": 500,
        #         "y": 300,
        #         "text": INVESTORLIFT_EMAIL,
        #         "press_enter": False
        #     }
        # ))
        
        # And so on...
        
        print("""
        This approach requires knowing the exact coordinates for each element.
        For a fully working implementation, you would need to:
        1. Inspect the page to get element coordinates
        2. Use the normalized 1000x1000 coordinate system
        3. Execute each action step-by-step
        4. Parse the screenshots/state to extract data
        """)


if __name__ == "__main__":
    print("""
    ====================================================================
    InvestorLift Scraper - Computer Use Preview Framework Version
    ====================================================================
    
    This version demonstrates how to use the BrowserAgent framework
    for web scraping. The framework uses AI models to interact with
    the browser in a more intelligent way.
    
    Note: For production use, you would need to extend the framework
    to support structured data extraction and storage.
    
    Options:
    1. AI-driven approach (let the model figure out the actions)
    2. Direct action control (manually specify each browser action)
    
    Running AI-driven approach...
    ====================================================================
    """)
    
    main()
