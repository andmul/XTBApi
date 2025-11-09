# Production Scorecard Processing Guide

## For Processing Thousands of Scorecards

This guide explains how to use the production-ready OCR processor for handling large batches of golf scorecard images.

## Overview

The `production_scorecard_processor.py` tool is designed to:
- Process thousands of scorecards automatically
- Handle OCR library compatibility issues with automatic fallbacks
- Preprocess images to improve OCR accuracy
- Track progress and log results
- Export clean data with proper NaN handling

## Installation

### Option 1: Tesseract (Most Compatible - Recommended)

```bash
# Install Tesseract OCR binary
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt-get install tesseract-ocr

# Install Python packages
pip install pytesseract pandas numpy opencv-python Pillow
```

### Option 2: PaddleOCR

```bash
pip install paddleocr paddlepaddle pandas numpy opencv-python
```

### Option 3: EasyOCR

```bash
pip install easyocr pandas numpy opencv-python
```

**Note**: The processor will automatically use whichever OCR engine is available, trying Tesseract first, then PaddleOCR, then EasyOCR.

## Usage

### 1. Prepare Your Images

Place all scorecard images in the `golfsc/` directory:

```
golfsc/
├── scorecard_001.png
├── scorecard_002.png
├── scorecard_003.png
└── ...
```

### 2. Run the Processor

```bash
python production_scorecard_processor.py
```

### 3. Check Results

Results are saved to `scorecard_dataframes/`:

```
scorecard_dataframes/
├── scorecard_001_data.csv
├── scorecard_002_data.csv
├── scorecard_003_data.csv
├── ...
└── processing_log.json
```

## Features

### Automatic Image Preprocessing

The processor automatically:
- Resizes images for optimal OCR
- Increases contrast using CLAHE
- Applies denoising
- Sharpens text
- Converts to optimal format for OCR

### Data Cleaning

Automatically handles:
- Converts `--`, `-`, `—`, `–`, `−` to NaN
- Converts numeric strings to int/float
- Removes empty rows/columns
- Properly structures tabular data

### Progress Tracking

- Real-time console output showing progress
- Per-image success/failure status
- Final summary with success rate
- Detailed JSON log of all operations

### Error Recovery

- Continues processing even if individual images fail
- Logs all errors for review
- Falls back to original image if preprocessing fails
- Tries multiple OCR strategies

## Processing Log

The `processing_log.json` file contains:
- Timestamp of processing
- Total images processed
- Success/failure counts
- OCR engine used
- Detailed results for each image

Example:
```json
{
  "timestamp": "2025-10-29T23:30:00",
  "total": 1000,
  "success": 950,
  "failed": 50,
  "ocr_engine": "tesseract",
  "results": [
    {
      "file": "scorecard_001.png",
      "status": "success",
      "rows": 18,
      "cols": 6,
      "output": "scorecard_dataframes/scorecard_001_data.csv"
    },
    ...
  ]
}
```

## Troubleshooting

### No OCR Engine Available

If you see "ERROR: No OCR engine available":
1. Install at least one OCR library (see Installation above)
2. For Tesseract, make sure the binary is installed AND the Python package

### Low Success Rate

If many scorecards fail:
1. Check the `processing_log.json` for specific errors
2. Ensure images are clear and readable
3. Try different OCR engines (they have different strengths)
4. Adjust preprocessing parameters if needed

### Memory Issues with Large Batches

For very large batches (10,000+ images):
1. Process in smaller batches (1000 at a time)
2. Clear the output directory between batches
3. Combine results afterward using pandas

```python
import pandas as pd
from pathlib import Path

# Combine all CSV files
csv_files = Path('scorecard_dataframes').glob('*_data.csv')
dfs = [pd.read_csv(f) for f in csv_files]
combined = pd.concat(dfs, ignore_index=True)
combined.to_csv('all_scorecards_combined.csv', index=False)
```

## Performance

Typical processing times per image:
- **Tesseract**: 0.5-2 seconds per image
- **PaddleOCR** (CPU): 2-5 seconds per image  
- **EasyOCR** (CPU): 3-6 seconds per image

For 1000 scorecards:
- **Tesseract**: ~15-30 minutes
- **PaddleOCR**: ~30-60 minutes
- **EasyOCR**: ~45-90 minutes

**GPU acceleration** (PaddleOCR/EasyOCR) can reduce times by 5-10x.

## Best Practices

1. **Test First**: Process a small sample (10-20 images) first to check quality
2. **Review Failures**: Check the log for patterns in failed images
3. **Verify Quality**: Spot-check a few random outputs to ensure accuracy
4. **Keep Originals**: Always keep original images as backup
5. **Version Control**: Track the processing log with your data

## Advanced Usage

### Custom Output Directory

```python
from production_scorecard_processor import ScorecardProcessor

processor = ScorecardProcessor(
    image_dir='my_scorecards',
    output_dir='my_results'
)
processor.process_batch()
```

### Process Specific Images

```python
processor = ScorecardProcessor()

# Process single image
df, error = processor.process_scorecard('path/to/scorecard.png')
if df is not None:
    df.to_csv('output.csv', index=False)
```

## Support

If you encounter issues:
1. Check the processing log (`processing_log.json`)
2. Verify image quality (clear, readable text)
3. Try different OCR engines
4. Check image preprocessing results

For thousands of scorecards, expect some failures - aim for 90%+ success rate. Review failed images manually or adjust preprocessing if needed.
