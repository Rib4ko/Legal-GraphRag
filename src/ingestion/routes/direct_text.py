import aiofiles
from bs4 import BeautifulSoup
import markdownify
from datetime import datetime
from ..models.schemas import Document, DocumentMetadata

class DirectTextIngester:
    def __init__(self):
        pass

    async def process_html_file(self, file_path: str, source_url: str = None, language: str = None) -> Document:
        """
        Reads an HTML file, strips boilerplate, normalizes encodings, and converts to Markdown.
        """
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            raw_html = await f.read()
        
        return self.process_html_text(raw_html, source_file=file_path, source_url=source_url, language=language)

    def process_html_text(self, raw_html: str, source_file: str = None, source_url: str = None, language: str = None) -> Document:
        """
        Processes raw HTML text to structured Markdown.
        """
        soup = BeautifulSoup(raw_html, 'html.parser')
        
        # Remove common boilerplate elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
            
        # Get the cleaned HTML
        clean_html = str(soup)
        
        # Convert to Markdown
        md_content = markdownify.markdownify(clean_html, heading_style="ATX").strip()
        
        metadata = DocumentMetadata(
            source_url=source_url,
            source_file=source_file,
            language=language,
            date_extracted=datetime.utcnow()
        )
        
        return Document(metadata=metadata, markdown_content=md_content)
