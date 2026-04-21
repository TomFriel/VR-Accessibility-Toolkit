import cv2

from config import (
    ENEMY_ICON_PATH,
    ALLY_ICON_PATH,
    ICON_SCALE_FACTOR,
    CHEST_Y_RATIO,
    ICON_CENTER_Y_FINE_ADJUST,
    ALLY_ICON_Y_FINE_ADJUST_TRITAN,
    ENEMY_POST_COLOR_DEUTAN,
    ENEMY_POST_COLOR_PROTAN,
    ENEMY_POST_COLOR_TRITAN,
    ALLY_POST_COLOR_DEUTAN,
    ALLY_POST_COLOR_PROTAN,
    ALLY_POST_COLOR_TRITAN,
    REGION_BLEND_ALPHA,
)

from detection import (
    create_colour_masks_enemy_ally_tritan,
    get_main_blob,
    draw_detection_info,
)

from utils import (
    apply_daltonize_bgr,
    boost_image_appearance,
    recolour_detected_regions,
    load_icon_with_alpha_fallback,
    tint_icon_bgra,
    overlay_icon,
    add_outlines_fixplusplus,
)

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
            ally_anchor = get_chest_anchor(ally)

            if ally_anchor is not None:
                chest_x, chest_y = ally_anchor
                ah, aw = ally_icon.shape[:2]
                icon_height = max(1, int(icon_width * (ah / float(aw))))
                icon_top_y = chest_y - (icon_height // 2) + ally_y_adjust
                output = overlay_icon(output, ally_icon, chest_x, icon_top_y, icon_width)

    return output


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