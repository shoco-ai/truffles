# Truffle 🍄

> The first open-source framework for AI-powered web automation that builds on Playwright and learns globally.

Truffle extends Playwright with AI capabilities for web automation and data extraction, while introducing revolutionary global caching of AI interactions that the entire community can benefit from.

```python
from truffle import wrap
async def extract_products():
    page = await wrap(browser)  # Wraps any Playwright browser
    await page.goto("https://example.com/products")
    # AI-powered automation with community-shared intelligence
    products = await page.get_main_list()
    # Use familiar Playwright syntax with AI assistance when needed
    for product in products:
        title = await product.get_text("h2")
        price = await product.get_text("[data-price]")
```

## Why Truffle is Revolutionary

### 🌐 100% Open Source
- **Fully Transparent**: Every component is open source, from AI prompts to caching logic
- **Community Driven**: Shape the future of AI automation through contributions
- **No Vendor Lock-in**: Own and control your automation infrastructure

### 🧠 Global Intelligence Sharing
- **Community Knowledge Base**: Successfully used prompts and patterns are shared globally
- **Collective Learning**: Each automation makes the entire system smarter
- **Cost Sharing**: Benefit from cached AI interactions across all users

### ⚡ Seamless Playwright Integration
- **Drop-in Enhancement**: Add to existing Playwright projects with a single wrapper
- **Familiar Syntax**: Keep using Playwright's intuitive API
- **Best of Both Worlds**: Combine Playwright's reliability with AI capabilities

## Key Features

### 🛠️ Intelligent Tools with Global Caching
- **Smart List Detection**: Automatically identifies content patterns
- **Context-Aware Navigation**: Intelligent pagination and traversal
- **Flexible Element Location**: AI-powered element finding
- All powered by community-shared intelligence

### 📦 Production Ready
- **Built on Playwright**: Enterprise-grade foundation
- **Async Support**: Built for scale
- **Flexible Storage**: Choose your caching strategy

## Status

This is an active open-source project. We're working on:
- Expanding the shared knowledge base
- Additional AI-powered capabilities
- Enhanced documentation and examples
- Performance optimizations

## Contributing

Join us in revolutionizing web automation! Check out our issues page or contact us directly.

