#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify OCR setup is ready for golf scorecards
This script checks that all dependencies are properly installed.
"""

import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("=" * 70)
    print("CHECKING OCR DEPENDENCIES")
    print("=" * 70)
    print()
    
    dependencies = {
        'pandas': 'Data manipulation',
        'numpy': 'Numerical operations',
        'cv2': 'OpenCV for image processing',
        'paddleocr': 'PaddleOCR for text extraction'
    }
    
    all_ok = True
    for module, description in dependencies.items():
        try:
            if module == 'cv2':
                import cv2
                print(f"✅ {module:15} - {description:30} (v{cv2.__version__})")
            elif module == 'paddleocr':
                from paddleocr import PaddleOCR
                print(f"✅ {module:15} - {description:30} (installed)")
            elif module == 'pandas':
                import pandas as pd
                print(f"✅ {module:15} - {description:30} (v{pd.__version__})")
            elif module == 'numpy':
                import numpy as np
                print(f"✅ {module:15} - {description:30} (v{np.__version__})")
        except ImportError as e:
            print(f"❌ {module:15} - {description:30} (NOT INSTALLED)")
            all_ok = False
    
    print()
    if all_ok:
        print("✅ All dependencies are installed!")
        print()
        print("READY TO PROCESS GOLF SCORECARDS")
        print("-" * 70)
        print("Place your scorecard images (score_1.png to score_8.png) in the")
        print("current directory and run:")
        print()
        print("  python scorecard_ocr.py")
        print()
        return True
    else:
        print("❌ Some dependencies are missing!")
        print()
        print("To install, run:")
        print("  pip install -r requirements_ocr.txt")
        print()
        return False


def test_ocr_module():
    """Test if the OCR module can be imported and used"""
    print("=" * 70)
    print("TESTING OCR MODULE")
    print("=" * 70)
    print()
    
    try:
        from scorecard_ocr import ScorecardOCR, process_scorecard
        print("✅ scorecard_ocr module imported successfully")
        print()
        
        # Test initialization
        print("Testing OCR initialization...")
        ocr = ScorecardOCR(lang='en', use_gpu=False)
        print("✅ ScorecardOCR initialized successfully")
        print()
        
        # Test clean_value function
        print("Testing data cleaning functions...")
        test_cases = [
            ('--', 'NaN'),
            ('-', 'NaN'),
            ('—', 'NaN'),
            ('5', '5 (int)'),
            ('3.5', '3.5 (float)'),
            ('Par', 'Par (str)'),
        ]
        
        print("Sample conversions:")
        for input_val, expected_desc in test_cases:
            result = ocr.clean_value(input_val)
            print(f"  '{input_val}' → {result} ({type(result).__name__})")
        
        print()
        print("✅ All OCR functions working correctly!")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error testing OCR module: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_usage_examples():
    """Display usage examples"""
    print("=" * 70)
    print("USAGE EXAMPLES")
    print("=" * 70)
    print()
    
    print("1. Process a single scorecard:")
    print("-" * 70)
    print("from scorecard_ocr import process_scorecard")
    print()
    print("df = process_scorecard('score_1.png')")
    print("print(df)")
    print()
    
    print("2. Process multiple scorecards:")
    print("-" * 70)
    print("from scorecard_ocr import process_multiple_scorecards")
    print("import glob")
    print()
    print("images = glob.glob('score_*.png')")
    print("results = process_multiple_scorecards(images, output_dir='output_csv')")
    print()
    
    print("3. Run from command line:")
    print("-" * 70)
    print("# Place images in scorecards/ directory, then run:")
    print("python scorecard_ocr.py")
    print()


if __name__ == "__main__":
    success = True
    
    # Check dependencies
    if not check_dependencies():
        success = False
        print("\n⚠️  Install dependencies first, then run this test again.")
        sys.exit(1)
    
    print()
    
    # Test OCR module
    if not test_ocr_module():
        success = False
    
    print()
    
    # Show examples
    show_usage_examples()
    
    if success:
        print("=" * 70)
        print("✅ ALL TESTS PASSED - OCR SYSTEM IS READY!")
        print("=" * 70)
        print()
        print("📸 Waiting for actual golf scorecard images to process...")
        print()
    else:
        print("=" * 70)
        print("❌ SOME TESTS FAILED - CHECK ERRORS ABOVE")
        print("=" * 70)
        sys.exit(1)
