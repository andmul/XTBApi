#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Improved Golf Scorecard OCR Processor
Uses PaddleOCR with better table detection and structure recognition
"""

import os
import sys
import glob
import pandas as pd
import numpy as np
from PIL import Image
import cv2

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("Warning: PaddleOCR not available. Install with: pip install paddleocr paddlepaddle")


def clean_value(value):
    """
    Clean and convert values
    Converts '--' to NaN, tries to convert numbers
    """
    if not isinstance(value, str):
        return value
    
    value = value.strip()
    
    # Convert '--' and similar to NaN
    if value in ['--', '-', '—', '', '–']:
        return np.nan
    
    # Try to convert to numeric
    try:
        # Try integer first
        if '.' not in value:
            return int(value)
        else:
            return float(value)
    except ValueError:
        return value


def detect_table_structure(image_path):
    """
    Detect table structure using contours and lines
    Returns grid structure information
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to get binary image
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    # Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    # Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    detect_vertical = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    
    # Combine
    table_structure = cv2.add(detect_horizontal, detect_vertical)
    
    # Find contours to identify cells
    contours, _ = cv2.findContours(table_structure, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get bounding boxes for cells
    cells = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filter out very small or very large boxes
        if 20 < w < img.shape[1] * 0.3 and 15 < h < img.shape[0] * 0.2:
            cells.append({'x': x, 'y': y, 'w': w, 'h': h})
    
    return cells, img.shape


def process_golf_scorecard_improved(image_path):
    """
    Process a golf scorecard image with improved table detection
    
    Args:
        image_path: Path to the scorecard image
        
    Returns:
        pandas DataFrame with extracted data
    """
    print(f"\nProcessing: {os.path.basename(image_path)}")
    print("=" * 70)
    
    if not PADDLEOCR_AVAILABLE:
        print("ERROR: PaddleOCR is not installed!")
        print("Install with: pip install paddleocr paddlepaddle")
        return pd.DataFrame()
    
    # Initialize PaddleOCR
    # Note: use_angle_cls is deprecated in newer versions, use_textline_orientation is the new parameter
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
    except:
        # Fallback for newer versions
        ocr = PaddleOCR(lang='en', show_log=False)
    
    # Run OCR
    result = ocr.ocr(image_path, cls=True)
    
    if result is None or len(result) == 0 or result[0] is None:
        print("No text detected!")
        return pd.DataFrame()
    
    # Extract text with positions
    detections = []
    for line in result[0]:
        try:
            bbox = line[0]
            # Handle both old and new API formats
            if isinstance(line[1], tuple) and len(line[1]) >= 2:
                text = line[1][0]
                conf = line[1][1]
            elif isinstance(line[1], str):
                # Newer API format might return string directly
                text = line[1]
                conf = 0.9  # Default confidence
            else:
                continue
        except (IndexError, TypeError) as e:
            print(f"Warning: Could not parse detection: {e}")
            continue
        
        # Calculate center and bounds
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        
        detections.append({
            'text': text,
            'x_min': x_min,
            'x_max': x_max,
            'y_min': y_min,
            'y_max': y_max,
            'x_center': x_center,
            'y_center': y_center,
            'conf': conf
        })
    
    print(f"Detected {len(detections)} text elements")
    
    if not detections:
        print("No text detected!")
        return pd.DataFrame()
    
    # Sort by vertical position first
    detections_sorted = sorted(detections, key=lambda x: x['y_center'])
    
    # Group into rows using adaptive threshold
    rows = []
    current_row = [detections_sorted[0]]
    
    # Calculate average text height for threshold
    heights = [d['y_max'] - d['y_min'] for d in detections_sorted]
    avg_height = np.mean(heights)
    row_threshold = avg_height * 0.5  # Use half the average height as threshold
    
    print(f"Using row threshold: {row_threshold:.1f} pixels")
    
    for detection in detections_sorted[1:]:
        # Check if this detection is on the same row as the current row
        current_row_y = np.mean([d['y_center'] for d in current_row])
        
        if abs(detection['y_center'] - current_row_y) < row_threshold:
            current_row.append(detection)
        else:
            rows.append(current_row)
            current_row = [detection]
    
    if current_row:
        rows.append(current_row)
    
    print(f"Organized into {len(rows)} rows")
    
    # Sort each row by horizontal position (left to right)
    table_data = []
    for i, row in enumerate(rows):
        row_sorted = sorted(row, key=lambda x: x['x_center'])
        row_texts = [det['text'] for det in row_sorted]
        table_data.append(row_texts)
        print(f"Row {i}: {row_texts}")
    
    if not table_data:
        return pd.DataFrame()
    
    # Find maximum number of columns
    max_cols = max(len(row) for row in table_data)
    
    # Pad rows to have equal length
    for row in table_data:
        while len(row) < max_cols:
            row.append('')
    
    # Try to identify header row (usually first row or row with most text)
    # Create DataFrame
    if len(table_data) > 1:
        # Use first row as headers
        df = pd.DataFrame(table_data[1:], columns=table_data[0])
    else:
        df = pd.DataFrame(table_data)
    
    # Clean values
    for col in df.columns:
        df[col] = df[col].apply(clean_value)
    
    print("\nExtracted DataFrame:")
    print("=" * 70)
    print(df.to_string())
    print("=" * 70)
    print(f"Shape: {df.shape}")
    
    return df


def main():
    """Process all golf scorecards in the golfsc directory"""
    print("=" * 70)
    print("IMPROVED GOLF SCORECARD OCR PROCESSOR (PaddleOCR)")
    print("=" * 70)
    
    if not PADDLEOCR_AVAILABLE:
        print("\nERROR: PaddleOCR is not installed!")
        print("Please install with: pip install paddleocr paddlepaddle")
        return
    
    # Find scorecard images
    scorecard_dir = "golfsc"
    if not os.path.exists(scorecard_dir):
        print(f"\nError: Directory '{scorecard_dir}' not found")
        print("Please ensure golf scorecard images are in the 'golfsc' directory")
        return
    
    pattern = os.path.join(scorecard_dir, "*_scorecard_*.png")
    image_files = sorted(glob.glob(pattern))
    
    if not image_files:
        print(f"\nNo scorecard images found in '{scorecard_dir}'")
        return
    
    print(f"\nFound {len(image_files)} scorecard images")
    print("=" * 70)
    
    # Process each scorecard
    results = {}
    output_dir = "scorecard_dataframes_improved"
    os.makedirs(output_dir, exist_ok=True)
    
    for img_path in image_files:
        try:
            df = process_golf_scorecard_improved(img_path)
            results[img_path] = df
            
            # Save to CSV
            if not df.empty:
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                csv_path = os.path.join(output_dir, f"{base_name}.csv")
                df.to_csv(csv_path, index=False)
                print(f"\n✅ Saved to: {csv_path}\n")
            else:
                print(f"\n⚠️  No data extracted from {os.path.basename(img_path)}\n")
                
        except Exception as e:
            print(f"\n❌ Error processing {os.path.basename(img_path)}: {e}\n")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)
    successful = sum(1 for df in results.values() if not df.empty)
    print(f"Successfully processed: {successful}/{len(image_files)} scorecards")
    print(f"Output saved to: {output_dir}/")
    print("=" * 70)


if __name__ == "__main__":
    main()
