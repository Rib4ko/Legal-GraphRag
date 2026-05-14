import os
import argparse
import asyncio
from src.ingestion.routes.pdf_ocr import AdvancedOCRIngester
from src.ingestion.core.validator import Validator

async def run_ocr(image_path: str, lang: str = "en"):
    print(f"Initializing Ain OCR Engine (lang={lang})...")
    ingester = AdvancedOCRIngester(lang=lang)

    print(f"Processing {image_path} ...")
    doc = await ingester.process_image(image_path, language=lang)

    validator = Validator(pending_dir="data/pending_review")
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    await validator.submit_for_review(doc, base_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Advanced PP-Structure OCR on a given image."
    )
    parser.add_argument("image", help="Path to the image file.")
    parser.add_argument(
        "--lang", default="en",
        help="Language for OCR (en, fr, ar)"
    )
    args = parser.parse_args()

    if not os.path.isfile(args.image):
        print(f"Error: Image not found: {args.image}")
    else:
        asyncio.run(run_ocr(args.image, lang=args.lang))
