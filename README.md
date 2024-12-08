# truffles 🍫
A python framework that extends [playwright](https://playwright.dev/) with language model tools for web automation and data extraction.

```python
page = truffles.wrap(browser)

# go to your favorite website
page.goto("https://example.com/products")

# auto list detection
items = await page.get_main_list() 

# json structure from locator
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
- Autonomous Pagination (_under development_)
- Intelligent Data Extraction (_under development_)

### Context Manager
The `ContextManager` is internally used by tools to store and retrieve reusable context in automations. This greatly reduces the amount of LLM calls required.
In the future, a shared context will be publicly available to further reduce costs.
The `ContextManager` operates mostly in the background and is automatically initialized when `truffles.astart` is called, but it can also be initialized and accessedmanually.
```python
from truffles.context import ContextManager

ContextManager.initialize()
```

### Tool Extensibility
The framework is designed to be easily extensible. You can implement your own tools by inheriting from `BaseTool` and implementing the `execute` method.
```python
from truffles.tools import BaseTool

class MyTool(BaseTool): 

    def execute(self, *args, **kwargs):
        # your code here
        pass
```

## Technical Details
- Asynchronous architecture
- Built to extend existing playwright projects
- Fully integrable with langchain supported models

## A more extensive setup example
```python
from playwright.async_api import async_playwright
import truffles

p = await async_playwright().start()
browser = await p.chromium.launch()

await truffles.astart()
page = truffles.wrap(browser)

# your code here
```

## Project Status
Current development focuses on:
- Improving current tools
- Adding more tools
- Optimizing caching performance


