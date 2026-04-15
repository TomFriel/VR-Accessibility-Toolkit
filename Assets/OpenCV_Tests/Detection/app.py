import os
import base64

import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from daltonize.daltonize import daltonize

app = FastAPI()

# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENEMY_ICON_PATH = os.path.join(BASE_DIR, "icons", "enemy_icon.png")
ALLY_ICON_PATH = os.path.join(BASE_DIR, "icons", "ally_icon.png")
MINIMAP_ICON_PATH = os.path.join(BASE_DIR, "icons", "Minimap_Icon.png")

# =========================================================
# SETTINGS
# =========================================================

MIN_CONTOUR_AREA = 500
MINIMAP_MIN_CONTOUR_AREA = 40

# Enemy / Ally
ICON_SCALE_FACTOR = 0.4
CHEST_Y_RATIO = 0.28
ICON_CENTER_Y_FINE_ADJUST = 0

#Tritan manual adjustment
ALLY_ICON_Y_FINE_ADJUST_TRITAN = -2

# Health bar
HEALTH_PATTERN_SPACING = 14
HEALTH_PATTERN_THICKNESS = 2
HEALTH_OUTLINE_THICKNESS_OUTER = 5
HEALTH_OUTLINE_THICKNESS_INNER = 2

# Minimap
MINIMAP_ICON_SCALE_FACTOR = 1.7
MINIMAP_OUTLINE_THICKNESS_OUTER = 4
MINIMAP_OUTLINE_THICKNESS_INNER = 2

# Optional mild post boost after daltonization
SATURATION_BOOST = 1.15
VALUE_BOOST = 1.08

# Enemy / Ally post-fix colours (BGR)
ENEMY_POST_COLOR_DEUTAN = (0, 180, 255)   # orange
ENEMY_POST_COLOR_PROTAN = (0, 190, 255)   # orange-yellow
ENEMY_POST_COLOR_TRITAN = (0, 140, 255)   # deeper orange

ALLY_POST_COLOR_DEUTAN = (255, 220, 0)    # cyan-yellowish
ALLY_POST_COLOR_PROTAN = (255, 235, 0)    # cyan
ALLY_POST_COLOR_TRITAN = (255, 200, 80)   # cyan-warm

# Health-bar post-fix colours (BGR)
HEALTH_DANGER_DEUTAN = (0, 165, 255)      # orange
HEALTH_SAFE_DEUTAN = (255, 220, 0)        # cyan-yellowish

HEALTH_DANGER_PROTAN = (0, 180, 255)      # orange
HEALTH_SAFE_PROTAN = (255, 235, 0)        # cyan

HEALTH_DANGER_TRITAN = (0, 120, 255)      # orange-red
HEALTH_SAFE_TRITAN = (0, 210, 80)         # greenish-cyan

# Minimap post-fix colours (BGR)
MINIMAP_ENEMY_DEUTAN = (0, 180, 255)      # orange hostile
MINIMAP_ALLY_DEUTAN = (255, 220, 0)       # bright ally

MINIMAP_ENEMY_PROTAN = (0, 190, 255)
MINIMAP_ALLY_PROTAN = (255, 235, 0)

MINIMAP_ENEMY_TRITAN = (0, 150, 255)
MINIMAP_ALLY_TRITAN = (0, 220, 120)

REGION_BLEND_ALPHA = 0.95

# =========================================================
# GENERAL HELPERS
# =========================================================

def encode_image_to_base64(img):
    success, buffer = cv2.imencode(".png", img)
    if not success:
        return None
    return base64.b64encode(buffer).decode("utf-8")


def apply_daltonize_bgr(image_bgr, cvd_type):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_rgb_float = image_rgb.astype(np.float32) / 255.0

    fixed_rgb_float = daltonize(image_rgb_float, color_deficit=cvd_type)

    fixed_rgb = np.clip(fixed_rgb_float * 255.0, 0, 255).astype(np.uint8)
    fixed_bgr = cv2.cvtColor(fixed_rgb, cv2.COLOR_RGB2BGR)

    return fixed_bgr


def boost_image_appearance(image_bgr, sat_boost=SATURATION_BOOST, val_boost=VALUE_BOOST):
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)

    hsv[:, :, 1] *= sat_boost
    hsv[:, :, 2] *= val_boost

    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)

    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def recolour_detected_regions(base_bgr, red_mask, green_mask, enemy_color_bgr, ally_color_bgr, alpha=0.75):
    output = base_bgr.copy().astype(np.float32)

    enemy_color = np.full_like(output, enemy_color_bgr, dtype=np.float32)
    ally_color = np.full_like(output, ally_color_bgr, dtype=np.float32)

    red_bool = red_mask > 0
    green_bool = green_mask > 0

    output[red_bool] = (1.0 - alpha) * output[red_bool] + alpha * enemy_color[red_bool]
    output[green_bool] = (1.0 - alpha) * output[green_bool] + alpha * ally_color[green_bool]

    return np.clip(output, 0, 255).astype(np.uint8)


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

    return {
        "label": name.lower(),
        "x": int(x),
        "y": int(y),
        "w": int(w),
        "h": int(h),
        "cx": int(cx),
        "cy": int(cy)
    }


def draw_detection_info(img, data, box_color, label):
    if data is None:
        return

    x, y, w, h = data["x"], data["y"], data["w"], data["h"]

    cv2.rectangle(img, (x, y), (x + w, y + h), box_color, 3)

    head_x = x + w // 2
    head_y = y + int(h * 0.18)

    cv2.circle(img, (head_x, head_y), 6, box_color, -1)

    cv2.putText(
        img,
        label,
        (x, max(20, y - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        box_color,
        2
    )


def create_colour_masks(image_bgr):
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # RED
    lower_red1 = np.array([0, 80, 80])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 80, 80])
    upper_red2 = np.array([179, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # GREEN
    lower_green = np.array([35, 60, 60])
    upper_green = np.array([90, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((5, 5), np.uint8)

    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

    return red_mask, green_mask

def create_colour_masks_enemy_ally_tritan(image_bgr):
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # RED enemy
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # BLUE ally
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    kernel_small = np.ones((5, 5), np.uint8)
    kernel_big = np.ones((9, 9), np.uint8)

    # clean tiny noise
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel_small)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel_small)

    # thicken outlines
    red_mask = cv2.dilate(red_mask, kernel_big, iterations=1)
    blue_mask = cv2.dilate(blue_mask, kernel_big, iterations=1)

    # close gaps
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel_big)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel_big)

    blue_mask = cv2.erode(blue_mask, kernel_small, iterations=1)
    blue_mask = trim_bottom_of_mask(blue_mask, trim_ratio=0.12)

    # fill the largest contour so get_main_blob sees one solid body
    #red_mask = fill_largest_contour(red_mask)
    #blue_mask = fill_largest_contour(blue_mask)

    return red_mask, blue_mask   

def create_colour_masks_healthbar(image_bgr):

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # red mask
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    red_mask = red_mask1 | red_mask2

    # green mask
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    return red_mask, green_mask

def create_colour_masks_healthbar_red_blue(image_bgr):
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # RED danger region
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # BLUE safe region
    lower_blue = np.array([95, 120, 120])
    upper_blue = np.array([115, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    kernel_red = np.ones((5, 5), np.uint8)
    kernel_blue = np.ones((3, 3), np.uint8)

    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel_red)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel_red)

    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel_blue)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel_blue)

    blue_mask = cv2.erode(blue_mask, kernel_blue, iterations=1)

    return red_mask, blue_mask

def choose_best_healthbar_masks(image_bgr):
    red_mask_rg, green_mask_rg = create_colour_masks_healthbar(image_bgr)
    red_mask_by, green_mask_by = create_colour_masks_healthbar_tritan(image_bgr)

    rg_score = int(np.count_nonzero(red_mask_rg)) + int(np.count_nonzero(green_mask_rg))
    by_score = int(np.count_nonzero(red_mask_by)) + int(np.count_nonzero(green_mask_by))

    if by_score > rg_score:
        return red_mask_by, green_mask_by, "by"
    else:
        return red_mask_rg, green_mask_rg, "rg"

def create_colour_masks_minimap(image_bgr):
    """
    Slightly gentler cleanup for tiny minimap dots.
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 70, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 70, 70])
    upper_red2 = np.array([179, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    lower_green = np.array([35, 50, 50])
    upper_green = np.array([95, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((3, 3), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

    return red_mask, green_mask


def load_icon_with_alpha_fallback(path):
    print(f"Trying to load icon from: {path}")
    icon = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if icon is None:
        print(f"Could not load icon: {path}")
        return None

    if len(icon.shape) == 3 and icon.shape[2] == 4:
        return icon

    if len(icon.shape) == 3 and icon.shape[2] == 3:
        bgr = icon
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        alpha = np.where(gray > 15, 255, 0).astype(np.uint8)
        bgra = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = alpha
        return bgra

    return None


def tint_icon_bgra(icon_bgra, color_bgr):
    """
    Recolour the icon while preserving alpha.
    Useful when the source icon is too dark for the background.
    """
    if icon_bgra is None:
        return None

    tinted = icon_bgra.copy()

    alpha = tinted[:, :, 3] > 0
    tinted[:, :, 0][alpha] = color_bgr[0]
    tinted[:, :, 1][alpha] = color_bgr[1]
    tinted[:, :, 2][alpha] = color_bgr[2]

    return tinted


def overlay_icon(background_bgr, overlay_bgra, center_x, top_y, target_width):
    if overlay_bgra is None:
        return background_bgr

    oh, ow = overlay_bgra.shape[:2]
    if ow <= 0 or oh <= 0 or target_width <= 0:
        return background_bgr

    scale = target_width / float(ow)
    new_w = max(1, int(ow * scale))
    new_h = max(1, int(oh * scale))

    overlay_resized = cv2.resize(overlay_bgra, (new_w, new_h), interpolation=cv2.INTER_AREA)

    x = int(center_x - new_w / 2)
    y = int(top_y)

    h, w = background_bgr.shape[:2]

    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(w, x + new_w)
    y2 = min(h, y + new_h)

    if x1 >= x2 or y1 >= y2:
        return background_bgr

    ox1 = x1 - x
    oy1 = y1 - y
    ox2 = ox1 + (x2 - x1)
    oy2 = oy1 + (y2 - y1)

    overlay_crop = overlay_resized[oy1:oy2, ox1:ox2]

    alpha = overlay_crop[:, :, 3].astype(np.float32) / 255.0
    alpha = np.expand_dims(alpha, axis=2)

    overlay_rgb = overlay_crop[:, :, :3].astype(np.float32)
    background_crop = background_bgr[y1:y2, x1:x2].astype(np.float32)

    blended = alpha * overlay_rgb + (1.0 - alpha) * background_crop
    background_bgr[y1:y2, x1:x2] = blended.astype(np.uint8)

    return background_bgr


def draw_mask_outline(image_bgr, mask, color=(255, 255, 255), thickness=3, min_area=MIN_CONTOUR_AREA):
    output = image_bgr.copy()
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]

    if valid_contours:
        cv2.drawContours(output, valid_contours, -1, color, thickness)

    return output


def add_outlines_fixplusplus(image_bgr, masks):
    output = image_bgr.copy()

    for mask in masks:
        output = draw_mask_outline(output, mask, color=(0, 0, 0), thickness=HEALTH_OUTLINE_THICKNESS_OUTER)

    for mask in masks:
        output = draw_mask_outline(output, mask, color=(255, 255, 255), thickness=HEALTH_OUTLINE_THICKNESS_INNER)

    return output


# =========================================================
# ENEMY / ALLY HELPERS
# =========================================================

def get_chest_anchor(data):
    if data is None:
        return None

    chest_x = data["x"] + data["w"] // 2
    chest_y = data["y"] + int(data["h"] * CHEST_Y_RATIO) + ICON_CENTER_Y_FINE_ADJUST

    return int(chest_x), int(chest_y)


def add_icons_to_fixplus(image_bgr, enemy_data, ally_data, enemy_icon, ally_icon, ally_y_adjust=0):
    output = image_bgr.copy()

    if enemy_data is None:
        enemy_items = []
    elif isinstance(enemy_data, list):
        enemy_items = enemy_data
    else:
        enemy_items = [enemy_data]

    if ally_data is None:
        ally_items = []
    elif isinstance(ally_data, list):
        ally_items = ally_data
    else:
        ally_items = [ally_data]

    if enemy_icon is not None:
        for enemy in enemy_items:
            icon_width = max(20, int(enemy["w"] * ICON_SCALE_FACTOR))
            enemy_anchor = get_chest_anchor(enemy)

            if enemy_anchor is not None:
                chest_x, chest_y = enemy_anchor
                eh, ew = enemy_icon.shape[:2]
                icon_height = max(1, int(icon_width * (eh / float(ew))))
                icon_top_y = chest_y - (icon_height // 2)
                output = overlay_icon(output, enemy_icon, chest_x, icon_top_y, icon_width)

    if ally_icon is not None:
        for ally in ally_items:
            icon_width = max(20, int(ally["w"] * ICON_SCALE_FACTOR))
            cx, cy = ally["cx"], ally["cy"]

            ah, aw = ally_icon.shape[:2]
            icon_height = max(1, int(icon_width * (ah / float(aw))))
            icon_top_y = chest_y - (icon_height // 2) + ally_y_adjust

            output = overlay_icon(output, ally_icon, cx, icon_top_y, icon_width)

        return output

def overlay_icon_centered(base_bgr, icon_bgra, center_x, center_y, target_width):
    if icon_bgra is None:
        return base_bgr

    ih, iw = icon_bgra.shape[:2]
    if iw == 0 or ih == 0:
        return base_bgr

    scale = target_width / float(iw)
    target_height = max(1, int(ih * scale))

    top_y = int(center_y - (target_height // 2))

    return overlay_icon(base_bgr, icon_bgra, center_x, top_y, target_width)

def draw_icon_backing_circle(image_bgr, center_x, center_y, radius, color=(15, 15, 15)):
    output = image_bgr.copy()
    cv2.circle(output, (int(center_x), int(center_y)), int(radius), color, -1)
    return output    

def add_icons_to_fixplus_minimap(image_bgr, enemy_data, ally_data, enemy_icon, ally_icon):
    output = image_bgr.copy()

    if enemy_data is None:
        enemy_items = []
    elif isinstance(enemy_data, list):
        enemy_items = enemy_data
    else:
        enemy_items = [enemy_data]

    if enemy_icon is not None:
        for enemy in enemy_items:
            cx, cy = enemy["cx"], enemy["cy"]
            icon_width = max(28, int(max(enemy["w"], enemy["h"]) * 2.6))
            output = overlay_icon_centered(output, enemy_icon, cx, cy, icon_width)

    return output  

def fill_largest_contour(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return mask

    largest = max(contours, key=cv2.contourArea)

    filled = np.zeros_like(mask)
    cv2.drawContours(filled, [largest], -1, 255, thickness=cv2.FILLED)
    return filled

def trim_bottom_of_mask(mask, trim_ratio=0.12):
    trimmed = mask.copy()
    h, w = trimmed.shape[:2]
    cut_y = int(h * (1.0 - trim_ratio))
    trimmed[cut_y:h, :] = 0
    return trimmed    

# =========================================================
# HEALTH BAR HELPERS
# =========================================================

def add_diagonal_hatching_to_mask(image_bgr, mask, line_color=(255, 255, 255), spacing=14, thickness=2):
    output = image_bgr.copy()
    h, w = output.shape[:2]

    line_layer = np.zeros_like(output)

    for x0 in range(-h, w, spacing):
        pt1 = (x0, 0)
        pt2 = (x0 + h, h)
        cv2.line(line_layer, pt1, pt2, line_color, thickness)

    mask_3 = cv2.merge([mask, mask, mask])
    line_pixels = cv2.bitwise_and(line_layer, mask_3)

    keep = mask > 0
    output[keep] = np.where(line_pixels[keep] > 0, line_pixels[keep], output[keep])

    return output


def add_bar_divider(image_bgr, left_data, right_data, color=(255, 255, 255), thickness=3):
    output = image_bgr.copy()

    if left_data is None or right_data is None:
        return output

    divider_x = int((left_data["x"] + left_data["w"] + right_data["x"]) / 2)
    top_y = min(left_data["y"], right_data["y"])
    bottom_y = max(left_data["y"] + left_data["h"], right_data["y"] + right_data["h"])

    cv2.line(output, (divider_x, top_y), (divider_x, bottom_y), color, thickness)
    return output


def draw_bar_label(image_bgr, data, text, color=(255, 255, 255)):
    output = image_bgr.copy()

    if data is None:
        return output

    x, y, w, h = data["x"], data["y"], data["w"], data["h"]
    tx = x + max(8, int(w * 0.06))
    ty = y + int(h * 0.7)

    cv2.putText(
        output,
        text,
        (tx, ty),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        color,
        2,
        cv2.LINE_AA
    )
    return output


# =========================================================
# MINIMAP HELPERS
# =========================================================

def get_all_blobs(mask, label, min_area=MINIMAP_MIN_CONTOUR_AREA):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []

    for c in contours:
        area = cv2.contourArea(c)
        if area <= min_area:
            continue

        x, y, w, h = cv2.boundingRect(c)
        cx = x + w // 2
        cy = y + h // 2

        blobs.append({
            "label": label,
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h),
            "cx": int(cx),
            "cy": int(cy),
            "area": float(area)
        })

    return blobs


def draw_minimap_detection(img, blobs, color, label_prefix):
    output = img
    for i, b in enumerate(blobs):
        cv2.circle(output, (b["cx"], b["cy"]), max(4, b["w"] // 2), color, 2)
        cv2.putText(
            output,
            f"{label_prefix}{i+1}",
            (b["x"], max(20, b["y"] - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            1,
            cv2.LINE_AA
        )
    return output


def overlay_warning_icons_on_red_blobs(image_bgr, red_blobs, warning_icon):
    output = image_bgr.copy()

    if warning_icon is None:
        return output

    for blob in red_blobs:
        icon_width = max(18, int(max(blob["w"], blob["h"]) * MINIMAP_ICON_SCALE_FACTOR))

        ih, iw = warning_icon.shape[:2]
        icon_height = max(1, int(icon_width * (ih / float(iw))))
        top_y = blob["cy"] - (icon_height // 2)

        output = overlay_icon(output, warning_icon, blob["cx"], top_y, icon_width)

    return output


def add_minimap_outlines(image_bgr, red_mask, green_mask):
    output = image_bgr.copy()
    output = draw_mask_outline(output, red_mask, color=(0, 0, 0), thickness=MINIMAP_OUTLINE_THICKNESS_OUTER, min_area=MINIMAP_MIN_CONTOUR_AREA)
    output = draw_mask_outline(output, green_mask, color=(0, 0, 0), thickness=MINIMAP_OUTLINE_THICKNESS_OUTER, min_area=MINIMAP_MIN_CONTOUR_AREA)
    output = draw_mask_outline(output, red_mask, color=(255, 255, 255), thickness=MINIMAP_OUTLINE_THICKNESS_INNER, min_area=MINIMAP_MIN_CONTOUR_AREA)
    output = draw_mask_outline(output, green_mask, color=(255, 255, 255), thickness=MINIMAP_OUTLINE_THICKNESS_INNER, min_area=MINIMAP_MIN_CONTOUR_AREA)
    return output

def recolour_minimap_blobs_separate(image_bgr, red_blobs, green_blobs, enemy_color_bgr=None, ally_color_bgr=None):
    """
    Recolour minimap dots selectively.
    Pass None for a category if you want to leave it unchanged.
    """
    output = image_bgr.copy()

    if enemy_color_bgr is not None:
        for blob in red_blobs:
            cx, cy = blob["cx"], blob["cy"]
            radius = max(4, min(blob["w"], blob["h"]) // 2)
            cv2.circle(output, (cx, cy), radius, enemy_color_bgr, -1)

    if ally_color_bgr is not None:
        for blob in green_blobs:
            cx, cy = blob["cx"], blob["cy"]
            radius = max(4, min(blob["w"], blob["h"]) // 2)
            cv2.circle(output, (cx, cy), radius, ally_color_bgr, -1)

    return output    


# =========================================================
# TEMPLATE: ENEMY / ALLY
# =========================================================

def process_enemy_ally(image_bgr):
    original = image_bgr.copy()

    red_mask, green_mask = create_colour_masks_enemy_ally_tritan(original)

    enemy_data = get_main_blob(red_mask, "Enemy")
    ally_data = get_main_blob(green_mask, "Ally")

    detected = original.copy()
    draw_detection_info(detected, enemy_data, (0, 255, 255), "Enemy")
    draw_detection_info(detected, ally_data, (255, 255, 0), "Ally")

    enemy_icon = load_icon_with_alpha_fallback(ENEMY_ICON_PATH)
    ally_icon = load_icon_with_alpha_fallback(ALLY_ICON_PATH)

    enemy_icon = tint_icon_bgra(enemy_icon, (255, 255, 255))
    ally_icon = tint_icon_bgra(ally_icon, (255, 255, 255))

    fix_deutan = boost_image_appearance(apply_daltonize_bgr(original, "d"))
    fix_protan = boost_image_appearance(apply_daltonize_bgr(original, "p"))
    fix_tritan = boost_image_appearance(apply_daltonize_bgr(original, "t"))

    fix_deutan = recolour_detected_regions(
        fix_deutan, red_mask, green_mask,
        ENEMY_POST_COLOR_DEUTAN, ALLY_POST_COLOR_DEUTAN, REGION_BLEND_ALPHA
    )
    fix_protan = recolour_detected_regions(
        fix_protan, red_mask, green_mask,
        ENEMY_POST_COLOR_PROTAN, ALLY_POST_COLOR_PROTAN, REGION_BLEND_ALPHA
    )
    fix_tritan = recolour_detected_regions(
        fix_tritan, red_mask, green_mask,
        ENEMY_POST_COLOR_TRITAN, ALLY_POST_COLOR_TRITAN, REGION_BLEND_ALPHA
    )

    fixplus_deutan = add_icons_to_fixplus(fix_deutan, enemy_data, ally_data, enemy_icon, ally_icon)
    fixplus_protan = add_icons_to_fixplus(fix_protan, enemy_data, ally_data, enemy_icon, ally_icon)
    fixplus_tritan = add_icons_to_fixplus(
    fix_tritan,
    enemy_data,
    ally_data,
    enemy_icon,
    ally_icon,
    ally_y_adjust=ALLY_ICON_Y_FINE_ADJUST_TRITAN
)

    fixplusplus_deutan = add_outlines_fixplusplus(fixplus_deutan, [red_mask, green_mask])
    fixplusplus_protan = add_outlines_fixplusplus(fixplus_protan, [red_mask, green_mask])
    fixplusplus_tritan = add_outlines_fixplusplus(fixplus_tritan, [red_mask, green_mask])

    metadata = {"template": "enemy_ally", "objects": []}

    if enemy_data is not None:
        metadata["objects"].append(enemy_data)
    if ally_data is not None:
        metadata["objects"].append(ally_data)

    return {
        "detected": detected,

        "fix_deutan": fix_deutan,
        "fix_protan": fix_protan,
        "fix_tritan": fix_tritan,

        "fixplus_deutan": fixplus_deutan,
        "fixplus_protan": fixplus_protan,
        "fixplus_tritan": fixplus_tritan,

        "fixplusplus_deutan": fixplusplus_deutan,
        "fixplusplus_protan": fixplusplus_protan,
        "fixplusplus_tritan": fixplusplus_tritan,

        "metadata": metadata
    }

def get_marker_blobs(mask, min_area=40, max_area=600):

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    blobs = []

    for cnt in contours:

        area = cv2.contourArea(cnt)

        if min_area < area < max_area:

            x, y, w, h = cv2.boundingRect(cnt)

            blobs.append({
                "bbox": (x, y, w, h),
                "center": (x + w//2, y + h//2)
            })

    return blobs    


# =========================================================
# TEMPLATE: HEALTH BAR
# =========================================================

def process_health_bar(image_bgr):
    original = image_bgr.copy()

    # Detect the two health bar regions for this poster:
    # danger = red, safe = blue
    danger_mask, safe_mask = create_colour_masks_healthbar_red_blue(original)

    danger_data = get_main_blob(danger_mask, "Danger")
    safe_data = get_main_blob(safe_mask, "Safe")

    detected = original.copy()
    draw_detection_info(detected, danger_data, (0, 255, 255), "Danger")
    draw_detection_info(detected, safe_data, (255, 255, 0), "Safe")

    fix_deutan = boost_image_appearance(apply_daltonize_bgr(original, "d"))
    fix_protan = boost_image_appearance(apply_daltonize_bgr(original, "p"))
    fix_tritan = boost_image_appearance(apply_daltonize_bgr(original, "t"))

    fix_deutan = recolour_detected_regions(
        fix_deutan, danger_mask, safe_mask,
        HEALTH_DANGER_DEUTAN, HEALTH_SAFE_DEUTAN, REGION_BLEND_ALPHA
    )

    fix_protan = recolour_detected_regions(
        fix_protan, danger_mask, safe_mask,
        HEALTH_DANGER_PROTAN, HEALTH_SAFE_PROTAN, REGION_BLEND_ALPHA
    )

    fix_tritan = recolour_detected_regions(
        fix_tritan, danger_mask, safe_mask,
        HEALTH_DANGER_TRITAN, HEALTH_SAFE_TRITAN, REGION_BLEND_ALPHA
    )

    fixplus_deutan = add_diagonal_hatching_to_mask(
        fix_deutan, danger_mask,
        line_color=(255, 255, 255),
        spacing=HEALTH_PATTERN_SPACING,
        thickness=HEALTH_PATTERN_THICKNESS
    )

    fixplus_protan = add_diagonal_hatching_to_mask(
        fix_protan, danger_mask,
        line_color=(255, 255, 255),
        spacing=HEALTH_PATTERN_SPACING,
        thickness=HEALTH_PATTERN_THICKNESS
    )

    fixplus_tritan = add_diagonal_hatching_to_mask(
        fix_tritan, danger_mask,
        line_color=(255, 255, 255),
        spacing=HEALTH_PATTERN_SPACING,
        thickness=HEALTH_PATTERN_THICKNESS
    )

    fixplusplus_deutan = add_outlines_fixplusplus(fixplus_deutan, [danger_mask, safe_mask])
    fixplusplus_protan = add_outlines_fixplusplus(fixplus_protan, [danger_mask, safe_mask])
    fixplusplus_tritan = add_outlines_fixplusplus(fixplus_tritan, [danger_mask, safe_mask])

    metadata = {"template": "health_bar", "objects": []}

    if danger_data is not None:
        metadata["objects"].append(danger_data)
    if safe_data is not None:
        metadata["objects"].append(safe_data)

    return {
        "detected": detected,

        "fix_deutan": fix_deutan,
        "fix_protan": fix_protan,
        "fix_tritan": fix_tritan,

        "fixplus_deutan": fixplus_deutan,
        "fixplus_protan": fixplus_protan,
        "fixplus_tritan": fixplus_tritan,

        "fixplusplus_deutan": fixplusplus_deutan,
        "fixplusplus_protan": fixplusplus_protan,
        "fixplusplus_tritan": fixplusplus_tritan,

        "metadata": metadata
    }


# =========================================================
# TEMPLATE: MINIMAP
# =========================================================

def process_minimap(image_bgr):
    """
    Minimap / radar logic:
    - Detect red and green dots as separate blobs.
    - FIX: recolour each dot to safer tones, keeping them tight and small.
    - FIX+: overlay a solid minimap warning icon on hostile red dots only.
    - FIX++: add outlines to improve contrast.
    """
    original = image_bgr.copy()

    red_mask, green_mask = create_colour_masks_minimap(original)

    red_blobs = get_all_blobs(red_mask, "enemy", min_area=MINIMAP_MIN_CONTOUR_AREA)
    green_blobs = get_all_blobs(green_mask, "ally", min_area=MINIMAP_MIN_CONTOUR_AREA)

    detected = original.copy()
    detected = draw_minimap_detection(detected, red_blobs, (0, 255, 255), "E")
    detected = draw_minimap_detection(detected, green_blobs, (255, 255, 0), "A")

    # Load minimap-specific solid icon
    minimap_icon = load_icon_with_alpha_fallback(MINIMAP_ICON_PATH)

    # FIX = recolour both enemy and ally dots
    fix_deutan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        MINIMAP_ENEMY_DEUTAN, MINIMAP_ALLY_DEUTAN
    )
    fix_protan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        MINIMAP_ENEMY_PROTAN, MINIMAP_ALLY_PROTAN
    )
    fix_tritan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        MINIMAP_ENEMY_TRITAN, MINIMAP_ALLY_TRITAN
    )

    # FIX+ = recolour ally dots only, leave enemy dots unchanged, then overlay enemy warning icons
    fixplus_base_deutan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        None, MINIMAP_ALLY_DEUTAN
    )
    fixplus_base_protan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        None, MINIMAP_ALLY_PROTAN
    )
    fixplus_base_tritan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        None, MINIMAP_ALLY_TRITAN
    )

    fixplus_deutan = add_icons_to_fixplus_minimap(
        fixplus_base_deutan,
        red_blobs,
        None,
        minimap_icon,
        None
    )

    fixplus_protan = add_icons_to_fixplus_minimap(
        fixplus_base_protan,
        red_blobs,
        None,
        minimap_icon,
        None
    )

    fixplus_tritan = add_icons_to_fixplus_minimap(
        fixplus_base_tritan,
        red_blobs,
        None,
        minimap_icon,
        None
    )

    # FIX++
    fixplusplus_deutan = add_minimap_outlines(fixplus_deutan, red_mask, green_mask)
    fixplusplus_protan = add_minimap_outlines(fixplus_protan, red_mask, green_mask)
    fixplusplus_tritan = add_minimap_outlines(fixplus_tritan, red_mask, green_mask)

    metadata = {"template": "minimap", "objects": []}
    metadata["objects"].extend(red_blobs)
    metadata["objects"].extend(green_blobs)

    return {
        "detected": detected,

        "fix_deutan": fix_deutan,
        "fix_protan": fix_protan,
        "fix_tritan": fix_tritan,

        "fixplus_deutan": fixplus_deutan,
        "fixplus_protan": fixplus_protan,
        "fixplus_tritan": fixplus_tritan,

        "fixplusplus_deutan": fixplusplus_deutan,
        "fixplusplus_protan": fixplusplus_protan,
        "fixplusplus_tritan": fixplusplus_tritan,

        "metadata": metadata
    }


# =========================================================
# API
# =========================================================

@app.get("/")
def root():
    return {"message": "OpenCV poster API is running"}


@app.post("/generate")
async def generate(
    file: UploadFile = File(...),
    template_type: str = Form("enemy_ally")
):
    try:
        file_bytes = await file.read()
        np_arr = np.frombuffer(file_bytes, np.uint8)
        image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image_bgr is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not decode uploaded image."}
            )

        if template_type == "enemy_ally":
            outputs = process_enemy_ally(image_bgr)
        elif template_type == "health_bar":
            outputs = process_health_bar(image_bgr)
        elif template_type == "minimap":
            outputs = process_minimap(image_bgr)
        else:
            return JSONResponse(
                status_code=400,
                content={"error": f"Unsupported template_type: {template_type}"}
            )

        return {
            "template_type": template_type,
            "detected_base64": encode_image_to_base64(outputs["detected"]),

            "fix_deutan_base64": encode_image_to_base64(outputs["fix_deutan"]),
            "fix_protan_base64": encode_image_to_base64(outputs["fix_protan"]),
            "fix_tritan_base64": encode_image_to_base64(outputs["fix_tritan"]),

            "fixplus_deutan_base64": encode_image_to_base64(outputs["fixplus_deutan"]),
            "fixplus_protan_base64": encode_image_to_base64(outputs["fixplus_protan"]),
            "fixplus_tritan_base64": encode_image_to_base64(outputs["fixplus_tritan"]),

            "fixplusplus_deutan_base64": encode_image_to_base64(outputs["fixplusplus_deutan"]),
            "fixplusplus_protan_base64": encode_image_to_base64(outputs["fixplusplus_protan"]),
            "fixplusplus_tritan_base64": encode_image_to_base64(outputs["fixplusplus_tritan"]),

            "metadata": outputs["metadata"]
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )