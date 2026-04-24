"""
COLOR VISION DEFICIENCY ACCESSIBILITY PROCESSOR
==============================================
Processes game UI elements to make them accessible to people with color vision deficiencies.

Main Features:
  - Detects colored UI elements (enemy/ally, minimap, health bars)
  - Generates three accessibility levels:
    * FIX: Daltonize + recolor detected regions
    * FIX+: FIX + add visual indicators (icons, patterns)
    * FIX++: FIX+ + add outlines for maximum contrast
  - Supports three CVD types: Deuteranopia, Protanopia, Tritanopia
  - Returns detection metadata for game integration
"""

# ============================================================================
# IMPORTS
# ============================================================================
# Color detection and image processing
from detection import (
    create_colour_masks_enemy_ally_tritan,
    create_colour_masks_minimap,
    create_colour_masks_healthbar_red_blue,
    get_main_blob,
    get_all_blobs,
    draw_detection_info,
    draw_minimap_detection
)

# Icon and visual enhancement utilities
from visual_enhancements import (
    load_icon_with_alpha_fallback,
    tint_icon_bgra,
    add_icons_to_fixplus,
    add_icons_to_fixplus_minimap,
    add_diagonal_hatching_to_mask,
    add_outlines_fixplusplus,
    add_minimap_outlines
)

# Color correction and recoloring
from color_correction import (
    apply_daltonize_bgr,
    boost_image_appearance,
    recolour_detected_regions,
    recolour_minimap_blobs_separate
)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================
# Icon paths
ENEMY_ICON_PATH = "path/to/enemy_icon.png"
ALLY_ICON_PATH = "path/to/ally_icon.png"
MINIMAP_ICON_PATH = "path/to/minimap_icon.png"

# Enemy/Ally detection colors (RGB)
ENEMY_POST_COLOR_DEUTAN = (255, 100, 0)   # Orange for deuteranopia
ALLY_POST_COLOR_DEUTAN = (50, 150, 255)   # Blue for deuteranopia
ENEMY_POST_COLOR_PROTAN = (255, 100, 0)   # Orange for protanopia
ALLY_POST_COLOR_PROTAN = (50, 150, 255)   # Blue for protanopia
ENEMY_POST_COLOR_TRITAN = (255, 100, 0)   # Orange for tritanopia
ALLY_POST_COLOR_TRITAN = (50, 150, 255)   # Blue for tritanopia

# Health bar colors
HEALTH_DANGER_DEUTAN = (255, 100, 0)      # Orange for danger
HEALTH_SAFE_DEUTAN = (50, 150, 255)       # Blue for safe
HEALTH_DANGER_PROTAN = (255, 100, 0)
HEALTH_SAFE_PROTAN = (50, 150, 255)
HEALTH_DANGER_TRITAN = (255, 100, 0)
HEALTH_SAFE_TRITAN = (50, 150, 255)

# Minimap colors
MINIMAP_ENEMY_DEUTAN = (255, 100, 0)      # Orange for enemies
MINIMAP_ALLY_DEUTAN = (50, 150, 255)      # Blue for allies
MINIMAP_ENEMY_PROTAN = (255, 100, 0)
MINIMAP_ALLY_PROTAN = (50, 150, 255)
MINIMAP_ENEMY_TRITAN = (255, 100, 0)
MINIMAP_ALLY_TRITAN = (50, 150, 255)

# Visual parameters
REGION_BLEND_ALPHA = 0.7                  # Blend factor for recoloring regions
HEALTH_PATTERN_SPACING = 8                # Diagonal line spacing
HEALTH_PATTERN_THICKNESS = 2              # Diagonal line thickness
ALLY_ICON_Y_FINE_ADJUST_TRITAN = -5       # Y offset adjustment for tritanopia

MINIMAP_MIN_CONTOUR_AREA = 50             # Minimum blob size on minimap


def process_enemy_ally(image_bgr):
    """
    Process enemy/ally detection poster with accessibility enhancements.
    
    PSEUDOCODE:
    1. Create color masks for red (enemy) and green (ally)
    2. Detect largest blob for each team
    3. Apply daltonize correction for each CVD type
    4. Recolor detected regions to accessibility colors
    5. FIX+: Add icon overlays at detected positions
    6. FIX++: Add outlines for contrast enhancement
    7. Return all versions + detection metadata
    """
    # Keep copy of original for reference
    original = image_bgr.copy()

    # STEP 1: Detect red (enemy) and green (ally) regions
    red_mask, green_mask = create_colour_masks_enemy_ally_tritan(original)

    # STEP 2: Extract the main blob for enemy and ally
    enemy_data = get_main_blob(red_mask, "Enemy")
    ally_data = get_main_blob(green_mask, "Ally")

    # STEP 3: Create detection visualization
    detected = original.copy()
    draw_detection_info(detected, enemy_data, (0, 255, 255), "Enemy")  # Cyan
    draw_detection_info(detected, ally_data, (255, 255, 0), "Ally")    # Yellow

    # STEP 4: Load and prepare icons for FIX+ overlay
    enemy_icon = load_icon_with_alpha_fallback(ENEMY_ICON_PATH)
    ally_icon = load_icon_with_alpha_fallback(ALLY_ICON_PATH)

    # Tint icons to white for visibility
    enemy_icon = tint_icon_bgra(enemy_icon, (255, 255, 255))
    ally_icon = tint_icon_bgra(ally_icon, (255, 255, 255))

    # STEP 5: Generate FIX versions (daltonize + recolor for each CVD type)
    # Deuteranopia (green-blind) corrections
    fix_deutan = boost_image_appearance(apply_daltonize_bgr(original, "d"))
    # Protanopia (red-blind) corrections
    fix_protan = boost_image_appearance(apply_daltonize_bgr(original, "p"))
    # Tritanopia (blue-yellow) corrections
    fix_tritan = boost_image_appearance(apply_daltonize_bgr(original, "t"))

    # Recolor detected enemy/ally regions with accessible colors
    fix_deutan = recolour_detected_regions(
        fix_deutan, red_mask, green_mask,
        ENEMY_POST_COLOR_DEUTAN, ALLY_POST_COLOR_DEUTAN, REGION_BLEND_ALPHA
    )

    # STEP 6: Generate FIX+ versions (FIX + add icon overlays)

    # STEP 7: Generate FIX++ versions (FIX+ + add outlines for maximum contrast)
    fixplusplus_deutan = add_outlines_fixplusplus(fixplus_deutan, [red_mask, green_mask])
    fixplusplus_protan = add_outlines_fixplusplus(fixplus_protan, [red_mask, green_mask])
    fixplusplus_tritan = add_outlines_fixplusplus(fixplus_tritan, [red_mask, green_mask])

    # STEP 8: Compile detection metadata for game integration
    metadata = {"template": "enemy_ally", "objects": []}  # Detected objects

    # Add detected objects to metadata
    if enemy_data is not None:
        metadata["objects"].append(enemy_data)
    if ally_data is not None:
        metadata["objects"].append(ally_data)

    # STEP 9: Return all versions (original, FIX, FIX+, FIX++) plus metadata
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

    # STEP 5: Generate FIX versions (recolor both enemy and ally dots)
    # Deuteranopia: recolor both teams
    fix_deutan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        MINIMAP_ENEMY_DEUTAN, MINIMAP_ALLY_DEUTAN
    )
    # Protanopia: recolor both teams
    fix_protan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        MINIMAP_ENEMY_PROTAN, MINIMAP_ALLY_PROTAN
    )
    # Tritanopia: recolor both teams
    fix_tritan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        MINIMAP_ENEMY_TRITAN, MINIMAP_ALLY_TRITAN
    )

    # STEP 6: Generate FIX+ base (recolor allies only, leave enemies unchanged)
    # Strategy: Pass None for enemy color to preserve original red, recolor allies
    fixplus_base_deutan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        None, MINIMAP_ALLY_DEUTAN  # None = don't recolor enemies
    )
    fixplus_base_protan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        None, MINIMAP_ALLY_PROTAN
    )
    fixplus_base_tritan = recolour_minimap_blobs_separate(
        original, red_blobs, green_blobs,
        None, MINIMAP_ALLY_TRITAN
    )

    # Add warning icons overlay to FIX+ (only on enemy dots)
    fixplus_deutan = add_icons_to_fixplus_minimap(
        fixplus_base_deutan,
        red_blobs,       # Enemy blobs
        None,            # No ally icons
        minimap_icon,    # Enemy warning icon
        None             # No ally icon
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

    # STEP 7: Generate FIX++ versions (FIX+ + add outlines for contrast)
    fixplusplus_deutan = add_minimap_outlines(fixplus_deutan, red_mask, green_mask)
    fixplusplus_protan = add_minimap_outlines(fixplus_protan, red_mask, green_mask)
    fixplusplus_tritan = add_minimap_outlines(fixplus_tritan, red_mask, green_mask)

    # STEP 8: Compile detection metadata with all detected blobs
    metadata = {"template": "minimap", "objects": []}
    # Add all enemy and ally blobs to metadata
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

def process_health_bar(image_bgr):
    """
    Process health bar detection with accessibility enhancements.
    
    PSEUDOCODE:
    1. Create color masks for red (danger) and blue (safe) regions
    2. Detect largest blob for each state
    3. Apply daltonize correction for each CVD type
    4. Recolor detected regions to accessibility colors
    5. FIX+: Add diagonal hatching pattern to danger region for shape recognition
    6. FIX++: Add outlines for contrast enhancement
    7. Return all versions + detection metadata
    """
    # Keep copy of original for reference
    original = image_bgr.copy()

    # STEP 1: Detect red (danger) and blue (safe) health bar regions
    # This health bar uses red/blue split instead of red/green
    danger_mask, safe_mask = create_colour_masks_healthbar_red_blue(original)

    # STEP 2: Extract the main blob for each health state
    danger_data = get_main_blob(danger_mask, "Danger")
    safe_data = get_main_blob(safe_mask, "Safe")

    # STEP 3: Create detection visualization
    detected = original.copy()
    draw_detection_info(detected, danger_data, (0, 255, 255), "Danger")  # Cyan
    draw_detection_info(detected, safe_data, (255, 255, 0), "Safe")      # Yellow

    fix_deutan = boost_image_appearance(apply_daltonize_bgr(original, "d"))
    fix_protan = boost_image_appearance(apply_daltonize_bgr(original, "p"))
    fix_tritan = boost_image_appearance(apply_daltonize_bgr(original, "t"))

    # Recolor detected health bar regions with accessible colors
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

    # STEP 5: Generate FIX+ versions (FIX + add diagonal hatching pattern)
    # Add diagonal line pattern to danger region for shape-based recognition
    fixplus_deutan = add_diagonal_hatching_to_mask(
        fix_deutan, danger_mask,
        line_color=(255, 255, 255),  # White lines
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

    # STEP 6: Generate FIX++ versions (FIX+ + add outlines for maximum contrast)
    fixplusplus_deutan = add_outlines_fixplusplus(fixplus_deutan, [danger_mask, safe_mask])
    fixplusplus_protan = add_outlines_fixplusplus(fixplus_protan, [danger_mask, safe_mask])
    fixplusplus_tritan = add_outlines_fixplusplus(fixplus_tritan, [danger_mask, safe_mask])

    # STEP 7: Compile detection metadata
    metadata = {"template": "health_bar", "objects": []}

    # Add detected objects to metadata
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