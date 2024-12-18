# truffles 🍫

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/truffles.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/truffles/) [![PyPI - Installs](https://img.shields.io/pypi/dm/truffles.svg?color=blue&label=Installs&logo=pypi&logoColor=gold)](https://pypi.org/project/truffles/)

[![ci/tests](https://github.com/shoco-team/truffles/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/shoco-team/truffles/actions/workflows/ci-tests.yml) [![cd/release](https://github.com/shoco-team/truffles/actions/workflows/release-please.yml/badge.svg)](https://github.com/shoco-team/truffles/actions/workflows/release-please.yml)



An open-source framework that extends [playwright](https://playwright.dev) with automatic element detection, validation and structuring. Further utilities such as global caching of selectors reduce latency and cost.

> **Note:** Currently only supported with async playwright.

<!--<div align="center">
| | |
| --- | --- |
| CI/CD | [![ci/tests](https://github.com/shoco-team/truffles/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/shoco-team/truffles/actions/workflows/ci-tests.yml) [![cd/release](https://github.com/shoco-team/truffles/actions/workflows/release-please.yml/badge.svg)](https://github.com/shoco-team/truffles/actions/workflows/release-please.yml) |
| Meta | [![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit) |
</div>-->

<!-- | Docs |  | -->
<!-- | Package | [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/truffles.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/truffles/) [![PyPI - Installs](https://img.shields.io/pypi/dm/truffles.svg?color=blue&label=Installs&logo=pypi&logoColor=gold)](https://pypi.org/project/truffles/) | -->

## Installation

```

$ pip install truffles

```

After installation you may need to run `playwright install`. A more extensive introduction to the package can be found [here](https://github.com/shoco-ai/truffles/blob/main/examples/extract_list.ipynb).

## Quick Start
A common workflow that is fully automated by `truffles` is data extraction from list elements:

```python
import truffles
from pydantic import BaseModel

await truffles.start()

### define a schema ###
class Product(BaseModel):
    title: str = Field(description = "The name of the product")
    price: float = Field(description = "The main listed price")


### Define & Execute Task ###
task = truffles.tasks.ListingTask(
    page="https://example.com/products",
    schema=Product
)

results = await task.run()
```

## Tools

The `page.tools` and `locator.tools` currently extend playwright with automatic list detection and structured element extraction. This makes all `truffles` code
* Natively integrated with [playwright](https://playwright.dev)

* Reusable across websites

* Much more robust to page content and structure changes

### An Example Listing Task
```python
page = truffles.wrap(browser)
page.goto("https://example.com/products")


item_list = await page.tools.get_main_list() # automatically finds main list on page


task_list = [
    loc.tools.to_structure(Product) # structures locator content according to Product
    for loc in locators
]
await asyncio.gather(task_list)
```

## Tool Overview

The repo contains tools that implement common patterns for web automation. They are commonly powered by LLMs and have been extensively tested. These are:
- Automatic List Detection (see `get_main_list`)

- Intelligent & Robust Data Extraction (see `to_structure`)

- Get Element by Prompt (_under development_)

- Page to Markdown (_under development_)

- Support for Image Data (_under development_)

### Extensibility
Truffles is designed to be easily extensible. You can implement your own tools by inheriting from `BaseTool` and implementing the `execute` method.
```python

from truffles.tools import BaseTool

class ValidateElementAlignment(BaseTool):

    def execute(self, alignment_rule, prompt = None):

        # your code here
        pass

```


## The Store Manager
The `StoreManager` is internally used by tools to cache and retrieve reusable context in automations. This greatly reduces the amount of LLM calls required.

It operates mostly in the shadows and is automatically initialized when `truffles.start` is called, but it can also be initialized and accessed manually.
```python
from truffles.context import StoreManager

StoreManager.initialize()
```

In the future, a publicly accessible context will be available to further reduce costs.


## Project Status
Current development focuses on:
- Improving current tools
- Extending the functionality
- Optimizing performance of `StoreManager`
