#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo script for Golf Scorecard OCR Processing

This script demonstrates how to use the scorecard OCR functionality.
It includes a simulated example showing expected input/output.
"""

import os
import sys

def demo_without_dependencies():
    """
    Demonstrates the expected functionality without requiring
    actual OCR dependencies to be installed.
    """
    print("=" * 70)
    print("GOLF SCORECARD OCR - DEMONSTRATION")
    print("=" * 70)
    
    print("\n📋 OVERVIEW")
    print("-" * 70)
    print("This tool processes golf scorecard images and converts them to")
    print("pandas DataFrames using PaddleOCR.")
    print()
    print("Features:")
    print("  ✓ High-accuracy OCR using PaddleOCR")
    print("  ✓ Automatic table detection and organization")
    print("  ✓ Converts '--' to NaN for missing values")
    print("  ✓ Automatic numeric type conversion")
    print("  ✓ Batch processing support")
    print("  ✓ CSV export capability")
    
    print("\n📦 INSTALLATION")
    print("-" * 70)
    print("1. Install dependencies:")
    print("   pip install -r requirements_ocr.txt")
    print()
    print("2. Or install manually:")
    print("   pip install pandas numpy opencv-python paddleocr==2.7.0.3 paddlepaddle")
    
    print("\n💻 USAGE EXAMPLE")
    print("-" * 70)
    print()
    print("# Single scorecard processing")
    print("from scorecard_ocr import process_scorecard")
    print()
    print("df = process_scorecard('score_1.png')")
    print("print(df)")
    print()
    
    print("\n📊 EXPECTED OUTPUT")
    print("-" * 70)
    print()
    print("Input: score_1.png (golf scorecard image)")
    print()
    print("Extracted table:")
    print("┌──────────────┬────────┬────────┬────────┬──────────┐")
    print("│ Player       │ Hole 1 │ Hole 2 │ Hole 3 │ Total    │")
    print("├──────────────┼────────┼────────┼────────┼──────────┤")
    print("│ John Smith   │ 4      │ 5      │ --     │ 9        │")
    print("│ Jane Doe     │ 3      │ 4      │ 5      │ 12       │")
    print("│ Bob Johnson  │ 5      │ --     │ 4      │ 9        │")
    print("└──────────────┴────────┴────────┴────────┴──────────┘")
    print()
    print("Converted to DataFrame (-- becomes NaN):")
    print()
    print("        Player  Hole 1  Hole 2  Hole 3  Total")
    print("0   John Smith       4       5     NaN      9")
    print("1     Jane Doe       3       4     5.0     12")
    print("2  Bob Johnson       5     NaN     4.0      9")
    print()
    
    print("\n🔄 BATCH PROCESSING")
    print("-" * 70)
    print()
    print("# Process multiple scorecards")
    print("from scorecard_ocr import process_multiple_scorecards")
    print("import glob")
    print()
    print("# Find all scorecard images")
    print("image_files = glob.glob('score_*.png')")
    print()
    print("# Process and save to CSV")
    print("results = process_multiple_scorecards(")
    print("    image_files,")
    print("    output_dir='output_csv'")
    print(")")
    print()
    
    print("\n⚙️  CUSTOMIZATION")
    print("-" * 70)
    print()
    print("# Adjust row grouping threshold")
    print("df = process_scorecard('score_1.png', row_threshold=20)")
    print()
    print("# Enable GPU acceleration")
    print("from scorecard_ocr import ScorecardOCR")
    print("ocr = ScorecardOCR(use_gpu=True)")
    print("df = ocr.process_scorecard('score_1.png')")
    print()
    
    print("\n📁 EXPECTED FILE STRUCTURE")
    print("-" * 70)
    print(".")
    print("├── scorecard_ocr.py          # Main OCR script")
    print("├── requirements_ocr.txt      # Dependencies")
    print("├── README_OCR.md            # Documentation")
    print("├── demo_scorecard_ocr.py    # This demo file")
    print("├── scorecards/              # Input images directory")
    print("│   ├── score_1.png")
    print("│   ├── score_2.png")
    print("│   └── ...")
    print("└── output_csv/              # Output CSV files (auto-created)")
    print("    ├── score_1.csv")
    print("    ├── score_2.csv")
    print("    └── ...")
    print()
    
    print("\n🎯 NEXT STEPS")
    print("-" * 70)
    print("1. Place your scorecard images (score_1.png to score_8.png) in the")
    print("   current directory or a 'scorecards/' subdirectory")
    print()
    print("2. Install the required dependencies:")
    print("   pip install -r requirements_ocr.txt")
    print()
    print("3. Run the OCR processor:")
    print("   python scorecard_ocr.py")
    print()
    print("4. Check the 'output_csv/' directory for extracted data")
    print()
    
    print("\n" + "=" * 70)
    print("For detailed documentation, see README_OCR.md")
    print("=" * 70)
    print()


def test_with_dependencies():
    """
    Test the actual OCR functionality if dependencies are installed.
    """
    try:
        from scorecard_ocr import process_scorecard, ScorecardOCR
        import glob
        
        print("\n✅ Dependencies installed! Testing OCR functionality...\n")
        
        # Look for scorecard images
        scorecard_patterns = [
            'score_*.png',
            'scorecards/score_*.png',
            '*.png'
        ]
        
        image_files = []
        for pattern in scorecard_patterns:
            image_files.extend(glob.glob(pattern))
        
        if image_files:
            print(f"Found {len(image_files)} image(s) to process:\n")
            for img in image_files[:5]:  # Show first 5
                print(f"  - {img}")
            
            if len(image_files) > 5:
                print(f"  ... and {len(image_files) - 5} more")
            
            print("\nProcessing first image as a test...")
            test_image = image_files[0]
            
            df = process_scorecard(test_image)
            
            if not df.empty:
                print(f"\n✅ Success! Extracted data from {test_image}:")
                print(df.to_string())
            else:
                print(f"\n⚠️  No data extracted from {test_image}")
        else:
            print("⚠️  No image files found to process.")
            print("\nTo test with actual images:")
            print("  1. Add scorecard images (score_1.png, score_2.png, etc.)")
            print("  2. Run this script again")
        
    except ImportError as e:
        print("\n⚠️  Dependencies not yet installed.")
        print(f"   Error: {e}")
        print("\nPlease run:")
        print("   pip install -r requirements_ocr.txt")
        return False
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    # Always show the demo
    demo_without_dependencies()
    
    # Try to test with actual dependencies if available
    if '--test' in sys.argv:
        test_with_dependencies()
    else:
        print("\n💡 TIP: Run with --test flag to test with actual OCR:")
        print("   python demo_scorecard_ocr.py --test")
        print()
