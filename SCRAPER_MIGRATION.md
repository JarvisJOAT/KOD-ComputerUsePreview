# InvestorLift Scraper Migration Guide

## Overview

This document explains the migration from the direct Playwright scraper (`scraper.py`) to the Computer Use Preview framework-based scraper (`scraper_agent.py`).

## Why Migrate?

The Computer Use Preview framework provides several advantages:

1. **AI-Driven Automation**: Uses AI models (like Gemini) to intelligently navigate websites
2. **Better Error Handling**: Built-in retry mechanisms and exponential backoff
3. **Normalized Coordinate System**: 1000x1000 coordinate system for consistent behavior across screen sizes
4. **Safety Confirmations**: Built-in safety checks for potentially destructive actions
5. **State Management**: Automatic screenshot and state tracking
6. **Extensibility**: Easy to add custom functions and behaviors

## Architecture Comparison

### Original Scraper (scraper.py)
- Direct Playwright API calls
- Manual element selection using CSS selectors
- Hardcoded interaction sequences
- Manual error handling for each step

### Framework-Based Scraper (scraper_agent.py)
- Uses `BrowserAgent` class for orchestration
- AI model determines optimal actions
- Coordinate-based interactions (1000x1000 normalized)
- Built-in retry and error handling

## Two Approaches

### 1. AI-Driven Approach (Recommended for Complex Tasks)

```python
agent = BrowserAgent(
    browser_computer=browser_computer,
    query="Detailed instructions for the AI...",
    model_name="gemini-2.0-flash-exp",
    initial_url=LOGIN_URL
)
```

**Advantages:**
- AI figures out the best way to interact
- More resilient to page layout changes
- Can handle unexpected scenarios

**Disadvantages:**
- Requires API key and credits for AI model
- Less predictable execution path
- May need guidance for complex multi-step tasks

### 2. Direct Action Control (Better for Predictable Tasks)

```python
from google.ai.generativelanguage_v1beta import types

# Click at specific coordinates
state = agent.handle_action(types.FunctionCall(
    name="click_at",
    args={"x": 500, "y": 300}
))

# Type text
state = agent.handle_action(types.FunctionCall(
    name="type_text_at",
    args={
        "x": 500,
        "y": 300,
        "text": "search text",
        "press_enter": True
    }
))
```

**Advantages:**
- Precise control over each action
- No AI model costs
- Deterministic behavior

**Disadvantages:**
- Requires knowing exact coordinates
- Less resilient to layout changes
- More manual setup required

## Available Browser Actions

The framework provides these normalized actions:

### Navigation
- `open_web_browser()` - Opens browser window
- `navigate(url)` - Direct URL navigation
- `search()` - Jump to search engine
- `go_back()` / `go_forward()` - History navigation

### Interaction
- `click_at(x, y)` - Click at coordinates
- `hover_at(x, y)` - Hover at coordinates
- `type_text_at(x, y, text, press_enter, clear_before_typing)` - Type text
- `drag_and_drop(x, y, destination_x, destination_y)` - Drag/drop

### Page Control
- `scroll_document(direction)` - Full page scroll
- `scroll_at(x, y, direction, magnitude)` - Localized scroll
- `wait_5_seconds()` - Wait for page load
- `key_combination(keys)` - Keyboard shortcuts

## Setup Requirements

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install-deps chrome
playwright install chrome
```

### Environment Variables

For AI-driven approach, set one of:

**Option 1: Gemini API**
```bash
export GEMINI_API_KEY="your-api-key"
```

**Option 2: Vertex AI**
```bash
export USE_VERTEXAI=true
export VERTEXAI_PROJECT="your-project-id"
export VERTEXAI_LOCATION="us-central1"
```

## Running the Scrapers

### Original Scraper
```bash
python scraper.py
```

### Framework-Based Scraper
```bash
python scraper_agent.py
```

## Implementation Roadmap

To fully implement the framework-based scraper, you would need to:

### Phase 1: Basic Integration ✅
- [x] Create scraper_agent.py with BrowserAgent integration
- [x] Set up browser computer instance
- [x] Define scraping query for AI model

### Phase 2: Data Extraction (Next Steps)
- [ ] Extend BrowserAgent to support data extraction callbacks
- [ ] Add method to parse property data from screenshots/context
- [ ] Implement structured data collection

### Phase 3: State Management
- [ ] Add progress tracking for multi-property scraping
- [ ] Implement checkpoint/resume functionality
- [ ] Handle pagination for large result sets

### Phase 4: Error Handling
- [ ] Add retry logic for failed property scrapes
- [ ] Implement graceful degradation for missing fields
- [ ] Add comprehensive logging

### Phase 5: Optimization
- [ ] Cache login session to avoid re-authentication
- [ ] Parallelize property detail scraping
- [ ] Optimize screenshot storage

## Example: Converting a Scraper Action

### Original (scraper.py)
```python
page.fill("input[placeholder='Email address']", INVESTORLIFT_EMAIL)
page.click("button:has-text('Continue')")
```

### Framework-Based (scraper_agent.py)
```python
# AI-Driven
query = "Fill in the email field with my email and click Continue"

# Or Direct Control
state = agent.handle_action(types.FunctionCall(
    name="type_text_at",
    args={"x": 500, "y": 300, "text": INVESTORLIFT_EMAIL}
))
state = agent.handle_action(types.FunctionCall(
    name="click_at",
    args={"x": 500, "y": 400}
))
```

## Coordinate System

The framework uses a normalized 1000x1000 coordinate system:

```python
# Original screen: 1920x1080
# Element at pixel (960, 540) = center

# Framework coordinates
x = 500  # (960 / 1920) * 1000
y = 500  # (540 / 1080) * 1000

agent.handle_action(types.FunctionCall(
    name="click_at",
    args={"x": 500, "y": 500}  # Clicks center regardless of screen size
))
```

## Best Practices

1. **Start Simple**: Begin with AI-driven approach for exploration
2. **Add Precision**: Switch to direct control for production reliability
3. **Error Handling**: Use try/except blocks and the framework's retry mechanisms
4. **State Tracking**: Monitor the EnvState objects returned by each action
5. **Screenshots**: Use screenshots for debugging and verification
