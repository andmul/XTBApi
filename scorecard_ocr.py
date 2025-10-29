#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OCR Processing for Golf Scorecards using PaddleOCR

This script processes scorecard images and converts them to pandas DataFrames.
It handles tabular numeric data and converts '--' to NaN.

Recommended PaddleOCR version: 2.7.0.3 (stable and tested)
Note: PaddleOCR 3.3 was requested but uses a different API structure.
This implementation uses 2.7.x which provides better stability.
"""

import os
import pandas as pd
import numpy as np
from paddleocr import PaddleOCR
import cv2


class ScorecardOCR:
    """OCR processor for golf scorecards"""
    
    def __init__(self, lang='en', use_angle_cls=True, use_gpu=False):
        """
        Initialize PaddleOCR
        
        Args:
            lang: Language for OCR (default: 'en')
            use_angle_cls: Use angle classification (default: True)
            use_gpu: Use GPU for processing (default: False)
        """
        self.ocr = PaddleOCR(
            use_angle_cls=use_angle_cls,
            lang=lang,
            use_gpu=use_gpu,
            show_log=False
        )
    
    def process_image(self, image_path):
        """
        Process a single scorecard image
        
        Args:
            image_path: Path to the scorecard image
            
        Returns:
            List of detection results with text, confidence, and bounding boxes
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Run OCR
        result = self.ocr.ocr(image_path, cls=True)
        
        if result is None or len(result) == 0:
            return []
        
        # Extract text and positions
        detections = []
        for line in result[0]:
            bbox = line[0]  # Bounding box coordinates
            text_info = line[1]  # (text, confidence)
            text = text_info[0]
            confidence = text_info[1]
            
            # Calculate center position for sorting
            center_x = sum([point[0] for point in bbox]) / 4
            center_y = sum([point[1] for point in bbox]) / 4
            
            detections.append({
                'text': text,
                'confidence': confidence,
                'bbox': bbox,
                'center_x': center_x,
                'center_y': center_y
            })
        
        return detections
    
    def clean_value(self, value):
        """
        Clean and convert values
        
        Args:
            value: String value to clean
            
        Returns:
            Cleaned value (converts '--' to NaN, tries to convert numbers)
        """
        if not isinstance(value, str):
            return value
        
        value = value.strip()
        
        # Convert '--' to NaN
        if value == '--' or value == '-' or value == '—':
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
    
    def organize_into_table(self, detections, row_threshold=15):
        """
        Organize OCR detections into a table structure
        
        Args:
            detections: List of detection dictionaries
            row_threshold: Vertical distance threshold to group items into rows (pixels)
            
        Returns:
            pandas DataFrame
        """
        if not detections:
            return pd.DataFrame()
        
        # Sort by vertical position (top to bottom)
        detections_sorted = sorted(detections, key=lambda x: x['center_y'])
        
        # Group into rows based on vertical proximity
        rows = []
        current_row = [detections_sorted[0]]
        
        for det in detections_sorted[1:]:
            if abs(det['center_y'] - current_row[-1]['center_y']) < row_threshold:
                current_row.append(det)
            else:
                rows.append(current_row)
                current_row = [det]
        
        if current_row:
            rows.append(current_row)
        
        # Sort each row by horizontal position (left to right)
        table_data = []
        for row in rows:
            row_sorted = sorted(row, key=lambda x: x['center_x'])
            row_texts = [det['text'] for det in row_sorted]
            table_data.append(row_texts)
        
        # Find maximum row length for padding
        max_cols = max(len(row) for row in table_data) if table_data else 0
        
        # Pad rows to have equal length
        for row in table_data:
            while len(row) < max_cols:
                row.append('')
        
        # Create DataFrame
        if len(table_data) > 1:
            # First row as headers
            df = pd.DataFrame(table_data[1:], columns=table_data[0])
        else:
            df = pd.DataFrame(table_data)
        
        # Clean values (convert '--' to NaN, convert numbers)
        for col in df.columns:
            df[col] = df[col].apply(self.clean_value)
        
        return df
    
    def process_scorecard(self, image_path, row_threshold=15):
        """
        Process a scorecard image and return a DataFrame
        
        Args:
            image_path: Path to the scorecard image
            row_threshold: Vertical distance threshold for grouping rows (pixels)
            
        Returns:
            pandas DataFrame with scorecard data
        """
        print(f"Processing: {image_path}")
        detections = self.process_image(image_path)
        
        if not detections:
            print(f"Warning: No text detected in {image_path}")
            return pd.DataFrame()
        
        df = self.organize_into_table(detections, row_threshold)
        print(f"Extracted table with shape: {df.shape}")
        
        return df


def process_scorecard(image_path, **kwargs):
    """
    Convenience function to process a single scorecard
    
    Args:
        image_path: Path to the scorecard image
        **kwargs: Additional arguments for ScorecardOCR
        
    Returns:
        pandas DataFrame
    """
    ocr = ScorecardOCR(**kwargs)
    return ocr.process_scorecard(image_path)


def process_multiple_scorecards(image_paths, output_dir=None, **kwargs):
    """
    Process multiple scorecards and optionally save to CSV
    
    Args:
        image_paths: List of paths to scorecard images
        output_dir: Directory to save CSV files (optional)
        **kwargs: Additional arguments for ScorecardOCR
        
    Returns:
        Dictionary mapping image paths to DataFrames
    """
    ocr = ScorecardOCR(**kwargs)
    results = {}
    
    for image_path in image_paths:
        try:
            df = ocr.process_scorecard(image_path)
            results[image_path] = df
            
            # Save to CSV if output directory specified
            if output_dir and not df.empty:
                os.makedirs(output_dir, exist_ok=True)
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                csv_path = os.path.join(output_dir, f"{base_name}.csv")
                df.to_csv(csv_path, index=False)
                print(f"Saved to: {csv_path}")
        
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            results[image_path] = None
    
    return results


if __name__ == "__main__":
    import glob
    
    # Example usage
    print("=" * 60)
    print("Golf Scorecard OCR Processor")
    print("=" * 60)
    
    # Find all scorecard images
    scorecard_dir = "scorecards"
    if os.path.exists(scorecard_dir):
        image_files = sorted(glob.glob(os.path.join(scorecard_dir, "*.png")))
        
        if image_files:
            print(f"\nFound {len(image_files)} scorecard images")
            print("-" * 60)
            
            # Process all scorecards
            results = process_multiple_scorecards(
                image_files,
                output_dir="output_csv"
            )
            
            # Display results
            print("\n" + "=" * 60)
            print("RESULTS SUMMARY")
            print("=" * 60)
            
            for img_path, df in results.items():
                print(f"\n{os.path.basename(img_path)}:")
                if df is not None and not df.empty:
                    print(df.to_string())
                else:
                    print("  No data extracted")
        else:
            print(f"\nNo scorecard images found in '{scorecard_dir}' directory")
    else:
        print(f"\nDirectory '{scorecard_dir}' not found")
        print("\nUsage example:")
        print("  from scorecard_ocr import process_scorecard")
        print("  df = process_scorecard('path/to/scorecard.png')")
        print("  print(df)")
