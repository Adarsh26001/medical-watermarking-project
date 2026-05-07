"""
Medical Image Watermarking Algorithms

This module contains the core watermarking algorithms for secure medical image
authentication. The system uses ROI-based watermarking with cryptographic hashing
for tamper detection while maintaining diagnostic image quality.

Author: Adarsh
License: MIT
"""

import cv2
import numpy as np
import hashlib
from skimage.metrics import structural_similarity as ssim
import math


def generate_hash(image: np.ndarray) -> str:
    """
    Generate SHA-256 hash of image data for integrity verification.

    Args:
        image: Input image array

    Returns:
        str: Hexadecimal SHA-256 hash
    """
    return hashlib.sha256(image.tobytes()).hexdigest()


def get_roi(image: np.ndarray) -> np.ndarray:
    """
    Extract Region of Interest (ROI) from medical image.

    The ROI is defined as the central 50% of the image (both width and height)
    to focus watermarking on diagnostically relevant areas while preserving
    image borders that may contain patient information.

    Args:
        image: Input grayscale image

    Returns:
        np.ndarray: ROI region (h//4:h//2, w//4:w//2)
    """
    h, w = image.shape
    return image[h//4:h//2, w//4:w//2]


def embed_watermark(image_path: str) -> tuple[str, str]:
    """
    Embed invisible watermark in medical image.

    The watermarking process:
    1. Load image in grayscale
    2. Extract ROI
    3. Generate hash of original ROI
    4. Add watermark (intensity +10) to ROI
    5. Save watermarked image

    Args:
        image_path: Path to input image

    Returns:
        tuple: (output_path, hash_value)
    """
    # Load image in grayscale
    image = cv2.imread(image_path, 0)

    # Extract region of interest
    roi = get_roi(image)

    # Create watermark pattern (constant intensity addition)
    watermark = np.ones_like(roi) * 10

    # Get image dimensions
    h, w = image.shape

    # Embed watermark by adding to ROI
    image[h//4:h//2, w//4:w//2] = cv2.add(roi, watermark)

    # Generate hash of original ROI for verification
    hash_value = generate_hash(roi)

    # Create output path
    output_path = image_path.replace('.png', '_watermarked.png')

    # Save watermarked image
    cv2.imwrite(output_path, image)

    return output_path, hash_value


def verify_image(image_path: str, original_hash: str) -> bool:
    """
    Verify image authenticity by comparing ROI hash.

    Args:
        image_path: Path to image to verify
        original_hash: Original SHA-256 hash of ROI

    Returns:
        bool: True if authentic, False if tampered
    """
    # Load image in grayscale
    image = cv2.imread(image_path, 0)

    # Extract current ROI
    roi = get_roi(image)

    # Generate current hash
    current_hash = generate_hash(roi)

    # Compare hashes
    return current_hash == original_hash


def calculate_psnr(original: np.ndarray, compressed: np.ndarray) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR).

    PSNR measures image quality degradation. Higher values indicate
    better quality preservation.

    Args:
        original: Original image
        compressed: Processed image

    Returns:
        float: PSNR value in dB
    """
    mse = np.mean((original - compressed) ** 2)

    if mse == 0:
        return 100  # Perfect match

    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

    return psnr


def calculate_ssim(original: np.ndarray, processed: np.ndarray) -> float:
    """
    Calculate Structural Similarity Index (SSIM).

    SSIM measures structural similarity between images. Values closer to 1
    indicate higher similarity.

    Args:
        original: Original image
        processed: Processed image

    Returns:
        float: SSIM score (0-1)
    """
    score, _ = ssim(original, processed, full=True)
    return score


def calculate_ber(original_bits: np.ndarray, extracted_bits: np.ndarray) -> float:
    """
    Calculate Bit Error Rate (BER).

    BER measures the percentage of bits that differ between original and
    extracted watermarks.

    Args:
        original_bits: Original bit sequence
        extracted_bits: Extracted bit sequence

    Returns:
        float: BER as percentage (0-1)
    """
    errors = np.sum(original_bits != extracted_bits)
    total = len(original_bits)
    return errors / total


def calculate_nc(original: np.ndarray, extracted: np.ndarray) -> float:
    """
    Calculate Normalized Correlation (NC).

    NC measures the correlation between original and extracted watermarks.
    Values closer to 1 indicate better extraction accuracy.

    Args:
        original: Original watermark
        extracted: Extracted watermark

    Returns:
        float: NC coefficient (-1 to 1)
    """
    numerator = np.sum(original * extracted)
    denominator = np.sqrt(np.sum(original**2) * np.sum(extracted**2))
    return numerator / denominator