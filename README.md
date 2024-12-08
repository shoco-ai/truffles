# truffles 🍪
A python framework that extends [playwright](https://playwright.dev/) with language model tools for web automation and data extraction.

```python
page = truffle.wrap(browser)
page.goto("https://example.com/products")

# auto list detection
items = await page.get_main_list() 

# structure from locator
products = await items.to_structure(
    {
        "title": str, 
        "price": float
    }
) 
```

## Features

### Implemented Tools
The repo contains a few tools that implement common patterns for web automation, that are powered by LLMs and have been proven to work well in the wild.
Currently, the following tools are implemented or in the works:
- Automatic List Detection
- Autonomous Pagination (under development)
- Intelligent Data Extraction (under development)

### Context Manager
The `ContextManager` is internally used by tools to store and retrieve reusable context in automations. This greatly reduces the amount of LLM calls required.
In the future, a shared context will be publicly available to further reduce costs.
The `ContextManager` operates mostly in the background, but it can be accessed directly if needed.
```python
from truffle.context import ContextManager

ContextManager.initialize()
```

### Tool Extensibility
The framework is designed to be easily extensible. You can implement your own tools by inheriting from `BaseTool` and implementing the `execute` method.
```python
from truffle.tools import BaseTool

class MyTool(BaseTool): 

    def execute(self, *args, **kwargs):
        pass
```

## Technical Details
- Asynchronous architecture
- Built to extend existing playwright projects
- Fully integrable with langchain supported models

## A more extensive setup example
```python
from playwright.async_api import async_playwright
from truffle.models import LLMManager
from truffle.context import ContextManager, MemoryContextStore

ContextManager.initialize(MemoryContextStore())

LLMManager.initialize(
    model=ChatAnthropic(model="claude-3-5-sonnet-20241022")
)

p = await async_playwright().start()
browser = await p.chromium.launch()
page = truffle.wrap(browser)
```

## Project Status
Current development focuses on:
- Improving current tools
- Adding more tools
- Optimizing caching performance


