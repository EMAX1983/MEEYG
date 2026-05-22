import asyncio
import os
import sys
from typing import List

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.parsing.tandoor_playwright_parser import TandoorPlaywrightParser
from src.database.session import get_session
from src.database.models import Supplier

async def test_parse_product_page():
    """Test parsing a single product page."""
    # Test URL
    test_url = "https://tandoor.ru/catalog/product/dekanto-belyy-evo-pet-do-seryy-satin-2000-800/"
    
    # Get database session
    with get_session() as db_session:
        # Get supplier (assuming supplier with ID 1 exists)
        supplier = db_session.query(Supplier).first()
        if not supplier:
            print("No supplier found in database")
            return
            
        # Create parser instance
        parser = TandoorPlaywrightParser(
            supplier_id=supplier.id,
            db_session=db_session,
            headless=True,
            delay_range=(1.0, 3.0),
            log_callback=print,
            progress_callback=lambda p, t, m: print(f"Progress: {p}% - {m}")
        )
        
        try:
            # Parse product page
            print(f"Parsing product page: {test_url}")
            result = await parser.parse_product_page(test_url)
            
            # Print results
            print(f"Title: {result.title}")
            print(f"Price: {result.price}")
            print(f"Currency: {result.currency}")
            print(f"SKU: {result.sku}")
            print(f"Description: {result.description}")
            print(f"Images: {len(result.image_urls)}")
            print(f"Molding items: {len(result.molding_items)}")
            print(f"Variations: {len(result.variations)}")
            
            # Print attributes
            print("Attributes:")
            for name, value in result.attributes.items():
                print(f"  {name}: {value}")
                
            # Print molding items
            if result.molding_items:
                print("Molding Items:")
                for item in result.molding_items:
                    print(f"  - {item['title']} ({item['type']}) - {item['price']} RUB")
                    
            # Print variations
            if result.variations:
                print("Variations:")
                for variation in result.variations:
                    print(f"  - {variation.title} - {variation.price} {variation.currency}")
                    
        except Exception as e:
            print(f"Error during test: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(test_parse_product_page())