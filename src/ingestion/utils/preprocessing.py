"""
Image preprocessing to improve OCR quality on Arabic legal documents.

Key techniques:
- Upscale low-res images (screenshots are ~96 DPI, OCR needs ~300 DPI)
- Convert to grayscale to eliminate color noise (blue headers, etc.)
- Apply CLAHE for local contrast enhancement
- Binarize with Otsu's threshold for crisp character edges
"""
import cv2
import numpy as np


def preprocess_for_ocr(img: np.ndarray, upscale: float = 2.0) -> np.ndarray:
    """
    Preprocess image for optimal Arabic OCR quality.
    Returns a BGR image suitable for PaddleOCR.
    """
    # 1. Upscale - critical for screenshots at screen resolution
    if upscale > 1.0:
        img = cv2.resize(img, None, fx=upscale, fy=upscale,
                         interpolation=cv2.INTER_CUBIC)

    # 2. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. CLAHE - adaptive contrast enhancement
    #    Helps with faded text and uneven lighting
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 4. Light Gaussian blur to reduce noise before thresholding
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # 5. Otsu's binarization - crisp black text on white background
    _, binary = cv2.threshold(blurred, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 6. Convert back to BGR (PaddleOCR expects 3 channels)
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
