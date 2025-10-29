# Quick Start Guide - Golf Scorecard OCR

The Tesseract approach wasn't working well for the structured table data in your golf scorecards. Here's an **improved solution using PaddleOCR** with better table detection.

## Why the Previous Approach Failed

Tesseract OCR had trouble with:
- Identifying table rows correctly (vertical alignment issues)
- Separating columns properly (horizontal spacing)
- The structured nature of scorecard tables

## New Improved Approach

The new `process_scorecards_improved.py` uses PaddleOCR with:
- **Adaptive row detection**: Calculates threshold based on actual text height
- **Better column separation**: Uses center positions for accurate sorting
- **Robust table structure recognition**: Handles varying layouts

## Installation

```bash
# Install PaddleOCR (works with version 3.0+)
pip install paddleocr paddlepaddle

# Install other dependencies
pip install pandas numpy opencv-python Pillow
```

## Usage

### Quick Test (Process All Scorecards)

```bash
# Make sure your scorecard images are in real_golf_scorecards/ directory
python process_scorecards_improved.py
```

This will:
1. Process all `*_scorecard_*.png` files in `real_golf_scorecards/`
2. Show detected rows and columns for each image
3. Save results as CSV files in `scorecard_dataframes_improved/`
4. Automatically convert `--` to NaN
5. Convert numeric values to int/float

### Process Single Scorecard

```python
from process_scorecards_improved import process_golf_scorecard_improved

df = process_golf_scorecard_improved('real_golf_scorecards/000_scorecard_490002648255_1_496637001254.png')
print(df)
```

## Expected Output

The script will show:
- Number of text elements detected
- Row grouping (what text ended up in each row)
- The resulting DataFrame
- Saved CSV file location

Example output:
```
Processing: 000_scorecard_490002648255_1_496637001254.png
======================================================================
Detected 89 text elements
Using row threshold: 12.5 pixels
Organized into 8 rows
Row 0: ['Hole', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'OUT']
Row 1: ['Par', '4', '3', '5', '4', '4', '3', '5', '4', '4', '36']
Row 2: ['Score', '5', '--', '6', '4', '5', '3', '6', '4', '5', '38']
...

Extracted DataFrame:
======================================================================
  Hole  1  2  3  4  5  6  7  8  9 OUT
0  Par  4  3  5  4  4  3  5  4  4  36
1 Score 5 NaN 6  4  5  3  6  4  5  38
...
```

Notice that `--` is automatically converted to `NaN`!

## Troubleshooting

### Issue: Still not getting good results

Try adjusting the row threshold multiplier in the code:
```python
row_threshold = avg_height * 0.5  # Try 0.3, 0.4, 0.6, or 0.7
```

### Issue: PaddleOCR installation fails

If PaddleOCR 3.0+ has issues, you can also try:
```bash
pip install paddleocr==2.7.3 paddlepaddle
```

### Issue: Wrong column order

The script sorts columns left-to-right using the center position of each text box. If columns are still wrong, the image might need preprocessing (rotation, perspective correction).

## Alternative: Manual Inspection

If the automated approach still doesn't work perfectly, you can:

1. Run the script to see what it detects
2. Look at the "Row X: [...]" output to see how it's grouping text
3. Manually adjust the CSV files if needed
4. Or provide feedback on what's wrong, and I can fine-tune the detection algorithm

## Comparison: Old vs New

**Old Tesseract approach:**
- Used fixed pixel threshold (15 pixels)
- Didn't adapt to actual text size
- Simple vertical sorting

**New PaddleOCR approach:**
- Adaptive threshold based on text height
- Better handling of varying layouts
- More robust text detection
- Shows debug output so you can see what's happening

## Next Steps

1. Try running: `python process_scorecards_improved.py`
2. Check the console output to see how rows are being detected
3. Look at the CSV files in `scorecard_dataframes_improved/`
4. If results are still not good, share the console output so I can see what's being detected and adjust the algorithm
