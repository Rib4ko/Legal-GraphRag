import os
import cv2
import numpy as np
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from pdf2image import convert_from_path

import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
from dotenv import load_dotenv

load_dotenv() # Load environment variables like HF_TOKEN

from ..models.schemas import Document, DocumentMetadata

class AdvancedOCRIngester:
    """
    Uses MBZUAI/AIN (Qwen2-VL) for high-accuracy Arabic text extraction.
    """

    def __init__(self, lang: str = "ar"):
        self.lang = lang
        print("Loading AIN model in 16-bit precision...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            "MBZUAI/AIN", 
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32, 
            device_map="auto" if self.device == "cuda" else None
        )
        
        min_pixels = 256 * 28 * 28
        max_pixels = 1024 * 28 * 28 
        self.processor = AutoProcessor.from_pretrained(
            "MBZUAI/AIN", 
            min_pixels=min_pixels, 
            max_pixels=max_pixels
        )
        print("Model and processor successfully loaded!")

    async def process_image(self, file_path: str,
                            source_url: Optional[str] = None,
                            language: Optional[str] = None) -> Document:
        target_lang = language or self.lang
        md = self._process_with_ain(file_path)

        return Document(
            metadata=DocumentMetadata(
                source_url=source_url, source_file=file_path,
                language=target_lang, date_extracted=datetime.utcnow(),
            ),
            markdown_content=md,
        )

    async def process_pdf(self, file_path: str,
                          source_url: Optional[str] = None,
                          language: Optional[str] = None) -> Document:
        target_lang = language or self.lang
        images = convert_from_path(file_path, dpi=300)
        pages = []
        for i, img in enumerate(images):
            tmp = f"_page_{i}.png"
            img.save(tmp)
            pages.append(f"## Page {i + 1}\n" + self._process_with_ain(tmp))
            os.remove(tmp)

        return Document(
            metadata=DocumentMetadata(
                source_url=source_url, source_file=file_path,
                language=target_lang, date_extracted=datetime.utcnow(),
            ),
            markdown_content="\n\n".join(pages),
        )

    def _process_with_ain(self, file_path: str) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": file_path,
                    },
                    {"type": "text", "text": "استخرج النص الكامل من هذه الصورة حرفياً من البداية إلى النهاية بصيغة Markdown. حافظ على الجداول والعناوين. لا تختصر أي شيء."},
                ],
            }
        ]

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to(self.device)

        with torch.no_grad(): 
            generated_ids = self.model.generate(
                **inputs, 
                max_new_tokens=2048,
                repetition_penalty=1.05
            )

        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )
        
        return output_text[0] if output_text else ""
