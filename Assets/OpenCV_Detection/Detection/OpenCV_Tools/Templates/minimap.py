import cv2

from config import (
    MINIMAP_ICON_PATH,
    MINIMAP_ICON_SCALE_FACTOR,
    MINIMAP_OUTLINE_THICKNESS_OUTER,
    MINIMAP_OUTLINE_THICKNESS_INNER,
    MINIMAP_MIN_CONTOUR_AREA,
    MINIMAP_ENEMY_DEUTAN,
    MINIMAP_ALLY_DEUTAN,
    MINIMAP_ENEMY_PROTAN,
    MINIMAP_ALLY_PROTAN,
    MINIMAP_ENEMY_TRITAN,
    MINIMAP_ALLY_TRITAN,
)

from detection import (
    create_colour_masks_minimap,
    get_all_blobs,
    draw_minimap_detection,
)

from utils import (
    load_icon_with_alpha_fallback,
    overlay_icon,
    overlay_icon_centered,
    draw_mask_outline,
)

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


def process_minimap(image_bgr):
    original = image_bgr.copy()

    red_mask, green_mask = create_colour_masks_minimap(original)

    red_blobs = get_all_blobs(red_mask, "enemy", min_area=MINIMAP_MIN_CONTOUR_AREA)
    green_blobs = get_all_blobs(green_mask, "ally", min_area=MINIMAP_MIN_CONTOUR_AREA)

    detected = original.copy()
    detected = draw_minimap_detection(detected, red_blobs, (0, 255, 255), "E")
    detected = draw_minimap_detection(detected, green_blobs, (255, 255, 0), "A")

    minimap_icon = load_icon_with_alpha_fallback(MINIMAP_ICON_PATH)

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