from bs4 import BeautifulSoup
import json

def main():
    try:
        print("--- Starting Parser Test ---")
        with open("property_detail.html.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        soup = BeautifulSoup(content, "lxml")
        script_tag = soup.find('script', string=lambda t: t and 'window.__NUXT__=' in t)
        script_content = script_tag.string

        # Isolate the part of the script after 'window.__NUXT__.config='
        # This is where the actual data seems to be
        if 'window.__NUXT__.config=' in script_content:
            target_text = script_content.split('window.__NUXT__.config=', 1)[1]
        else:
            raise ValueError("Could not find 'window.__NUXT__.config=' in script tag.")

        # Find the first opening brace
        start_index = target_text.find('{')
        if start_index == -1:
            raise ValueError("Could not find starting '{' for NUXT config object")

        # Bracket-matching to find the corresponding closing brace
        open_braces = 1
        end_index = -1
        for i, char in enumerate(target_text[start_index + 1:]):
            if char == '{':
                open_braces += 1
            elif char == '}':
                open_braces -= 1
            
            if open_braces == 0:
                end_index = start_index + i + 2 # +1 for current char, +1 for 0-based index
                break
        
        if end_index == -1:
            raise ValueError("Could not find matching '}' for NUXT config object")

        # Slice the string to get only the JSON part
        json_text = target_text[start_index:end_index]

        # Parse the isolated JSON
        nuxt_data = json.loads(json_text)

        print("--- Full NUXT Config Data ---")
        print(json.dumps(nuxt_data, indent=2))
        print("-----------------------------")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
