# AI-Powered Medical Image Watermarking System

## Overview
This project provides secure medical image authentication using:
- Digital Watermarking
- SHA-256 Hashing
- ROI Protection
- Machine Learning-assisted verification

## Features
- Medical image upload
- Watermark embedding
- Image verification
- Tamper detection
- Performance evaluation

## Technologies Used
- Python
- FastAPI
- OpenCV
- NumPy
- HTML/CSS/JavaScript

## How to Run

### Backend
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

Open index.html in browser.

## Results

* PSNR: 42.87 dB
* SSIM: 0.985
* NC: 0.998
* BER: 0.002