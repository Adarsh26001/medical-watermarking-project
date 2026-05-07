"""
Backend API for Medical Image Watermarking.

This backend serves as the REST API for the medical watermarking system.
It provides endpoints to embed a watermark into an uploaded image and to
verify whether a submitted image has been tampered with.

The project is intentionally designed for submission and demonstration
purposes. The backend stores a single session hash in memory and exposes
basic image processing endpoints.

Author: Adarsh
License: MIT
"""

from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from watermark import embed_watermark, verify_image

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(
    title="Medical Image Watermarking API",
    description="REST API for authenticated medical image watermark embedding and verification",
    version="1.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For a public demo this is fine; lock this down in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

stored_hash = ""
stored_image = ""


def save_upload(file: UploadFile) -> Path:
    """Save an uploaded file to the uploads directory and return its path."""
    destination = UPLOAD_DIR / file.filename
    with destination.open("wb") as buffer:
        buffer.write(file.file.read())
    return destination


@app.post("/embed")
async def embed_watermark_endpoint(file: UploadFile = File(...)):
    """Embed watermark into a medical image and return verification metadata."""
    global stored_hash, stored_image

    saved_path = save_upload(file)
    output_path, hash_value = embed_watermark(str(saved_path))

    stored_hash = hash_value
    stored_image = output_path

    return {
        "message": "Watermark embedded successfully.",
        "hash": hash_value,
        "output_url": f"/uploads/{Path(output_path).name}",
        "original_upload": file.filename,
    }


@app.post("/verify")
async def verify_image_endpoint(file: UploadFile = File(...)):
    """Verify whether a submitted image is authentic or has been tampered with."""
    global stored_hash

    if not stored_hash:
        raise HTTPException(
            status_code=400,
            detail="No stored watermark hash found. Embed an image before verifying.",
        )

    saved_path = save_upload(file)
    valid = verify_image(str(saved_path), stored_hash)

    return {
        "message": "Verification completed.",
        "status": "Authentic" if valid else "Tampered",
        "stored_hash": stored_hash,
        "verified_file": file.filename,
    }


@app.get("/")
async def read_root():
    """Return basic API metadata and endpoints."""
    return {
        "project": "Medical Image Watermarking API",
        "description": "Upload an image to embed a watermark or verify image integrity.",
        "version": "1.0.1",
        "endpoints": {
            "embed": "/embed",
            "verify": "/verify",
        },
    }
