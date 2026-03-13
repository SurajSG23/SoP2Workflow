from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import fitz
import pdfplumber
from docx import Document


@dataclass
class ParsedDocument:
    text: str
    images: list[bytes]


class DocumentParserError(Exception):
    """Raised when a document cannot be parsed."""


class DocumentParserService:
    def parse(self, filename: str, content: bytes) -> ParsedDocument:
        suffix = filename.lower().rsplit(".", maxsplit=1)[-1]

        if suffix == "pdf":
            return self._parse_pdf(content)
        if suffix == "docx":
            return self._parse_docx(content)

        raise DocumentParserError("Unsupported file type. Please upload PDF or DOCX.")

    def _parse_pdf(self, content: bytes) -> ParsedDocument:
        text_chunks: list[str] = []
        images: list[bytes] = []

        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text() or ""
                if extracted.strip():
                    text_chunks.append(extracted.strip())

        pdf_file = fitz.open(stream=content, filetype="pdf")
        try:
            for page in pdf_file:
                for image_data in page.get_images(full=True):
                    xref = image_data[0]
                    image_bytes = pdf_file.extract_image(xref).get("image")
                    if image_bytes:
                        images.append(image_bytes)
        finally:
            pdf_file.close()

        return ParsedDocument(text="\n".join(text_chunks), images=images)

    def _parse_docx(self, content: bytes) -> ParsedDocument:
        document = Document(BytesIO(content))

        text_chunks = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        images: list[bytes] = []

        for relation in document.part.rels.values():
            if "image" in relation.reltype:
                images.append(relation.target_part.blob)

        return ParsedDocument(text="\n".join(text_chunks), images=images)
