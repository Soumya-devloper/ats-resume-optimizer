"""
PDF Processor - Extract text from PDF files
"""

import pdfplumber
import PyPDF2
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file using pdfplumber as primary method,
    fallback to PyPDF2 if needed.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Extracted text from the PDF
    """
    text = ""

    try:
        # Try pdfplumber first (better for structured text)
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if text.strip():
            return text.strip()
    except Exception as e:
        print(f"pdfplumber extraction failed: {e}, trying PyPDF2...")

    # Fallback to PyPDF2
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"PyPDF2 extraction also failed: {e}")
        raise ValueError(f"Failed to extract text from PDF: {e}")

    return text.strip()


def extract_metadata_from_pdf(pdf_path: str) -> dict:
    """
    Extract metadata from PDF (title, author, etc.)
    """
    metadata = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if pdf.metadata:
                metadata = {
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "pages": len(pdf.pages)
                }
    except Exception as e:
        print(f"Could not extract metadata: {e}")

    return metadata
