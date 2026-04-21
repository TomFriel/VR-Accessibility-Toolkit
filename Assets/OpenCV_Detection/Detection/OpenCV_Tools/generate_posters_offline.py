
import os
import json
import argparse
from pathlib import Path

import cv2

# Import your existing processing functions from app.py
# This works because app.py already contains:
# - process_enemy_ally(image_bgr)
# - process_health_bar(image_bgr)
# - process_minimap(image_bgr)
from app import process_enemy_ally, process_health_bar, process_minimap


VALID_TEMPLATES = {"enemy_ally", "health_bar", "minimap"}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_image(path: Path, image_bgr) -> None:
    ok = cv2.imwrite(str(path), image_bgr)
    if not ok:
        raise RuntimeError(f"Failed to save image: {path}")


def choose_processor(template_type: str):
    if template_type == "enemy_ally":
        return process_enemy_ally
    if template_type == "health_bar":
        return process_health_bar
    if template_type == "minimap":
        return process_minimap
    raise ValueError(f"Unsupported template_type: {template_type}")


def generate_outputs(input_path: Path, template_type: str, output_root: Path) -> Path:
    if template_type not in VALID_TEMPLATES:
        raise ValueError(
            f"template_type must be one of {sorted(VALID_TEMPLATES)}, got: {template_type}"
        )

    if not input_path.exists():
        raise FileNotFoundError(f"Input image not found: {input_path}")

    image_bgr = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise RuntimeError(f"Could not decode image: {input_path}")

    processor = choose_processor(template_type)
    outputs = processor(image_bgr)

    stem = input_path.stem
    output_dir = output_root / template_type / stem
    ensure_dir(output_dir)

    # Save original input too, so the whole poster family lives together.
    save_image(output_dir / f"{stem}_original.png", image_bgr)

    image_keys = [
        "detected",
        "fix_deutan",
        "fix_protan",
        "fix_tritan",
        "fixplus_deutan",
        "fixplus_protan",
        "fixplus_tritan",
        "fixplusplus_deutan",
        "fixplusplus_protan",
        "fixplusplus_tritan",
    ]

    for key in image_keys:
        if key in outputs and outputs[key] is not None:
            save_image(output_dir / f"{stem}_{key}.png", outputs[key])

    metadata = outputs.get("metadata", {})
    with open(output_dir / f"{stem}_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return output_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate offline poster outputs for Unity/Quest using your existing OpenCV pipeline."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a single source poster image, for example: input/enemyally_01.png",
    )
    parser.add_argument(
        "--template",
        required=True,
        choices=sorted(VALID_TEMPLATES),
        help="Which pipeline to run: enemy_ally, health_bar, or minimap",
    )
    parser.add_argument(
        "--output-root",
        default="PosterAutomationOutputs",
        help="Root folder where generated PNGs will be saved",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_root = Path(args.output_root)

    output_dir = generate_outputs(input_path, args.template, output_root)

    print("Done.")
    print(f"Generated files saved in: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
