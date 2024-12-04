# Truffle 🍄

> AI-powered web agents and data extraction, made scalable and reusable.

Truffle is an open-source framework that brings AI capabilities to web automation and data extraction while keeping costs low and reusability high.

```python
from truffle import wrap
async def extract_products():
    page = await wrap(browser)
    await page.goto("https://example.com/products")
    # Automatically finds and extracts product list
    products = await page.get_main_list()
    # AI assistance only used if needed, results cached for reuse
    for product in products:
        title = await product.get_text("h2")
        price = await product.get_text("[data-price]")
```

## Key Features

### 🧠 Context-Aware Automation
The ContextStore system remembers successful element selectors and interaction patterns, reducing unnecessary AI calls and making your automations more reliable:

- **Cost Efficient**: AI is only used when needed, with successful patterns cached for reuse
- **Self-Learning**: Builds a knowledge base of working selectors across different sites
- **Flexible Storage**: In-memory, persistent, or distributed storage options

### 🛠️ Intelligent Tools

- **List Detection**: Automatically identifies and extracts repeated content patterns
- **Smart Navigation**: Context-aware pagination and traversal
- **Attribute Matching**: Flexible element location using partial or exact matches
- **More Coming**: Structure recognition, form filling, and other AI-powered capabilities

## Why Truffle?

- **Reduced Costs**: Minimize AI usage through intelligent caching
- **Better Reliability**: Self-healing automations that adapt to site changes
- **Developer Friendly**: Clean API that feels like standard Playwright
- **Production Ready**: Built for scale with async support and flexible storage

## Status

This project is under active development. We're working on:
- Additional AI-powered tools
- Enhanced context management
- Documentation and examples
- Performance optimizations

## Contributing

We welcome contributions! Check out our issues page or contact us directly.

