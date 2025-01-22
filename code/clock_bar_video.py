import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip

# Video settings
WIDTH = 1280
HEIGHT = 720
DURATION = 60  # seconds
FPS = 30

# Font settings (change path to a valid .ttf on your system)
FONT_PATH = "C:/Windows/Fonts/Calibri.ttf"
FONT_SIZE = 80
TEXT_COLOR = (255, 255, 255)  # white

# Bar settings
BAR_COLOR = (255, 255, 255)   # white
BAR_WIDTH = 50
BAR_HEIGHT = 50
BAR_X = 200  # Horizontal position of the bar
# We'll move the bar down every 10 seconds by 80 pixels,
# starting from an initial offset (e.g., 200 px from top).
#BAR_OFFSET_Y = 200
#BAR_STEP = 80  # how many pixels to move every 10s

# The bar will toggle between two Y positions:
BAR_INIT_Y = 300      # "down" / initial position
BAR_UP_Y = 150        # "up" position

# Load a TrueType font
font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

def make_frame(t):
    """
    Generate a single frame at time t (in seconds).
    Returns a HxWx3 (RGB) NumPy array.
    """
    # 1. Create a black image (Pillow expects (width, height))
    img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))

    draw = ImageDraw.Draw(img)

    # 2. Draw current time (integer seconds)
    current_second = int(t)  # floor of t
    time_text = str(current_second)
    # Choose where to place the text
    # (e.g., 50 px from left, 50 px from top)
    text_x, text_y = (50, 50)
    draw.text((text_x, text_y), time_text, font=font, fill=TEXT_COLOR)

    # 3. Compute the bar’s vertical position
    #    Moves down every 10 seconds by BAR_STEP pixels.
    #    Example: t in [0..9] => bar_index=0 => y=BAR_OFFSET_Y
    #             t in [10..19] => bar_index=1 => y=BAR_OFFSET_Y + BAR_STEP
    #bar_index = current_second // 10  # integer division by 10
    #bar_y = BAR_OFFSET_Y + bar_index * BAR_STEP

    # 3. Determine bar position
    #    Every 10 seconds, we toggle between two positions.
    #    0..9s -> bar_index=0 -> bar at BAR_INIT_Y
    #    10..19s -> bar_index=1 -> bar at BAR_UP_Y
    #    20..29s -> bar_index=2 -> bar_index % 2=0 -> back to BAR_INIT_Y
    #    30..39s -> bar_index=3 -> bar_index % 2=1 -> BAR_UP_Y
    #    etc.
    bar_index = (current_second // 10) % 2
    if bar_index == 0:
        bar_y = BAR_INIT_Y
    else:
        bar_y = BAR_UP_Y



    # 4. Draw the white bar (rectangle) at (BAR_X, bar_y)
    #bar_coords = [
    #    (BAR_X, bar_y),
    #    (BAR_X + BAR_WIDTH, bar_y + BAR_HEIGHT)
    #]

    bar_coords = [(BAR_X, bar_y), (BAR_X + BAR_WIDTH, bar_y + BAR_HEIGHT)]
    draw.rectangle(bar_coords, fill=BAR_COLOR)

    # 5. Convert Pillow image to NumPy array (H x W x 3)
    frame = np.array(img)
    return frame

# Create the VideoClip with our make_frame function
clip = VideoClip(make_frame, duration=DURATION)

# Set the frames per second and write the output video
clip.write_videofile("clock_bar_video.mp4", fps=FPS)