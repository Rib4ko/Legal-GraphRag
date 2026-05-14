import json
import os
import aiofiles
from pathlib import Path
from ..models.schemas import Document

class Validator:
    def __init__(self, pending_dir: str = "data/pending_review"):
        self.pending_dir = Path(pending_dir)
        self.pending_dir.mkdir(parents=True, exist_ok=True)

    async def submit_for_review(self, doc: Document, base_filename: str):
        """
        Saves the structured markdown and its metadata as a pair in the pending_review directory.
        Halts the automatic flow to the Vector DB by storing it here.
        """
        md_path = self.pending_dir / f"{base_filename}.md"
        json_path = self.pending_dir / f"{base_filename}.json"

        # Save Markdown
        async with aiofiles.open(md_path, mode='w', encoding='utf-8') as f:
            await f.write(doc.markdown_content)

        # Save Metadata
        async with aiofiles.open(json_path, mode='w', encoding='utf-8') as f:
            # We serialize datetime to ISO format
            metadata_json = doc.metadata.model_dump_json(indent=4)
            await f.write(metadata_json)

        print(f"Document submitted for human review. Files saved: \n - {md_path}\n - {json_path}")
        return True
