#!/usr/bin/env python3
"""
Manual Scorecard Data Extractor - Simple GUI Tool
Allows manual extraction of scorecard data when OCR fails
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import cv2
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk

class ScorecardExtractor:
    def __init__(self, image_dir='golfsc'):
        self.image_dir = image_dir
        self.current_image_idx = 0
        self.images = sorted([f for f in os.listdir(image_dir) if f.endswith('.png')])
        self.data = []
        self.current_row = []
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Golf Scorecard Manual Extractor")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Image display
        self.canvas = tk.Canvas(main_frame, width=1000, height=400, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        
        # Instructions
        instructions = """
        Instructions:
        1. Look at the scorecard image
        2. Enter values from left to right, top to bottom
        3. Use '--' for missing values (will become NaN)
        4. Click 'Next Cell' after each value
        5. Click 'Next Row' to move to next row
        6. Click 'Next Image' when done with this scorecard
        """
        ttk.Label(main_frame, text=instructions, justify=tk.LEFT).grid(row=1, column=0, columnspan=3, pady=5)
        
        # Entry field
        ttk.Label(main_frame, text="Enter Value:").grid(row=2, column=0, padx=5)
        self.entry = ttk.Entry(main_frame, width=20)
        self.entry.grid(row=2, column=1, padx=5)
        self.entry.bind('<Return>', lambda e: self.add_cell())
        
        # Buttons
        ttk.Button(main_frame, text="Next Cell", command=self.add_cell).grid(row=2, column=2, padx=5)
        ttk.Button(main_frame, text="Next Row", command=self.next_row).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(main_frame, text="Next Image", command=self.next_image).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Save & Exit", command=self.save_and_exit).grid(row=3, column=2, padx=5, pady=5)
        
        # Current data display
        self.data_text = tk.Text(main_frame, height=10, width=80)
        self.data_text.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
        
        # Load first image
        self.load_image()
        
    def load_image(self):
        if self.current_image_idx >= len(self.images):
            messagebox.showinfo("Complete", "All images processed!")
            self.save_and_exit()
            return
            
        image_path = os.path.join(self.image_dir, self.images[self.current_image_idx])
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize to fit canvas
        h, w = img.shape[:2]
        scale = min(1000/w, 400/h)
        new_w, new_h = int(w*scale), int(h*scale)
        img = cv2.resize(img, (new_w, new_h))
        
        # Convert to PhotoImage
        img_pil = Image.fromarray(img)
        self.photo = ImageTk.PhotoImage(img_pil)
        self.canvas.create_image(500, 200, image=self.photo)
        
        self.root.title(f"Scorecard Extractor - {self.images[self.current_image_idx]} ({self.current_image_idx+1}/{len(self.images)})")
        self.update_data_display()
        
    def add_cell(self):
        value = self.entry.get().strip()
        if not value:
            return
            
        # Convert '--' to NaN marker
        if value in ['--', '-', '—']:
            value = 'NaN'
            
        self.current_row.append(value)
        self.entry.delete(0, tk.END)
        self.update_data_display()
        
    def next_row(self):
        if self.current_row:
            self.data.append(self.current_row)
            self.current_row = []
            self.update_data_display()
            
    def next_image(self):
        # Save current row if not empty
        if self.current_row:
            self.data.append(self.current_row)
            self.current_row = []
            
        # Save current image data
        if self.data:
            self.save_current_scorecard()
            self.data = []
            
        self.current_image_idx += 1
        self.load_image()
        
    def update_data_display(self):
        self.data_text.delete(1.0, tk.END)
        self.data_text.insert(1.0, f"Current row: {self.current_row}\n\n")
        self.data_text.insert(tk.END, "Completed rows:\n")
        for i, row in enumerate(self.data):
            self.data_text.insert(tk.END, f"Row {i+1}: {row}\n")
            
    def save_current_scorecard(self):
        if not self.data:
            return
            
        # Convert to DataFrame
        df = pd.DataFrame(self.data)
        
        # Convert 'NaN' strings to actual NaN
        df = df.replace('NaN', np.nan)
        
        # Try to convert numeric columns
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='ignore')
            
        # Save to CSV
        output_dir = 'scorecard_dataframes'
        os.makedirs(output_dir, exist_ok=True)
        
        filename = self.images[self.current_image_idx].replace('.png', '_manual.csv')
        output_path = os.path.join(output_dir, filename)
        df.to_csv(output_path, index=False)
        
        print(f"✓ Saved {filename}")
        print(df)
        print()
        
    def save_and_exit(self):
        # Save current work
        if self.current_row:
            self.data.append(self.current_row)
        if self.data:
            self.save_current_scorecard()
            
        messagebox.showinfo("Complete", "All data saved to scorecard_dataframes/")
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()


def main():
    """Main entry point for manual scorecard extraction"""
    
    # Check if image directory exists
    if not os.path.exists('golfsc'):
        print("Error: 'golfsc' directory not found!")
        print("Please create the directory and add your scorecard images.")
        return
        
    images = [f for f in os.listdir('golfsc') if f.endswith('.png')]
    if not images:
        print("Error: No PNG images found in 'golfsc' directory!")
        return
        
    print(f"Found {len(images)} scorecard images")
    print("\nStarting manual extraction tool...")
    print("This tool allows you to manually enter the scorecard data.")
    print("\nTips:")
    print("- Enter values left to right, top to bottom")
    print("- Use '--' for missing values (they'll become NaN)")
    print("- Press Enter or click 'Next Cell' after each value")
    print("- Click 'Next Row' when you finish a row")
    print("- Click 'Next Image' when done with a scorecard")
    print()
    
    extractor = ScorecardExtractor()
    extractor.run()


if __name__ == '__main__':
    main()
