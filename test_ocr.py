from PIL import Image, ImageDraw, ImageFont
from paddleocr import PaddleOCR
import os

# Disable MKLDNN to fix PaddlePaddle 3.x bug on Windows
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_ENABLE_ONEDNN"] = "0"

# 1. Create a dummy image with some text
img_path = "test_image.png"
img = Image.new('RGB', (400, 100), color = (255, 255, 255))
d = ImageDraw.Draw(img)
# Draw some text
d.text((10, 40), "This is a test for PaddleOCR.", fill=(0,0,0))
img.save(img_path)

print("Created test image.")

# 2. Initialize PaddleOCR
print("Initializing PaddleOCR (this might take a moment to download models the first time)...")
ocr = PaddleOCR(use_angle_cls=True, lang='en') 

# 3. Run OCR on the image
print(f"Running OCR on {img_path}...")
result = ocr.ocr(img_path, cls=True)

# 4. Print results
print("\n--- OCR Results ---")
for idx in range(len(result)):
    res = result[idx]
    if res is None:
        continue
    for line in res:
        # line format: [[box], (text, confidence)]
        box = line[0]
        text_info = line[1]
        print(f"Detected Text: '{text_info[0]}' (Confidence: {text_info[1]:.4f})")

# Clean up
if os.path.exists(img_path):
    os.remove(img_path)
