from pathlib import Path
import hashlib
import uuid

import cv2
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Medical Image Watermark Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


def compute_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_watermark(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

    overlay = image.copy()
    text = "WATERMARK"
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1.2
    thickness = 2
    text_size, _ = cv2.getTextSize(text, font, scale, thickness)
    position = (10, image.shape[0] - 20)

    cv2.rectangle(
        overlay,
        (position[0] - 5, position[1] - text_size[1] - 5),
        (position[0] + text_size[0] + 5, position[1] + 5),
        (0, 0, 0),
        cv2.FILLED,
    )
    cv2.putText(
        overlay,
        text,
        position,
        font,
        scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA,
    )
    return overlay


def decode_image(file_bytes: bytes) -> np.ndarray:
    array = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")
    return image


@app.post("/embed")
async def embed_watermark(file: UploadFile = File(...)):
    contents = await file.read()
    image = decode_image(contents)
    watermarked = make_watermark(image)

    success, encoded = cv2.imencode(".png", watermarked)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to encode watermarked image.")

    output_bytes = encoded.tobytes()
    output_hash = compute_hash(output_bytes)
    output_name = f"{uuid.uuid4().hex}_watermarked.png"
    output_path = UPLOAD_DIR / output_name
    output_path.write_bytes(output_bytes)

    return {
        "message": "Watermark embedded successfully.",
        "hash": output_hash,
        "output_url": f"/uploads/{output_name}",
    }


@app.post("/verify")
async def verify_image(file: UploadFile = File(...), reference_hash: str = Form(...)):
    contents = await file.read()
    current_hash = compute_hash(contents)
    authentic = current_hash == reference_hash
    return {
        "message": "Verification complete.",
        "authentic": authentic,
        "reference_hash": reference_hash,
        "current_hash": current_hash,
    }
