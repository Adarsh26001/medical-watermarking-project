"""
Medical Image Watermarking Algorithms

This module contains the core watermarking algorithms for secure medical image
authentication. The implementation is designed to be demonstrative, easy to
discover, and clearly understandable for academic submission.

Instead of a flat constant watermark, this version uses a deterministic pattern
generated from a small sinusoidal blend, which keeps the image quality high but
introduces a more recognizable signature.

Author: Adarsh
License: MIT
"""

from pathlib import Path
import cv2
import numpy as np
import hashlib
from skimage.metrics import structural_similarity as ssim
import math


def hash_roi(roi: np.ndarray) -> str:
    """Return a SHA-256 digest of the ROI pixel array."""
    return hashlib.sha256(roi.tobytes()).hexdigest()


def load_grayscale_image(path: str) -> np.ndarray:
    """Read an image from disk and return it as a single-channel grayscale array."""
    image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Unable to read image: {path}")
    if image.ndim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif image.ndim == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    return image


def extract_roi(image: np.ndarray, margin: float = 0.25) -> np.ndarray:
    """Extract a central ROI from the image according to the margin percentage."""
    h, w = image.shape
    top = int(h * margin)
    left = int(w * margin)
    bottom = int(h * (1 - margin))
    right = int(w * (1 - margin))
    return image[top:bottom, left:right]


def create_watermark_pattern(shape: tuple[int, int], scale: float = 12.0) -> np.ndarray:
    """Create a repeating sinusoidal watermark pattern for the ROI."""
    rows, cols = shape
    y = np.linspace(0, math.pi * 2, rows, dtype=np.float32)[:, None]
    x = np.linspace(0, math.pi * 3, cols, dtype=np.float32)[None, :]
    pattern = (np.sin(y * 1.2 + 0.5) + np.cos(x * 1.5 - 0.3)) * (scale / 2)
    normalized = np.clip(pattern + scale, 0, 255).astype(np.uint8)
    return normalized


def embed_watermark(image_path: str) -> tuple[str, str]:
    """Embed a watermark pattern into the ROI of the image and return the result."""
    image = load_grayscale_image(image_path)
    roi = extract_roi(image)
    watermark = create_watermark_pattern(roi.shape, scale=10.0)

    pasted = cv2.add(roi, watermark)
    image_slice = image.copy()
    h, w = roi.shape
    top = int(image.shape[0] * 0.25)
    left = int(image.shape[1] * 0.25)
    image_slice[top:top + h, left:left + w] = pasted

    hash_value = hash_roi(roi)
    output_path = str(Path(image_path).with_name(Path(image_path).stem + "_watermarked.png"))
    cv2.imwrite(output_path, image_slice)

    return output_path, hash_value


def verify_image(image_path: str, original_hash: str) -> bool:
    """Verify the integrity of a watermarked image by recomputing the ROI hash."""
    image = load_grayscale_image(image_path)
    roi = extract_roi(image)
    return hash_roi(roi) == original_hash


def calculate_psnr(original: np.ndarray, processed: np.ndarray) -> float:
    """Return PSNR comparing original and processed grayscale image arrays."""
    mse = np.mean((original.astype(np.float64) - processed.astype(np.float64)) ** 2)
    if mse == 0:
        return float("inf")
    return 20 * math.log10(255.0 / math.sqrt(mse))


def calculate_ssim(original: np.ndarray, processed: np.ndarray) -> float:
    """Return the SSIM score for two grayscale images."""
    score, _ = ssim(original, processed, full=True)
    return float(score)


def calculate_ber(original_bits: np.ndarray, extracted_bits: np.ndarray) -> float:
    """Return the bit error rate between two binary sequences."""
    if original_bits.size == 0:
        return 0.0
    return float(np.mean(original_bits != extracted_bits))


def calculate_nc(original: np.ndarray, extracted: np.ndarray) -> float:
    """Return the normalized correlation between two arrays."""
    numerator = np.sum(original.astype(np.float64) * extracted.astype(np.float64))
    denominator = math.sqrt(np.sum(original.astype(np.float64) ** 2) * np.sum(extracted.astype(np.float64) ** 2))
    return float(numerator / denominator) if denominator != 0 else 0.0
