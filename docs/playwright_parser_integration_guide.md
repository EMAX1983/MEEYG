# MEEYG 1.0 Playwright Parser Integration Guide

## Overview

This document describes how to use the new Playwright-based parser for tandoor.ru integration in MEEYG 1.0.

## Components

1. **TandoorPlaywrightParser** - New Playwright-based parser in `src/modules/parsing/tandoor_playwright_parser.py`
2. **ParserEngine enhancements** - Modified `src/modules/parsing/engine.py` to support both aiohttp and Playwright parsers
3. **Configuration** - Added Playwright settings to `.env`

## Usage

### 1. Parser Selection

The `ParserEngine` now supports two parser types:
- `"aiohttp"` (default) - Traditional parser for static content
- `"playwright"` - New parser for dynamic content

To use the Playwright parser:

```python
from src.modules.parsing.engine import ParserEngine

parser = ParserEngine(
    supplier_id=1,
    base_url="https://tandoor.ru",
    parser_type="playwright"  # Enable Playwright parser
)
```

### 2. Configuration

The following settings were added to `.env`:

```env
# Playwright settings
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=30000
PLAYWRIGHT_DELAY_MIN=1.0
PLAYWRIGHT_DELAY_MAX=3.0
```

### 3. Testing

A test script is available at `tests/test_tandoor_parser.py`:

```bash
python tests/test_tandoor_parser.py
```

### 4. Features

The Playwright parser supports:
- Dynamic content loading
- JavaScript interactions
- Radio button selection for product variations
- Automatic handling of AJAX updates
- Full product data extraction including:
  - Basic product info (title, price, SKU)
  - Images
  - Attributes
  - Molding items (accessories)
  - Product variations (sizes, types)
  
### 5. Database Integration

The parser integrates with the existing database schema:
- Main products are saved with `parent_product_id=NULL`
- Molding items are saved with `parent_product_id` linking to the main product
- Variations are saved as separate products linked to the main product
- All attributes are stored in the `product_attributes` table

## Implementation Details

### TandoorPlaywrightParser Class

Located in `src/modules/parsing/tandoor_playwright_parser.py`

Key methods:
- `parse_product_page(url)` - Parses a single product page
- `handle_variations(page, base_url)` - Handles product variations
- `parse_molding_items(soup)` - Extracts molding items
- `save_to_database(product)` - Saves product to database
- `parse_category(category_url)` - Parses a category page
- `run(category_urls)` - Main entry point

### ParserEngine Modifications

Located in `src/modules/parsing/engine.py`

Enhancements:
- Added `parser_type` parameter to constructor
- Modified `_parse_category` to delegate to Playwright parser when needed
- Updated `run` method to handle Playwright session management

## Example Usage

```python
from src.modules.parsing.engine import ParserEngine
from src.database.session import get_session

# Get database session
with get_session() as db_session:
    # Create Playwright parser
    parser = ParserEngine(
        supplier_id=1,
        base_url="https://tandoor.ru",
        parser_type="playwright",
        concurrency=3  # Limit concurrent browsers
    )
    
    # Run parser on category URLs
    result = await parser.run([
        "https://tandoor.ru/catalog/doors/"
    ], db_session)
    
    print(f"Parsed {result['products_parsed']} products")
```

## Troubleshooting

1. **Playwright not found**: Run `playwright install chromium`
2. **Browser automation issues**: Set `PLAYWRIGHT_HEADLESS=false` for debugging
3. **Slow parsing**: Adjust `PLAYWRIGHT_DELAY_MIN` and `PLAYWRIGHT_DELAY_MAX` in `.env`