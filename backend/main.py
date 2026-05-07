"""
AI-Powered Medical Image Watermarking System - Backend API

This module provides a FastAPI-based REST API for secure medical image
watermarking and authentication. The system embeds invisible watermarks
in medical images and provides cryptographic verification capabilities.

Author: Adarsh
License: MIT
"""

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from watermark import embed_watermark, verify_image

# Initialize FastAPI application
app = FastAPI(
    title="Medical Image Watermarking API",
    description="Secure watermarking system for medical image authentication",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory configuration
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files for image serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Global variable to store the original hash (in production, use database)
stored_hash = ""


@app.post("/embed")
async def embed_watermark_endpoint(file: UploadFile = File(...)):
    """
    Embed invisible watermark in uploaded medical image.

    This endpoint:
    1. Accepts PNG medical image upload
    2. Embeds watermark in ROI (Region of Interest)
    3. Generates SHA-256 hash of original ROI
    4. Returns watermarked image and hash for verification

    Args:
        file: Medical image file (PNG format recommended)

    Returns:
        dict: Success message, hash, and output path
    """
    global stored_hash

    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Embed watermark and generate hash
    output_path, hash_value = embed_watermark(file_path)

    # Store hash for verification (in production, store in database)
    stored_hash = hash_value

    return {
        "message": "Watermark Embedded Successfully",
        "hash": hash_value,
        "output": output_path
    }


@app.post("/verify")
async def verify_image_endpoint(file: UploadFile = File(...)):
    """
    Verify authenticity of watermarked medical image.

    This endpoint:
    1. Accepts potentially modified image
    2. Extracts ROI and computes current hash
    3. Compares with original hash
    4. Returns authentication status

    Args:
        file: Image to verify

    Returns:
        dict: Authentication status ("Authentic" or "Tampered")
    """
    global stored_hash

    # Save uploaded file for verification
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Verify image integrity
    status = verify_image(file_path, stored_hash)

    return {
        "status": "Authentic" if status else "Tampered"
    }


@app.get("/")
async def root():
    """
    Root endpoint providing API information.
    """
    return {
        "message": "Medical Image Watermarking API",
        "version": "1.0.0",
        "endpoints": {
            "POST /embed": "Embed watermark in image",
            "POST /verify": "Verify image authenticity"
        }
    }
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
