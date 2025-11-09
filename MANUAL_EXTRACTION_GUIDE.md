# Manual Scorecard Extraction Guide

Since the OCR libraries (PaddleOCR, EasyOCR, Tesseract) are having compatibility issues with your system, this manual extraction tool provides a reliable alternative.

## What is This?

A simple GUI tool that displays your scorecard images and lets you manually type in the values. It then converts them to pandas DataFrames with proper handling of:
- `--` converted to NaN
- Automatic numeric type conversion
- CSV export

## Installation

```bash
# Install only the basic dependencies (no OCR libraries needed!)
pip install pandas numpy opencv-python pillow
```

## Usage

1. **Make sure your scorecard images are in the `golfsc/` directory**

2. **Run the tool:**
   ```bash
   python manual_scorecard_extractor.py
   ```

3. **The GUI will show:**
   - The scorecard image at the top
   - An entry field to type values
   - Buttons to navigate
   - A display of your current data

4. **How to extract data:**
   - Look at the scorecard image
   - Type the first value (leftmost cell in top row)
   - Press Enter or click "Next Cell"
   - Continue entering values from left to right
   - When you finish a row, click "Next Row"
   - When you finish the entire scorecard, click "Next Image"
   - Repeat for all scorecards
   - Click "Save & Exit" when done

5. **Special handling:**
   - For missing values, type `--` (will become NaN)
   - Numbers are automatically converted to numeric types
   - All data is saved to `scorecard_dataframes/` as CSV files

## Example Workflow

```
Scorecard: 000_scorecard_490002648255_1_496637001254.png

Image shows:
| Hole | Par | Score | Putt |
|------|-----|-------|------|
|  1   |  4  |   5   |  2   |
|  2   |  3  |   --  |  --  |

You enter:
- "Hole" → Next Cell
- "Par" → Next Cell
- "Score" → Next Cell
- "Putt" → Next Row
- "1" → Next Cell
- "4" → Next Cell
- "5" → Next Cell
- "2" → Next Row
- "2" → Next Cell
- "3" → Next Cell
- "--" → Next Cell
- "--" → Next Row
→ Next Image

Output CSV:
Hole,Par,Score,Putt
1,4,5,2
2,3,,
```

## Output

All scorecards will be saved to `scorecard_dataframes/` with filenames like:
- `000_scorecard_490002648255_1_496637001254_manual.csv`
- `001_scorecard_490002776791_2_496637001254_manual.csv`
- etc.

## Tips

- Take your time - accuracy is more important than speed
- You can close and restart anytime - progress is saved per image
- If you make a mistake, just continue - you can edit the CSV files after
- The tool is much more reliable than fighting with OCR library compatibility issues

## Why Manual Extraction?

Given the challenges with:
- PaddleOCR not detecting text (returning 0 elements)
- EasyOCR crashing with illegal instruction errors (CPU incompatibility)
- Tesseract producing poor table structure results
- OpenMP library conflicts
- Python 3.13 compatibility issues

Manual extraction is actually the **fastest** and **most reliable** solution for your 11 scorecards. It should take about 10-15 minutes total to extract all the data accurately.

## Need Help?

If the manual tool has issues:
1. Make sure `golfsc/` directory exists with your PNG files
2. Check that you have the basic dependencies installed
3. Try running on Python 3.10 or 3.11 if you're on 3.13
