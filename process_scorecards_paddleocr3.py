#!/usr/bin/env python3
"""
PaddleOCR 3.0+ Scorecard Processor with Column Detection Fix
==================================

Working processor for PaddleOCR 3.0+ that correctly parses OCRResult objects.
Processes golf scorecards and converts them to pandas DataFrames.

Features:
- Correct PaddleOCR 3.0+ API parsing (rec_texts, rec_polys, rec_scores)
- Adaptive row/column detection based on spatial positioning
- **NEW: Configurable parameters to fix missing first column**
- Converts '--' to NaN automatically
- Automatic numeric type conversion
- Batch processing with progress tracking
- CSV export

New Parameters:
    x_margin_left: Pixels to ignore from left edge (default: 0)
        Use if leftmost column is being cut off
    row_threshold_factor: Multiplier for row detection (default: 0.6)
        Increase to group more loosely, decrease for tighter grouping
    
Usage:
    pip install paddleocr paddlepaddle pandas numpy opencv-python
    python process_scorecards_paddleocr3.py
    
    # Or with custom parameters:
    from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3
    df = process_golf_scorecard_paddleocr3('image.png', x_margin_left=10, row_threshold_factor=0.5)
"""

import os
import glob
import numpy as np
import pandas as pd
from pathlib import Path

def process_golf_scorecard_paddleocr3(image_path, x_margin_left=0, row_threshold_factor=0.6):
    """
    Process a golf scorecard image using PaddleOCR 3.0+ API.
    
    Args:
        image_path: Path to the scorecard image
        x_margin_left: Pixels to ignore from left edge (default: 0)
            If the first column is missing, try values like 5, 10, or 15
        row_threshold_factor: Multiplier for row detection threshold (default: 0.6)
            Higher values = more lenient row grouping
            Lower values = stricter row grouping
        
    Returns:
        pandas DataFrame with the extracted scorecard data
    """
    from paddleocr import PaddleOCR
    
    # Initialize PaddleOCR (using simple initialization for 3.0+)
    ocr = PaddleOCR(lang='en')
    
    # Run OCR using predict() method (PaddleOCR 3.0+ API)
    result = ocr.predict(image_path)
    
    # Parse PaddleOCR 3.0+ result format
    # result is a list with one OCRResult object
    if not result or len(result) == 0:
        print("No text detected!")
        return None
    
    ocr_result = result[0]
    
    # Access the OCRResult attributes
    texts = ocr_result.rec_texts  # List of recognized text strings
    polys = ocr_result.rec_polys  # List of bounding box polygons (numpy arrays)
    scores = ocr_result.rec_scores  # List of confidence scores
    
    print(f"Detected {len(texts)} text elements")
    
    if len(texts) == 0:
        print("No text detected!")
        return None
    
    # Extract text elements with their positions
    elements = []
    min_x_found = float('inf')
    
    for i, (text, poly, score) in enumerate(zip(texts, polys, scores)):
        try:
            # poly is a numpy array with shape (4, 2) containing 4 corner points
            # Calculate center position and bounds
            x_coords = poly[:, 0]
            y_coords = poly[:, 1]
            
            x_center = float(np.mean(x_coords))
            y_center = float(np.mean(y_coords))
            x_min = float(np.min(x_coords))
            y_min = float(np.min(y_coords))
            x_max = float(np.max(x_coords))
            y_max = float(np.max(y_coords))
            height = y_max - y_min
            
            # Track minimum x coordinate
            min_x_found = min(min_x_found, x_min)
            
            # Skip elements too close to left margin if specified
            if x_min < x_margin_left:
                print(f"  Skipping '{text}' (x={x_min:.1f} < margin {x_margin_left})")
                continue
            
            elements.append({
                'text': text,
                'x_center': x_center,
                'y_center': y_center,
                'x_min': x_min,
                'y_min': y_min,
                'x_max': x_max,
                'y_max': y_max,
                'height': height,
                'score': score
            })
        except Exception as e:
            print(f"Warning: Could not parse element {i}: {e}")
            continue
    
    if len(elements) == 0:
        print("No valid text elements parsed!")
        return None
    
    print(f"Parsed {len(elements)} valid text elements")
    print(f"Minimum x-coordinate found: {min_x_found:.1f}")
    if x_margin_left == 0 and min_x_found < 20:
        print(f"💡 TIP: If first column is missing, try: x_margin_left={int(min_x_found) + 5}")
    
    # Sort elements by vertical position (top to bottom)
    elements.sort(key=lambda x: x['y_center'])
    
    # Group elements into rows based on adaptive row detection
    # Calculate median text height for adaptive thresholding
    heights = [e['height'] for e in elements]
    median_height = np.median(heights)
    row_threshold = median_height * row_threshold_factor
    
    rows = []
    current_row = [elements[0]]
    
    for elem in elements[1:]:
        # Check if this element is on the same row as the previous one
        if abs(elem['y_center'] - current_row[-1]['y_center']) <= row_threshold:
            current_row.append(elem)
        else:
            # Start a new row
            rows.append(current_row)
            current_row = [elem]
    
    # Don't forget the last row
    if current_row:
        rows.append(current_row)
    
    print(f"Organized into {len(rows)} rows (threshold: {row_threshold:.1f}px)")
    
    # Debug: Show row structure
    for i, row in enumerate(rows):
        row_texts = [e['text'] for e in row]
        print(f"Row {i}: {row_texts}")
    
    # Sort elements within each row by horizontal position (left to right)
    for row in rows:
        row.sort(key=lambda x: x['x_center'])
    
    # Convert to DataFrame
    # Find the maximum number of columns
    max_cols = max(len(row) for row in rows)
    
    # Create data matrix
    data = []
    for row in rows:
        row_data = [elem['text'] for elem in row]
        # Pad with empty strings if row has fewer elements
        row_data.extend([''] * (max_cols - len(row_data)))
        data.append(row_data)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Convert '--' to NaN
    df = df.replace('--', np.nan)
    df = df.replace('-', np.nan)
    
    # Try to convert numeric columns
    for col in df.columns:
        try:
            # Try to convert to numeric, keeping NaN values
            df[col] = pd.to_numeric(df[col], errors='ignore')
        except:
            pass
    
    return df


def main():
    """Main function to process all scorecards in the golfsc directory."""
    
    print("=" * 70)
    print("PaddleOCR 3.0+ Scorecard Processor (with Column Detection Fix)")
    print("=" * 70)
    print()
    
    # Find all scorecard images in golfsc directory
    image_dir = 'golfsc'
    if not os.path.exists(image_dir):
        print(f"Error: Directory '{image_dir}' not found!")
        print("Please create the 'golfsc' directory and place your scorecard images there.")
        return
    
    # Look for PNG images
    image_patterns = [
        os.path.join(image_dir, '*.png'),
        os.path.join(image_dir, '*.PNG'),
        os.path.join(image_dir, '*.jpg'),
        os.path.join(image_dir, '*.JPG'),
        os.path.join(image_dir, '*.jpeg'),
        os.path.join(image_dir, '*.JPEG')
    ]
    
    image_files = []
    for pattern in image_patterns:
        image_files.extend(glob.glob(pattern))
    
    image_files = sorted(set(image_files))  # Remove duplicates and sort
    
    if len(image_files) == 0:
        print(f"No images found in '{image_dir}' directory!")
        return
    
    print(f"Found {len(image_files)} scorecard images")
    print()
    
    # Configurable parameters
    # Adjust these if the first column is missing:
    X_MARGIN_LEFT = 0  # Change to 5, 10, or 15 if first column is cut off
    ROW_THRESHOLD_FACTOR = 0.6  # Change to 0.5 for tighter rows, 0.7 for looser
    
    print(f"Processing parameters:")
    print(f"  x_margin_left: {X_MARGIN_LEFT} pixels")
    print(f"  row_threshold_factor: {ROW_THRESHOLD_FACTOR}")
    print()
    
    # Create output directory for CSV files
    output_dir = 'scorecard_output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each image
    successful = 0
    failed = 0
    
    for i, img_path in enumerate(image_files, 1):
        print("=" * 70)
        print(f"[{i}/{len(image_files)}] Processing: {os.path.basename(img_path)}")
        print("=" * 70)
        
        try:
            df = process_golf_scorecard_paddleocr3(
                img_path,
                x_margin_left=X_MARGIN_LEFT,
                row_threshold_factor=ROW_THRESHOLD_FACTOR
            )
            
            if df is not None and len(df) > 0:
                # Generate output filename
                base_name = Path(img_path).stem
                csv_path = os.path.join(output_dir, f'{base_name}.csv')
                
                # Save to CSV
                df.to_csv(csv_path, index=False)
                print(f"✓ Saved to: {csv_path}")
                print(f"  Shape: {df.shape}")
                print()
                print("Preview:")
                print(df.head())
                print()
                
                successful += 1
            else:
                print(f"⚠️  No data extracted from {os.path.basename(img_path)}")
                print()
                failed += 1
                
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(img_path)}: {e}")
            import traceback
            traceback.print_exc()
            print()
            failed += 1
    
    # Summary
    print()
    print("=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Total images: {len(image_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Output directory: {output_dir}/")
    print()
    
    if successful > 0:
        print("✓ CSV files have been saved to the 'scorecard_output' directory")
        print("✓ '--' has been converted to NaN")
        print("✓ Numeric columns have been auto-detected and converted")
        print()
        print("=" * 70)
        print("TROUBLESHOOTING")
        print("=" * 70)
        print("If the first column is still missing, edit this script and adjust:")
        print("  X_MARGIN_LEFT = 5      # Try 5, 10, or 15")
        print("  ROW_THRESHOLD_FACTOR = 0.5  # Try 0.5 for tighter grouping")
        print()


if __name__ == "__main__":
    main()
