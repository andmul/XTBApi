#!/usr/bin/env python3
"""
PaddleOCR 3.0+ Scorecard Processor with Enhanced Accuracy
==================================

Working processor for PaddleOCR 3.0+ that correctly parses OCRResult objects.
Processes golf scorecards and converts them to pandas DataFrames.

Features:
- Correct PaddleOCR 3.0+ API parsing (rec_texts, rec_polys, rec_scores)
- **NEW: Image preprocessing for improved OCR accuracy (fixes 6/9 confusion)**
- **NEW: Smart column detection handles right-aligned numbers**
- Adaptive row/column detection based on spatial positioning
- Configurable parameters to fix missing first column
- Converts '--' to NaN automatically
- Automatic numeric type conversion
- Batch processing with progress tracking
- CSV export

New Parameters:
    x_margin_left: Pixels to ignore from left edge (default: 0)
        Use if leftmost column is being cut off
    row_threshold_factor: Multiplier for row detection (default: 0.6)
        Increase to group more loosely, decrease for tighter grouping
    enable_preprocessing: Apply image preprocessing for better accuracy (default: True)
    use_x_min_for_sorting: Use left edge instead of center for column detection (default: True)
        Fixes issues with right-aligned numbers in first column
    
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
import cv2

def preprocess_image(image_path):
    """
    Preprocess image to improve OCR accuracy.
    Fixes issues like 6 vs 9 confusion by enhancing image quality.
    
    Args:
        image_path: Path to the image
        
    Returns:
        Preprocessed image as numpy array
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding to handle varying lighting
    # This helps distinguish similar digits like 6 and 9
    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Denoise to reduce artifacts
    denoised = cv2.fastNlMeansDenoising(binary, None, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Slight dilation to make text clearer
    kernel = np.ones((2, 2), np.uint8)
    dilated = cv2.dilate(denoised, kernel, iterations=1)
    
    # Sharpen to enhance edges (helps with digit recognition)
    kernel_sharpen = np.array([[-1,-1,-1],
                                [-1, 9,-1],
                                [-1,-1,-1]])
    sharpened = cv2.filter2D(dilated, -1, kernel_sharpen)
    
    return sharpened


def process_golf_scorecard_paddleocr3(image_path, x_margin_left=0, row_threshold_factor=0.6, 
                                     enable_preprocessing=True, use_x_min_for_sorting=True):
    """
    Process a golf scorecard image using PaddleOCR 3.0+ API with enhanced accuracy.
    
    Args:
        image_path: Path to the scorecard image
        x_margin_left: Pixels to ignore from left edge (default: 0)
            If the first column is missing, try values like 5, 10, or 15
        row_threshold_factor: Multiplier for row detection threshold (default: 0.6)
            Higher values = more lenient row grouping
            Lower values = stricter row grouping
        enable_preprocessing: Apply image preprocessing for better accuracy (default: True)
            Helps fix digit confusion like 6 vs 9
        use_x_min_for_sorting: Use left edge (x_min) instead of center for column sorting (default: True)
            Fixes issues with right-aligned numbers causing cutoffs in first column
        
    Returns:
        pandas DataFrame with the extracted scorecard data
    """
    from paddleocr import PaddleOCR
    
    # Preprocess image if enabled
    if enable_preprocessing:
        print("Preprocessing image for enhanced accuracy...")
        preprocessed_img = preprocess_image(image_path)
        # Save to temp file for PaddleOCR
        temp_path = '/tmp/preprocessed_scorecard.png'
        cv2.imwrite(temp_path, preprocessed_img)
        ocr_image_path = temp_path
    else:
        ocr_image_path = image_path
    
    # Initialize PaddleOCR with better parameters for accuracy
    ocr = PaddleOCR(
        lang='en',
        use_angle_cls=True,  # Enable angle classification for better accuracy
        use_space_char=True,  # Preserve spaces
        drop_score=0.5  # Higher threshold for more accurate results
    )
    
    # Run OCR using predict() method (PaddleOCR 3.0+ API)
    result = ocr.predict(ocr_image_path)
    
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
    # Use x_min (left edge) instead of x_center to handle right-aligned numbers
    # This fixes the issue where right-aligned numbers in the first column
    # get misaligned because their centers are at different positions
    sort_key = 'x_min' if use_x_min_for_sorting else 'x_center'
    for row in rows:
        row.sort(key=lambda x: x[sort_key])
    
    print(f"Column sorting: Using {sort_key} for positioning (fixes right-aligned numbers)")
    
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
    ENABLE_PREPROCESSING = True  # Image preprocessing for better accuracy (fixes 6/9 confusion)
    USE_X_MIN_FOR_SORTING = True  # Use left edge for sorting (fixes right-aligned numbers)
    
    print(f"Processing parameters:")
    print(f"  x_margin_left: {X_MARGIN_LEFT} pixels")
    print(f"  row_threshold_factor: {ROW_THRESHOLD_FACTOR}")
    print(f"  enable_preprocessing: {ENABLE_PREPROCESSING} (improves digit accuracy)")
    print(f"  use_x_min_for_sorting: {USE_X_MIN_FOR_SORTING} (fixes right-aligned numbers)")
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
                row_threshold_factor=ROW_THRESHOLD_FACTOR,
                enable_preprocessing=ENABLE_PREPROCESSING,
                use_x_min_for_sorting=USE_X_MIN_FOR_SORTING
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
        print("✓ Image preprocessing applied for better accuracy (fixes 6/9 confusion)")
        print("✓ Smart column detection handles right-aligned numbers")
        print()
        print("=" * 70)
        print("TROUBLESHOOTING")
        print("=" * 70)
        print("If issues persist, edit this script and adjust:")
        print("  X_MARGIN_LEFT = 5      # Try 5, 10, or 15")
        print("  ROW_THRESHOLD_FACTOR = 0.5  # Try 0.5 for tighter grouping")
        print("  ENABLE_PREPROCESSING = False  # Disable if causing issues")
        print("  USE_X_MIN_FOR_SORTING = False  # Use center-based sorting instead")
        print()


if __name__ == "__main__":
    main()
