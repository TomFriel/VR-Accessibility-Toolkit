import os

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
ENEMY_POST_COLOR_DEUTAN = (0, 180, 255)
ENEMY_POST_COLOR_PROTAN = (0, 190, 255)
ENEMY_POST_COLOR_TRITAN = (0, 140, 255)

ALLY_POST_COLOR_DEUTAN = (255, 220, 0)
ALLY_POST_COLOR_PROTAN = (255, 235, 0)
ALLY_POST_COLOR_TRITAN = (255, 200, 80)

# Health-bar post-fix colours (BGR)
HEALTH_DANGER_DEUTAN = (0, 165, 255)
HEALTH_SAFE_DEUTAN = (255, 220, 0)

HEALTH_DANGER_PROTAN = (0, 180, 255)
HEALTH_SAFE_PROTAN = (255, 235, 0)

HEALTH_DANGER_TRITAN = (0, 120, 255)
HEALTH_SAFE_TRITAN = (0, 210, 80)

# Minimap post-fix colours (BGR)
MINIMAP_ENEMY_DEUTAN = (0, 180, 255)
MINIMAP_ALLY_DEUTAN = (255, 220, 0)

MINIMAP_ENEMY_PROTAN = (0, 190, 255)
MINIMAP_ALLY_PROTAN = (255, 235, 0)

MINIMAP_ENEMY_TRITAN = (0, 150, 255)
MINIMAP_ALLY_TRITAN = (0, 220, 120)

REGION_BLEND_ALPHA = 0.95