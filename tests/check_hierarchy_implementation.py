#!/usr/bin/env python3
"""
Verification script for hierarchy parsing implementation
"""

import json
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_implementation():
    """Verify that the implementation is correct"""
    
    print("=== Implementation Verification ===")
    
    # Check that required methods exist in engine.py
    engine_path = Path(__file__).parent.parent / "src" / "modules" / "parsing" / "engine.py"
    if not engine_path.exists():
        print("ERROR: engine.py not found")
        return False
        
    engine_content = engine_path.read_text(encoding='utf-8')
    
    # Check for _extract_variations method
    if "_extract_variations" not in engine_content:
        print("ERROR: _extract_variations method not found in engine.py")
        return False
        
    # Check for _upsert_molding_item method
    if "_upsert_molding_item" not in engine_content:
        print("ERROR: _upsert_molding_item method not found in engine.py")
        return False
        
    # Check for variations handling in _save_batch
    if "variations" not in engine_content:
        print("WARNING: Variations handling may not be implemented in _save_batch")
        
    print("[OK] engine.py contains required methods")
    
    # Check that required methods exist in tandoor_playwright_parser.py
    parser_path = Path(__file__).parent.parent / "src" / "modules" / "parsing" / "tandoor_playwright_parser.py"
    if not parser_path.exists():
        print("ERROR: tandoor_playwright_parser.py not found")
        return False
        
    parser_content = parser_path.read_text(encoding='utf-8')
    
    # Check for _extract_variations method
    if "_extract_variations" not in parser_content:
        print("ERROR: _extract_variations method not found in tandoor_playwright_parser.py")
        return False
        
    # Check for _upsert_molding_item method
    if "_upsert_molding_item" not in parser_content:
        print("ERROR: _upsert_molding_item method not found in tandoor_playwright_parser.py")
        return False
        
    print("[OK] tandoor_playwright_parser.py contains required methods")
    
    # Check that test file exists
    test_path = Path(__file__).parent.parent / "tests" / "test_hierarchy_logic.py"
    if not test_path.exists():
        print("ERROR: test_hierarchy_logic.py not found")
        return False
        
    print("[OK] test_hierarchy_logic.py exists")
    
    print("\n=== Verification Passed ===")
    return True


if __name__ == "__main__":
    success = check_implementation()
    sys.exit(0 if success else 1)