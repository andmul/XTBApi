# Golf Scorecard OCR Processing - Setup Guide

This guide explains how to process the actual golf scorecard images from the `andmul/golfsc` repository.

## Golf Scorecard Images

The actual golf scorecard images are located in the **andmul/golfsc** repository:
- Files: `000_scorecard_*.png` to `010_scorecard_*.png` (11 total images)
- Format: PNG images, approximately 1030x370 pixels
- Content: Tabular golf scorecard data with numeric scores and `--` for missing values

## Processing Scripts

### `process_golf_scorecards.py`

Main script for processing golf scorecards using Tesseract OCR.

**Features:**
- Uses Tesseract OCR for high-accuracy text extraction
- Automatically organizes text into table rows/columns
- Converts `--`, `-`, and empty values to NaN  
- Converts numeric strings to int/float automatically
- Saves results to CSV files in `scorecard_dataframes/` directory

**Usage:**

1. **Download the scorecard images:**
   ```bash
   # Create directory
   mkdir -p real_golf_scorecards
   cd real_golf_scorecards
   
   # Download all 11 scorecard images from andmul/golfsc repository
   for file in 000_scorecard_490002648255_1_496637001254.png \
               001_scorecard_490002776791_2_496637001254.png \
               002_scorecard_490002776791_1_496637001254.png \
               003_scorecard_490002648253_1_496637001254.png \
               004_scorecard_490002648251_1_496637001254.png \
               005_scorecard_490002776790_3_496637001254.png \
               006_scorecard_490002776790_1_496637001254.png \
               007_scorecard_490002776790_2_496637001254.png \
               008_scorecard_490002654106_1_496637001254.png \
               009_scorecard_490002648244_1_496637001254.png \
               010_scorecard_490002648242_1_496637001254.png; do
       curl -L -o "$file" "https://raw.githubusercontent.com/andmul/golfsc/main/$file"
   done
   cd ..
   ```

2. **Install dependencies:**
   ```bash
   # System packages (Tesseract OCR)
   sudo apt-get update
   sudo apt-get install -y tesseract-ocr
   
   # Python packages
   pip install pandas numpy opencv-python-headless pytesseract Pillow
   ```

3. **Run the processor:**
   ```bash
   python process_golf_scorecards.py
   ```

4. **Check results:**
   ```bash
   # View CSV outputs
   ls scorecard_dataframes/
   cat scorecard_dataframes/000_scorecard_490002648255_1_496637001254.csv
   ```

## Alternative: Using PaddleOCR

The `scorecard_ocr.py` script provides an alternative implementation using PaddleOCR:

```bash
# Install PaddleOCR (works with version 2.7+ or 3.0+)
pip install paddleocr paddlepaddle

# Use the scorecard_ocr module
python -c "
from scorecard_ocr import process_scorecard
import glob

for img in sorted(glob.glob('real_golf_scorecards/*.png')):
    df = process_scorecard(img)
    print(f'\n{img}:')
    print(df)
"
```

**Note:** PaddleOCR 3.0+ works with this code. The older version 2.7.0.3 is no longer required.

## Data Cleaning

Both scripts automatically clean the data:

**Input (from OCR):**
```
Player    Hole1  Hole2  Hole3  Total
John      4      5      --     9
Jane      3      --     5      8
```

**Output (DataFrame):**
```
   Player  Hole1  Hole2  Hole3  Total
0    John      4    5.0    NaN      9
1    Jane      3    NaN    5.0      8
```

## Expected Output Structure

Each golf scorecard will be converted to a pandas DataFrame with:
- **Columns**: Extracted from the first row of the table
- **Numeric values**: Automatically converted to int/float
- **Missing values**: `--` converted to NaN
- **Text values**: Preserved as strings

## Troubleshooting

### No text detected
- Check image quality and resolution
- Try adjusting the `row_threshold` parameter in the script
- Verify Tesseract is installed: `tesseract --version`

### Wrong table structure
- The script groups text by vertical position (Y-coordinate)
- Adjust `row_threshold` value (default: 15 pixels) if rows are incorrectly grouped
- Check the "Extracted table structure" output to see how rows are organized

### Installation issues
- For Tesseract: `sudo apt-get install tesseract-ocr`
- For Python packages: Use a virtual environment
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements_ocr.txt
  ```

## File Structure

```
.
├── process_golf_scorecards.py    # Main processor for golf scorecards (Tesseract)
├── scorecard_ocr.py              # Alternative processor (PaddleOCR)
├── requirements_ocr.txt          # Python dependencies
├── README_GOLF_SCORECARDS.md     # This file
├── real_golf_scorecards/         # Downloaded scorecard images (excluded from git)
│   ├── 000_scorecard_*.png
│   ├── 001_scorecard_*.png
│   └── ...
└── scorecard_dataframes/         # Output CSV files (excluded from git)
    ├── 000_scorecard_*.csv
    ├── 001_scorecard_*.csv
    └── ...
```

## Integration with golfsc Repository

The golf scorecard images are maintained in the **andmul/golfsc** repository. To process them:

1. Clone or download images from https://github.com/andmul/golfsc
2. Place images in `real_golf_scorecards/` directory
3. Run `process_golf_scorecards.py`
4. Find results in `scorecard_dataframes/` directory

## Next Steps

1. Download the actual golf scorecard images from andmul/golfsc
2. Install dependencies
3. Run the processor
4. Review the extracted DataFrames
5. Adjust parameters if needed for better accuracy
6. Use the CSV files for further analysis

For more details on the OCR implementation, see `README_OCR.md`.
