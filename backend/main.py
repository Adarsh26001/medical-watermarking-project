from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from watermark import embed_watermark, verify_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

stored_hash = ""


@app.post("/embed")
async def embed(file: UploadFile = File(...)):
    global stored_hash

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    output_path, hash_value = embed_watermark(file_path)

    stored_hash = hash_value

    return {
        "message": "Watermark Embedded Successfully",
        "hash": hash_value,
        "output": output_path
    }


@app.post("/verify")
async def verify(file: UploadFile = File(...)):
    global stored_hash

    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as f:
        f.write(await file.read())

    status = verify_image(file_path, stored_hash)

    return {
        "status": "Authentic" if status else "Tampered"
    }