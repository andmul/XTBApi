#!/usr/bin/env python3
"""
Production-ready scorecard OCR processor for handling thousands of scorecards.

This processor combines multiple OCR strategies with fallbacks to ensure
maximum success rate across large batches of scorecard images.

Features:
- Multiple OCR engines with automatic fallback
- Image preprocessing to improve OCR accuracy
- Batch processing with progress tracking
- Error recovery and logging
- Automatic '--' to NaN conversion
- CSV export with batch summaries
"""

import os
import sys
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import traceback

# Configuration
IMAGE_DIR = 'golfsc'
OUTPUT_DIR = 'scorecard_dataframes'
LOG_FILE = 'processing_log.json'

class ScorecardProcessor:
    """
    Production OCR processor with multiple strategies and fallbacks.
    """
    
    def __init__(self, image_dir=IMAGE_DIR, output_dir=OUTPUT_DIR):
        self.image_dir = image_dir
        self.output_dir = output_dir
        self.ocr_engine = None
        self.ocr_type = None
        self.processing_log = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize OCR engine
        self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Try to initialize OCR engines in order of preference."""
        
        # Try 1: Tesseract (most compatible)
        try:
            import pytesseract
            # Test if tesseract is actually installed
            pytesseract.get_tesseract_version()
            self.ocr_engine = 'tesseract'
            self.ocr_type = 'tesseract'
            print("✓ Using Tesseract OCR")
            return
        except Exception as e:
            print(f"  Tesseract not available: {e}")
        
        # Try 2: PaddleOCR
        try:
            from paddleocr import PaddleOCR
            # Initialize with minimal parameters
            ocr = PaddleOCR(lang='en', show_log=False)
            self.ocr_engine = ocr
            self.ocr_type = 'paddleocr'
            print("✓ Using PaddleOCR")
            return
        except Exception as e:
            print(f"  PaddleOCR not available: {e}")
        
        # Try 3: EasyOCR
        try:
            os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            self.ocr_engine = reader
            self.ocr_type = 'easyocr'
            print("✓ Using EasyOCR")
            return
        except Exception as e:
            print(f"  EasyOCR not available: {e}")
        
        print("\n❌ ERROR: No OCR engine available!")
        print("\nPlease install one of the following:")
        print("  1. Tesseract: pip install pytesseract (and install Tesseract binary)")
        print("  2. PaddleOCR: pip install paddleocr paddlepaddle")
        print("  3. EasyOCR: pip install easyocr")
        sys.exit(1)
    
    def preprocess_image(self, image_path):
        """
        Preprocess image to improve OCR accuracy.
        - Resize if too small
        - Increase contrast
        - Apply denoising
        - Sharpen text
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Resize if too small (helps OCR)
        height, width = img.shape[:2]
        if width < 1000:
            scale = 1500 / width
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Increase contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(gray)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(contrast, None, 10, 7, 21)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # Threshold to get black text on white background
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def run_ocr(self, image_path):
        """Run OCR on preprocessed image."""
        
        # Preprocess
        try:
            processed_img = self.preprocess_image(image_path)
        except Exception as e:
            print(f"    Preprocessing failed: {e}")
            # Fall back to original image
            processed_img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        results = []
        
        if self.ocr_type == 'tesseract':
            import pytesseract
            # Get detailed box information
            data = pytesseract.image_to_data(processed_img, output_type=pytesseract.Output.DICT)
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text and int(data['conf'][i]) > 30:  # Confidence threshold
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    # Store as (text, bbox, confidence)
                    results.append((text, [[x, y], [x+w, y], [x+w, y+h], [x, y+h]], data['conf'][i]))
        
        elif self.ocr_type == 'paddleocr':
            try:
                # Try predict() first (newer API)
                result = self.ocr_engine.predict(image_path)
            except:
                # Fall back to ocr() (older API)
                result = self.ocr_engine.ocr(image_path)
            
            if result and result[0]:
                for line in result[0]:
                    if isinstance(line, (list, tuple)) and len(line) >= 2:
                        bbox = line[0]
                        text_info = line[1]
                        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                            text = text_info[0]
                            conf = text_info[1] * 100  # Convert to percentage
                            results.append((text, bbox, conf))
        
        elif self.ocr_type == 'easyocr':
            result = self.ocr_engine.readtext(processed_img)
            for bbox, text, conf in result:
                results.append((text, bbox, conf * 100))
        
        return results
    
    def organize_into_table(self, ocr_results):
        """
        Organize OCR results into a structured table.
        Groups text by rows based on Y-coordinates.
        """
        if not ocr_results:
            return pd.DataFrame()
        
        # Extract text with positions
        elements = []
        for text, bbox, conf in ocr_results:
            # Get bounding box coordinates
            if isinstance(bbox[0], (list, tuple)):
                y_coords = [point[1] for point in bbox]
                x_coords = [point[0] for point in bbox]
            else:
                y_coords = [bbox[0][1], bbox[2][1]]
                x_coords = [bbox[0][0], bbox[2][0]]
            
            y_center = sum(y_coords) / len(y_coords)
            x_center = sum(x_coords) / len(x_coords)
            height = max(y_coords) - min(y_coords)
            
            elements.append({
                'text': text,
                'x': x_center,
                'y': y_center,
                'height': height,
                'conf': conf
            })
        
        if not elements:
            return pd.DataFrame()
        
        # Sort by Y position
        elements.sort(key=lambda e: e['y'])
        
        # Group into rows based on Y proximity
        rows = []
        current_row = [elements[0]]
        avg_height = elements[0]['height']
        
        for elem in elements[1:]:
            # If within 0.5 * average height, same row
            if elem['y'] - current_row[0]['y'] < avg_height * 0.5:
                current_row.append(elem)
            else:
                # Start new row
                # Sort current row by X
                current_row.sort(key=lambda e: e['x'])
                rows.append(current_row)
                current_row = [elem]
                # Update average height
                avg_height = (avg_height + elem['height']) / 2
        
        # Add last row
        if current_row:
            current_row.sort(key=lambda e: e['x'])
            rows.append(current_row)
        
        # Convert to DataFrame
        max_cols = max(len(row) for row in rows)
        data = []
        for row in rows:
            row_data = [elem['text'] for elem in row]
            # Pad with empty strings
            row_data.extend([''] * (max_cols - len(row_data)))
            data.append(row_data)
        
        df = pd.DataFrame(data)
        
        # Clean up data
        df = self.clean_dataframe(df)
        
        return df
    
    def clean_dataframe(self, df):
        """
        Clean the dataframe:
        - Convert '--', '-', '—' to NaN
        - Convert numeric strings to appropriate types
        """
        # Replace various dash representations with NaN
        df = df.replace(['--', '-', '—', '–', '−'], np.nan)
        
        # Try to convert columns to numeric where possible
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass
        
        return df
    
    def process_scorecard(self, image_path):
        """Process a single scorecard image."""
        try:
            print(f"    Running OCR...")
            ocr_results = self.run_ocr(image_path)
            
            print(f"    Detected {len(ocr_results)} text elements")
            
            if len(ocr_results) == 0:
                return None, "No text detected"
            
            print(f"    Organizing into table...")
            df = self.organize_into_table(ocr_results)
            
            if df.empty:
                return None, "Could not organize into table"
            
            return df, None
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            traceback.print_exc()
            return None, error_msg
    
    def process_batch(self):
        """Process all scorecards in the image directory."""
        
        # Find all PNG images
        image_paths = list(Path(self.image_dir).glob('*.png'))
        
        if not image_paths:
            print(f"\n❌ No PNG images found in '{self.image_dir}/' directory")
            print(f"\nPlease place your scorecard images in the '{self.image_dir}/' directory.")
            return
        
        print(f"\nFound {len(image_paths)} scorecard images")
        print("=" * 70)
        
        success_count = 0
        fail_count = 0
        
        for idx, img_path in enumerate(image_paths, 1):
            print(f"\n[{idx}/{len(image_paths)}] Processing: {img_path.name}")
            print("-" * 70)
            
            df, error = self.process_scorecard(str(img_path))
            
            if df is not None:
                # Save to CSV
                output_file = Path(self.output_dir) / f"{img_path.stem}_data.csv"
                df.to_csv(output_file, index=False)
                print(f"    ✓ Saved: {output_file}")
                print(f"    Shape: {df.shape[0]} rows x {df.shape[1]} columns")
                
                success_count += 1
                self.processing_log.append({
                    'file': img_path.name,
                    'status': 'success',
                    'rows': int(df.shape[0]),
                    'cols': int(df.shape[1]),
                    'output': str(output_file)
                })
            else:
                print(f"    ❌ Failed: {error}")
                fail_count += 1
                self.processing_log.append({
                    'file': img_path.name,
                    'status': 'failed',
                    'error': error
                })
        
        # Save processing log
        log_path = Path(self.output_dir) / LOG_FILE
        with open(log_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total': len(image_paths),
                'success': success_count,
                'failed': fail_count,
                'ocr_engine': self.ocr_type,
                'results': self.processing_log
            }, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Total processed: {len(image_paths)}")
        print(f"✓ Successful: {success_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"Success rate: {success_count/len(image_paths)*100:.1f}%")
        print(f"\nResults saved to: {self.output_dir}/")
        print(f"Processing log: {log_path}")
        
        if fail_count > 0:
            print(f"\n⚠️  {fail_count} scorecard(s) failed to process.")
            print("Check the processing log for details.")


def main():
    """Main entry point."""
    print("=" * 70)
    print("PRODUCTION SCORECARD PROCESSOR")
    print("=" * 70)
    print("\nInitializing OCR engine...")
    
    processor = ScorecardProcessor()
    processor.process_batch()
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
