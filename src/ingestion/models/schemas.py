from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    source_url: Optional[str] = Field(None, description="The URL from where the document was scraped (if applicable).")
    source_file: Optional[str] = Field(None, description="The local filename of the parsed document.")
    date_extracted: datetime = Field(default_factory=datetime.utcnow, description="When the document was extracted.")
    language: Optional[str] = Field(None, description="Primary language of the document (e.g., 'ar', 'fr').")

class Document(BaseModel):
    metadata: DocumentMetadata = Field(..., description="Metadata associated with the document.")
    markdown_content: str = Field(..., description="The structured markdown content of the legal document.")
