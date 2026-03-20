import cv2
import numpy as np
import os

# ----------------------------
# SETTINGS
# ----------------------------
INPUT_IMAGE = "enemy_ally.png"   # rename your image to this, or change this filename
OUTPUT_DETECTED = "detected_output.png"
OUTPUT_FIX = "fix_output.png"
OUTPUT_FIXPLUS = "fixplus_output.png"

# Safer colours for Fix/Fix+
# OpenCV uses BGR, not RGB
ENEMY_FIX_COLOR = (0, 165, 255)   # orange
ALLY_FIX_COLOR = (255, 255, 0)    # cyan

# Marker settings
MARKER_RADIUS = 20
MARKER_OFFSET_Y = 35  # how far above the top of the box
MIN_CONTOUR_AREA = 500  # ignore tiny blobs/noise


# ----------------------------
# LOAD IMAGE
# ----------------------------
image = cv2.imread(INPUT_IMAGE)

if image is None:
    print(f"Could not find image: {INPUT_IMAGE}")
    print("Make sure the file is in the same folder as this script.")
    exit()

original = image.copy()
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


# ----------------------------
# COLOUR MASKS
# ----------------------------
# Red needs 2 HSV ranges because hue wraps around
lower_red1 = np.array([0, 80, 80])
upper_red1 = np.array([10, 255, 255])

lower_red2 = np.array([160, 80, 80])
upper_red2 = np.array([179, 255, 255])

red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
red_mask = cv2.bitwise_or(red_mask1, red_mask2)

# Green range
lower_green = np.array([35, 60, 60])
upper_green = np.array([90, 255, 255])
green_mask = cv2.inRange(hsv, lower_green, upper_green)

# Clean up masks a bit
kernel = np.ones((5, 5), np.uint8)
red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)


# ----------------------------
# FIND MAIN FIGURE
# ----------------------------
def get_main_blob(mask, name):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    valid_contours = [c for c in contours if cv2.contourArea(c) > MIN_CONTOUR_AREA]

    if not valid_contours:
        print(f"No valid {name} contour found.")
        return None

    largest = max(valid_contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    cx = x + w // 2
    cy = y + h // 2

    print(f"{name} found:")
    print(f"  x={x}, y={y}, w={w}, h={h}, centre=({cx}, {cy})")

    return {
        "contour": largest,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "cx": cx,
        "cy": cy
    }


enemy_data = get_main_blob(red_mask, "Enemy")
ally_data = get_main_blob(green_mask, "Ally")


# ----------------------------
# DRAW DETECTION OUTPUT
# ----------------------------
detected = original.copy()

def draw_detection_info(img, data, box_color, label):
    if data is None:
        return

    x, y, w, h = data["x"], data["y"], data["w"], data["h"]

    # Bounding box
    cv2.rectangle(img, (x, y), (x + w, y + h), box_color, 3)

    # Use estimated head point instead of full-box centre
    head_x = x + w // 2
    head_y = y + int(h * 0.18)

    cv2.circle(img, (head_x, head_y), 6, box_color, -1)

    # Label
    cv2.putText(img, label, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)


# ----------------------------
# CREATE FIX OUTPUT
# ----------------------------
fix = original.copy()

# Recolour the detected regions
fix[red_mask > 0] = ENEMY_FIX_COLOR
fix[green_mask > 0] = ALLY_FIX_COLOR

cv2.imwrite(OUTPUT_FIX, fix)


# ----------------------------
# CREATE FIX+ OUTPUT
# ----------------------------
fixplus = fix.copy()

def draw_marker(img, data, fill_color, text_label):
    if data is None:
        return

    x, y, w, h = data["x"], data["y"], data["w"], data["h"]
    cx = data["cx"]

    # Place marker above top centre of bounding box
    marker_x = x + w // 2
    marker_y = y + int(h * 0.42) - 20

    # Draw filled circle marker
    cv2.circle(img, (marker_x, marker_y), MARKER_RADIUS, fill_color, -1)

    # Black border for visibility
    cv2.circle(img, (marker_x, marker_y), MARKER_RADIUS, (0, 0, 0), 2)

    # Label in the marker
    cv2.putText(img, text_label,
                (marker_x - 8, marker_y + 7),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Optional line from marker to figure
    #cv2.line(img, (marker_x, marker_y + MARKER_RADIUS),
             #(marker_x, y), fill_color, 2)

draw_marker(fixplus, enemy_data, (0, 255, 255), "!")
draw_marker(fixplus, ally_data, (255, 255, 0), "+")

cv2.imwrite(OUTPUT_FIXPLUS, fixplus)

print("\nDone.")
print(f"Saved: {OUTPUT_DETECTED}")
print(f"Saved: {OUTPUT_FIX}")
print(f"Saved: {OUTPUT_FIXPLUS}")