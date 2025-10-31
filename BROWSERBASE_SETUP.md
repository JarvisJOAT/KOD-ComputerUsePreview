# Browserbase Setup Guide

## What is Browserbase?

Browserbase is a managed browser infrastructure service that provides:
- Remote browser instances designed for automation
- Residential IP addresses to bypass bot detection
- Professional browser fingerprinting
- Built-in support in the Computer Use Preview framework

## Quick Setup Steps

### 1. Sign Up for Browserbase

Visit: https://www.browserbase.com

- Click "Sign Up" or "Get Started"
- Create an account (they offer a free tier)
- Verify your email

### 2. Get Your API Credentials

Once logged in:

1. Go to your **Dashboard**
2. Navigate to **Settings** or **API Keys**
3. You'll need two values:
   - **API Key** (looks like: `bb_live_xxxxxxxxxxxxx`)
   - **Project ID** (looks like: `proj_xxxxxxxxxxxxx`)

### 3. Set Environment Variables

#### On macOS/Linux:

```bash
# Add to your shell profile (~/.zshrc or ~/.bashrc)
export BROWSERBASE_API_KEY="bb_live_your_key_here"
export BROWSERBASE_PROJECT_ID="proj_your_id_here"

# Or set temporarily for current session:
export BROWSERBASE_API_KEY="bb_live_your_key_here"
export BROWSERBASE_PROJECT_ID="proj_your_id_here"
```

#### To make permanent:

```bash
# Add to .venv/bin/activate
echo 'export BROWSERBASE_API_KEY="bb_live_your_key_here"' >> .venv/bin/activate
echo 'export BROWSERBASE_PROJECT_ID="proj_your_id_here"' >> .venv/bin/activate

# Reload the virtual environment
deactivate
source .venv/bin/activate
```

### 4. Verify Setup

```bash
# Check if variables are set
echo $BROWSERBASE_API_KEY
echo $BROWSERBASE_PROJECT_ID
```

### 5. Run the Scraper

```bash
python scraper_browserbase.py
```

## What You Get with Browserbase

### Free Tier (Typical Limits)
- ~1,000 session minutes per month
- Access to basic features
- Perfect for testing and small projects

### Benefits for InvestorLift Scraping
- ✅ Bypasses CloudFront 403 errors
- ✅ Uses residential IPs (looks like real user)
- ✅ Professional browser fingerprinting
- ✅ No local Chrome installation issues
- ✅ Scalable infrastructure

## Troubleshooting

### "API Key not set" Error
Make sure you've exported the environment variables in your current terminal session.

### "Connection failed" Error
Check that:
1. Your API key and Project ID are correct
2. You have active session minutes in your Browserbase account
3. Your internet connection is working

### "Computer Use not enabled" Error
This is a separate issue with Gemini API - see the main README for Computer Use API access.

## Alternative: Use Without Computer Use API

If you don't have Computer Use API access yet, you can still use Browserbase with direct Playwright commands:

```python
from computers.browserbase.browserbase import BrowserbaseComputer

with BrowserbaseComputer() as browser:
    # Use browser like regular Playwright
    # But through Browserbase infrastructure
```

## Cost Considerations

- **Free Tier**: Great for development and testing
- **Paid Plans**: If you need more session minutes
- **Cost vs Benefit**: Much cheaper than maintaining proxy infrastructure

## Security Notes

- Keep your API keys secure
- Don't commit them to git
- Use environment variables
- Consider using a `.env` file with python-dotenv for production

## Next Steps

Once set up, the scraper will:
1. Connect to a Browserbase remote browser
2. Use AI (via Gemini) to navigate InvestorLift
3. Bypass CloudFront protection automatically
4. Extract property data

The combination of Browserbase (bot avoidance) + BrowserAgent (AI navigation) is the most robust solution for complex web scraping.
