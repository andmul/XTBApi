#!/usr/bin/env python3
"""
Example: How to Fix Missing First Column in OCR Results

This script demonstrates how to use the new parameters to fix issues
where the first column is fractionally missing from OCR output.
"""

import os
import sys

def example_basic():
    """Basic usage with default parameters"""
    print("=" * 70)
    print("Example 1: Basic Usage (Default Parameters)")
    print("=" * 70)
    print()
    
    try:
        from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3
        
        # This uses default parameters: x_margin_left=0, row_threshold_factor=0.6
        image_path = 'golfsc/example_scorecard.png'
        
        if os.path.exists(image_path):
            df = process_golf_scorecard_paddleocr3(image_path)
            
            if df is not None:
                print("\nExtracted DataFrame:")
                print(df)
            else:
                print("\nNo data extracted. Try adjusting parameters.")
        else:
            print(f"Image not found: {image_path}")
            print("This is just an example. Replace with your actual image path.")
    
    except ImportError:
        print("ERROR: process_scorecards_paddleocr3.py not found in current directory")
        print("Make sure you're running this from the correct directory.")
    except Exception as e:
        print(f"ERROR: {e}")


def example_fix_missing_first_column():
    """Fix missing first column by adjusting x_margin_left"""
    print("\n" + "=" * 70)
    print("Example 2: Fix Missing First Column")
    print("=" * 70)
    print()
    
    try:
        from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3
        
        image_path = 'golfsc/example_scorecard.png'
        
        if os.path.exists(image_path):
            # Try with x_margin_left to exclude left edge artifacts
            print("Processing with x_margin_left=10...")
            df = process_golf_scorecard_paddleocr3(
                image_path,
                x_margin_left=10  # Skip leftmost 10 pixels
            )
            
            if df is not None:
                print("\nExtracted DataFrame:")
                print(df)
                print("\n✓ Check if first column is now present!")
            else:
                print("\nNo data extracted.")
                print("Try increasing x_margin_left to 15 or 20.")
        else:
            print(f"Image not found: {image_path}")
            print("Replace with your actual image path in the code.")
    
    except ImportError:
        print("ERROR: process_scorecards_paddleocr3.py not found")
    except Exception as e:
        print(f"ERROR: {e}")


def example_fix_row_alignment():
    """Fix row alignment issues with row_threshold_factor"""
    print("\n" + "=" * 70)
    print("Example 3: Fix Row Alignment Issues")
    print("=" * 70)
    print()
    
    try:
        from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3
        
        image_path = 'golfsc/example_scorecard.png'
        
        if os.path.exists(image_path):
            # Try with looser row grouping
            print("Processing with row_threshold_factor=0.7 (looser grouping)...")
            df = process_golf_scorecard_paddleocr3(
                image_path,
                row_threshold_factor=0.7  # More lenient row grouping
            )
            
            if df is not None:
                print("\nExtracted DataFrame:")
                print(df)
                print("\n✓ Check if first column items are now on correct rows!")
            else:
                print("\nNo data extracted.")
        else:
            print(f"Image not found: {image_path}")
    
    except ImportError:
        print("ERROR: process_scorecards_paddleocr3.py not found")
    except Exception as e:
        print(f"ERROR: {e}")


def example_combined_fix():
    """Combine both parameters for best results"""
    print("\n" + "=" * 70)
    print("Example 4: Combined Fix (Both Parameters)")
    print("=" * 70)
    print()
    
    try:
        from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3
        
        image_path = 'golfsc/example_scorecard.png'
        
        if os.path.exists(image_path):
            print("Processing with both parameters adjusted...")
            df = process_golf_scorecard_paddleocr3(
                image_path,
                x_margin_left=10,         # Skip left edge artifacts
                row_threshold_factor=0.7  # Looser row grouping
            )
            
            if df is not None:
                print("\nExtracted DataFrame:")
                print(df)
                print("\n✓ This combination often works best!")
                
                # Save to CSV
                output_file = 'output_example.csv'
                df.to_csv(output_file, index=False)
                print(f"\n✓ Saved to: {output_file}")
            else:
                print("\nNo data extracted.")
        else:
            print(f"Image not found: {image_path}")
    
    except ImportError:
        print("ERROR: process_scorecards_paddleocr3.py not found")
    except Exception as e:
        print(f"ERROR: {e}")


def example_batch_processing():
    """Process multiple scorecards with custom parameters"""
    print("\n" + "=" * 70)
    print("Example 5: Batch Processing with Custom Parameters")
    print("=" * 70)
    print()
    
    try:
        from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3
        import glob
        from pathlib import Path
        
        # Find all scorecard images
        image_dir = 'golfsc'
        image_files = glob.glob(os.path.join(image_dir, '*.png'))
        
        if not image_files:
            print(f"No images found in '{image_dir}/' directory")
            print("Add your scorecard images to the 'golfsc' directory first.")
            return
        
        print(f"Found {len(image_files)} scorecard images")
        print()
        
        # Process each with custom parameters
        output_dir = 'scorecard_output_fixed'
        os.makedirs(output_dir, exist_ok=True)
        
        for i, img_path in enumerate(image_files, 1):
            print(f"[{i}/{len(image_files)}] Processing: {os.path.basename(img_path)}")
            
            try:
                df = process_golf_scorecard_paddleocr3(
                    img_path,
                    x_margin_left=10,         # Adjust based on your needs
                    row_threshold_factor=0.6  # Adjust based on your needs
                )
                
                if df is not None and len(df) > 0:
                    # Save to CSV
                    output_file = os.path.join(
                        output_dir,
                        f"{Path(img_path).stem}.csv"
                    )
                    df.to_csv(output_file, index=False)
                    print(f"  ✓ Saved: {output_file}")
                else:
                    print(f"  ⚠️  No data extracted")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            print()
        
        print("=" * 70)
        print(f"Batch processing complete! Check '{output_dir}/' directory")
        print("=" * 70)
    
    except ImportError:
        print("ERROR: process_scorecards_paddleocr3.py not found")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    """Run all examples"""
    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║       Examples: Fixing Missing First Column in OCR Results           ║
╚═══════════════════════════════════════════════════════════════════════╝

These examples demonstrate how to use the new parameters to fix issues
where the first column is fractionally missing from OCR output.

Parameters:
  • x_margin_left: Pixels to skip from left edge (try 10, 15, 20)
  • row_threshold_factor: Row grouping strictness (try 0.5 to 0.8)

    """)
    
    # Check if module is available
    try:
        from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3
    except ImportError:
        print("=" * 70)
        print("ERROR: process_scorecards_paddleocr3.py not found!")
        print("=" * 70)
        print()
        print("Make sure you have the file in the current directory.")
        print("You can find it in the repository.")
        sys.exit(1)
    
    # Run examples
    print("\nRunning examples...\n")
    
    # Note: These examples won't actually process images unless
    # you have scorecard images in the golfsc/ directory
    
    print("NOTE: These are code examples showing different parameter combinations.")
    print("To actually run them, add your scorecard images to 'golfsc/' directory.")
    print()
    
    # Show example usage patterns
    print("=" * 70)
    print("Usage Patterns")
    print("=" * 70)
    print()
    
    print("1. Default (no parameters):")
    print("   df = process_golf_scorecard_paddleocr3('image.png')")
    print()
    
    print("2. Fix missing first column:")
    print("   df = process_golf_scorecard_paddleocr3('image.png', x_margin_left=10)")
    print()
    
    print("3. Fix row alignment:")
    print("   df = process_golf_scorecard_paddleocr3('image.png', row_threshold_factor=0.7)")
    print()
    
    print("4. Combined fix:")
    print("   df = process_golf_scorecard_paddleocr3('image.png', x_margin_left=10, row_threshold_factor=0.7)")
    print()
    
    print("=" * 70)
    print("To run actual processing:")
    print("=" * 70)
    print("1. Add your scorecard images to 'golfsc/' directory")
    print("2. Run: python process_scorecards_paddleocr3.py")
    print("3. Or use the examples in this file as templates")
    print()


if __name__ == "__main__":
    main()
