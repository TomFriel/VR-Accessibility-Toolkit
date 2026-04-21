import cv2
import numpy as np

from config import (
    HEALTH_PATTERN_SPACING,
    HEALTH_PATTERN_THICKNESS,
    HEALTH_DANGER_DEUTAN,
    HEALTH_SAFE_DEUTAN,
    HEALTH_DANGER_PROTAN,
    HEALTH_SAFE_PROTAN,
    HEALTH_DANGER_TRITAN,
    HEALTH_SAFE_TRITAN,
    REGION_BLEND_ALPHA,
)

from detection import (
    create_colour_masks_healthbar_red_blue,
    get_main_blob,
    draw_detection_info,
)

from utils import (
    apply_daltonize_bgr,
    boost_image_appearance,
    recolour_detected_regions,
    add_outlines_fixplusplus,
)

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


def process_health_bar(image_bgr):
    original = image_bgr.copy()

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