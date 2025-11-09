#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to create sample scorecard images for testing OCR
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_scorecard(filename, player_data):
    """Create a sample scorecard image"""
    # Image dimensions
    width, height = 800, 600
    
    # Create white background
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
    
    # Draw title
    draw.text((300, 20), "GAME SCORECARD", fill='black', font=font_title)
    
    # Draw table headers
    y_pos = 80
    draw.rectangle([(50, y_pos), (750, y_pos + 30)], outline='black', width=2)
    draw.text((60, y_pos + 5), "Player", fill='black', font=font_header)
    draw.text((250, y_pos + 5), "Score", fill='black', font=font_header)
    draw.text((350, y_pos + 5), "Assists", fill='black', font=font_header)
    draw.text((450, y_pos + 5), "Rebounds", fill='black', font=font_header)
    draw.text((580, y_pos + 5), "Team", fill='black', font=font_header)
    
    # Draw horizontal lines
    for i in range(len(player_data) + 1):
        y = y_pos + 30 + (i * 40)
        draw.line([(50, y), (750, y)], fill='black', width=1)
    
    # Draw vertical lines
    x_positions = [50, 240, 340, 440, 570, 750]
    for x in x_positions:
        draw.line([(x, y_pos), (x, y_pos + 30 + len(player_data) * 40)], fill='black', width=1)
    
    # Draw player data
    for i, (player, score, assists, rebounds, team) in enumerate(player_data):
        y = y_pos + 35 + (i * 40)
        draw.text((60, y), player, fill='black', font=font_text)
        draw.text((260, y), str(score), fill='black', font=font_text)
        draw.text((360, y), str(assists), fill='black', font=font_text)
        draw.text((470, y), str(rebounds), fill='black', font=font_text)
        draw.text((580, y), team, fill='black', font=font_text)
    
    # Save image
    img.save(filename)
    print(f"Created {filename}")

# Sample data for different scorecards
scorecards_data = [
    [  # 000_scorecard_0.png
        ("John Smith", 28, 5, 12, "Lakers"),
        ("Mike Johnson", 15, 8, 6, "Lakers"),
        ("Tom Davis", 22, 3, 9, "Lakers"),
        ("Chris Brown", 18, 6, 7, "Warriors"),
        ("David Wilson", 25, 4, 11, "Warriors"),
    ],
    [  # 001_scorecard_0.png
        ("Sarah Jones", 32, 7, 8, "Storm"),
        ("Lisa Miller", 19, 9, 5, "Storm"),
        ("Emma Taylor", 24, 5, 10, "Storm"),
        ("Amy Anderson", 21, 6, 7, "Mystics"),
        ("Kate Thomas", 27, 4, 9, "Mystics"),
    ],
    [  # 002_scorecard_0.png
        ("Alex Garcia", 30, 8, 6, "Heat"),
        ("Ryan Martinez", 16, 4, 11, "Heat"),
        ("Kevin Lopez", 23, 6, 8, "Heat"),
        ("Brian Lee", 20, 5, 9, "Celtics"),
        ("Jason White", 26, 7, 7, "Celtics"),
    ],
    [  # 003_scorecard_0.png
        ("Mark Harris", 29, 6, 10, "Bulls"),
        ("Paul Clark", 17, 8, 5, "Bulls"),
        ("Steve Lewis", 22, 4, 12, "Bulls"),
        ("Dan Walker", 19, 7, 6, "Knicks"),
        ("Jim Hall", 25, 5, 9, "Knicks"),
    ],
    [  # 004_scorecard_0.png
        ("Peter Young", 31, 9, 7, "Nets"),
        ("Robert King", 18, 5, 10, "Nets"),
        ("William Wright", 24, 6, 8, "Nets"),
        ("James Scott", 21, 7, 6, "Spurs"),
        ("Charles Green", 28, 4, 11, "Spurs"),
    ],
    [  # 005_scorecard_0.png
        ("Richard Adams", 27, 8, 9, "Suns"),
        ("Thomas Baker", 20, 6, 7, "Suns"),
        ("Daniel Nelson", 23, 5, 10, "Suns"),
        ("Matthew Carter", 19, 7, 6, "Mavs"),
        ("Joseph Mitchell", 26, 4, 8, "Mavs"),
    ],
    [  # 006_scorecard_0.png
        ("Andrew Perez", 33, 10, 5, "Rockets"),
        ("Joshua Roberts", 16, 4, 12, "Rockets"),
        ("Ryan Turner", 25, 7, 8, "Rockets"),
        ("Nicholas Phillips", 22, 5, 9, "Jazz"),
        ("Tyler Campbell", 29, 6, 7, "Jazz"),
    ],
    [  # 007_scorecard_0.png
        ("Brandon Parker", 28, 8, 10, "Blazers"),
        ("Aaron Evans", 19, 6, 6, "Blazers"),
        ("Eric Edwards", 24, 5, 11, "Blazers"),
        ("Adam Collins", 21, 7, 7, "Nuggets"),
        ("Jack Stewart", 27, 4, 9, "Nuggets"),
    ],
    [  # 008_scorecard_0.png
        ("Justin Morris", 30, 9, 8, "Clippers"),
        ("Samuel Rogers", 17, 5, 10, "Clippers"),
        ("Kyle Reed", 23, 6, 7, "Clippers"),
        ("Sean Cook", 20, 7, 9, "Grizzlies"),
        ("Nathan Morgan", 26, 4, 6, "Grizzlies"),
    ],
    [  # 009_scorecard_0.png
        ("Carl Bell", 31, 8, 11, "Pelicans"),
        ("Keith Murphy", 18, 6, 5, "Pelicans"),
        ("Gerald Bailey", 25, 5, 9, "Pelicans"),
        ("Lawrence Rivera", 22, 7, 8, "Magic"),
        ("Dennis Cooper", 28, 4, 10, "Magic"),
    ],
    [  # 0010_scorecard_0.png
        ("Randy Richardson", 29, 9, 7, "Pistons"),
        ("Albert Cox", 19, 5, 11, "Pistons"),
        ("Harold Howard", 24, 6, 6, "Pistons"),
        ("Eugene Ward", 21, 7, 9, "Hornets"),
        ("Howard Torres", 27, 4, 8, "Hornets"),
    ],
]

# Create directory for scorecards if it doesn't exist
os.makedirs("/home/runner/work/XTBApi/XTBApi/scorecards", exist_ok=True)

# Generate all scorecards
for i, data in enumerate(scorecards_data):
    if i < 10:
        filename = f"/home/runner/work/XTBApi/XTBApi/scorecards/00{i}_scorecard_0.png"
    else:
        filename = f"/home/runner/work/XTBApi/XTBApi/scorecards/0{i}_scorecard_0.png"
    create_scorecard(filename, data)

print("\nAll scorecards created successfully!")
