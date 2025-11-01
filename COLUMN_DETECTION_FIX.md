# Fixing Missing First Column in OCR Results

## Problem

When processing golf scorecards with OCR, you may notice that the **first column is fractionally missing** or cut off from the results.

## Solution

The updated `process_scorecards_paddleocr3.py` script now includes **configurable parameters** to fix this issue.

## Parameters

### 1. `x_margin_left` (default: 0)

Controls how many pixels from the left edge of the image should be ignored.

**When to use:**
- The first column is completely missing
- Text on the far left is not being detected
- You want to exclude edge artifacts

**How to set:**
```python
from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3

# Try incrementally: 0, 5, 10, 15 pixels
df = process_golf_scorecard_paddleocr3('scorecard.png', x_margin_left=10)
```

**Values to try:**
- `0` (default) - No margin, include all detected text
- `5` - Exclude text within 5 pixels of left edge
- `10` - Exclude text within 10 pixels of left edge (recommended starting point)
- `15` - Exclude text within 15 pixels of left edge

### 2. `row_threshold_factor` (default: 0.6)

Controls how strictly elements are grouped into rows. This affects vertical alignment tolerance.

**When to use:**
- Rows are being split incorrectly
- Elements that should be on the same row are on different rows
- The first column items are being placed on separate rows

**How to set:**
```python
# Tighter grouping (elements must be closer vertically)
df = process_golf_scorecard_paddleocr3('scorecard.png', row_threshold_factor=0.5)

# Looser grouping (elements can be further apart vertically)
df = process_golf_scorecard_paddleocr3('scorecard.png', row_threshold_factor=0.7)
```

**Values to try:**
- `0.4` - Very strict (elements must be very close)
- `0.5` - Strict (tighter than default)
- `0.6` (default) - Balanced
- `0.7` - Lenient (looser grouping)
- `0.8` - Very lenient

## Quick Fix Guide

### If the first column is completely missing:

1. **First, run without parameters** to see diagnostic output:
   ```bash
   python process_scorecards_paddleocr3.py
   ```

2. **Look for the diagnostic message:**
   ```
   Minimum x-coordinate found: 8.3
   💡 TIP: If first column is missing, try: x_margin_left=13
   ```

3. **Edit the script** at line ~260 and set the suggested value:
   ```python
   X_MARGIN_LEFT = 0  # Change this to the suggested value
   ```

4. **Re-run the script:**
   ```bash
   python process_scorecards_paddleocr3.py
   ```

### If the first column is partially there but misaligned:

Try adjusting the row threshold factor:

```python
# In the script, around line 261:
ROW_THRESHOLD_FACTOR = 0.5  # Try 0.5 instead of 0.6
```

### If using as a Python module:

```python
from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3

# Try different combinations
df = process_golf_scorecard_paddleocr3(
    'scorecard.png',
    x_margin_left=10,         # Skip left 10 pixels
    row_threshold_factor=0.5  # Tighter row grouping
)

print(df)
```

## Understanding the Debug Output

When you run the processor, it shows diagnostic information:

```
Detected 142 text elements
Parsed 140 valid text elements
Minimum x-coordinate found: 8.3
💡 TIP: If first column is missing, try: x_margin_left=13
Organized into 8 rows (threshold: 7.5px)
Row 0: ['Hole', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'OUT']
Row 1: ['Par', '4', '3', '5', '4', '4', '3', '5', '4', '4', '36']
...
```

**Key information:**
- **Detected X text elements**: Total text found by OCR
- **Parsed X valid text elements**: Elements after filtering
- **Minimum x-coordinate**: Leftmost position of detected text
- **Organized into X rows**: How many rows were detected
- **Row X: [...]**: Contents of each row (check if first column is present)

## Common Scenarios

### Scenario 1: First column completely missing

**Symptom:** Row data starts from second column
```
Row 0: ['1', '2', '3', '4', '5']  # Missing 'Hole' column
```

**Fix:** Increase `x_margin_left` to exclude edge artifacts
```python
X_MARGIN_LEFT = 10  # or 15
```

### Scenario 2: First column item on wrong row

**Symptom:** First column appears in different rows than it should
```
Row 0: ['Hole']
Row 1: ['1', '2', '3', '4', '5']
```

**Fix:** Adjust `row_threshold_factor`
```python
ROW_THRESHOLD_FACTOR = 0.7  # Looser grouping
```

### Scenario 3: First column partially present

**Symptom:** Only some first column items are missing
```
Row 0: ['Hole', '1', '2', '3']
Row 1: ['2', '4', '5']  # Missing 'Par' in first position
Row 2: ['Score', '3', '5', '6']
```

**Fix:** Combine both parameters
```python
X_MARGIN_LEFT = 5
ROW_THRESHOLD_FACTOR = 0.65
```

## Testing Your Changes

After adjusting parameters:

1. **Check the debug output** to see if row structure improves
2. **Inspect the CSV file** to verify first column is present
3. **View the DataFrame preview** in the console output
4. **Try processing multiple scorecards** to ensure consistency

## Advanced: Per-Image Parameters

If different scorecards need different parameters, use Python:

```python
from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3
import glob

scorecards = glob.glob('golfsc/*.png')

for scorecard in scorecards:
    # Adjust parameters based on scorecard filename or characteristics
    if 'type_a' in scorecard:
        df = process_golf_scorecard_paddleocr3(
            scorecard,
            x_margin_left=10,
            row_threshold_factor=0.5
        )
    else:
        df = process_golf_scorecard_paddleocr3(
            scorecard,
            x_margin_left=5,
            row_threshold_factor=0.6
        )
    
    # Save with custom name
    df.to_csv(f'output/{Path(scorecard).stem}.csv', index=False)
```

## Still Having Issues?

If adjusting these parameters doesn't fix the first column issue:

1. **Check image quality**: Ensure the image is clear and well-lit
2. **Check image alignment**: Ensure the scorecard is not rotated or skewed
3. **Check OCR detection**: Some text might not be detected at all by OCR
4. **Try preprocessing**: Apply image preprocessing (contrast, sharpening) before OCR
5. **Check for table lines**: Heavy table borders might interfere with text detection

## Summary

**Quick reference for fixing missing first column:**

| Issue | Parameter | Value to Try |
|-------|-----------|--------------|
| First column completely missing | `x_margin_left` | 10, 15, 20 |
| First column on wrong rows | `row_threshold_factor` | 0.7, 0.8 |
| First column partially missing | Both parameters | `x_margin_left=5`, `row_threshold_factor=0.65` |
| Rows split incorrectly | `row_threshold_factor` | 0.5, 0.4 (tighter) |
