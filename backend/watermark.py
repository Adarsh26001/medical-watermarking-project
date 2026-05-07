import cv2
import numpy as np
import hashlib
from skimage.metrics import structural_similarity as ssim
import math


def generate_hash(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


# ROI extraction

def get_roi(image):
    h, w = image.shape
    return image[h//4:h//2, w//4:w//2]


# Watermark embedding

def embed_watermark(image_path):
    image = cv2.imread(image_path, 0)

    roi = get_roi(image)

    watermark = np.ones_like(roi) * 10

    h, w = image.shape

    image[h//4:h//2, w//4:w//2] = cv2.add(roi, watermark)

    hash_value = generate_hash(roi)

    output_path = image_path.replace('.png', '_watermarked.png')

    cv2.imwrite(output_path, image)

    return output_path, hash_value


# Verification

def verify_image(image_path, original_hash):
    image = cv2.imread(image_path, 0)

    roi = get_roi(image)

    current_hash = generate_hash(roi)

    return current_hash == original_hash


# PSNR calculation

def calculate_psnr(original, compressed):
    mse = np.mean((original - compressed) ** 2)

    if mse == 0:
        return 100

    max_pixel = 255.0

    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))

    return psnr


# SSIM calculation

def calculate_ssim(original, processed):
    score, _ = ssim(original, processed, full=True)
    return score


# BER calculation

def calculate_ber(original_bits, extracted_bits):
    errors = np.sum(original_bits != extracted_bits)
    total = len(original_bits)
    return errors / total


# NC calculation

def calculate_nc(original, extracted):
    numerator = np.sum(original * extracted)
    denominator = np.sqrt(np.sum(original**2) * np.sum(extracted**2))
    return numerator / denominator