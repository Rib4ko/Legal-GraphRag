"""
1_extractor.py — Phase 1: Scrape & Extract Arabic Legal Texts
==============================================================
Scrapes the Adala resources page for PDF links, downloads them,
and extracts the Arabic text (un-garbling it using PyMuPDF,
arabic_reshaper, and bidi) into clean Markdown files.
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
import fitz  # PyMuPDF
import arabic_reshaper
from bidi.algorithm import get_display

# Fix Windows terminal encoding for emoji/Arabic
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
API_BASE = "https://adala.justice.gov.ma/api"
API_ROOT_RESOURCES = f"{API_BASE}/files/resources"
API_FOLDER = f"{API_BASE}/folders/"
DOMAIN = "https://adala.justice.gov.ma"
OUTPUT_DIR = Path("data/ready_for_db")
PDF_DIR = Path("data/raw_pdfs")

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_pdfs_from_api() -> list[str]:
    """Recursively fetches PDF links from the Adala JSON API."""
    print(f"🔍 Fetching root resources from {API_ROOT_RESOURCES}...")
    pdf_links = set()
    
    try:
        response = requests.get(API_ROOT_RESOURCES, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Seed folders from root API
        folders_to_visit = []
        if isinstance(data, list):
            for item in data:
                if "id" in item:
                    folders_to_visit.append(str(item["id"]))
        elif isinstance(data, dict) and "FileFolders" in data:
            for folder in data["FileFolders"]:
                folders_to_visit.append(str(folder["id"]))
                
        # Also seed folders by scraping the homepage HTML since some are hidden
        try:
            home_html = requests.get(f"{DOMAIN}/resources", timeout=10).text
            import re
            html_ids = re.findall(r'/resources/(\d+)', home_html)
            folders_to_visit.extend(html_ids)
            print(f"  -> Extracted {len(html_ids)} additional folder ID(s) from homepage.")
        except Exception as e:
            print(f"  ⚠️ Could not scrape homepage for extra IDs: {e}")
            
        # The API doesn't expose the full tree, so we inject all known root section IDs:
        # (Royal Speeches, Treaties, Legislative Texts, Periodicals, References, etc.)
        known_sections = [
            332, 333, 335,  # Royal Speeches
            496, 497,       # Agreements & Treaties
            2, 12, 568, 896, 1052, 1053, 1054,  # Legislative/Regulatory
            1079,           # Judiciary Magazine
            143, 149, 625, 1109, 1110, 1111, 1112,  # Document References
            3, 1078,        # Circulars
            1084            # Ministry Publications
        ]
        for idx in known_sections:
            folders_to_visit.append(str(idx))
            
        # Ensure unique items in list
        folders_to_visit = list(set(folders_to_visit))

        visited_folders = set()
        
        while folders_to_visit:
            folder_id = str(folders_to_visit.pop(0))
            if folder_id in visited_folders:
                continue
            visited_folders.add(folder_id)
            
            print(f"  -> Fetching folder ID: {folder_id}")
            try:
                folder_resp = requests.get(f"{API_FOLDER}{folder_id}", timeout=10)
                folder_resp.raise_for_status()
                folder_data = folder_resp.json()
                
                # Extract files
                if "files" in folder_data and folder_data["files"]:
                    for file_item in folder_data["files"]:
                        if "path" in file_item:
                            path = file_item["path"]
                            if path.lower().endswith(".pdf"):
                                # Clean up duplicate slashes if needed
                                path = path.lstrip("/")
                                full_url = f"{API_BASE}/{path}"
                                pdf_links.add(full_url)
                
                # Queue sub-folders from "FileFolders"
                if "FileFolders" in folder_data and folder_data["FileFolders"]:
                    for sub_folder in folder_data["FileFolders"]:
                        if "id" in sub_folder:
                            sid = str(sub_folder["id"])
                            if sid not in visited_folders and sid not in folders_to_visit:
                                folders_to_visit.append(sid)
                                
                # Queue sub-folders from "folders"
                if "folders" in folder_data and folder_data["folders"]:
                    for sub_folder in folder_data["folders"]:
                        if "id" in sub_folder:
                            sid = str(sub_folder["id"])
                            if sid not in visited_folders and sid not in folders_to_visit:
                                folders_to_visit.append(sid)
                            
            except Exception as e:
                print(f"  ❌ Failed to fetch folder {folder_id}: {e}")
                
        print(f"✅ Found {len(pdf_links)} PDF(s) via the API.")
        return list(pdf_links)
    except Exception as e:
        print(f"❌ Failed to reach the root API endpoint: {e}")
        return []

def download_pdf(url: str, output_path: Path) -> bool:
    """Downloads a PDF from a URL to the given path."""
    if output_path.exists():
        print(f"  ⏭️ Already downloaded: {output_path.name}")
        return True
        
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  ⬇️ Downloaded: {output_path.name}")
        return True
    except Exception as e:
        print(f"  ❌ Failed to download {url}: {e}")
        return False

def extract_and_ungarble_arabic(pdf_path: Path) -> str:
    """
    Extracts text from a PDF. 
    PyMuPDF (fitz) >1.23.0 inherently handles Arabic text correctly 
    in logical string order, which is what Markdown editors need to render RTL.
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Modern PyMuPDF natively extracts Arabic in correct logical order.
            # Applying arabic_reshaper or get_display here actually breaks rendering
            # in standard Markdown editors which handle RTL automatically.
            text = page.get_text("text")
            full_text.append(text)
            
        return "\n\n".join(full_text)
    except Exception as e:
        print(f"  ❌ Failed to extract text from {pdf_path.name}: {e}")
        return ""

def format_as_markdown(text: str, title: str) -> str:
    """Formats the raw text as a Markdown document."""
    md = f"# {title}\n\n"
    # Basic structuring: could be improved to detect 'الفصل' or 'المادة'
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("المادة") or line.startswith("الفصل"):
            md += f"\n## {line}\n"
        else:
            md += f"{line}\n"
    return md

# ---------------------------------------------------------
# 3. MAIN PIPELINE
# ---------------------------------------------------------
def main():
    print("⚖️  Moroccan Legal Extractor — Phase 1")
    print("=" * 50)
    
    # 1. Fetch PDF links via API
    pdf_urls = get_pdfs_from_api()
    
    if not pdf_urls:
        print("⚠️ No PDFs found from the API. Please verify network access to adala.justice.gov.ma.")
        return
        
    import re
    # 2. Download and Process each PDF
    for url in pdf_urls:
        raw_filename = url.split("/")[-1]
        # Sanitize filename to prevent path traversal
        filename = re.sub(r'[^a-zA-Z0-9.\-_]', '_', raw_filename).lstrip('.-')
        if not filename:
            filename = "document.pdf"
        
        pdf_path = PDF_DIR / filename
        md_path = OUTPUT_DIR / f"{filename}.md"
        
        if md_path.exists():
            print(f"\n  ⏭️ Already processed: {md_path.name}")
            continue
            
        print(f"\n📄 Processing: {filename}")
        
        # Download
        # If it's a dummy URL, it will fail to download, we handle it gracefully
        success = download_pdf(url, pdf_path)
        
        if success:
            # Extract
            print("  ⚙️ Extracting and un-garbling Arabic text...")
            raw_text = extract_and_ungarble_arabic(pdf_path)
            
            if raw_text.strip():
                # Format to Markdown
                md_content = format_as_markdown(raw_text, title=filename.replace(".pdf", ""))
                
                # Save Markdown
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                print(f"  ✅ Saved perfectly formatted Markdown: {md_path}")
            else:
                print(f"  ⚠️ No text could be extracted from {filename}.")
        
        time.sleep(1) # Be respectful to the server

    print(f"\n{'=' * 50}")
    print(f"✅ Extraction complete! Files are ready in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
