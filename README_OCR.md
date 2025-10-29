# Golf Scorecard OCR Processing

This project provides OCR functionality to extract tabular data from golf scorecard images and convert them to pandas DataFrames using PaddleOCR.

## Features

- **High-accuracy OCR** using PaddleOCR (tested with version 2.7.0.3)
- **Automatic table detection** and organization
- **Smart data cleaning**: Converts `--` to `NaN` for missing values
- **Numeric type conversion**: Automatically converts numbers to int/float
- **Batch processing**: Process multiple scorecards at once
- **CSV export**: Save extracted data to CSV files

## Installation

### Prerequisites

- Python 3.6 or higher
- pip

### Install Dependencies

```bash
pip install -r requirements_ocr.txt
```

Or install packages individually:

```bash
pip install pandas numpy opencv-python paddleocr==2.7.0.3 paddlepaddle
```

## Usage

### Basic Usage

Process a single scorecard image:

```python
from scorecard_ocr import process_scorecard

# Process one scorecard
df = process_scorecard('score_1.png')
print(df)
```

### Advanced Usage

Use the `ScorecardOCR` class for more control:

```python
from scorecard_ocr import ScorecardOCR

# Initialize OCR processor
ocr = ScorecardOCR(lang='en', use_angle_cls=True, use_gpu=False)

# Process image
df = ocr.process_scorecard('score_1.png', row_threshold=15)

# Display results
print(df)
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
```

### Batch Processing

Process multiple scorecards and save to CSV:

```python
from scorecard_ocr import process_multiple_scorecards
import glob

# Find all scorecard images
image_files = glob.glob('score_*.png')

# Process all and save to CSV
results = process_multiple_scorecards(
    image_files,
    output_dir='output_csv'
)

# Display results
for img_path, df in results.items():
    print(f"\n{img_path}:")
    print(df)
```

### Command Line Usage

Run the script directly to process all scorecards in the `scorecards/` directory:

```bash
python scorecard_ocr.py
```

This will:
1. Find all `.png` files in the `scorecards/` directory
2. Process each image with OCR
3. Save results to CSV files in `output_csv/` directory
4. Display extracted data in the terminal

## Data Cleaning

The OCR processor automatically cleans extracted data:

- **Missing values**: `--`, `-`, `—` are converted to `NaN`
- **Numbers**: Strings that look like numbers are converted to `int` or `float`
- **Text**: Other values remain as strings

Example:

```
Input:    ["John", "25", "--", "3.5", "Team A"]
Output:   ["John", 25, NaN, 3.5, "Team A"]
```

## Customization

### Adjust Row Grouping

If text on the same row is not being grouped correctly, adjust the `row_threshold` parameter:

```python
# Increase threshold for more lenient row grouping
df = ocr.process_scorecard('score_1.png', row_threshold=20)

# Decrease threshold for stricter row grouping
df = ocr.process_scorecard('score_1.png', row_threshold=10)
```

### GPU Acceleration

Enable GPU for faster processing (requires CUDA):

```python
ocr = ScorecardOCR(use_gpu=True)
```

### Different Languages

Support for multiple languages:

```python
# For Chinese scorecards
ocr = ScorecardOCR(lang='ch')

# For mixed English and Chinese
ocr = ScorecardOCR(lang='ch')
```

## Expected Input Format

The OCR works best with:

- **Clear, high-resolution images** (recommended: at least 800x600 pixels)
- **Well-lit, minimal shadows**
- **Tabular layout** with rows and columns
- **Printed or typed text** (handwriting may have lower accuracy)

## Output Format

The output is a pandas DataFrame with:

- **First row of table**: Used as column headers
- **Subsequent rows**: Data rows
- **Numeric columns**: Automatically converted to appropriate types
- **Missing values**: Represented as `NaN`

Example output:

```
     Player  Hole 1  Hole 2  Hole 3  Team
0     John       4       5     NaN  Team A
1     Jane       3       4       5  Team B
2      Bob       5     NaN       4  Team A
```

## Troubleshooting

### Low Accuracy

1. **Improve image quality**: Use higher resolution images
2. **Adjust preprocessing**: PaddleOCR has built-in preprocessing that usually works well
3. **Adjust row_threshold**: Fine-tune the row grouping parameter

### Installation Issues

If you encounter issues installing PaddleOCR:

1. Make sure you have the correct Python version (3.6+)
2. Try installing paddlepaddle separately first: `pip install paddlepaddle`
3. Check PaddleOCR documentation: https://github.com/PaddlePaddle/PaddleOCR

### Alternative OCR Libraries

If PaddleOCR doesn't work for your use case, consider:

- **EasyOCR**: `pip install easyocr` - Good for multi-language support
- **Tesseract**: `pip install pytesseract` - Requires Tesseract-OCR installation
- **Azure Computer Vision**: Cloud-based, very high accuracy

## File Structure

```
.
├── scorecard_ocr.py          # Main OCR processing script
├── requirements_ocr.txt      # Python dependencies
├── README_OCR.md            # This file
├── scorecards/              # Directory for input scorecard images
│   ├── score_1.png
│   ├── score_2.png
│   └── ...
└── output_csv/              # Directory for output CSV files (auto-created)
    ├── score_1.csv
    ├── score_2.csv
    └── ...
```

## Testing

To test with the sample scorecards:

```bash
# Make sure scorecard images are in the scorecards/ directory
ls scorecards/

# Run the OCR processor
python scorecard_ocr.py

# Check the output
ls output_csv/
cat output_csv/score_1.csv
```

## Performance

Processing time depends on:

- **Image resolution**: Higher resolution = longer processing time
- **Number of text elements**: More text = longer processing time
- **Hardware**: GPU acceleration significantly speeds up processing

Typical processing times (CPU):
- Small image (800x600): 2-5 seconds
- Medium image (1920x1080): 5-10 seconds
- Large image (4000x3000): 15-30 seconds

## License

This code is provided as-is for processing golf scorecards using OCR technology.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review PaddleOCR documentation: https://github.com/PaddlePaddle/PaddleOCR
3. Open an issue in the repository
