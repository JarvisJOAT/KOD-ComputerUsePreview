# Copilot Instructions for Computer Use Preview

This document provides essential guidance for AI agents working with the Computer Use Preview codebase.

## Project Overview

Computer Use Preview is a Python-based browser automation framework that allows AI models to interact with web browsers. The project has two main browser backends:
- `playwright`: Local browser automation using Playwright
- `browserbase`: Remote browser automation using Browserbase service

## Key Components

### Core Architecture
- `main.py`: Entry point and CLI interface
- `agent.py`: Core BrowserAgent class handling model interactions and browser actions
- `computers/`: Browser automation implementations
  - `browserbase/browserbase.py`: Browserbase integration
  - `playwright/playwright.py`: Local Playwright automation

### Browser Actions

The framework provides the following browser actions, all using a normalized 1000x1000 coordinate system:

1. **Basic Navigation**:
   - `open_web_browser()`: Opens browser window
   - `navigate(url)`: Direct navigation to URL
   - `search()`: Jump to search engine
   - `go_back()/go_forward()`: Browser history navigation

2. **Interaction**:
   - `click_at(x, y)`: Mouse click at coordinates
   - `hover_at(x, y)`: Mouse hover at coordinates
   - `type_text_at(x, y, text, press_enter=True, clear_before_typing=True)`: Text input
   - `drag_and_drop(x, y, destination_x, destination_y)`: Drag and drop elements

3. **Page Control**:
   - `scroll_document(direction)`: Whole page scroll
   - `scroll_at(x, y, direction, magnitude)`: Localized scroll
   - `wait_5_seconds()`: Wait for page processes
   - `key_combination(keys)`: Keyboard shortcuts

Example usage:
```python
# Click search box
state = agent.handle_action(types.FunctionCall(
    name="click_at",
    args={"x": 500, "y": 300}
))

# Type search query
state = agent.handle_action(types.FunctionCall(
    name="type_text_at",
    args={
        "x": 500,
        "y": 300,
        "text": "search query",
        "press_enter": True
    }
))
```

### Error Handling and Retry Patterns

1. **Model Response Retries**:
```python
def get_model_response(self, max_retries=5, base_delay_s=1):
    for attempt in range(max_retries):
        try:
            return self._client.models.generate_content(...)
        except Exception as e:
            if attempt < max_retries - 1:
                delay = base_delay_s * (2**attempt)
                # Exponential backoff
                time.sleep(delay)
            else:
                raise
```

2. **Safety Confirmations**:
- Model actions requiring safety confirmations return a safety_decision object
- Agent prompts for user confirmation before proceeding
- Implement in `_get_safety_confirmation` method

3. **State Management**:
- All actions return `EnvState` objects with current URL and screenshot
- Use `current_state()` to get latest state without action

## Testing Best Practices

1. **Test Setup**:
```python
def setUp(self):
    self.mock_browser_computer = MagicMock()
    self.mock_browser_computer.screen_size.return_value = (1000, 1000)
    self.agent = BrowserAgent(
        browser_computer=self.mock_browser_computer,
        query="test query",
        model_name="test_model"
    )
```

2. **Action Testing**:
- Test each browser action independently
- Mock browser computer responses
- Verify correct coordinate normalization
- Test both success and error cases

3. **Model Integration Testing**:
- Mock model responses using FunctionCall objects
- Test complete interaction flows
- Verify state management and updates

## Performance Optimization

1. **Screenshot Management**:
- Only keep MAX_RECENT_TURN_WITH_SCREENSHOTS (3) screenshots in history
- Remove screenshots from older turns to manage memory

2. **Coordinate System**:
- Use normalized 1000x1000 coordinate system for consistent behavior
- Denormalize at action execution time
```python
def denormalize_x(self, x: int) -> int:
    return int(x / 1000 * self._browser_computer.screen_size()[0])
```

3. **Browser Session Handling**:
- Use context managers for browser sessions
- Clean up resources properly on exit
```python
def __exit__(self, exc_type, exc_val, exc_tb):
    self._page.close()
    self._context.close()
    self._browser.close()
```

## Development Workflow

1. **Setup**:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install-deps chrome
playwright install chrome
```

2. **Configuration**:
- For Gemini API: Set `GEMINI_API_KEY`
- For Vertex AI: Set `USE_VERTEXAI=true`, `VERTEXAI_PROJECT`, `VERTEXAI_LOCATION`
- For Browserbase: Set `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID`

3. **Running**:
```bash
python main.py --query="your query" --env="playwright|browserbase" [--initial_url="url"]
```

## Extension Points

1. Add custom functions by:
- Implement function in `agent.py`
- Add to `custom_functions` in `BrowserAgent.__init__`
- Add handler in `BrowserAgent.handle_action`

2. Add new browser environments by:
- Create new module under `computers/`
- Implement `Computer` interface
- Add to environment choices in `main.py`