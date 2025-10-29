#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golf Scorecard OCR Processor using EasyOCR
Alternative high-accuracy OCR solution
"""

import os
import sys
import glob
import pandas as pd
import numpy as np

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("Error: EasyOCR not installed. Install with: pip install easyocr")


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


def process_golf_scorecard_easyocr(image_path):
    """
    Process a golf scorecard image with EasyOCR
    
    Args:
        image_path: Path to the scorecard image
        
    Returns:
        pandas DataFrame with extracted data
    """
    print(f"\nProcessing: {os.path.basename(image_path)}")
    print("=" * 70)
    
    if not EASYOCR_AVAILABLE:
        print("ERROR: EasyOCR is not installed!")
        print("Install with: pip install easyocr")
        return pd.DataFrame()
    
    # Initialize EasyOCR reader (only once is recommended, but we do it per image for simplicity)
    print("Initializing EasyOCR...")
    reader = easyocr.Reader(['en'], gpu=False)
    
    # Run OCR
    print("Running OCR...")
    result = reader.readtext(image_path)
    
    if not result:
        print("No text detected!")
        return pd.DataFrame()
    
    # Extract text with positions
    detections = []
    for detection in result:
        bbox, text, conf = detection
        
        # Calculate center and bounds
        x_coords = [point[0] for point in bbox]
        y_coords = [point[1] for point in bbox]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        
        detections.append({
            'text': text,
            'x_center': x_center,
            'y_center': y_center,
            'y_min': y_min,
            'y_max': y_max,
            'conf': conf
        })
    
    print(f"Detected {len(detections)} text elements")
    
    # Sort by vertical position
    detections_sorted = sorted(detections, key=lambda x: x['y_center'])
    
    # Group into rows
    rows = []
    current_row = [detections_sorted[0]]
    
    # Calculate average text height for threshold
    heights = [d['y_max'] - d['y_min'] for d in detections_sorted]
    avg_height = np.mean(heights)
    row_threshold = avg_height * 0.5
    
    print(f"Using row threshold: {row_threshold:.1f} pixels")
    
    for detection in detections_sorted[1:]:
        current_row_y = np.mean([d['y_center'] for d in current_row])
        
        if abs(detection['y_center'] - current_row_y) < row_threshold:
            current_row.append(detection)
        else:
            rows.append(current_row)
            current_row = [detection]
    
    if current_row:
        rows.append(current_row)
    
    print(f"Organized into {len(rows)} rows")
    
    # Sort each row by horizontal position
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
    
    # Create DataFrame
    if len(table_data) > 1:
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
    """Process all golf scorecards"""
    print("=" * 70)
    print("GOLF SCORECARD OCR PROCESSOR (EasyOCR)")
    print("=" * 70)
    
    if not EASYOCR_AVAILABLE:
        print("\nERROR: EasyOCR is not installed!")
        print("Please install with: pip install easyocr")
        return
    
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
    print("=" * 70)
    
    # Process each scorecard
    results = {}
    output_dir = "scorecard_dataframes_easyocr"
    os.makedirs(output_dir, exist_ok=True)
    
    for img_path in image_files:
        try:
            df = process_golf_scorecard_easyocr(img_path)
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
