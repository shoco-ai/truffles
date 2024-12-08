# truffles 🍪
A python framework that extends [playwright](https://playwright.dev/) with AI tools for web automation and data extraction.

```python
page = truffle.wrap(browser)
page.goto("https://example.com/products")

items = await page.get_main_list() # auto list detection

products = await items.to_structure({"title": str, "price": float}) # structure from locator
```

## Features

### Implemented Tools
The repo contains a few tools that implement common patterns for web automation, that are powered by LLMs and have been proven to work well in the wild.
- List Detector
- Page Navigation
- Data Extraction

### Context Manager
The context manager is internally used by tools to store and retrieve reusable context in automations. This greatly reduces the amount of LLM calls required.


### Tool Extensibility
The framework is designed to be easily extensible. You can implement your own tools by inheriting from the base classes.


## Technical Details
- Built on Playwright's production-tested foundation
- Asynchronous architecture
- Configurable caching backend
- Comprehensive error handling

## Project Status
Current development focuses on:
- Expanding automation capabilities
- Optimizing caching performance
- Improving documentation
- Adding usage examples


