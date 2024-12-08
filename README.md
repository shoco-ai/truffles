# truffles 🍫
A python framework that extends [playwright](https://playwright.dev/) with language model tools (`page.tools`) for web automation and data extraction.

> **Note:** Currently only supported with async playwright.

<div align="center">

| | |
| --- | --- |
| CI/CD | [![ci/tests](https://github.com/shoco-team/truffles/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/shoco-team/truffles/actions/workflows/ci-tests.yml) [![cd/release](https://github.com/shoco-team/truffles/actions/workflows/release-please.yml/badge.svg)](https://github.com/shoco-team/truffles/actions/workflows/release-please.yml) |
| Meta | [![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit) |

</div>

<!-- | Docs |  | -->
<!-- | Package | [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/truffles.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/truffles/) [![PyPI - Installs](https://img.shields.io/pypi/dm/truffles.svg?color=blue&label=Installs&logo=pypi&logoColor=gold)](https://pypi.org/project/truffles/) | -->


An open-source framework that extends Playwright with AI capabilities for web automation and data extraction. truffles implements global caching of AI interactions to improve efficiency across the community.

```python
page = truffles.wrap(browser)

# go to your favorite website
page.goto("https://example.com/products")

# auto list detection
items = await page.tools.get_main_list()

# json structure from locator
products = await items.tools.to_structure(
    {
        "title": str,
        "price": float
    }
)
```

## Tools

The `.tools` attribute is a namespace for all added tools, cleanly separating them from the page object.

### Implemented Tools
The repo contains a few tools that implement common patterns for web automation, that are powered by LLMs and have been proven to work well in the wild.
Currently, the following tools are implemented or in the works:
- Automatic List Detection
- Autonomous Pagination (_under development_)
- Intelligent & Safe Data Extraction (_under development_)

### Context Manager
The `ContextManager` is internally used by tools to store and retrieve reusable context in automations. This greatly reduces the amount of LLM calls required.
In the future, a publicly shared context will be available as an optional feature to further reduce costs.
The `ContextManager` operates mostly in the background and is automatically initialized when `truffles.astart` is called, but it can also be initialized and accessed manually.
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
- Built to seamlessly extend existing playwright projects
- Out-of-the-box support for langchain supported models

## A more extensive setup example
```python
from playwright.async_api import async_playwright
import truffles

p = await async_playwright().start()
browser = await p.chromium.launch()

# initializes the default model and context manager
await truffles.astart()
page = truffles.wrap(browser)

# your code here

```

## Project Status
Current development focuses on:
- Improving current tools
- Extending the functionality
- Optimizing performance of `ContextManager`
