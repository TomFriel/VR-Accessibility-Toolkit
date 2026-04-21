import base64
import cv2
import numpy as np
from daltonize.daltonize import daltonize

from config import (
    SATURATION_BOOST,
    VALUE_BOOST,
    MIN_CONTOUR_AREA,
    HEALTH_OUTLINE_THICKNESS_OUTER,
    HEALTH_OUTLINE_THICKNESS_INNER,
)

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