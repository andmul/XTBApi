#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Golf Scorecard OCR Processor using Tesseract OCR
Processes golf scorecard images and converts to pandas DataFrames
"""

import os
import sys
import glob
import pandas as pd
import numpy as np
from PIL import Image
import pytesseract
import cv2

def clean_value(value):
    """
    Clean and convert values
    Converts '--' to NaN, tries to convert numbers
    """
    if not isinstance(value, str):
        return value
    
    value = value.strip()
    
    # Convert '--' and similar to NaN
    if value in ['--', '-', '—', '']:
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


def process_golf_scorecard(image_path):
    """
    Process a golf scorecard image and extract tabular data
    
    Args:
        image_path: Path to the scorecard image
        
    Returns:
        pandas DataFrame with extracted data
    """
    print(f"\nProcessing: {os.path.basename(image_path)}")
    print("=" * 70)
    
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return pd.DataFrame()
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Use Tesseract to do OCR
    # Get detailed data with bounding boxes
    data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
    
    # Extract text elements with positions
    elements = []
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        if text:  # Only include non-empty text
            conf = int(data['conf'][i])
            if conf > 30:  # Only include confident detections
                elements.append({
                    'text': text,
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'conf': conf
                })
    
    print(f"Detected {len(elements)} text elements")
    
    if not elements:
        print("No text detected!")
        return pd.DataFrame()
    
    # Group elements into rows based on vertical position
    # Sort by vertical position first
    elements_sorted_by_top = sorted(elements, key=lambda x: x['top'])
    
    # Group into rows (elements with similar 'top' values)
    rows = []
    current_row = [elements_sorted_by_top[0]]
    row_threshold = 15  # pixels tolerance for same row
    
    for elem in elements_sorted_by_top[1:]:
        if abs(elem['top'] - current_row[0]['top']) < row_threshold:
            current_row.append(elem)
        else:
            rows.append(current_row)
            current_row = [elem]
    
    if current_row:
        rows.append(current_row)
    
    print(f"Organized into {len(rows)} rows")
    
    # Sort each row by horizontal position
    table_data = []
    for row in rows:
        row_sorted = sorted(row, key=lambda x: x['left'])
        row_texts = [elem['text'] for elem in row_sorted]
        table_data.append(row_texts)
    
    # Display extracted structure
    print("\nExtracted table structure:")
    print("-" * 70)
    for i, row in enumerate(table_data):
        print(f"Row {i}: {row}")
    
    # Find maximum row length
    if table_data:
        max_cols = max(len(row) for row in table_data)
        
        # Pad rows to have equal length
        for row in table_data:
            while len(row) < max_cols:
                row.append('')
        
        # Create DataFrame
        # Try to use first row as headers if it looks like headers
        if len(table_data) > 1:
            df = pd.DataFrame(table_data[1:], columns=table_data[0])
        else:
            df = pd.DataFrame(table_data)
        
        # Clean values (convert '--' to NaN, convert numbers)
        for col in df.columns:
            df[col] = df[col].apply(clean_value)
        
        print("\nExtracted DataFrame:")
        print("=" * 70)
        print(df.to_string())
        print("=" * 70)
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        return df
    else:
        return pd.DataFrame()


def main():
    """Process all golf scorecards in the real_golf_scorecards directory"""
    print("=" * 70)
    print("GOLF SCORECARD OCR PROCESSOR")
    print("=" * 70)
    
    # Find scorecard images
    scorecard_dir = "real_golf_scorecards"
    if not os.path.exists(scorecard_dir):
        print(f"\nError: Directory '{scorecard_dir}' not found")
        print("Please ensure golf scorecard images are in the 'real_golf_scorecards' directory")
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
    output_dir = "scorecard_dataframes"
    os.makedirs(output_dir, exist_ok=True)
    
    for img_path in image_files:
        try:
            df = process_golf_scorecard(img_path)
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
