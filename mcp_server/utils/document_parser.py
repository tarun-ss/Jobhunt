"""
Document parser utilities for extracting text from PDF, DOCX, and DOC files
"""
import io
from typing import Optional
import PyPDF2
import pdfplumber
from docx import Document

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        # Try pdfplumber first (better text extraction)
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text.strip()
    except Exception as e:
        print(f"pdfplumber failed: {e}, trying PyPDF2...")
        
    try:
        # Fallback to PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {e}")

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(io.BytesIO(file_content))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse DOCX: {e}")

def extract_text_from_file(filename: str, file_content: bytes) -> str:
    """
    Extract text from a file based on its extension
    
    Args:
        filename: Name of the file
        file_content: Binary content of the file
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If file type is not supported or parsing fails
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(file_content)
    elif filename_lower.endswith('.doc'):
        # DOC files are trickier - try as DOCX (some .doc files are actually .docx)
        try:
            return extract_text_from_docx(file_content)
        except:
            raise ValueError("Legacy .doc format not fully supported. Please convert to .docx or .pdf")
    elif filename_lower.endswith('.txt'):
        return file_content.decode('utf-8', errors='ignore')
    else:
        raise ValueError(f"Unsupported file type: {filename}. Supported: .pdf, .docx, .txt")
