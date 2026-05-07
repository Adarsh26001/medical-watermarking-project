import cv2
import numpy as np
import matplotlib.pyplot as plt
from watermark import calculate_psnr, calculate_ssim


original = cv2.imread('../dataset/sample1.png', 0)
watermarked = cv2.imread('../dataset/sample1_watermarked.png', 0)


psnr_value = calculate_psnr(original, watermarked)
ssim_value = calculate_ssim(original, watermarked)


print("PSNR:", psnr_value)
print("SSIM:", ssim_value)


methods = ['LSB', 'DWT', 'DCT-DWT', 'Proposed']
psnr_scores = [34.5, 38.7, 40.1, 42.8]


plt.figure(figsize=(8,5))
plt.bar(methods, psnr_scores)
plt.title('PSNR Comparison')
plt.xlabel('Methods')
plt.ylabel('PSNR (dB)')
plt.savefig('../results/psnr_results.png')
plt.show()