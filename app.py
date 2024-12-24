import pymysql
from PIL import Image, ImageDraw, ImageFont
import os

# Database connection details
db_config = {
    'host': 'localhost',      # Your MySQL host
    'user': 'root',           # MySQL username (root)
    'password': 'root',       # MySQL password
    'database': 'mpl'         # Database name
}

# Create the output directory if it doesn't exist
output_dir = './tmpo'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Connect to the database
try:
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    print("Database connected successfully.")
except pymysql.MySQLError as e:
    print(f"Error connecting to the database: {e}")
    exit(1)

# Query to get player_id, name, position, and photo path
query = "SELECT player_id, name, position, photo_path FROM players"
cursor.execute(query)

# Fetch all records
players = cursor.fetchall()

# Settings for overlay and font size
overlay_height_ratio = 0.15  # Height of the overlay box as 15% of the image height
font_size_ratio = 0.045  # Font size as 4.5% of the image height

# Font for writing text on image
try:
    font_path = "arialbd.ttf"  # Path to a bold font
    font = ImageFont.truetype(font_path, 20)  # Temporary size, resized per image
except IOError:
    print("Font 'arialbd.ttf' not found. Falling back to default font.")
    font = ImageFont.load_default()

# Process each player image
for player in players:
    player_id, name, position, photo_path = player

    if not os.path.exists(photo_path):
        print(f"Error: Image path '{photo_path}' does not exist.")
        continue

    try:
        with Image.open(photo_path) as img:
            img = img.convert("RGBA")  # Ensure image is in RGBA mode
            width, height = img.size

            # Overlay settings
            overlay_height = int(height * overlay_height_ratio)
            overlay_y_start = height - overlay_height
            overlay_color = (0, 0, 128, 180)  # Navy blue with transparency

            # Create overlay
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [(0, overlay_y_start), (width, height)], fill=overlay_color
            )

            # Merge overlay with the image
            img = Image.alpha_composite(img, overlay)

            # Font settings
            font_size = int(height * font_size_ratio)
            font = ImageFont.truetype(font_path, font_size)

            # Draw text
            draw = ImageDraw.Draw(img)
            text_color = "white"

            # Text settings
            text_name = name
            text_position = position
            text_y_spacing = 10  # Space between name and position

            # Calculate text positions
            bbox_name = draw.textbbox((0, 0), text_name, font=font)
            bbox_position = draw.textbbox((0, 0), text_position, font=font)

            name_width = bbox_name[2] - bbox_name[0]
            position_width = bbox_position[2] - bbox_position[0]

            name_x = (width - name_width) // 2
            position_x = (width - position_width) // 2
            name_y = overlay_y_start + (overlay_height // 4) - bbox_name[3] // 2
            position_y = name_y + bbox_name[3] + text_y_spacing

            # Draw text on image
            draw.text((name_x, name_y), text_name, font=font, fill=text_color)
            draw.text((position_x, position_y), text_position, font=font, fill=text_color)

            # Save the final image
            output_path = os.path.join(output_dir, f"{player_id}.png")
            img.convert("RGB").save(output_path, "PNG")
            print(f"Saved image for player {player_id} at {output_path}")

    except Exception as e:
        print(f"Error processing image for player {player_id}: {e}")

# Close database connection
cursor.close()
conn.close()
