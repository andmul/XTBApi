#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script to understand PaddleOCR 3.0+ output format
"""

import os
import glob

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("ERROR: PaddleOCR is not installed!")
    exit(1)

def debug_paddleocr(image_path):
    """Debug PaddleOCR to understand its output format"""
    print(f"\n{'='*70}")
    print(f"DEBUGGING: {os.path.basename(image_path)}")
    print(f"{'='*70}")
    
    # Initialize OCR
    print("\n1. Initializing PaddleOCR...")
    ocr = PaddleOCR(lang='en')
    print("   ✓ Initialization successful")
    
    # Run OCR
    print(f"\n2. Running OCR on image...")
    try:
        result = ocr.predict(image_path)
        print(f"   ✓ OCR completed")
        print(f"\n3. Result type: {type(result)}")
        print(f"   Result length: {len(result) if result else 0}")
        
        if result:
            print(f"\n4. First level structure:")
            for i, item in enumerate(result[:3]):  # Show first 3 items
                print(f"   Item {i}: type={type(item)}, len={len(item) if hasattr(item, '__len__') else 'N/A'}")
                if hasattr(item, '__len__') and len(item) > 0:
                    print(f"            First element: {item[0] if isinstance(item, (list, tuple)) else item}")
            
            print(f"\n5. Full result structure (first 2 detections):")
            for i, detection in enumerate(result[:2]):
                print(f"   Detection {i}: {detection}")
        else:
            print("   ⚠️  Result is None or empty")
            
    except AttributeError as e:
        print(f"   ✗ predict() method not available: {e}")
        print(f"\n   Trying ocr() method instead...")
        try:
            result = ocr.ocr(image_path)
            print(f"   ✓ ocr() completed")
            print(f"\n3. Result type: {type(result)}")
            print(f"   Result length: {len(result) if result else 0}")
            
            if result and len(result) > 0:
                print(f"\n4. result[0] type: {type(result[0])}")
                print(f"   result[0] length: {len(result[0]) if result[0] else 0}")
                
                if result[0] and len(result[0]) > 0:
                    print(f"\n5. First detection structure:")
                    first_det = result[0][0]
                    print(f"   Type: {type(first_det)}")
                    print(f"   Length: {len(first_det) if hasattr(first_det, '__len__') else 'N/A'}")
                    print(f"   Content: {first_det}")
                    
                    print(f"\n6. Full result[0] (first 2 detections):")
                    for i, detection in enumerate(result[0][:2]):
                        print(f"   Detection {i}: {detection}")
        except Exception as e2:
            print(f"   ✗ ocr() method also failed: {e2}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Debug first scorecard found"""
    print("="*70)
    print("PaddleOCR 3.0+ DEBUG SCRIPT")
    print("="*70)
    
    # Find scorecard images
    scorecard_dir = "golfsc"
    if not os.path.exists(scorecard_dir):
        print(f"\nError: Directory '{scorecard_dir}' not found")
        return
    
    pattern = os.path.join(scorecard_dir, "*_scorecard_*.png")
    image_files = sorted(glob.glob(pattern))
    
    if not image_files:
        print(f"\nNo scorecard images found in '{scorecard_dir}'")
        return
    
    print(f"\nFound {len(image_files)} scorecard images")
    print(f"Will debug first image: {os.path.basename(image_files[0])}")
    
    # Debug first image
    debug_paddleocr(image_files[0])
    
    print("\n" + "="*70)
    print("DEBUG COMPLETE")
    print("="*70)
    print("\nPlease share the output above so we can fix the parsing logic!")

if __name__ == "__main__":
    main()
