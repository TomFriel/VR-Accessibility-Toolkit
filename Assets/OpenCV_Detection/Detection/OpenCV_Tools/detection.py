import cv2
import numpy as np

from config import MIN_CONTOUR_AREA, MINIMAP_MIN_CONTOUR_AREA

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

    lower_red1 = np.array([0, 80, 80])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 80, 80])
    upper_red2 = np.array([179, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

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
    from utils import trim_bottom_of_mask

    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    kernel_small = np.ones((5, 5), np.uint8)
    kernel_big = np.ones((9, 9), np.uint8)

    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel_small)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel_small)

    red_mask = cv2.dilate(red_mask, kernel_big, iterations=1)
    blue_mask = cv2.dilate(blue_mask, kernel_big, iterations=1)

    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel_big)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel_big)

    blue_mask = cv2.erode(blue_mask, kernel_small, iterations=1)
    blue_mask = trim_bottom_of_mask(blue_mask, trim_ratio=0.12)

    return red_mask, blue_mask


def create_colour_masks_healthbar(image_bgr):
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = red_mask1 | red_mask2

    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    return red_mask, green_mask


def create_colour_masks_healthbar_red_blue(image_bgr):
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])

    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

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


def create_colour_masks_minimap(image_bgr):
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


def get_marker_blobs(mask, min_area=40, max_area=600):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blobs = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if min_area < area < max_area:
            x, y, w, h = cv2.boundingRect(cnt)
            blobs.append({
                "bbox": (x, y, w, h),
                "center": (x + w // 2, y + h // 2)
            })

    return blobs