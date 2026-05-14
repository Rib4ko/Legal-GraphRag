import os
import time
import requests
from bs4 import BeautifulSoup
import pdfplumber
import arabic_reshaper
from bidi.algorithm import get_display

# ---------------------------------------------------------
# DIRECTORY SETUP
# ---------------------------------------------------------
RAW_PDF_DIR = "./data/raw_pdfs"
CLEAN_MD_DIR = "./data/ready_for_db"

os.makedirs(RAW_PDF_DIR, exist_ok=True)
os.makedirs(CLEAN_MD_DIR, exist_ok=True)

# ---------------------------------------------------------
# PART 1: THE ADALA SCRAPER
# ---------------------------------------------------------
def scrape_adala_pdfs(target_url):
    """
    Scrapes the Adala portal for PDF links and downloads them.
    Note: You may need to inspect the exact URL structure of the Adala pagination 
    and update the targeting logic based on their specific HTML classes.
    """
    print(f"🌐 Scraping {target_url}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all anchor tags that link to a .pdf file
        pdf_links = []
        for a_tag in soup.find_all('a', href=True):
            if a_tag['href'].lower().endswith('.pdf'):
                # Handle relative URLs
                link = a_tag['href']
                if not link.startswith('http'):
                    link = "https://adala.justice.gov.ma" + link
                pdf_links.append(link)
        
        print(f"✅ Found {len(pdf_links)} legal PDFs. Starting download...")
        
        for i, link in enumerate(pdf_links):
            filename = link.split('/')[-1]
            filepath = os.path.join(RAW_PDF_DIR, filename)
            
            # Skip if already downloaded
            if not os.path.exists(filepath):
                print(f"📥 Downloading: {filename}")
                pdf_resp = requests.get(link, headers=headers)
                with open(filepath, 'wb') as f:
                    f.write(pdf_resp.content)
                time.sleep(1) # Be polite to the government servers
                
        return [os.path.join(RAW_PDF_DIR, f) for f in os.listdir(RAW_PDF_DIR) if f.endswith('.pdf')]

    except Exception as e:
        print(f"❌ Scraping Error: {e}")
        return []

# ---------------------------------------------------------
# PART 2: THE ARABIC PDF EXTRACTOR
# ---------------------------------------------------------
def clean_arabic_text(raw_text):
    """Fixes the disconnected and reversed Arabic letters from PDFs."""
    if not raw_text:
        return ""
    # Reshape: Connects the letters correctly (e.g., ﻡ ﺭ ﺣ ﺒ ﺎ -> ﻣﺮﺣﺒﺎ)
    reshaped_text = arabic_reshaper.reshape(raw_text)
    # Bidi: Reverses the string to read Right-to-Left correctly
    bidi_text = get_display(reshaped_text)
    return bidi_text

def process_pdf_to_markdown(pdf_path):
    """Extracts text from the PDF, cleans it, and saves as Markdown."""
    filename = os.path.basename(pdf_path).replace('.pdf', '.md')
    output_path = os.path.join(CLEAN_MD_DIR, filename)
    
    # Skip if we already processed this law
    if os.path.exists(output_path):
        print(f"⏭️ Already processed: {filename}")
        return

    print(f"📄 Extracting text from: {os.path.basename(pdf_path)}")
    full_markdown = f"# Document: {filename}\n\n"
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                # Extract text preserving layout where possible
                raw_text = page.extract_text()
                if raw_text:
                    clean_text = clean_arabic_text(raw_text)
                    
                    # Add basic Markdown structure (treating pages as sections for now)
                    full_markdown += f"## صفحة {i + 1}\n\n"
                    full_markdown += f"{clean_text}\n\n"
                    
        # Save to the ready folder for Station 2 (Indexer)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_markdown)
        print(f"✅ Saved clean Markdown to {output_path}")
        
    except Exception as e:
        print(f"❌ Error extracting {pdf_path}: {e}")

# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    # TARGET: Replace with the exact Adala page containing the lists of laws
    TARGET_ADALA_URL = "https://adala.justice.gov.ma/resources/" 
    
    print("🚀 Starting Station 1: Legal Ingestion Pipeline")
    
    # 1. Scrape and Download
    downloaded_pdfs = scrape_adala_pdfs(TARGET_ADALA_URL)
    
    # 2. Extract and Convert to Markdown
    if downloaded_pdfs:
        print("\n⚙️ Beginning Text Extraction...")
        for pdf_file in downloaded_pdfs:
            process_pdf_to_markdown(pdf_file)
            
    print("\n🎉 Station 1 Complete. Data is ready for the Qdrant Indexer.")