import numpy as np
import cv2

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

from utils import encode_image_to_base64
from templates.enemy_ally import process_enemy_ally
from templates.health_bar import process_health_bar
from templates.minimap import process_minimap

app = FastAPI()


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