# Quick Fix: Missing First Column

## The Problem
You mentioned that **the first column is fractionally missing** from your OCR results.

## The Solution
I've added **two configurable parameters** to fix this:

### 1. `x_margin_left` - Handles left edge issues
Set this to ignore pixels from the left edge that might be causing problems.

### 2. `row_threshold_factor` - Controls row grouping
Set this to adjust how strictly elements are grouped into rows.

## How to Use

### Option A: Edit the Script (Easiest)

1. Open `process_scorecards_paddleocr3.py`

2. Find lines ~256-257:
   ```python
   X_MARGIN_LEFT = 0  # Change to 5, 10, or 15 if first column is cut off
   ROW_THRESHOLD_FACTOR = 0.6  # Change to 0.5 for tighter rows, 0.7 for looser
   ```

3. Change the values:
   ```python
   X_MARGIN_LEFT = 10  # Try this first
   ROW_THRESHOLD_FACTOR = 0.6  # Keep as is initially
   ```

4. Run again:
   ```bash
   python process_scorecards_paddleocr3.py
   ```

### Option B: Use as Python Module

```python
from process_scorecards_paddleocr3 import process_golf_scorecard_paddleocr3

# Process with parameters
df = process_golf_scorecard_paddleocr3(
    'your_scorecard.png',
    x_margin_left=10,         # Adjust as needed
    row_threshold_factor=0.6  # Adjust as needed
)

print(df)
```

## Which Values to Try?

### For `x_margin_left`:
- Start with `10`
- If still missing, try `15` or `20`
- If that's too much, try `5`

### For `row_threshold_factor`:
- If first column items are on separate rows: try `0.7` or `0.8` (looser)
- If rows are merging incorrectly: try `0.5` or `0.4` (tighter)
- Default `0.6` works for most cases

## Diagnostic Output

The script now shows helpful information:

```
Detected 142 text elements
Parsed 140 valid text elements
Minimum x-coordinate found: 8.3
💡 TIP: If first column is missing, try: x_margin_left=13
```

**Follow the TIP!** The script tells you what value to try for `x_margin_left`.

## Example Scenarios

### Scenario: First column completely missing
```python
# Before: Row 0: ['1', '2', '3', '4']
# After:  Row 0: ['Hole', '1', '2', '3', '4']

# Fix:
X_MARGIN_LEFT = 10
```

### Scenario: First column on wrong rows  
```python
# Before:
# Row 0: ['Hole']
# Row 1: ['1', '2', '3']

# After:
# Row 0: ['Hole', '1', '2', '3']

# Fix:
ROW_THRESHOLD_FACTOR = 0.7  # Looser grouping
```

## Full Documentation

See `COLUMN_DETECTION_FIX.md` for:
- Detailed explanation of parameters
- More examples
- Troubleshooting guide
- Advanced usage

## Questions?

The parameters are well-documented in the code. Just look for the docstring at the top of `process_golf_scorecard_paddleocr3()` function.
