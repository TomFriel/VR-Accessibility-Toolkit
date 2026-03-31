from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import base64
from daltonize.daltonize import daltonize

app = FastAPI()

# =========================================================
# SETTINGS
# =========================================================

MIN_CONTOUR_AREA = 500

# Icon files in same folder as app.py
ENEMY_ICON_PATH = "enemy_icon.png"
ALLY_ICON_PATH = "ally_icon.png"

# Scale icons relative to detected figure width
ICON_SCALE_FACTOR = 0.38

# Vertical offset above head
ICON_Y_OFFSET = 40

# Optional mild post boost after daltonization
SATURATION_BOOST = 1.15
VALUE_BOOST = 1.08

# Presentation-friendly post-fix colours (BGR)
ENEMY_POST_COLOR_DEUTAN = (0, 180, 255)   # bright orange
ENEMY_POST_COLOR_PROTAN = (0, 190, 255)   # bright orange/yellow
ENEMY_POST_COLOR_TRITAN = (0, 140, 255)   # slightly deeper orange

ALLY_POST_COLOR_DEUTAN = (255, 220, 0)    # bright cyan-yellowish
ALLY_POST_COLOR_PROTAN = (255, 235, 0)    # bright cyan
ALLY_POST_COLOR_TRITAN = (255, 200, 80)   # cyan with a bit more warmth

REGION_BLEND_ALPHA = 0.95


# =========================================================
# HELPERS
# =========================================================

def recolour_detected_regions(base_bgr, red_mask, green_mask, enemy_color_bgr, ally_color_bgr, alpha=0.75):
    """
    Push detected enemy/ally regions toward clearer presentation colours
    after daltonization, while keeping some of the original shading.
    """
    output = base_bgr.copy().astype(np.float32)

    enemy_color = np.full_like(output, enemy_color_bgr, dtype=np.float32)
    ally_color = np.full_like(output, ally_color_bgr, dtype=np.float32)

    red_bool = red_mask > 0
    green_bool = green_mask > 0

    output[red_bool] = (1.0 - alpha) * output[red_bool] + alpha * enemy_color[red_bool]
    output[green_bool] = (1.0 - alpha) * output[green_bool] + alpha * ally_color[green_bool]

    return np.clip(output, 0, 255).astype(np.uint8)

def encode_image_to_base64(img):
    success, buffer = cv2.imencode(".png", img)
    if not success:
        return None
    return base64.b64encode(buffer).decode("utf-8")


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

    # RED MASK
    lower_red1 = np.array([0, 80, 80])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 80, 80])
    upper_red2 = np.array([179, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    # GREEN MASK
    lower_green = np.array([35, 60, 60])
    upper_green = np.array([90, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = np.ones((5, 5), np.uint8)

    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
    green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

    return red_mask, green_mask


def apply_daltonize_bgr(image_bgr, cvd_type):
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    image_rgb_float = image_rgb.astype(np.float32) / 255.0

    fixed_rgb_float = daltonize(image_rgb_float, color_deficit=cvd_type)

    fixed_rgb = np.clip(fixed_rgb_float * 255.0, 0, 255).astype(np.uint8)
    fixed_bgr = cv2.cvtColor(fixed_rgb, cv2.COLOR_RGB2BGR)

    return fixed_bgr


def boost_image_appearance(image_bgr, sat_boost=SATURATION_BOOST, val_boost=VALUE_BOOST):
    """
    Makes raw daltonized output look a bit less dull.
    """
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)

    hsv[:, :, 1] *= sat_boost
    hsv[:, :, 2] *= val_boost

    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2], 0, 255)

    hsv = hsv.astype(np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def load_icon_with_alpha_fallback(path):
    """
    Loads icon.
    If image has no alpha, treat near-black pixels as transparent.
    """
    icon = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if icon is None:
        print(f"Could not load icon: {path}")
        return None

    # If already BGRA, great
    if len(icon.shape) == 3 and icon.shape[2] == 4:
        return icon

    # If BGR, create alpha from non-black pixels
    if len(icon.shape) == 3 and icon.shape[2] == 3:
        bgr = icon
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

        # Black background becomes transparent
        alpha = np.where(gray > 15, 255, 0).astype(np.uint8)

        bgra = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = alpha
        return bgra

    return None


def overlay_icon(background_bgr, overlay_bgra, center_x, top_y, target_width):
    """
    Draw icon centered at center_x, with top at top_y.
    target_width controls scale.
    """
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


def add_icons_to_fixplus(image_bgr, enemy_data, ally_data, enemy_icon, ally_icon):
    output = image_bgr.copy()

    if enemy_data is not None and enemy_icon is not None:
        icon_width = max(50, int(enemy_data["w"] * ICON_SCALE_FACTOR))
        icon_top_y = enemy_data["cy"] - (icon_width // 2) - 80
        output = overlay_icon(output, enemy_icon, enemy_data["cx"], icon_top_y, icon_width)

    if ally_data is not None and ally_icon is not None:
        icon_width = max(50, int(ally_data["w"] * ICON_SCALE_FACTOR))
        icon_top_y = ally_data["cy"] - (icon_width // 2) - 80
        output = overlay_icon(output, ally_icon, ally_data["cx"], icon_top_y, icon_width)

    return output


def process_enemy_ally(image_bgr):
    original = image_bgr.copy()

    red_mask, green_mask = create_colour_masks(original)

    enemy_data = get_main_blob(red_mask, "Enemy")
    ally_data = get_main_blob(green_mask, "Ally")

    detected = original.copy()
    draw_detection_info(detected, enemy_data, (0, 255, 255), "Enemy")
    draw_detection_info(detected, ally_data, (255, 255, 0), "Ally")

    # Load icons once per request
    enemy_icon = load_icon_with_alpha_fallback(ENEMY_ICON_PATH)
    ally_icon = load_icon_with_alpha_fallback(ALLY_ICON_PATH)

    # Fix per CVD type
    fix_deutan = boost_image_appearance(apply_daltonize_bgr(original, "d"))
    fix_protan = boost_image_appearance(apply_daltonize_bgr(original, "p"))
    fix_tritan = boost_image_appearance(apply_daltonize_bgr(original, "t"))

    fix_deutan = recolour_detected_regions(
        fix_deutan,
        red_mask,
        green_mask,
        ENEMY_POST_COLOR_DEUTAN,
        ALLY_POST_COLOR_DEUTAN,
        REGION_BLEND_ALPHA
    )

    fix_protan = recolour_detected_regions(
        fix_protan,
        red_mask,
        green_mask,
        ENEMY_POST_COLOR_PROTAN,
        ALLY_POST_COLOR_PROTAN,
        REGION_BLEND_ALPHA
    )

    fix_tritan = recolour_detected_regions(
        fix_tritan,
        red_mask,
        green_mask,
        ENEMY_POST_COLOR_TRITAN,
        ALLY_POST_COLOR_TRITAN,
        REGION_BLEND_ALPHA
)

    # Fix+ per CVD type with big icons
    fixplus_deutan = add_icons_to_fixplus(fix_deutan, enemy_data, ally_data, enemy_icon, ally_icon)
    fixplus_protan = add_icons_to_fixplus(fix_protan, enemy_data, ally_data, enemy_icon, ally_icon)
    fixplus_tritan = add_icons_to_fixplus(fix_tritan, enemy_data, ally_data, enemy_icon, ally_icon)

    metadata = {
        "template": "enemy_ally",
        "objects": []
    }

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
        "metadata": metadata
    }


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

            "metadata": outputs["metadata"]
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )