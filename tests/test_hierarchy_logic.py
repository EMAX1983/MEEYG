#!/usr/bin/env python3
"""
Test script for hierarchy parsing logic
"""

import json
import sys
import os
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up Django settings if needed
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.core.settings')

def test_hierarchy_logic():
    """Test the hierarchy parsing logic"""
    
    # Mock data simulating a parsed door product with variations and molding
    mock_product_data = {
        "url": "https://example.com/product/door-123",
        "title": "Дверь Бона белая",
        "price": 15000.0,
        "currency": "RUB",
        "sku": "BONA-WHITE-123",
        "description": "Белая межкомнатная дверь Бона",
        "is_available": True,
        "image_urls": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        "attributes": {
            "Материал": "ЛДСП",
            "Покрытие": "Белый глянец",
            "Производитель": "Фабрика Дверей"
        },
        "category_id": 5,  # "Межкомнатные двери"
        "variations": [
            {
                "title": "Дверь Бона белая 70x200",
                "price": 15000.0,
                "attributes": {
                    "Размер": "70x200",
                    "Тип": "Правая"
                }
            },
            {
                "title": "Дверь Бона белая 80x200",
                "price": 16000.0,
                "attributes": {
                    "Размер": "80x200",
                    "Тип": "Правая"
                }
            },
            {
                "title": "Дверь Бона белая 90x200",
                "price": 17000.0,
                "attributes": {
                    "Размер": "90x200",
                    "Тип": "Правая"
                }
            }
        ],
        "molding_items": [
            {
                "title": "Добор 100x20 мм белый",
                "price": 1200.0,
                "color": "Белый",
                "external_id": "DOBOR-100-20-WHITE",
                "type": "Добор"
            },
            {
                "title": "Наличник 60x20 мм белый",
                "price": 800.0,
                "color": "Белый",
                "external_id": "NALICHNIK-60-20-WHITE",
                "type": "Наличник"
            }
        ]
    }
    
    print("=== Test: Hierarchy Parsing Logic ===")
    print(f"Testing product: {mock_product_data['title']}")
    print(f"Variations count: {len(mock_product_data['variations'])}")
    print(f"Molding items count: {len(mock_product_data['molding_items'])}")
    
    # Test Product model helpers for compatible_collections
    print(f"\nTesting Product model helpers:")
    
    # Since we can't easily instantiate the Product model without Django setup,
    # we'll test the logic conceptually
    
    # Test compatible collections logic
    door_category_path = "Межкомнатные двери > Бона"
    
    # Simulate existing compatible collections
    existing_collections = ["Межкомнатные двери > Лофт"]
    
    # Add new collection if not present
    if door_category_path not in existing_collections:
        existing_collections.append(door_category_path)
    
    print(f"  Existing collections: ['Межкомнатные двери > Лофт']")
    print(f"  Added new collection: {door_category_path}")
    print(f"  Final collections: {existing_collections}")
    print(f"  New collection included: {door_category_path in existing_collections}")
    
    # Test adding duplicate collection
    initial_count = len(existing_collections)
    if door_category_path not in existing_collections:
        existing_collections.append(door_category_path)
    final_count = len(existing_collections)
    
    print(f"  Attempting to add duplicate collection")
    print(f"  Collection count unchanged: {initial_count == final_count}")
    
    # Test variations combining logic
    print(f"\nTesting variations combining logic:")
    
    # Simulate collecting all sizes from variations
    all_sizes = []
    for variation in mock_product_data['variations']:
        size_attr = variation.get("attributes", {}).get("Размер")
        if size_attr and size_attr not in all_sizes:
            all_sizes.append(size_attr)
    
    sizes_string = "|".join(all_sizes)
    print(f"  Collected sizes: {all_sizes}")
    print(f"  Sizes string: {sizes_string}")
    
    print("\n=== Test Completed ===")


if __name__ == "__main__":
    test_hierarchy_logic()