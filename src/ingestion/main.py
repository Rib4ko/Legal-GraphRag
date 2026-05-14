import asyncio
import argparse
from pathlib import Path

from .routes.direct_text import DirectTextIngester
from .routes.pdf_ocr import AdvancedOCRIngester
from .core.validator import Validator

async def main():
    parser = argparse.ArgumentParser(description="Phase 1 Ingestion Pipeline for Moroccan LegalTech SaaS")
    parser.add_argument("input_path", type=str, help="Path to the raw file (HTML, TXT, PDF, PNG, JPG) to process.")
    parser.add_argument("--url", type=str, default=None, help="Optional source URL.")
    parser.add_argument("--lang", type=str, default="fr", help="Language for OCR (ar or fr).")
    args = parser.parse_args()

    input_file = Path(args.input_path)
    if not input_file.exists():
        print(f"Error: Input file '{args.input_path}' does not exist.")
        return

    ext = input_file.suffix.lower()
    validator = Validator(pending_dir="data/pending_review")

    print(f"Starting ingestion for: {input_file.name}")
    print("--------------------------------------------------")

    doc = None
    if ext in [".pdf", ".png", ".jpg", ".jpeg"]:
        print(f"-> Routing to Advanced OCR Lane ({ext})")
        ingester = AdvancedOCRIngester(lang=args.lang)
        if ext == ".pdf":
            doc = await ingester.process_pdf(file_path=str(input_file), source_url=args.url, language=args.lang)
        else:
            doc = await ingester.process_image(file_path=str(input_file), source_url=args.url, language=args.lang)
            
    elif ext in [".html", ".htm", ".txt"]:
        print("-> Routing to Scraper Lane: Direct Text Ingestion")
        ingester = DirectTextIngester()
        doc = await ingester.process_html_file(file_path=str(input_file), source_url=args.url, language=args.lang)
    else:
        print(f"Error: Unsupported extension '{ext}'.")
        return

    if doc:
        print("-> Parsing completed. Submitting for Review.")
        await validator.submit_for_review(doc, base_filename=input_file.stem)
        print("--------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
